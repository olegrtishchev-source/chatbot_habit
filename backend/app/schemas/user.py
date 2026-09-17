"""Схемы пользователя."""

from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    """Пользователь бота в ответах API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    telegram_username: str | None
