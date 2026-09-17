"""Эндпоинты аутентификации бота."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token
from app.database import get_db
from app.models import User
from app.schemas.auth import TokenRequest, TokenResponse
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def issue_token(request: TokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Находит или создаёт пользователя по telegram_id и выдаёт ему JWT."""
    user = db.query(User).filter(User.telegram_id == request.telegram_id).first()

    if user is None:
        user = User(telegram_id=request.telegram_id, telegram_username=request.telegram_username)
        db.add(user)
        db.commit()
        db.refresh(user)
    elif request.telegram_username and user.telegram_username != request.telegram_username:
        user.telegram_username = request.telegram_username
        db.commit()

    access_token = create_access_token(user.id)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    """Возвращает данные пользователя, которому принадлежит переданный токен."""
    return current_user
