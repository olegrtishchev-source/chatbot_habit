"""Подсчёт серии выполнений привычки и её отсев по достижении цели."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Habit, HabitLog


def calculate_current_streak(db: Session, habit_id: int) -> int:
    """Считает количество дней подряд с is_completed=True, начиная с последнего дня.

    Отсчёт идёт назад от самой поздней записи HabitLog. Любой пропущенный день
    (нет записи) или день с is_completed=False обрывает серию.
    """
    logs = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id)
        .order_by(HabitLog.date.desc())
        .all()
    )
    if not logs:
        return 0

    logs_by_date = {log.date: log for log in logs}
    streak = 0
    expected_date = logs[0].date

    while expected_date in logs_by_date and logs_by_date[expected_date].is_completed:
        streak += 1
        expected_date -= timedelta(days=1)

    return streak


def update_streak_and_deactivate_if_formed(db: Session, habit: Habit) -> tuple[int, bool]:
    """Пересчитывает серию привычки; при достижении цели отключает привычку.

    Возвращает (текущая_серия, привычка_сформирована).
    """
    streak = calculate_current_streak(db, habit.id)
    habit_formed = streak >= settings.habit_streak_target

    if habit_formed and habit.is_active:
        habit.is_active = False
        db.commit()

    return streak, habit_formed
