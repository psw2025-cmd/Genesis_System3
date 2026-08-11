"""Install Cloud Run-safe Dhan read-only wrappers before the FastAPI app loads.

The wrappers keep Google Secret Manager as the runtime token source. On a Dhan
authentication failure they first reload ``latest``. If ``latest`` itself is
invalid, they invoke the single canonical Cloud Run token-rotation Job, wait for
its Secret Manager version to advance, reload that version, and retry the
read-only broker call once.

Safety contract:
- never place, modify, cancel, or route an order;
- never expose a raw token;
- never mint a Dhan token inside the serving web process;
- canonical rotation is allowed only while every LIVE flag is OFF;
- single-flight + cooldown prevents dashboard polling from creating job storms.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Any, Callable

import requests

from core.brokers.dhan.cloud_token_provider import (
    force_reload,
    get_access_token,
    token_metadata,
)

_INSTALL_LOCK = threading.Lock()
_INSTALLED = False
_ROTATION_LOCK = threading.Lock()
_LAST_ROTATION_ATTEMPT_AT = 0.0
_METADATA_TOKEN_URL = (
    "http://metadata.google.internal/computeMetadata/v1/instance/"
    "service-accounts/default/token"
)


def _text_blob(value: Any) -> str:
    try:
        if isinstance(value, dict):
            parts = []
            for key, item in value.items():
                if key.lower() in {"access_token", "token", "authorization"}:
                    continue
                parts.append(f"{key}={_text_blob(item)}")
            return " ".join(parts)
        if isinstance(value, (list, tuple)):
            return " ".join(_text_blob(v) for v in value)
        return str(value or "")
    except Exception:
        return ""


def _auth_failed(result: Any) -> bool:
    blob = _text_blob(result).lower()
    return any(
        marker in blob
        for marker in (
            "token_expired_or_invalid",
            "invalid token",
            "dh-906",
            "unauthorized",
            "http_401",
            "status_code=401",
        )
    )


def _falsey_env(name: str) -> bool:
    return os.getenv(name, "0").strip().lower() in {"", "0", "false", "no", "off"}


def _live_is_locked() -> bool:
    return all(
        _falsey_env(name)
        for name in (
            "LIVE_TRADING_ENABLED",
            "SYSTEM3_LIVE_TRADING_ALLOWED",
            "AUTO_EXECUTE_TRADES",
        )
    )


def _canonical_heal_enabled() -> bool:
    raw = os.getenv("DHAN_CANONICAL_ROTATION_SELF_HEAL", "1").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _rotation_cooldown_s() -> float:
    raw = os.getenv("DHAN_CANONICAL_ROTATION_COOLDOWN_S", "130").strip()
    try:
        return max(120.0, min(float(raw), 3600.0))
    except ValueError:
        return 130.0


def _metadata_access_token() -> str:
    response = requests.get(
        _METADATA_TOKEN_URL,
        headers={"Metadata-Flavor": "Google"},
        timeout=10,
    )
    response.raise_for_status()
    token = str((response.json() or {}).get("access_token") or "").strip()
    if not token:
        raise RuntimeError("metadata server returned no Google access token")
    return token


def _invoke_canonical_rotation(reason: str) -> dict[str, Any]:
    """Run the sole GCP token mint authority and return non-secret proof."""
    global _LAST_ROTATION_ATTEMPT_AT

    proof: dict[str, Any] = {
        "attempted": False,
        "success": False,
        "authority": "gcp-cloud-run-job",
        "reason": reason,
        "raw_token_exposed": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }

    if not _canonical_heal_enabled():
        proof["skipped"] = "CANONICAL_SELF_HEAL_DISABLED"
        return proof
    if not _live_is_locked():
        proof["skipped"] = "LIVE_GATE_NOT_LOCKED"
        return proof
    if not (os.getenv("K_SERVICE") or os.getenv("CLOUD_MODE")):
        proof["skipped"] = "NOT_GCP_RUNTIME"
        return proof

    now = time.time()
    cooldown = _rotation_cooldown_s()
    if _LAST_ROTATION_ATTEMPT_AT and now - _LAST_ROTATION_ATTEMPT_AT < cooldown:
        proof["skipped"] = "COOLDOWN"
        proof["cooldown_remaining_s"] = int(cooldown - (now - _LAST_ROTATION_ATTEMPT_AT))
        return proof

    if not _ROTATION_LOCK.acquire(timeout=2):
        proof["skipped"] = "SINGLE_FLIGHT_BUSY"
        return proof

    try:
        now = time.time()
        if _LAST_ROTATION_ATTEMPT_AT and now - _LAST_ROTATION_ATTEMPT_AT < cooldown:
            proof["skipped"] = "COOLDOWN"
            proof["cooldown_remaining_s"] = int(cooldown - (now - _LAST_ROTATION_ATTEMPT_AT))
            return proof
        _LAST_ROTATION_ATTEMPT_AT = now
        proof["attempted"] = True

        before = token_metadata()
        before_version = str(before.get("secret_version") or "")
        project = (
            os.getenv("GOOGLE_CLOUD_PROJECT")
            or os.getenv("GCP_PROJECT")
            or "system3-openalgo-safe"
        )
        region = os.getenv("GCP_REGION", "asia-south1")
        job = os.getenv("DHAN_TOKEN_ROTATION_JOB", "genesis-system3-dhan-token-rotate")
        access_token = _metadata_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        run_url = (
            f"https://run.googleapis.com/v2/projects/{project}/locations/{region}/"
            f"jobs/{job}:run"
        )
        response = requests.post(run_url, headers=headers, json={}, timeout=30)
        response.raise_for_status()
        operation = response.json() or {}
        op_name = str(operation.get("name") or "")
        proof["job"] = job
        proof["operation_started"] = bool(op_name)
        if not op_name:
            proof["error_type"] = "MissingOperationName"
            return proof

        op_url = f"https://run.googleapis.com/v2/{op_name}"
        deadline = time.time() + float(os.getenv("DHAN_CANONICAL_ROTATION_WAIT_S", "120") or "120")
        while time.time() < deadline:
            poll = requests.get(op_url, headers=headers, timeout=20)
            poll.raise_for_status()
            payload = poll.json() or {}
            if payload.get("done") is True:
                if payload.get("error"):
                    proof["error_type"] = "CloudRunJobOperationError"
                    proof["operation_error_code"] = (payload.get("error") or {}).get("code")
                    return proof
                break
            time.sleep(2)
        else:
            proof["error_type"] = "CloudRunJobOperationTimeout"
            return proof

        # Secret Manager is the hand-off boundary. Wait until the canonical job
        # publishes a different concrete version, then let the existing dynamic
        # provider update DHAN_ACCESS_TOKEN in-process.
        reload_deadline = time.time() + 45
        after_version = before_version
        while time.time() < reload_deadline:
            get_access_token(force_refresh=True, reason="canonical_rotation_completed")
            meta = token_metadata()
            after_version = str(meta.get("secret_version") or "")
            if after_version and after_version != before_version:
                proof["success"] = True
                break
            time.sleep(2)

        proof["secret_version_advanced"] = bool(
            before_version and after_version and before_version != after_version
        )
        proof["secret_version_before"] = before_version or None
        proof["secret_version_after"] = after_version or None
        if not proof["success"]:
            proof["error_type"] = "SecretVersionDidNotAdvance"
        return proof
    except Exception as exc:
        proof["error_type"] = type(exc).__name__
        proof["message"] = str(exc)[:160]
        return proof
    finally:
        _ROTATION_LOCK.release()


def _clear_status_cache(module: Any) -> None:
    try:
        module._STATUS_RESULT_CACHE = None
        module._STATUS_RESULT_CACHE_AT = 0.0
    except Exception:
        pass


def _wrap_read(module: Any, name: str, original: Callable[..., Any]) -> Callable[..., Any]:
    def wrapped(*args, **kwargs):
        get_access_token(reason=f"pre_{name}")
        result = original(*args, **kwargs)
        reload_attempted = False
        reload_success = False
        canonical_rotation: dict[str, Any] = {
            "attempted": False,
            "success": False,
            "raw_token_exposed": False,
        }

        if _auth_failed(result):
            reload_attempted = True
            reload_success = force_reload(reason=f"{name}_auth_failure")
            _clear_status_cache(module)
            if reload_success:
                result = original(*args, **kwargs)

            # A same-version reload cannot repair a token Dhan has invalidated.
            # Escalate only to the canonical GCP job; the web process itself
            # never calls Dhan token-generation APIs.
            if _auth_failed(result):
                canonical_rotation = _invoke_canonical_rotation(f"{name}_auth_failure")
                if canonical_rotation.get("success"):
                    _clear_status_cache(module)
                    result = original(*args, **kwargs)

        if isinstance(result, dict):
            result = dict(result)
            result["token_reload"] = {
                "attempted": reload_attempted,
                "success": reload_success,
                "raw_token_exposed": False,
            }
            result["canonical_rotation"] = canonical_rotation
            if name == "get_status":
                result["token_proof"] = token_metadata()
                result["cloud_runtime_patch"] = True
        return result

    wrapped.__name__ = getattr(original, "__name__", name)
    wrapped.__doc__ = getattr(original, "__doc__", None)
    return wrapped


def install() -> dict[str, Any]:
    """Patch the read-only adapter once and return non-secret install proof."""
    global _INSTALLED
    with _INSTALL_LOCK:
        if _INSTALLED:
            return {
                "installed": True,
                "already_installed": True,
                "live_trading_enabled": False,
            }

        get_access_token(force_refresh=True, reason="cloud_runtime_startup")

        from core.brokers.dhan import dhan_readonly as module

        patched = []
        for name in (
            "get_status",
            "get_profile",
            "get_funds",
            "get_holdings",
            "get_positions",
            "get_orders_readonly",
        ):
            original = getattr(module, name, None)
            if callable(original) and not getattr(original, "_system3_cloud_wrapped", False):
                wrapped = _wrap_read(module, name, original)
                setattr(wrapped, "_system3_cloud_wrapped", True)
                setattr(module, name, wrapped)
                patched.append(name)

        _INSTALLED = True
        return {
            "installed": True,
            "patched": patched,
            "token_source": token_metadata().get("source"),
            "canonical_rotation_authority": "gcp-cloud-run-job",
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "raw_token_exposed": False,
        }
