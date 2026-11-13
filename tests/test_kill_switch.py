from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_kill_switch_endpoint():
    response = client.get("/api/audit/kill-switch/status")
    assert response.status_code == 200
    data = response.json()
    assert data["armed"] is True
