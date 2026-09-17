"""Модель записи о выполнении привычки за конкретный день (совпадает со схемой backend)."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.habit import Habit


class HabitLog(Base):
    """Отметка о выполнении привычки за один день."""

    __tablename__ = "habit_logs"
    __table_args__ = (UniqueConstraint("habit_id", "date", name="uq_habit_log_habit_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id", ondelete="CASCADE"))
    date: Mapped[datetime.date] = mapped_column(Date)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    marked_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))

    habit: Mapped[Habit] = relationship(back_populates="logs")
