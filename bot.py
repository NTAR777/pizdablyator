#!/usr/bin/env python3
"""
Пиздаблятор 2.0 — стебёт кента через OpenRouter.

Каждое сообщение кента уходит в модель, а бот отвечает подколом.
Модель и цель выбираются прямо в чате командами:
  /target <user_id>  (или реплаем на его сообщение: /target)
  /model <id>        (например: /model deepseek/deepseek-chat-v3.1:free)
  /prompt <текст>    (своё поведение бота, опционально)
  /status            (посмотреть текущие настройки)

Настройки хранятся в config.json и переживают перезапуск.
"""

import json
import logging
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("pizdablyator")

# ================= НАСТРОЙКИ =================
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
CONFIG_FILE = Path("config.json")

# Модель по умолчанию (бесплатная), меняется через /model
DEFAULT_MODEL = "deepseek/deepseek-chat-v3.1:free"

# Промт по умолчанию, меняется через /prompt
DEFAULT_PROMPT = (
    "Ты — Пиздаблятор, злой кореш из телеграм-чата. Твоя работа — стебать "
    "над каждым сообщением: короткий едкий подкол, 1-2 предложения, можно "
    "с матом. Не помогай и не отвечай по делу — только рофли над человеком "
    "и его сообщением. Пиши как обычное сообщение в телеге, без Markdown."
)


# ================= КОНФИГ =================
def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("config.json не читается (%s), начинаю с нуля", e)
    return {}


def save_config(cfg: dict) -> None:
    CONFIG_FILE.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def get_chat_cfg(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> dict:
    """Настройки конкретного чата с дефолтами."""
    store = context.bot_data.setdefault("config", load_config())
    entry = store.setdefault(str(chat_id), {})
    entry.setdefault("target_id", None)
    entry.setdefault("model", DEFAULT_MODEL)
    entry.setdefault("prompt", DEFAULT_PROMPT)
    return entry


def persist(context: ContextTypes.DEFAULT_TYPE) -> None:
    save_config(context.bot_data["config"])


# ================= OPENROUTER =================
async def ask_openrouter(model: str, prompt: str, user_name: str, text: str) -> str:
    """Шлёт сообщение кента в OpenRouter и возвращает ответ модели."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"{user_name} пишет: {text}"},
        ],
        "max_tokens": 300,
        "temperature": 1.0,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return content.strip() if content else "Модель ответила пустотой, как и этот кент."


def error_hint(status_code: int) -> str:
    return {
        401: "Ключ OpenRouter неверный — проверь OPENROUTER_API_KEY в .env",
        402: "На аккаунте OpenRouter кончились кредиты",
        404: f"Модель не найдена — возьми правильный ID на https://openrouter.ai/models",
        429: "Лимит запросов OpenRouter, подожди чуть-чуть",
    }.get(status_code, f"OpenRouter вернул ошибку {status_code}")


# ================= КОМАНДЫ =================
async def cmd_model(update, context):
    """Задаёт модель OpenRouter: /model <id> или показывает текущую."""
    cfg = get_chat_cfg(context, update.effective_chat.id)
    if not context.args:
        await update.message.reply_text(
            f"Текущая модель:\n{cfg['model']}\n\n"
            "Менять так: /model google/gemini-2.0-flash-exp:free\n"
            "ID моделей смотреть тут: https://openrouter.ai/models",
        )
        return
    cfg["model"] = context.args[0].strip()
    persist(context)
    await update.message.reply_text(f"Записал модель: {cfg['model']}")


async def cmd_target(update, context):
    """Выбирает кента: /target <user_id> или реплаем на его сообщение."""
    cfg = get_chat_cfg(context, update.effective_chat.id)
    reply = update.message.reply_to_message

    if not context.args:
        if cfg["target_id"]:
            await update.message.reply_text(
                f"Сейчас под раздачей: id {cfg['target_id']}\n"
                "Снять: /target off"
            )
        else:
            await update.message.reply_text(
                "Кент не выбран. Реплай на его сообщение командой /target "
                "или напиши /target <user_id>"
            )
        return

    arg = context.args[0].lower()
    if arg in ("off", "выкл", "стоп"):
        cfg["target_id"] = None
        persist(context)
        await update.message.reply_text("Кент отпущен, стебать больше никого не буду.")
        return

    if reply and reply.from_user and not reply.from_user.is_bot:
        cfg["target_id"] = reply.from_user.id
    elif arg.isdigit():
        cfg["target_id"] = int(arg)
    else:
        await update.message.reply_text(
            "Не понял. Реплай на сообщение кента командой /target, "
            "либо /target <user_id>, либо /target off"
        )
        return

    persist(context)
    await update.message.reply_text(
        f"Цель захвачена: id {cfg['target_id']}. Теперь каждое его сообщение получит подкол."
    )


async def cmd_prompt(update, context):
    """Меняет промт бота: /prompt <текст>, сброс: /prompt reset."""
    cfg = get_chat_cfg(context, update.effective_chat.id)
    if not context.args:
        await update.message.reply_text(
            f"Текущий промт:\n\n{cfg['prompt']}\n\n"
            "Сменить: /prompt <новый промт>\n"
            "Сбросить на дефолт: /prompt reset"
        )
        return

    text = " ".join(context.args)
    if text.lower() == "reset":
        cfg["prompt"] = DEFAULT_PROMPT
        await update.message.reply_text("Промт сброшен на дефолт.")
    else:
        cfg["prompt"] = text
        await update.message.reply_text("Промт обновлён.")
    persist(context)


async def cmd_status(update, context):
    """Показывает текущие настройки чата."""
    cfg = get_chat_cfg(context, update.effective_chat.id)
    target = f"id {cfg['target_id']}" if cfg["target_id"] else "не выбран"
    key_state = "задан" if OPENROUTER_API_KEY else "НЕ задан (см. .env)"
    await update.message.reply_text(
        f"🎯 Кент: {target}\n"
        f"🧠 Модель: {cfg['model']}\n"
        f"🔑 OPENROUTER_API_KEY: {key_state}\n\n"
        f"Промт:\n{cfg['prompt']}"
    )


# ================= ГЛАВНАЯ ЛОГИКА =================
async def roast_handler(update, context):
    """Каждое сообщение кента улетает в модель и возвращается подколом."""
    message = update.message
    cfg = get_chat_cfg(context, message.chat.id)

    if cfg["target_id"] is None or message.from_user.id != cfg["target_id"]:
        return  # это не кент, игнорим

    if not OPENROUTER_API_KEY:
        await message.reply_text(
            "OPENROUTER_API_KEY не задан в .env — стебать не выйдет."
        )
        return

    await context.bot.send_chat_action(
        chat_id=message.chat.id, action=ChatAction.TYPING
    )

    user_name = message.from_user.first_name or "Кент"
    try:
        answer = await ask_openrouter(
            cfg["model"], cfg["prompt"], user_name, message.text
        )
    except httpx.HTTPStatusError as e:
        logger.error("OpenRouter HTTP %s: %s", e.response.status_code, e)
        await message.reply_text(error_hint(e.response.status_code))
        return
    except (httpx.RequestError, KeyError, IndexError, TypeError) as e:
        logger.error("Ошибка запроса к OpenRouter: %s", e)
        await message.reply_text("OpenRouter не ответил. Хуй знает почему, попробуй ещё.")
        return

    if len(answer) > 4000:
        answer = answer[:4000] + "…"

    await message.reply_text(answer, reply_to_message_id=message.message_id)


# ================= ЗАПУСК =================
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не найден! Добавь в .env: BOT_TOKEN=твой_токен")
        return
    if not OPENROUTER_API_KEY:
        print("⚠️  OPENROUTER_API_KEY не задан — рофлов не будет.")
        print("   Добавь в .env: OPENROUTER_API_KEY=sk-or-v1-...")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("model", cmd_model))
    application.add_handler(CommandHandler("target", cmd_target))
    application.add_handler(CommandHandler("prompt", cmd_prompt))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, roast_handler)
    )

    print("🐷 Пиздаблятор 2.0 готов стебать кента")
    print("Команды: /target — выбрать кента, /model — модель OpenRouter,")
    print("         /prompt — стиль стёба, /status — что настроено")
    application.run_polling()


if __name__ == "__main__":
    main()
