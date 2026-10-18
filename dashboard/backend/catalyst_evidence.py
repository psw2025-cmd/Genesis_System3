"""Fail-closed point-in-time catalyst evidence for equity research; no orders."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from urllib.parse import urlparse


_OFFICIAL_HOSTS = {"nseindia.com", "www.nseindia.com", "bseindia.com",
                   "www.bseindia.com", "beta.bseindia.com"}


def _time(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return result.astimezone(timezone.utc)


def validate_catalyst(event: dict, issued_at: str, raw_source: bytes) -> dict:
    """Only mark an official filing usable when observed by issue time.

    Publication time alone is insufficient: a later retrieval cannot prove
    the system saw the filing earlier. This validates evidence, not causation.
    """
    try:
        issued = _time(issued_at)
        published = _time(event["published_at"])
        observed = _time(event["first_observed_at"])
        url = urlparse(event["source_url"])
        if url.scheme != "https" or url.hostname not in _OFFICIAL_HOSTS:
            raise ValueError("SOURCE_NOT_OFFICIAL")
        if not isinstance(raw_source, bytes) or not raw_source:
            raise ValueError("SOURCE_BYTES_REQUIRED")
        if sha256(raw_source).hexdigest() != event["source_sha256"]:
            raise ValueError("SOURCE_HASH_MISMATCH")
        symbol = str(event["symbol"]).strip().upper()
        if not symbol or not str(event["event_id"]).strip():
            raise ValueError("IDENTITY_REQUIRED")
        if not published <= observed <= issued:
            raise ValueError("CATALYST_NOT_KNOWN_AT_ISSUE")
    except (KeyError, AttributeError, TypeError, ValueError) as exc:
        return {"status": "NOT_PROVEN", "reason": str(exc)}
    return {"status": "KNOWN_AT_ISSUE", "symbol": symbol,
            "event_id": event["event_id"], "published_at": published.isoformat(),
            "first_observed_at": observed.isoformat(), "issued_at": issued.isoformat(),
            "source_url": event["source_url"],
            "source_sha256": event["source_sha256"],
            "causal_effect_proven": False, "order_placement_allowed": False}
