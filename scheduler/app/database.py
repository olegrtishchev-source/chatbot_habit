"""Подключение к базе данных через SQLAlchemy."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Базовый класс для моделей SQLAlchemy."""


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Отдаёт сессию БД для разового сценария (не FastAPI Depends), закрывает по выходу."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
