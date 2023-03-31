import factory
from app.models import User, Transaction


def user_factory(session):
    class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
        """
        Фабрика Пользователя.

        """

        name = factory.Faker("word")

        class Meta:
            model = User
            sqlalchemy_session = session

    return UserFactory


def transaction_factory(session):
    class TransactionFactory(factory.alchemy.SQLAlchemyModelFactory):
        """
        Фабрика Транзакции.

        """

        user = factory.SubFactory(user_factory(session))
        amount = factory.Sequence(lambda x: x + 10)
        order_id = factory.Sequence(lambda x: str(f"ID {x}"))
        service_id = factory.Sequence(lambda x: str(f"ID {x}"))

        class Meta:
            model = Transaction
            sqlalchemy_session = session

    return TransactionFactory
