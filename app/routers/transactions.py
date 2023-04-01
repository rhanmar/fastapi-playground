from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.models import Transaction
from app.schemas import TransactionSchema
from app.config.database import get_db
from app.services import TransactionsService


router = APIRouter(
    prefix="/api/transactions",
)


@router.get("/", response_model=list[TransactionSchema])
def transactions_list(
    user_id: int | None = None,
    service_id: str | None = None,
    sort_by_amount: bool = False,
    sort_by_date: bool = False,
    db: Session = Depends(get_db),
) -> list[Transaction]:
    """Получить список Транзакций."""
    transactions = TransactionsService(db=db).get_transactions_list(
        user_id, service_id, sort_by_amount, sort_by_date
    )
    return transactions


@router.get("/services_statistics/")
def transactions_services_statistics(
    month: int | None = None, year: int | None = None, db: Session = Depends(get_db)
) -> list[dict]:
    """Статистика по Услугам на основании Транзакций."""
    return TransactionsService(db=db).get_transactions_services_statistics(month, year)


@router.get("/{transaction_id}/", response_model=TransactionSchema)
def transaction_detail(
    transaction_id: int, db: Session = Depends(get_db)
) -> Transaction:
    """Получить Транзакцию."""
    return TransactionsService(db=db).get_transaction(transaction_id)
