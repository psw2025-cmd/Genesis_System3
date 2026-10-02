"""Behavioral checks for forward picks versus retrospective top movers."""
from datetime import datetime, timezone, timedelta
import pytest

from scripts.cepe_forward_scorecard import score

IST = timezone(timedelta(hours=5, minutes=30))
CUTOFF = datetime(2026, 9, 17, 18, 0, tzinfo=IST)
HASH = "a" * 64
BASE = {
    "previous_day": "2026-09-17",
    "following_day": "2026-09-18",
    "previous_sha256": HASH,
    "following_sha256": "b" * 64,
    "distribution_scope": "FULL_MATCHED_CONTRACT_SET_UNCAPPED",
    "matches": [
        {"symbol": "ABC", "expiry": "2026-09-29", "strike": "100.0000", "type": "CE", "multiple": 4},
        {"symbol": "XYZ", "expiry": "2026-09-29", "strike": "200.0000", "type": "PE", "multiple": 3},
        {"symbol": "DEF", "expiry": "2026-09-29", "strike": "300.0000", "type": "CE", "multiple": 1.1},
    ],
}


def pick(symbol, strike, kind="CE", issued="2026-09-17T17:00:00+05:30"):
    return {"symbol": symbol, "expiry": "2026-09-29", "strike": strike,
            "type": kind, "issued_at": issued, "source_sha256": HASH}


def test_reports_wrong_picks_and_missed_winners():
    result = score([pick("ABC", 100), pick("DEF", 300)], BASE,
                   target_multiple=3, issued_cutoff=CUTOFF)
    assert (result["hits"], result["false_picks"], result["missed_winners"]) == (1, 1, 1)
    assert (result["precision"], result["recall"], result["baseline_winner_rate"]) == (.5, .5, 2 / 3)
    assert result["opening_fill_proven"] is False


def test_no_prediction_does_not_claim_accuracy():
    result = score([], BASE, target_multiple=3, issued_cutoff=CUTOFF)
    assert result["status"] == "NOT_PROVEN"
    assert result["precision"] is None
    assert result["missed_winners"] == 2


@pytest.mark.parametrize("issued,source", [
    ("2026-09-18T10:00:00+05:30", HASH),
    ("2026-09-17T17:00:00+05:30", "wrong"),
])
def test_rejects_hindsight_and_unbound_sources(issued, source):
    row = pick("ABC", 100, issued=issued)
    row["source_sha256"] = source
    with pytest.raises(ValueError):
        score([row], BASE, target_multiple=3, issued_cutoff=CUTOFF)


def test_rejects_cutoff_after_market_open():
    with pytest.raises(ValueError):
        score([], BASE, target_multiple=3,
              issued_cutoff=datetime(2026, 9, 18, 9, 16, tzinfo=IST))
