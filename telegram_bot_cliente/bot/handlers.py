from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from bot.client_data import ClientData
from bot.validator import ClientValidator
from bot.excel_generator import ExcelGenerator

class ConversationHandler:
    def __init__(self):
        self.client_data = {}
        self.validators = {}
        self.excel_generator = ExcelGenerator()
        self.blocks = ["personal", "employment", "family", "financing", "special"]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        self.client_data[user_id] = ClientData()
        self.validators[user_id] = ClientValidator()
        context.user_data['current_block'] = 0
        context.user_data['block_personal_index'] = 0

        welcome = """
👋 Bem-vindo ao Sistema de Cadastro de Cliente!

Vou ajudá-lo a preencher os dados necessários para a candidatura a imóvel em 5 blocos.
Responda com calma e precisão. Se houver dúvidas, pergunte!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 BLOCO 1/5: INFORMAÇÕES PESSOAIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Qual é o nome completo do cliente?
(Conforme aparece no Zairyu Card)
        """
        await update.message.reply_text(welcome, reply_markup=ReplyKeyboardRemove())

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_input = update.message.text

        validator = self.validators.get(user_id)
        if not validator:
            await update.message.reply_text("❌ Por favor, clique em /start para começar")
            return

        current_block = context.user_data.get('current_block', 0)
        block_name = self.blocks[current_block] if current_block < len(self.blocks) else "special"

        # Perguntas diretas do bot (não da Claude)
        questions = {
            "personal": [
                "Qual é o nome completo do cliente? (Conforme Zairyu Card)",
                "Qual é a data de nascimento do cliente? (YYYY/M/D)",
                "Qual é o endereço do cliente?",
                "Qual é o CEP do cliente?",
                "Qual é o email do cliente?",
                "Qual é o telefone do cliente?",
                "Qual é a nacionalidade do cliente?"
            ],
            "employment": [
                "Qual é o nome da empresa do cliente?",
                "Qual é o endereço da empresa?",
                "Qual é o local de trabalho do cliente?",
                "Qual é a renda anual do cliente?",
                "Qual é o tipo de contrato do cliente? (正社員, 契約社員, etc)",
                "Qual é a data de contratação do cliente? (YYYY/M/D)",
                "Qual é o dia do pagamento do cliente?"
            ],
            "family": [
                "Qual é o estado civil do cliente? (solteiro/casado/divorciado/viúvo)",
                "O cliente tem dependentes?",
                "Quais são os nomes e idades dos dependentes?"
            ],
            "financing": [
                "O cliente teve liquidações nos últimos 3 meses?",
                "Quantos financiamentos ativos o cliente tem?",
                "Quais são os detalhes dos financiamentos? (tipo, instituição, valor, parcelas)"
            ],
            "special": [
                "O cliente tem trabalho paralelo?",
                "O cliente está em licença maternidade?",
                "O cliente tem doenças ou toma medicamentos?",
                "Há alguma observação especial que devemos saber?"
            ]
        }

        # Validar entrada com Claude (apenas validação, não fazer perguntas)
        try:
            result = await validator.validate_input(user_input, block_name)
            await update.message.reply_text(result["text"])
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao processar: {str(e)}\n\nTente novamente.")

        # Próxima pergunta do mesmo bloco ou próximo bloco
        question_index = context.user_data.get(f'block_{block_name}_index', 0)
        block_questions = questions.get(block_name, [])

        if question_index + 1 < len(block_questions):
            # Próxima pergunta do mesmo bloco
            next_question = block_questions[question_index + 1]
            context.user_data[f'block_{block_name}_index'] = question_index + 1
            await update.message.reply_text(f"\n➡️ {next_question}")
        else:
            # Passou para o próximo bloco
            context.user_data['current_block'] = current_block + 1
            context.user_data[f'block_{block_name}_index'] = 0

            if current_block + 1 < len(self.blocks):
                next_block = self.blocks[current_block + 1]
                next_questions = questions.get(next_block, [])
                if next_questions:
                    await update.message.reply_text(
                        f"\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📋 BLOCO {current_block + 2}/5: {next_block.upper()}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"{next_questions[0]}"
                    )
            else:
                await update.message.reply_text(
                    "\n✅ Todos os blocos foram preenchidos!\n\n"
                    "Envie /complete para gerar o Excel"
                )

    async def complete_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        try:
            client = self.client_data[user_id]
            if not client.is_complete():
                await update.message.reply_text(
                    "❌ Cadastro incompleto!\n\n"
                    "Por favor, complete todos os 5 blocos:\n"
                    "1. Informações Pessoais\n"
                    "2. Informações de Emprego\n"
                    "3. Informações Familiares\n"
                    "4. Financiamentos\n"
                    "5. Informações Especiais\n\n"
                    "Depois envie /complete novamente."
                )
                return

            output_path = self.excel_generator.generate(client)

            with open(output_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=output_path.name,
                    caption=(
                        "✅ Cadastro concluído com sucesso!\n\n"
                        "Seu arquivo foi gerado e está pronto.\n"
                        "Este é o documento com todas as informações coletadas.\n\n"
                        "Próximos passos:\n"
                        "• Revise os dados\n"
                        "• Encaminhe para análise\n"
                        "• Aguarde aprovação\n\n"
                        "Obrigado pela candidatura!"
                    )
                )

            # Limpeza após conclusão
            if user_id in self.client_data:
                del self.client_data[user_id]
            if user_id in self.validators:
                del self.validators[user_id]
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao gerar Excel: {str(e)}")
