from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from db import models
from db.schemas import TransactionSchema
from dependencies import get_db, get_transaction

router = APIRouter(
    prefix="/api/transactions",
)


@router.get("/", response_model=list[TransactionSchema])
def transactions_list(db: Session = Depends(get_db)) -> list[models.Transaction]:
    """Получить список Транзакций."""
    transactions_db = db.query(models.Transaction).all()
    return transactions_db


@router.get("/{transaction_id}/", response_model=TransactionSchema)
def transaction_detail(
    transaction: models.Transaction = Depends(get_transaction),
) -> models.Transaction:
    """Получить Транзакцию."""
    return transaction
