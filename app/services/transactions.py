from fastapi import HTTPException, status
from sqlalchemy.orm import Query

from app.services.main import AppCRUD, AppService
from app.models import Transaction
from sqlalchemy import desc, func, extract


class TransactionsCRUD(AppCRUD):
    """
    CRUD для Транзакций.

    """

    def get_transaction(self, transaction_id: int) -> Transaction | None:
        """Получить Транзакцию по ID."""
        transaction_db = self.db.query(Transaction).filter_by(id=transaction_id).first()
        if transaction_db:
            return transaction_db
        return None

    def get_transactions_list(self) -> Query:
        """Получить Query списка Транзакций."""
        transactions_db = self.db.query(Transaction)
        return transactions_db


class TransactionsService(AppService):
    """
    Сервис Транзакций.

    """

    def get_transaction(self, transaction_id: int) -> Transaction:
        """Получить Транзакцию по ID."""
        transaction = TransactionsCRUD(db=self.db).get_transaction(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Транзакция с ID {transaction_id} не найдена.",
            )
        return transaction

    def get_transactions_list(
        self,
        user_id: int = None,
        service_id: str = None,
        sort_by_amount: bool = False,
        sort_by_date: bool = False,
    ) -> list[Transaction]:
        """Получить список Транзакций."""
        transactions_query = TransactionsCRUD(db=self.db).get_transactions_list()
        if user_id:
            transactions_query = transactions_query.filter_by(user_id=user_id)
        if service_id:
            transactions_query = transactions_query.filter_by(service_id=service_id)
        if sort_by_amount:
            transactions_query = transactions_query.order_by(desc("amount"))
        if sort_by_date:
            transactions_query = transactions_query.order_by(desc("created_at"))
        return transactions_query.all()

    def get_transactions_services_statistics(
        self, month: int | None = None, year: int | None = None
    ) -> list[dict]:
        """Статистика по Услугам на основании Транзакций."""
        qs = self.db.query(
            Transaction.service_id.label("service_id"),
            func.count(Transaction.service_id).label("count"),
            func.sum(Transaction.amount).label("sum"),
        ).group_by(Transaction.service_id)
        if month and year:
            qs = qs.filter(extract("month", Transaction.created_at) == month)
            qs = qs.filter(extract("year", Transaction.created_at) == year)
        qs = qs.all()
        return qs
