"""Offline, no-broker-network proof for independent GET-only Dhan audit."""
import json
from pathlib import Path

import pytest

from scripts import cloud_verify_readonly as cv


class Response:
    def __init__(self, payload):
        self.body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, size):
        assert size <= 2_000_001
        return self.body


def setup(monkeypatch, tmp_path):
    path = tmp_path / "broker-get-evidence.jsonl"
    monkeypatch.setenv("CLOUD_VERIFY_EVIDENCE", str(path))
    monkeypatch.setenv("PAPER_MODE", "1")
    monkeypatch.setenv("LIVE_ORDER_AUTHORITY", "0")
    monkeypatch.setenv("REAL_BROKER_ORDERS", "0")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN", "SENSITIVE_TEST_ACCESS_TOKEN")
    monkeypatch.setenv("DHAN_CLIENT_ID", "SENSITIVE_TEST_CLIENT_ID")
    return path


def test_get_only_zero_count_and_hash_without_secret_output(monkeypatch, tmp_path, capsys):
    path = setup(monkeypatch, tmp_path)

    def fake_get(request, timeout):
        assert request.get_method() == "GET"
        assert request.full_url == "https://api.dhan.co/v2/orders"
        assert timeout == 15
        return Response([])

    monkeypatch.setattr(cv, "urlopen", fake_get)
    assert cv.dhan_orders() is True
    output = capsys.readouterr().out
    assert "SENSITIVE_TEST_ACCESS_TOKEN" not in output
    assert "SENSITIVE_TEST_CLIENT_ID" not in output
    record = json.loads(path.read_text().strip())
    assert record["status"] == "PASS"
    assert record["order_count"] == 0
    assert len(record["response_sha256"]) == 64


def test_get_nonempty_is_fail_not_zero(monkeypatch, tmp_path):
    path = setup(monkeypatch, tmp_path)
    monkeypatch.setattr(cv, "urlopen", lambda *_args, **_kw: Response([
        {"orderId": "TEST_ONLY_UNSENT_ORDER"}
    ]))
    assert cv.dhan_orders() is False
    record = json.loads(path.read_text().strip())
    assert record["status"] == "FAIL"
    assert record["order_count"] == 1


def test_error_object_is_not_zero_orders(monkeypatch, tmp_path):
    path = setup(monkeypatch, tmp_path)
    monkeypatch.setattr(cv, "urlopen", lambda *_args, **_kw: Response({
        "errorMessage": "SENSITIVE_TEST_ACCESS_TOKEN", "errorCode": "DH-906"
    }))
    assert cv.dhan_orders() is False
    record = json.loads(path.read_text().strip())
    assert record["status"] == "NOT_VERIFIED"
    assert "SENSITIVE_TEST_ACCESS_TOKEN" not in path.read_text()


def test_unexpected_exception_text_does_not_expose_secrets(monkeypatch, tmp_path, capsys):
    path = setup(monkeypatch, tmp_path)
    monkeypatch.setattr(cv, "guard", lambda: (_ for _ in ()).throw(
        RuntimeError("SENSITIVE_TEST_ACCESS_TOKEN")
    ))
    assert cv.main() == 1
    assert "SENSITIVE_TEST_ACCESS_TOKEN" not in capsys.readouterr().out
    assert "SENSITIVE_TEST_ACCESS_TOKEN" not in path.read_text()


def test_source_enforces_get_without_real_order_mutations():
    src = (Path(__file__).resolve().parents[1] / "scripts" /
           "cloud_verify_readonly.py").read_text(encoding="utf-8")
    assert 'method="GET"' in src
    assert '"/v2/orders"' not in src.replace('https://api.dhan.co/v2/orders', '')
    for marker in ('method="POST"', 'method="PUT"', 'method="DELETE"', 'method="PATCH"'):
        assert marker not in src
