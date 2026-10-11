"""Frozen CEPE-NEXT-006 prior-only ranking and retrospective outcome audit.

The score is preregistered in ``cepe_event_liquidity_v2.json``.  It consumes
only the previous official NSE F&O session snapshot.  Following-session opens
are reference observations, never claimed fills, and this module cannot place
orders.
"""
from __future__ import annotations

from collections import Counter
import csv
from datetime import date
from hashlib import sha256
from io import StringIO
from math import isfinite, log1p
from statistics import mean
from typing import Any

from scripts.cepe_forward_scorecard import _identity
from scripts.cepe_next_open_proof import _rows, compare
from scripts.cepe_session_scope import require_session_alignment


VERSION = "event-liquidity-expiry-v2"
FEATURE_WEIGHTS = {
    "prior_premium_return": 0.35,
    "close_location": 0.15,
    "log_volume": 0.15,
    "log_transactions": 0.10,
    "open_interest_change_ratio": 0.10,
    "near_expiry_regime": 0.10,
    "lower_premium": 0.05,
}


def _number(row: dict[str, str], field: str) -> float:
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(field) from exc
    if not isfinite(value):
        raise ValueError(field)
    return value


def _percentile_ranks(values: list[float]) -> list[float]:
    """Return deterministic average percentile ranks in the interval (0, 1]."""
    size = len(values)
    if not size:
        return []
    order = sorted(range(size), key=lambda index: (values[index], index))
    result = [0.0] * size
    offset = 0
    while offset < size:
        end = offset + 1
        while end < size and values[order[end]] == values[order[offset]]:
            end += 1
        average_rank = ((offset + 1) + end) / 2
        percentile = average_rank / size
        for position in range(offset, end):
            result[order[position]] = percentile
        offset = end
    return result


def rank(previous: bytes, previous_day: date, following_day: date) -> dict[str, Any]:
    """Rank the preregistered top decile using previous-session fields only."""
    if following_day <= previous_day:
        raise ValueError("Following day must follow previous day")
    _rows(previous, previous_day)
    source_hash = sha256(previous).hexdigest()
    eligible: list[dict[str, Any]] = []
    rejected: Counter[str] = Counter()
    reader = csv.DictReader(StringIO(previous.decode("utf-8-sig")))
    for row in reader:
        if row.get("OptnTp") not in {"CE", "PE"}:
            continue
        try:
            expiry = date.fromisoformat(row["XpryDt"])
        except (KeyError, TypeError, ValueError):
            rejected["MISSING_OR_INVALID_EXPIRY"] += 1
            continue
        if expiry < following_day:
            rejected["EXPIRED_BEFORE_OUTCOME"] += 1
            continue
        try:
            opening = _number(row, "OpnPric")
            high = _number(row, "HghPric")
            low = _number(row, "LwPric")
            close = _number(row, "ClsPric")
            previous_close = _number(row, "PrvsClsgPric")
            underlying = _number(row, "UndrlygPric")
            open_interest = _number(row, "OpnIntrst")
            open_interest_change = _number(row, "ChngInOpnIntrst")
            volume = _number(row, "TtlTradgVol")
            transfer_value = _number(row, "TtlTrfVal")
            transactions = _number(row, "TtlNbOfTxsExctd")
            lot_size = _number(row, "NewBrdLotQty")
        except ValueError:
            rejected["MISSING_OR_INVALID_FEATURE"] += 1
            continue
        if not (
            opening > 0
            and high > low >= 0
            and low <= opening <= high
            and low <= close <= high
        ):
            rejected["INVALID_PRICE_RANGE"] += 1
            continue
        if (
            close < 5
            or previous_close <= 0
            or underlying <= 0
            or volume < 1000
            or open_interest <= 0
            or transfer_value <= 0
            or transactions <= 0
            or lot_size <= 0
        ):
            rejected["PRIOR_QUALITY_OR_LIQUIDITY_FILTER"] += 1
            continue
        key = _identity(
            {
                "symbol": row["TckrSymb"],
                "expiry": row["XpryDt"],
                "strike": row["StrkPric"],
                "type": row["OptnTp"],
            }
        )
        eligible.append(
            {
                "symbol": key[0],
                "expiry": key[1],
                "strike": key[2],
                "type": key[3],
                "previous_close": close,
                "raw_momentum": close / opening,
                "feature_values": {
                    "prior_premium_return": close / previous_close,
                    "close_location": (close - low) / (high - low),
                    "log_volume": log1p(volume),
                    "log_transactions": log1p(transactions),
                    "open_interest_change_ratio": open_interest_change / open_interest,
                    "near_expiry_regime": -(expiry - following_day).days,
                    "lower_premium": -close,
                },
            }
        )

    for feature, weight in FEATURE_WEIGHTS.items():
        ranks = _percentile_ranks(
            [item["feature_values"][feature] for item in eligible]
        )
        for item, percentile in zip(eligible, ranks):
            item.setdefault("feature_percentiles", {})[feature] = percentile
            item["score"] = item.get("score", 0.0) + weight * percentile

    eligible.sort(key=lambda item: (-item["score"], _identity(item)))
    selected = eligible[: len(eligible) // 10]
    return {
        "version": VERSION,
        "previous_day": previous_day.isoformat(),
        "following_day": following_day.isoformat(),
        "source_sha256": source_hash,
        "eligible": eligible,
        "selected": selected,
        "rejected": dict(rejected),
        "feature_weights": FEATURE_WEIGHTS,
        "feature_availability": {
            "archived_bhavcopy_fields": "COMPLETE_FOR_ELIGIBLE_ROWS",
            "implied_volatility": "NOT_AVAILABLE_ZERO_COVERAGE",
            "greeks": "NOT_AVAILABLE_ZERO_COVERAGE",
        },
        "feature_status": "PREREGISTERED_RESEARCH_CANDIDATE_NOT_PROVEN",
        "expected_multiple": None,
        "expected_range": None,
        "forward_issued": False,
        "orders_allowed": False,
    }


def _score(items: list[dict[str, Any]], actual: dict[tuple[str, str, str, str], float]) -> dict[str, Any]:
    selected = {_identity(item) for item in items}
    multiples = [actual[key] for key in sorted(selected & actual.keys())]
    thresholds = {str(level): sum(value >= level for value in multiples)
                  for level in (3, 10, 20, 30)}
    population_events = sum(value >= 3 for value in actual.values())
    return {
        "selected": len(selected),
        "scoreable": len(multiples),
        "unscoreable": len(selected - actual.keys()),
        "hits": thresholds["3"],
        "threshold_counts": thresholds,
        "false_picks": len(multiples) - thresholds["3"],
        "missed_events": population_events - thresholds["3"],
        "event_recall": thresholds["3"] / population_events if population_events else None,
        "positive_returns": sum(value > 1 for value in multiples),
        "negative_returns": sum(value < 1 for value in multiples),
        "unchanged_returns": sum(value == 1 for value in multiples),
        "event_precision": thresholds["3"] / len(multiples) if multiples else None,
        "reference_multiples": multiples,
        "gross_reference_mean_return_pct": (
            mean((value - 1) * 100 for value in multiples) if multiples else None
        ),
        "assumed_cost_stress_mean_return_pct": {
            str(bps): (
                mean((value - 1) * 100 - bps / 100 for value in multiples)
                if multiples else None
            )
            for bps in (0, 25, 50, 100)
        },
    }


def evaluate(
    previous: bytes,
    following: bytes,
    previous_day: date,
    following_day: date,
    *,
    session_calendar: bytes | None = None,
) -> dict[str, Any]:
    """Score the frozen prior-only ranking against a later reference open."""
    ranking = rank(previous, previous_day, following_day)
    comparison = compare(
        previous,
        following,
        previous_day,
        following_day,
        min_volume=1,
        min_previous_close=5,
        session_calendar=session_calendar,
    )
    require_session_alignment(comparison)
    eligible = {_identity(item) for item in ranking["eligible"]}
    actual = {
        _identity(row): row["multiple"]
        for row in comparison["matches"]
        if _identity(row) in eligible
    }
    selection_size = len(ranking["eligible"]) // 10
    raw_momentum = sorted(
        ranking["eligible"], key=lambda item: (-item["raw_momentum"], _identity(item))
    )[:selection_size]
    return {
        "version": VERSION,
        "previous_day": previous_day.isoformat(),
        "following_day": following_day.isoformat(),
        "previous_sha256": ranking["source_sha256"],
        "following_sha256": comparison["following_sha256"],
        "session_alignment_status": comparison["session_alignment_status"],
        "session_calendar_sha256": comparison["session_calendar_sha256"],
        "calendar_source_status": comparison["calendar_source_status"],
        "calendar_source_count": comparison["calendar_source_count"],
        "eligible_prior_contracts": len(eligible),
        "matched_eligible_contracts": len(actual),
        "rejected": ranking["rejected"],
        "feature_availability": ranking["feature_availability"],
        "variant": _score(ranking["selected"], actual),
        "same_universe_raw_momentum": _score(raw_momentum, actual),
        "uncapped_eligible_multiples": sorted(actual.values()),
        "population_threshold_counts": {
            str(level): sum(value >= level for value in actual.values())
            for level in (3, 10, 20, 30)
        },
        "status": "RETROSPECTIVE_REFERENCE_ONLY",
        "expected_range": None,
        "source_availability_at_issue": "NOT_PROVEN",
        "cost_and_fill_proof": "NOT_PROVEN",
        "forward_issued_predictions": 0,
        "orders_allowed": False,
    }
