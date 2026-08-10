"""Dynamic Dhan access-token provider for Google Cloud Run.

Security contract:
- Reads only the configured Dhan access-token secret.
- Never logs, returns, or exposes the raw token in metadata.
- Keeps live trading and order routing completely out of scope.
- Refreshes the in-process environment when Secret Manager publishes a new version.
"""
from __future__ import annotations

import base64
import json
import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable

_LOCK = threading.RLock()
_CACHE: dict[str, Any] = {
    "token": "",
    "version": None,
    "secret_resource": None,
    "fetched_at_epoch": 0.0,
    "version_created_at": None,
    "reload_count": 0,
    "last_reload_reason": None,
    "last_error": None,
}
_CLIENT_FACTORY: Callable[[], Any] | None = None


def enabled() -> bool:
    mode = os.getenv("DHAN_TOKEN_SOURCE", "").strip().lower()
    if mode in {"env", "environment", "disabled", "off"}:
        return False
    if mode in {"gcp", "gcp-secret-manager", "gcp-secret-manager-dynamic", "secret-manager"}:
        return True
    return bool(os.getenv("K_SERVICE") or os.getenv("CLOUD_MODE"))


def _project_id() -> str:
    return (
        os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCP_PROJECT")
        or os.getenv("SYSTEM3_FIRESTORE_PROJECT")
        or "system3-openalgo-safe"
    )


def _secret_id() -> str:
    return os.getenv("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token").strip() or "dhan-access-token"


def _ttl_seconds() -> float:
    raw = os.getenv("DHAN_TOKEN_CACHE_TTL_S", "30").strip()
    try:
        return max(1.0, min(float(raw), 300.0))
    except ValueError:
        return 30.0


def _client():
    if _CLIENT_FACTORY is not None:
        return _CLIENT_FACTORY()
    from google.cloud import secretmanager

    return secretmanager.SecretManagerServiceClient()


def _jwt_expiry(token: str) -> datetime | None:
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload_part = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_part.encode("ascii")))
        exp = payload.get("exp")
        return datetime.fromtimestamp(float(exp), tz=timezone.utc) if exp else None
    except Exception:
        return None


def _iso_utc(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "ToDatetime"):
        value = value.ToDatetime()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def _fetch_latest(reason: str) -> str:
    resource = f"projects/{_project_id()}/secrets/{_secret_id()}/versions/latest"
    client = _client()
    response = client.access_secret_version(request={"name": resource})
    token = response.payload.data.decode("utf-8").strip()
    if not token:
        raise RuntimeError("Secret Manager returned an empty Dhan access token")

    version_name = getattr(response, "name", None) or resource
    created_at = None
    try:
        version = client.get_secret_version(request={"name": version_name})
        created_at = _iso_utc(getattr(version, "create_time", None))
    except Exception:
        created_at = None

    _CACHE.update(
        {
            "token": token,
            "version": str(version_name).rsplit("/", 1)[-1],
            "secret_resource": str(version_name),
            "fetched_at_epoch": time.time(),
            "version_created_at": created_at,
            "reload_count": int(_CACHE.get("reload_count") or 0) + 1,
            "last_reload_reason": reason,
            "last_error": None,
        }
    )
    os.environ["DHAN_ACCESS_TOKEN"] = token
    return token


def get_access_token(*, force_refresh: bool = False, reason: str = "credential_read") -> str:
    if not enabled():
        return os.getenv("DHAN_ACCESS_TOKEN", "").strip()

    with _LOCK:
        cached = str(_CACHE.get("token") or "")
        age = time.time() - float(_CACHE.get("fetched_at_epoch") or 0.0)
        if cached and not force_refresh and age < _ttl_seconds():
            return cached
        try:
            return _fetch_latest(reason)
        except Exception as exc:
            _CACHE["last_error"] = type(exc).__name__
            return cached or os.getenv("DHAN_ACCESS_TOKEN", "").strip()


_FORCE_RELOAD_MIN_INTERVAL_S = 30.0
_LAST_FORCE_RELOAD_EPOCH = 0.0


def force_reload(reason: str = "auth_failure") -> bool:
    """Force-fetch the latest secret version, rate-limited to stop SM hammering.

    SYS3-BLK-011: during a bad-token loop every read call triggered a forced
    Secret Manager access (~4/sec, reload_count 25k+). A 30s floor bounds
    worst-case SM traffic to 2 reads/min while still healing promptly.
    """
    global _LAST_FORCE_RELOAD_EPOCH
    with _LOCK:
        now = time.time()
        if now - _LAST_FORCE_RELOAD_EPOCH < _FORCE_RELOAD_MIN_INTERVAL_S:
            _CACHE["last_reload_reason"] = f"{reason}_throttled"
            return False
        _LAST_FORCE_RELOAD_EPOCH = now
        before_token = str(_CACHE.get("token") or os.getenv("DHAN_ACCESS_TOKEN", "").strip())
        before_version = str(_CACHE.get("version") or "")
    token = get_access_token(force_refresh=True, reason=reason)
    with _LOCK:
        after_version = str(_CACHE.get("version") or "")
    changed = token != before_token or (bool(after_version) and after_version != before_version)
    return bool(token) and changed


def token_metadata() -> dict[str, Any]:
    with _LOCK:
        token = str(_CACHE.get("token") or os.getenv("DHAN_ACCESS_TOKEN", "").strip())
        expiry = _jwt_expiry(token) if token else None
        hours = (expiry - datetime.now(timezone.utc)).total_seconds() / 3600 if expiry else None
        fetched_epoch = float(_CACHE.get("fetched_at_epoch") or 0.0)
        return {
            "source": "GCP_SECRET_MANAGER_DYNAMIC" if enabled() else "ENVIRONMENT_FALLBACK",
            "secret_id": _secret_id() if enabled() else None,
            "secret_version": _CACHE.get("version"),
            "secret_version_created_at_utc": _CACHE.get("version_created_at"),
            "loaded_at_utc": datetime.fromtimestamp(fetched_epoch, tz=timezone.utc).isoformat() if fetched_epoch else None,
            "cache_age_s": round(max(0.0, time.time() - fetched_epoch), 1) if fetched_epoch else None,
            "cache_ttl_s": _ttl_seconds(),
            "expires_at_utc": expiry.isoformat() if expiry else None,
            "hours_remaining": round(hours, 2) if hours is not None else None,
            "expired": bool(hours is not None and hours <= 0),
            "reload_count": int(_CACHE.get("reload_count") or 0),
            "last_reload_reason": _CACHE.get("last_reload_reason"),
            "last_error_type": _CACHE.get("last_error"),
            "rotation_job": os.getenv("DHAN_TOKEN_ROTATION_JOB", "genesis-system3-dhan-token-rotate"),
            "rotation_schedule": os.getenv("DHAN_TOKEN_ROTATION_SCHEDULE", "07:30 IST daily"),
            "token_present": bool(token),
            "token_value_exposed": False,
        }


def _set_client_factory_for_tests(factory: Callable[[], Any] | None) -> None:
    global _CLIENT_FACTORY
    with _LOCK:
        _CLIENT_FACTORY = factory
        _CACHE.update(
            {
                "token": "",
                "version": None,
                "secret_resource": None,
                "fetched_at_epoch": 0.0,
                "version_created_at": None,
                "reload_count": 0,
                "last_reload_reason": None,
                "last_error": None,
            }
        )
