"""Инлайн-клавиатуры бота."""

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_habit_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий для одной привычки: выполнить / изменить / удалить."""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("✅ Выполнено", callback_data=f"complete:{habit_id}"),
        InlineKeyboardButton("✏️ Изменить", callback_data=f"edit:{habit_id}"),
    )
    keyboard.row(InlineKeyboardButton("🗑 Удалить", callback_data=f"delete:{habit_id}"))
    return keyboard


def build_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура отмены — для шага, где ввод обязателен (например, название)."""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
    return keyboard


def build_skip_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для необязательного шага — пропустить или отменить весь диалог."""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Пропустить", callback_data="skip"),
        InlineKeyboardButton("Отмена", callback_data="cancel"),
    )
    return keyboard
