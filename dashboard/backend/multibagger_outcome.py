"""Point-in-time equity forecast-to-outcome reconciliation; no orders or market fetches.

Inputs must come from separately retained, dated source snapshots. A matching
price is evidence of an observed outcome, not proof the model predicted it well.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from math import isfinite
from typing import Any


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("TIMESTAMP_REQUIRED")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("INVALID_TIMESTAMP") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return result.astimezone(timezone.utc)


def _price(value: Any) -> float:
    if isinstance(value, bool):
        raise ValueError("INVALID_PRICE")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_PRICE") from exc
    if not isfinite(result) or result <= 0:
        raise ValueError("INVALID_PRICE")
    return result


def reconcile(prediction: dict[str, Any], outcome: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    """Evaluate one issued equity prediction against a later adjusted close.

    Returns NOT_PROVEN with a reason for missing or contradictory evidence.
    The seven-day tolerance covers non-trading days but cannot choose a more
    favorable distant exit. Both prices must share an adjustment basis.
    """
    try:
        issued = _timestamp(prediction["issued_at"])
        due = _timestamp(prediction["due_at"])
        entry_at = _timestamp(prediction["entry_observed_at"])
        exit_at = _timestamp(outcome["observed_at"])
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        if not entry_at <= issued < due <= exit_at <= current:
            raise ValueError("INVALID_TIME_ORDER")
        if exit_at > due + timedelta(days=7):
            raise ValueError("OUTCOME_TOO_LATE")
        symbol = str(prediction["symbol"]).strip().upper()
        if not symbol or symbol != str(outcome["symbol"]).strip().upper():
            raise ValueError("SYMBOL_MISMATCH")
        pred_id = str(prediction["prediction_id"]).strip()
        if not pred_id:
            raise ValueError("PREDICTION_ID_REQUIRED")
        source = str(outcome["source"]).strip().upper()
        if source not in {"NSE", "BSE", "DHAN"}:
            raise ValueError("OUTCOME_SOURCE_UNVERIFIED")
        if not str(prediction["entry_source_hash"]).strip() or not str(outcome["source_hash"]).strip():
            raise ValueError("SOURCE_HASH_REQUIRED")
        basis = str(prediction["adjustment_basis"]).strip()
        if not basis or basis != str(outcome["adjustment_basis"]).strip():
            raise ValueError("CORPORATE_ACTION_BASIS_MISMATCH")
        entry = _price(prediction["entry_adjusted_close"])
        exit_price = _price(outcome["adjusted_close"])
        forecast = float(prediction["predicted_return_pct"])
        if not isfinite(forecast):
            raise ValueError("INVALID_FORECAST")
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        reason = str(exc) if isinstance(exc, ValueError) else "REQUIRED_EVIDENCE_MISSING"
        return {"status": "NOT_PROVEN", "reason": reason}

    actual = (exit_price / entry - 1.0) * 100.0
    return {
        "status": "EVALUATED",
        "prediction_id": pred_id,
        "symbol": symbol,
        "issued_at": issued.isoformat(),
        "due_at": due.isoformat(),
        "outcome_observed_at": exit_at.isoformat(),
        "predicted_return_pct": round(forecast, 6),
        "actual_return_pct": round(actual, 6),
        "absolute_error_pp": round(abs(forecast - actual), 6),
        "direction_correct": (forecast > 0) == (actual > 0) if forecast != 0 and actual != 0 else forecast == actual,
        "entry_source_hash": prediction["entry_source_hash"],
        "outcome_source_hash": outcome["source_hash"],
        "outcome_source": source,
        "adjustment_basis": basis,
        "live_trading_enabled": False,
    }
