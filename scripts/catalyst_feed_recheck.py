"""Validate a later official catalyst-feed capture without backfilling it."""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
import re
from typing import Any
from urllib.parse import urlsplit


SCHEMA = "catalyst-feed-recheck-v1"
TASK_ID = "CAT-LINK-012"
EXPECTED_KEYS = {
    "schema",
    "task_id",
    "lane",
    "symbol",
    "isin",
    "prediction_id",
    "prediction_event_hash",
    "prediction_issued_at",
    "source_url",
    "prior_capture",
    "current_capture",
    "feed_progression",
    "feature_record",
    "published_at",
    "disseminated_at",
    "interpretation",
    "later_measured_return",
    "catalyst_contribution",
    "causal_attribution",
    "linked_prediction_count",
    "eligible_catalyst_feature_count",
    "matured_outcome_count",
    "live_trading_enabled",
    "orders_allowed",
    "record_hash",
}


def _instant(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} requires timezone")
    return parsed


def _digest(value: Any, length: int, field: str) -> str:
    text = str(value).lower()
    if not re.fullmatch(rf"[0-9a-f]{{{length}}}", text):
        raise ValueError(f"Invalid {field}")
    return text


def _canonical(record: dict[str, Any]) -> bytes:
    return json.dumps(
        {key: value for key, value in record.items() if key != "record_hash"},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def validate(record: dict[str, Any]) -> dict[str, Any]:
    """Return a compact proof summary or reject hindsight/absence inflation."""
    if not isinstance(record, dict) or set(record) != EXPECTED_KEYS:
        raise ValueError("Feed recheck fields do not match the locked schema")
    if record["schema"] != SCHEMA or record["task_id"] != TASK_ID:
        raise ValueError("Unsupported feed recheck schema or task")
    if record["lane"] != "NEWS_CATALYST":
        raise ValueError("Catalyst evidence cannot be mixed with another lane")
    if record["symbol"] != "MOLBIO" or record["isin"] != "INE869T01028":
        raise ValueError("Unexpected issuer identity")
    _digest(record["prediction_event_hash"], 64, "prediction_event_hash")

    parsed = urlsplit(record["source_url"])
    if (
        parsed.scheme != "https"
        or parsed.hostname != "www.nseindia.com"
        or parsed.path != "/api/corporate-announcements"
        or parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.port not in (None, 443)
    ):
        raise ValueError("Invalid official announcement source URL")

    issued = _instant(record["prediction_issued_at"], "prediction_issued_at")
    prior = record["prior_capture"]
    current = record["current_capture"]
    if not isinstance(prior, dict) or not isinstance(current, dict):
        raise ValueError("Capture records must be objects")
    _digest(prior.get("commit"), 40, "prior commit")
    _digest(prior.get("raw_sha256"), 64, "prior raw_sha256")
    _digest(prior.get("record_hash"), 64, "prior record_hash")
    _digest(current.get("raw_sha256"), 64, "current raw_sha256")
    _digest(current.get("raw_gzip_sha256"), 64, "raw_gzip_sha256")
    _digest(current.get("raw_gzip_git_blob_sha"), 40, "raw_gzip_git_blob_sha")
    prior_observed = _instant(prior.get("first_observed_at"), "prior observed_at")
    current_observed = _instant(current.get("first_observed_at"), "current observed_at")
    request_started = _instant(current.get("request_started_at"), "request_started_at")
    if not issued < prior_observed < request_started <= current_observed:
        raise ValueError("Prediction and source observations are not chronological")
    if current.get("http_status") != 200 or current.get("content_type") != "application/json":
        raise ValueError("Current official feed receipt is invalid")
    if prior.get("exact_symbol_or_isin_matches") != 0 or current.get("exact_symbol_or_isin_matches") != 0:
        raise ValueError("No-match recheck contains an exact match")
    if current.get("captured_feed_rows") != current.get("unique_sequence_ids"):
        raise ValueError("Announcement sequence IDs are not unique")

    progression = record["feed_progression"]
    if not isinstance(progression, dict):
        raise ValueError("feed_progression must be an object")
    if progression.get("prior_exact_rows_removed") != 0:
        raise ValueError("Later feed is not an exact superset")
    if progression.get("prior_exact_rows_preserved") != prior.get("captured_feed_rows"):
        raise ValueError("Prior feed rows were not preserved")
    if (
        progression.get("prior_exact_rows_preserved")
        + progression.get("new_exact_rows_added")
        != current.get("captured_feed_rows")
    ):
        raise ValueError("Feed progression counts do not reconcile")
    if progression.get("new_rows_with_dissemination_at_or_before_prediction") != 0:
        raise ValueError("Later capture contains newly added pre-issue rows")
    if progression.get("new_rows_with_dissemination_after_prediction") != progression.get("new_exact_rows_added"):
        raise ValueError("Added-row dissemination counts do not reconcile")
    if (
        progression.get("full_feed_rows_with_dissemination_at_or_before_prediction")
        + progression.get("full_feed_rows_with_dissemination_after_prediction")
        != current.get("captured_feed_rows")
    ):
        raise ValueError("Full-feed dissemination counts do not reconcile")
    if progression.get("timezone_independently_proven") is not False:
        raise ValueError("NSE API display timezone was overstated")

    feature = record["feature_record"]
    expected_feature_keys = {
        "feature_id", "source_fields", "source_first_observed_at", "missingness",
        "transformation", "version", "reason", "known_by_prediction_issue_time",
        "feature_eligible", "promotion_status",
    }
    if not isinstance(feature, dict) or set(feature) != expected_feature_keys:
        raise ValueError("Feature metadata is incomplete")
    if _instant(feature["source_first_observed_at"], "feature source time") != current_observed:
        raise ValueError("Feature is not bound to the current source observation")
    if feature["known_by_prediction_issue_time"] is not False or feature["feature_eligible"] is not False:
        raise ValueError("Post-issue no-match cannot become a prediction feature")
    if feature["promotion_status"] != "MISSING_NOT_IMPUTED":
        raise ValueError("Missing catalyst feature was silently imputed")
    if feature["version"] != "catalyst-link-v1" or not feature["reason"]:
        raise ValueError("Feature version or reason is missing")

    if record["published_at"] is not None or record["disseminated_at"] is not None:
        raise ValueError("No-match record cannot invent issuer timestamps")
    if "NOT_PROOF_OF_ABSENCE" not in record["interpretation"]:
        raise ValueError("No-match limitation was removed")
    if record["later_measured_return"] is not None:
        raise ValueError("Unmatured catalyst return was invented")
    if record["catalyst_contribution"] != "NOT_PROVEN":
        raise ValueError("Catalyst contribution was invented")
    if record["causal_attribution"] != "NOT_CLAIMED":
        raise ValueError("Causality cannot be inferred")
    if record["linked_prediction_count"] != 1:
        raise ValueError("Linked prediction count changed")
    if record["eligible_catalyst_feature_count"] != 0 or record["matured_outcome_count"] != 0:
        raise ValueError("No-match evidence cannot create a feature or outcome")
    if record["live_trading_enabled"] is not False or record["orders_allowed"] is not False:
        raise ValueError("Unsafe inspection flags")
    if record["record_hash"] != sha256(_canonical(record)).hexdigest():
        raise ValueError("Feed recheck record hash mismatch")

    return {
        "task_id": TASK_ID,
        "status": "POST_ISSUE_FEED_SUPERSET_NO_MATCH_SEALED",
        "prior_rows": prior["captured_feed_rows"],
        "current_rows": current["captured_feed_rows"],
        "new_rows": progression["new_exact_rows_added"],
        "exact_matches": 0,
        "eligible_catalyst_features": 0,
        "linked_predictions": 1,
        "matured_outcomes": 0,
        "catalyst_contribution": "NOT_PROVEN",
        "orders_allowed": False,
    }
