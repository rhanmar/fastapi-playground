from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.config.database import Base


class User(Base):
    """
    Пользователь.

    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=True)
    balance = Column(Float, default=0, info={"verbose_name": "Баланс пользователя"})
    reserve = Column(Float, default=0, info={"verbose_name": "Резерв пользователя"})
    transactions = relationship("Transaction", back_populates="user")

    @hybrid_property
    def transactions_count(self):
        return len(self.transactions)

    @hybrid_property
    def transactions_avg_amount(self):
        if self.transactions:
            return sum(t.amount for t in self.transactions) / self.transactions_count

    @hybrid_property
    def transactions_min_amount(self):
        if self.transactions:
            return min(t.amount for t in self.transactions)

    @hybrid_property
    def transactions_max_amount(self):
        if self.transactions:
            return max(t.amount for t in self.transactions)

    @hybrid_property
    def transactions_sum_amount(self):
        if self.transactions:
            return sum(t.amount for t in self.transactions)
