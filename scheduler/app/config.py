"""Настройки фонового сервиса (перенос привычек, напоминания)."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# абсолютный путь к .env в корне проекта — не зависит от того, откуда
# запущена команда
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Конфигурация сервиса переноса привычек и напоминаний."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    database_url: str
    telegram_bot_token: str
    carryover_hour: int = 0
    carryover_minute: int = 5
    reminder_hour: int = 20
    reminder_minute: int = 0


settings = Settings()
