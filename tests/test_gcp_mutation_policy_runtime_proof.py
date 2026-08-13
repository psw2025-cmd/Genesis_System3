"""Mutation-policy runtime proof retries Cloud Run 429/5xx instead of failing closed."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "gcp_mutation_policy_runtime_proof_under_test",
    ROOT / "scripts" / "gcp_mutation_policy_runtime_proof.py",
)
proof = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(proof)


class _FakeResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code


def test_request_with_retry_skips_transient_429(monkeypatch):
    calls = {"n": 0}

    def fake_request(method, url, **kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            return _FakeResponse(429)
        return _FakeResponse(403)

    monkeypatch.setattr(proof.requests, "request", fake_request)
    monkeypatch.setattr(proof.time, "sleep", lambda _s: None)
    response = proof._request_with_retry("POST", "https://example.invalid/probe")
    assert response.status_code == 403
    assert calls["n"] == 3
