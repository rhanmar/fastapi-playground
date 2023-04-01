from fastapi import HTTPException, status

from app.services.main import AppCRUD, AppService
from app.models import User, Transaction
from app.schemas import UserCreateSchema


class UsersCRUD(AppCRUD):
    """
    CRUD для Пользователей.

    """

    def create_user(self, user: UserCreateSchema) -> User:
        """Создать Пользователя."""
        user_db = User(name=user.name)
        self.db.add(user_db)
        self.db.commit()
        return user_db

    def get_users_list(self) -> list[User]:
        """Получить список Пользователей."""
        return self.db.query(User).all()

    def get_user_by_id(self, user_id: int) -> User | None:
        """Получить Пользователя по ID."""
        user_db = self.db.query(User).filter_by(id=user_id).first()
        if not user_db:
            return None
        return user_db

    def get_user_by_id_or_404(self, user_id: int) -> User | None:
        """Получить Пользователя по ID или выброчить исключение."""
        user_db = self.db.query(User).filter_by(id=user_id).first()
        if not user_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {user_id} не найден.",
            )
        return user_db


class UsersService(AppService):
    """
    Сервис Пользователей.

    """

    def create_user(self, user: UserCreateSchema) -> dict:
        """Создать Пользователя."""
        user_db = UsersCRUD(db=self.db).create_user(user)
        return {"user_id": user_db.id}

    def get_users_list(self) -> list[User]:
        """Получить список Пользователей."""
        return UsersCRUD(db=self.db).get_users_list()

    def get_user_by_id(self, user_id: int) -> User:
        """Получить Пользователя по ID."""
        user_db = UsersCRUD(db=self.db).get_user_by_id_or_404(user_id)
        return user_db

    def reset_reserve(self, user_id: int) -> dict:
        """Перенести все деньги из резерва в баланс."""
        user_db = UsersCRUD(db=self.db).get_user_by_id_or_404(user_id)
        if user_db.reserve <= 0:
            return {
                "info": "В резерве нет средств",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        old_reserve = user_db.reserve
        user_db.balance += user_db.reserve
        user_db.reserve = 0
        self.db.add(user_db)
        self.db.commit()
        return {
            "info": f"{old_reserve} средств возвращены с резерва в баланс",
            "status_code": status.HTTP_200_OK,
        }

    def confirm_payment(
        self, user_id: int, money_amount: float, service_id: str, order_id: str
    ) -> dict:
        """Подтвердить оплату, снять указанное количество средств с резерва и создать Транзакцию."""
        user_db = UsersCRUD(db=self.db).get_user_by_id_or_404(user_id)
        if user_db.reserve < money_amount:
            return {
                "info": "В резерве недостаточно средств",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        user_db.reserve -= money_amount
        self.db.add(user_db)
        self.db.commit()

        transaction_db = Transaction(
            user_id=user_db.id,
            amount=money_amount,
            order_id=order_id,
            service_id=service_id,
        )
        self.db.add(transaction_db)
        self.db.commit()
        return {
            "info": f"Средства списаны с резерва. Создана Транзакция №{transaction_db.id}",
            "status_code": status.HTTP_200_OK,
        }

    def reserve_money(
        self, user_id: int, money_amount: float, service_id: str, order_id: str
    ) -> dict:
        """Зарезервировать средства."""
        user_db = UsersCRUD(db=self.db).get_user_by_id_or_404(user_id)
        if user_db.balance < money_amount:
            return {
                "info": "Недостаточно средств для резервирования",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        user_db.balance -= money_amount
        user_db.reserve += money_amount
        self.db.add(user_db)
        self.db.commit()
        print(f"Обработка service_id ({service_id})")
        print(f"Обработка order_id ({order_id})")
        return {"info": "Средства зарезервированы", "status_code": status.HTTP_200_OK}

    def add_money_to_account(self, user_id: int, money_amount: float) -> dict:
        """Зачислить средства на баланс."""
        user_db = UsersCRUD(db=self.db).get_user_by_id_or_404(user_id)
        user_db.balance += money_amount
        self.db.add(user_db)
        self.db.commit()
        return {"info": "Средства зачислены", "status_code": status.HTTP_200_OK}
