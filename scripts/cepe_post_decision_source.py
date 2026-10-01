"""Validate an official CE/PE source first observed after a locked decision."""
from __future__ import annotations

from datetime import date, datetime
from hashlib import sha256
import json
import re
from typing import Any
from urllib.parse import urlsplit


SCHEMA = "cepe-post-decision-source-v1"
TASK_ID = "CEPE-SOURCE-015"
ARCHIVE_URL = (
    "https://nsearchives.nseindia.com/content/fo/"
    "BhavCopy_NSE_FO_0_0_0_20261001_F_0000.csv.zip"
)
TARGET_OPEN_AT = "2026-10-05T09:15:00+05:30"
CALENDAR_URL = "https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf"
CALENDAR_SHA256 = "5a2079cd78b2e6b536ef0d28300e63b645721bed22cc82a91facf5945f3296ea"
EXPECTED_TOP_LEVEL = {
    "schema",
    "task_id",
    "lane",
    "evidence_as_of",
    "source_session_date",
    "target_open_at",
    "target_session",
    "prior_decision_lock",
    "availability_timeline",
    "official_archive",
    "mechanical_universe",
    "feature_registry",
    "forward_state",
    "gate_status",
    "interpretation",
    "opening_price_is_executable_fill",
    "fees_slippage_applied",
    "real_money_ready",
    "live_trading_enabled",
    "orders_allowed",
}
REQUIRED_FEATURES = {
    "exact_contract_identity",
    "option_close",
    "option_ohl",
    "prior_close",
    "traded_volume",
    "open_interest",
    "change_in_open_interest",
    "underlying_price",
    "settlement_price",
    "board_lot_quantity",
    "close_volume_liquidity_screen",
    "implied_volatility",
    "greeks_delta_gamma_theta_vega",
    "bid_ask_spread",
    "fees_and_slippage",
}


def _instant(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include timezone")
    return parsed


def _sha(value: Any, length: int, field: str) -> str:
    text = str(value).lower()
    if not re.fullmatch(rf"[0-9a-f]{{{length}}}", text):
        raise ValueError(f"Invalid {field}")
    return text


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def validate(payload: dict[str, Any]) -> dict[str, Any]:
    """Return an auditable summary or reject chronology/provenance inflation."""
    if not isinstance(payload, dict) or set(payload) != EXPECTED_TOP_LEVEL:
        raise ValueError("Source receipt fields do not match the locked schema")
    if payload["schema"] != SCHEMA or payload["task_id"] != TASK_ID:
        raise ValueError("Unsupported source schema or task")
    if payload["lane"] != "CEPE_NEXT_OPEN":
        raise ValueError("CE/PE evidence cannot be mixed with another lane")

    try:
        source_day = date.fromisoformat(str(payload["source_session_date"]))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid source_session_date") from exc
    evidence_as_of = _instant(payload["evidence_as_of"], "evidence_as_of")
    target_open = _instant(payload["target_open_at"], "target_open_at")
    if not source_day < target_open.date() or not evidence_as_of < target_open:
        raise ValueError("Source session and target opening are not chronological")
    if payload["target_open_at"] != TARGET_OPEN_AT:
        raise ValueError("Target opening is not the next eligible NSE F&O session")

    target_session = payload["target_session"]
    expected_target_session_fields = {
        "segment",
        "calendar_source_url",
        "calendar_source_sha256",
        "calendar_source_first_observed_at",
        "calendar_source_published_date",
        "calendar_source_circular",
        "official_holiday_date",
        "official_holiday_reason",
        "weekend_dates",
        "next_eligible_session_date",
        "opening_time_basis",
    }
    if not isinstance(target_session, dict) or set(target_session) != expected_target_session_fields:
        raise ValueError("Target-session evidence is incomplete")
    if target_session["segment"] != "FO":
        raise ValueError("Target-session calendar is not for NSE F&O")
    calendar_url = str(target_session["calendar_source_url"])
    calendar_source = urlsplit(calendar_url)
    if (
        calendar_url != CALENDAR_URL
        or calendar_source.scheme != "https"
        or calendar_source.hostname != "nsearchives.nseindia.com"
        or calendar_source.username
        or calendar_source.password
        or calendar_source.fragment
        or calendar_source.port not in (None, 443)
    ):
        raise ValueError("Target-session calendar source is not the exact official NSE circular")
    if _sha(target_session["calendar_source_sha256"], 64, "calendar source") != CALENDAR_SHA256:
        raise ValueError("Target-session calendar source hash changed")
    calendar_observed = _instant(
        target_session["calendar_source_first_observed_at"],
        "calendar_source_first_observed_at",
    )
    if calendar_observed >= evidence_as_of:
        raise ValueError("Target-session calendar was not observed before the source receipt")
    if (
        target_session["calendar_source_published_date"] != "2025-12-12"
        or target_session["calendar_source_circular"] != "NSE/FAOP/71777"
    ):
        raise ValueError("Target-session circular identity changed")
    if (
        target_session["official_holiday_date"] != "2026-10-02"
        or target_session["official_holiday_reason"] != "Mahatma Gandhi Jayanti"
    ):
        raise ValueError("Official F&O holiday evidence changed")
    if target_session["weekend_dates"] != ["2026-10-03", "2026-10-04"]:
        raise ValueError("Intervening weekend dates changed")
    if (
        target_session["next_eligible_session_date"] != "2026-10-05"
        or target_open.date().isoformat() != target_session["next_eligible_session_date"]
    ):
        raise ValueError("Next eligible F&O session does not match target opening")
    if target_session["opening_time_basis"] != "REGULAR_SESSION_ASSUMPTION_NOT_EXECUTABLE_FILL":
        raise ValueError("Target opening basis was overstated")

    lock = payload["prior_decision_lock"]
    if not isinstance(lock, dict):
        raise ValueError("prior_decision_lock must be an object")
    _sha(lock.get("commit"), 40, "prior decision commit")
    decision_at = _instant(lock.get("decision_issued_at"), "decision_issued_at")
    email_at = _instant(lock.get("email_sent_at"), "email_sent_at")
    if lock.get("decision") != "NO_VERIFIED_SIGNAL" or not decision_at <= email_at:
        raise ValueError("Prior decision chronology is invalid")
    if lock.get("source_status_at_decision") != "NOT_OBTAINED":
        raise ValueError("Prior decision source state was rewritten")
    if lock.get("source_status_at_email") != "NOT_OBTAINED":
        raise ValueError("Email source state was rewritten")
    if lock.get("decision_rewrite_allowed") is not False:
        raise ValueError("Post-decision data cannot rewrite the decision")
    if lock.get("second_email_allowed") is not False:
        raise ValueError("Post-decision data cannot authorize a second email")

    timeline = payload["availability_timeline"]
    if not isinstance(timeline, list) or len(timeline) != 4:
        raise ValueError("Exactly four availability observations are required")
    if any(not isinstance(item, dict) for item in timeline):
        raise ValueError("Availability observations must be objects")
    times = [_instant(item.get("observed_at"), "availability observed_at") for item in timeline]
    if times != sorted(times):
        raise ValueError("Availability timeline is not chronological")
    if evidence_as_of != times[-1]:
        raise ValueError("evidence_as_of must equal the completed repeat observation")
    repeat_started = _instant(
        timeline[3].get("request_started_at"), "repeat request_started_at"
    )
    if not times[2] < repeat_started <= times[3]:
        raise ValueError("Repeat retrieval chronology is invalid")
    if [item.get("http_status") for item in timeline] != [404, 404, 200, 200]:
        raise ValueError("Availability status sequence changed")
    if [item.get("response_bytes") for item in timeline] != [3425, 3425, 1048928, 1048928]:
        raise ValueError("Availability response byte counts changed")
    if [item.get("content_type") for item in timeline] != [
        "text/html;charset=UTF-8",
        "text/html;charset=UTF-8",
        "application/zip",
        "application/zip",
    ]:
        raise ValueError("Availability content types changed")
    for item in timeline:
        _sha(item.get("response_sha256"), 64, "response_sha256")
    if not times[1] < email_at < times[2]:
        raise ValueError("Successful source observation was not after the locked email")
    if timeline[0]["response_sha256"] != timeline[1]["response_sha256"]:
        raise ValueError("Pre-email 404 receipts do not match")
    if timeline[2]["response_sha256"] != timeline[3]["response_sha256"]:
        raise ValueError("Successful repeat retrieval is not byte-identical")
    if timeline[3].get("byte_identical_to_first_success") is not True:
        raise ValueError("Repeat retrieval proof is missing")

    archive = payload["official_archive"]
    if not isinstance(archive, dict):
        raise ValueError("official_archive must be an object")
    archive_url = str(archive.get("url", ""))
    parsed = urlsplit(archive_url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "nsearchives.nseindia.com"
        or parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.port not in (None, 443)
    ):
        raise ValueError("Archive URL is not the official NSE archive host")
    if archive_url != ARCHIVE_URL:
        raise ValueError("Archive URL is not the exact official session source")
    _sha(archive.get("zip_sha256"), 64, "zip_sha256")
    _sha(archive.get("csv_sha256"), 64, "csv_sha256")
    _sha(archive.get("raw_zip_git_blob_sha"), 40, "raw_zip_git_blob_sha")
    if archive.get("zip_sha256") != timeline[2]["response_sha256"]:
        raise ValueError("Archive hash is not bound to the successful retrieval")
    if archive.get("zip_bytes") != 1048928 or archive.get("csv_bytes") != 6044690:
        raise ValueError("Archive or CSV byte count changed")
    if archive.get("raw_zip_path") != "research/evidence/cepe/raw/fo_20261001.zip":
        raise ValueError("Raw archive path changed")
    if archive.get("member") != "BhavCopy_NSE_FO_0_0_0_20261001_F_0000.csv":
        raise ValueError("Archive member name changed")
    if archive.get("source_rows") != 33250:
        raise ValueError("Unexpected source row count")
    if archive.get("trade_date") != source_day.isoformat() or archive.get("segment") != "FO":
        raise ValueError("Source date or segment mismatch")
    if archive.get("date_source_segment_checks") != "PASS":
        raise ValueError("Date/source/segment checks did not pass")
    if archive.get("duplicate_rows_by_instrument_id") != 0:
        raise ValueError("Duplicate instrument rows detected")
    if archive.get("exchange_publication_time") is not None:
        raise ValueError("Server headers cannot invent exchange dissemination time")
    if archive.get("header_time_is_exchange_dissemination_time") is not False:
        raise ValueError("Server header was promoted to exchange dissemination time")
    if archive.get("member_timestamp_used_as_availability_proof") is not False:
        raise ValueError("ZIP member timestamp cannot prove availability")
    if _instant(archive.get("server_date_header"), "server date") != times[3]:
        raise ValueError("Server date is not bound to the repeat observation")
    if not email_at < _instant(archive.get("server_last_modified_header"), "last-modified") < times[2]:
        raise ValueError("Server last-modified chronology is inconsistent")

    universe = payload["mechanical_universe"]
    if not isinstance(universe, dict):
        raise ValueError("mechanical_universe must be an object")
    if universe.get("option_rows") != 32597:
        raise ValueError("Unexpected option row count")
    if universe.get("ce_rows") + universe.get("pe_rows") != universe.get("option_rows"):
        raise ValueError("CE/PE row counts do not reconcile")
    if universe.get("unique_exact_contract_keys") != universe.get("option_rows"):
        raise ValueError("Exact option contract keys are not unique")
    if universe.get("duplicate_exact_contract_rows") != 0:
        raise ValueError("Duplicate exact contracts detected")
    if universe.get("positive_volume_rows") + universe.get("zero_volume_rows") != universe.get("option_rows"):
        raise ValueError("Volume counts do not reconcile")
    if universe.get("screen_is_prediction") is not False:
        raise ValueError("Mechanical screen cannot be called a prediction")
    if universe.get("screen_is_strategy_qualification") is not False:
        raise ValueError("Mechanical screen cannot qualify the strategy")

    features = payload["feature_registry"]
    if not isinstance(features, list):
        raise ValueError("feature_registry must be a list")
    by_id = {item.get("feature_id"): item for item in features if isinstance(item, dict)}
    if set(by_id) != REQUIRED_FEATURES or len(features) != len(REQUIRED_FEATURES):
        raise ValueError("Feature registry is incomplete or duplicated")
    first_success = times[2]
    for feature_id, feature in by_id.items():
        required = {
            "feature_id", "source_fields", "available", "source_observed_at",
            "missing_count", "zero_count", "transformation", "version", "reason",
            "promotion_status",
        }
        if set(feature) != required:
            raise ValueError(f"Feature metadata is incomplete: {feature_id}")
        if _instant(feature["source_observed_at"], "feature source_observed_at") != first_success:
            raise ValueError("Feature timestamp is not bound to source observation")
        if feature["version"] != "cepe-source-v1" or not feature["reason"]:
            raise ValueError("Feature version or reason is missing")
        if feature["available"] is False:
            if (
                feature["missing_count"] != universe["option_rows"]
                or feature["transformation"] != "NOT_AVAILABLE_IN_SOURCE"
                or feature["promotion_status"] != "MISSING_NOT_IMPUTED"
            ):
                raise ValueError("Unavailable feature was silently imputed")
        elif feature["missing_count"] != 0:
            raise ValueError("Available feature has unexpected missing values")

    forward = payload["forward_state"]
    if not isinstance(forward, dict):
        raise ValueError("forward_state must be an object")
    zero_fields = (
        "qualified_candidates", "issued_contract_forecasts", "matured_forward_outcomes",
        "positive_forecasts", "negative_forecasts",
    )
    if any(forward.get(field) != 0 for field in zero_fields):
        raise ValueError("Post-email source cannot create a forecast")
    if forward.get("expected_premium_move_range") is not None:
        raise ValueError("Unqualified source cannot create a premium range")
    if forward.get("uncertainty") != "NOT_PROVEN":
        raise ValueError("Uncertainty must remain NOT_PROVEN")
    if forward.get("post_email_source_backfilled_into_prior_decision") is not False:
        raise ValueError("Post-email source was backfilled into the prior decision")
    if forward.get("historical_screen_promoted_to_forecast") is not False:
        raise ValueError("Mechanical screen was promoted to forecast")

    gates = payload["gate_status"]
    if not isinstance(gates, dict):
        raise ValueError("gate_status must be an object")
    expected_targets = {
        "minimum_oos_trades": 100,
        "minimum_oos_days": 60,
        "minimum_directional_accuracy": 0.65,
        "minimum_top_decile_precision": 0.70,
        "minimum_sharpe": 2.5,
        "maximum_drawdown": 0.10,
        "minimum_deflated_sharpe_probability": 0.95,
    }
    if any(gates.get(field) != value for field, value in expected_targets.items()):
        raise ValueError("Project gate thresholds changed")
    if gates.get("valid_forward_trades") != 0 or gates.get("valid_forward_days") != 0:
        raise ValueError("Forward sample was fabricated")
    if any(
        gates.get(field) is not None
        for field in (
            "directional_accuracy",
            "top_decile_precision",
            "sharpe",
            "max_drawdown",
            "deflated_sharpe_probability",
        )
    ):
        raise ValueError("Unevaluated forward metrics must remain null")
    if gates.get("strategy_promoted") is not False or gates.get("frozen_test_retuned") is not False:
        raise ValueError("Failed strategy cannot be promoted or retuned")

    for field in (
        "opening_price_is_executable_fill",
        "fees_slippage_applied",
        "real_money_ready",
        "live_trading_enabled",
        "orders_allowed",
    ):
        if payload[field] is not False:
            raise ValueError(f"Unsafe or dishonest flag: {field}")

    return {
        "task_id": TASK_ID,
        "status": "OFFICIAL_SOURCE_CAPTURED_AFTER_LOCKED_ABSTENTION",
        "source_session_date": source_day.isoformat(),
        "target_open_at": target_open.isoformat(),
        "first_successfully_observed_at": times[2].isoformat(),
        "zip_sha256": archive["zip_sha256"],
        "csv_sha256": archive["csv_sha256"],
        "option_rows": universe["option_rows"],
        "mechanically_screened_observations": universe["close_ge_1_and_volume_ge_100_rows"],
        "qualified_candidates": 0,
        "issued_contract_forecasts": 0,
        "matured_forward_outcomes": 0,
        "second_email_allowed": False,
        "receipt_sha256": sha256(_canonical(payload)).hexdigest(),
        "orders_allowed": False,
    }
