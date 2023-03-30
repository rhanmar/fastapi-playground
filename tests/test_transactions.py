from fastapi import status
from db.models import User, Transaction
from .factories import transaction_factory, user_factory
from datetime import datetime, timedelta


def test_transaction_list(test_db, client, db_session, url_transactions_list):
    transactions = [transaction_factory(db_session).create() for _ in range(10)]
    db_session.commit()
    assert db_session.query(Transaction).count() == len(transactions)
    assert db_session.query(User).count() == len(transactions)
    response = client.get(url_transactions_list)
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


def test_transaction_detail(test_db, client, db_session, url_transactions_detail):
    transaction = transaction_factory(db_session).create()
    db_session.commit()
    url = url_transactions_detail.format(transaction.id)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    transaction_json = response.json()
    assert "id" in transaction_json
    assert "user_id" in transaction_json
    assert "amount" in transaction_json
    assert "order_id" in transaction_json
    assert "service_id" in transaction_json
    assert "created_at" in transaction_json


def test_transaction_detail_error(test_db, client, db_session, url_transactions_detail):
    wrong_id = 404
    url = url_transactions_detail.format(wrong_id)
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Транзакция с ID {wrong_id} не найдена."}


def test_transaction_list_filters(test_db, client, db_session, url_transactions_list):
    user1 = user_factory(db_session).create()
    user2 = user_factory(db_session).create()
    amount1 = 10
    amount2 = 20
    amount3 = 30

    now = datetime.now()
    created_at1 = now + timedelta(days=1)
    created_at2 = now + timedelta(days=2)
    created_at3 = now + timedelta(days=3)
    transaction1 = transaction_factory(db_session).create(
        user=user1, amount=amount1, created_at=created_at1
    )
    transaction2 = transaction_factory(db_session).create(
        user=user1, amount=amount3, created_at=created_at3
    )
    transaction3 = transaction_factory(db_session).create(
        user=user1, amount=amount2, created_at=created_at2
    )
    transaction4 = transaction_factory(db_session).create(
        user=user2, amount=amount2, created_at=created_at1
    )
    db_session.commit()

    response = client.get(url_transactions_list + f"?user_id={user1.id}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3

    response = client.get(url_transactions_list + f"?user_id={user2.id}")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1

    response = client.get(url_transactions_list + "?sort_by_amount=True")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 4

    response = client.get(
        url_transactions_list + f"?user_id={user1.id}&sort_by_amount=True"
    )
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert len(res_json) == 3
    assert res_json[0]["id"] == transaction2.id
    assert res_json[1]["id"] == transaction3.id
    assert res_json[2]["id"] == transaction1.id

    response = client.get(url_transactions_list + "?sort_by_date=True")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 4

    response = client.get(
        url_transactions_list + f"?user_id={user1.id}&sort_by_date=True"
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3
    assert res_json[0]["id"] == transaction2.id
    assert res_json[1]["id"] == transaction3.id
    assert res_json[2]["id"] == transaction1.id
