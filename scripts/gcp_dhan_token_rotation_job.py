#!/usr/bin/env python3
"""Canonical Dhan access-token rotation for Google Cloud Run Job.

This is the sole production token mint authority for Genesis System3. It:
1. reads and validates the authoritative latest ``dhan-access-token`` Secret
   Manager version rather than trusting a potentially stale mounted snapshot;
2. distinguishes broker-auth rejection from transient network/API failures so
   transient failures can never authorize token generation;
3. coordinates concurrent Cloud Run Job executions using the expected Secret
   Manager version plus a bounded execution-name stagger and revalidation;
4. generates a new token with PIN + TOTP only when Dhan explicitly rejects the
   authoritative latest token or the JWT is genuinely near expiry;
5. validates the generated token before writing exactly one new authoritative
   Secret Manager version.

It never calls order endpoints and always forces LIVE execution OFF.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any

import pyotp
from dhanhq import DhanLogin
from google.cloud import secretmanager

PROJECT = (
    os.getenv("GOOGLE_CLOUD_PROJECT")
    or os.getenv("GCP_PROJECT")
    or os.getenv("SYSTEM3_FIRESTORE_PROJECT")
    or "system3-openalgo-safe"
)
SECRET_ID = os.getenv("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token").strip() or "dhan-access-token"
MIN_HOURS = float(os.getenv("DHAN_ROTATE_WHEN_HOURS_LEFT", "6"))
AUTHORITY = "gcp-cloud-run-job"

PROFILE_VALID = "VALID"
PROFILE_AUTH_INVALID = "AUTH_INVALID"
PROFILE_TRANSIENT_ERROR = "TRANSIENT_ERROR"
PROFILE_CONFIG_ERROR = "CONFIG_ERROR"

_AUTH_MARKERS = (
    "dh-906",
    "invalid token",
    "token expired",
    "token_expired_or_invalid",
    "unauthorized",
    "http_401",
    "status_code=401",
)

# stdout is intentionally limited to constant, allow-listed evidence lines.
# No object that has ever contained a token, broker response, PIN, TOTP, or
# exception body is serialized to logs. Detailed decisions stay in process.
_SAFE_STATUS_LINES = {
    "ROTATED_AND_VERIFIED": '{"authority":"gcp-cloud-run-job","live_trading_enabled":false,"order_endpoints_called":false,"raw_token_exposed":false,"status":"ROTATED_AND_VERIFIED"}',
    "ROTATION_FAILED": '{"authority":"gcp-cloud-run-job","live_trading_enabled":false,"order_endpoints_called":false,"raw_token_exposed":false,"status":"ROTATION_FAILED"}',
    "SKIPPED_CONCURRENT_ROTATION_WON": '{"authority":"gcp-cloud-run-job","live_trading_enabled":false,"order_endpoints_called":false,"raw_token_exposed":false,"status":"SKIPPED_CONCURRENT_ROTATION_WON"}',
    "SKIPPED_TOKEN_HEALTHY": '{"authority":"gcp-cloud-run-job","live_trading_enabled":false,"order_endpoints_called":false,"raw_token_exposed":false,"status":"SKIPPED_TOKEN_HEALTHY"}',
    "SKIPPED_TOKEN_HEALTHY_AFTER_STAGGER": '{"authority":"gcp-cloud-run-job","live_trading_enabled":false,"order_endpoints_called":false,"raw_token_exposed":false,"status":"SKIPPED_TOKEN_HEALTHY_AFTER_STAGGER"}',
    "BLOCKED_TRANSIENT_PROFILE_ERROR": '{"authority":"gcp-cloud-run-job","live_trading_enabled":false,"order_endpoints_called":false,"raw_token_exposed":false,"status":"BLOCKED_TRANSIENT_PROFILE_ERROR"}',
    "BLOCKED_PROFILE_CONFIG_ERROR": '{"authority":"gcp-cloud-run-job","live_trading_enabled":false,"order_endpoints_called":false,"raw_token_exposed":false,"status":"BLOCKED_PROFILE_CONFIG_ERROR"}',
    "BLOCKED_STAGGER_REVALIDATION_ERROR": '{"authority":"gcp-cloud-run-job","live_trading_enabled":false,"order_endpoints_called":false,"raw_token_exposed":false,"status":"BLOCKED_STAGGER_REVALIDATION_ERROR"}',
    "BLOCKED_MINT_NOT_AUTHORIZED": '{"authority":"gcp-cloud-run-job","live_trading_enabled":false,"order_endpoints_called":false,"raw_token_exposed":false,"status":"BLOCKED_MINT_NOT_AUTHORIZED"}',
}


def _emit_status(status: str) -> None:
    """Emit a constant non-secret status record; unknown values fail closed."""
    line = _SAFE_STATUS_LINES.get(status, _SAFE_STATUS_LINES["ROTATION_FAILED"])
    print(line)


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


def _hours_remaining(token: str) -> float | None:
    expiry = _jwt_expiry(token)
    if expiry is None:
        return None
    return (expiry - datetime.now(timezone.utc)).total_seconds() / 3600


def _safe_blob(value: Any) -> str:
    """Flatten only non-secret diagnostic text for conservative auth matching."""
    try:
        if isinstance(value, dict):
            parts: list[str] = []
            for key, item in value.items():
                if str(key).lower() in {"access_token", "token", "authorization"}:
                    continue
                parts.append(f"{key}={_safe_blob(item)}")
            return " ".join(parts)
        if isinstance(value, (list, tuple)):
            return " ".join(_safe_blob(item) for item in value)
        return str(value or "")
    except Exception:
        return ""


def _is_auth_failure(value: Any, *, status_code: int | None = None) -> bool:
    blob = _safe_blob(value).lower()
    return status_code == 401 or any(marker in blob for marker in _AUTH_MARKERS)


def _profile_probe(client_id: str, token: str) -> dict[str, Any]:
    """Return tri-state broker-auth truth without turning transport errors into auth failures."""
    remaining = _hours_remaining(token) if token else None
    hours_remaining = round(remaining, 2) if remaining is not None else None
    base = {
        "hours_remaining": hours_remaining,
        "client_id_suffix_present": bool(client_id),
    }
    if not client_id or not token:
        return {
            **base,
            "valid": False,
            "auth_state": PROFILE_CONFIG_ERROR,
            "reason": "credentials_missing",
        }

    try:
        profile = DhanLogin(client_id).user_profile(token)
        if profile and not bool((profile or {}).get("errorCode")):
            return {
                **base,
                "valid": True,
                "auth_state": PROFILE_VALID,
                "reason": None,
                "client_id_suffix_present": bool((profile or {}).get("dhanClientId") or client_id),
            }
        if _is_auth_failure(profile):
            return {
                **base,
                "valid": False,
                "auth_state": PROFILE_AUTH_INVALID,
                "reason": "DHAN_PROFILE_REJECTED_TOKEN",
            }
        return {
            **base,
            "valid": False,
            "auth_state": PROFILE_TRANSIENT_ERROR,
            "reason": "DHAN_PROFILE_NON_AUTH_ERROR",
        }
    except Exception as exc:
        response = getattr(exc, "response", None)
        status_code = getattr(response, "status_code", None) if response is not None else None
        body = ""
        if response is not None:
            try:
                body = str(getattr(response, "text", "") or "")[:240]
            except Exception:
                body = ""
        diagnostic = f"{status_code or ''} {body} {type(exc).__name__} {exc}"
        auth_invalid = _is_auth_failure(diagnostic, status_code=status_code)
        return {
            **base,
            "valid": False,
            "auth_state": PROFILE_AUTH_INVALID if auth_invalid else PROFILE_TRANSIENT_ERROR,
            "reason": "DHAN_AUTH_REJECTED" if auth_invalid else type(exc).__name__,
            "http_status": status_code,
        }


def _safe_profile_valid(client_id: str, token: str) -> dict[str, Any]:
    """Backward-compatible name retained for existing tests and audit tooling."""
    return _profile_probe(client_id, token)


def _latest_token_snapshot() -> tuple[str, dict[str, Any]]:
    """Return latest token internally plus non-secret version proof."""
    client = secretmanager.SecretManagerServiceClient()
    resource = f"projects/{PROJECT}/secrets/{SECRET_ID}/versions/latest"
    response = client.access_secret_version(request={"name": resource})
    version_name = str(getattr(response, "name", "") or "")
    payload = getattr(getattr(response, "payload", None), "data", b"") or b""
    token = payload.decode("utf-8").strip() if payload else ""
    version = client.get_secret_version(request={"name": version_name}) if version_name else None
    created = getattr(version, "create_time", None)
    if hasattr(created, "isoformat"):
        created = created.isoformat()
    proof = {
        "secret_id": SECRET_ID,
        "version": version_name.rsplit("/", 1)[-1] if version_name else None,
        "created_at": str(created) if created else None,
        "token_present": bool(token),
        "raw_token_exposed": False,
    }
    return token, proof


def _latest_version_proof() -> dict[str, Any]:
    try:
        _token, proof = _latest_token_snapshot()
        return proof
    except Exception as exc:
        return {
            "secret_id": SECRET_ID,
            "version": None,
            "token_present": False,
            "raw_token_exposed": False,
            "metadata_error_type": type(exc).__name__,
        }


def _execution_stagger_s() -> int:
    """Spread independently-started executions without any new GCP privilege."""
    execution = os.getenv("CLOUD_RUN_EXECUTION", "").strip()
    if not execution:
        return 0
    slots = max(2, min(8, int(os.getenv("DHAN_ROTATION_STAGGER_SLOTS", "8") or "8")))
    step = max(2, min(10, int(os.getenv("DHAN_ROTATION_STAGGER_STEP_S", "6") or "6")))
    digest = hashlib.sha256(execution.encode("utf-8")).hexdigest()
    slot = int(digest[:8], 16) % slots
    return 3 + (slot * step)


def _near_expiry(before: dict[str, Any]) -> bool:
    remaining = before.get("hours_remaining")
    if remaining is None:
        return False
    try:
        return float(remaining) <= MIN_HOURS
    except (TypeError, ValueError):
        return False


def _should_rotate(before: dict[str, Any]) -> bool:
    """Authorize minting only for explicit auth rejection or proven near-expiry."""
    state = str(before.get("auth_state") or "")
    return state == PROFILE_AUTH_INVALID or _near_expiry(before)


def _non_rotation_status(before: dict[str, Any], healthy_status: str) -> tuple[str, int]:
    state = str(before.get("auth_state") or "")
    if state == PROFILE_TRANSIENT_ERROR:
        return "BLOCKED_TRANSIENT_PROFILE_ERROR", 2
    if state == PROFILE_CONFIG_ERROR:
        return "BLOCKED_PROFILE_CONFIG_ERROR", 2
    return healthy_status, 0


def _skip_proof(
    status: str,
    started: datetime,
    before: dict[str, Any],
    before_secret: dict[str, Any],
    **extra: Any,
) -> dict[str, Any]:
    proof = {
        "status": status,
        "authority": AUTHORITY,
        "generated_at_utc": started.isoformat(),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "before": before,
        "after": before,
        "secret_before": before_secret,
        "secret_after": before_secret,
        "secret_version_advanced": False,
        "rotation_threshold_hours": MIN_HOURS,
        "mint_authorized": _should_rotate(before),
        "live_trading_enabled": False,
        "order_endpoints_called": False,
        "raw_token_exposed": False,
    }
    proof.update(extra)
    return proof


def _generate_token(client_id: str, pin: str, totp_secret: str) -> str:
    if not client_id or not pin or not totp_secret:
        raise RuntimeError("Dhan client/PIN/TOTP prerequisites are missing")

    seconds_left = 30 - (int(time.time()) % 30)
    if seconds_left < 5:
        time.sleep(seconds_left + 0.5)

    otp = pyotp.TOTP(totp_secret).now()
    response = DhanLogin(client_id).generate_token(pin, otp)
    token = (
        (response or {}).get("accessToken")
        or (response or {}).get("access_token")
        or ((response or {}).get("data") or {}).get("accessToken")
    )
    if not token:
        raise RuntimeError("Dhan generate_token returned no access token")
    return str(token).strip()


def _persist_authoritative_token(token: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{PROJECT}/secrets/{SECRET_ID}"
    response = client.add_secret_version(
        request={"parent": parent, "payload": {"data": token.encode("utf-8")}}
    )
    return str(getattr(response, "name", "") or "").rsplit("/", 1)[-1]


def main() -> int:
    os.environ["CLOUD_MODE"] = "1"
    os.environ["CLOUD_WORKER"] = "1"
    os.environ["DHAN_TOKEN_ROTATION_AUTHORITY"] = AUTHORITY
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
    os.environ["LIVE_TRADING_ENABLED"] = "0"
    os.environ["AUTO_EXECUTE_TRADES"] = "0"
    os.environ["ANALYZE_MODE"] = "1"

    started = datetime.now(timezone.utc)
    client_id = os.getenv("DHAN_CLIENT_ID", "").strip()
    pin = os.getenv("DHAN_PIN", "").strip()
    totp_secret = os.getenv("DHAN_TOTP_SECRET", "").strip()
    expected_version = os.getenv("DHAN_ROTATION_EXPECTED_VERSION", "").strip()
    execution = os.getenv("CLOUD_RUN_EXECUTION", "").strip()

    try:
        token, before_secret = _latest_token_snapshot()
    except Exception as exc:
        proof = {
            "status": "ROTATION_FAILED",
            "authority": AUTHORITY,
            "generated_at_utc": started.isoformat(),
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
            "message": "authoritative latest token could not be loaded",
            "secret_before": _latest_version_proof(),
            "expected_secret_version": expected_version or None,
            "cloud_run_execution_present": bool(execution),
            "rotation_threshold_hours": MIN_HOURS,
            "mint_authorized": False,
            "live_trading_enabled": False,
            "order_endpoints_called": False,
            "raw_token_exposed": False,
        }
        _emit_status("ROTATION_FAILED")
        return 2

    before = _profile_probe(client_id, token)
    current_version = str(before_secret.get("version") or "")

    if expected_version and current_version and current_version != expected_version and before.get("valid"):
        proof = _skip_proof(
            "SKIPPED_CONCURRENT_ROTATION_WON",
            started,
            before,
            before_secret,
            expected_secret_version=expected_version,
            observed_secret_version=current_version,
            cloud_run_execution_present=bool(execution),
            coordination="version_mismatch_latest_valid",
        )
        _emit_status("SKIPPED_CONCURRENT_ROTATION_WON")
        return 0

    if not _should_rotate(before):
        status, rc = _non_rotation_status(before, "SKIPPED_TOKEN_HEALTHY")
        proof = _skip_proof(
            status,
            started,
            before,
            before_secret,
            expected_secret_version=expected_version or None,
            cloud_run_execution_present=bool(execution),
            transient_errors_authorize_mint=False,
        )
        _emit_status(status)
        return rc

    settle_s = _execution_stagger_s()
    if settle_s:
        time.sleep(settle_s)
        try:
            settled_token, settled_secret = _latest_token_snapshot()
            settled_before = _profile_probe(client_id, settled_token)
            settled_version = str(settled_secret.get("version") or "")
            if settled_version and settled_version != current_version and settled_before.get("valid"):
                proof = _skip_proof(
                    "SKIPPED_CONCURRENT_ROTATION_WON",
                    started,
                    settled_before,
                    settled_secret,
                    expected_secret_version=expected_version or None,
                    observed_secret_version=settled_version,
                    previous_secret_version=current_version or None,
                    stagger_seconds=settle_s,
                    cloud_run_execution_present=bool(execution),
                    coordination="post_stagger_latest_valid",
                )
                _emit_status("SKIPPED_CONCURRENT_ROTATION_WON")
                return 0
            token, before_secret, before = settled_token, settled_secret, settled_before
            current_version = settled_version
            if not _should_rotate(before):
                status, rc = _non_rotation_status(before, "SKIPPED_TOKEN_HEALTHY_AFTER_STAGGER")
                proof = _skip_proof(
                    status,
                    started,
                    before,
                    before_secret,
                    expected_secret_version=expected_version or None,
                    stagger_seconds=settle_s,
                    cloud_run_execution_present=bool(execution),
                    transient_errors_authorize_mint=False,
                )
                _emit_status(status)
                return rc
        except Exception as exc:
            # A transient revalidation failure must never increase authority.
            proof = _skip_proof(
                "BLOCKED_STAGGER_REVALIDATION_ERROR",
                started,
                before,
                before_secret,
                expected_secret_version=expected_version or None,
                stagger_seconds=settle_s,
                cloud_run_execution_present=bool(execution),
                error_type=type(exc).__name__,
                transient_errors_authorize_mint=False,
            )
            _emit_status("BLOCKED_STAGGER_REVALIDATION_ERROR")
            return 2

    # Last fail-closed authority check immediately before the only mint call.
    if not _should_rotate(before):
        proof = _skip_proof(
            "BLOCKED_MINT_NOT_AUTHORIZED",
            started,
            before,
            before_secret,
            expected_secret_version=expected_version or None,
            stagger_seconds=settle_s,
            cloud_run_execution_present=bool(execution),
            transient_errors_authorize_mint=False,
        )
        _emit_status("BLOCKED_MINT_NOT_AUTHORIZED")
        return 2

    try:
        new_token = _generate_token(client_id, pin, totp_secret)
        generated_check = _profile_probe(client_id, new_token)
        if not generated_check.get("valid"):
            raise RuntimeError(
                "new Dhan token failed profile validation: "
                f"{generated_check.get('auth_state')}:{generated_check.get('reason')}"
            )

        new_version = _persist_authoritative_token(new_token)
        os.environ["DHAN_ACCESS_TOKEN"] = new_token
        after_secret = _latest_version_proof()
        before_version = str(before_secret.get("version") or "")
        after_version = str(after_secret.get("version") or new_version or "")
        version_advanced = bool(after_version and after_version != before_version)
        # generated_check is already a successful broker validation. Avoid a
        # redundant second profile call after persistence, which only increases
        # rate-limit/timeout exposure without adding authority proof.
        after = dict(generated_check)
        success = bool(after.get("valid") and version_advanced)
        proof = {
            "status": "ROTATED_AND_VERIFIED" if success else "ROTATION_FAILED",
            "authority": AUTHORITY,
            "generated_at_utc": started.isoformat(),
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "strategy": "generate_token_pin_totp",
            "coordination": "secret_version_expected_plus_execution_stagger",
            "expected_secret_version": expected_version or None,
            "stagger_seconds": settle_s,
            "cloud_run_execution_present": bool(execution),
            "before": before,
            "after": after,
            "secret_before": before_secret,
            "secret_after": after_secret,
            "secret_version_advanced": version_advanced,
            "secret_persisted": version_advanced,
            "rotation_threshold_hours": MIN_HOURS,
            "mint_authorized": True,
            "transient_errors_authorize_mint": False,
            "post_persist_profile_reprobe_performed": False,
            "live_trading_enabled": False,
            "order_endpoints_called": False,
            "raw_token_exposed": False,
        }
        if success:
            _emit_status("ROTATED_AND_VERIFIED")
            return 0
        _emit_status("ROTATION_FAILED")
        return 2
    except Exception as exc:
        proof = {
            "status": "ROTATION_FAILED",
            "authority": AUTHORITY,
            "generated_at_utc": started.isoformat(),
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
            "message": "token rotation failed",
            "before": before,
            "secret_before": before_secret,
            "expected_secret_version": expected_version or None,
            "stagger_seconds": settle_s,
            "cloud_run_execution_present": bool(execution),
            "rotation_threshold_hours": MIN_HOURS,
            "mint_authorized": _should_rotate(before),
            "transient_errors_authorize_mint": False,
            "live_trading_enabled": False,
            "order_endpoints_called": False,
            "raw_token_exposed": False,
        }
        _emit_status("ROTATION_FAILED")
        return 2


if __name__ == "__main__":
    sys.exit(main())