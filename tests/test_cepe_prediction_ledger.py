"""End-to-end issue/settle tests use deterministic market fixtures, not real forecasts."""
from datetime import date, datetime, timedelta, timezone
import pytest

from scripts.cepe_prediction_ledger import issue, settle

IST = timezone(timedelta(hours=5, minutes=30))
BEFORE = (
    b"TckrSymb,XpryDt,OptnTp,StrkPric,OpnPric,ClsPric,TradDt,TtlTradgVol\n"
    b"ABC,2026-09-29,CE,100,8,10,2026-09-17,200\n"
    b"XYZ,2026-09-29,PE,200,8,10,2026-09-17,200\n"
)
AFTER = (
    b"TckrSymb,XpryDt,OptnTp,StrkPric,OpnPric,ClsPric,TradDt,TtlTradgVol\n"
    b"ABC,2026-09-29,CE,100,40,25,2026-09-18,200\n"
    b"XYZ,2026-09-29,PE,200,30,20,2026-09-18,200\n"
)
ISSUED = datetime(2026, 9, 17, 17, 0, tzinfo=IST)
CUTOFF = datetime(2026, 9, 17, 18, 0, tzinfo=IST)
PICK = [{"symbol": "ABC", "expiry": "2026-09-29", "strike": 100, "type": "CE"}]


def receipt():
    return issue(BEFORE, date(2026, 9, 17), date(2026, 9, 18),
                 PICK, CUTOFF, now=ISSUED, target_multiple=3)


def test_issue_then_settle_counts_advance_pick_and_missed_winner():
    recorded = receipt()
    result = settle(BEFORE, AFTER, recorded)
    assert (result["hits"], result["missed_winners"], result["false_picks"]) == (1, 1, 0)
    assert result["forward_proof_status"] == "LOCAL_RECEIPT_ONLY_NOT_PROVEN"
    assert result["verified_forecast_accuracy"] is None


def test_cannot_issue_winner_after_open_or_from_missing_contract():
    with pytest.raises(ValueError):
        issue(BEFORE, date(2026, 9, 17), date(2026, 9, 18),
              PICK, CUTOFF, now=datetime(2026, 9, 18, 10, tzinfo=IST))
    with pytest.raises(ValueError):
        issue(BEFORE, date(2026, 9, 17), date(2026, 9, 18),
              [{**PICK[0], "symbol": "MISSING"}], CUTOFF, now=ISSUED)


def test_source_or_receipt_tamper_rejected():
    recorded = receipt()
    with pytest.raises(ValueError, match="source bytes changed"):
        settle(BEFORE + b"\n", AFTER, recorded)
    recorded["record"]["predictions"] = []
    with pytest.raises(ValueError, match="Receipt hash mismatch"):
        settle(BEFORE, AFTER, recorded)


def test_publication_timestamp_is_only_supplied_not_independently_verified():
    result = settle(BEFORE, AFTER, receipt(),
                    publication_time=datetime(2026, 9, 17, 17, 30, tzinfo=IST))
    assert result["forward_proof_status"].endswith("UNVERIFIED")
    with pytest.raises(ValueError):
        settle(BEFORE, AFTER, receipt(),
               publication_time=datetime(2026, 9, 18, 10, tzinfo=IST))
