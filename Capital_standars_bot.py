import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

CHOOSE_BANK = 0
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    print("❌ BOT_TOKEN not found!")
    exit(1)

print("✅ Bot token loaded")

# Banks data
BANKS = {
    "Беларусбанк": "https://belarusbank.by/ru/33139/33151/33154/10560",
    "Белагропромбанк": "https://www.belapb.by/about/spravochnaya-informatsiya/normativy-bezopasnogo-funktsionirovaniya",
    "Белинвестбанк": "https://www.belinvestbank.by/about-bank/finance-statistic",
    "Приорбанк": "https://www.priorbank.by/priorbank-main/business-information/bank-reporting/about-normativy-rezervy",
    "Сбер Банк": "https://www.sber-bank.by/standards-of-safe-functioning",
    "Альфа-Банк": "https://www.alfabank.by/about/reporting",
    "Белгазпромбанк": "https://belgazprombank.by/about/finansovie_pokazateli/vipolnenie_normativov_bezopasnogo_funkci",
    "Банк БелВЭБ": "https://www.belveb.by/standards",
    "БНБ-Банк": "https://bnb.by/o-nas/nashi-rezultaty/prudentsialnaya-otchetnost",
    "МТБанк": "https://www.mtbank.by/about/reporting/standards/",
    "Банк ВТБ": "https://www.vtb.by/o-banke/finansovaya-otchetnost/2025?type=6"
}

def create_keyboard():
    keyboard = [[bank] for bank in BANKS.keys()]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = create_keyboard()
    await update.message.reply_text(
        "Привет! Выберите банк:",
        reply_markup=reply_markup
    )
    return CHOOSE_BANK

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bank = update.message.text
    if bank in BANKS:
        await update.message.reply_text(f"Ссылка: {BANKS[bank]}")
    else:
        await update.message.reply_text("Банк не найден")
    
    reply_markup = create_keyboard()
    await update.message.reply_text("Выберите следующий банк:", reply_markup=reply_markup)
    return CHOOSE_BANK

def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={CHOOSE_BANK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)]},
        fallbacks=[]
    )
    
    app.add_handler(conv_handler)
    print("🤖 Bot started!")
    app.run_polling()

if __name__ == '__main__':
    main()
