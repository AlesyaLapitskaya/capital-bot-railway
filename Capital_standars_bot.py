import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

CHOOSE_BANK = 0
TOKEN = os.getenv('BOT_TOKEN')

# Загружаем конфиг банков с абсолютным путем
try:
    # Пробуем разные возможные пути к файлу
    possible_paths = [
        'banks_config.json',
        './banks_config.json',
        '/app/banks_config.json'
    ]
    
    BANKS = {}
    for path in possible_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                BANKS = json.load(f)
            print(f"✅ Файл banks_config.json успешно загружен по пути: {path}")
            print(f"✅ Загружено банков: {len(BANKS)}")
            break
        except FileNotFoundError:
            print(f"❌ Файл не найден по пути: {path}")
            continue
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка JSON в файле {path}: {e}")
            continue
    
    if not BANKS:
        print("❌ Не удалось загрузить файл banks_config.json ни по одному из путей!")
        # Создаем заглушку для тестирования
        BANKS = {
            "Тестовый банк": {
                "disclosure_url": "https://example.com",
                "type": "html"
            }
        }
        print("✅ Создана тестовая заглушка")
        
except Exception as e:
    print(f"❌ Критическая ошибка при загрузке файла: {e}")
    BANKS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not BANKS:
        await update.message.reply_text("❌ Данные банков не загружены. Обратитесь к администратору.")
        return ConversationHandler.END
    
    keyboard = [[name] for name in BANKS.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Привет! Я бот для поиска нормативного капитала банков Беларуси.\n"
        "Выбери название банка, и я покажу его капитал:",
        reply_markup=reply_markup
    )
    return CHOOSE_BANK

async def handle_bank_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bank_name = update.message.text
    if bank_name not in BANKS:
        await update.message.reply_text("Банк не найден. Попробуйте снова.")
        return CHOOSE_BANK

    url = BANKS[bank_name].get("disclosure_url")
    if not url:
        await update.message.reply_text("Для этого банка ссылка не задана.")
    else:
        await update.message.reply_text(f"Ссылка на нормативный капитал банка {bank_name}:\n{url}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE_BANK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bank_choice)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    print("🤖 Бот запущен и готов к работе!")
    print(f"📊 Доступно банков: {len(BANKS)}")
    app.run_polling()

if __name__ == '__main__':
    main()
