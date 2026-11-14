from datetime import datetime
from zoneinfo import ZoneInfo

from core.utils.nse_holidays import attach_market_calendar_evidence, market_calendar_evidence


IST = ZoneInfo("Asia/Kolkata")


def test_official_calendar_proves_saturday_closed_without_live_quote_claim():
    proof = market_calendar_evidence(datetime(2026, 11, 14, 10, 0, tzinfo=IST))
    assert proof["verified"] is True
    assert proof["exchange"] == "NSE"
    assert proof["is_open"] is False
    assert proof["session_status"] == "CLOSED"
    assert proof["reason"] == "WEEKEND_SATURDAY"
    assert proof["source_url"].startswith("https://nsearchives.nseindia.com/")
    assert len(proof["calendar_sha256"]) == 64


def test_regular_open_session_requires_date_and_time_in_session():
    proof = market_calendar_evidence(datetime(2026, 11, 16, 10, 0, tzinfo=IST))
    assert proof["verified"] is True
    assert proof["is_open"] is True
    assert proof["reason"] == "NSE_REGULAR_SESSION"


def test_special_session_without_confirmed_hours_is_unknown_not_closed():
    proof = market_calendar_evidence(datetime(2026, 11, 8, 18, 30, tzinfo=IST))
    assert proof["verified"] is False
    assert proof["is_open"] is None
    assert proof["reason"] == "SPECIAL_SESSION_TIMES_NOT_VERIFIED"


def test_missing_calendar_year_is_unknown_and_overrides_cached_open_flag():
    proof_time = datetime(2027, 1, 4, 10, 0, tzinfo=IST)
    state = attach_market_calendar_evidence({"market": {"is_open": True, "calendar_verified": True}}, proof_time)
    assert state["market"]["is_open"] is None
    assert state["market"]["calendar_verified"] is False
    assert state["market"]["calendar_proof"]["reason"] == "NSE_CALENDAR_NOT_LOADED"

