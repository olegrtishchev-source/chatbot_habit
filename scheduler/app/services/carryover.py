"""Ежедневный перенос привычек: создание пустых HabitLog на новый день."""

from datetime import date

from sqlalchemy.orm import Session

from app.models import Habit, HabitLog


def create_missing_logs_for_today(db: Session) -> int:
    """Создаёт HabitLog(is_completed=False) на сегодня для активных привычек,
    у которых ещё нет записи за сегодня.

    Возвращает количество созданных записей.
    """
    today = date.today()

    active_habit_ids = [
        habit_id for (habit_id,) in db.query(Habit.id).filter(Habit.is_active.is_(True))
    ]
    if not active_habit_ids:
        return 0

    existing_habit_ids = {
        habit_id
        for (habit_id,) in db.query(HabitLog.habit_id).filter(
            HabitLog.date == today, HabitLog.habit_id.in_(active_habit_ids)
        )
    }

    missing_habit_ids = [
        habit_id for habit_id in active_habit_ids if habit_id not in existing_habit_ids
    ]
    for habit_id in missing_habit_ids:
        db.add(HabitLog(habit_id=habit_id, date=today, is_completed=False))

    db.commit()
    return len(missing_habit_ids)
