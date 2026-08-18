import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

WELCOME_TEXT = (
    "🏠 Envie as 2 capturas de tela do imóvel (物件概要 e その他詳細) "
    "pelo botão abaixo para calcular os custos automaticamente."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    webapp_url = os.environ["WEBAPP_URL"]
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📤 Enviar capturas do imóvel", web_app=WebAppInfo(url=webapp_url))]]
    )
    await update.message.reply_text(WELCOME_TEXT, reply_markup=keyboard)


def build_application() -> Application:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    return application


if __name__ == "__main__":
    build_application().run_polling()
