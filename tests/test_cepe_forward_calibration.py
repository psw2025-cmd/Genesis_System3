from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest

from scripts.cepe_forward_calibration import report


IST = timezone(timedelta(hours=5, minutes=30))
AS_OF = datetime(2026, 10, 1, 12, tzinfo=IST)
HASH_A = "a" * 64
HASH_B = "b" * 64


def observation(
    prediction_id="p1", probability=.8, multiple=1.2, *, day="2026-09-30"
):
    return {
        "prediction_id": prediction_id,
        "strategy_id": "directional-regime",
        "strategy_version": "v1",
        "event_type": "positive_next_open",
        "probability": probability,
        "symbol": "ABC",
        "expiry": "2026-10-29",
        "strike": 100,
        "type": "CE",
        "previous_day": "2026-09-29",
        "following_day": day,
        "issued_at": "2026-09-29T16:00:00+05:30",
        "published_at": "2026-09-29T16:01:00+05:30",
        "cutoff_at": "2026-09-29T18:00:00+05:30",
        "following_open_at": f"{day}T09:15:00+05:30",
        "prediction_source_sha256": HASH_A,
        "publication_receipt_sha256": "c" * 64,
        "session_calendar_sha256": "d" * 64,
        "outcome_multiple": multiple,
        "outcome_observed_at": f"{day}T09:16:00+05:30",
        "outcome_source_sha256": HASH_B,
        "forward_issued": True,
        "retrospective": False,
        "source_qualified": True,
        "official_session_verified": True,
        "publication_verified": True,
        "opening_fill_proven": False,
        "orders_allowed": False,
    }


def test_empty_or_pending_records_never_claim_calibration():
    assert report([], as_of=AS_OF)["status"] == "NOT_PROVEN"
    pending = observation()
    pending["following_day"] = "2026-10-02"
    pending["following_open_at"] = "2026-10-02T09:15:00+05:30"
    pending["expiry"] = "2026-10-29"
    pending.pop("outcome_multiple")
    pending.pop("outcome_observed_at")
    pending.pop("outcome_source_sha256")
    result = report([pending], as_of=AS_OF)
    assert (result["pending_outcomes"], result["matured_outcomes"]) == (1, 0)
    assert result["metrics"] is None


def test_measured_fixture_calibration_arithmetic_and_hash_are_deterministic():
    rows = [
        observation("p1", .8, 1.2),
        observation("p2", .7, .8),
        observation("p3", .2, .7),
        observation("p4", .1, 1.1),
    ]
    result = report(rows, as_of=AS_OF)
    assert result["status"] == "MEASURED_BELOW_RESEARCH_GATE"
    assert result["metrics"]["directional_accuracy"] == .5
    assert result["metrics"]["brier_score"] == pytest.approx(.345)
    assert len(result["observation_set_sha256"]) == 64
    assert result["real_money_ready"] is False
    assert result["orders_allowed"] is False


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("retrospective", True, "Retrospective"),
        ("publication_verified", False, "publication"),
        ("source_qualified", False, "source"),
        ("official_session_verified", False, "Official session"),
        ("opening_fill_proven", True, "fill"),
        ("orders_allowed", True, "Orders"),
        ("probability", 1.0, "Probability"),
    ],
)
def test_rejects_unproven_or_unsafe_forecast_rows(field, value, match):
    row = observation()
    row[field] = value
    with pytest.raises(ValueError, match=match):
        report([row], as_of=AS_OF)


def test_rejects_hindsight_partial_outcomes_and_duplicate_ids():
    row = observation()
    row["published_at"] = "2026-09-30T09:16:00+05:30"
    with pytest.raises(ValueError, match="published before"):
        report([row], as_of=AS_OF)
    row = observation()
    row.pop("outcome_source_sha256")
    with pytest.raises(ValueError, match="Partial outcome"):
        report([row], as_of=AS_OF)
    with pytest.raises(ValueError, match="Duplicate prediction_id"):
        report([observation(), observation()], as_of=AS_OF)
    row = observation()
    row["outcome_source_sha256"] = HASH_A
    with pytest.raises(ValueError, match="later source bytes"):
        report([row], as_of=AS_OF)


def test_project_sample_and_accuracy_gates_use_forward_rows_only():
    rows = []
    start = datetime(2026, 1, 1, 9, 15, tzinfo=IST)
    for index in range(100):
        following = (start + timedelta(days=index)).date()
        previous = following - timedelta(days=1)
        row = observation(f"p{index}", .8, 1.1, day=following.isoformat())
        row["previous_day"] = previous.isoformat()
        row["issued_at"] = f"{previous.isoformat()}T16:00:00+05:30"
        row["published_at"] = f"{previous.isoformat()}T16:01:00+05:30"
        row["cutoff_at"] = f"{previous.isoformat()}T18:00:00+05:30"
        rows.append(row)
    result = report(rows, as_of=datetime(2026, 5, 1, tzinfo=IST))
    assert result["status"] == "RESEARCH_CALIBRATION_GATE_PASS"
    assert all(result["research_gates"].values())
    assert result["metrics"]["directional_accuracy"] == 1
    assert result["real_money_ready"] is False


def test_registry_matches_code_governance_and_has_no_performance_claim():
    registry = json.loads(
        Path("research/experiments/cepe_forward_calibration_v1.json").read_text()
    )
    assert registry["experiment_id"] == "CEPE-NEXT-008"
    assert registry["forward_predictions"] == 0
    assert registry["forward_outcomes"] == 0
    assert registry["orders_allowed"] is False
