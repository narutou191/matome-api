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

        welcome = """
👋 Bem-vindo ao Cadastro de Cliente!

Vou ajudá-lo a preencher todos os dados necessários em 5 etapas.

👤 BLOCO 1: INFORMAÇÕES PESSOAIS

Qual é seu nome completo? (Conforme Zairyu Card)
        """
        await update.message.reply_text(welcome, reply_markup=ReplyKeyboardRemove())

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        user_input = update.message.text

        validator = self.validators.get(user_id)
        if not validator:
            await update.message.reply_text("❌ Por favor, clique em /start")
            return

        result = validator.validate_input(user_input, "client_registration")
        await update.message.reply_text(result["text"])

    async def complete_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id

        try:
            client = self.client_data[user_id]
            if not client.is_complete():
                await update.message.reply_text("❌ Cadastro incompleto. Preencha todos os blocos primeiro.")
                return

            output_path = self.excel_generator.generate(client)

            with open(output_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=output_path.name,
                    caption="✅ Seu cadastro foi concluído com sucesso!"
                )
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao gerar Excel: {str(e)}")
