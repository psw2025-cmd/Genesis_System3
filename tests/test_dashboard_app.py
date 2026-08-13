"""
Backend route tests for dashboard/backend/app.py.

Uses raw ASGI calls rather than starlette.testclient.TestClient, since
that requires a package ("httpx2") not present in this project's
dependency set - confirmed missing during this session rather than
adding a new test-only dependency for it.
"""

import asyncio
import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(scope="module")
def app():
    import os
    old_val = os.environ.get("REQUIRE_API_KEY")
    os.environ["REQUIRE_API_KEY"] = "false"
    try:
        spec = importlib.util.spec_from_file_location(
            "dashboard_backend_app_under_test", ROOT_DIR / "dashboard" / "backend" / "app.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.app
    finally:
        if old_val is not None:
            os.environ["REQUIRE_API_KEY"] = old_val
        else:
            os.environ.pop("REQUIRE_API_KEY", None)


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


def test_multibagger_contract_is_truthful_pending_without_evidence(app):
    status, _, body = call(app, "GET", "/api/research/multibagger")
    assert status == 200
    data = json.loads(body)
    assert data["schema_version"] == "1.0.0"
    assert data["status"] == "pending"
    assert data["candidates"] == []
    assert data["sections"]["candidate_ranking"] == "pending"
    assert data["safety"] == {"read_only": True, "orders_enabled": False}


def test_multibagger_contract_requires_price_and_model_provenance(app):
    endpoint = route_endpoint(app, "GET", "/api/research/multibagger")
    now = datetime.now(timezone.utc).isoformat()
    result = endpoint.__globals__["_build_multibagger_contract"]({
        "as_of": now, "source": "GENESIS_FORECAST_EVALUATOR",
        "candidates": [{"candidate_id": "c-1", "symbol": "RELIANCE", "rank": 1, "price": {"value": 100}}]
    })
    assert result["status"] == "pending"
    assert result["validation"]["accepted"] == 0
    assert "PRICE_PROVENANCE_REQUIRED" in result["validation"]["rejections"][0]["reason"]
    assert "MODEL_PROVENANCE_REQUIRED" in result["validation"]["rejections"][0]["reason"]


def test_multibagger_contract_exposes_only_validated_partial_evidence(app):
    endpoint = route_endpoint(app, "GET", "/api/research/multibagger")
    now = datetime.now(timezone.utc).isoformat()
    result = endpoint.__globals__["_build_multibagger_contract"]({
        "as_of": now,
        "source": "GENESIS_FORECAST_EVALUATOR",
        "candidates": [{
            "candidate_id": "c-1", "symbol": "reliance", "rank": 1,
            "price": {"value": 1500.5, "currency": "inr", "source": "DHAN", "observed_at": now, "secret": "drop"},
            "model": {"name": "gain-rank", "version": "2026.08", "scoring_method": "rank_score", "generated_at": now, "internal": "drop"},
            "extra": "drop",
        }],
    })
    assert result["status"] == "partial"
    assert result["sections"]["candidate_ranking"] == "partial"
    assert result["sections"]["probability_ladder"] == "pending"
    assert result["candidates"][0]["symbol"] == "RELIANCE"
    assert result["candidates"][0]["price"]["source"] == "DHAN"
    assert result["candidates"][0]["model"]["proof_ready"] is False
    assert result["candidates"][0]["model"]["evidence_status"] == "unverified"
    assert "extra" not in result["candidates"][0]
    assert "secret" not in result["candidates"][0]["price"]
    assert "internal" not in result["candidates"][0]["model"]
    assert result["validation"] == {"accepted": 1, "rejected": 0, "rejections": []}


def test_multibagger_contract_rejects_bad_rank_duplicates_and_unapproved_price_source(app):
    build = route_endpoint(app, "GET", "/api/research/multibagger").__globals__["_build_multibagger_contract"]
    now = datetime.now(timezone.utc).isoformat()
    def row(candidate_id, symbol, rank, source="DHAN"):
        return {"candidate_id": candidate_id, "symbol": symbol, "rank": rank,
                "price": {"value": 10, "currency": "INR", "source": source, "observed_at": now},
                "model": {"name": "m", "version": "1", "scoring_method": "score", "generated_at": now}}
    result = build({"as_of": now, "source": "GENESIS_FORECAST_EVALUATOR", "candidates": [
        row("a", "AAA", 1), row("a", "BBB", 2), row("c", "AAA", 3),
        row("d", "DDD", 1), row("e", "EEE", 1.5), row("f", "FFF", 6, "CSV"),
    ]})
    reasons = "|".join(item["reason"] for item in result["validation"]["rejections"])
    assert result["validation"]["accepted"] == 1
    assert "DUPLICATE_CANDIDATE_OR_SYMBOL" in reasons
    assert "DUPLICATE_RANK" in reasons
    assert "POSITIVE_INTEGRAL_RANK_REQUIRED" in reasons
    assert "PRICE_PROVENANCE_REQUIRED" in reasons


def test_multibagger_contract_requires_approved_producer_and_fresh_aware_timestamps(app):
    build = route_endpoint(app, "GET", "/api/research/multibagger").__globals__["_build_multibagger_contract"]
    assert build({"as_of": datetime.now(timezone.utc).isoformat(), "source": "UNKNOWN", "candidates": []})["reason"] == "PRODUCER_SOURCE_UNVERIFIED"
    assert build({"as_of": "2026-08-14T10:00:00", "source": "GENESIS_FORECAST_EVALUATOR", "candidates": []})["reason"] == "INVALID_OR_FUTURE_AS_OF"
    future = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    assert build({"as_of": future, "source": "GENESIS_FORECAST_EVALUATOR", "candidates": []})["reason"] == "INVALID_OR_FUTURE_AS_OF"


def test_multibagger_contract_marks_old_envelope_stale_and_rejects_stale_candidate_evidence(app):
    build = route_endpoint(app, "GET", "/api/research/multibagger").__globals__["_build_multibagger_contract"]
    now = datetime.now(timezone.utc)
    old = (now - timedelta(hours=2)).isoformat()
    fresh = now.isoformat()
    valid = {"candidate_id": "a", "symbol": "AAA", "rank": 1,
             "price": {"value": 10, "currency": "INR", "source": "DHAN", "observed_at": fresh},
             "model": {"name": "m", "version": "1", "scoring_method": "score", "generated_at": fresh}}
    result = build({"as_of": old, "source": "GENESIS_FORECAST_EVALUATOR", "candidates": [valid]})
    assert result["status"] == "stale" and result["stale"] is True
    valid["price"]["observed_at"] = old
    result = build({"as_of": fresh, "source": "GENESIS_FORECAST_EVALUATOR", "candidates": [valid]})
    assert result["status"] == "pending"
    assert "PRICE_EVIDENCE_STALE" in result["validation"]["rejections"][0]["reason"]
    valid["price"]["observed_at"] = fresh
    valid["model"]["generated_at"] = old
    result = build({"as_of": fresh, "source": "GENESIS_FORECAST_EVALUATOR", "candidates": [valid]})
    assert "MODEL_EVIDENCE_STALE" in result["validation"]["rejections"][0]["reason"]
    valid["model"]["generated_at"] = (now + timedelta(minutes=10)).isoformat()
    result = build({"as_of": fresh, "source": "GENESIS_FORECAST_EVALUATOR", "candidates": [valid]})
    assert "MODEL_PROVENANCE_REQUIRED" in result["validation"]["rejections"][0]["reason"]


def test_multibagger_model_proof_requires_all_hashes(app):
    build = route_endpoint(app, "GET", "/api/research/multibagger").__globals__["_build_multibagger_contract"]
    now = datetime.now(timezone.utc).isoformat()
    row = {"candidate_id": "a", "symbol": "AAA", "rank": 1,
           "price": {"value": 10, "currency": "INR", "source": "DHAN", "observed_at": now},
           "model": {"name": "m", "version": "1", "scoring_method": "score", "generated_at": now,
                     "proof": {"artifact_sha256": "a" * 64, "data_sha256": "b" * 64, "code_sha": "c" * 40}}}
    result = build({"as_of": now, "source": "GENESIS_FORECAST_EVALUATOR", "candidates": [row]})
    model = result["candidates"][0]["model"]
    assert model["proof_ready"] is False
    assert model["evidence_status"] == "unverified"
    assert model["manifest_complete"] is True
    assert model["producer_asserted_hashes"]["artifact_sha256"] == "a" * 64
    assert "proof" not in model


def test_root_advertises_cloud_urls_not_localhost(app, monkeypatch):
    monkeypatch.setenv("CLOUD_MODE", "1")
    monkeypatch.setenv("SYSTEM3_DEPLOY_TARGET", "gcp-cloud-run")
    monkeypatch.setenv(
        "SYSTEM3_PUBLIC_BACKEND_URL",
        "https://genesis-system3-web-doq2wplepa-el.a.run.app",
    )
    monkeypatch.delenv("PUBLIC_BACKEND_URL", raising=False)
    monkeypatch.delenv("PUBLIC_DASHBOARD_URL", raising=False)
    status, _, body = call(app, "GET", "/")
    assert status == 200
    data = json.loads(body)
    assert data["backend_url"] == "https://genesis-system3-web-doq2wplepa-el.a.run.app"
    assert data["dashboard_url"] == "https://genesis-system3-web-doq2wplepa-el.a.run.app/ui"
    assert data["health"] == "https://genesis-system3-web-doq2wplepa-el.a.run.app/api/health"
    assert "127.0.0.1" not in data["backend_url"]
    assert "localhost" not in data["dashboard_url"]
    assert data["relative_paths"]["dashboard"] == "/ui"


def test_root_ignores_localhost_env_when_cloud_permanent(app, monkeypatch):
    monkeypatch.setenv("CLOUD_MODE", "1")
    monkeypatch.setenv("SYSTEM3_DEPLOY_TARGET", "gcp-cloud-run")
    monkeypatch.setenv("PUBLIC_BACKEND_URL", "http://127.0.0.1:8000")
    monkeypatch.setenv("PUBLIC_DASHBOARD_URL", "http://127.0.0.1:8000")
    status, _, body = call(app, "GET", "/")
    assert status == 200
    data = json.loads(body)
    assert data["backend_url"].startswith("https://")
    assert data["dashboard_url"].endswith("/ui")
    assert "127.0.0.1" not in json.dumps(data)


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
    # Make a request first so there's at least one data point.
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


def test_safe_dashboard_reads_do_not_trip_compat_rate_bucket(app):
    # Regression: Cloud Run proxy clients can share request.client.host. A
    # normal dashboard burst must not make unrelated read endpoints return 429.
    for _ in range(181):
        status, _, _ = call(app, "GET", "/api/state")
        assert status == 200


def test_mutation_policy_probes_do_not_trip_compat_rate_bucket(app):
    for _ in range(181):
        status, _, _ = call(
            app,
            "POST",
            "/api/security/mutation-policy/probe/paper",
            json_body={"proof": "deny-only"},
        )
        assert status != 429
        status, _, _ = call(
            app,
            "POST",
            "/__system3_unknown_mutation_probe__",
            json_body={"proof": "deny-only"},
        )
        assert status != 429


def test_unified_portfolio_caches_successful_result(app, monkeypatch):
    endpoint = route_endpoint(app, "GET", "/api/portfolio/unified")
    endpoint.__globals__["_API_CACHE"].pop("portfolio", None)
    calls = {"count": 0}

    async def fake_run_blocking(*args, **kwargs):
        calls["count"] += 1
        return {"status": "ok", "live_trading_enabled": False}

    monkeypatch.setitem(endpoint.__globals__, "_run_blocking", fake_run_blocking)
    first = asyncio.run(endpoint())
    second = asyncio.run(endpoint())
    assert first == second
    assert calls["count"] == 1
    assert first["live_trading_enabled"] is False


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
