from fastapi import Depends, status, Body, APIRouter
from sqlalchemy.orm import Session
from app.models import User, Transaction
from app.schemas import UserSchema, UserCreateSchema
from app.dependencies import get_db, get_user

router = APIRouter(
    prefix="/api/users",
)


@router.post("/{user_id}/add_money/")
def add_money_to_account(
    money_amount: float = Body(embed=True),
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    """Начислить средства."""
    user.balance += money_amount
    db.add(user)
    db.commit()
    return {"info": "Средства зачислены", "status_code": status.HTTP_200_OK}


@router.post("/{user_id}/reserve/")
def reserve_money(
    money_amount: float = Body(embed=True),
    service_id: str = Body(embed=True, default=None),
    order_id: str = Body(embed=True, default=None),
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    """Зарезервировать средства."""
    if user.balance < money_amount:
        return {
            "info": "Недостаточно средств для резервирования",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    user.balance -= money_amount
    user.reserve += money_amount
    db.add(user)
    db.commit()
    print(f"Обработка service_id ({service_id})")
    print(f"Обработка order_id ({order_id})")
    return {"info": "Средства зарезервированы", "status_code": status.HTTP_200_OK}


@router.post("/{user_id}/confirm/")
def payment_confirmation(
    money_amount: float = Body(embed=True),
    service_id: str = Body(embed=True),
    order_id: str = Body(embed=True),
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    """Подтвердить оплату и снять указанное колияечтво денег с резерва."""
    if user.reserve < money_amount:
        return {
            "info": "В резерве недостаточно средств",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    user.reserve -= money_amount
    db.add(user)
    db.commit()

    transaction_db = Transaction(
        user_id=user.id,
        amount=money_amount,
        order_id=order_id,
        service_id=service_id,
    )
    db.add(transaction_db)
    db.commit()
    return {
        "info": f"Средства списаны с резерва. Создана Транзакция №{transaction_db.id}",
        "status_code": status.HTTP_200_OK,
    }


@router.post("/{user_id}/reset_reserve/")
def reset_reserve(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
):
    """Вернуть деньги из резерва на баланс."""
    if user.reserve <= 0:
        return {
            "info": "В резерве нет средств",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    old_reserve = user.reserve
    user.balance += user.reserve
    user.reserve = 0
    db.add(user)
    db.commit()
    return {
        "info": f"{old_reserve} средств возвращены с резерва в баланс",
        "status_code": status.HTTP_200_OK,
    }


@router.get("/{user_id}/", response_model=UserSchema)
def user_account(user: User = Depends(get_user)) -> User:
    """Получить информацию о счёте Пользователя."""
    return user


@router.get("/", response_model=list[UserSchema])
def users_list(db: Session = Depends(get_db)) -> list[User]:
    """Получить список всех Пользователей."""
    users_db = db.query(User).all()
    return users_db


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreateSchema, db: Session = Depends(get_db)
) -> dict[str, int]:
    """Создать Пользователя."""
    user_db = User(name=user.name)
    db.add(user_db)
    db.commit()
    return {"user_id": user_db.id}
