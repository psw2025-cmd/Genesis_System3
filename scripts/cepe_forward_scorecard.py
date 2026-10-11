"""Score pre-issued CE/PE picks against the complete next-open contract set.

The input comparison comes from cepe_next_open_proof.compare. Predictions must
be independently recorded before the following session; historical winners
selected after the open cannot enter this scorecard.
"""
from __future__ import annotations

from datetime import date, datetime
from math import isfinite
from typing import Any

from scripts.cepe_session_scope import IST, require_session_alignment, session_scope


def _identity(row: dict[str, Any]) -> tuple[str, str, str, str]:
    symbol = str(row["symbol"]).strip().upper()
    expiry = date.fromisoformat(str(row["expiry"])).isoformat()
    strike = float(row["strike"])
    kind = str(row["type"]).strip().upper()
    if not symbol or not isfinite(strike) or strike < 0 or kind not in {"CE", "PE"}:
        raise ValueError("Invalid contract identity")
    return symbol, expiry, f"{strike:.4f}", kind


def score(
    predictions: list[dict[str, Any]],
    comparison: dict[str, Any],
    *,
    target_multiple: float,
    issued_cutoff: datetime,
    session_calendar: bytes | None = None,
) -> dict[str, Any]:
    """Count hits, false picks, missed movers and uncovered selections.

    issued_cutoff is a pre-registered cutoff before the next opening, not
    inferred from the eventual price move. An empty prediction list yields
    NOT_PROVEN rather than a spurious zero-percent accuracy claim.
    """
    if issued_cutoff.tzinfo is None or issued_cutoff.utcoffset() is None:
        raise ValueError("Cutoff needs timezone")
    target = float(target_multiple)
    if not isfinite(target) or target <= 1:
        raise ValueError("Target multiple must exceed one")
    following = date.fromisoformat(comparison["following_day"])
    previous = date.fromisoformat(comparison["previous_day"])
    scope = session_scope(previous, following, session_calendar, known_by=issued_cutoff)
    require_session_alignment(scope)
    if comparison.get("session_calendar_sha256") != scope["session_calendar_sha256"]:
        raise ValueError("Comparison calendar differs from prediction calendar")
    if issued_cutoff >= datetime.fromisoformat(scope["following_open_at"]):
        raise ValueError("Cutoff is not before next opening")
    if comparison.get("distribution_scope") != "FULL_MATCHED_CONTRACT_SET_UNCAPPED":
        raise ValueError("Comparison must cover all eligible matched contracts")
    if not comparison.get("previous_sha256") or not comparison.get("following_sha256"):
        raise ValueError("Missing data provenance")
    actual: dict[tuple[str, str, str, str], float] = {}
    for row in comparison["matches"]:
        key = _identity(row)
        if key in actual:
            raise ValueError("Duplicate actual contract")
        multiple = float(row["multiple"])
        if not isfinite(multiple) or multiple <= 0:
            raise ValueError("Invalid actual multiple")
        actual[key] = multiple
    selected: set[tuple[str, str, str, str]] = set()
    for prediction in predictions:
        timestamp = datetime.fromisoformat(str(prediction["issued_at"]).replace("Z", "+00:00"))
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("Prediction timestamp needs timezone")
        if timestamp > issued_cutoff:
            raise ValueError("Prediction issued after registered cutoff")
        if timestamp.astimezone(IST).date() < previous:
            raise ValueError("Prediction predates previous session")
        session_scope(previous, following, session_calendar, known_by=timestamp)
        if prediction.get("source_sha256") != comparison["previous_sha256"]:
            raise ValueError("Prediction is not bound to previous source bytes")
        key = _identity(prediction)
        if key in selected:
            raise ValueError("Duplicate prediction")
        selected.add(key)
    winners = {key for key, multiple in actual.items() if multiple >= target}
    covered = selected & actual.keys()
    hits = len(covered & winners)
    wrong = len(covered - winners)
    missed = len(winners - selected)
    uncovered = len(selected - actual.keys())
    return {
        **scope,
        "status": "SCORED_PREISSUED_REFERENCES" if selected and covered else "NOT_PROVEN",
        "target_multiple": target,
        "predictions": len(selected),
        "eligible_contracts": len(actual),
        "actual_winners": len(winners),
        "hits": hits,
        "false_picks": wrong,
        "missed_winners": missed,
        "uncovered_picks": uncovered,
        "precision": hits / len(covered) if covered else None,
        "recall": hits / len(winners) if winners else None,
        "baseline_winner_rate": len(winners) / len(actual) if actual else None,
        "previous_sha256": comparison["previous_sha256"],
        "following_sha256": comparison["following_sha256"],
        "opening_fill_proven": False,
        "net_return_proven": False,
        "orders_allowed": False,
    }
