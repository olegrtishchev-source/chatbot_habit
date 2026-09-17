"""Схемы привычек."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HabitCreate(BaseModel):
    """Данные для создания привычки."""

    title: str
    description: str | None = None


class HabitUpdate(BaseModel):
    """Данные для обновления привычки (оба поля необязательны)."""

    title: str | None = None
    description: str | None = None


class HabitRead(BaseModel):
    """Привычка в ответах API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    is_active: bool
    created_at: datetime
