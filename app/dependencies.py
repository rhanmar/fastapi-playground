from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import Transaction, User
from app.config.database import SessionLocal


def get_db() -> SessionLocal:
    """Получить сессию БД из запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    """Получить пользователя из запроса."""
    user_db = db.query(User).filter_by(id=user_id).first()
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден.",
        )
    return user_db
