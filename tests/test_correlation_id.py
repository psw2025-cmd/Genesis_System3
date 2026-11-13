from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_correlation_id_header_present():
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Correlation-ID" in response.headers
