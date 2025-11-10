import logging
import os
import re
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

# Список слов и ответов на них
WORD_RESPONSES = {
    "да": "Пизда.",
    "нет": "Пидора ответ.",
    "возможно": "Хуй знает.",
    "может быть": "А может и не быть.",
    "конечно": "Ебать ты уверен.",
    "точно": "Точно пизда.",
    "правда": "Пиздеж.",
    "спасибо": "На хуй.",
    "привет": "Пошёл на хуй.",
    "здравствуй": "Здравствуй иди нахуй.",
    "пока": "Пока, пидор.",
    "хорошо": "Хуёво.",
    "отлично": "Хуёво.",
    "класс": "Хуёво.",
    "понятно": "Нехуй не понятно.",
    "ясно": "Ясно, пизда.",
}

async def handle_message(update, context):
    """Обработчик входящих сообщений"""
    message_text = update.message.text.strip().lower()
    
    # Проверяем каждое слово из списка
    for word, response in WORD_RESPONSES.items():
        # Используем регулярное выражение для поиска целого слова
        if re.search(r'\b' + re.escape(word) + r'\b', message_text, re.IGNORECASE):
            # Отвечаем на сообщение
            await update.message.reply_text(response)
            break  # Прерываем после первого найденного слова

def main():
    """Основная функция"""
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("Пиздаблятор готов ебашить")
    print("Отслеживаемые слова:")
    for word, response in WORD_RESPONSES.items():
        print(f"  '{word}' -> '{response}'")
    
    application.run_polling()

if __name__ == "__main__":
    main()