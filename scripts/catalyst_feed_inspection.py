"""Seal an official NSE announcement-feed inspection without inventing a filing."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any


SCHEMA = "catalyst-feed-inspection-v1"
URL = "https://www.nseindia.com/api/corporate-announcements?index=equities&from_date=01-10-2026&to_date=01-10-2026"
_ISIN = re.compile(r"^IN[A-Z0-9]{10}$")


def _instant(value: Any, field: str) -> datetime:
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"{field} requires timezone")
    return result.astimezone(timezone.utc)


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(
        {key: item for key, item in value.items() if key != "record_hash"},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def build_no_match_inspection(
    raw_feed: bytes,
    receipt: dict[str, Any],
    *,
    symbol: str,
    isin: str,
    prediction_id: str,
    prediction_event_hash: str,
    prediction_issued_at: str,
) -> dict[str, Any]:
    """Record zero exact matches while refusing to turn that into absence proof."""
    if (
        not raw_feed
        or receipt.get("url") != URL
        or receipt.get("final_url") != URL
        or receipt.get("http_status") != 200
        or receipt.get("raw_sha256") != sha256(raw_feed).hexdigest()
        or receipt.get("bytes") != len(raw_feed)
    ):
        raise ValueError("Official announcement receipt mismatch")
    observed = _instant(receipt.get("first_observed_at"), "first_observed_at")
    issued = _instant(prediction_issued_at, "prediction_issued_at")
    symbol = symbol.strip().upper()
    isin = isin.strip().upper()
    if not symbol or not _ISIN.fullmatch(isin):
        raise ValueError("Invalid symbol or ISIN")
    if len(prediction_event_hash) != 64 or any(c not in "0123456789abcdef" for c in prediction_event_hash):
        raise ValueError("Invalid prediction event hash")
    try:
        rows = json.loads(raw_feed)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid announcement feed") from exc
    if not isinstance(rows, list):
        raise ValueError("Announcement feed must be a list")
    for row in rows:
        if not isinstance(row, dict) or "symbol" not in row or "sm_isin" not in row:
            raise ValueError("Unsupported announcement row")
    matches = [
        row for row in rows
        if str(row["symbol"]).strip().upper() == symbol
        or str(row["sm_isin"]).strip().upper() == isin
    ]
    if matches:
        raise ValueError("Exact filing match requires filing-level evidence workflow")
    record = {
        "schema": SCHEMA,
        "task_id": "CAT-LINK-011",
        "evidence_class": "OFFICIAL_FEED_INSPECTION_NO_EXACT_MATCH",
        "symbol": symbol,
        "isin": isin,
        "prediction_id": prediction_id,
        "prediction_event_hash": prediction_event_hash,
        "prediction_issued_at": issued.isoformat(),
        "source_url": URL,
        "source_first_observed_at": observed.isoformat(),
        "source_raw_sha256": sha256(raw_feed).hexdigest(),
        "source_raw_bytes": len(raw_feed),
        "captured_feed_rows": len(rows),
        "exact_symbol_or_isin_matches": 0,
        "published_at": None,
        "disseminated_at": None,
        "known_by_prediction_issue_time": False,
        "feature_eligible": False,
        "interpretation": "NO_EXACT_MATCH_IN_CAPTURED_FEED_NOT_PROOF_OF_ABSENCE",
        "later_measured_return": None,
        "catalyst_contribution": "NOT_PROVEN",
        "causal_attribution": "NOT_CLAIMED",
        "live_trading_enabled": False,
        "orders_allowed": False,
    }
    if observed <= issued:
        raise ValueError("This no-match contract is only for a post-issue inspection")
    record["record_hash"] = sha256(_canonical(record)).hexdigest()
    return record


def validate_no_match_inspection(record: dict[str, Any]) -> dict[str, Any]:
    if record.get("schema") != SCHEMA:
        raise ValueError("Invalid inspection schema")
    if record.get("record_hash") != sha256(_canonical(record)).hexdigest():
        raise ValueError("Inspection record hash mismatch")
    if record.get("exact_symbol_or_isin_matches") != 0:
        raise ValueError("No-match record contains matches")
    if record.get("known_by_prediction_issue_time") is not False or record.get("feature_eligible") is not False:
        raise ValueError("Post-issue inspection cannot become a prediction feature")
    if record.get("published_at") is not None or record.get("disseminated_at") is not None:
        raise ValueError("No-match record cannot invent filing timestamps")
    if record.get("later_measured_return") is not None or record.get("catalyst_contribution") != "NOT_PROVEN":
        raise ValueError("No-match record cannot claim an outcome")
    if record.get("causal_attribution") != "NOT_CLAIMED":
        raise ValueError("Causality cannot be inferred")
    if record.get("live_trading_enabled") is not False or record.get("orders_allowed") is not False:
        raise ValueError("Unsafe inspection flags")
    return {
        "status": "POST_ISSUE_NO_MATCH_INSPECTION_SEALED",
        "symbol": record["symbol"],
        "captured_feed_rows": record["captured_feed_rows"],
        "exact_matches": 0,
        "feature_eligible": False,
        "catalyst_contribution": "NOT_PROVEN",
        "orders_allowed": False,
    }
