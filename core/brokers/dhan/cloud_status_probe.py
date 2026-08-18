"""Deterministic Cloud Run Dhan broker status probe.

Safety: read-only profile GET only; no order APIs; no raw token output.
Official Dhan docs document Profile as ``access-token`` only while the official
Python SDK sends ``access-token`` plus ``dhanClientId``. A second SDK-contract
probe is therefore attempted only for client-id/config, opaque HTTP 400, or
DH-906 request-contract failures, and only adopted when that request succeeds.
Rate-limit and auth failures never multiply Profile GETs and never authorize
token rotation. Both success and failure status results are TTL-cached so the
bounded reconcile cannot become a per-caller request-amplification loop.
"""
from __future__ import annotations

import base64
import json
import re
import time
from datetime import datetime, timezone
from typing import Any

from core.brokers.dhan.first_rejection_trace import record_auth_rejection, snapshot

_TOKEN_AUTH_CODES = {901, 807, 808, 809}
_RATE_LIMIT_CODES = {904, 805}
_CLIENT_ID_INVALID_CODES = {810}
_REQUEST_REJECTED_CODES = {906}

_PROFILE_DOCS_CONTRACT = "docs-access-token-only"
_PROFILE_SDK_CONTRACT = "sdk-dhanClientId"
# Dhan's public docs and official Python SDK currently disagree on the Profile
# header contract. A docs-contract 906 is therefore eligible for exactly one
# SDK-contract reconciliation attempt. This remains non-auth and must never
# authorize token rotation. Auth and rate-limit failures never fall back.
_PROFILE_FALLBACK_ERRORS = {
    "CLIENT_ID_INVALID",
    "HTTP_400",
    "DHAN_REQUEST_REJECTED_906",
}


def _public_contract(contract: str) -> str:
    """Stable public label; exact experimental variant is reported separately."""
    if contract == _PROFILE_DOCS_CONTRACT:
        return "access-token-only"
    if contract == _PROFILE_SDK_CONTRACT:
        return "access-token-plus-dhanClientId"
    return "unknown"


def _clock_expired(token: str) -> bool | None:
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        exp = json.loads(base64.urlsafe_b64decode(payload.encode("ascii"))).get("exp")
        if exp is None:
            return None
        return float(exp) <= datetime.now(timezone.utc).timestamp()
    except Exception:
        return None


def _auth_classification(token: str) -> str:
    expired = _clock_expired(token)
    if expired is True:
        return "TOKEN_CLOCK_EXPIRED"
    if expired is False:
        return "DHAN_TOKEN_REJECTED"
    return "DHAN_TOKEN_REJECTED_CLOCK_UNKNOWN"


def _safe_upstream_code(blob: str) -> int | None:
    """Extract only a numeric Dhan error code; never return response text."""
    text = str(blob or "")
    for pattern in (
        r'"(?:error[_-]?code|code)"\s*:\s*"?(?:dh-)?(\d{3,5})',
        r"\b(?:error[_-]?code|code)\s*[=: ]\s*(?:dh-)?(\d{3,5})\b",
        r"\bdh-(\d{3,5})\b",
    ):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


def _http_auth_failure(status_code: Any, blob: str) -> bool:
    code = _safe_upstream_code(blob)
    if code in _RATE_LIMIT_CODES | _REQUEST_REJECTED_CODES | _CLIENT_ID_INVALID_CODES:
        return False
    if status_code == 401 or code in _TOKEN_AUTH_CODES:
        return True
    auth_markers = (
        "invalid token",
        "invalid access token",
        "access token is expired",
        "token expired",
        "token is expired",
        "authentication failed",
        "invalid authentication",
    )
    return status_code == 400 and any(marker in blob for marker in auth_markers)


def _non_auth_upstream_classification(status_code: Any, blob: str) -> str | None:
    code = _safe_upstream_code(blob)
    if code in _RATE_LIMIT_CODES or status_code == 429:
        return "DHAN_RATE_LIMITED"
    if code in _REQUEST_REJECTED_CODES:
        return "DHAN_REQUEST_REJECTED_906"
    if code in _CLIENT_ID_INVALID_CODES:
        return "DHAN_CLIENT_ID_INVALID"
    return None


def _payload_blob(data: Any) -> str:
    try:
        return json.dumps(data, sort_keys=True, default=str).lower()
    except Exception:
        return str(data or "").lower()


def _payload_failure(data: Any) -> tuple[str | None, str | None, int | None]:
    if not isinstance(data, dict):
        return None, None, None
    blob = _payload_blob(data)
    code = _safe_upstream_code(blob)
    status = str(data.get("status") or "").strip().lower()

    if code in _TOKEN_AUTH_CODES:
        return "TOKEN_EXPIRED_OR_INVALID", None, code
    if code in _CLIENT_ID_INVALID_CODES:
        return "CLIENT_ID_INVALID", "DHAN_CLIENT_ID_INVALID", code
    if code in _RATE_LIMIT_CODES:
        return "DHAN_RATE_LIMITED", "DHAN_RATE_LIMITED", code
    if code in _REQUEST_REJECTED_CODES:
        return "DHAN_REQUEST_REJECTED_906", "DHAN_REQUEST_REJECTED_906", code

    auth_markers = (
        "invalid token",
        "invalid access token",
        "access token is expired",
        "token expired",
        "token is expired",
        "authentication failed",
        "invalid authentication",
    )
    if any(marker in blob for marker in auth_markers):
        return "TOKEN_EXPIRED_OR_INVALID", None, code
    if status in {"failure", "failed", "error"}:
        return "DHAN_UPSTREAM_FAILURE", "DHAN_UPSTREAM_FAILURE", code
    return None, None, code


def _secret_version() -> str | None:
    try:
        from core.brokers.dhan.cloud_token_provider import token_metadata

        return str(token_metadata().get("secret_version") or "") or None
    except Exception:
        return None


def _record_rejection(token: str, status_code: int | None, blob: str) -> dict[str, Any]:
    return record_auth_rejection(
        secret_version=_secret_version(),
        auth_classification=_auth_classification(token),
        http_status=status_code,
        upstream_code=_safe_upstream_code(blob),
    )


def _profile_request(
    module: Any,
    access_token: str,
    client_id: str,
    *,
    timeout_s: float,
    contract: str,
) -> dict:
    """Execute exactly one safe Profile GET under a named header contract."""
    test_hook = getattr(module, "_profile_probe_request", None)
    if callable(test_hook):
        return test_hook(
            access_token,
            client_id,
            timeout_s=timeout_s,
            contract=contract,
        )

    if contract == _PROFILE_DOCS_CONTRACT:
        rest_get = getattr(module, "_rest_get", None)
        if callable(rest_get):
            return rest_get(
                module._DHAN_PROFILE_URL,
                access_token,
                client_id,
                timeout=max(1.0, min(float(timeout_s), 8.0)),
                include_client_id=False,
            )
    elif contract != _PROFILE_SDK_CONTRACT:
        raise RuntimeError("unsupported profile header contract")

    requests_module = getattr(module, "_requests", None)
    requests_ok = bool(getattr(module, "_REQUESTS_OK", False))
    if not requests_ok or requests_module is None:
        raise RuntimeError("requests library not available")

    headers = {"access-token": access_token}
    if contract == _PROFILE_SDK_CONTRACT:
        headers["dhanClientId"] = client_id

    response = requests_module.get(
        module._DHAN_PROFILE_URL,
        headers=headers,
        timeout=max(1.0, min(float(timeout_s), 8.0)),
    )
    response.raise_for_status()
    return response.json()


def _sdk_contract_transport_available(module: Any) -> bool:
    """Whether a real second Profile transport exists without inventing one."""
    if callable(getattr(module, "_profile_probe_request", None)):
        return True
    return bool(
        getattr(module, "_REQUESTS_OK", False)
        and getattr(module, "_requests", None) is not None
    )


def _safe_attempt(
    contract: str,
    *,
    outcome: str,
    status_code: Any = None,
    upstream_code: Any = None,
) -> dict[str, Any]:
    return {
        "contract": contract,
        "public_contract": _public_contract(contract),
        "outcome": outcome,
        "http_status": status_code,
        "upstream_code": upstream_code,
        "credential_value_exposed": False,
    }


def _probe_contract(
    module: Any,
    access_token: str,
    client_id: str,
    *,
    timeout_s: float,
    contract: str,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        data = _profile_request(
            module,
            access_token,
            client_id,
            timeout_s=timeout_s,
            contract=contract,
        )
        latency_ms = int((time.monotonic() - started) * 1000)
        error, upstream_classification, upstream_code = _payload_failure(data)
        if error:
            return {
                "ok": False,
                "error": error,
                "auth_classification": (
                    _auth_classification(access_token)
                    if error == "TOKEN_EXPIRED_OR_INVALID"
                    else None
                ),
                "upstream_classification": upstream_classification,
                "upstream_code": upstream_code,
                "http_status": None,
                "blob": _payload_blob(data),
                "latency_ms": latency_ms,
                "attempt": _safe_attempt(
                    contract,
                    outcome=error,
                    upstream_code=upstream_code,
                ),
            }
        return {
            "ok": True,
            "error": None,
            "auth_classification": "AUTH_OK",
            "upstream_classification": None,
            "upstream_code": None,
            "http_status": 200,
            "blob": "",
            "latency_ms": latency_ms,
            "attempt": _safe_attempt(contract, outcome="AUTH_OK", status_code=200),
        }
    except Exception as exc:
        latency_ms = int((time.monotonic() - started) * 1000)
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None) if response is not None else None
        try:
            body = str(getattr(response, "text", "") or "")[:160] if response is not None else ""
        except Exception:
            body = ""
        blob = f"{status_code or ''} {body} {exc}".lower()
        upstream_code = _safe_upstream_code(blob)
        auth_classification = None
        upstream_classification = None
        if _http_auth_failure(status_code, blob):
            error = "TOKEN_EXPIRED_OR_INVALID"
            auth_classification = _auth_classification(access_token)
        else:
            upstream_classification = _non_auth_upstream_classification(status_code, blob)
            if upstream_classification == "DHAN_REQUEST_REJECTED_906":
                error = "DHAN_REQUEST_REJECTED_906"
            elif upstream_classification == "DHAN_RATE_LIMITED":
                error = "DHAN_RATE_LIMITED"
            elif upstream_classification == "DHAN_CLIENT_ID_INVALID":
                error = "CLIENT_ID_INVALID"
            elif status_code == 403 or "forbidden" in blob:
                error = "ACCESS_FORBIDDEN"
            elif status_code:
                error = f"HTTP_{status_code}"
            else:
                error = f"NETWORK_ERROR:{type(exc).__name__}"
        return {
            "ok": False,
            "error": error,
            "auth_classification": auth_classification,
            "upstream_classification": upstream_classification,
            "upstream_code": upstream_code,
            "http_status": status_code,
            "blob": blob,
            "latency_ms": latency_ms,
            "attempt": _safe_attempt(
                contract,
                outcome=error,
                status_code=status_code,
                upstream_code=upstream_code,
            ),
        }


def get_cloud_status(module: Any, *, timeout_s: float = 5.0) -> dict[str, Any]:
    now = time.time()
    cache = getattr(module, "_STATUS_RESULT_CACHE", None)
    cache_at = float(getattr(module, "_STATUS_RESULT_CACHE_AT", 0.0) or 0.0)
    ttl = float(getattr(module, "_STATUS_RESULT_TTL_S", 25.0) or 25.0)
    if cache and (now - cache_at) < ttl:
        out = dict(cache)
        out.update(
            cache_hit=True,
            cache_age_s=round(now - cache_at, 1),
            probe_strategy="cloud_rest_profile_bounded_contract_reconcile",
            auth_rejection_trace=snapshot(),
        )
        return out

    creds = module.get_dhan_credentials()
    client_id = str(creds.get("client_id") or "").strip().lstrip("\ufeff")
    access_token = str(creds.get("access_token") or "").strip().lstrip("\ufeff")
    cached_contract = str(
        getattr(module, "_PROFILE_HEADER_CONTRACT_CACHE", "") or ""
    ).strip()
    primary_contract = (
        cached_contract
        if cached_contract in {_PROFILE_DOCS_CONTRACT, _PROFILE_SDK_CONTRACT}
        else _PROFILE_DOCS_CONTRACT
    )
    base = {
        "broker": "dhan",
        "mode": "ANALYZER",
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "client_id_present": bool(client_id),
        "access_token_present": bool(access_token),
        "credentials_present": bool(client_id and access_token),
        "sdk_available": bool(getattr(module, "_DHAN_SDK_OK", False)),
        "env_source": getattr(module, "_ENV_LOADED_VIA", "unknown"),
        "cache_hit": False,
        "probe_strategy": "cloud_rest_profile_bounded_contract_reconcile",
        "probe_header_contract": _public_contract(primary_contract),
        "probe_header_variant": primary_contract,
        "probe_contract_cached": bool(cached_contract),
        "probe_timeout_s": float(timeout_s),
        "auth_rejection_trace": snapshot(),
    }
    if not client_id or not access_token:
        return {
            **base,
            "connected": False,
            "error": "CONFIG_MISSING",
            "auth_classification": "CONFIG_MISSING",
            "upstream_classification": None,
            "upstream_code": None,
            "probe_header_attempts": [],
            "latency_ms": 0,
        }

    total_started = time.monotonic()
    first = _probe_contract(
        module,
        access_token,
        client_id,
        timeout_s=timeout_s,
        contract=primary_contract,
    )
    attempts = [first["attempt"]]
    chosen_contract = primary_contract
    final = first

    if (
        not first["ok"]
        and primary_contract == _PROFILE_DOCS_CONTRACT
        and first["error"] in _PROFILE_FALLBACK_ERRORS
        and _sdk_contract_transport_available(module)
    ):
        second = _probe_contract(
            module,
            access_token,
            client_id,
            timeout_s=timeout_s,
            contract=_PROFILE_SDK_CONTRACT,
        )
        attempts.append(second["attempt"])
        if second["ok"]:
            final = second
            chosen_contract = _PROFILE_SDK_CONTRACT

    latency_ms = int((time.monotonic() - total_started) * 1000)
    if final["ok"]:
        setattr(module, "_PROFILE_HEADER_CONTRACT_CACHE", chosen_contract)
        result = {
            **base,
            "connected": True,
            "error": None,
            "auth_classification": "AUTH_OK",
            "upstream_classification": None,
            "upstream_code": None,
            "auth_rejection_trace": snapshot(),
            "latency_ms": latency_ms,
            "profile_source": "rest",
            "probe_header_contract": _public_contract(chosen_contract),
            "probe_header_variant": chosen_contract,
            "probe_contract_cached": bool(cached_contract),
            "probe_header_attempts": attempts,
        }
        module._STATUS_RESULT_CACHE = dict(result)
        module._STATUS_RESULT_CACHE_AT = time.time()
        return result

    trace = snapshot()
    if final["error"] == "TOKEN_EXPIRED_OR_INVALID":
        trace = _record_rejection(
            access_token,
            final.get("http_status"),
            final.get("blob") or "",
        )
    result = {
        **base,
        "connected": False,
        "error": final["error"],
        "auth_classification": final["auth_classification"],
        "upstream_classification": final["upstream_classification"],
        "upstream_code": final["upstream_code"],
        "auth_rejection_trace": trace,
        "latency_ms": latency_ms,
        "probe_header_contract": _public_contract(chosen_contract),
        "probe_header_variant": chosen_contract,
        "probe_contract_cached": bool(cached_contract),
        "probe_header_attempts": attempts,
    }
    module._STATUS_RESULT_CACHE = dict(result)
    module._STATUS_RESULT_CACHE_AT = time.time()
    return result
