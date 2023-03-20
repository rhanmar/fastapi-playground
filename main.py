from fastapi import FastAPI, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from db import models
from db.database import engine
from db.database import SessionLocal
from db.schemas import UserSchema


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db() -> SessionLocal:
    """Получить сессию БД из запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(user_id: int, db: Session = Depends(get_db)) -> models.User:
    """Получить пользователя из запроса."""
    user_db = db.query(models.User).filter_by(id=user_id).first()
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден.",
        )
    return user_db


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/users/{user_id}/add_money/")
def add_money_to_account(
    money_amount: float = Body(embed=True),
    user: models.User = Depends(get_user),
    db: Session = Depends(get_db),
):
    """Начислить средства."""
    user.balance += money_amount
    db.add(user)
    db.commit()
    return {"info": "Средства зачислены", "status_code": status.HTTP_200_OK}


@app.post("/api/users/{user_id}/reserve/")
def reserve_money(
    money_amount: float = Body(embed=True),
    service_id: str = Body(embed=True, default=None),
    order_id: str = Body(embed=True, default=None),
    user: models.User = Depends(get_user),
    db: Session = Depends(get_db),
):
    """Зарезервировать средства."""
    if user.balance < money_amount:
        return {
            "info": "Недостаточно средств для резервации",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        }
    user.balance -= money_amount
    user.reserve = money_amount
    db.add(user)
    db.commit()
    print(f"Обработка service_id ({service_id})")
    print(f"Обработка order_id ({order_id})")
    return {"info": "Средства зарезервированы", "status_code": status.HTTP_200_OK}


@app.post("/api/users/{user_id}/reserve/")
def payment_confirmation(
    money_amount: float = Body(embed=True),
    service_id: str = Body(embed=True, default=None),
    order_id: str = Body(embed=True, default=None),
    user: models.User = Depends(get_user),
    db: Session = Depends(get_db),
):
    """Подтвердить оплату и снять деньги с резерва."""
    user.reserve = 0
    db.add(user)
    db.commit()
    print(f"Обработка service_id ({service_id})")
    print(f"Обработка order_id ({order_id})")
    print(f"{money_amount} будет передано в бухгалтерию")
    return {"info": "Средства зарезервированы", "status_code": status.HTTP_200_OK}


@app.get("/api/users/{user_id}", response_model=UserSchema)
def user_account(user: models.User = Depends(get_user)) -> models.User:
    """Получить информацию о счёте Пользователя."""
    return user


@app.get("/api/users/", response_model=list[UserSchema])
def users_list(db: Session = Depends(get_db)) -> list[models.User]:
    """Получить список всех Пользователей."""
    users_db = db.query(models.User).all()
    return users_db


@app.post("/api/users/", status_code=status.HTTP_201_CREATED)
def create_user(db: Session = Depends(get_db)) -> dict[str, int]:
    """Создать Пользователя."""
    user_db = models.User()
    db.add(user_db)
    db.commit()
    return {"user_id": user_db.id}