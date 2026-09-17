"""HTTP-клиент для обращений Telegram-бота к backend."""

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Ошибка при обращении к backend API — текст уже готов для показа пользователю."""


def _send(
    method: str,
    url: str,
    headers: dict[str, str] | None,
    json: dict[str, Any] | None,
) -> httpx.Response:
    """Выполняет HTTP-запрос и оборачивает любые сетевые/HTTP-ошибки в ApiError.

    Техническую причину сбоя пишет в лог бота — пользователю уходит только
    понятный текст на русском.
    """
    try:
        response = httpx.request(method, url, headers=headers, json=json, timeout=10)
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        logger.error(
            "Backend %s %s -> %s: %s",
            method,
            url,
            error.response.status_code,
            error.response.text,
        )
        detail = "Не удалось выполнить запрос"
        try:
            detail = error.response.json().get("detail", detail)
        except ValueError:
            pass
        raise ApiError(detail) from error
    except httpx.HTTPError as error:
        logger.error("Backend %s %s failed: %r", method, url, error)
        raise ApiError("Не удалось связаться с сервером, попробуйте позже") from error
    return response


def _authenticate(telegram_id: int, telegram_username: str | None) -> str:
    """Получает свежий JWT-токен пользователя по telegram_id (выдаёт и при первом обращении)."""
    response = _send(
        "POST",
        f"{settings.backend_base_url}/auth/token",
        headers=None,
        json={"telegram_id": telegram_id, "telegram_username": telegram_username},
    )
    return str(response.json()["access_token"])


def _request(
    method: str,
    path: str,
    telegram_id: int,
    telegram_username: str | None,
    json: dict[str, Any] | None = None,
) -> httpx.Response:
    """Выполняет авторизованный запрос к backend (сначала получает свежий токен)."""
    token = _authenticate(telegram_id, telegram_username)
    return _send(
        method,
        f"{settings.backend_base_url}{path}",
        headers={"Authorization": f"Bearer {token}"},
        json=json,
    )


def register_user(telegram_id: int, telegram_username: str | None) -> None:
    """Регистрирует пользователя в backend (или подтверждает, что он уже есть)."""
    _authenticate(telegram_id, telegram_username)


def list_habits(telegram_id: int, telegram_username: str | None) -> list[dict[str, Any]]:
    """Возвращает активные привычки пользователя."""
    response = _request("GET", "/habits", telegram_id, telegram_username)
    return list(response.json())


def create_habit(
    telegram_id: int, telegram_username: str | None, title: str, description: str | None
) -> dict[str, Any]:
    """Создаёт новую привычку."""
    response = _request(
        "POST",
        "/habits",
        telegram_id,
        telegram_username,
        json={"title": title, "description": description},
    )
    return dict(response.json())


def update_habit(
    telegram_id: int,
    telegram_username: str | None,
    habit_id: int,
    title: str | None,
    description: str | None,
) -> dict[str, Any]:
    """Обновляет название и/или описание привычки (None — оставить как есть)."""
    response = _request(
        "PATCH",
        f"/habits/{habit_id}",
        telegram_id,
        telegram_username,
        json={"title": title, "description": description},
    )
    return dict(response.json())


def delete_habit(telegram_id: int, telegram_username: str | None, habit_id: int) -> None:
    """Мягко удаляет привычку."""
    _request("DELETE", f"/habits/{habit_id}", telegram_id, telegram_username)


def complete_habit(
    telegram_id: int, telegram_username: str | None, habit_id: int
) -> dict[str, Any]:
    """Отмечает привычку выполненной сегодня."""
    response = _request("POST", f"/habits/{habit_id}/complete", telegram_id, telegram_username)
    return dict(response.json())
