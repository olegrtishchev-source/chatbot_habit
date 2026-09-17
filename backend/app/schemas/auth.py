"""Схемы запросов и ответов для аутентификации."""

from pydantic import BaseModel


class TokenRequest(BaseModel):
    """Данные, которые бот присылает для получения токена."""

    telegram_id: int
    telegram_username: str | None = None


class TokenResponse(BaseModel):
    """JWT-токен, выдаваемый пользователю."""

    access_token: str
    token_type: str = "bearer"
