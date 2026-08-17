"""Process-local, non-secret latch for the first Dhan auth rejection.

The purpose is forensic ordering: preserve the first upstream rejection observed by
this runtime instance before Secret Manager reload/recovery activity can obscure
what happened first. No token value, client id, request payload, or order data is
stored or returned.
"""
from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timezone
from typing import Any

_LOCK = threading.RLock()
_STATE: dict[str, Any] = {
    "first_rejected_at_epoch": 0.0,
    "last_rejected_at_epoch": 0.0,
    "rejection_count": 0,
    "secret_version": None,
    "auth_classification": None,
    "http_status": None,
    "upstream_code": None,
}


def _utc(epoch: float) -> str | None:
    if not epoch:
        return None
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()


def record_auth_rejection(
    *,
    secret_version: str | None,
    auth_classification: str,
    http_status: int | None = None,
    upstream_code: int | None = None,
) -> dict[str, Any]:
    """Latch first rejection and update only safe ordering metadata."""
    now = time.time()
    with _LOCK:
        if not _STATE["first_rejected_at_epoch"]:
            _STATE["first_rejected_at_epoch"] = now
            _STATE["secret_version"] = secret_version or None
            _STATE["auth_classification"] = auth_classification
            _STATE["http_status"] = http_status
            _STATE["upstream_code"] = upstream_code
        _STATE["last_rejected_at_epoch"] = now
        _STATE["rejection_count"] = int(_STATE["rejection_count"] or 0) + 1
        return snapshot()


def snapshot() -> dict[str, Any]:
    with _LOCK:
        first = float(_STATE["first_rejected_at_epoch"] or 0.0)
        last = float(_STATE["last_rejected_at_epoch"] or 0.0)
        return {
            "first_rejected_at_utc": _utc(first),
            "last_rejected_at_utc": _utc(last),
            "rejection_count": int(_STATE["rejection_count"] or 0),
            "secret_version": _STATE["secret_version"],
            "auth_classification": _STATE["auth_classification"],
            "http_status": _STATE["http_status"],
            "upstream_code": _STATE["upstream_code"],
            "runtime_instance": os.getenv("K_REVISION") or os.getenv("HOSTNAME") or None,
            "raw_token_exposed": False,
            "client_id_exposed": False,
        }


def _reset_for_tests() -> None:
    with _LOCK:
        _STATE.update(
            first_rejected_at_epoch=0.0,
            last_rejected_at_epoch=0.0,
            rejection_count=0,
            secret_version=None,
            auth_classification=None,
            http_status=None,
            upstream_code=None,
        )
