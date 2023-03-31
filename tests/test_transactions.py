from fastapi import status
from app.models import User, Transaction
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


def test_transactions_services_statistics(test_db, client, db_session):
    service_id_1 = "111"
    service_id_2 = "222"
    amounts_1 = [2, 4, 6]
    transaction11 = transaction_factory(db_session).create(
        service_id=service_id_1, amount=amounts_1[0]
    )
    transaction12 = transaction_factory(db_session).create(
        service_id=service_id_1, amount=amounts_1[1]
    )
    transaction13 = transaction_factory(db_session).create(
        service_id=service_id_1, amount=amounts_1[2]
    )
    transactions1 = [transaction11, transaction12, transaction13]
    amounts_2 = [3, 6]
    transaction21 = transaction_factory(db_session).create(
        service_id=service_id_2, amount=amounts_2[0]
    )
    transaction22 = transaction_factory(db_session).create(
        service_id=service_id_2, amount=amounts_2[1]
    )
    transactions2 = [transaction21, transaction22]
    db_session.commit()
    assert db_session.query(Transaction).count() == len(transactions1) + len(
        transactions2
    )

    url = "/api/transactions/services_statistics/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert len(res_json) == 2
    for item_json in res_json:
        match item_json["service_id"]:
            case "111":  # service_id_1
                assert item_json["count"] == len(transactions1)
                assert item_json["sum"] == sum(amounts_1)
            case "222":  # service_id_2
                assert item_json["count"] == len(transactions2)
                assert item_json["sum"] == sum(amounts_2)


def test_transactions_services_statistics_with_dates(test_db, client, db_session):
    service_id_1 = "111"
    service_id_2 = "222"
    amounts_1 = [2, 4, 6]
    amounts_1_avoided = [8, 10]
    now = datetime.now()
    last_year_dt = now - timedelta(days=400)
    two_years_ago_dt = now - timedelta(days=800)
    transaction11 = transaction_factory(db_session).create(
        service_id=service_id_1, amount=amounts_1[0], created_at=now
    )
    transaction12 = transaction_factory(db_session).create(
        service_id=service_id_1, amount=amounts_1[1], created_at=now
    )
    transaction13 = transaction_factory(db_session).create(
        service_id=service_id_1, amount=amounts_1[2], created_at=now
    )
    transaction14_avoided = transaction_factory(db_session).create(
        service_id=service_id_1, amount=amounts_1_avoided[0], created_at=last_year_dt
    )
    transaction15_avoided = transaction_factory(db_session).create(
        service_id=service_id_1,
        amount=amounts_1_avoided[1],
        created_at=two_years_ago_dt,
    )
    transactions1 = [transaction11, transaction12, transaction13]
    amounts_2 = [3, 6]
    amounts_2_avoided = [9, 12]
    transaction21 = transaction_factory(db_session).create(
        service_id=service_id_2, amount=amounts_2[0]
    )
    transaction22 = transaction_factory(db_session).create(
        service_id=service_id_2, amount=amounts_2[1]
    )
    transaction23_avoided = transaction_factory(db_session).create(
        service_id=service_id_2, amount=amounts_2_avoided[0], created_at=last_year_dt
    )
    transaction24_avoided = transaction_factory(db_session).create(
        service_id=service_id_2,
        amount=amounts_2_avoided[1],
        created_at=two_years_ago_dt,
    )
    transactions2 = [transaction21, transaction22]
    db_session.commit()

    url = f"/api/transactions/services_statistics/?month={now.month}&year={now.year}"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert len(res_json) == 2
    for item_json in res_json:
        match item_json["service_id"]:
            case "111":  # service_id_1
                assert item_json["count"] == len(transactions1)
                assert item_json["sum"] == sum(amounts_1)
            case "222":  # service_id_2
                assert item_json["count"] == len(transactions2)
                assert item_json["sum"] == sum(amounts_2)
