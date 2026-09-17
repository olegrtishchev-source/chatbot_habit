"""Обработчик команды /start — регистрация пользователя и приветствие."""

from telebot import TeleBot
from telebot.types import Message

from app.api_client import ApiError, register_user

WELCOME_TEXT = (
    "Привет! Я помогу отслеживать привычки.\n\n"
    "Команды:\n"
    "/habits — список привычек\n"
    "/add — добавить привычку"
)


def register_start_handlers(bot: TeleBot) -> None:
    """Регистрирует обработчик команды /start."""

    @bot.message_handler(commands=["start"])
    def handle_start(message: Message) -> None:
        """Регистрирует пользователя в backend и показывает приветствие."""
        if message.from_user is None:
            return
        try:
            register_user(message.from_user.id, message.from_user.username)
        except ApiError as error:
            bot.reply_to(message, f"Не удалось зарегистрироваться: {error}")
            return
        bot.reply_to(message, WELCOME_TEXT)
