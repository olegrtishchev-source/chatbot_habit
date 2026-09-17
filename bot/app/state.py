"""Состояние пошаговых диалогов бота (создание/изменение привычки), в памяти процесса."""

from dataclasses import dataclass

_states: dict[int, "DialogState"] = {}


@dataclass
class DialogState:
    """Текущий шаг диалога с пользователем и накопленные на предыдущих шагах данные."""

    step: str
    habit_id: int | None = None
    title: str | None = None


def set_state(telegram_id: int, state: DialogState) -> None:
    """Сохраняет состояние диалога для пользователя."""
    _states[telegram_id] = state


def get_state(telegram_id: int) -> DialogState | None:
    """Возвращает текущее состояние диалога пользователя, если оно есть."""
    return _states.get(telegram_id)


def clear_state(telegram_id: int) -> None:
    """Сбрасывает состояние диалога пользователя."""
    _states.pop(telegram_id, None)
