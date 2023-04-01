from fastapi import Depends, status, Body, APIRouter
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserSchema, UserCreateSchema
from app.config.database import get_db
from app.services import UsersService

router = APIRouter(
    prefix="/api/users",
)


@router.post("/{user_id}/add_money/")
def add_money_to_account(
    user_id: int,
    money_amount: float = Body(embed=True),
    db: Session = Depends(get_db),
) -> dict:
    """Зачислить средства на баланс."""
    return UsersService(db=db).add_money_to_account(user_id, money_amount)


@router.post("/{user_id}/reserve/")
def reserve_money(
    user_id: int,
    money_amount: float = Body(embed=True),
    service_id: str = Body(embed=True, default=None),
    order_id: str = Body(embed=True, default=None),
    db: Session = Depends(get_db),
) -> dict:
    """Зарезервировать средства."""
    return UsersService(db=db).reserve_money(
        user_id=user_id,
        money_amount=money_amount,
        service_id=service_id,
        order_id=order_id,
    )


@router.post("/{user_id}/confirm/")
def confirm_payment(
    user_id: int,
    money_amount: float = Body(embed=True),
    service_id: str = Body(embed=True),
    order_id: str = Body(embed=True),
    db: Session = Depends(get_db),
) -> dict:
    """Подтвердить оплату, снять указанное количество средств с резерва и создать Транзакцию."""
    return UsersService(db=db).confirm_payment(
        user_id=user_id,
        money_amount=money_amount,
        service_id=service_id,
        order_id=order_id,
    )


@router.post("/{user_id}/reset_reserve/")
def reset_reserve(
    user_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Перенести все деньги из резерва в баланс."""
    return UsersService(db=db).reset_reserve(user_id)


@router.get("/{user_id}/", response_model=UserSchema)
def user_account(user_id: int, db: Session = Depends(get_db)) -> User:
    """Получить информацию о счёте Пользователя."""
    return UsersService(db=db).get_user_by_id(user_id)


@router.get("/", response_model=list[UserSchema])
def users_list(db: Session = Depends(get_db)) -> list[User]:
    """Получить список всех Пользователей."""
    return UsersService(db=db).get_users_list()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreateSchema, db: Session = Depends(get_db)
) -> dict[str, int]:
    """Создать Пользователя."""
    return UsersService(db=db).create_user(user)
