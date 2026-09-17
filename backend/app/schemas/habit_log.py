"""Схемы отметок выполнения привычки."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class HabitLogRead(BaseModel):
    """Отметка о выполнении привычки за день в ответах API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_id: int
    date: date
    is_completed: bool
    marked_at: datetime | None


class HabitCompletionResult(BaseModel):
    """Результат отметки выполнения: сам лог, текущая серия и статус привычки."""

    habit_log: HabitLogRead
    current_streak: int
    habit_formed: bool
