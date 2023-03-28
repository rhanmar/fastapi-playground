from fastapi import status
from db.models import User, Transaction
from .factories import transaction_factory


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


def test_transaction_detail_error(test_db, client, db_session):
    wrong_id = 404
    url = f"/api/transactions/{wrong_id}"
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Транзакция с ID {wrong_id} не найдена."}
