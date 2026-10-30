import importlib.util
from pathlib import Path

import pytest
import requests


ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = ROOT / "scripts" / "gcp_public_dashboard_runtime_proof.py"
SPEC = importlib.util.spec_from_file_location("gcp_public_dashboard_runtime_proof", PROOF_PATH)
assert SPEC and SPEC.loader
proof = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proof)


class FakeResponse:
    def __init__(self, status_code: int, payload=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = "<div id='root'></div>"

    def json(self):
        return self._payload


def _disable_sleep(monkeypatch):
    monkeypatch.setattr(proof.time, "sleep", lambda _seconds: None)


def test_timeout_then_success_is_bounded_and_records_safe_attempt_metadata(monkeypatch):
    _disable_sleep(monkeypatch)
    calls = {"count": 0}

    def fake_get(_url, timeout):
        assert timeout == proof.TIMEOUT_S
        calls["count"] += 1
        if calls["count"] == 1:
            raise requests.Timeout("transient cold-start")
        return FakeResponse(200)

    monkeypatch.setattr(proof.requests, "get", fake_get)
    response, attempts = proof._get_with_readiness("https://example.invalid/secret-path", "root")

    assert response.status_code == 200
    assert calls["count"] == 2
    assert attempts == [
        {"attempt": 1, "label": "root", "http_status": None, "error_type": "Timeout"},
        {"attempt": 2, "label": "root", "http_status": 200, "error_type": None},
    ]
    assert all("url" not in item and "body" not in item for item in attempts)


def test_transient_503_retries_but_401_never_retries(monkeypatch):
    _disable_sleep(monkeypatch)
    sequence = [FakeResponse(503), FakeResponse(200)]
    monkeypatch.setattr(proof.requests, "get", lambda _url, timeout: sequence.pop(0))
    response, attempts = proof._get_with_readiness("https://example.invalid/", "health")
    assert response.status_code == 200
    assert [item["http_status"] for item in attempts] == [503, 200]

    calls = {"count": 0}

    def auth_failure(_url, timeout):
        calls["count"] += 1
        return FakeResponse(401)

    monkeypatch.setattr(proof.requests, "get", auth_failure)
    response, attempts = proof._get_with_readiness("https://example.invalid/api/auth/status", "auth_status")
    assert response.status_code == 401
    assert calls["count"] == 1
    assert len(attempts) == 1


def test_persistent_timeout_fails_closed_after_exact_attempt_budget(monkeypatch):
    _disable_sleep(monkeypatch)
    calls = {"count": 0}

    def always_timeout(_url, timeout):
        calls["count"] += 1
        raise requests.Timeout("still unavailable")

    monkeypatch.setattr(proof.requests, "get", always_timeout)
    with pytest.raises(requests.Timeout):
        proof._get_with_readiness("https://example.invalid/", "root")
    assert calls["count"] == proof.READINESS_ATTEMPTS == 3


def test_json_probe_preserves_semantic_status_and_does_not_fabricate_success(monkeypatch):
    _disable_sleep(monkeypatch)
    monkeypatch.setattr(
        proof.requests,
        "get",
        lambda _url, timeout: FakeResponse(403, {"detail": "forbidden"}),
    )
    status, body, attempts = proof._get_json("https://example.invalid/api/state", "state")
    assert status == 403
    assert body == {"detail": "forbidden"}
    assert len(attempts) == 1
