"""
NSE/BSE Equity Trading Holiday Calendar
==========================================
Source of truth for "is today an NSE/BSE trading holiday" checks used by
the job scheduler (core/engine/system3_phase82_job_scheduler.py) and any
other code that needs to distinguish "market closed because weekend/
holiday" from "market closed because outside trading hours".

2026 dates are reconciled to NSE's official F&O holiday circular
(https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf).
Equity/derivatives segment only (excludes MCX-only and settlement-only
holidays). The special Sunday Nov-08 Muhurat date is handled separately;
unknown session hours remain UNKNOWN rather than being guessed.

IMPORTANT: this list must be updated annually. NSE publishes the next
year's calendar in December via circular. There is no reliable free API
for this — Render's worker has outbound internet but NSE's holiday page
is not a stable scrape target for production use, so this is a
maintained static list with provenance per entry, re-verified at need.

If a job runs and the year is not in HOLIDAYS_BY_YEAR, is_trading_holiday
returns False (fail-open to "not a holiday") rather than blocking all
jobs — but logs a warning so the gap is visible, consistent with how
core/engine/system3_phase173_holiday_detection.py's old stub silently
returned False without ever raising a flag.
"""

import logging
from datetime import date

logger = logging.getLogger("nse_holidays")

# NSE equity-derivatives calendar provenance. No NSE website scraping is used.
NSE_FO_HOLIDAY_CIRCULAR_URL = "https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf"
NSE_MARKET_TIMINGS_URL = "https://www.nseindia.com/static/market-data/market-timings"
NSE_HOLIDAY_CALENDAR_URL = "https://www.nseindia.com/resources/exchange-communication-holidays"
NSE_SPECIAL_SESSION_DATES = {
    2026: {date(2026, 11, 8): "Diwali Laxmi Pujan Muhurat Trading"},
}

# NSE F&O holiday circular ref. 172/2025, published 2025-12-12;
# reconciled against the official NSE calendar on 2026-11-14.
HOLIDAYS_BY_YEAR = {
    2026: {
        date(2026, 1, 15): "Municipal Corporation Elections in Maharashtra",
        date(2026, 1, 26): "Republic Day",
        date(2026, 3, 3):  "Holi",
        date(2026, 3, 26): "Shri Ram Navami",
        date(2026, 3, 31): "Shri Mahavir Jayanti",
        date(2026, 4, 3):  "Good Friday",
        date(2026, 4, 14): "Dr. Baba Saheb Ambedkar Jayanti",
        date(2026, 5, 1):  "Maharashtra Day",
        date(2026, 5, 28): "Bakri Eid",
        date(2026, 6, 26): "Moharram",
        date(2026, 9, 14): "Ganesh Chaturthi",
        date(2026, 10, 2): "Mahatma Gandhi Jayanti",
        date(2026, 10, 20): "Dussehra",
        date(2026, 11, 10): "Diwali-Balipratipada",
        date(2026, 11, 24): "Prakash Gurpurb Sri Guru Nanak Dev",
        date(2026, 12, 25): "Christmas",
    },
}


def is_trading_holiday(d: date) -> tuple:
    """
    Returns (is_holiday: bool, reason: str|None).
    Checks ONLY the equity/derivatives holiday list — weekend detection
    is the caller's responsibility (most callers already check
    weekday() < 5 separately, e.g. job scheduler's weekdays_only flag).
    """
    year_map = HOLIDAYS_BY_YEAR.get(d.year)
    if year_map is None:
        logger.warning(
            f"nse_holidays: no holiday calendar loaded for year {d.year} — "
            f"treating as non-holiday by default. Update HOLIDAYS_BY_YEAR "
            f"in core/utils/nse_holidays.py with next year's NSE circular."
        )
        return False, None
    name = year_map.get(d)
    if name:
        return True, name
    return False, None


def is_trading_day(d: date) -> tuple:
    """
    Combined check: weekday AND not a holiday. Returns (is_trading_day, reason).
    """
    if d.weekday() >= 5:
        return False, f"Weekend ({d.strftime('%A')})"
    is_hol, hol_name = is_trading_holiday(d)
    if is_hol:
        return False, f"NSE/BSE holiday: {hol_name}"
    return True, "Trading day"


def market_calendar_evidence(now=None) -> dict:
    """Evaluate the official circular cache and NSE regular session hours.

    No network call or NSE website scrape is performed. Live market data must
    still independently satisfy the quote freshness gate.
    """
    import hashlib
    import json
    from datetime import datetime, time, timezone
    from zoneinfo import ZoneInfo

    ist = ZoneInfo("Asia/Kolkata")
    current = datetime.now(ist) if now is None else now
    current = current.replace(tzinfo=ist) if current.tzinfo is None else current.astimezone(ist)
    day = current.date()
    year_holidays = HOLIDAYS_BY_YEAR.get(day.year)
    special = NSE_SPECIAL_SESSION_DATES.get(day.year, {}).get(day)
    payload = {
        "evidence_type": "OFFICIAL_NSE_FO_CIRCULAR_CACHE",
        "year": day.year,
        "holidays": sorted((d.isoformat(), name) for d, name in (year_holidays or {}).items()),
        "special_sessions": sorted((d.isoformat(), name) for d, name in NSE_SPECIAL_SESSION_DATES.get(day.year, {}).items()),
        "source": NSE_FO_HOLIDAY_CIRCULAR_URL,
        "market_timings_source": NSE_MARKET_TIMINGS_URL,
        "regular_session_ist": {"opens": "09:15", "closes_exclusive": "15:30"},
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    verified = year_holidays is not None
    is_open = None
    reason = "NSE_CALENDAR_NOT_LOADED" if not verified else ""
    status = "UNKNOWN"

    if verified and special:
        verified, reason = False, "SPECIAL_SESSION_TIMES_NOT_VERIFIED"
    elif verified and day.weekday() >= 5:
        is_open, reason, status = False, f"WEEKEND_{day.strftime('%A').upper()}", "CLOSED"
    elif verified and day in year_holidays:
        is_open, reason, status = False, f"NSE_FO_HOLIDAY:{year_holidays[day]}", "CLOSED"
    elif verified and not (time(9, 15) <= current.time().replace(tzinfo=None) < time(15, 30)):
        is_open, reason, status = False, "OUTSIDE_NSE_REGULAR_SESSION", "CLOSED"
    elif verified:
        is_open, reason, status = True, "NSE_REGULAR_SESSION", "OPEN"

    evaluated_utc = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return {
        "schema_version": 1,
        "evidence_type": "OFFICIAL_NSE_FO_CIRCULAR_CACHE",
        "exchange": "NSE",
        "session_date": day.isoformat(),
        "verified": verified,
        "is_open": is_open,
        "session_status": status,
        "reason": reason,
        "source_url": NSE_FO_HOLIDAY_CIRCULAR_URL,
        "holiday_calendar_url": NSE_HOLIDAY_CALENDAR_URL,
        "market_hours_source_url": NSE_MARKET_TIMINGS_URL,
        "calendar_sha256": digest,
        "evaluated_at_utc": evaluated_utc,
        "evaluated_at_ist": current.isoformat(timespec="seconds"),
    }


def attach_market_calendar_evidence(state: dict, now=None) -> dict:
    """Attach calendar evidence and fail closed when the schedule is unknown."""
    if not isinstance(state, dict):
        return state
    result = dict(state)
    current_market = result.get("market")
    market = dict(current_market) if isinstance(current_market, dict) else {}
    proof = market_calendar_evidence(now)
    market["calendar_proof"] = proof
    market["calendar_verified"] = proof["verified"]
    market["calendar_status"] = proof["session_status"]
    market["calendar_reason"] = proof["reason"]
    market["is_open"] = proof["is_open"]
    result["market"] = market
    return result


if __name__ == "__main__":
    import sys
    today = date.today()
    ok, reason = is_trading_day(today)
    print(f"{today.isoformat()}: {'TRADING DAY' if ok else 'CLOSED'} — {reason}")
    sys.exit(0)
