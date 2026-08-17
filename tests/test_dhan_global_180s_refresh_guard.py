from __future__ import annotations

import base64
import importlib.util
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

_ROTATOR = Path("scripts/gcp_dhan_token_rotation_job.py")


def _load_rotator():
    spec = importlib.util.spec_from_file_location("system3_dhan_180s_guard_test", _ROTATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _jwt(*, issued_at: datetime | None, expires_in_hours: int = 12) -> str:
    payload = {"exp": int((datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)).timestamp())}
    if issued_at is not None:
        payload["iat"] = int(issued_at.timestamp())
    body = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    return f"header.{body}.signature"


def test_global_refresh_floor_cannot_be_configured_below_180(monkeypatch):
    monkeypatch.setenv("DHAN_MIN_REFRESH_INTERVAL_SECONDS", "1")
    rotator = _load_rotator()
    assert rotator.MIN_REFRESH_INTERVAL_SECONDS == 180


def test_179_seconds_is_blocked():
    rotator = _load_rotator()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    token = _jwt(issued_at=now - timedelta(seconds=179))
    allowed, status, age = rotator._refresh_interval_status(token, now=now)
    assert allowed is False
    assert status == "BLOCKED_MIN_REFRESH_INTERVAL"
    assert age == 179


def test_180_seconds_is_allowed():
    rotator = _load_rotator()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    token = _jwt(issued_at=now - timedelta(seconds=180))
    allowed, status, age = rotator._refresh_interval_status(token, now=now)
    assert allowed is True
    assert status == "REFRESH_INTERVAL_SATISFIED"
    assert age == 180


def test_missing_iat_fails_closed():
    rotator = _load_rotator()
    token = _jwt(issued_at=None)
    allowed, status, age = rotator._refresh_interval_status(token)
    assert allowed is False
    assert status == "BLOCKED_REFRESH_INTERVAL_UNPROVEN"
    assert age is None


def test_dh906_and_805_are_never_auth_failures():
    rotator = _load_rotator()
    assert rotator._is_auth_failure({"code": 906, "message": "invalid token"}) is False
    assert rotator._is_auth_failure({"errorCode": 805, "message": "invalid token"}) is False
    assert rotator._is_auth_failure("DH-906 invalid token", status_code=400) is False


def test_808_and_http_401_remain_auth_failures():
    rotator = _load_rotator()
    assert rotator._is_auth_failure({"code": 808}) is True
    assert rotator._is_auth_failure("unauthorized", status_code=401) is True


def test_only_mint_call_is_behind_interval_guard():
    text = _ROTATOR.read_text(encoding="utf-8")
    guard = "interval_ok, interval_status, token_age_seconds = _refresh_interval_status(token)"
    mint = "new_token = _generate_token(client_id, pin, totp_secret)"
    assert text.count(mint) == 1
    assert guard in text
    assert text.index(guard) < text.index(mint)
    assert '"force_bypass_allowed": False' in text
    assert 'MIN_REFRESH_INTERVAL_SECONDS = max(' in text
    assert "180" in text[text.index("MIN_REFRESH_INTERVAL_SECONDS"):text.index("AUTHORITY")]


def test_dh906_not_present_in_auth_markers():
    text = _ROTATOR.read_text(encoding="utf-8")
    marker_block = text[text.index("_AUTH_MARKERS = ("):text.index("_NON_AUTH_UPSTREAM_CODES")]
    assert "dh-906" not in marker_block.lower()
    assert "_NON_AUTH_UPSTREAM_CODES = {805, 906}" in text
