"""Point-in-time calibration report for genuinely forward CE/PE forecasts.

This module is deliberately separate from retrospective CE/PE replays.  It
accepts only source-qualified forecasts that were independently published
before the following NSE opening and binds every matured outcome to later raw
source bytes.  Pending forecasts stay pending; an overdue missing outcome
fails the research gate instead of being silently discarded.

The report is research evidence only.  Opening prices are references, not
executable fills, and this code never places an order.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from math import isfinite, log, sqrt
from pathlib import Path
from statistics import mean, median
from typing import Any


TASK_ID = "CEPE-NEXT-008"
VERSION = "forward-calibration-v1"
MIN_MATURED_OUTCOMES = 100
MIN_OOS_DAYS = 60
MIN_DIRECTIONAL_ACCURACY = 0.65
EVENT_TYPES = {"positive_next_open", "at_least_3x"}


def _instant(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include timezone")
    return parsed


def _day(value: Any, field: str) -> date:
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc


def _sha(value: Any, field: str) -> str:
    text = str(value).lower()
    if len(text) != 64 or any(char not in "0123456789abcdef" for char in text):
        raise ValueError(f"Invalid {field}")
    return text


def _number(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if not isfinite(number):
        raise ValueError(f"Invalid {field}")
    return number


def _wilson(successes: int, total: int) -> list[float] | None:
    if not total:
        return None
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return [max(0.0, centre - margin), min(1.0, centre + margin)]


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _validate_common(record: dict[str, Any]) -> dict[str, Any]:
    prediction_id = str(record.get("prediction_id", "")).strip()
    strategy_id = str(record.get("strategy_id", "")).strip()
    strategy_version = str(record.get("strategy_version", "")).strip()
    symbol = str(record.get("symbol", "")).strip().upper()
    option_type = str(record.get("type", "")).strip().upper()
    if not all((prediction_id, strategy_id, strategy_version, symbol)):
        raise ValueError("Missing immutable forecast identity")
    if option_type not in {"CE", "PE"}:
        raise ValueError("Invalid option type")
    strike = _number(record.get("strike"), "strike")
    if strike < 0:
        raise ValueError("Invalid strike")
    expiry = _day(record.get("expiry"), "expiry")
    previous_day = _day(record.get("previous_day"), "previous_day")
    following_day = _day(record.get("following_day"), "following_day")
    if not previous_day < following_day or expiry < following_day:
        raise ValueError("Invalid session or expiry chronology")

    issued_at = _instant(record.get("issued_at"), "issued_at")
    published_at = _instant(record.get("published_at"), "published_at")
    cutoff_at = _instant(record.get("cutoff_at"), "cutoff_at")
    following_open_at = _instant(record.get("following_open_at"), "following_open_at")
    if not issued_at <= published_at <= cutoff_at < following_open_at:
        raise ValueError("Forecast was not published before following opening")

    probability = _number(record.get("probability"), "probability")
    if not 0 < probability < 1:
        raise ValueError("Probability must be strictly between zero and one")
    event_type = str(record.get("event_type", ""))
    if event_type not in EVENT_TYPES:
        raise ValueError("Unsupported event type")
    if record.get("forward_issued") is not True or record.get("retrospective") is not False:
        raise ValueError("Retrospective rows cannot enter forward calibration")
    if record.get("source_qualified") is not True:
        raise ValueError("Prediction source is not qualified")
    if record.get("official_session_verified") is not True:
        raise ValueError("Official session is not verified")
    if record.get("publication_verified") is not True:
        raise ValueError("Independent publication is not verified")
    if record.get("orders_allowed") is not False:
        raise ValueError("Orders must remain disabled")
    if record.get("opening_fill_proven") is not False:
        raise ValueError("Opening reference cannot be labelled as a proven fill")

    return {
        "prediction_id": prediction_id,
        "strategy_id": strategy_id,
        "strategy_version": strategy_version,
        "event_type": event_type,
        "probability": probability,
        "symbol": symbol,
        "expiry": expiry.isoformat(),
        "strike": format(strike, ".4f"),
        "type": option_type,
        "previous_day": previous_day.isoformat(),
        "following_day": following_day.isoformat(),
        "issued_at": issued_at.isoformat(),
        "published_at": published_at.isoformat(),
        "cutoff_at": cutoff_at.isoformat(),
        "following_open_at": following_open_at.isoformat(),
        "prediction_source_sha256": _sha(
            record.get("prediction_source_sha256"), "prediction_source_sha256"
        ),
        "publication_receipt_sha256": _sha(
            record.get("publication_receipt_sha256"), "publication_receipt_sha256"
        ),
        "session_calendar_sha256": _sha(
            record.get("session_calendar_sha256"), "session_calendar_sha256"
        ),
    }


def report(records: list[dict[str, Any]], *, as_of: datetime) -> dict[str, Any]:
    """Return an honest calibration report over one strategy/event cohort."""
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must include timezone")
    if not isinstance(records, list):
        raise ValueError("Records must be a list")

    normalized: list[dict[str, Any]] = []
    pending = 0
    overdue = 0
    seen_ids: set[str] = set()
    cohort: tuple[str, str, str] | None = None
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each record must be an object")
        item = _validate_common(record)
        if item["prediction_id"] in seen_ids:
            raise ValueError("Duplicate prediction_id")
        seen_ids.add(item["prediction_id"])
        current_cohort = (
            item["strategy_id"], item["strategy_version"], item["event_type"]
        )
        if cohort is None:
            cohort = current_cohort
        elif current_cohort != cohort:
            raise ValueError("Calibration cannot mix strategy versions or event types")

        following_open = _instant(item["following_open_at"], "following_open_at")
        outcome_multiple = record.get("outcome_multiple")
        observed_at = record.get("outcome_observed_at")
        outcome_hash = record.get("outcome_source_sha256")
        if outcome_multiple is None and observed_at is None and outcome_hash is None:
            if as_of < following_open:
                pending += 1
            else:
                overdue += 1
            continue
        if outcome_multiple is None or observed_at is None or outcome_hash is None:
            raise ValueError("Partial outcome provenance")
        observed = _instant(observed_at, "outcome_observed_at")
        if observed < following_open or observed > as_of:
            raise ValueError("Outcome timestamp conflicts with following opening or as_of")
        multiple = _number(outcome_multiple, "outcome_multiple")
        if multiple <= 0:
            raise ValueError("Invalid outcome_multiple")
        outcome_source_sha256 = _sha(outcome_hash, "outcome_source_sha256")
        if outcome_source_sha256 == item["prediction_source_sha256"]:
            raise ValueError("Outcome must be bound to later source bytes")
        item.update(
            outcome_multiple=multiple,
            outcome_observed_at=observed.isoformat(),
            outcome_source_sha256=outcome_source_sha256,
        )
        normalized.append(item)

    if not normalized:
        status = "NOT_PROVEN_DATA_GAP" if overdue else "NOT_PROVEN"
        return {
            "task_id": TASK_ID,
            "version": VERSION,
            "status": status,
            "as_of": as_of.isoformat(),
            "forward_predictions": len(records),
            "matured_outcomes": 0,
            "pending_outcomes": pending,
            "overdue_missing_outcomes": overdue,
            "metrics": None,
            "research_gates": {
                "minimum_100_matured": False,
                "minimum_60_oos_days": False,
                "directional_accuracy_at_least_65pct": False,
                "zero_overdue_missing_outcomes": overdue == 0,
            },
            "real_money_ready": False,
            "orders_allowed": False,
        }

    outcomes = [
        (item["outcome_multiple"] > 1)
        if item["event_type"] == "positive_next_open"
        else (item["outcome_multiple"] >= 3)
        for item in normalized
    ]
    probabilities = [item["probability"] for item in normalized]
    correct = [((probability >= 0.5) == outcome) for probability, outcome in zip(probabilities, outcomes)]
    brier = mean((probability - int(outcome)) ** 2 for probability, outcome in zip(probabilities, outcomes))
    log_loss = -mean(
        int(outcome) * log(probability) + (1 - int(outcome)) * log(1 - probability)
        for probability, outcome in zip(probabilities, outcomes)
    )

    bins: list[dict[str, Any]] = []
    ece = 0.0
    for index in range(10):
        members = [
            position
            for position, probability in enumerate(probabilities)
            if min(9, int(probability * 10)) == index
        ]
        if not members:
            continue
        mean_probability = mean(probabilities[position] for position in members)
        observed_rate = mean(int(outcomes[position]) for position in members)
        ece += len(members) / len(normalized) * abs(mean_probability - observed_rate)
        bins.append(
            {
                "lower": index / 10,
                "upper": (index + 1) / 10,
                "count": len(members),
                "mean_probability": mean_probability,
                "observed_rate": observed_rate,
            }
        )

    returns = [(item["outcome_multiple"] - 1) * 100 for item in normalized]
    successes = sum(correct)
    oos_days = len({item["following_day"] for item in normalized})
    accuracy = successes / len(normalized)
    gates = {
        "minimum_100_matured": len(normalized) >= MIN_MATURED_OUTCOMES,
        "minimum_60_oos_days": oos_days >= MIN_OOS_DAYS,
        "directional_accuracy_at_least_65pct": accuracy >= MIN_DIRECTIONAL_ACCURACY,
        "zero_overdue_missing_outcomes": overdue == 0,
    }
    status = (
        "RESEARCH_CALIBRATION_GATE_PASS"
        if all(gates.values())
        else ("NOT_PROVEN_DATA_GAP" if overdue else "MEASURED_BELOW_RESEARCH_GATE")
    )
    normalized.sort(key=lambda item: (item["issued_at"], item["prediction_id"]))
    return {
        "task_id": TASK_ID,
        "version": VERSION,
        "status": status,
        "as_of": as_of.isoformat(),
        "strategy_id": cohort[0],
        "strategy_version": cohort[1],
        "event_type": cohort[2],
        "forward_predictions": len(records),
        "matured_outcomes": len(normalized),
        "pending_outcomes": pending,
        "overdue_missing_outcomes": overdue,
        "oos_days": oos_days,
        "positive_events": sum(outcomes),
        "negative_events": len(outcomes) - sum(outcomes),
        "metrics": {
            "directional_accuracy": accuracy,
            "directional_accuracy_wilson_95pct": _wilson(successes, len(normalized)),
            "brier_score": brier,
            "naive_50pct_brier": 0.25,
            "brier_skill_vs_50pct": 1 - brier / 0.25,
            "log_loss": log_loss,
            "expected_calibration_error_10_bin": ece,
            "reliability_bins": bins,
            "mean_gross_reference_return_pct": mean(returns),
            "median_gross_reference_return_pct": median(returns),
            "threshold_counts": {
                str(level): sum(item["outcome_multiple"] >= level for item in normalized)
                for level in (3, 10, 20, 30)
            },
        },
        "research_gates": gates,
        "observation_set_sha256": sha256(_canonical(normalized)).hexdigest(),
        "opening_price_is_executable_fill": False,
        "real_money_ready": False,
        "orders_allowed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument(
        "--as-of", required=True, type=lambda value: _instant(value, "as_of")
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = report(payload, as_of=args.as_of)
    rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
