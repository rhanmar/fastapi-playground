from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship

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


class Order(Base):
    """
    Заказ.

    """

    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)


class Service(Base):
    """
    Услуга.

    """

    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)


# class Balance(Base):
#     """
#     Баланс.
#
#     """
#
#     __tablename__ = "balances"
#     id = Column(Integer, primary_key=True, index=True)
#
#
# class Reserve(Base):
#     """
#     Резерв.
#
#     """
#
#     __tablename__ = "reserves"
#     id = Column(Integer, primary_key=True, index=True)
#
