from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path

import pytest

from scripts.cepe_forward_calibration import report
from scripts.cepe_forward_decision import (
    CALENDAR_SHA256,
    NSE_FO_2026_WEEKDAY_HOLIDAYS,
    validate as validate_decision,
    validate_github_publication,
)


IST = timezone(timedelta(hours=5, minutes=30))
AS_OF = datetime(2026, 10, 1, 12, tzinfo=IST)
HASH_A = "a" * 64
HASH_B = "b" * 64


def observation(
    prediction_id="p1",
    probability=.8,
    multiple=1.2,
    *,
    day="2026-09-30",
    previous="2026-09-29",
    calendar_observed="2026-09-27T15:47:09Z",
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
        "previous_day": previous,
        "following_day": day,
        "issued_at": f"{previous}T16:00:00+05:30",
        "published_at": f"{previous}T16:01:00+05:30",
        "cutoff_at": f"{previous}T18:00:00+05:30",
        "following_open_at": f"{day}T09:15:00+05:30",
        "prediction_source_sha256": HASH_A,
        "publication_receipt_sha256": "c" * 64,
        "session_calendar_sha256": CALENDAR_SHA256,
        "session_calendar_evidence": {
            "segment": "FO",
            "source_url": (
                "https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf"
            ),
            "source_sha256": CALENDAR_SHA256,
            "source_first_observed_at": calendar_observed,
            "source_published_date": "2025-12-12",
            "source_circular": "NSE/FAOP/71777",
            "session_date": day,
            "session_status": "SCHEDULED_REGULAR_SESSION_AS_OF_SOURCE",
            "opening_time_basis": (
                "REGULAR_SESSION_ASSUMPTION_NOT_EXECUTABLE_FILL"
            ),
        },
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
    pending.pop("outcome_multiple")
    pending.pop("outcome_observed_at")
    pending.pop("outcome_source_sha256")
    result = report([pending], as_of=datetime(2026, 9, 29, 18, 30, tzinfo=IST))
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


def test_calibration_rejects_self_attested_or_horizon_mismatched_calendars():
    substituted = observation()
    substituted["session_calendar_sha256"] = "d" * 64
    substituted["session_calendar_evidence"]["source_sha256"] = "d" * 64
    with pytest.raises(ValueError, match="source hash changed"):
        report([substituted], as_of=AS_OF)

    late = observation()
    late["session_calendar_evidence"]["source_first_observed_at"] = (
        "2026-09-29T16:00:01+05:30"
    )
    with pytest.raises(ValueError, match="not known by the decision cutoff"):
        report([late], as_of=AS_OF)

    mismatched = observation()
    mismatched["following_day"] = "2026-10-01"
    with pytest.raises(ValueError, match="does not match following_day"):
        report([mismatched], as_of=AS_OF)

    skipped = observation()
    skipped["following_day"] = "2026-10-01"
    skipped["following_open_at"] = "2026-10-01T09:15:00+05:30"
    skipped["session_calendar_evidence"]["session_date"] = "2026-10-01"
    skipped["outcome_observed_at"] = "2026-10-01T09:16:00+05:30"
    with pytest.raises(ValueError, match="next eligible NSE F&O session"):
        report([skipped], as_of=AS_OF)

    before_close = observation()
    before_close["issued_at"] = "2026-09-29T15:29:00+05:30"
    with pytest.raises(ValueError, match="after the stated previous-session close"):
        report([before_close], as_of=AS_OF)


def test_project_sample_and_accuracy_gates_use_forward_rows_only():
    rows = []
    sessions = []
    cursor = date(2026, 1, 2)
    while len(sessions) < 101:
        if cursor.weekday() < 5 and cursor not in NSE_FO_2026_WEEKDAY_HOLIDAYS:
            sessions.append(cursor)
        cursor += timedelta(days=1)
    for index in range(100):
        previous, following = sessions[index : index + 2]
        row = observation(
            f"p{index}",
            .8,
            1.1,
            day=following.isoformat(),
            previous=previous.isoformat(),
            calendar_observed="2025-12-12T00:00:00+05:30",
        )
        rows.append(row)
    result = report(rows, as_of=datetime(2026, 12, 31, tzinfo=IST))
    assert result["status"] == "MEASURED_BELOW_RESEARCH_GATE"
    assert result["research_gates"]["minimum_100_matured"] is True
    assert result["research_gates"]["minimum_60_oos_days"] is True
    assert result["research_gates"]["directional_accuracy_at_least_65pct"] is True
    assert result["research_gates"]["top_decile_precision_at_least_70pct"] is True
    assert result["research_gates"]["fees_and_slippage_applied"] is False
    assert result["research_gates"]["sharpe_at_least_2_5"] is False
    assert result["research_gates"]["max_drawdown_at_most_10pct"] is False
    assert result["research_gates"]["deflated_sharpe_probability_at_least_0_95"] is False
    assert result["metrics"]["directional_accuracy"] == 1
    assert result["metrics"]["top_decile_precision"] == 1
    assert result["metrics"]["net_sharpe"] is None
    assert result["metrics"]["net_max_drawdown"] is None
    assert result["metrics"]["deflated_sharpe_probability"] is None
    assert result["real_money_ready"] is False


def test_registry_matches_code_governance_and_has_no_performance_claim():
    registry = json.loads(
        Path("research/experiments/cepe_forward_calibration_v1.json").read_text()
    )
    assert registry["experiment_id"] == "CEPE-NEXT-008"
    assert registry["forward_predictions"] == 0
    assert registry["forward_outcomes"] == 0
    assert registry["orders_allowed"] is False

    project_registry = json.loads(
        Path("research/experiments/cepe_forward_calibration_v2.json").read_text()
    )
    assert project_registry["parent_commit"] == (
        "ed2697cf47e8a1aabd7d0a421cd8c2cb11c339aa"
    )
    assert project_registry["targets"] == {
        "minimum_oos_trades": 100,
        "minimum_oos_days": 60,
        "minimum_directional_accuracy": 0.65,
        "minimum_top_decile_precision": 0.7,
        "minimum_sharpe": 2.5,
        "maximum_drawdown": 0.1,
        "minimum_deflated_sharpe_probability": 0.95,
    }
    assert project_registry["cost_evidence"]["status"] == (
        "NOT_PROVEN_MISSING_COST_INPUTS"
    )
    assert project_registry["fixture_results_are_market_validation"] is False
    assert project_registry["automatic_model_promotion"] is False


def test_real_forward_no_signal_record_was_sealed_before_open():
    path = Path("research/forward/cepe/2026-09-30_no_verified_signal.json")
    raw = path.read_bytes()
    receipt = Path(
        "research/evidence/cepe/2026-09-30_no_signal_publication_comment.json"
    ).read_bytes()
    assert sha256(raw).hexdigest() == (
        "1a273996c1f150ccfecef2f380c8beea3cc85162bb11dfa1e7ad255963e3f9c3"
    )
    assert sha256(receipt).hexdigest() == (
        "47d224edaf8879e717c1b0edb07bca81339fb47313e6cdc987c5309d78817aa7"
    )
    result = validate_github_publication(
        json.loads(raw),
        decision_bytes=raw,
        publication_receipt_bytes=receipt,
        expected_commit_sha="ce9a1327321691e474fdfefa853a08fd499959cf",
    )
    assert result["status"] == "FORWARD_NO_SIGNAL_SEALED"
    assert result["published_before_open"] is True
    assert result["publication_status"] == (
        "GITHUB_SERVER_TIMESTAMP_RECEIPT_VERIFIED"
    )
    assert result["publication_comment_id"] == 5903586616
    assert result["published_at"] == "2026-09-30T03:40:25+00:00"
    assert result["candidate_count"] == result["prediction_count"] == 0
    assert result["real_money_ready"] is False
    assert result["orders_allowed"] is False


def _real_decision_and_receipt():
    decision = Path(
        "research/forward/cepe/2026-09-30_no_verified_signal.json"
    ).read_bytes()
    receipt = Path(
        "research/evidence/cepe/2026-09-30_no_signal_publication_comment.json"
    ).read_bytes()
    return decision, json.loads(receipt)


@pytest.mark.parametrize(
    "mutation,match",
    [
        (
            lambda receipt: receipt.update(updated_at="2026-09-30T03:41:25Z"),
            "modified after creation",
        ),
        (
            lambda receipt: receipt.update(
                created_at="2026-09-30T03:45:00Z",
                updated_at="2026-09-30T03:45:00Z",
            ),
            "between issue and opening",
        ),
        (
            lambda receipt: receipt.update(body=receipt["body"].replace(
                "1a273996c1f150ccfecef2f380c8beea3cc85162bb11dfa1e7ad255963e3f9c3",
                "0" * 64,
            )),
            "does not bind",
        ),
    ],
)
def test_publication_receipt_rejects_tampering_late_release_or_unbound_body(
    mutation, match
):
    decision, receipt = _real_decision_and_receipt()
    mutation(receipt)
    with pytest.raises(ValueError, match=match):
        validate_github_publication(
            json.loads(decision),
            decision_bytes=decision,
            publication_receipt_bytes=json.dumps(receipt).encode(),
            expected_commit_sha="ce9a1327321691e474fdfefa853a08fd499959cf",
        )


def test_publication_receipt_rejects_wrong_commit_and_duplicate_json_keys():
    decision, receipt = _real_decision_and_receipt()
    with pytest.raises(ValueError, match="does not bind"):
        validate_github_publication(
            json.loads(decision),
            decision_bytes=decision,
            publication_receipt_bytes=json.dumps(receipt).encode(),
            expected_commit_sha="0" * 40,
        )

    duplicate = json.dumps(receipt)[:-1] + ',"id":5903586616}'
    with pytest.raises(ValueError, match="Duplicate publication receipt key"):
        validate_github_publication(
            json.loads(decision),
            decision_bytes=decision,
            publication_receipt_bytes=duplicate.encode(),
            expected_commit_sha="ce9a1327321691e474fdfefa853a08fd499959cf",
        )


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("candidate_count", 1, "zero candidates"),
        ("prediction_count", 1, "zero candidates"),
        ("highest_gap_up_contract", {"symbol": "ABC"}, "forecast or performance"),
        ("forecast_issued", True, "inconsistent"),
        ("retrospective", True, "retrospective"),
        ("orders_allowed", True, "orders_allowed"),
        ("issued_at", "2026-09-30T09:15:00+05:30", "before opening"),
    ],
)
def test_no_signal_contract_rejects_hindsight_or_hidden_trade_claims(field, value, match):
    record = json.loads(
        Path("research/forward/cepe/2026-09-30_no_verified_signal.json").read_text()
    )
    record[field] = value
    with pytest.raises(ValueError, match=match):
        validate_decision(record)


def test_no_signal_contract_rejects_absence_claim_unknown_field_and_late_publication():
    path = Path("research/forward/cepe/2026-09-30_no_verified_signal.json")
    record = json.loads(path.read_text())
    record["source_checks"][0]["interpretation"] = "OFFICIAL_FILE_ABSENT"
    with pytest.raises(ValueError, match="absence claim"):
        validate_decision(record)

    record = json.loads(path.read_text())
    record["trade_action"] = "BUY"
    with pytest.raises(ValueError, match="locked schema"):
        validate_decision(record)

    record = json.loads(path.read_text())
    with pytest.raises(ValueError, match="between issue and opening"):
        validate_decision(
            record,
            externally_published_at=datetime(2026, 9, 30, 9, 15, tzinfo=IST),
        )
