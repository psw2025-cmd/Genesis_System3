#!/usr/bin/env python3
"""Rotate the Dhan access token in a dedicated Google Cloud Run Job.

This process has no order functions. It validates the current token, rotates only
when required, writes a new Secret Manager version, validates the new token, and
emits non-secret proof JSON for Cloud Logging.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

PROJECT = (
    os.getenv("GOOGLE_CLOUD_PROJECT")
    or os.getenv("GCP_PROJECT")
    or os.getenv("SYSTEM3_FIRESTORE_PROJECT")
    or "system3-openalgo-safe"
)
SECRET_ID = os.getenv("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token")
MIN_HOURS = float(os.getenv("DHAN_ROTATE_WHEN_HOURS_LEFT", "6"))


def _latest_version_proof() -> dict:
    try:
        from google.cloud import secretmanager

        client = secretmanager.SecretManagerServiceClient()
        parent = f"projects/{PROJECT}/secrets/{SECRET_ID}"
        versions = list(
            client.list_secret_versions(
                request={"parent": parent, "filter": "state:ENABLED"}
            )
        )
        if not versions:
            return {"secret_id": SECRET_ID, "version": None, "created_at_utc": None}
        latest = max(versions, key=lambda item: int(item.name.rsplit("/", 1)[-1]))
        created = getattr(latest, "create_time", None)
        if hasattr(created, "ToDatetime"):
            created = created.ToDatetime()
        if isinstance(created, datetime):
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            created = created.astimezone(timezone.utc).isoformat()
        return {
            "secret_id": SECRET_ID,
            "version": latest.name.rsplit("/", 1)[-1],
            "created_at_utc": str(created) if created else None,
        }
    except Exception as exc:
        return {
            "secret_id": SECRET_ID,
            "version": None,
            "created_at_utc": None,
            "metadata_error_type": type(exc).__name__,
        }


def _safe_verify(raw: dict) -> dict:
    return {
        "valid": bool(raw.get("valid")),
        "reason": str(raw.get("reason") or "")[:160] or None,
        "expires_at": raw.get("expires_at"),
        "hours_remaining": raw.get("hours_remaining"),
        "client_id_suffix_present": bool(raw.get("client_id")),
    }


def main() -> int:
    os.environ["CLOUD_MODE"] = "1"
    os.environ["DHAN_PERSIST_TOKEN_TO_SM"] = "1"
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
    os.environ["LIVE_TRADING_ENABLED"] = "0"
    os.environ["AUTO_EXECUTE_TRADES"] = "0"

    from core.brokers.dhan.token_manager import refresh_token, verify_token

    started = datetime.now(timezone.utc)
    before = _safe_verify(verify_token())
    before_secret = _latest_version_proof()
    remaining = before.get("hours_remaining")

    should_rotate = not before["valid"]
    if remaining is not None:
        try:
            should_rotate = should_rotate or float(remaining) <= MIN_HOURS
        except (TypeError, ValueError):
            should_rotate = True

    if not should_rotate:
        proof = {
            "status": "SKIPPED_TOKEN_HEALTHY",
            "generated_at_utc": started.isoformat(),
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
        print(json.dumps(proof, sort_keys=True))
        return 0

    result = refresh_token(force_generate=True)
    after = _safe_verify(verify_token())
    after_secret = _latest_version_proof()
    before_version = before_secret.get("version")
    after_version = after_secret.get("version")
    version_advanced = bool(
        before_version and after_version and before_version != after_version
    )
    persisted = bool(after_version) and (
        version_advanced or before_version is None
    )
    success = bool(result.get("success") and after["valid"] and persisted)

    proof = {
        "status": "ROTATED_AND_VERIFIED" if success else "ROTATION_FAILED",
        "generated_at_utc": started.isoformat(),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "strategy": result.get("strategy"),
        "message": str(result.get("message") or "")[:200],
        "before": before,
        "after": after,
        "secret_before": before_secret,
        "secret_after": after_secret,
        "secret_version_advanced": version_advanced,
        "secret_persisted": persisted,
        "rotation_threshold_hours": MIN_HOURS,
        "live_trading_enabled": False,
        "order_endpoints_called": False,
        "raw_token_exposed": False,
    }
    print(json.dumps(proof, sort_keys=True))
    return 0 if success else 2


if __name__ == "__main__":
    sys.exit(main())
