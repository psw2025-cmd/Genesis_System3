from __future__ import annotations

from types import SimpleNamespace

import pytest

from core.brokers.dhan import dhan_readonly as ro
from core.brokers.dhan.cloud_status_probe import get_cloud_status


class _Response:
    def __init__(self, payload=None, *, status_code=200, text=""):
        self._payload = payload or {}
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            exc = RuntimeError(f"HTTP {self.status_code}")
            exc.response = self
            raise exc

    def json(self):
        return self._payload


def _creds():
    return {"client_id": "1000000001", "access_token": "header.payload.sig"}


def test_rest_get_can_omit_client_id_for_non_trading_endpoint(monkeypatch):
    captured = {}

    def fake_get(url, *, headers, timeout):
        captured.update(url=url, headers=dict(headers), timeout=timeout)
        return _Response({"dhanClientId": "1000000001"})

    monkeypatch.setattr(ro, "_REQUESTS_OK", True)
    monkeypatch.setattr(ro, "_requests", SimpleNamespace(get=fake_get))
    out = ro._rest_get(
        ro._DHAN_PROFILE_URL,
        "secret-token",
        "1000000001",
        include_client_id=False,
    )

    assert out["dhanClientId"] == "1000000001"
    assert captured["headers"]["access-token"] == "secret-token"
    assert "client-id" not in captured["headers"]


def test_profile_rest_uses_access_token_only(monkeypatch):
    captured = {}

    def fake_get(url, *, headers, timeout):
        captured["headers"] = dict(headers)
        return _Response({"dhanClientId": "1000000001", "tokenValidity": "valid"})

    monkeypatch.setattr(ro, "get_dhan_credentials", _creds)
    monkeypatch.setattr(ro, "create_dhan_client", lambda: None)
    monkeypatch.setattr(ro, "_REQUESTS_OK", True)
    monkeypatch.setattr(ro, "_requests", SimpleNamespace(get=fake_get))

    result = ro.get_profile()

    assert result["success"] is True
    assert captured["headers"]["access-token"] == "header.payload.sig"
    assert "client-id" not in captured["headers"]


def test_fund_limit_rest_uses_access_token_only(monkeypatch):
    captured = {}

    def fake_get(url, *, headers, timeout):
        captured["headers"] = dict(headers)
        return _Response({"dhanClientId": "1000000001", "availabelBalance": 1.0})

    monkeypatch.setattr(ro, "get_dhan_credentials", _creds)
    monkeypatch.setattr(ro, "create_dhan_client", lambda: None)
    monkeypatch.setattr(ro, "_REQUESTS_OK", True)
    monkeypatch.setattr(ro, "_requests", SimpleNamespace(get=fake_get))

    result = ro.get_funds()

    assert result["success"] is True
    assert captured["headers"]["access-token"] == "header.payload.sig"
    assert "client-id" not in captured["headers"]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"remarks": {"error_code": "DH-901", "error_message": "Invalid Authentication"}, "status": "failure"}, "TOKEN_EXPIRED_OR_INVALID"),
        ({"remarks": {"error_code": "DH-904", "error_message": "Too many requests"}, "status": "failure"}, "DHAN_RATE_LIMITED"),
        ({"remarks": {"error_code": "DH-906", "error_message": "incorrect request"}, "status": "failure"}, "DHAN_REQUEST_REJECTED_906"),
        ({"errorCode": "805", "errorMessage": "Too many requests", "status": "failure"}, "DHAN_RATE_LIMITED"),
        ({"errorCode": "807", "errorMessage": "Access token expired", "status": "failure"}, "TOKEN_EXPIRED_OR_INVALID"),
        ({"errorCode": "808", "errorMessage": "Authentication failed", "status": "failure"}, "TOKEN_EXPIRED_OR_INVALID"),
        ({"errorCode": "809", "errorMessage": "Access token invalid", "status": "failure"}, "TOKEN_EXPIRED_OR_INVALID"),
        ({"errorCode": "810", "errorMessage": "Client ID is invalid", "status": "failure"}, "CLIENT_ID_INVALID"),
    ],
)
def test_payload_taxonomy(payload, expected):
    assert ro._payload_error(payload) == expected


@pytest.mark.parametrize(
    ("status_code", "text", "expected"),
    [
        (400, "DH-901 Invalid Authentication", "TOKEN_EXPIRED_OR_INVALID"),
        (400, "DH-904 Too many requests", "DHAN_RATE_LIMITED"),
        (429, "Too many requests", "DHAN_RATE_LIMITED"),
        (400, "code 805 invalid token text", "DHAN_RATE_LIMITED"),
        (400, "code 810 client id invalid", "CLIENT_ID_INVALID"),
        (400, "DH-906 invalid token text", "DHAN_REQUEST_REJECTED_906"),
    ],
)
def test_exception_taxonomy_numeric_codes_override_free_text(status_code, text, expected):
    response = _Response(status_code=status_code, text=text)
    try:
        response.raise_for_status()
    except Exception as exc:
        assert ro._exception_error(exc) == expected


def test_906_is_never_auth_failure():
    payload = {
        "remarks": {"error_code": "DH-906", "error_message": "Invalid token text must not override numeric code"},
        "status": "failure",
    }
    assert ro._auth_failure_payload(payload) is False
    assert ro._payload_error(payload) == "DHAN_REQUEST_REJECTED_906"


def test_805_is_never_auth_failure():
    payload = {"errorCode": "805", "errorMessage": "Too many requests", "status": "failure"}
    assert ro._auth_failure_payload(payload) is False
    assert ro._payload_error(payload) == "DHAN_RATE_LIMITED"


def test_810_is_configuration_not_token_failure():
    payload = {"errorCode": "810", "errorMessage": "Client ID is invalid", "status": "failure"}
    assert ro._auth_failure_payload(payload) is False
    assert ro._payload_error(payload) == "CLIENT_ID_INVALID"


def test_get_funds_exposes_906_truth_not_token_expired(monkeypatch):
    monkeypatch.setattr(ro, "get_dhan_credentials", _creds)
    monkeypatch.setattr(
        ro,
        "create_dhan_client",
        lambda: SimpleNamespace(
            get_fund_limits=lambda: {
                "remarks": {"error_code": "DH-906", "error_message": "incorrect request"},
                "status": "failure",
            }
        ),
    )

    result = ro.get_funds()

    assert result["success"] is False
    assert result["error"] == "DHAN_REQUEST_REJECTED_906"
    assert result["error"] != "TOKEN_EXPIRED_OR_INVALID"


def test_status_does_not_refresh_on_906(monkeypatch):
    refresh_calls = []
    monkeypatch.setattr(ro, "get_dhan_credentials", _creds)
    monkeypatch.setattr(
        ro,
        "get_dhan_credentials_masked",
        lambda: {
            "client_id_present": True,
            "access_token_present": True,
        },
    )
    monkeypatch.setattr(
        ro,
        "get_profile",
        lambda: {"success": False, "error": "DHAN_REQUEST_REJECTED_906", "data": None},
    )
    monkeypatch.setattr(
        ro,
        "_safe_refresh_token_for_status",
        lambda reason: refresh_calls.append(reason) or {"attempted": True, "success": False},
    )
    monkeypatch.setattr(ro, "_STATUS_RESULT_CACHE", None)
    monkeypatch.setattr(ro, "_STATUS_RESULT_CACHE_AT", 0.0)

    result = ro.get_status()

    assert result["connected"] is False
    assert result["error"] == "DHAN_REQUEST_REJECTED_906"
    assert refresh_calls == []


def test_status_does_not_refresh_on_client_id_invalid(monkeypatch):
    refresh_calls = []
    monkeypatch.setattr(ro, "get_dhan_credentials", _creds)
    monkeypatch.setattr(
        ro,
        "get_dhan_credentials_masked",
        lambda: {"client_id_present": True, "access_token_present": True},
    )
    monkeypatch.setattr(
        ro,
        "get_profile",
        lambda: {"success": False, "error": "CLIENT_ID_INVALID", "data": None},
    )
    monkeypatch.setattr(
        ro,
        "_safe_refresh_token_for_status",
        lambda reason: refresh_calls.append(reason) or {"attempted": True, "success": False},
    )
    monkeypatch.setattr(ro, "_STATUS_RESULT_CACHE", None)
    monkeypatch.setattr(ro, "_STATUS_RESULT_CACHE_AT", 0.0)

    result = ro.get_status()

    assert result["connected"] is False
    assert result["error"] == "CLIENT_ID_INVALID"
    assert refresh_calls == []


def test_cloud_profile_probe_uses_canonical_header_scope(monkeypatch):
    calls = []

    class Module:
        _STATUS_RESULT_CACHE = None
        _STATUS_RESULT_CACHE_AT = 0.0
        _STATUS_RESULT_TTL_S = 25.0
        _DHAN_SDK_OK = False
        _ENV_LOADED_VIA = "test"
        _DHAN_PROFILE_URL = ro._DHAN_PROFILE_URL

        @staticmethod
        def get_dhan_credentials():
            return _creds()

        @staticmethod
        def _rest_get(url, access_token, client_id, timeout, *, include_client_id=True):
            calls.append(include_client_id)
            return {"dhanClientId": "1000000001", "tokenValidity": "valid"}

        @staticmethod
        def _auth_failure_payload(data):
            return False

        @staticmethod
        def _payload_error(data):
            return None

    monkeypatch.setattr("core.brokers.dhan.cloud_status_probe.snapshot", lambda: {})
    result = get_cloud_status(Module())

    assert result["connected"] is True
    assert result["probe_header_contract"] == "access-token-only"
    assert calls == [False]
