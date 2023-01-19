from fastapi import status
from db.models import User


def test_create_user(test_db, client, db_session, url_users_list):
    assert db_session.query(User).count() == 0
    response = client.post(url_users_list)
    assert response.status_code == status.HTTP_201_CREATED
    user_id = response.json()["user_id"]
    assert db_session.query(User).count() == 1
    assert db_session.query(User).first().id == user_id


def test_user_list(test_db, client, db_session, url_users_list):
    response_create = client.post(url_users_list)
    assert response_create.status_code == status.HTTP_201_CREATED
    user_id = response_create.json()["user_id"]
    response_list = client.get(url_users_list)
    assert response_list.status_code == status.HTTP_200_OK
    res_json = response_list.json()
    for user_json in res_json:
        assert "id" in user_json
        assert "balance" in user_json
        assert "reserve" in user_json

    user_json = res_json[0]
    user_db = db_session.query(User).filter_by(id=user_id).first()
    assert user_json["id"] == user_db.id
    assert user_json["balance"] == user_db.balance
    assert user_json["reserve"] == user_db.reserve


def test_user_account(test_db, client, db_session, url_users_list, url_users_detail):
    response_create = client.post(url_users_list)
    assert response_create.status_code == status.HTTP_201_CREATED
    user_id = response_create.json()["user_id"]
    response_account = client.get(url_users_detail.format(user_id))
    assert response_account.status_code == status.HTTP_200_OK
    user_json = response_account.json()
    user_db = db_session.query(User).filter_by(id=user_id).first()
    assert user_json["id"] == user_db.id
    assert user_json["balance"] == user_db.balance
    assert user_json["reserve"] == user_db.reserve


def test_accrue_funds(test_db, client, db_session, url_users_list, url_users_detail):
    response_create = client.post(url_users_list)
    assert response_create.status_code == status.HTTP_201_CREATED
    user_id = response_create.json()["user_id"]
    data = {
        "funds_amount": 100.111,
    }
    response_accrue = client.patch(url_users_detail.format(user_id), json=data)
    assert response_accrue.status_code == status.HTTP_200_OK
    assert response_accrue.json()["info"] == "Средства зачислены"
    user_db = db_session.query(User).filter_by(id=user_id).first()
    assert user_db.balance == data["funds_amount"]
