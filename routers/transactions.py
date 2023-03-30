from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from db import models
from db.schemas import TransactionSchema
from dependencies import get_db, get_transaction
from sqlalchemy import desc
import sqlalchemy
from sqlalchemy import func


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
) -> list[models.Transaction]:
    """Получить список Транзакций."""
    transactions_db = db.query(models.Transaction)
    if user_id:
        transactions_db = transactions_db.filter_by(user_id=user_id)
    if service_id:
        transactions_db = transactions_db.filter_by(service_id=service_id)
    if sort_by_amount:
        transactions_db = transactions_db.order_by(desc("amount"))
    if sort_by_date:
        transactions_db = transactions_db.order_by(desc("created_at"))
    return transactions_db.all()


@router.get("/services_statistics/")
def transactions_services_statistics(
    month: int | None = None, year: int | None = None, db: Session = Depends(get_db)
) -> dict:
    """Статистика по Услугам на основании Транзакций."""
    qs = db.query(
        models.Transaction.service_id.label("service_id"),
        func.count(models.Transaction.service_id).label("count"),
        func.sum(models.Transaction.amount).label("sum"),
    ).group_by(models.Transaction.service_id)
    if month:
        qs = qs.filter(
            sqlalchemy.extract("month", models.Transaction.created_at) == month
        )
    if year:
        qs = qs.filter(
            sqlalchemy.extract("year", models.Transaction.created_at) == year
        )
    qs = qs.all()
    return qs


@router.get("/{transaction_id}/", response_model=TransactionSchema)
def transaction_detail(
    transaction: models.Transaction = Depends(get_transaction),
) -> models.Transaction:
    """Получить Транзакцию."""
    return transaction
