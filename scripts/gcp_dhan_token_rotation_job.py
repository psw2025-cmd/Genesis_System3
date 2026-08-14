#!/usr/bin/env python3
"""Canonical Dhan access-token rotation for Google Cloud Run Job.

This is the sole production token mint authority for Genesis System3. It:
1. reads and validates the authoritative latest ``dhan-access-token`` Secret
   Manager version rather than trusting a potentially stale mounted snapshot;
2. coordinates concurrent Cloud Run Job executions using the expected Secret
   Manager version plus a bounded execution-name stagger and revalidation;
3. generates a new token with PIN + TOTP only when Dhan still rejects the
   authoritative latest token or the token is near expiry;
4. validates the generated token before writing exactly one new authoritative
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


def _safe_profile_valid(client_id: str, token: str) -> dict[str, Any]:
    if not client_id or not token:
        return {
            "valid": False,
            "reason": "credentials_missing",
            "hours_remaining": _hours_remaining(token) if token else None,
        }
    try:
        profile = DhanLogin(client_id).user_profile(token)
        valid = bool(profile) and not bool((profile or {}).get("errorCode"))
        return {
            "valid": valid,
            "reason": None if valid else "DHAN_PROFILE_REJECTED_TOKEN",
            "hours_remaining": round(_hours_remaining(token), 2) if _hours_remaining(token) is not None else None,
            "client_id_suffix_present": bool((profile or {}).get("dhanClientId") or client_id),
        }
    except Exception as exc:
        return {
            "valid": False,
            "reason": type(exc).__name__,
            "hours_remaining": round(_hours_remaining(token), 2) if _hours_remaining(token) is not None else None,
            "client_id_suffix_present": bool(client_id),
        }


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


def _should_rotate(before: dict[str, Any]) -> bool:
    remaining = before.get("hours_remaining")
    should_rotate = not bool(before.get("valid"))
    if remaining is not None:
        try:
            should_rotate = should_rotate or float(remaining) <= MIN_HOURS
        except (TypeError, ValueError):
            return True
    return should_rotate


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
            "live_trading_enabled": False,
            "order_endpoints_called": False,
            "raw_token_exposed": False,
        }
        print(json.dumps(proof, sort_keys=True))
        return 2

    before = _safe_profile_valid(client_id, token)
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
        print(json.dumps(proof, sort_keys=True))
        return 0

    if not _should_rotate(before):
        proof = _skip_proof(
            "SKIPPED_TOKEN_HEALTHY",
            started,
            before,
            before_secret,
            expected_secret_version=expected_version or None,
            cloud_run_execution_present=bool(execution),
        )
        print(json.dumps(proof, sort_keys=True))
        return 0

    settle_s = _execution_stagger_s()
    if settle_s:
        time.sleep(settle_s)
        try:
            settled_token, settled_secret = _latest_token_snapshot()
            settled_before = _safe_profile_valid(client_id, settled_token)
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
                print(json.dumps(proof, sort_keys=True))
                return 0
            token, before_secret, before = settled_token, settled_secret, settled_before
            current_version = settled_version
            if not _should_rotate(before):
                proof = _skip_proof(
                    "SKIPPED_TOKEN_HEALTHY_AFTER_STAGGER",
                    started,
                    before,
                    before_secret,
                    expected_secret_version=expected_version or None,
                    stagger_seconds=settle_s,
                    cloud_run_execution_present=bool(execution),
                )
                print(json.dumps(proof, sort_keys=True))
                return 0
        except Exception:
            # Fail closed on the existing authoritative snapshot; do not expose
            # any payload and do not bypass the subsequent generated-token check.
            pass

    try:
        new_token = _generate_token(client_id, pin, totp_secret)
        generated_check = _safe_profile_valid(client_id, new_token)
        if not generated_check.get("valid"):
            raise RuntimeError("new Dhan token failed profile validation")

        new_version = _persist_authoritative_token(new_token)
        os.environ["DHAN_ACCESS_TOKEN"] = new_token
        after = _safe_profile_valid(client_id, new_token)
        after_secret = _latest_version_proof()
        before_version = str(before_secret.get("version") or "")
        after_version = str(after_secret.get("version") or new_version or "")
        version_advanced = bool(after_version and after_version != before_version)
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
            "live_trading_enabled": False,
            "order_endpoints_called": False,
            "raw_token_exposed": False,
        }
        print(json.dumps(proof, sort_keys=True))
        return 0 if success else 2
    except Exception as exc:
        proof = {
            "status": "ROTATION_FAILED",
            "authority": AUTHORITY,
            "generated_at_utc": started.isoformat(),
            "completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
            "message": str(exc)[:200],
            "before": before,
            "secret_before": before_secret,
            "expected_secret_version": expected_version or None,
            "stagger_seconds": settle_s,
            "cloud_run_execution_present": bool(execution),
            "rotation_threshold_hours": MIN_HOURS,
            "live_trading_enabled": False,
            "order_endpoints_called": False,
            "raw_token_exposed": False,
        }
        print(json.dumps(proof, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
