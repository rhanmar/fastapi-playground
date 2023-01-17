from pydantic import BaseModel


class UserSchema(BaseModel):
    """
    Схема Пользователя.

    """

    id: int
    balance: float
    reserve: float

    class Config:
        orm_mode = True
