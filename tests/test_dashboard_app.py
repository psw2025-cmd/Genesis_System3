"""
Backend inner-route tests for dashboard/backend/app.py.

These tests intentionally exercise legacy handler mechanics directly. Production
Cloud Run launches dashboard.backend.secure_app, whose outer MutationPolicy is
tested separately and blocks public writes before these handlers are reachable.
Dashboard credential environment flags are retired and are not configured here.
"""

import asyncio
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(scope="module")
def app():
    # Load the inner app for handler-level regression tests only. Dashboard auth
    # is not a supported switch; production authority is secure_app + MutationPolicy.
    spec = importlib.util.spec_from_file_location(
        "dashboard_backend_app_under_test", ROOT_DIR / "dashboard" / "backend" / "app.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.app


async def _call(app, method: str, path: str, headers=None, json_body=None):
    body = b""
    request_headers = list(headers or [])
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        request_headers.append((b"content-type", b"application/json"))

    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": request_headers,
        "query_string": b"",
    }
    sent_body = {"sent": False}

    async def receive():
        if sent_body["sent"]:
            return {"type": "http.request", "body": b"", "more_body": False}
        sent_body["sent"] = True
        return {"type": "http.request", "body": body, "more_body": False}

    messages = []

    async def send(message):
        messages.append(message)

    await app(scope, receive, send)

    start = next(m for m in messages if m["type"] == "http.response.start")
    response_body = b"".join(m["body"] for m in messages if m["type"] == "http.response.body")
    return start["status"], dict(start.get("headers") or []), response_body


def call(app, method, path, **kwargs):
    return asyncio.run(_call(app, method, path, **kwargs))


def route_endpoint(app, method: str, path: str):
    """Return an exact FastAPI route endpoint for direct inner-gate tests."""
    for route in app.routes:
        methods = getattr(route, "methods", set()) or set()
        if route.path == path and method.upper() in methods:
            return route.endpoint
    raise AssertionError(f"Route not found: {method} {path}")


def test_health_endpoint_returns_200(app):
    status, _, body = call(app, "GET", "/api/health")
    assert status == 200
    data = json.loads(body)
    assert "mode" in data
    assert "broker_status" in data


def test_state_endpoint_returns_200(app):
    status, _, body = call(app, "GET", "/api/state")
    assert status == 200
    data = json.loads(body)
    assert "state_version" in data


def test_kill_switch_status_endpoint(app):
    status, _, body = call(app, "GET", "/api/kill-switch/status")
    assert status == 200
    data = json.loads(body)
    assert data["status"] in ("OK", "KILL", "ERROR")


def test_metrics_endpoint_is_prometheus_text(app):
    call(app, "GET", "/api/health")
    status, headers, body = call(app, "GET", "/metrics")
    assert status == 200
    text = body.decode()
    assert "# TYPE system3_up gauge" in text
    assert "system3_up 1" in text
    assert "system3_http_requests_total" in text


def test_request_id_header_present_on_every_response(app):
    status, headers, _ = call(app, "GET", "/api/health")
    assert status == 200
    assert b"x-request-id" in headers


def test_order_create_rejected_when_approval_not_signed_off(app, monkeypatch):
    try:
        import dashboard.backend.human_approval_service as approval_mod
    except ImportError:
        import human_approval_service as approval_mod

    monkeypatch.setattr(
        approval_mod,
        "build_approval_status",
        lambda: {"human_approval": False, "note": "test override"},
    )

    endpoint = route_endpoint(app, "POST", "/api/orders/create")
    data = asyncio.run(
        endpoint(
            {
                "symbol": "NIFTY",
                "order_type": "MARKET",
                "quantity": 1,
            }
        )
    )
    assert data["status"] == "ERROR"
    assert (
        "approval" in data["message"].lower()
        or "approval" in str(data.get("approval", "")).lower()
    )


def test_order_create_rejected_when_kill_switch_active(app, monkeypatch, tmp_path):
    kill_file = tmp_path / "kill_switch.json"
    kill_file.write_text(json.dumps({"kill": True}))

    try:
        import core.engine.system3_phase113_kill_switch_monitor as ks_mod
    except ImportError:
        pytest.skip("kill switch monitor module not importable in this environment")

    monkeypatch.setattr(ks_mod, "KILL_SWITCH_JSON", kill_file)

    endpoint = route_endpoint(app, "POST", "/api/orders/create")
    data = asyncio.run(
        endpoint(
            {
                "symbol": "NIFTY",
                "order_type": "MARKET",
                "quantity": 1,
            }
        )
    )
    assert data["status"] == "ERROR"
    assert "kill switch" in data["message"].lower()
