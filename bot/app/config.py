"""Настройки Telegram-бота."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# абсолютный путь к .env в корне проекта — не зависит от того, откуда
# запущена команда (из backend/, из bot/ или из корня)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Конфигурация бота."""

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    telegram_bot_token: str
    backend_base_url: str = "http://backend:8000"


settings = Settings()
