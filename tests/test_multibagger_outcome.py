"""Numerical checks for the equity outcome contract; no claims about model skill."""
from datetime import datetime, timezone

from dashboard.backend.multibagger_outcome import reconcile


PREDICTION = {
    "prediction_id": "p-1", "symbol": "RAYMOND",
    "issued_at": "2026-09-01T12:00:00+00:00",
    "due_at": "2026-09-08T12:00:00+00:00",
    "entry_observed_at": "2026-09-01T10:00:00+00:00",
    "entry_adjusted_close": 100.0, "predicted_return_pct": 20.0,
    "entry_source_hash": "entry-sha", "adjustment_basis": "corporate-action-series-v1",
}
OUTCOME = {
    "symbol": "RAYMOND", "observed_at": "2026-09-08T12:00:00+00:00",
    "adjusted_close": 110.0, "source": "NSE",
    "source_hash": "exit-sha", "adjustment_basis": "corporate-action-series-v1",
}
NOW = datetime(2026, 9, 24, tzinfo=timezone.utc)


def test_reconciles_signed_point_in_time_prices_without_claiming_target_hit():
    result = reconcile(PREDICTION, OUTCOME, now=NOW)
    assert result["status"] == "EVALUATED"
    assert result["actual_return_pct"] == 10.0
    assert result["absolute_error_pp"] == 10.0
    assert result["direction_correct"] is True
    assert result["outcome_source_hash"] == "exit-sha"
    assert result["live_trading_enabled"] is False


def test_rejects_future_outcome_or_missing_provenance():
    assert reconcile(PREDICTION, {**OUTCOME, "observed_at": "2026-09-25T12:00:00+00:00"}, now=NOW)["status"] == "NOT_PROVEN"
    assert reconcile(PREDICTION, {**OUTCOME, "source_hash": ""}, now=NOW)["reason"] == "SOURCE_HASH_REQUIRED"
    assert reconcile(PREDICTION, {**OUTCOME, "adjustment_basis": "raw-unadjusted"}, now=NOW)["reason"] == "CORPORATE_ACTION_BASIS_MISMATCH"


def test_rejects_outcome_before_horizon_and_invalid_price():
    assert reconcile(PREDICTION, {**OUTCOME, "observed_at": "2026-09-07T12:00:00+00:00"}, now=NOW)["reason"] == "INVALID_TIME_ORDER"
    assert reconcile(PREDICTION, {**OUTCOME, "adjusted_close": float("nan")}, now=NOW)["reason"] == "INVALID_PRICE"
