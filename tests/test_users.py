from fastapi import status
from db.models import User
from .factories import user_factory


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
    response_accrue = client.post(url, json=data)
    assert response_accrue.status_code == status.HTTP_200_OK
    assert response_accrue.json() == {
        "info": "Средства зачислены",
        "status_code": status.HTTP_200_OK,
    }
    db_session.refresh(user)
    assert user.balance == data["money_amount"]


# test_reserve_money
# test_reserve_money_error
# payment_confirmation + transaction
# payment_confirmation_error
# reset_reserve
# reset_reserve_no_money
# transaction_list
# transaction_detail
