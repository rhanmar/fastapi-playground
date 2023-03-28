from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db import models
from db.database import SessionLocal


def get_db() -> SessionLocal:
    """Получить сессию БД из запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(user_id: int, db: Session = Depends(get_db)) -> models.User:
    """Получить пользователя из запроса."""
    user_db = db.query(models.User).filter_by(id=user_id).first()
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден.",
        )
    return user_db


def get_transaction(
    transaction_id: int, db: Session = Depends(get_db)
) -> models.Transaction:
    """Получить Транзакцию по ID."""
    transaction_db = db.query(models.Transaction).filter_by(id=transaction_id).first()
    if not transaction_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Транзакция с ID {transaction_id} не найдена.",
        )
    return transaction_db
