import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv('BOT_TOKEN')

# Проверяем что токен загружен
if not TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден в переменных окружения!")
    print("❌ Проверьте что переменная BOT_TOKEN добавлена в Railway")
    exit(1)

print(f"✅ Токен бота загружен: {TOKEN[:10]}...")

# Данные банков прямо в коде
BANKS = {
    "Беларусбанк": {
        "disclosure_url": "https://belarusbank.by/ru/33139/33151/33154/10560",
        "type": "html"
    },
    "Белагропромбанк": {
        "disclosure_url": "https://www.belapb.by/about/spravochnaya-informatsiya/normativy-bezopasnogo-funktsionirovaniya", 
        "type": "html"
    },
    "Белинвестбанк": {
        "disclosure_url": "https://www.belinvestbank.by/about-bank/finance-statistic",
        "type": "pdf"
    },
    "Приорбанк": {
        "disclosure_url": "https://www.priorbank.by/priorbank-main/business-information/bank-reporting/about-normativy-rezervy",
        "type": "html"
    },
    "Сбер Банк": {
        "disclosure_url": "https://www.sber-bank.by/standards-of-safe-functioning",
        "type": "pdf"
    },
    "Альфа-Банк": {
        "disclosure_url": "https://www.alfabank.by/about/reporting",
        "type": "pdf"
    },
    "Белгазпромбанк": {
        "disclosure_url": "https://belgazprombank.by/about/finansovie_pokazateli/vipolnenie_normativov_bezopasnogo_funkci",
        "type": "pdf"
    },
    "Банк БелВЭБ": {
        "disclosure_url": "https://www.belveb.by/standards",
        "type": "pdf"
    },
    "БНБ-Банк": {
        "disclosure_url": "https://bnb.by/o-nas/nashi-rezultaty/prudentsialnaya-otchetnost",
        "type": "pdf"
    }
}

print(f"✅ Данные банков загружены напрямую в код")
print(f"✅ Загружено банков: {len(BANKS)}")

# Функция для создания клавиатуры
def create_bank_keyboard():
    keyboard = [[name] for name in BANKS.keys()]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    reply_markup = create_bank_keyboard()
    await update.message.reply_text(
        "Привет! Я бот для поиска нормативного капитала банков Беларуси.\n"
        "Выбери название банка из списка ниже:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех текстовых сообщений"""
    bank_name = update.message.text
    reply_markup = create_bank_keyboard()
    
    # Если сообщение - название банка
    if bank_name in BANKS:
        url = BANKS[bank_name].get("disclosure_url")
        if not url:
            await update.message.reply_text(
                f"Для банка '{bank_name}' ссылка не задана.\n\nВыберите другой банк:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                f"Ссылка на нормативный капитал банка {bank_name}:\n{url}\n\nВыберите следующий банк:",
                reply_markup=reply_markup
            )
    else:
        # Если сообщение не название банка
        await update.message.reply_text(
            "Выберите банк из списка ниже:",
            reply_markup=reply_markup
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    reply_markup = create_bank_keyboard()
    await update.message.reply_text(
        "Я бот для поиска нормативного капитала банков Беларуси.\n"
        "Просто выберите банк из списка ниже:",
        reply_markup=reply_markup
    )

def main():
    app = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # Обработчик для всех текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен и готов к работе!")
    print(f"📊 Доступно банков: {len(BANKS)}")
    app.run_polling()

if __name__ == '__main__':
    main()
