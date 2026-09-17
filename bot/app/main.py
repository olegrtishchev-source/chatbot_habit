"""Точка входа Telegram-бота."""

import logging

import telebot
from telebot.types import BotCommand

from app.config import settings
from app.handlers.habits import register_habit_handlers
from app.handlers.start import register_start_handlers

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(settings.telegram_bot_token)

register_start_handlers(bot)
register_habit_handlers(bot)


def _setup_commands() -> None:
    """Регистрирует меню команд бота в Telegram (кнопка рядом с полем ввода)."""
    try:
        bot.set_my_commands(
            [
                BotCommand("start", "Начать работу"),
                BotCommand("habits", "Список привычек"),
                BotCommand("add", "Добавить привычку"),
            ]
        )
    except Exception:
        logger.exception("Не удалось зарегистрировать меню команд бота")


if __name__ == "__main__":
    _setup_commands()
    bot.infinity_polling()
