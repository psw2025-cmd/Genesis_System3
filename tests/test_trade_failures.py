from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_trade_missing_order_id():
    response = client.post(
        "/api/audit/trades",
        json={
            "broker": "DHAN"
        }
    )
    assert response.status_code == 422


def test_trade_negative_quantity():
    response = client.post(
        "/api/audit/trades",
        json={
            "order_id": "ORD1",
            "broker": "DHAN",
            "exchange": "NSE",
            "symbol": "RELIANCE",
            "side": "BUY",
            "quantity": -100,
            "price": 2500,
            "execution_status": "OPEN"
        }
    )
    assert response.status_code == 422
