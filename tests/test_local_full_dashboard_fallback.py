from pathlib import Path
from fastapi.testclient import TestClient
from content.app.app import app


def test_legacy_full_dashboard_replaces_autoreload_placeholder():
    response = TestClient(app).get('/ui')
    assert response.status_code == 200
    assert len(response.content) > 10000
    assert 'Auto-reload active every 2s' not in response.text
    assert '<html' in response.text.lower()


def test_local_dashboard_source_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / 'dashboard' / 'index.html').stat().st_size > 10000
