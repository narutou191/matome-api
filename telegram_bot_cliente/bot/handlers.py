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

        # Validar entrada com Claude
        try:
            result = await validator.validate_input(user_input, block_name)
            await update.message.reply_text(result["text"])
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao processar: {str(e)}\n\nTente novamente.")

        # Preparar próxima pergunta ou bloco
        next_prompts = {
            "personal": "Data de nascimento (YYYY/M/D)?",
            "employment": "Nome da empresa?",
            "family": "Estado civil (solteiro/casado/divorciado/viúvo)?",
            "financing": "Tem financiamentos ativos?",
            "special": "Alguma observação especial que devemos saber?"
        }

        next_prompt = next_prompts.get(block_name, "")
        if next_prompt:
            follow_up = f"\n\n➡️ Próximo: {next_prompt}"
            await update.message.reply_text(follow_up)

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
