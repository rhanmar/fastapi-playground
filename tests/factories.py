import factory
from db.models import User


def user_factory(session):
    class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
        """
        Фабрика Пользователя.

        """

        name = factory.Faker("first_name")

        class Meta:
            model = User
            sqlalchemy_session = session

    return UserFactory
