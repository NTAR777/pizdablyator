# Пиздаблятор 2.0 — стебёт кента через OpenRouter

Телеграм-бот, который выбирает "кента" в чате и отвечает подколом на каждое его
сообщение. Ответы генерирует модель через OpenRouter — ID модели задаётся
прямо в чате командой бота.

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/NTAR777/pizdablyator
```

```bash
cd pizdablyator
```

```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` со следующим содержимым:
```env
BOT_TOKEN=токен_от_BotFather
OPENROUTER_API_KEY=sk-or-v1-...клю4_из_https://openrouter.ai/keys
```

3. Запуск:
```bash
python bot.py
```

## Команды бота (прямо в чате)

| Команда | Что делает |
|---|---|
| `/target <user_id>` | Выбрать кента по ID (или реплай на его сообщение `/target`) |
| `/target off` | Перестать стебать кента |
| `/model <id>` | Модель OpenRouter, например `deepseek/deepseek-chat-v3.1:free` |
| `/model` | Показать текущую модель |
| `/prompt <текст>` | Свой стиль стёба (системный промт) |
| `/prompt reset` | Вернуть дефолтный промт |
| `/status` | Текущие настройки чата |

ID моделей смотрите на https://openrouter.ai/models (для бесплатных берите
варианты с пометкой `:free`).

## Как узнать user_id кента

Проще всего: реплай на его сообщение командой `/target` — бот сам вытащит ID.
Либо попросите кента написать боту @userinfobot.

Настройки (`кент`, `модель`, `промт`) сохраняются в `config.json` и переживают
перезапуск, причём для каждого чата свои.

## Если linux arch или просто хотим окружение
1. Создаём окружение
```bash
python -m venv venv
```
2. Запускаем окружение:

Для Windows
```bash
venv\Scripts\activate
```
Для Linux/MacOS
```bash
source venv/bin/activate
```
3. Устанавливаем зависимости в окружение:
```bash
pip install -r requirements.txt
```
Для выхода из окружения:
```bash
deactivate
```
