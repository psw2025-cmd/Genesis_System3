"""Validate a post-issue catalyst filing without backfilling or causality claims."""
from __future__ import annotations

from datetime import datetime
import gzip
from hashlib import sha256
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


SCHEMA_VERSION = "catalyst-horizon-filing-v1"
TASK_ID = "CAT-LINK-013"
SYMBOL = "MOLBIO"
ISIN = "INE869T01028"
PREDICTION_ID = "EQ7D-2026-10-01-MOLBIO-V1"
PREDICTION_EVENT_HASH = (
    "91912ef5ef5264cdff60fd06449f355fcd4bfcedc6b743e46c7b6ded7236744f"
)
FEED_URL = (
    "https://www.nseindia.com/api/corporate-announcements?"
    "index=equities&from_date=01-10-2026&to_date=08-10-2026"
)
ATTACHMENT_URL = (
    "https://nsearchives.nseindia.com/corporate/"
    "MOLBIO_08102026131105_Certificate_under_74_5_.pdf"
)
TOP_LEVEL_FIELDS = {
    "schema_version",
    "task_id",
    "lane",
    "symbol",
    "isin",
    "prediction",
    "feed_source",
    "filing",
    "attachment",
    "feature_eligibility",
    "later_horizon_reference",
    "ablation",
    "counts",
    "safety",
    "record_hash",
}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _instant(value: Any, field: str) -> datetime:
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError(f"{field} requires timezone")
    return result


def _safe_file(root: Path, relative: str, field: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe {field} path")
    resolved_root = root.resolve(strict=True)
    resolved = (resolved_root / path).resolve(strict=True)
    if resolved_root not in resolved.parents:
        raise ValueError(f"Unsafe {field} path")
    return resolved


def _approved_url(value: Any, host: str, path: str, field: str) -> str:
    parsed = urlsplit(str(value))
    if (
        parsed.scheme != "https"
        or parsed.hostname != host
        or parsed.path != path
        or parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.port not in (None, 443)
    ):
        raise ValueError(f"Invalid {field} URL")
    return str(value)


def validate(record: dict[str, Any], repo_root: Path = Path(".")) -> dict[str, Any]:
    """Replay retained bytes and enforce point-in-time, attribution and safety limits."""
    if not isinstance(record, dict) or set(record) != TOP_LEVEL_FIELDS:
        raise ValueError("Horizon filing fields do not match the locked schema")
    expected_hash = sha256(
        _canonical({k: v for k, v in record.items() if k != "record_hash"})
    ).hexdigest()
    if record.get("record_hash") != expected_hash:
        raise ValueError("Horizon filing record hash mismatch")
    if (
        record["schema_version"] != SCHEMA_VERSION
        or record["task_id"] != TASK_ID
        or record["lane"] != "NEWS_CATALYST"
        or record["symbol"] != SYMBOL
        or record["isin"] != ISIN
    ):
        raise ValueError("Horizon filing identity changed")

    prediction = record["prediction"]
    issued = _instant(prediction.get("issued_at"), "prediction issued_at")
    if prediction != {
        "prediction_id": PREDICTION_ID,
        "prediction_event_hash": PREDICTION_EVENT_HASH,
        "issued_at": "2026-10-01T12:44:51.984966+00:00",
        "catalyst_feature_included": False,
    }:
        raise ValueError("Prediction anchor changed")

    feed = record["feed_source"]
    if feed.get("url") != FEED_URL:
        raise ValueError("Announcement feed query changed")
    _approved_url(
        feed["url"],
        "www.nseindia.com",
        "/api/corporate-announcements",
        "feed",
    )
    request_started = _instant(feed.get("request_started_at"), "feed request")
    first_observed = _instant(feed.get("first_observed_at"), "feed observation")
    if (
        request_started > first_observed
        or feed.get("http_status") != 200
        or feed.get("content_type") != "application/json"
        or feed.get("exchange_published_at") is not None
    ):
        raise ValueError("Announcement feed receipt changed")
    gzip_path = _safe_file(
        Path(repo_root), feed.get("gzip_path"), "announcement feed"
    )
    compressed = gzip_path.read_bytes()
    if (
        len(compressed) != feed.get("gzip_bytes")
        or sha256(compressed).hexdigest() != feed.get("gzip_sha256")
    ):
        raise ValueError("Retained announcement gzip changed")
    try:
        raw_feed = gzip.decompress(compressed)
        rows = json.loads(raw_feed)
    except (gzip.BadGzipFile, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid retained announcement feed") from exc
    if (
        len(raw_feed) != feed.get("raw_bytes")
        or sha256(raw_feed).hexdigest() != feed.get("raw_sha256")
        or not isinstance(rows, list)
        or len(rows) != feed.get("captured_rows")
    ):
        raise ValueError("Announcement feed measurement changed")
    matches = [
        row
        for row in rows
        if isinstance(row, dict)
        and (
            str(row.get("symbol", "")).strip().upper() == SYMBOL
            or str(row.get("sm_isin", "")).strip().upper() == ISIN
        )
    ]
    if len(matches) != 1 or feed.get("exact_symbol_or_isin_matches") != 1:
        raise ValueError("Exact issuer match count changed")

    filing = record["filing"]
    row = matches[0]
    if (
        filing.get("sequence_id") != row.get("seq_id")
        or filing.get("source_row_sha256") != sha256(_canonical(row)).hexdigest()
        or filing.get("category") != row.get("desc")
        or filing.get("description") != row.get("attchmntText")
        or filing.get("published_at_raw") != row.get("an_dt")
        or filing.get("disseminated_at_raw") != row.get("exchdisstime")
        or filing.get("attachment_url") != row.get("attchmntFile")
    ):
        raise ValueError("Filing row replay changed")
    published = _instant(filing.get("published_at"), "filing published_at")
    disseminated = _instant(
        filing.get("disseminated_at"), "filing disseminated_at"
    )
    if (
        filing.get("timestamp_basis")
        != "NSE_API_DISPLAY_ASSUMED_ASIA_KOLKATA"
        or filing.get("timezone_independently_proven") is not False
        or not issued < published <= disseminated < first_observed
        or filing.get("known_by_prediction_issue_time") is not False
        or filing.get("point_in_time_system_observation_before_outcome_close")
        is not False
    ):
        raise ValueError("Filing time or point-in-time limits changed")

    attachment = record["attachment"]
    if attachment.get("url") != ATTACHMENT_URL:
        raise ValueError("Attachment URL changed")
    _approved_url(
        attachment["url"],
        "nsearchives.nseindia.com",
        "/corporate/MOLBIO_08102026131105_Certificate_under_74_5_.pdf",
        "attachment",
    )
    attachment_observed = _instant(
        attachment.get("first_observed_at"), "attachment observation"
    )
    pdf_path = _safe_file(
        Path(repo_root), attachment.get("path"), "attachment"
    )
    pdf = pdf_path.read_bytes()
    if (
        attachment.get("http_status") != 200
        or attachment.get("content_type") != "application/pdf"
        or attachment_observed < first_observed
        or len(pdf) != attachment.get("bytes")
        or sha256(pdf).hexdigest() != attachment.get("sha256")
        or not pdf.startswith(b"%PDF-")
    ):
        raise ValueError("Retained attachment changed")

    feature = record["feature_eligibility"]
    if feature != {
        "feature_id": "exact_issuer_catalyst_match",
        "version": "catalyst-link-v1",
        "known_by_prediction_issue_time": False,
        "feature_eligible": False,
        "source_backfilled_into_prediction": False,
        "promotion_status": "POST_ISSUE_EVIDENCE_NOT_A_PREDICTION_FEATURE",
    }:
        raise ValueError("Post-issue filing was backfilled or promoted")

    reference = record["later_horizon_reference"]
    if reference != {
        "horizon_session_date": "2026-10-08",
        "raw_unadjusted_equity_return_pct": -2.240434,
        "raw_unadjusted_nifty_50_return_pct": -0.848053,
        "raw_unadjusted_equity_excess_pp": -1.392381,
        "adjusted_outcome_proven": False,
        "performance_metric_status": "NOT_PROVEN_RAW_REFERENCE_ONLY",
        "equity_maturity_record_hash": "d222604fb3df647e1f95373aa642f6d00e21ac6ce2a81d3ecc6a46b28b7f4f9b",
        "equity_commit": "d7f1c184d4a459891d393571386a1db62cf26eff",
    }:
        raise ValueError("Later horizon reference changed")
    if record["ablation"] != {
        "no_catalyst_baseline": True,
        "catalyst_eligible_at_issue": False,
        "valid_ablation_sample_size": 0,
        "catalyst_contribution": "NOT_PROVEN",
        "causal_attribution": "CORRELATION_ONLY_NOT_CAUSAL",
    }:
        raise ValueError("Catalyst ablation or attribution was overstated")
    if record["counts"] != {
        "captured_feed_rows": 3535,
        "exact_horizon_filings": 1,
        "eligible_catalyst_features_at_issue": 0,
        "linked_predictions": 1,
        "matured_adjusted_outcomes": 0,
    }:
        raise ValueError("Catalyst counts changed")
    if record["safety"] != {
        "market_validation_claimed": False,
        "real_money_ready": False,
        "live_trading_enabled": False,
        "orders_allowed": False,
    }:
        raise ValueError("Unsafe catalyst state")
    return {
        "task_id": TASK_ID,
        "status": "POST_ISSUE_HORIZON_FILING_RETAINED_NOT_BACKFILLED",
        "exact_horizon_filings": 1,
        "eligible_catalyst_features_at_issue": 0,
        "matured_adjusted_outcomes": 0,
        "catalyst_contribution": "NOT_PROVEN",
        "orders_allowed": False,
    }
