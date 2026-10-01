"""Point-in-time catalyst evidence for equity research.

Only official NSE/BSE publication URLs are accepted. Later returns are recorded
as association, never as proof that a catalyst caused the move.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from math import isfinite
import re
from typing import Any
from urllib.parse import urlparse


SCHEMA_VERSION = "catalyst-evidence-v1"
_ALLOWED_CATEGORIES = {
    "BOARD_MEETING",
    "CORPORATE_ACTION",
    "EARNINGS",
    "ORDER_CONTRACT",
    "REGULATORY",
    "SHAREHOLDING",
    "OTHER_OFFICIAL_FILING",
}
_APPROVED_PRICE_SOURCES = {"NSE", "BSE", "DHAN"}
_ISIN_RE = re.compile(r"^IN[A-Z0-9]{10}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class CatalystEvidenceError(ValueError):
    """Raised when point-in-time evidence is incomplete or contradictory."""


def _timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise CatalystEvidenceError(f"{field}_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CatalystEvidenceError(f"{field}_INVALID") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CatalystEvidenceError(f"{field}_TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _official_url(value: Any) -> str:
    url = str(value).strip()
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    official = (
        host == "nseindia.com"
        or host.endswith(".nseindia.com")
        or host == "bseindia.com"
        or host.endswith(".bseindia.com")
    )
    if parsed.scheme != "https" or not official:
        raise CatalystEvidenceError("SOURCE_URL_NOT_OFFICIAL_NSE_BSE")
    return url


def _price(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise CatalystEvidenceError(f"{field}_INVALID")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise CatalystEvidenceError(f"{field}_INVALID") from exc
    if not isfinite(number) or number <= 0:
        raise CatalystEvidenceError(f"{field}_INVALID")
    return number


def _digest(value: Any, field: str) -> str:
    digest = str(value).strip().lower()
    if not _SHA256_RE.fullmatch(digest):
        raise CatalystEvidenceError(f"{field}_INVALID_SHA256")
    return digest


def _canonical(record: dict[str, Any]) -> bytes:
    payload = {key: value for key, value in record.items() if key != "record_hash"}
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def build_catalyst_record(
    raw_source: bytes,
    metadata: dict[str, Any],
    *,
    prediction_issued_at: str,
) -> dict[str, Any]:
    """Seal an official filing and determine if it was knowable at issue time."""
    if not isinstance(raw_source, bytes) or not raw_source:
        raise CatalystEvidenceError("RAW_SOURCE_BYTES_REQUIRED")
    published = _timestamp(metadata.get("published_at"), "PUBLISHED_AT")
    disseminated = _timestamp(
        metadata.get("disseminated_at"),
        "DISSEMINATED_AT",
    )
    first_observed = _timestamp(
        metadata.get("first_observed_at"),
        "FIRST_OBSERVED_AT",
    )
    issue = _timestamp(prediction_issued_at, "PREDICTION_ISSUED_AT")
    if not published <= disseminated <= first_observed:
        raise CatalystEvidenceError("INVALID_PUBLICATION_TIME_ORDER")

    symbol = str(metadata.get("symbol", "")).strip().upper()
    isin = str(metadata.get("isin", "")).strip().upper()
    if not symbol:
        raise CatalystEvidenceError("SYMBOL_REQUIRED")
    if not _ISIN_RE.fullmatch(isin):
        raise CatalystEvidenceError("ISIN_INVALID")
    category = str(metadata.get("category", "")).strip().upper()
    if category not in _ALLOWED_CATEGORIES:
        raise CatalystEvidenceError("CATEGORY_UNAPPROVED")

    source_hash = sha256(raw_source).hexdigest()
    declared = metadata.get("source_sha256")
    if declared is not None and _digest(declared, "SOURCE_HASH") != source_hash:
        raise CatalystEvidenceError("SOURCE_HASH_MISMATCH")

    known_by_issue = first_observed <= issue
    record = {
        "schema_version": SCHEMA_VERSION,
        "symbol": symbol,
        "isin": isin,
        "source_url": _official_url(metadata.get("source_url")),
        "source_sha256": source_hash,
        "published_at": published.isoformat(),
        "disseminated_at": disseminated.isoformat(),
        "first_observed_at": first_observed.isoformat(),
        "prediction_issued_at": issue.isoformat(),
        "category": category,
        "known_by_prediction_issue_time": known_by_issue,
        "feature_eligible": known_by_issue,
        "causal_attribution": "NOT_CLAIMED",
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    record["record_hash"] = sha256(_canonical(record)).hexdigest()
    return record


def measure_later_return(
    catalyst: dict[str, Any],
    outcome: dict[str, Any],
) -> dict[str, Any]:
    """Measure a later return only for a catalyst known at forecast issue time."""
    try:
        if catalyst.get("schema_version") != SCHEMA_VERSION:
            raise CatalystEvidenceError("CATALYST_SCHEMA_INVALID")
        if catalyst.get("record_hash") != sha256(_canonical(catalyst)).hexdigest():
            raise CatalystEvidenceError("CATALYST_RECORD_TAMPERED")
        if catalyst.get("feature_eligible") is not True:
            raise CatalystEvidenceError("POST_ISSUE_CATALYST_NOT_ELIGIBLE")

        issue = _timestamp(
            catalyst.get("prediction_issued_at"),
            "PREDICTION_ISSUED_AT",
        )
        entry_at = _timestamp(outcome.get("entry_observed_at"), "ENTRY_OBSERVED_AT")
        exit_at = _timestamp(outcome.get("exit_observed_at"), "EXIT_OBSERVED_AT")
        if not entry_at <= issue < exit_at:
            raise CatalystEvidenceError("INVALID_OUTCOME_TIME_ORDER")

        symbol = str(outcome.get("symbol", "")).strip().upper()
        if symbol != catalyst.get("symbol"):
            raise CatalystEvidenceError("SYMBOL_MISMATCH")
        source = str(outcome.get("source", "")).strip().upper()
        if source not in _APPROVED_PRICE_SOURCES:
            raise CatalystEvidenceError("OUTCOME_SOURCE_UNVERIFIED")
        raw = outcome.get("source_snapshot")
        if not isinstance(raw, bytes) or not raw:
            raise CatalystEvidenceError("OUTCOME_SNAPSHOT_REQUIRED")
        digest = _digest(outcome.get("source_sha256"), "OUTCOME_SOURCE_HASH")
        if sha256(raw).hexdigest() != digest:
            raise CatalystEvidenceError("OUTCOME_SOURCE_HASH_MISMATCH")

        entry = _price(outcome.get("entry_adjusted_close"), "ENTRY_PRICE")
        exit_price = _price(outcome.get("exit_adjusted_close"), "EXIT_PRICE")
    except (CatalystEvidenceError, TypeError, ValueError) as exc:
        reason = (
            str(exc)
            if isinstance(exc, CatalystEvidenceError)
            else "REQUIRED_EVIDENCE_MISSING"
        )
        return {"status": "NOT_PROVEN", "reason": reason}

    return_pct = (exit_price / entry - 1.0) * 100.0
    return {
        "status": "MEASURED_CORRELATION_ONLY",
        "symbol": catalyst["symbol"],
        "isin": catalyst["isin"],
        "category": catalyst["category"],
        "prediction_issued_at": issue.isoformat(),
        "exit_observed_at": exit_at.isoformat(),
        "adjusted_return_pct": round(return_pct, 6),
        "catalyst_record_hash": catalyst["record_hash"],
        "outcome_source": source,
        "outcome_source_sha256": digest,
        "causal_attribution": "NOT_CLAIMED",
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
