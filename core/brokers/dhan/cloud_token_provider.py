"""Dynamic Dhan access-token provider for Google Cloud Run.

Security contract:
- Reads only the configured Dhan access-token secret.
- Never logs, returns, or exposes the raw token in metadata.
- Keeps live trading and order routing completely out of scope.
- Refreshes the in-process environment when Secret Manager publishes a new version.
- Suppresses repeated auth-failure force reloads of the same rejected version while
  leaving normal TTL refresh intact so a newly published version is discovered.
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
    "token": "", "version": None, "secret_resource": None, "fetched_at_epoch": 0.0,
    "version_created_at": None, "reload_count": 0, "last_reload_reason": None,
    "last_error": None, "rejected_version": None, "rejected_at_epoch": 0.0,
    "auth_reload_suppressed_count": 0,
}
_CLIENT_FACTORY: Callable[[], Any] | None = None


def enabled() -> bool:
    mode = os.getenv("DHAN_TOKEN_SOURCE", "").strip().lower()
    if mode in {"env", "environment", "disabled", "off"}: return False
    if mode in {"gcp", "gcp-secret-manager", "gcp-secret-manager-dynamic", "secret-manager"}: return True
    return bool(os.getenv("K_SERVICE") or os.getenv("CLOUD_MODE"))


def _project_id() -> str:
    return os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or os.getenv("SYSTEM3_FIRESTORE_PROJECT") or "system3-openalgo-safe"


def _secret_id() -> str:
    return os.getenv("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token").strip() or "dhan-access-token"


def _ttl_seconds() -> float:
    try: return max(1.0, min(float(os.getenv("DHAN_TOKEN_CACHE_TTL_S", "30").strip()), 300.0))
    except ValueError: return 30.0


def _auth_reload_backoff_s() -> float:
    try: return max(5.0, min(float(os.getenv("DHAN_AUTH_RELOAD_BACKOFF_S", "30").strip()), 300.0))
    except ValueError: return 30.0


def _client():
    if _CLIENT_FACTORY is not None: return _CLIENT_FACTORY()
    from google.cloud import secretmanager
    return secretmanager.SecretManagerServiceClient()


def _jwt_expiry(token: str) -> datetime | None:
    try:
        parts = token.split(".")
        if len(parts) < 2: return None
        payload_part = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_part.encode("ascii")))
        exp = payload.get("exp")
        return datetime.fromtimestamp(float(exp), tz=timezone.utc) if exp else None
    except Exception: return None


def _iso_utc(value: Any) -> str | None:
    if value is None: return None
    if hasattr(value, "ToDatetime"): value = value.ToDatetime()
    if isinstance(value, datetime):
        if value.tzinfo is None: value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def _fetch_latest(reason: str) -> str:
    resource = f"projects/{_project_id()}/secrets/{_secret_id()}/versions/latest"
    client = _client(); response = client.access_secret_version(request={"name": resource})
    token = response.payload.data.decode("utf-8").strip()
    if not token: raise RuntimeError("Secret Manager returned an empty Dhan access token")
    version_name = getattr(response, "name", None) or resource
    created_at = None
    try: created_at = _iso_utc(getattr(client.get_secret_version(request={"name": version_name}), "create_time", None))
    except Exception: pass
    version = str(version_name).rsplit("/", 1)[-1]
    previous_version = str(_CACHE.get("version") or "")
    _CACHE.update({"token": token, "version": version, "secret_resource": str(version_name),
                   "fetched_at_epoch": time.time(), "version_created_at": created_at,
                   "reload_count": int(_CACHE.get("reload_count") or 0) + 1,
                   "last_reload_reason": reason, "last_error": None})
    if previous_version and version != previous_version:
        _CACHE["rejected_version"] = None; _CACHE["rejected_at_epoch"] = 0.0
    os.environ["DHAN_ACCESS_TOKEN"] = token
    return token


def get_access_token(*, force_refresh: bool = False, reason: str = "credential_read") -> str:
    if not enabled(): return os.getenv("DHAN_ACCESS_TOKEN", "").strip()
    with _LOCK:
        cached = str(_CACHE.get("token") or "")
        age = time.time() - float(_CACHE.get("fetched_at_epoch") or 0.0)
        if cached and not force_refresh and age < _ttl_seconds(): return cached
        try: return _fetch_latest(reason)
        except Exception as exc:
            _CACHE["last_error"] = type(exc).__name__
            return cached or os.getenv("DHAN_ACCESS_TOKEN", "").strip()


def force_reload(reason: str = "auth_failure") -> bool:
    """Force SM reload, but bound repeated auth reloads of one rejected version.

    Suppression applies only to auth-failure force reloads. Normal TTL reads are
    deliberately unaffected and can discover a newly published version.
    """
    auth_failure = "auth_failure" in reason.lower()
    with _LOCK:
        before_token = str(_CACHE.get("token") or os.getenv("DHAN_ACCESS_TOKEN", "").strip())
        before_version = str(_CACHE.get("version") or "")
        now = time.time()
        if auth_failure and before_version and _CACHE.get("rejected_version") == before_version:
            age = now - float(_CACHE.get("rejected_at_epoch") or 0.0)
            if age < _auth_reload_backoff_s():
                _CACHE["auth_reload_suppressed_count"] = int(_CACHE.get("auth_reload_suppressed_count") or 0) + 1
                _CACHE["last_reload_reason"] = "auth_failure_same_version_suppressed"
                return False
    token = get_access_token(force_refresh=True, reason=reason)
    with _LOCK:
        after_version = str(_CACHE.get("version") or "")
        changed = token != before_token or (bool(after_version) and after_version != before_version)
        if auth_failure and before_version and after_version == before_version and not changed:
            _CACHE["rejected_version"] = before_version
            _CACHE["rejected_at_epoch"] = time.time()
    return bool(token) and changed


def token_metadata() -> dict[str, Any]:
    with _LOCK:
        token = str(_CACHE.get("token") or os.getenv("DHAN_ACCESS_TOKEN", "").strip())
        expiry = _jwt_expiry(token) if token else None
        hours = (expiry - datetime.now(timezone.utc)).total_seconds() / 3600 if expiry else None
        fetched_epoch = float(_CACHE.get("fetched_at_epoch") or 0.0)
        rejected_at = float(_CACHE.get("rejected_at_epoch") or 0.0)
        return {"source": "GCP_SECRET_MANAGER_DYNAMIC" if enabled() else "ENVIRONMENT_FALLBACK",
                "secret_id": _secret_id() if enabled() else None, "secret_version": _CACHE.get("version"),
                "secret_version_created_at_utc": _CACHE.get("version_created_at"),
                "loaded_at_utc": datetime.fromtimestamp(fetched_epoch, tz=timezone.utc).isoformat() if fetched_epoch else None,
                "cache_age_s": round(max(0.0, time.time()-fetched_epoch),1) if fetched_epoch else None,
                "cache_ttl_s": _ttl_seconds(), "expires_at_utc": expiry.isoformat() if expiry else None,
                "hours_remaining": round(hours,2) if hours is not None else None, "expired": bool(hours is not None and hours <= 0),
                "reload_count": int(_CACHE.get("reload_count") or 0), "last_reload_reason": _CACHE.get("last_reload_reason"),
                "last_error_type": _CACHE.get("last_error"), "rejected_secret_version": _CACHE.get("rejected_version"),
                "rejected_at_utc": datetime.fromtimestamp(rejected_at, tz=timezone.utc).isoformat() if rejected_at else None,
                "auth_reload_backoff_s": _auth_reload_backoff_s(),
                "auth_reload_suppressed_count": int(_CACHE.get("auth_reload_suppressed_count") or 0),
                "runtime_instance": os.getenv("K_REVISION") or os.getenv("HOSTNAME") or None,
                "rotation_job": os.getenv("DHAN_TOKEN_ROTATION_JOB", "genesis-system3-dhan-token-rotate"),
                "rotation_schedule": os.getenv("DHAN_TOKEN_ROTATION_SCHEDULE", "07:30 IST daily"),
                "token_present": bool(token), "token_value_exposed": False}


def _set_client_factory_for_tests(factory: Callable[[], Any] | None) -> None:
    global _CLIENT_FACTORY
    with _LOCK:
        _CLIENT_FACTORY = factory
        _CACHE.update({"token":"", "version":None, "secret_resource":None, "fetched_at_epoch":0.0,
                       "version_created_at":None, "reload_count":0, "last_reload_reason":None,
                       "last_error":None, "rejected_version":None, "rejected_at_epoch":0.0,
                       "auth_reload_suppressed_count":0})
