"""Bind regular-session CE/PE outcomes to a complete, dated session calendar.

A supplied calendar is a sourced declaration, not independent authentication.
Without one only consecutive calendar dates establish that no date was skipped.
Missing bhavcopies and weekday heuristics never prove exchange closure.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
import json
import re
from typing import Any
from urllib.parse import urlsplit

IST = timezone(timedelta(hours=5, minutes=30))


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate calendar key")
        result[key] = value
    return result


def _aware(value: str) -> datetime:
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Calendar availability must include timezone")
    return value


def session_scope(previous: date, following: date, calendar: bytes | None = None,
                  *, known_by: datetime | None = None) -> dict[str, Any]:
    """Validate complete interval coverage; never infer closure from missing files."""
    if following <= previous:
        raise ValueError("Following session must be later than previous session")
    status = "NOT_PROVEN"
    result = {
        "session_alignment_status": status,
        "session_calendar_sha256": None,
        "calendar_source_status": "NOT_PROVEN",
        "following_open_at": None,
        "opening_time_basis": "NOT_PROVEN",
    }
    if calendar is None:
        if (following - previous).days == 1:
            result.update(
                session_alignment_status="CONSECUTIVE_DATED_OBSERVATIONS",
                following_open_at=datetime.combine(following, time(9, 15), tzinfo=IST).isoformat(),
                opening_time_basis="REGULAR_SESSION_ASSUMPTION",
            )
        return result
    try:
        data = json.loads(calendar.decode("utf-8"), object_pairs_hook=_unique)
        if data["schema"] != "nse-session-calendar-v1" or data["segment"] != "FO":
            raise ValueError("Unsupported session calendar")
        start, end = date.fromisoformat(data["start"]), date.fromisoformat(data["end"])
        if not start <= previous < following <= end or (end - start).days > 3660:
            raise ValueError("Calendar does not cover requested sessions")
        available = _aware(data["available_at"])
        if known_by is not None:
            if known_by.tzinfo is None or known_by.utcoffset() is None or available > known_by:
                raise ValueError("Calendar was not available at prediction issue time")
        source = urlsplit(data["source_url"])
        if (source.scheme != "https" or source.hostname not in
                {"nseindia.com", "www.nseindia.com", "nsearchives.nseindia.com"}
                or source.username or source.password or source.fragment or source.port not in (None, 443)):
            raise ValueError("Calendar requires an official NSE source URL")
        if not re.fullmatch(r"[0-9a-f]{64}", data["source_sha256"]):
            raise ValueError("Calendar requires raw source SHA-256")
        days = data["days"]
        expected = {(start + timedelta(days=i)).isoformat()
                    for i in range((end - start).days + 1)}
        if not isinstance(days, dict) or set(days) != expected:
            raise ValueError("Calendar must explicitly cover every date")
        for day, opening in days.items():
            if opening is not None and _aware(opening).astimezone(IST).date().isoformat() != day:
                raise ValueError("Session opening timestamp has wrong date")
        if days[previous.isoformat()] is None or days[following.isoformat()] is None:
            raise ValueError("Requested observation falls on a declared closed date")
        if any(days[(previous + timedelta(days=i)).isoformat()] is not None
               for i in range(1, (following - previous).days)):
            raise ValueError("Missing intervening trading session")
        result.update(
            session_alignment_status="DECLARED_CALENDAR_ALIGNED",
            session_calendar_sha256=sha256(calendar).hexdigest(),
            calendar_source_status="DECLARED_SOURCE_NOT_INDEPENDENTLY_VERIFIED",
            following_open_at=days[following.isoformat()],
            opening_time_basis="DECLARED_SESSION_CALENDAR",
        )
        return result
    except (KeyError, TypeError, AttributeError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid session calendar schema") from exc


def require_session_alignment(scope: dict[str, Any]) -> None:
    if scope["session_alignment_status"] == "NOT_PROVEN":
        raise ValueError("Session gap requires a complete sourced calendar; next opening is NOT_PROVEN")
