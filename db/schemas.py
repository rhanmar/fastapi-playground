from pydantic import BaseModel


class UserSchema(BaseModel):
    """
    Схема Пользователя.

    """

    id: int
    name: str = None
    balance: float
    reserve: float

    class Config:
        orm_mode = True


class UserCreateSchema(BaseModel):
    """
    Схема создания Пользователя.

    """

    name: str

    class Config:
        orm_mode = True
