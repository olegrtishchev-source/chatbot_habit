"""Создание и проверка JWT-токенов для аутентификации бота."""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status

from app.config import settings


def create_access_token(user_id: int) -> str:
    """Создаёт JWT-токен, удостоверяющий пользователя по его id в базе."""
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int:
    """Проверяет токен и возвращает id пользователя, которому он выдан."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен"
        ) from error
    return int(payload["sub"])
