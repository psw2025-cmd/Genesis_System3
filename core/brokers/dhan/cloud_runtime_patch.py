"""Install Cloud Run-safe Dhan read-only wrappers before the FastAPI app loads.

The wrappers keep Google Secret Manager as the runtime token source. On a Dhan
authentication failure they first reload ``latest``. If ``latest`` itself is
invalid, they may invoke the single canonical Cloud Run token-rotation Job only
when that authority is explicitly enabled, wait for its Secret Manager version
to advance, reload that version, and retry the read-only broker call once.

Broker ``connected`` truth is stricter than token presence: the cloud status
path must prove Profile plus Funds, Holdings, and Positions using bounded,
read-only Dhan calls. Only sanitized success/error/count metadata is returned.

Safety contract:
- never place, modify, cancel, or route an order;
- never expose a raw token;
- never mint a Dhan token inside the serving web process;
- canonical rotation is allowed only while every LIVE flag is OFF;
- local single-flight + cooldown bounds one process;
- the expected Secret Manager version is passed to the Job so separate Cloud Run
  instances/executions can coordinate without exposing token payloads.
"""
from __future__ import annotations

import base64
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait
from typing import Any, Callable

from core.brokers.dhan.cloud_status_probe import get_cloud_status, _safe_upstream_code
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
    """Return true only for affirmative auth failures that justify recovery.

    A stable normalized auth classification/error is authoritative even when
    Dhan also reports DH-906. Bare DH-906 remains a non-auth request rejection,
    and Dhan 805/HTTP429 remains rate-limit evidence that must never trigger
    Secret Manager reload or rotation.
    """
    blob = _text_blob(result).lower()
    code = _safe_upstream_code(blob)
    if isinstance(result, dict):
        auth_classification = str(result.get("auth_classification") or "").strip()
        stable_error = str(result.get("error") or "").strip()
        if auth_classification in {
            "DHAN_TOKEN_REJECTED",
            "DHAN_TOKEN_REJECTED_CLOCK_UNKNOWN",
            "TOKEN_CLOCK_EXPIRED",
        } or stable_error == "TOKEN_EXPIRED_OR_INVALID":
            return True
        upstream = str(result.get("upstream_classification") or "").strip()
        if upstream == "DHAN_RATE_LIMITED":
            return False
    if code == 805:
        return False
    if code == 906:
        # The status/profile classifiers are responsible for upgrading the
        # observed DH-906 + explicit Invalid Token anomaly to the stable
        # TOKEN_EXPIRED_OR_INVALID signal above. A bare 906 cannot self-heal.
        return False
    if code == 808:
        return True
    return any(
        marker in blob
        for marker in (
            "token_expired_or_invalid",
            "invalid token",
            "unauthorized",
            "http_401",
            "status_code=401",
            "authentication failed",
            "authentication error",
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
    # Fail-closed: web must reload Secret Manager only unless explicitly enabled.
    raw = os.getenv("DHAN_CANONICAL_ROTATION_SELF_HEAL", "0").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _rotation_cooldown_s() -> float:
    # Default 900s (15 min) mutex window between auto-heal Job invokes.
    raw = os.getenv("DHAN_CANONICAL_ROTATION_COOLDOWN_S", "900").strip()
    try:
        return max(120.0, min(float(raw), 3600.0))
    except ValueError:
        return 900.0


def _metadata_access_token() -> str:
    import requests

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

    import requests

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
        proof["expected_secret_version"] = before_version or None
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
        request_body: dict[str, Any] = {}
        if before_version:
            request_body = {
                "overrides": {
                    "containerOverrides": [
                        {
                            "env": [
                                {
                                    "name": "DHAN_ROTATION_EXPECTED_VERSION",
                                    "value": before_version,
                                }
                            ]
                        }
                    ]
                }
            }
        response = requests.post(run_url, headers=headers, json=request_body, timeout=30)
        response.raise_for_status()
        # Best-effort operator signal on Pub/Sub topic (never required for mint success).
        try:
            topic = os.getenv("DHAN_ROTATE_PUBSUB_TOPIC", "broker-token-rotate").strip()
            if topic:
                pub_url = (
                    f"https://pubsub.googleapis.com/v1/projects/{project}/topics/{topic}:publish"
                )
                msg = json.dumps(
                    {
                        "reason": reason,
                        "expected_secret_version": before_version or None,
                        "job": job,
                    }
                ).encode("utf-8")
                requests.post(
                    pub_url,
                    headers=headers,
                    json={"messages": [{"data": base64.b64encode(msg).decode("ascii")}]},
                    timeout=10,
                )
                proof["pubsub_topic"] = topic
        except Exception:
            proof["pubsub_publish"] = "best_effort_failed"
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


def _safe_count(data: Any) -> int | None:
    if isinstance(data, (list, tuple)):
        return len(data)
    if isinstance(data, dict):
        nested = data.get("data")
        if isinstance(nested, (list, tuple)):
            return len(nested)
    return None


def _strict_account_proof(module: Any, *, timeout_s: float = 4.0) -> dict[str, Any]:
    """Prove funds/holdings/positions without returning any account payload."""
    creds = module.get_dhan_credentials()
    client_id = str(creds.get("client_id") or "").strip().lstrip("\ufeff")
    access_token = str(creds.get("access_token") or "").strip().lstrip("\ufeff")
    rest_get = getattr(module, "_rest_get", None)
    payload_error = getattr(module, "_payload_error", None)
    exception_error = getattr(module, "_exception_error", None)
    specs = {
        "funds": (getattr(module, "_DHAN_FUNDS_URL", ""), False),
        "holdings": (getattr(module, "_DHAN_HOLDINGS_URL", ""), True),
        "positions": (getattr(module, "_DHAN_POSITIONS_URL", ""), True),
    }
    if not client_id or not access_token or not callable(rest_get) or not callable(payload_error):
        return {
            "ok": False,
            "error": "ACCOUNT_PROOF_UNAVAILABLE",
            "checks": {},
            "raw_payload_exposed": False,
        }
    if any(not url for url, _include_client_id in specs.values()):
        return {
            "ok": False,
            "error": "ACCOUNT_PROOF_UNAVAILABLE",
            "checks": {},
            "raw_payload_exposed": False,
        }

    def run_one(name: str, url: str, include_client_id: bool) -> tuple[str, dict[str, Any]]:
        started = time.monotonic()
        try:
            data = rest_get(
                url,
                access_token,
                client_id,
                timeout=max(1.0, min(float(timeout_s), 5.0)),
                include_client_id=include_client_id,
            )
            error = payload_error(data)
            return name, {
                "ok": error is None,
                "error": error,
                "item_count": _safe_count(data),
                "latency_ms": int((time.monotonic() - started) * 1000),
            }
        except Exception as exc:
            error = exception_error(exc) if callable(exception_error) else f"NETWORK_ERROR:{type(exc).__name__}"
            return name, {
                "ok": False,
                "error": error,
                "item_count": None,
                "latency_ms": int((time.monotonic() - started) * 1000),
            }

    executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="dhan-proof")
    future_to_name = {
        executor.submit(run_one, name, url, include_client_id): name
        for name, (url, include_client_id) in specs.items()
    }
    done, pending = wait(future_to_name, timeout=max(1.0, min(float(timeout_s) + 1.0, 6.0)))
    checks: dict[str, dict[str, Any]] = {}
    for future in done:
        name = future_to_name[future]
        try:
            _returned_name, proof = future.result()
            checks[name] = proof
        except Exception as exc:
            checks[name] = {
                "ok": False,
                "error": f"PROBE_ERROR:{type(exc).__name__}",
                "item_count": None,
                "latency_ms": None,
            }
    for future in pending:
        name = future_to_name[future]
        future.cancel()
        checks[name] = {
            "ok": False,
            "error": "PROBE_TIMEOUT",
            "item_count": None,
            "latency_ms": None,
        }
    executor.shutdown(wait=False, cancel_futures=True)

    first_error = next(
        (checks[name].get("error") for name in ("funds", "holdings", "positions") if not checks.get(name, {}).get("ok")),
        None,
    )
    return {
        "ok": len(checks) == 3 and all(checks.get(name, {}).get("ok") for name in specs),
        "error": first_error,
        "checks": checks,
        "raw_payload_exposed": False,
    }


def _strict_cloud_status(module: Any) -> dict[str, Any]:
    """Require Profile + Funds + Holdings + Positions for connected=true."""
    status = dict(get_cloud_status(module))
    if "account_read_proof" in status:
        return status

    profile_ok = status.get("connected") is True
    proof: dict[str, Any] = {
        "profile": {
            "ok": profile_ok,
            "error": None if profile_ok else status.get("error"),
        },
        "raw_payload_exposed": False,
    }
    if profile_ok:
        account = _strict_account_proof(module)
        proof.update(account.get("checks") or {})
        account_ok = bool(account.get("ok"))
        if not account_ok:
            status["connected"] = False
            status["error"] = account.get("error") or "ACCOUNT_READ_PROOF_FAILED"
            if status["error"] == "TOKEN_EXPIRED_OR_INVALID":
                status["auth_classification"] = "DHAN_TOKEN_REJECTED"
    else:
        account_ok = False
        for name in ("funds", "holdings", "positions"):
            proof[name] = {"ok": False, "error": "SKIPPED_PROFILE_NOT_AUTHENTICATED"}

    status["account_read_proof"] = proof
    status["broker_truth_contract"] = "profile+funds+holdings+positions"
    status["broker_truth_complete"] = bool(profile_ok and account_ok)
    status["raw_account_payload_exposed"] = False
    try:
        module._STATUS_RESULT_CACHE = dict(status)
        module._STATUS_RESULT_CACHE_AT = time.time()
    except Exception:
        pass
    return status


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

        # The cloud status path uses one bounded Profile probe followed by a
        # parallel, bounded read-only proof for funds/holdings/positions. This
        # avoids cosmetic connected=true while keeping dashboard polling bounded.
        module.get_status = lambda: _strict_cloud_status(module)

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
            "broker_status_probe": "cloud_profile_plus_account_reads_bounded",
            "broker_truth_contract": "profile+funds+holdings+positions",
            "canonical_rotation_authority": "gcp-cloud-run-job",
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "raw_token_exposed": False,
        }
