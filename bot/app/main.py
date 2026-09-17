"""Точка входа Telegram-бота."""

import telebot
from telebot.types import Message

from app.config import settings

bot = telebot.TeleBot(settings.telegram_bot_token)


@bot.message_handler(commands=["start"])
def handle_start(message: Message) -> None:
    """Обрабатывает команду /start."""
    bot.reply_to(message, "Бот для трекинга привычек скоро заработает 🙂")


if __name__ == "__main__":
    bot.infinity_polling()
