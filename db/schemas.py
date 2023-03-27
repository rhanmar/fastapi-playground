from datetime import datetime

from pydantic import BaseModel, validator


class UserSchema(BaseModel):
    """
    Схема Пользователя.

    """

    id: int
    name: str = None
    balance: float
    reserve: float
    transactions_count: int = None
    transactions_sum_amount: float = None
    transactions_avg_amount: float = None
    transactions_min_amount: float = None
    transactions_max_amount: float = None

    class Config:
        orm_mode = True


class UserCreateSchema(BaseModel):
    """
    Схема создания Пользователя.

    """

    name: str

    class Config:
        orm_mode = True


class TransactionSchema(BaseModel):
    """
    Схема Транзакции.

    """

    id: int
    user_id: int
    amount: float
    order_id: str
    service_id: str
    created_at: datetime

    class Config:
        orm_mode = True
