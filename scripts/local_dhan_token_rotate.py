#!/usr/bin/env python3
"""Local (laptop) Dhan access-token rotation — Windows-vault-native twin of
scripts/gcp_dhan_token_rotation_job.py.

Replaces the GCP Cloud Run Job's Secret Manager persistence with the local
Windows-DPAPI vault (core.security.windows_secret_vault). The Dhan
login/TOTP/JWT logic is intentionally duplicated (not imported) from the GCP
script so this file never pulls in google-cloud-secret-manager as a runtime
dependency and so the GCP script can keep working unmodified until it is
safe to delete per the do-not-delete-yet checklist.

PAPER/ANALYZER only. Never calls order endpoints. Never sets any LIVE flag.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["LIVE_TRADING_ENABLED"] = "0"
os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
os.environ["AUTO_EXECUTE_TRADES"] = "0"
os.environ["ANALYZE_MODE"] = "1"

MIN_HOURS = float(os.getenv("DHAN_ROTATE_WHEN_HOURS_LEFT", "2"))
AUTHORITY = "local-laptop-scheduler"


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


def _generate_token(client_id: str, pin: str, totp_secret: str) -> str:
    import pyotp
    from dhanhq import DhanLogin

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


def _profile_valid(client_id: str, token: str) -> bool:
    from dhanhq import DhanLogin

    if not client_id or not token:
        return False
    try:
        profile = DhanLogin(client_id).user_profile(token)
        return bool(profile) and not bool((profile or {}).get("errorCode"))
    except Exception:
        return False


def run_once() -> dict[str, Any]:
    """Rotate the local Dhan token if it is missing or near expiry. Returns a
    non-secret status dict for logging/state; never includes token values."""
    from core.security.windows_secret_vault import get_secret, save_secret

    client_id = get_secret("DHAN_CLIENT_ID") or os.getenv("DHAN_CLIENT_ID", "").strip()
    pin = get_secret("DHAN_PIN") or os.getenv("DHAN_PIN", "").strip()
    totp_secret = get_secret("DHAN_TOTP_SECRET") or os.getenv("DHAN_TOTP_SECRET", "").strip()
    current_token = get_secret("DHAN_ACCESS_TOKEN") or ""

    hours_left = _hours_remaining(current_token) if current_token else None
    needs_rotation = current_token == "" or hours_left is None or hours_left < MIN_HOURS

    result: dict[str, Any] = {
        "authority": AUTHORITY,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "had_existing_token": bool(current_token),
        "hours_remaining_before": round(hours_left, 2) if hours_left is not None else None,
        "rotated": False,
        "status": "no_rotation_needed",
    }

    if not needs_rotation:
        return result

    if not (client_id and pin and totp_secret):
        result["status"] = "blocked_missing_credentials"
        return result

    try:
        new_token = _generate_token(client_id, pin, totp_secret)
    except Exception as exc:
        result["status"] = "generation_failed"
        result["error_type"] = type(exc).__name__
        return result

    if not _profile_valid(client_id, new_token):
        result["status"] = "new_token_failed_validation_not_persisted"
        return result

    if not save_secret("DHAN_ACCESS_TOKEN", new_token):
        result["status"] = "generated_and_validated_but_vault_write_failed"
        return result

    result["rotated"] = True
    result["hours_remaining_after"] = round(_hours_remaining(new_token) or 0, 2)
    result["status"] = "rotated_ok"
    return result


if __name__ == "__main__":
    outcome = run_once()
    print(json.dumps(outcome, indent=2))
    sys.exit(0 if outcome["status"] not in ("generation_failed", "generated_and_validated_but_vault_write_failed") else 1)
