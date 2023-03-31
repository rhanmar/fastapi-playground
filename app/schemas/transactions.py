from datetime import datetime

from pydantic import BaseModel


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
