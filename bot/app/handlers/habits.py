"""Обработчики привычек: список, добавление, изменение, отметка выполнения, удаление."""

from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from app.api_client import (
    ApiError,
    complete_habit,
    create_habit,
    delete_habit,
    list_habits,
    uncomplete_habit,
    update_habit,
)
from app.keyboards import build_cancel_keyboard, build_habit_keyboard, build_skip_keyboard
from app.state import DialogState, clear_state, get_state, set_state


def register_habit_handlers(bot: TeleBot) -> None:
    """Регистрирует обработчики команд /habits, /add, диалогов и инлайн-кнопок."""

    @bot.message_handler(commands=["habits"])
    def handle_habits(message: Message) -> None:
        """Показывает список активных привычек с кнопками действий."""
        if message.from_user is None:
            return
        try:
            habits = list_habits(message.from_user.id, message.from_user.username)
        except ApiError as error:
            bot.reply_to(message, f"Не удалось получить список привычек: {error}")
            return

        if not habits:
            bot.reply_to(message, "У вас пока нет привычек. Добавьте первую командой /add")
            return

        for habit in habits:
            text = f"📌 {habit['title']}"
            if habit.get("description"):
                text += f"\n{habit['description']}"
            bot.send_message(message.chat.id, text, reply_markup=build_habit_keyboard(habit["id"]))

    @bot.message_handler(commands=["add"])
    def handle_add(message: Message) -> None:
        """Начинает пошаговый диалог создания привычки."""
        if message.from_user is None:
            return
        clear_state(message.from_user.id)
        set_state(message.from_user.id, DialogState(step="add_title"))
        bot.reply_to(message, "Как назвать привычку?", reply_markup=build_cancel_keyboard())

    @bot.message_handler(
        func=lambda message: message.from_user is not None
        and get_state(message.from_user.id) is not None,
        content_types=["text"],
    )
    def handle_dialog_text(message: Message) -> None:
        """Обрабатывает текстовый ввод в рамках пошагового диалога создания/изменения."""
        if message.from_user is None:
            return
        telegram_id = message.from_user.id
        telegram_username = message.from_user.username
        state = get_state(telegram_id)
        if state is None:
            return

        if state.step == "add_title":
            set_state(telegram_id, DialogState(step="add_description", title=message.text))
            bot.reply_to(
                message,
                "Добавьте описание привычки (необязательно):",
                reply_markup=build_skip_keyboard(),
            )
            return

        if state.step == "add_description":
            _finish_add(
                bot, message.chat.id, telegram_id, telegram_username, state.title, message.text
            )
            return

        if state.step == "edit_title":
            set_state(
                telegram_id,
                DialogState(step="edit_description", habit_id=state.habit_id, title=message.text),
            )
            bot.reply_to(
                message,
                "Введите новое описание (необязательно):",
                reply_markup=build_skip_keyboard(),
            )
            return

        if state.step == "edit_description":
            _finish_edit(
                bot,
                message.chat.id,
                telegram_id,
                telegram_username,
                state.habit_id,
                state.title,
                message.text,
            )
            return

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call: CallbackQuery) -> None:
        """Обрабатывает нажатия инлайн-кнопок."""
        if call.data is None or call.message is None:
            bot.answer_callback_query(call.id)
            return

        telegram_id = call.from_user.id
        telegram_username = call.from_user.username
        data = call.data
        chat_id = call.message.chat.id

        if data == "cancel":
            clear_state(telegram_id)
            bot.answer_callback_query(call.id, "Отменено")
            bot.send_message(chat_id, "Действие отменено.")
            return

        if data == "skip":
            state = get_state(telegram_id)
            bot.answer_callback_query(call.id)
            if state is None:
                return
            if state.step == "add_description":
                _finish_add(bot, chat_id, telegram_id, telegram_username, state.title, None)
            elif state.step == "edit_title":
                set_state(
                    telegram_id,
                    DialogState(step="edit_description", habit_id=state.habit_id, title=None),
                )
                bot.send_message(
                    chat_id,
                    "Введите новое описание (необязательно):",
                    reply_markup=build_skip_keyboard(),
                )
            elif state.step == "edit_description":
                _finish_edit(
                    bot, chat_id, telegram_id, telegram_username, state.habit_id, state.title, None
                )
            return

        action, _, raw_habit_id = data.partition(":")
        habit_id = int(raw_habit_id) if raw_habit_id else None

        if action == "complete" and habit_id is not None:
            bot.answer_callback_query(call.id)
            try:
                result = complete_habit(telegram_id, telegram_username, habit_id)
            except ApiError as error:
                bot.send_message(chat_id, f"Не удалось отметить выполнение: {error}")
                return
            if result["habit_formed"]:
                bot.send_message(
                    chat_id,
                    "🎉 Привычка сформирована! Серия — "
                    f"{result['current_streak']} дней подряд. Убрана из активного списка.",
                )
            else:
                bot.send_message(
                    chat_id,
                    f"✅ Отмечено выполненным сегодня. "
                    f"Серия: {result['current_streak']} дней подряд.",
                )
            return

        if action == "uncomplete" and habit_id is not None:
            bot.answer_callback_query(call.id)
            try:
                result = uncomplete_habit(telegram_id, telegram_username, habit_id)
            except ApiError as error:
                bot.send_message(chat_id, f"Не удалось снять отметку: {error}")
                return
            bot.send_message(
                chat_id,
                "❌ Отметка о выполнении сегодня снята. "
                f"Серия: {result['current_streak']} дней подряд.",
            )
            return

        if action == "edit" and habit_id is not None:
            clear_state(telegram_id)
            set_state(telegram_id, DialogState(step="edit_title", habit_id=habit_id))
            bot.answer_callback_query(call.id)
            bot.send_message(
                chat_id,
                "Введите новое название привычки (или нажмите «Пропустить»):",
                reply_markup=build_skip_keyboard(),
            )
            return

        if action == "delete" and habit_id is not None:
            bot.answer_callback_query(call.id)
            try:
                delete_habit(telegram_id, telegram_username, habit_id)
            except ApiError as error:
                bot.send_message(chat_id, f"Не удалось удалить привычку: {error}")
                return
            bot.send_message(chat_id, "🗑 Привычка удалена.")
            return

        bot.answer_callback_query(call.id)


def _finish_add(
    bot: TeleBot,
    chat_id: int,
    telegram_id: int,
    telegram_username: str | None,
    title: str | None,
    description: str | None,
) -> None:
    """Завершает диалог создания привычки и вызывает backend."""
    clear_state(telegram_id)
    try:
        habit = create_habit(telegram_id, telegram_username, title or "", description)
    except ApiError as error:
        bot.send_message(chat_id, f"Не удалось создать привычку: {error}")
        return
    bot.send_message(chat_id, f"✅ Привычка «{habit['title']}» добавлена.")


def _finish_edit(
    bot: TeleBot,
    chat_id: int,
    telegram_id: int,
    telegram_username: str | None,
    habit_id: int | None,
    title: str | None,
    description: str | None,
) -> None:
    """Завершает диалог изменения привычки и вызывает backend."""
    clear_state(telegram_id)
    if habit_id is None:
        return
    try:
        habit = update_habit(telegram_id, telegram_username, habit_id, title, description)
    except ApiError as error:
        bot.send_message(chat_id, f"Не удалось изменить привычку: {error}")
        return
    bot.send_message(chat_id, f"✏️ Привычка «{habit['title']}» обновлена.")
