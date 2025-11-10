import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, filters

# Загружаем переменные из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем настройки из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
RESPONSE_WORD = os.getenv('RESPONSE_WORD', 'Пизда.')  # По умолчанию "Нет"

async def handle_message(update, context):
    """Обработчик входящих сообщений"""
    message_text = update.message.text.strip().lower()
    
    # Проверяем, содержит ли сообщение "да"
    if message_text == "да" or "Да":
        # Отвечаем на сообщение
        await update.message.reply_text(RESPONSE_WORD)

def main():
    """Основная функция"""
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print(f"Пиздаблятор готов ебашить")
    
    application.run_polling()

if __name__ == "__main__":
    main()