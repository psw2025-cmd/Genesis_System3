"""Calendar and issue/settle regression fixtures; no real-market success claim."""
from datetime import date, datetime, timedelta
from hashlib import sha256
import json

import pytest

from scripts.cepe_forward_scorecard import score
from scripts.cepe_next_open_proof import compare
from scripts.cepe_prediction_ledger import issue, settle
from scripts.cepe_session_scope import IST, session_scope
from scripts.cepe_walkforward_baseline import run

HEADER = "TckrSymb,XpryDt,OptnTp,StrkPric,OpnPric,ClsPric,TradDt,TtlTradgVol\n"


def snapshot(day, opening=8, close=10):
    return (HEADER + f"ABC,2026-09-29,CE,100,{opening},{close},{day},200\n").encode()


def calendar(start="2026-09-18", end="2026-09-21", *, closed=("2026-09-19", "2026-09-20")):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    days = {(first + timedelta(days=i)).isoformat(): None
            for i in range((last - first).days + 1)}
    for day in days:
        if day not in closed:
            days[day] = day + "T09:15:00+05:30"
    return dict(schema="nse-session-calendar-v1", segment="FO", start=start, end=end,
                available_at="2026-09-01T12:00:00+05:30", days=days,
                source_url="https://nsearchives.nseindia.com/content/circulars/fixture.pdf",
                source_sha256="a" * 64)


def packed(data):
    return json.dumps(data).encode()


def test_missing_weekday_is_not_next_open_and_cannot_enter_scorecard():
    previous, following = date(2026, 9, 21), date(2026, 9, 23)
    result = compare(snapshot(previous), snapshot(following, opening=40), previous, following)
    assert result["highest_multiple"] == 4
    assert result["status"] == "HISTORICAL_INTERVAL_ONLY"
    assert result["session_alignment_status"] == "NOT_PROVEN"
    assert result["matches"][0]["next_open"] is None
    assert result["matches"][0]["observed_open"] == 40
    with pytest.raises(ValueError, match="Session gap"):
        score([], result, target_multiple=3, issued_cutoff=datetime(2026, 9, 21, 18, tzinfo=IST))
    with pytest.raises(ValueError, match="Session gap"):
        run([(previous, snapshot(previous)), (following, snapshot(following))])


def test_declared_open_intervening_date_is_rejected():
    with pytest.raises(ValueError, match="intervening trading session"):
        session_scope(date(2026, 9, 21), date(2026, 9, 23),
                      packed(calendar("2026-09-21", "2026-09-23", closed=())))


def test_weekend_requires_calendar_instead_of_weekday_assumption():
    assert session_scope(date(2026, 9, 18), date(2026, 9, 21))["session_alignment_status"] == "NOT_PROVEN"
    value = calendar()
    scope = session_scope(date(2026, 9, 18), date(2026, 9, 21), packed(value))
    assert scope["session_calendar_sha256"] == sha256(packed(value)).hexdigest()
    assert scope["calendar_source_status"] == "DECLARED_SOURCE_NOT_INDEPENDENTLY_VERIFIED"
    value["days"]["2026-09-19"] = "2026-09-19T11:00:00+05:30"
    with pytest.raises(ValueError, match="intervening trading session"):
        session_scope(date(2026, 9, 18), date(2026, 9, 21), packed(value))


@pytest.mark.parametrize("change", [
    lambda c: c["days"].pop("2026-09-20"),
    lambda c: c.update(segment="CM"),
    lambda c: c.update(source_sha256="missing"),
    lambda c: c.update(source_url="https://nseindia.com.example.org/calendar"),
    lambda c: c.update(available_at="2026-09-01T12:00:00"),
    lambda c: c["days"].update({"2026-09-18": None}),
    lambda c: c["days"].update({"2026-09-21": "2026-09-22T09:15:00+05:30"}),
])
def test_incomplete_or_invalid_calendar_fails_closed(change):
    value = calendar()
    change(value)
    with pytest.raises(ValueError):
        session_scope(date(2026, 9, 18), date(2026, 9, 21), packed(value))


def test_calendar_duplicate_keys_fail_closed():
    raw = packed(calendar()).replace(b'"segment": "FO"', b'"segment": "CM", "segment": "FO"')
    with pytest.raises(ValueError, match="Duplicate calendar key"):
        session_scope(date(2026, 9, 18), date(2026, 9, 21), raw)


def test_advance_receipt_binds_calendar_and_settles_only_same_horizon():
    previous, following = date(2026, 9, 18), date(2026, 9, 21)
    before, after = snapshot(previous), snapshot(following, opening=40)
    pick = [{"symbol": "ABC", "expiry": "2026-09-29", "strike": 100, "type": "CE"}]
    issued, cutoff = datetime(2026, 9, 18, 17, tzinfo=IST), datetime(2026, 9, 18, 18, tzinfo=IST)
    with pytest.raises(ValueError, match="Session gap"):
        issue(before, previous, following, pick, cutoff, now=issued)
    declaration = packed(calendar())
    receipt = issue(before, previous, following, pick, cutoff, now=issued, session_calendar=declaration)
    assert receipt["record"]["session_calendar_sha256"] == sha256(declaration).hexdigest()
    result = settle(before, after, receipt)
    assert result["hits"] == 1 and result["verified_forecast_accuracy"] is None
    assert result["orders_allowed"] is False
    receipt["record"]["session_calendar_utf8"] += " "
    with pytest.raises(ValueError, match="Receipt hash mismatch"):
        settle(before, after, receipt)


def test_post_issue_calendar_cannot_be_backfilled():
    value = calendar()
    value["available_at"] = "2026-09-19T10:00:00+05:30"
    with pytest.raises(ValueError, match="not available"):
        issue(snapshot("2026-09-18"), date(2026, 9, 18), date(2026, 9, 21), [],
              datetime(2026, 9, 18, 18, tzinfo=IST),
              now=datetime(2026, 9, 18, 17, tzinfo=IST), session_calendar=packed(value))


def test_special_session_opening_time_controls_issue_and_score_cutoffs():
    value = calendar()
    value["days"]["2026-09-21"] = "2026-09-21T18:00:00+05:30"
    declaration = packed(value)
    previous, following = date(2026, 9, 18), date(2026, 9, 21)
    issued = datetime(2026, 9, 21, 16, tzinfo=IST)
    cutoff = datetime(2026, 9, 21, 17, tzinfo=IST)
    receipt = issue(snapshot(previous), previous, following, [], cutoff,
                    now=issued, session_calendar=declaration)
    result = settle(snapshot(previous), snapshot(following), receipt)
    assert result["following_open_at"] == value["days"]["2026-09-21"]
    assert result["status"] == "NOT_PROVEN"  # no picks, never a success claim
    with pytest.raises(ValueError, match="precede next opening"):
        issue(snapshot(previous), previous, following, [],
              datetime(2026, 9, 21, 18, tzinfo=IST),
              now=issued, session_calendar=declaration)


def test_expired_candidate_and_zero_reference_price_are_not_scoreable():
    raw = snapshot("2026-09-18").replace(b"2026-09-29", b"2026-09-18")
    pick = [{"symbol": "ABC", "expiry": "2026-09-18", "strike": 100, "type": "CE"}]
    with pytest.raises(ValueError, match="expires"):
        issue(raw, date(2026, 9, 18), date(2026, 9, 21), pick,
              datetime(2026, 9, 18, 18, tzinfo=IST), now=datetime(2026, 9, 18, 17, tzinfo=IST),
              session_calendar=packed(calendar()))
    result = compare(snapshot("2026-09-17", close=0), snapshot("2026-09-18"),
                     date(2026, 9, 17), date(2026, 9, 18), min_previous_close=0)
    assert result["matched_contracts"] == 0


@pytest.mark.parametrize("multiple", [float("nan"), float("inf"), 0, -1])
def test_nonfinite_or_nonpositive_scorecard_outcomes_rejected(multiple):
    result = compare(snapshot("2026-09-17"), snapshot("2026-09-18"), date(2026, 9, 17), date(2026, 9, 18))
    result["matches"][0]["multiple"] = multiple
    with pytest.raises(ValueError, match="actual multiple"):
        score([], result, target_multiple=3, issued_cutoff=datetime(2026, 9, 17, 18, tzinfo=IST))
