from pydantic import BaseModel


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
