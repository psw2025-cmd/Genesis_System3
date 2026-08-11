"""Dhan pre-flight status check — permanently non-mutating.

Token creation/renewal belongs exclusively to the canonical GCP Cloud Run
rotation job.  Preflight may inspect status but can never repair credentials.
"""
from __future__ import annotations


def token_health() -> dict:
    try:
        from core.brokers.dhan.token_manager import get_token_status

        status = dict(get_token_status())
        hours = status.get("hours_remaining")
        if status.get("valid"):
            if isinstance(hours, (int, float)) and hours < 0.5:
                level = "CRITICAL"
            elif isinstance(hours, (int, float)) and hours < 2:
                level = "WARNING"
            else:
                level = "OK"
        else:
            level = "EXPIRED_OR_INVALID"
        status["status"] = level
        status["mutation_attempted"] = False
        return status
    except Exception as exc:
        return {
            "valid": False,
            "status": "ERROR",
            "error_type": type(exc).__name__,
            "mutation_attempted": False,
        }


def ensure_valid_token(min_minutes: int = 30) -> bool:
    """Return current JWT validity only; never mint, renew, or persist a token."""
    del min_minutes
    return bool(token_health().get("valid"))
