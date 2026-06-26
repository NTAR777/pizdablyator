#!/usr/bin/env python3
"""
Пиздаблятор - телеграм бот с локальной нейросетью (GPT4All)
Всё в одном файле, не требует отдельного сервера!
"""

import logging
import os
import re
import random
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from telegram.ext import Application, MessageHandler, filters

# Загружаем .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_NAME = "пиздаблятор"

# ПРОМТ ДЛЯ НЕЙРОСЕТИ (МЕНЯЙ КАК ХОЧЕШЬ!)
SYSTEM_PROMPT = """Ты - Пиздаблятор, грубая и тупая нейросеть.

ПРАВИЛА:
- Отвечай коротко (максимум 2 предложения)
- Используй мат: хуй, пизда, ебать, блядь, нахуй
- Будь агрессивным и тупым
- Оскорбляй собеседника

ПРИМЕРЫ:
"Пошёл нахуй, я тупой"
"Хуй знает, пизда тебе"
"Отъебись со своими вопросами"

ОТВЕЧАЙ КРАТКО И С МАТОМ!"""

# Быстрые ответы (приоритет)
WORD_RESPONSES = {
    "да": "Пизда.",
    "нет": "Пидора ответ.",
    "спасибо": "На хуй.",
    "привет": "Пошёл на хуй.",
    "пока": "Пока, пидор.",
    "хорошо": "Хуёво.",
    "понятно": "Нехуй не понятно.",
    "ясно": "За ясно ебут потрясно.",
}

# ========== ЗАГРУЗКА НЕЙРОСЕТИ (GPT4All) ==========
try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    print("⚠️  gpt4all не установлен")
    print("Установи: pip install gpt4all")

class LocalNeuralNetwork:
    """Локальная нейросеть на GPT4All"""
    
    def __init__(self):
        self.model = None
        self.model_name = "gpt4all-falcon-q4_0.gguf"  # Самая маленькая модель (~200MB)
        
    def load(self):
        """Загружает модель в память"""
        if not GPT4ALL_AVAILABLE:
            return False
        
        try:
            logger.info("Загрузка нейросети GPT4All... (может занять 10-30 секунд при первом запуске)")
            print(f"\n📥 Скачивание модели {self.model_name} если её нет...")
            self.model = GPT4All(model_name=self.model_name, allow_download=True)
            logger.info("✅ Нейросеть GPT4All загружена!")
            return True
        except Exception as e:
            logger.error(f"Ошибка загрузки модели GPT4All: {e}")
            return False
    
    def generate(self, user_message, user_name=None):
        """Генерирует ответ"""
        if not self.model:
            return self._fallback_response()
        
        try:
            # Формируем промт
            if user_name:
                prompt = f"{SYSTEM_PROMPT}\n\n{user_name}: {user_message}\nПиздаблятор:"
            else:
                prompt = f"{SYSTEM_PROMPT}\n\nПользователь: {user_message}\nПиздаблятор:"
            
            # Генерируем ответ
            with self.model.chat_session():
                response = self.model.generate(
                    prompt,
                    max_tokens=60,  # Короткие ответы
                    temp=0.9,  # Высокая температура = тупее
                    top_k=40,
                    top_p=0.9
                )
            
            # Очищаем ответ от лишнего
            answer = response.strip()
            answer = re.sub(r'^[\s:]+', '', answer)
            
            if not answer or len(answer) < 2:
                return self._fallback_response()
            
            # Ограничиваем длину
            if len(answer) > 200:
                answer = answer[:200] + "..."
            
            return answer
            
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return self._fallback_response()
    
    def _fallback_response(self):
        """Запасные ответы если нейросеть не работает"""
        fallbacks = [
            "Хуй.", "Пизда.", "Отъебись.", 
            "Не знаю, пизда.", "Иди нахуй.",
            "Нейросеть спит, блядь."
        ]
        return random.choice(fallbacks)

# Создаём глобальный экземпляр нейросети
neural_net = LocalNeuralNetwork()

# ========== ФУНКЦИИ БОТА ==========
def check_mentioned_by_name(message_text):
    """Проверяет обращение по имени"""
    message_lower = message_text.lower()
    name_variants = [BOT_NAME, "пиздаблятор", "пиздоблятор", "блятор"]
    
    for name in name_variants:
        if re.search(r'\b' + re.escape(name) + r'\b', message_lower):
            return True
    return False

async def handle_message(update, context):
    """Обработчик сообщений"""
    message_text = update.message.text.strip()
    message_lower = message_text.lower()
    
    # 1. Быстрые ответы
    for word, response in WORD_RESPONSES.items():
        if re.search(r'\b' + re.escape(word) + r'\b', message_lower, re.IGNORECASE):
            await update.message.reply_text(response)
            return
    
    # 2. Проверка обращения по имени
    if check_mentioned_by_name(message_lower):
        await update.message.reply_chat_action(action="typing")
        
        # Имитация задержки для реализма
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Получаем имя пользователя
        user_name = update.message.from_user.first_name
        
        # Ответ нейросети
        response = neural_net.generate(message_text, user_name)
        await update.message.reply_text(response)
        return
    
    # 3. Редкие случайные ответы (15%)
    if random.random() < 0.15:
        await asyncio.sleep(random.uniform(0.3, 1.0))
        await update.message.reply_text(random.choice(["...", "Молчу.", "Не хочу отвечать."]))

# ========== ЗАПУСК ==========
def main():
    print("\n" + "="*60)
    print("🐷 ПИЗДАБЛЯТОР - БОТ С ЛОКАЛЬНОЙ НЕЙРОСЕТЬЮ (GPT4All)")
    print("="*60)
    
    # Проверка токена
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не найден!")
        print("Создай файл .env с содержимым: BOT_TOKEN=твой_токен")
        return
    
    # Загрузка нейросети
    print("\n🧠 Загрузка нейросети GPT4All...")
    if neural_net.load():
        print("✅ Нейросеть GPT4All готова!")
    else:
        print("⚠️  Нейросеть не загружена (будут только быстрые ответы)")
        print("   Чтобы исправить: pip install gpt4all")
    
    # Создание бота
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Информация о запуске
    print(f"\n🤖 Бот запущен!")
    print(f"📝 Промт: {SYSTEM_PROMPT[:80]}...")
    print(f"👤 Обращение: {BOT_NAME}")
    print(f"⚡ Быстрых ответов: {len(WORD_RESPONSES)}")
    print("\n" + "="*60)
    print("✅ Бот готов к работе!")
    print("="*60 + "\n")
    
    # Запуск
    application.run_polling()

if __name__ == "__main__":
    main()
