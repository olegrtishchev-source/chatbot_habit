"""Поиск пользователей с невыполненными сегодня привычками — для напоминаний."""

from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from app.models import Habit, HabitLog, User


@dataclass
class PendingReminder:
    """Один пользователь и заголовки его невыполненных сегодня привычек."""

    telegram_id: int
    habit_titles: list[str]


def find_users_with_pending_habits(db: Session) -> list[PendingReminder]:
    """Возвращает пользователей, у которых на сегодня есть невыполненные привычки."""
    today = date.today()

    rows = (
        db.query(User.telegram_id, Habit.title)
        .join(Habit, Habit.user_id == User.id)
        .join(HabitLog, (HabitLog.habit_id == Habit.id) & (HabitLog.date == today))
        .filter(Habit.is_active.is_(True), HabitLog.is_completed.is_(False))
        .all()
    )

    grouped: dict[int, list[str]] = {}
    for telegram_id, title in rows:
        grouped.setdefault(telegram_id, []).append(title)

    return [
        PendingReminder(telegram_id=telegram_id, habit_titles=titles)
        for telegram_id, titles in grouped.items()
    ]
