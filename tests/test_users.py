from fastapi import status
from db.models import User, Transaction
from .factories import user_factory, transaction_factory


def test_create_user(test_db, client, db_session, url_users_list):
    assert db_session.query(User).count() == 0
    data = {
        "name": "name1",
    }
    response = client.post(url_users_list, json=data)
    assert response.status_code == status.HTTP_201_CREATED
    user_id = response.json()["user_id"]
    assert db_session.query(User).count() == 1
    user_db = db_session.query(User).first()
    assert user_db.id == user_id
    assert user_db.name == data["name"]


def test_users_list(test_db, client, db_session, url_users_list):
    users = [user_factory(db_session).create() for _ in range(5)]
    db_session.commit()
    assert db_session.query(User).count() == len(users)

    response = client.get(url_users_list)
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    for user_json in res_json:
        assert "id" in user_json
        assert "name" in user_json
        assert "balance" in user_json
        assert "reserve" in user_json
        assert "transactions_count" in user_json
        assert "transactions_sum_amount" in user_json
        assert "transactions_avg_amount" in user_json
        assert "transactions_min_amount" in user_json
        assert "transactions_max_amount" in user_json


def test_user_account(test_db, client, db_session, url_users_detail):
    user = user_factory(db_session).create()
    db_session.commit()
    response = client.get(url_users_detail.format(user.id))
    assert response.status_code == status.HTTP_200_OK
    user_json = response.json()
    assert user_json["id"] == user.id
    assert user_json["name"] == user.name
    assert user_json["balance"] == user.balance
    assert user_json["reserve"] == user.reserve
    assert "transactions_count" in user_json
    assert "transactions_sum_amount" in user_json
    assert "transactions_avg_amount" in user_json
    assert "transactions_min_amount" in user_json
    assert "transactions_max_amount" in user_json


def test_add_money(test_db, client, db_session):
    user = user_factory(db_session).create()
    db_session.commit()
    url = f"/api/users/{user.id}/add_money/"
    data = {
        "money_amount": 50,
    }
    response = client.post(url, json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "info": "Средства зачислены",
        "status_code": status.HTTP_200_OK,
    }
    db_session.refresh(user)
    assert user.balance == data["money_amount"]


def test_reserve_money(test_db, client, db_session):
    old_balance = 100
    user = user_factory(db_session).create(balance=old_balance)
    db_session.commit()
    url = f"/api/users/{user.id}/reserve/"
    data = {
        "money_amount": 50,
        "service_id": "1",
        "order_id": "1",
    }
    response = client.post(url, json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "info": "Средства зарезервированы",
        "status_code": status.HTTP_200_OK,
    }
    db_session.refresh(user)
    assert user.reserve == data["money_amount"]
    assert user.balance == old_balance - data["money_amount"]


def test_reserve_money_error(test_db, client, db_session):
    old_balance = 10
    user = user_factory(db_session).create(balance=10)
    db_session.commit()
    url = f"/api/users/{user.id}/reserve/"
    data = {
        "money_amount": 50,
        "service_id": "1",
        "order_id": "1",
    }
    response = client.post(url, json=data)
    assert response.json() == {
        "info": "Недостаточно средств для резервирования",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    db_session.refresh(user)
    assert user.reserve == 0
    assert user.balance == old_balance


def test_payment_confirmation(test_db, client, db_session):
    old_reserve = 100
    user = user_factory(db_session).create(reserve=old_reserve)
    db_session.commit()
    url = f"/api/users/{user.id}/confirm/"
    data = {
        "money_amount": 100,
        "service_id": "1",
        "order_id": "1",
    }
    assert db_session.query(Transaction).count() == 0
    response = client.post(url, json=data)
    assert response.status_code == status.HTTP_200_OK
    assert db_session.query(Transaction).count() == 1
    transaction = db_session.query(Transaction).first()
    assert response.json() == {
        "info": f"Средства списаны с резерва. Создана Транзакция №{transaction.id}",
        "status_code": status.HTTP_200_OK,
    }
    db_session.refresh(user)
    assert user.reserve == old_reserve - data["money_amount"]
    assert transaction.service_id == data["service_id"]
    assert transaction.order_id == data["order_id"]
    assert transaction.amount == data["money_amount"]


def test_payment_confirmation_error(test_db, client, db_session):
    old_reserve = 10
    user = user_factory(db_session).create(reserve=old_reserve)
    db_session.commit()
    url = f"/api/users/{user.id}/confirm/"
    data = {
        "money_amount": 100,
        "service_id": "1",
        "order_id": "1",
    }
    assert db_session.query(Transaction).count() == 0
    response = client.post(url, json=data)
    assert db_session.query(Transaction).count() == 0
    assert response.json() == {
        "info": f"В резерве недостаточно средств",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }


def test_reset_reserve(test_db, client, db_session):
    old_reserve = 10.0
    user = user_factory(db_session).create(reserve=old_reserve)
    db_session.commit()
    url = f"/api/users/{user.id}/reset_reserve/"
    response = client.post(url)
    assert response.json() == {
        "info": f"{old_reserve} средств возвращены с резерва в баланс",
        "status_code": status.HTTP_200_OK,
    }


def test_reset_reserve_error(test_db, client, db_session):
    user = user_factory(db_session).create(reserve=0)
    db_session.commit()
    url = f"/api/users/{user.id}/reset_reserve/"
    response = client.post(url)
    assert response.json() == {
        "info": f"В резерве нет средств",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }


def test_transaction_list(test_db, client, db_session):
    transactions = [transaction_factory(db_session).create() for _ in range(10)]
    db_session.commit()
    assert db_session.query(Transaction).count() == len(transactions)
    assert db_session.query(User).count() == len(transactions)
    url = f"/api/transactions/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert len(res_json) == len(transactions)
    for transaction_json in res_json:
        assert "id" in transaction_json
        assert "user_id" in transaction_json
        assert "amount" in transaction_json
        assert "order_id" in transaction_json
        assert "service_id" in transaction_json
        assert "created_at" in transaction_json


def test_transaction_detail(test_db, client, db_session):
    transaction = transaction_factory(db_session).create()
    db_session.commit()
    url = f"/api/transactions/{transaction.id}"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    transaction_json = response.json()
    assert "id" in transaction_json
    assert "user_id" in transaction_json
    assert "amount" in transaction_json
    assert "order_id" in transaction_json
    assert "service_id" in transaction_json
    assert "created_at" in transaction_json


def test_users_list_transactions(test_db, client, db_session, url_users_list):
    users = [user_factory(db_session).create() for _ in range(5)]

    db_session.commit()
    min_amount = 10
    max_amount = 20
    for user in users:
        transaction1 = transaction_factory(db_session).create(
            user=user, amount=min_amount
        )
        transaction2 = transaction_factory(db_session).create(
            user=user, amount=max_amount
        )
        db_session.commit()

    assert db_session.query(User).count() == len(users)

    response = client.get(url_users_list)
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    for user_json in res_json:
        assert user_json["transactions_count"] == 2
        assert user_json["transactions_sum_amount"] == min_amount + max_amount
        assert user_json["transactions_avg_amount"] == (min_amount + max_amount) / 2
        assert user_json["transactions_min_amount"] == min_amount
        assert user_json["transactions_max_amount"] == max_amount


def test_users_account_transactions(test_db, client, db_session, url_users_detail):
    user = user_factory(db_session).create()
    db_session.commit()
    min_amount = 10
    max_amount = 20
    transaction1 = transaction_factory(db_session).create(user=user, amount=min_amount)
    transaction2 = transaction_factory(db_session).create(user=user, amount=max_amount)
    db_session.commit()

    response = client.get(url_users_detail.format(user.id))
    assert response.status_code == status.HTTP_200_OK
    user_json = response.json()
    assert user_json["transactions_count"] == 2
    assert user_json["transactions_sum_amount"] == min_amount + max_amount
    assert user_json["transactions_avg_amount"] == (min_amount + max_amount) / 2
    assert user_json["transactions_min_amount"] == min_amount
    assert user_json["transactions_max_amount"] == max_amount
