"""Fail-closed, read-only prediction vs later-market outcome audit.

This does not train a model, place orders, or infer missing broker fills.
"""
from datetime import datetime
from math import isfinite
from typing import Any


def _price(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value) or value <= 0:
        raise ValueError("INVALID_AUDIT_PRICE")
    return float(value)


def _time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("INVALID_AUDIT_TIMESTAMP")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("INVALID_AUDIT_TIMESTAMP") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("TIMESTAMP_MUST_BE_TIMEZONE_AWARE")
    return parsed


def evaluate_paper_prediction(
    *, trade_id: str, predicted_gain_pct: float, entry_price: float,
    exit_price: float, entry_timestamp: str, exit_timestamp: str,
    market_top_gain_pct: float | None = None,
    market_top_source: str | None = None,
    market_top_timestamp: str | None = None,
    market_top_universe: str | None = None,
    entry_source: str = "UNVERIFIED", exit_source: str = "UNVERIFIED",
) -> dict[str, Any]:
    """Compute descriptive gross returns, never verified net returns or learning claims."""
    if not isinstance(trade_id, str) or not trade_id.strip():
        raise ValueError("MISSING_TRADE_ID")
    if isinstance(predicted_gain_pct, bool) or not isinstance(predicted_gain_pct, (int, float)) or not isfinite(predicted_gain_pct):
        raise ValueError("INVALID_PREDICTION")
    entry, exit_ = _price(entry_price), _price(exit_price)
    started, ended = _time(entry_timestamp), _time(exit_timestamp)
    if ended <= started:
        raise ValueError("EXIT_MUST_FOLLOW_ENTRY")
    actual = round((exit_ / entry - 1) * 100, 4)
    result = {
        "trade_id": trade_id, "predicted_gain_pct": float(predicted_gain_pct),
        "actual_gross_gain_pct": actual,
        "prediction_error_pct_points": round(actual - predicted_gain_pct, 4),
        "entry_timestamp": started.isoformat(), "exit_timestamp": ended.isoformat(),
        "holding_seconds": round((ended - started).total_seconds(), 3),
        "entry_source": entry_source, "exit_source": exit_source,
        "real_market_outcome_verified": False,
        "net_gain_pct": None, "net_gain_verified": False,
        "market_top_comparison_status": "NOT_VERIFIED",
        "market_top_gain_pct": None, "market_top_gap_pct_points": None,
        "learning_status": "NOT_TRAINED",
        "training_eligible": False,
        "reason": "Gross arithmetic only; market provenance, fees and leakage-safe labels require independent evidence",
    }
    if market_top_gain_pct is not None:
        if isinstance(market_top_gain_pct, bool) or not isinstance(market_top_gain_pct, (int, float)) or not isfinite(market_top_gain_pct):
            raise ValueError("INVALID_MARKET_TOP_GAIN")
        if not all(isinstance(v, str) and v.strip() for v in (market_top_source, market_top_timestamp, market_top_universe)):
            raise ValueError("MARKET_TOP_PROVENANCE_REQUIRED")
        observed = _time(market_top_timestamp)
        if observed < started or observed > ended:
            raise ValueError("MARKET_TOP_TIME_WINDOW_MISMATCH")
        result.update({
            "market_top_comparison_status": "PROVISIONAL_SOURCE_REPORTED",
            "market_top_gain_pct": float(market_top_gain_pct),
            "market_top_gap_pct_points": round(actual - market_top_gain_pct, 4),
            "market_top_source": market_top_source,
            "market_top_timestamp": observed.isoformat(),
            "market_top_universe": market_top_universe,
        })
    return result
