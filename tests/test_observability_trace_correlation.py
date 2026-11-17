import asyncio
import re
from pathlib import Path

from dashboard.backend.structured_logging import RequestIDMiddleware


async def _ok_app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})


def _run(headers):
    sent = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/health",
        "headers": headers,
    }
    asyncio.run(RequestIDMiddleware(_ok_app)(scope, receive, send))
    start = next(m for m in sent if m["type"] == "http.response.start")
    return {k.decode().lower(): v.decode() for k, v in start["headers"]}


def test_valid_w3c_traceparent_is_correlated_and_echoed():
    trace_id = "0123456789abcdef0123456789abcdef"
    parent_span = "0123456789abcdef"
    headers = _run([(b"traceparent", f"00-{trace_id}-{parent_span}-01".encode())])
    assert headers["x-trace-id"] == trace_id
    assert re.fullmatch(rf"00-{trace_id}-[0-9a-f]{{16}}-01", headers["traceparent"])
    assert parent_span not in headers["traceparent"].split("-")[2]
    assert re.fullmatch(r"[0-9a-f-]{36}", headers["x-request-id"])


def test_valid_uuid_x_trace_id_is_canonicalized_to_32_hex():
    headers = _run([(b"x-trace-id", b"12345678-1234-1234-1234-123456789abc")])
    assert headers["x-trace-id"] == "12345678123412341234123456789abc"
    assert headers["traceparent"].startswith(
        "00-12345678123412341234123456789abc-"
    )


def test_invalid_trace_and_request_headers_are_not_reflected():
    headers = _run(
        [
            (b"x-trace-id", b"not-a-trace<script>"),
            (b"x-request-id", b"bad request id with spaces"),
        ]
    )
    assert headers["x-trace-id"] != "not-a-trace<script>"
    assert re.fullmatch(r"[0-9a-f]{32}", headers["x-trace-id"])
    assert headers["x-request-id"] != "bad request id with spaces"


def test_cloud_run_launcher_uses_observability_wrapper_without_new_authority():
    launcher = Path("scripts/start_cloud_run.py").read_text(encoding="utf-8")
    wrapper = Path("dashboard/backend/observability_app.py").read_text(encoding="utf-8")
    assert '"dashboard.backend.observability_app:app"' in launcher
    assert "from dashboard.backend.secure_app import app as secure_app" in wrapper
    assert "RequestIDMiddleware(secure_app)" in wrapper
    assert "place_order" not in wrapper
    assert "modify_order" not in wrapper
    assert "cancel_order" not in wrapper
