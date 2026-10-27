import pytest
from fastapi.testclient import TestClient

import app_final
from app_final import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_storage():
    app_final.expenses.clear()
    app_final.next_id = 1


def create(amount, category, description=None):
    response = client.post(
        "/expenses",
        json={"amount": amount, "category": category, "description": description},
    )
    assert response.status_code == 201
    return response.json()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version():
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": app_final.APP_VERSION}


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == app_final.APP_NAME
    assert response.json()["docs"] == "/docs"


def test_create_and_get_expense():
    created = create(350.5, "food", "Обед")

    response = client.get(f"/expenses/{created['id']}")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "amount": 350.5,
        "category": "food",
        "description": "Обед",
    }


def test_filter_by_category():
    create(100, "food")
    create(60, "transport")

    response = client.get("/expenses", params={"category": "FOOD"})

    assert response.status_code == 200
    assert [e["category"] for e in response.json()] == ["food"]


def test_get_missing_expense_returns_404():
    response = client.get("/expenses/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Расход 999 не найден"


def test_negative_amount_returns_422():
    response = client.post("/expenses", json={"amount": -5, "category": "food"})

    assert response.status_code == 422


def test_delete_expense():
    created = create(100, "food")

    response = client.delete(f"/expenses/{created['id']}")

    assert response.status_code == 200
    assert client.get(f"/expenses/{created['id']}").status_code == 404


def test_stats():
    create(350.5, "Food")
    create(350, "food")
    create(60, "transport")

    response = client.get("/stats")

    assert response.status_code == 200
    assert response.json() == {
        "currency": app_final.CURRENCY,
        "count": 3,
        "total": 760.5,
        "by_category": {"food": 700.5, "transport": 60.0},
    }
