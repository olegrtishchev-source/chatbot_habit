"""Настройки backend-сервиса, загружаемые из переменных окружения."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# абсолютный путь к .env в корне проекта — не зависит от того, откуда
# запущена команда (из backend/, из bot/ или из корня)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Конфигурация FastAPI-приложения."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 43200
    habit_streak_target: int = 21


settings = Settings()
