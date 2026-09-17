"""Подключение к базе данных через SQLAlchemy."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Базовый класс для моделей SQLAlchemy."""


def get_db() -> Generator[Session, None, None]:
    """Отдаёт сессию БД для зависимостей FastAPI (Depends)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
