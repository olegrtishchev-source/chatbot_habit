"""CRUD-эндпоинты привычек и отметка их выполнения."""

from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Habit, HabitLog, User
from app.schemas.habit import HabitCreate, HabitRead, HabitUpdate
from app.schemas.habit_log import HabitCompletionResult, HabitLogRead
from app.services.streak import update_streak_and_deactivate_if_formed

router = APIRouter(prefix="/habits", tags=["habits"])


def get_active_habit_or_404(db: Session, habit_id: int, user_id: int) -> Habit:
    """Находит активную привычку пользователя или возвращает 404."""
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.user_id == user_id, Habit.is_active.is_(True))
        .first()
    )
    if habit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Привычка не найдена")
    return habit


@router.post("", response_model=HabitRead, status_code=status.HTTP_201_CREATED)
def create_habit(
    request: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Habit:
    """Создаёт новую привычку текущего пользователя."""
    habit = Habit(user_id=current_user.id, title=request.title, description=request.description)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("", response_model=list[HabitRead])
def list_habits(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Habit]:
    """Возвращает активные привычки текущего пользователя."""
    return (
        db.query(Habit)
        .filter(Habit.user_id == current_user.id, Habit.is_active.is_(True))
        .order_by(Habit.created_at)
        .all()
    )


@router.get("/{habit_id}", response_model=HabitRead)
def read_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Habit:
    """Возвращает одну привычку текущего пользователя."""
    return get_active_habit_or_404(db, habit_id, current_user.id)


@router.patch("/{habit_id}", response_model=HabitRead)
def update_habit(
    habit_id: int,
    request: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Habit:
    """Обновляет название и/или описание привычки."""
    habit = get_active_habit_or_404(db, habit_id, current_user.id)
    if request.title is not None:
        habit.title = request.title
    if request.description is not None:
        habit.description = request.description
    db.commit()
    db.refresh(habit)
    return habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Мягко удаляет привычку — помечает её неактивной, история сохраняется."""
    habit = get_active_habit_or_404(db, habit_id, current_user.id)
    habit.is_active = False
    db.commit()


@router.post("/{habit_id}/complete", response_model=HabitCompletionResult)
def complete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> HabitCompletionResult:
    """Отмечает привычку выполненной сегодня. Повторный вызов идемпотентен.

    Пересчитывает серию выполнений подряд; если привычка набрала целевую серию
    (HABIT_STREAK_TARGET, по умолчанию 21 день), она автоматически отключается
    как сформированная.
    """
    habit = get_active_habit_or_404(db, habit_id, current_user.id)
    today = date.today()

    habit_log = (
        db.query(HabitLog).filter(HabitLog.habit_id == habit.id, HabitLog.date == today).first()
    )
    if habit_log is None:
        habit_log = HabitLog(
            habit_id=habit.id, date=today, is_completed=True, marked_at=datetime.now(UTC)
        )
        db.add(habit_log)
    elif not habit_log.is_completed:
        habit_log.is_completed = True
        habit_log.marked_at = datetime.now(UTC)

    db.commit()
    db.refresh(habit_log)

    current_streak, habit_formed = update_streak_and_deactivate_if_formed(db, habit)

    return HabitCompletionResult(
        habit_log=HabitLogRead.model_validate(habit_log),
        current_streak=current_streak,
        habit_formed=habit_formed,
    )
