# Telegram Bot - Ответчик на "Да"

Бот для Telegram, который отвечает заданным словом на сообщения "Да" или "да".

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
2. Создайте в папке .env

Вставьте туда:
```.env
BOT_TOKEN=your_actual_bot_token_here
```

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
venv\Scripts\activate
```
3. Устанавливаем зависимости в окружение:
```bash
pip install -r requirements.txt
```
Для выхода из окружения:
```bash
deactivate
```