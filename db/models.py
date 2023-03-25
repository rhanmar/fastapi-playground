from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from db.database import Base


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


class Transaction(Base):
    """
    Транзакция.

    """

    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="transactions")
    created_at = Column(DateTime, default=datetime.now)
    amount = Column(Float, info={"verbose_name": "Сумма средств"})
    order_id = Column(String, info={"verbose_name": "ID Заказа"})
    service_id = Column(String, info={"verbose_name": "ID Услуги"})
