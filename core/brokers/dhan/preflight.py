"""
Dhan Pre-Flight Token Check — Layer 3
======================================
Call ensure_valid_token() before ANY Dhan API operation.
It's instant if token is healthy (pure JWT decode, no network).
It refreshes only when needed (< 30 min left or expired).

Usage:
    from core.brokers.dhan.preflight import ensure_valid_token

    def my_trading_function():
        ensure_valid_token()   # add this one line
        ... rest of code ...
"""

import base64
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
logger = logging.getLogger("dhan_preflight")

REFRESH_IF_UNDER_MINUTES = 30   # refresh proactively if < 30 min left


def _hours_remaining(token: str) -> float:
    """Decode JWT expiry without network. Returns hours left (negative = expired)."""
    try:
        parts = token.split(".")
        pad = parts[1] + "=" * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(pad))
        exp = payload.get("exp", 0)
        return (datetime.fromtimestamp(exp) - datetime.now()).total_seconds() / 3600
    except Exception:
        return -999.0


def ensure_valid_token(min_minutes: int = REFRESH_IF_UNDER_MINUTES) -> bool:
    """
    Ensure the Dhan access token is valid before making any API call.

    - If token has > min_minutes remaining: no-op (instant return)
    - If token has < min_minutes remaining: refresh now
    - If token is expired: refresh now, raise RuntimeError if it fails

    Returns True if token is valid after this call.
    Raises RuntimeError only if refresh fails AND token is already expired.
    """
    try:
        # Load current token
        from dotenv import load_dotenv
        env_file = ROOT_DIR / ".secrets" / "dhan.env"
        load_dotenv(env_file, override=True)
        token = os.getenv("DHAN_ACCESS_TOKEN", "")

        hours = _hours_remaining(token)
        minutes_left = hours * 60

        if minutes_left > min_minutes:
            return True  # healthy, fast path

        # Need to refresh
        if hours < 0:
            logger.warning(f"Pre-flight: token EXPIRED {abs(hours):.1f}h ago — refreshing")
        else:
            logger.info(f"Pre-flight: token has {minutes_left:.0f}m left — proactive refresh")

        from core.brokers.dhan.token_manager import refresh_token
        result = refresh_token()

        if result.get("success"):
            logger.info(f"Pre-flight refresh OK via {result['strategy']}")
            return True

        if hours < 0:
            raise RuntimeError(
                f"Dhan token is EXPIRED and refresh failed: {result['message']}. "
                f"Run: python scripts/dhan_token_auto_refresh.py --oauth"
            )

        # Token still has some time — warn but don't raise
        logger.warning(f"Pre-flight refresh failed but token still valid: {result['message']}")
        return True

    except RuntimeError:
        raise
    except Exception as e:
        logger.error(f"Pre-flight check error: {e}")
        return False


def token_health() -> dict:
    """
    Returns a quick health dict — no network, pure JWT decode.
    Safe to call anywhere, frequently.
    """
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT_DIR / ".secrets" / "dhan.env", override=False)
        token = os.getenv("DHAN_ACCESS_TOKEN", "")
        hours = _hours_remaining(token)
        return {
            "valid": hours > 0,
            "hours_remaining": round(hours, 2),
            "status": (
                "EXPIRED" if hours < 0
                else "CRITICAL" if hours < 0.5
                else "WARNING" if hours < 2
                else "OK"
            ),
        }
    except Exception as e:
        return {"valid": False, "status": "ERROR", "error": str(e)}
