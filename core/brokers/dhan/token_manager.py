"""Dhan token compatibility facade — permanently non-mutating.

The only process allowed to mint or persist a Dhan access token is
`scripts/gcp_dhan_token_rotation_job.py`, running as the canonical Google Cloud
Run Job.  This module intentionally keeps a few historical function names so
older imports fail closed instead of recreating a second token authority.

Safety contract:
- never generate, renew, consume, write, or persist a Dhan token;
- never read PIN/TOTP/app-secret credentials;
- never print or return a raw access token;
- status is derived only from the already-supplied access token JWT.
"""
from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone


def _current_token() -> str:
    """Read the already-provided token only; never mutate its source."""
    token = (os.getenv("DHAN_ACCESS_TOKEN") or "").strip().lstrip("\ufeff")
    if token:
        return token
    try:
        from core.utils.env_loader import get_dhan_credentials

        return str(get_dhan_credentials().get("access_token") or "").strip().lstrip("\ufeff")
    except Exception:
        return ""


def _expiry(token: str) -> datetime | None:
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        body = parts[1] + "=" * (-len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(body.encode("ascii")))
        exp = payload.get("exp")
        return datetime.fromtimestamp(float(exp), tz=timezone.utc) if exp else None
    except Exception:
        return None


def verify_token() -> dict:
    """Return secret-safe JWT expiry metadata; performs no login or mutation."""
    token = _current_token()
    if not token:
        return {
            "valid": False,
            "reason": "credentials_missing",
            "source": "legacy-status-only",
            "raw_token_exposed": False,
        }
    exp = _expiry(token)
    if exp is None:
        return {
            "valid": False,
            "reason": "jwt_expiry_unavailable",
            "source": "legacy-status-only",
            "raw_token_exposed": False,
        }
    now = datetime.now(timezone.utc)
    hours = (exp - now).total_seconds() / 3600.0
    return {
        "valid": hours > 0,
        "reason": "jwt_expiry_ok" if hours > 0 else "jwt_expired",
        "expires_at": exp.isoformat(),
        "hours_remaining": round(hours, 2),
        "source": "legacy-status-only",
        "raw_token_exposed": False,
    }


def get_token_status() -> dict:
    """Compatibility alias for historical status callers."""
    return verify_token()


def refresh_token(*args, **kwargs) -> dict:
    """Historical mutation API retained only as a fail-closed compatibility stub."""
    del args, kwargs
    return {
        "success": False,
        "strategy": "RETIRED",
        "message": "Legacy token mutation retired; canonical GCP Cloud Run rotation job is the only authority",
        "mutation_attempted": False,
        "raw_token_exposed": False,
    }


def consume_oauth_token(*args, **kwargs) -> dict:
    """Historical OAuth mutation API retained only as a fail-closed stub."""
    del args, kwargs
    return {
        "success": False,
        "strategy": "RETIRED",
        "message": "Legacy OAuth token consumption retired",
        "mutation_attempted": False,
        "raw_token_exposed": False,
    }


if __name__ == "__main__":
    print(json.dumps(verify_token(), sort_keys=True))
