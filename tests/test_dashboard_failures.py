from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app, raise_server_exceptions=False)


def test_dashboard_db_failure():
    with patch("audit.router.service.get_post_stats", side_effect=Exception("db error")), \
         patch("audit.service.get_post_stats", side_effect=Exception("db error")):
        response = client.get("/api/audit/dashboard/summary")
        assert response.status_code == 500
