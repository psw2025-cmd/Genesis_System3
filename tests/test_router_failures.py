from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_invalid_post_payload():
    response = client.post(
        "/api/audit/post",
        json={}
    )
    assert response.status_code == 422


def test_invalid_status_code():
    response = client.post(
        "/api/audit/post",
        json={
            "endpoint": "/api/order",
            "initiated_by": "agent",
            "initiated_type": "agent",
            "request_hash": "x",
            "request_payload": {},
            "response_payload": {},
            "response_code": 999,
            "latency_ms": 10,
            "success": True
        }
    )
    assert response.status_code == 422


def test_negative_latency():
    response = client.post(
        "/api/audit/post",
        json={
            "endpoint": "/api/order",
            "initiated_by": "agent",
            "initiated_type": "agent",
            "request_hash": "x",
            "request_payload": {},
            "response_payload": {},
            "response_code": 200,
            "latency_ms": -100,
            "success": True
        }
    )
    assert response.status_code == 422
