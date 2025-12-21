from telegram import Update
from telegram.ext import Application,CommandHandler,ContextTypes
from telegram import InlineKeyboardButton,InlineKeyboardMarkup

async def start(update:Update,contex:ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("play ",web_app={"url":"https://ruletzreach.github.io/00/"})]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click the button to play",reply_markup=reply_markup)
def main():
    application = Application.builder().token("8540455024:AAGn1_E3Y8wrRmHAhsX4uMaGmgc3nX7eueE").build()
    application.add_handler(CommandHandler("start",start))
    application.run_polling()

main()
