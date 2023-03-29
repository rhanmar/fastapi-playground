from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from db import models
from db.schemas import TransactionSchema
from dependencies import get_db, get_transaction
from sqlalchemy import desc

router = APIRouter(
    prefix="/api/transactions",
)


@router.get("/", response_model=list[TransactionSchema])
def transactions_list(
    user_id: int | None = None,
    sort_by_amount: bool = False,
    sort_by_date: bool = False,
    db: Session = Depends(get_db),
) -> list[models.Transaction]:
    """Получить список Транзакций."""
    transactions_db = db.query(models.Transaction)
    if user_id:
        transactions_db = transactions_db.filter_by(user_id=user_id)
    if sort_by_amount:
        transactions_db = transactions_db.order_by(desc("amount"))
    if sort_by_date:
        transactions_db = transactions_db.order_by(desc("created_at"))
    return transactions_db.all()


@router.get("/{transaction_id}/", response_model=TransactionSchema)
def transaction_detail(
    transaction: models.Transaction = Depends(get_transaction),
) -> models.Transaction:
    """Получить Транзакцию."""
    return transaction
