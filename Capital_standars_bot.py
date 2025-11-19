import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
