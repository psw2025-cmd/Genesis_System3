"""Build an immutable, fail-closed equity maturity observation.

This adapter binds a direction-only forecast to retained NSE cash, index,
instrument-master and corporate-action bytes.  It deliberately records a raw
reference observation without promoting it to an adjusted outcome or a
performance metric.
"""
from __future__ import annotations

import csv
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import StringIO
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen

from dashboard.backend.multibagger_ledger import (
    LedgerError,
    _ledger_lock,
    _retained_snapshot_digest,
    _snapshot_reference,
)
from dashboard.backend.multibagger_outcome import (
    OutcomeLedgerError,
    reconcile_directional_reference,
    validate_directional_outcome_projection,
    verify_directional_projection_evidence,
)
from scripts.equity_corporate_action_scope import capture as capture_actions
from scripts.equity_corporate_action_scope import review as review_actions
from scripts.equity_instrument_scope import (
    EQUITY_URL,
    ETF_URL,
    VERSION as INSTRUMENT_SCOPE_VERSION,
    capture as capture_instruments,
)
from scripts.equity_forward_prediction import (
    GENESIS_HASH as FORWARD_PREDICTION_GENESIS_HASH,
    validate_prediction as validate_forward_prediction,
)


SCHEMA_VERSION = "equity-directional-maturity-observation-v1"
INDEX_URL_PREFIX = (
    "https://nsearchives.nseindia.com/content/indices/ind_close_all_"
)
CM_URL_PREFIX = "https://nsearchives.nseindia.com/content/cm/"
SOURCE_ROLES = {"outcome_cash", "company", "etf", "actions", "index"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_OBSERVATION_URI_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
_OBSERVATION_URI_PREFIX = "research/forward/equity/"
_ISIN_RE = re.compile(r"^IN[A-Z0-9]{10}$")
_SYMBOL_RE = re.compile(r"^[A-Z0-9][A-Z0-9&.-]{0,39}$")
_RECEIPT_FIELDS = {
    "url",
    "final_url",
    "http_status",
    "first_observed_at",
    "exchange_published_at",
    "sha256",
    "bytes",
    "snapshot_uri",
}
_IDENTITY_REVIEW_FIELDS = {
    "symbol",
    "isin",
    "classification",
    "snapshot_digest",
    "scope",
    "identity_change_proven",
}
_ACTION_REVIEW_FIELDS = {
    "action_count",
    "events",
    "identity_link_review_required",
    "requested_interval_covered",
    "status",
    "source_sha256",
    "adjusted_return_proven",
    "use_as_historical_prediction_feature_allowed",
    "complete_action_coverage",
    "raw_records",
    "unique_records",
}
_BENCHMARK_FIELDS = {
    "name",
    "outcome_session_date",
    "entry_reference_close",
    "outcome_reference_close",
    "raw_return_pct",
    "price_basis",
    "source_row_sha256",
    "performance_metric_status",
    "raw_unadjusted_equity_excess_pp",
}
_RAW_REFERENCE_FIELDS = {
    "status",
    "prediction_id",
    "prediction_event_hash",
    "projection_hash",
    "symbol",
    "isin",
    "forecast_kind",
    "forecast_direction",
    "issued_at",
    "due_at",
    "outcome_price_as_of_at",
    "outcome_source_exchange_published_at",
    "outcome_source_first_observed_at",
    "source_availability_status",
    "entry_reference_close",
    "outcome_reference_close",
    "predicted_return_pct",
    "expected_return_range",
    "calibrated_probability",
    "raw_actual_return_pct",
    "raw_reference_direction",
    "actual_return_pct",
    "absolute_error_pp",
    "direction_correct",
    "entry_source_hash",
    "entry_source_row_hash",
    "entry_snapshot_uri",
    "outcome_source",
    "outcome_source_url",
    "outcome_source_hash",
    "outcome_source_size_bytes",
    "outcome_source_row_hash",
    "outcome_snapshot_uri",
    "price_basis",
    "adjustment_status",
    "adjustment_basis",
    "matured_outcomes",
    "market_validation_claimed",
    "reference_prices_are_executable_fills",
    "performance_metrics_available",
    "performance_gate_passed",
    "real_money_ready",
    "live_trading_enabled",
    "order_placement_allowed",
}
_IDENTITY_CLASSIFICATIONS = {
    "COMPANY_EQ_IDENTITY_MATCHED",
    "ETF_EXCLUDED",
    "COMPANY_NON_EQ_SERIES_EXCLUDED",
    "NOT_PROVEN_SOURCE_NOT_YET_OBSERVED",
    "NOT_PROVEN_REFRESH_REQUIRED",
    "NOT_PROVEN_UNKNOWN_IDENTITY",
}
RECORD_FIELDS = {
    "schema_version",
    "task_id",
    "prediction_id",
    "prediction_event_hash",
    "projection_hash",
    "recorded_at",
    "source_cutoff_at",
    "source_receipts",
    "identity_review",
    "corporate_action_review",
    "raw_reference",
    "benchmark_raw_reference",
    "final_outcome_status",
    "final_outcome_blockers",
    "counts",
    "market_validation_claimed",
    "performance_metrics_available",
    "performance_gate_passed",
    "real_money_ready",
    "live_trading_enabled",
    "order_placement_allowed",
    "record_hash",
}
MATURITY_LEDGER_SCHEMA_VERSION = "equity-maturity-observation-ledger-v1"
MATURITY_LEDGER_GENESIS_HASH = "0" * 64
_MATURITY_LEDGER_EVENT_TYPE = "EQUITY_MATURITY_OBSERVATION_RECORDED"
_MAX_MATURITY_OBSERVATION_BYTES = 2 * 1024 * 1024
_MAX_ANCHOR_ARTIFACT_BYTES = 2 * 1024 * 1024
_MAX_ANCHOR_SOURCE_BYTES = 32 * 1024 * 1024
_MAX_ISSUANCE_MANIFEST_BYTES = 2 * 1024 * 1024
_ANCHOR_ARTIFACT_FIELDS = {"prediction_uri", "projection_uri"}
ISSUANCE_MANIFEST_SCHEMA_VERSION = "equity-issuance-artifact-ledger-v1"
ISSUANCE_MANIFEST_GENESIS_HASH = "0" * 64
_ISSUANCE_MANIFEST_EVENT_TYPE = "EQUITY_ISSUANCE_ARTIFACTS_REGISTERED"
_ISSUANCE_MANIFEST_FIELDS = {
    "schema_version", "event_type", "prediction_id",
    "prediction_event_hash", "prediction_uri",
    "prediction_file_sha256", "prediction_size_bytes",
    "projection_hash", "projection_uri", "projection_file_sha256",
    "projection_size_bytes", "issued_at", "due_at", "registered_at",
    "registration_status", "pre_maturity_registered", "previous_hash",
    "market_validation_claimed", "performance_metrics_available",
    "real_money_ready", "live_trading_enabled", "order_placement_allowed",
    "event_hash",
}
PUBLICATION_RECEIPT_SCHEMA_VERSION = (
    "equity-external-publication-receipt-ledger-v1"
)
PUBLICATION_RECEIPT_GENESIS_HASH = "0" * 64
_PUBLICATION_RECEIPT_EVENT_TYPE = (
    "EQUITY_ISSUANCE_EXTERNALLY_PUBLISHED"
)
_MAX_PUBLICATION_RECEIPT_BYTES = 2 * 1024 * 1024
_PUBLICATION_RECEIPT_FIELDS = {
    "schema_version", "event_type", "prediction_id",
    "issuance_manifest_event_hash", "prediction_event_hash",
    "projection_hash", "due_at", "provider", "repository",
    "pull_request_number", "comment_id", "author_login",
    "published_at", "source_updated_at", "first_observed_at",
    "source_url", "source_html_url", "source_snapshot_uri",
    "source_sha256", "source_size_bytes", "attestation_sha256",
    "publication_status", "forward_oos_eligible", "previous_hash",
    "market_validation_claimed", "performance_metrics_available",
    "real_money_ready", "live_trading_enabled",
    "order_placement_allowed", "event_hash",
}
_PUBLICATION_ATTESTATION_SCHEMA_VERSION = (
    "equity-publication-attestation-v1"
)
_PUBLICATION_ATTESTATION_FIELDS = {
    "schema_version", "prediction_id", "issuance_manifest_event_hash",
    "prediction_event_hash", "projection_hash", "registered_at",
    "due_at", "execution_mode", "market_validation_claimed",
    "live_trading_enabled", "order_placement_allowed",
}
_PUBLICATION_BODY_PREFIX = "GENESIS_SYSTEM3_EQUITY_PUBLICATION_V1\n"
_PUBLICATION_PROVIDER = "GITHUB_ISSUE_COMMENT"
_PUBLICATION_REPOSITORY = "psw2025-cmd/Genesis_System3"
_PUBLICATION_PULL_REQUEST = 471
_PUBLICATION_AUTHOR_LOGIN = "psw2025-cmd"
_GITHUB_API_VERSION = "2022-11-28"
_GITHUB_PUBLICATION_USER_AGENT = "Genesis-System3-equity-publication-v1"
_MATURITY_LEDGER_FIELDS = {
    "schema_version",
    "event_type",
    "prediction_id",
    "prediction_event_hash",
    "projection_hash",
    "observation_record_hash",
    "observation_file_sha256",
    "observation_size_bytes",
    "observation_uri",
    "recorded_at",
    "source_cutoff_at",
    "final_outcome_status",
    "raw_reference_observations",
    "matured_adjusted_outcomes",
    "adjusted_actual_return_pct",
    "direction_correct",
    "calibration_error",
    "previous_hash",
    "market_validation_claimed",
    "performance_metrics_available",
    "performance_gate_passed",
    "real_money_ready",
    "live_trading_enabled",
    "order_placement_allowed",
    "event_hash",
}


class MaturityObservationError(ValueError):
    """Raised when maturity evidence is incomplete or internally inconsistent."""


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _time(value: Any, field: str) -> datetime:
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise MaturityObservationError(f"{field}_INVALID") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise MaturityObservationError(f"{field}_TIMEZONE_REQUIRED")
    return result.astimezone(timezone.utc)


def _system_utc_now() -> datetime:
    """Return the registration time used by prospective issuance."""
    return datetime.now(timezone.utc)


def _positive_decimal(value: Any, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise MaturityObservationError(f"{field}_INVALID") from exc
    if not result.is_finite() or result <= 0:
        raise MaturityObservationError(f"{field}_INVALID")
    return result


def _finite_decimal(value: Any, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise MaturityObservationError(f"{field}_INVALID") from exc
    if not result.is_finite():
        raise MaturityObservationError(f"{field}_INVALID")
    return result


def _sha(value: Any, field: str) -> str:
    digest = str(value).strip()
    if digest != value or not _SHA256_RE.fullmatch(digest):
        raise MaturityObservationError(f"{field}_INVALID")
    return digest


def _rehash_without(record: Mapping[str, Any], field: str) -> str:
    return sha256(_canonical({key: value for key, value in record.items() if key != field})).hexdigest()


def _observation_reference(value: Any, field: str) -> str:
    """Accept only a repository-relative retained equity observation path."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 512
        or not _OBSERVATION_URI_RE.fullmatch(value)
    ):
        raise MaturityObservationError(f"{field}_INVALID")
    if any(segment in {"", ".", ".."} for segment in value.split("/")):
        raise MaturityObservationError(f"{field}_INVALID")
    if not value.startswith(_OBSERVATION_URI_PREFIX):
        raise MaturityObservationError(f"{field}_UNAPPROVED_PREFIX")
    return value


def _retained_snapshot_reference(value: Any, field: str) -> str:
    try:
        return _snapshot_reference(value, field)
    except LedgerError as exc:
        raise MaturityObservationError(str(exc)) from exc


def _verify_receipt(
    raw: bytes,
    receipt: Mapping[str, Any],
    *,
    expected_url: str,
    snapshot_uri: str,
    current: datetime,
) -> tuple[dict[str, Any], datetime]:
    parsed = urlsplit(expected_url)
    if (
        not isinstance(raw, bytes)
        or not raw
        or parsed.scheme != "https"
        or parsed.hostname not in {
            "nsearchives.nseindia.com",
            "www.nseindia.com",
        }
        or parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.port not in (None, 443)
        or receipt.get("url") != expected_url
        or receipt.get("final_url") != expected_url
        or receipt.get("http_status") != 200
        or receipt.get("raw_sha256") != sha256(raw).hexdigest()
        or receipt.get("bytes") != len(raw)
        or receipt.get("exchange_published_at") is not None
    ):
        raise MaturityObservationError("OFFICIAL_SOURCE_RECEIPT_MISMATCH")
    observed = _time(receipt.get("first_observed_at"), "FIRST_OBSERVED_AT")
    if observed > current:
        raise MaturityObservationError("SOURCE_OBSERVED_AFTER_RECORDING")
    try:
        retained = _snapshot_reference(snapshot_uri, "SNAPSHOT_URI")
    except LedgerError as exc:
        raise MaturityObservationError(str(exc)) from exc
    return (
        {
            "url": expected_url,
            "final_url": expected_url,
            "http_status": 200,
            "first_observed_at": observed.isoformat(),
            "exchange_published_at": None,
            "sha256": sha256(raw).hexdigest(),
            "bytes": len(raw),
            "snapshot_uri": retained,
        },
        observed,
    )


def _benchmark_reference(
    raw: bytes,
    *,
    session: date,
    entry_close: Any,
) -> dict[str, Any]:
    try:
        reader = csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    except UnicodeDecodeError as exc:
        raise MaturityObservationError("INDEX_ENCODING_INVALID") from exc
    required = {
        "Index Name",
        "Index Date",
        "Open Index Value",
        "High Index Value",
        "Low Index Value",
        "Closing Index Value",
    }
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)) or not required.issubset(fields):
        raise MaturityObservationError("INDEX_SCHEMA_INVALID")
    matches = [
        row
        for row in reader
        if row["Index Name"] == "Nifty 50"
        and row["Index Date"] == session.strftime("%d-%m-%Y")
    ]
    if len(matches) != 1:
        raise MaturityObservationError("INDEX_ROW_MISSING_OR_DUPLICATED")
    row = matches[0]
    values = {
        field: _positive_decimal(row[field], field)
        for field in (
            "Open Index Value",
            "High Index Value",
            "Low Index Value",
            "Closing Index Value",
        )
    }
    if not values["Low Index Value"] <= min(
        values["Open Index Value"], values["Closing Index Value"]
    ) <= max(
        values["Open Index Value"], values["Closing Index Value"]
    ) <= values["High Index Value"]:
        raise MaturityObservationError("INDEX_OHLC_INVALID")
    entry = _positive_decimal(entry_close, "INDEX_ENTRY_CLOSE")
    close = values["Closing Index Value"]
    raw_return = (close / entry - Decimal("1")) * Decimal("100")
    return {
        "name": "Nifty 50",
        "outcome_session_date": session.isoformat(),
        "entry_reference_close": str(entry),
        "outcome_reference_close": str(close),
        "raw_return_pct": round(float(raw_return), 6),
        "price_basis": "UNADJUSTED_EXCHANGE_REFERENCE",
        "source_row_sha256": sha256(_canonical(row)).hexdigest(),
        "performance_metric_status": (
            "RAW_REFERENCE_ONLY_EQUITY_ADJUSTMENT_NOT_PROVEN"
        ),
    }


def build_maturity_observation(
    sealed_prediction: dict[str, Any],
    projection: dict[str, Any],
    *,
    entry_source_snapshot: bytes,
    outcome_close: str,
    source_bytes: Mapping[str, bytes],
    source_receipts: Mapping[str, Mapping[str, Any]],
    source_snapshot_uris: Mapping[str, str],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Bind exact maturity sources while leaving the adjusted outcome unscored."""
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise MaturityObservationError("NOW_TIMEZONE_REQUIRED")
    current = current.astimezone(timezone.utc)
    try:
        validate_directional_outcome_projection(projection)
    except OutcomeLedgerError as exc:
        raise MaturityObservationError(str(exc)) from exc
    if (
        sealed_prediction.get("prediction_id") != projection["prediction_id"]
        or sealed_prediction.get("event_hash")
        != projection["prediction_event_hash"]
        or sealed_prediction.get("prediction", {}).get("symbol")
        != projection["symbol"]
        or sealed_prediction.get("prediction", {}).get("isin")
        != projection["isin"]
        or sealed_prediction.get("due_session_date")
        != projection["due_session_date"]
    ):
        raise MaturityObservationError("PREDICTION_PROJECTION_ANCHOR_MISMATCH")
    if (
        set(source_bytes) != SOURCE_ROLES
        or set(source_receipts) != SOURCE_ROLES
        or set(source_snapshot_uris) != SOURCE_ROLES
    ):
        raise MaturityObservationError("MATURITY_SOURCE_ROLES_INVALID")

    outcome_day = date.fromisoformat(projection["due_session_date"])
    urls = {
        "outcome_cash": (
            CM_URL_PREFIX
            + "BhavCopy_NSE_CM_0_0_0_"
            + outcome_day.strftime("%Y%m%d")
            + "_F_0000.csv.zip"
        ),
        "company": EQUITY_URL,
        "etf": ETF_URL,
        "actions": source_receipts["actions"].get("url"),
        "index": INDEX_URL_PREFIX + outcome_day.strftime("%d%m%Y") + ".csv",
    }
    verified_receipts: dict[str, dict[str, Any]] = {}
    observed: dict[str, datetime] = {}
    for role in sorted(SOURCE_ROLES):
        url = urls[role]
        if not isinstance(url, str):
            raise MaturityObservationError("MATURITY_SOURCE_URL_INVALID")
        verified_receipts[role], observed[role] = _verify_receipt(
            source_bytes[role],
            source_receipts[role],
            expected_url=url,
            snapshot_uri=source_snapshot_uris[role],
            current=current,
        )
    due = _time(projection["due_at"], "DUE_AT")
    if any(timestamp < due for timestamp in observed.values()):
        raise MaturityObservationError("MATURITY_SOURCE_OBSERVED_BEFORE_DUE")

    cash_receipt = verified_receipts["outcome_cash"]
    raw_reference = reconcile_directional_reference(
        projection,
        {
            "symbol": projection["symbol"],
            "isin": projection["isin"],
            "price_as_of_at": projection["due_at"],
            "source_exchange_published_at": None,
            "source_first_observed_at": cash_receipt["first_observed_at"],
            "reference_close": outcome_close,
            "source": "NSE",
            "source_url": cash_receipt["url"],
            "source_hash": cash_receipt["sha256"],
            "source_snapshot": source_bytes["outcome_cash"],
            "source_snapshot_uri": cash_receipt["snapshot_uri"],
            "price_basis": "UNADJUSTED_EXCHANGE_REFERENCE",
        },
        entry_source_snapshot=entry_source_snapshot,
        now=current,
    )
    if raw_reference.get("status") != (
        "RAW_REFERENCE_OBSERVED_ADJUSTMENT_REVIEW_PENDING"
    ):
        raise MaturityObservationError(
            "RAW_REFERENCE_" + raw_reference.get("reason", "NOT_PROVEN")
        )

    identity = capture_instruments(
        source_bytes["company"],
        source_bytes["etf"],
        equity_receipt={
            "url": verified_receipts["company"]["url"],
            "raw_sha256": verified_receipts["company"]["sha256"],
            "first_observed_at": verified_receipts["company"][
                "first_observed_at"
            ],
        },
        etf_receipt={
            "url": verified_receipts["etf"]["url"],
            "raw_sha256": verified_receipts["etf"]["sha256"],
            "first_observed_at": verified_receipts["etf"][
                "first_observed_at"
            ],
        },
    )
    source_cutoff = max(observed.values())
    classification = identity.classify(
        projection["symbol"],
        projection["isin"],
        issued_at=source_cutoff.isoformat(),
    )
    identity_review = {
        "symbol": projection["symbol"],
        "isin": projection["isin"],
        "classification": classification,
        "snapshot_digest": identity.receipt_sha256,
        "scope": (
            "CURRENT_MASTER_AT_OBSERVATION_NOT_POINT_IN_TIME_MATURITY"
        ),
        "identity_change_proven": False,
    }

    actions = capture_actions(
        source_bytes["actions"],
        {
            "source_url": verified_receipts["actions"]["url"],
            "raw_sha256": verified_receipts["actions"]["sha256"],
            "first_observed_at": verified_receipts["actions"][
                "first_observed_at"
            ],
        },
    )
    action_review = review_actions(
        actions,
        projection["symbol"],
        projection["isin"],
        date.fromisoformat(projection["entry_session_date"]),
        outcome_day,
    )
    action_review["complete_action_coverage"] = actions[
        "complete_action_coverage"
    ]
    action_review["raw_records"] = actions["raw_records"]
    action_review["unique_records"] = actions["unique_records"]

    benchmark = _benchmark_reference(
        source_bytes["index"],
        session=outcome_day,
        entry_close=sealed_prediction["benchmark"]["entry_reference_close"],
    )
    raw_excess = Decimal(str(raw_reference["raw_actual_return_pct"])) - Decimal(
        str(benchmark["raw_return_pct"])
    )
    benchmark["raw_unadjusted_equity_excess_pp"] = round(
        float(raw_excess), 6
    )

    blockers = ["EXCHANGE_PUBLICATION_TIME_NOT_PROVEN"]
    blockers.append("POINT_IN_TIME_MATURITY_IDENTITY_NOT_PROVEN")
    if classification != "COMPANY_EQ_IDENTITY_MATCHED":
        blockers.append("CURRENT_IDENTITY_MATCH_NOT_PROVEN")
    if action_review["action_count"] or action_review[
        "identity_link_review_required"
    ]:
        blockers.append("CORPORATE_ACTION_OR_IDENTITY_ADJUSTMENT_REQUIRED")
    if not actions["complete_action_coverage"]:
        blockers.append("COMPLETE_CORPORATE_ACTION_COVERAGE_NOT_PROVEN")

    record = {
        "schema_version": SCHEMA_VERSION,
        "task_id": "EQ-OUTCOME-027",
        "prediction_id": projection["prediction_id"],
        "prediction_event_hash": projection["prediction_event_hash"],
        "projection_hash": projection["projection_hash"],
        "recorded_at": current.isoformat(),
        "source_cutoff_at": source_cutoff.isoformat(),
        "source_receipts": verified_receipts,
        "identity_review": identity_review,
        "corporate_action_review": action_review,
        "raw_reference": raw_reference,
        "benchmark_raw_reference": benchmark,
        "final_outcome_status": "NOT_PROVEN_ADJUSTMENT_REVIEW_PENDING",
        "final_outcome_blockers": blockers,
        "counts": {
            "immutable_predictions": 1,
            "raw_reference_observations": 1,
            "matured_adjusted_outcomes": 0,
        },
        "market_validation_claimed": False,
        "performance_metrics_available": False,
        "performance_gate_passed": False,
        "real_money_ready": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    record["record_hash"] = sha256(_canonical(record)).hexdigest()
    validate_maturity_observation(record)
    return record


def _validate_raw_reference(
    record: Mapping[str, Any],
    *,
    recorded: datetime,
) -> tuple[dict[str, Any], datetime, datetime, str, str]:
    raw = record.get("raw_reference")
    if not isinstance(raw, dict) or set(raw) != _RAW_REFERENCE_FIELDS:
        raise MaturityObservationError("RAW_REFERENCE_FIELDS_INVALID")
    prediction_id = record.get("prediction_id")
    if (
        not isinstance(prediction_id, str)
        or prediction_id != prediction_id.strip()
        or not prediction_id
        or len(prediction_id) > 128
        or raw["prediction_id"] != prediction_id
    ):
        raise MaturityObservationError("PREDICTION_ID_INVALID")
    prediction_hash = _sha(record.get("prediction_event_hash"), "PREDICTION_EVENT_HASH")
    projection_hash = _sha(record.get("projection_hash"), "PROJECTION_HASH")
    if raw["prediction_event_hash"] != prediction_hash or raw["projection_hash"] != projection_hash:
        raise MaturityObservationError("RAW_REFERENCE_ANCHOR_MISMATCH")

    symbol = str(raw.get("symbol", ""))
    isin = str(raw.get("isin", ""))
    if symbol != symbol.strip().upper() or not _SYMBOL_RE.fullmatch(symbol):
        raise MaturityObservationError("RAW_REFERENCE_SYMBOL_INVALID")
    if isin != isin.strip().upper() or not _ISIN_RE.fullmatch(isin):
        raise MaturityObservationError("RAW_REFERENCE_ISIN_INVALID")

    issued = _time(raw.get("issued_at"), "RAW_ISSUED_AT")
    due = _time(raw.get("due_at"), "RAW_DUE_AT")
    price_as_of = _time(raw.get("outcome_price_as_of_at"), "RAW_OUTCOME_PRICE_AS_OF_AT")
    observed = _time(
        raw.get("outcome_source_first_observed_at"),
        "RAW_OUTCOME_SOURCE_FIRST_OBSERVED_AT",
    )
    if not issued < due == price_as_of <= observed <= recorded:
        raise MaturityObservationError("RAW_REFERENCE_TIME_ORDER_INVALID")

    entry = _positive_decimal(raw.get("entry_reference_close"), "RAW_ENTRY_REFERENCE_CLOSE")
    outcome = _positive_decimal(raw.get("outcome_reference_close"), "RAW_OUTCOME_REFERENCE_CLOSE")
    expected_return = round(
        float((outcome / entry - Decimal("1")) * Decimal("100")),
        6,
    )
    if _finite_decimal(raw.get("raw_actual_return_pct"), "RAW_ACTUAL_RETURN_PCT") != Decimal(str(expected_return)):
        raise MaturityObservationError("RAW_REFERENCE_RETURN_INVALID")
    expected_direction = "POSITIVE" if expected_return > 0 else "NEGATIVE" if expected_return < 0 else "FLAT"
    if raw.get("raw_reference_direction") != expected_direction:
        raise MaturityObservationError("RAW_REFERENCE_DIRECTION_INVALID")

    if (
        raw.get("status") != "RAW_REFERENCE_OBSERVED_ADJUSTMENT_REVIEW_PENDING"
        or raw.get("forecast_kind") != "DIRECTION_ONLY"
        or raw.get("forecast_direction") not in {"POSITIVE", "NEGATIVE"}
        or raw.get("outcome_source_exchange_published_at") is not None
        or raw.get("source_availability_status") != "FIRST_OBSERVED_ONLY_EXCHANGE_PUBLICATION_NOT_PROVEN"
        or raw.get("outcome_source") != "NSE"
        or raw.get("price_basis") != "UNADJUSTED_EXCHANGE_REFERENCE"
        or raw.get("adjustment_status") != "PENDING_MATURITY_RECHECK"
        or raw.get("matured_outcomes") != 0
    ):
        raise MaturityObservationError("RAW_REFERENCE_SEMANTICS_INVALID")
    for field in (
        "predicted_return_pct",
        "expected_return_range",
        "calibrated_probability",
        "actual_return_pct",
        "absolute_error_pp",
        "direction_correct",
        "adjustment_basis",
    ):
        if raw.get(field) is not None:
            raise MaturityObservationError("RAW_REFERENCE_SEMANTICS_INVALID")
    for field in (
        "market_validation_claimed",
        "reference_prices_are_executable_fills",
        "performance_metrics_available",
        "performance_gate_passed",
        "real_money_ready",
        "live_trading_enabled",
        "order_placement_allowed",
    ):
        if raw.get(field) is not False:
            raise MaturityObservationError(f"RAW_REFERENCE_{field.upper()}_INVALID")
    for field in (
        "entry_source_hash",
        "entry_source_row_hash",
        "outcome_source_hash",
        "outcome_source_row_hash",
    ):
        _sha(raw.get(field), f"RAW_{field.upper()}")
    for field in ("entry_snapshot_uri", "outcome_snapshot_uri"):
        try:
            if _snapshot_reference(raw.get(field), field.upper()) != raw.get(field):
                raise MaturityObservationError(f"RAW_REFERENCE_{field.upper()}_INVALID")
        except LedgerError as exc:
            raise MaturityObservationError(str(exc)) from exc
    size = raw.get("outcome_source_size_bytes")
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise MaturityObservationError("RAW_OUTCOME_SOURCE_SIZE_BYTES_INVALID")
    expected_url = CM_URL_PREFIX + "BhavCopy_NSE_CM_0_0_0_" + due.strftime("%Y%m%d") + "_F_0000.csv.zip"
    if raw.get("outcome_source_url") != expected_url:
        raise MaturityObservationError("RAW_OUTCOME_SOURCE_URL_INVALID")
    return raw, issued, due, symbol, isin


def _validate_source_receipts(
    record: Mapping[str, Any],
    *,
    raw: Mapping[str, Any],
    issued: datetime,
    due: datetime,
    recorded: datetime,
) -> dict[str, dict[str, Any]]:
    receipts = record.get("source_receipts")
    if not isinstance(receipts, dict) or set(receipts) != SOURCE_ROLES:
        raise MaturityObservationError("SOURCE_RECEIPT_ROLES_INVALID")
    expected_urls = {
        "outcome_cash": raw["outcome_source_url"],
        "company": EQUITY_URL,
        "etf": ETF_URL,
        "index": INDEX_URL_PREFIX + due.strftime("%d%m%Y") + ".csv",
    }
    observed: dict[str, datetime] = {}
    for role in sorted(SOURCE_ROLES):
        receipt = receipts[role]
        if not isinstance(receipt, dict) or set(receipt) != _RECEIPT_FIELDS:
            raise MaturityObservationError(f"{role.upper()}_RECEIPT_FIELDS_INVALID")
        url = receipt.get("url")
        parsed = urlsplit(str(url))
        if (
            receipt.get("final_url") != url
            or receipt.get("http_status") != 200
            or receipt.get("exchange_published_at") is not None
            or parsed.scheme != "https"
            or parsed.hostname not in {"nsearchives.nseindia.com", "www.nseindia.com"}
            or parsed.username
            or parsed.password
            or parsed.fragment
            or parsed.port not in (None, 443)
        ):
            raise MaturityObservationError(f"{role.upper()}_RECEIPT_SEMANTICS_INVALID")
        if role != "actions" and url != expected_urls[role]:
            raise MaturityObservationError(f"{role.upper()}_URL_INVALID")
        _sha(receipt.get("sha256"), f"{role.upper()}_SHA256")
        size = receipt.get("bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
            raise MaturityObservationError(f"{role.upper()}_BYTES_INVALID")
        try:
            if _snapshot_reference(receipt.get("snapshot_uri"), f"{role.upper()}_SNAPSHOT_URI") != receipt.get(
                "snapshot_uri"
            ):
                raise MaturityObservationError(f"{role.upper()}_SNAPSHOT_URI_INVALID")
        except LedgerError as exc:
            raise MaturityObservationError(str(exc)) from exc
        observed[role] = _time(
            receipt.get("first_observed_at"),
            f"{role.upper()}_FIRST_OBSERVED_AT",
        )
        if not due <= observed[role] <= recorded:
            raise MaturityObservationError(f"{role.upper()}_OBSERVATION_TIME_INVALID")

    action_url = str(receipts["actions"]["url"])
    action_parts = urlsplit(action_url)
    action_query = parse_qs(action_parts.query, keep_blank_values=True)
    try:
        action_start = datetime.strptime(action_query["from_date"][0], "%d-%m-%Y").date()
        action_end = datetime.strptime(action_query["to_date"][0], "%d-%m-%Y").date()
    except (KeyError, IndexError, ValueError) as exc:
        raise MaturityObservationError("ACTIONS_INTERVAL_INVALID") from exc
    if (
        action_parts.hostname != "www.nseindia.com"
        or action_parts.path != "/api/corporates-corporateActions"
        or set(action_query) != {"index", "from_date", "to_date"}
        or action_query["index"] != ["equities"]
        or action_start > issued.date()
        or action_end < due.date()
    ):
        raise MaturityObservationError("ACTIONS_SOURCE_SCOPE_INVALID")

    source_cutoff = max(observed.values())
    if _time(record.get("source_cutoff_at"), "SOURCE_CUTOFF_AT") != source_cutoff:
        raise MaturityObservationError("SOURCE_CUTOFF_MISMATCH")
    if (
        raw["outcome_source_first_observed_at"] != receipts["outcome_cash"]["first_observed_at"]
        or raw["outcome_source_hash"] != receipts["outcome_cash"]["sha256"]
        or raw["outcome_source_size_bytes"] != receipts["outcome_cash"]["bytes"]
        or raw["outcome_snapshot_uri"] != receipts["outcome_cash"]["snapshot_uri"]
    ):
        raise MaturityObservationError("RAW_OUTCOME_RECEIPT_MISMATCH")
    return receipts


def _validate_identity_review(
    record: Mapping[str, Any],
    *,
    raw: Mapping[str, Any],
    receipts: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    identity = record.get("identity_review")
    if not isinstance(identity, dict) or set(identity) != _IDENTITY_REVIEW_FIELDS:
        raise MaturityObservationError("IDENTITY_REVIEW_FIELDS_INVALID")
    if (
        identity.get("symbol") != raw["symbol"]
        or identity.get("isin") != raw["isin"]
        or identity.get("classification") not in _IDENTITY_CLASSIFICATIONS
        or identity.get("scope") != "CURRENT_MASTER_AT_OBSERVATION_NOT_POINT_IN_TIME_MATURITY"
        or identity.get("identity_change_proven") is not False
    ):
        raise MaturityObservationError("IDENTITY_REVIEW_SEMANTICS_INVALID")
    equity_receipt = {
        "url": receipts["company"]["url"],
        "raw_sha256": receipts["company"]["sha256"],
        "first_observed_at": receipts["company"]["first_observed_at"],
    }
    etf_receipt = {
        "url": receipts["etf"]["url"],
        "raw_sha256": receipts["etf"]["sha256"],
        "first_observed_at": receipts["etf"]["first_observed_at"],
    }
    expected_digest = sha256(
        _canonical(
            {
                "version": INSTRUMENT_SCOPE_VERSION,
                "equity": equity_receipt,
                "etf": etf_receipt,
            }
        )
    ).hexdigest()
    if identity.get("snapshot_digest") != expected_digest:
        raise MaturityObservationError("IDENTITY_SNAPSHOT_DIGEST_MISMATCH")
    return identity


def _validate_action_review(
    record: Mapping[str, Any],
    *,
    raw: Mapping[str, Any],
    receipts: Mapping[str, Mapping[str, Any]],
    issued: datetime,
    due: datetime,
) -> dict[str, Any]:
    review = record.get("corporate_action_review")
    if not isinstance(review, dict) or set(review) != _ACTION_REVIEW_FIELDS:
        raise MaturityObservationError("ACTION_REVIEW_FIELDS_INVALID")
    for field in ("action_count", "raw_records", "unique_records"):
        value = review.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise MaturityObservationError(f"ACTION_{field.upper()}_INVALID")
    if review["unique_records"] > review["raw_records"]:
        raise MaturityObservationError("ACTION_RECORD_COUNTS_INVALID")
    events = review.get("events")
    if not isinstance(events, list) or review["action_count"] != len(events):
        raise MaturityObservationError("ACTION_EVENTS_INVALID")
    hashes: set[str] = set()
    expected_identity_review = False
    for event in events:
        if not isinstance(event, dict):
            raise MaturityObservationError("ACTION_EVENT_INVALID")
        digest = _sha(event.get("record_sha256"), "ACTION_RECORD_SHA256")
        original = {key: value for key, value in event.items() if key not in {"record_sha256", "ex_date"}}
        if digest in hashes or sha256(_canonical(original)).hexdigest() != digest:
            raise MaturityObservationError("ACTION_EVENT_HASH_INVALID")
        hashes.add(digest)
        try:
            ex_date = date.fromisoformat(str(event.get("ex_date")))
        except ValueError as exc:
            raise MaturityObservationError("ACTION_EVENT_DATE_INVALID") from exc
        if not issued.date() < ex_date <= due.date() or (
            event.get("symbol") != raw["symbol"] and event.get("isin") != raw["isin"]
        ):
            raise MaturityObservationError("ACTION_EVENT_SCOPE_INVALID")
        expected_identity_review = expected_identity_review or event.get("isin") != raw["isin"]
    expected_status = "ACTION_OR_IDENTITY_REVIEW_REQUIRED" if events else "NO_MATCH_IN_CAPTURE_COVERAGE_NOT_PROVEN"
    action_parts = urlsplit(str(receipts["actions"]["url"]))
    action_query = parse_qs(action_parts.query)
    start = datetime.strptime(action_query["from_date"][0], "%d-%m-%Y").date()
    end = datetime.strptime(action_query["to_date"][0], "%d-%m-%Y").date()
    expected_covered = start <= issued.date() and due.date() <= end
    if (
        review.get("identity_link_review_required") is not expected_identity_review
        or review.get("requested_interval_covered") is not expected_covered
        or review.get("status") != expected_status
        or review.get("source_sha256") != receipts["actions"]["sha256"]
        or review.get("adjusted_return_proven") is not False
        or review.get("use_as_historical_prediction_feature_allowed") is not False
        or review.get("complete_action_coverage") is not False
    ):
        raise MaturityObservationError("ACTION_REVIEW_SEMANTICS_INVALID")
    return review


def _validate_benchmark(
    record: Mapping[str, Any],
    *,
    raw: Mapping[str, Any],
    due: datetime,
) -> None:
    benchmark = record.get("benchmark_raw_reference")
    if not isinstance(benchmark, dict) or set(benchmark) != _BENCHMARK_FIELDS:
        raise MaturityObservationError("BENCHMARK_FIELDS_INVALID")
    entry = _positive_decimal(benchmark.get("entry_reference_close"), "BENCHMARK_ENTRY_CLOSE")
    outcome = _positive_decimal(benchmark.get("outcome_reference_close"), "BENCHMARK_OUTCOME_CLOSE")
    expected_return = round(
        float((outcome / entry - Decimal("1")) * Decimal("100")),
        6,
    )
    if _finite_decimal(benchmark.get("raw_return_pct"), "BENCHMARK_RAW_RETURN_PCT") != Decimal(str(expected_return)):
        raise MaturityObservationError("BENCHMARK_RETURN_INVALID")
    expected_excess = round(
        float(
            _finite_decimal(raw.get("raw_actual_return_pct"), "RAW_ACTUAL_RETURN_PCT") - Decimal(str(expected_return))
        ),
        6,
    )
    if _finite_decimal(
        benchmark.get("raw_unadjusted_equity_excess_pp"),
        "BENCHMARK_RAW_EXCESS_PP",
    ) != Decimal(str(expected_excess)):
        raise MaturityObservationError("BENCHMARK_EXCESS_INVALID")
    if (
        benchmark.get("name") != "Nifty 50"
        or benchmark.get("outcome_session_date") != due.date().isoformat()
        or benchmark.get("price_basis") != "UNADJUSTED_EXCHANGE_REFERENCE"
        or benchmark.get("performance_metric_status") != "RAW_REFERENCE_ONLY_EQUITY_ADJUSTMENT_NOT_PROVEN"
    ):
        raise MaturityObservationError("BENCHMARK_SEMANTICS_INVALID")
    _sha(benchmark.get("source_row_sha256"), "BENCHMARK_SOURCE_ROW_SHA256")


def validate_maturity_observation(record: dict[str, Any]) -> dict[str, Any]:
    """Validate immutable semantics without turning a raw reference into a score."""
    if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
        raise MaturityObservationError("RECORD_FIELDS_INVALID")
    if record.get("schema_version") != SCHEMA_VERSION:
        raise MaturityObservationError("SCHEMA_VERSION_INVALID")
    if record.get("task_id") != "EQ-OUTCOME-027":
        raise MaturityObservationError("TASK_ID_INVALID")
    expected = _rehash_without(record, "record_hash")
    if record.get("record_hash") != expected:
        raise MaturityObservationError("RECORD_HASH_MISMATCH")
    recorded = _time(record.get("recorded_at"), "RECORDED_AT")
    raw, issued, due, _, _ = _validate_raw_reference(
        record,
        recorded=recorded,
    )
    receipts = _validate_source_receipts(
        record,
        raw=raw,
        issued=issued,
        due=due,
        recorded=recorded,
    )
    identity = _validate_identity_review(record, raw=raw, receipts=receipts)
    action_review = _validate_action_review(
        record,
        raw=raw,
        receipts=receipts,
        issued=issued,
        due=due,
    )
    _validate_benchmark(record, raw=raw, due=due)
    if record.get("final_outcome_status") != ("NOT_PROVEN_ADJUSTMENT_REVIEW_PENDING"):
        raise MaturityObservationError("FINAL_OUTCOME_STATUS_INVALID")
    counts = record.get("counts")
    if counts != {
        "immutable_predictions": 1,
        "raw_reference_observations": 1,
        "matured_adjusted_outcomes": 0,
    }:
        raise MaturityObservationError("COUNTS_INVALID")
    expected_blockers = [
        "EXCHANGE_PUBLICATION_TIME_NOT_PROVEN",
        "POINT_IN_TIME_MATURITY_IDENTITY_NOT_PROVEN",
    ]
    if identity["classification"] != "COMPANY_EQ_IDENTITY_MATCHED":
        expected_blockers.append("CURRENT_IDENTITY_MATCH_NOT_PROVEN")
    if action_review["action_count"] or action_review["identity_link_review_required"]:
        expected_blockers.append("CORPORATE_ACTION_OR_IDENTITY_ADJUSTMENT_REQUIRED")
    if not action_review["complete_action_coverage"]:
        expected_blockers.append("COMPLETE_CORPORATE_ACTION_COVERAGE_NOT_PROVEN")
    if record.get("final_outcome_blockers") != expected_blockers:
        raise MaturityObservationError("FINAL_OUTCOME_BLOCKERS_INVALID")
    for field in (
        "market_validation_claimed",
        "performance_metrics_available",
        "performance_gate_passed",
        "real_money_ready",
        "live_trading_enabled",
        "order_placement_allowed",
    ):
        if record.get(field) is not False:
            raise MaturityObservationError(f"{field.upper()}_INVALID")
    return {
        "status": "VERIFIED_RAW_REFERENCE_FINAL_OUTCOME_NOT_PROVEN",
        "prediction_id": record["prediction_id"],
        "raw_reference_observations": 1,
        "matured_adjusted_outcomes": 0,
        "orders_allowed": False,
    }


def verify_maturity_evidence(
    record: dict[str, Any],
    *,
    evidence_root: Path,
) -> None:
    """Recheck every maturity receipt against the retained exact bytes."""
    validate_maturity_observation(record)
    root = Path(evidence_root).resolve(strict=True)
    if not root.is_dir():
        raise MaturityObservationError("EVIDENCE_ROOT_NOT_DIRECTORY")
    for role in sorted(SOURCE_ROLES):
        receipt = record["source_receipts"][role]
        try:
            digest, size = _retained_snapshot_digest(
                root,
                receipt["snapshot_uri"],
                role.upper(),
            )
        except (KeyError, LedgerError) as exc:
            raise MaturityObservationError(
                f"{role.upper()}_RETAINED_UNAVAILABLE"
            ) from exc
        if digest != receipt["sha256"] or size != receipt["bytes"]:
            raise MaturityObservationError(
                f"{role.upper()}_RETAINED_HASH_OR_SIZE_MISMATCH"
            )


def _canonical_maturity_ledger_event(record: Mapping[str, Any]) -> bytes:
    return _canonical(
        {key: value for key, value in record.items() if key != "event_hash"}
    )


def _strict_json_object(raw: bytes, field: str) -> dict[str, Any]:
    if not isinstance(raw, bytes) or not raw:
        raise MaturityObservationError(f"{field}_BYTES_REQUIRED")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise MaturityObservationError(f"{field}_DUPLICATE_KEY")
            result[key] = value
        return result

    try:
        parsed = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs_hook)
    except MaturityObservationError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MaturityObservationError(f"{field}_INVALID_JSON") from exc
    if not isinstance(parsed, dict):
        raise MaturityObservationError(f"{field}_OBJECT_REQUIRED")
    return parsed


def _canonical_issuance_manifest_event(
    record: Mapping[str, Any],
) -> bytes:
    return _canonical(
        {key: value for key, value in record.items() if key != "event_hash"}
    )


def _validate_issuance_manifest_event(
    event: Mapping[str, Any],
    *,
    prefix: str = "",
    allow_unhashed: bool = False,
) -> tuple[datetime, datetime, datetime]:
    expected_fields = (
        _ISSUANCE_MANIFEST_FIELDS - {"event_hash"}
        if allow_unhashed
        else _ISSUANCE_MANIFEST_FIELDS
    )
    if not isinstance(event, dict) or set(event) != expected_fields:
        raise MaturityObservationError(
            f"{prefix}ISSUANCE_MANIFEST_FIELDS_INVALID"
        )
    if event.get("schema_version") != ISSUANCE_MANIFEST_SCHEMA_VERSION:
        raise MaturityObservationError(
            f"{prefix}ISSUANCE_MANIFEST_SCHEMA_INVALID"
        )
    if event.get("event_type") != _ISSUANCE_MANIFEST_EVENT_TYPE:
        raise MaturityObservationError(
            f"{prefix}ISSUANCE_MANIFEST_EVENT_TYPE_INVALID"
        )
    prediction_id = event.get("prediction_id")
    if (
        not isinstance(prediction_id, str)
        or not prediction_id
        or prediction_id != prediction_id.strip()
        or len(prediction_id) > 128
    ):
        raise MaturityObservationError(
            f"{prefix}ISSUANCE_PREDICTION_ID_INVALID"
        )
    for field in (
        "prediction_event_hash",
        "prediction_file_sha256",
        "projection_hash",
        "projection_file_sha256",
        "previous_hash",
    ):
        digest = _sha(event.get(field), f"{prefix}{field.upper()}")
        if event.get(field) != digest:
            raise MaturityObservationError(
                f"{prefix}{field.upper()}_INVALID"
            )
    for field in ("prediction_size_bytes", "projection_size_bytes"):
        size = event.get(field)
        if (
            isinstance(size, bool)
            or not isinstance(size, int)
            or size <= 0
            or size > _MAX_ANCHOR_ARTIFACT_BYTES
        ):
            raise MaturityObservationError(f"{prefix}{field.upper()}_INVALID")
    prediction_uri = _observation_reference(
        event.get("prediction_uri"),
        f"{prefix}PREDICTION_URI",
    )
    projection_uri = _observation_reference(
        event.get("projection_uri"),
        f"{prefix}PROJECTION_URI",
    )
    if (
        event.get("prediction_uri") != prediction_uri
        or event.get("projection_uri") != projection_uri
        or not prediction_uri.endswith(".json")
        or not projection_uri.endswith(".json")
        or prediction_uri == projection_uri
    ):
        raise MaturityObservationError(
            f"{prefix}ISSUANCE_ARTIFACT_URI_INVALID"
        )
    issued = _time(event.get("issued_at"), f"{prefix}ISSUED_AT")
    due = _time(event.get("due_at"), f"{prefix}DUE_AT")
    registered = _time(
        event.get("registered_at"),
        f"{prefix}REGISTERED_AT",
    )
    if not issued <= registered or not issued < due:
        raise MaturityObservationError(
            f"{prefix}ISSUANCE_MANIFEST_TIME_ORDER_INVALID"
        )
    pre_maturity = registered < due
    expected_status = (
        "PRE_MATURITY_REGISTERED"
        if pre_maturity
        else "HISTORICAL_AFTER_MATURITY_REGISTRATION_NOT_PROVEN"
    )
    if (
        type(event.get("pre_maturity_registered")) is not bool
        or event.get("pre_maturity_registered") is not pre_maturity
        or event.get("registration_status") != expected_status
    ):
        raise MaturityObservationError(
            f"{prefix}ISSUANCE_REGISTRATION_STATUS_INVALID"
        )
    for field in (
        "market_validation_claimed",
        "performance_metrics_available",
        "real_money_ready",
        "live_trading_enabled",
        "order_placement_allowed",
    ):
        if event.get(field) is not False:
            raise MaturityObservationError(
                f"{prefix}{field.upper()}_INVALID"
            )
    if not allow_unhashed:
        expected_hash = sha256(
            _canonical_issuance_manifest_event(event)
        ).hexdigest()
        if event.get("event_hash") != expected_hash:
            raise MaturityObservationError(
                f"{prefix}ISSUANCE_MANIFEST_HASH_MISMATCH"
            )
    return issued, due, registered


def build_issuance_artifact_event(
    *,
    prediction_bytes: bytes,
    projection_bytes: bytes,
    prediction_uri: str,
    projection_uri: str,
    registered_at: datetime,
    previous_hash: str,
) -> dict[str, Any]:
    """Seal exact forecast artifact bytes without claiming validation."""
    for raw, field in (
        (prediction_bytes, "PREDICTION_ARTIFACT"),
        (projection_bytes, "PROJECTION_ARTIFACT"),
    ):
        if (
            not isinstance(raw, bytes)
            or not raw
            or len(raw) > _MAX_ANCHOR_ARTIFACT_BYTES
        ):
            raise MaturityObservationError(f"{field}_SIZE_INVALID")
    prediction = _strict_json_object(prediction_bytes, "PREDICTION_ARTIFACT")
    projection = _strict_json_object(projection_bytes, "PROJECTION_ARTIFACT")
    try:
        validate_directional_outcome_projection(projection)
    except (KeyError, TypeError, ValueError) as exc:
        raise MaturityObservationError(
            "PROJECTION_ARTIFACT_INVALID"
        ) from exc
    prediction_event_hash = _sha(
        prediction.get("event_hash"),
        "PREDICTION_EVENT_HASH",
    )
    expected_prediction_hash = sha256(
        _canonical({
            key: value
            for key, value in prediction.items()
            if key != "event_hash"
        })
    ).hexdigest()
    if prediction_event_hash != expected_prediction_hash:
        raise MaturityObservationError("PREDICTION_ARTIFACT_HASH_MISMATCH")
    if (
        projection.get("prediction_id") != prediction.get("prediction_id")
        or projection.get("prediction_event_hash") != prediction_event_hash
        or projection.get("issued_at") != prediction.get("issued_at")
        or projection.get("due_at") != prediction.get("due_at")
    ):
        raise MaturityObservationError("ISSUANCE_ARTIFACT_BINDING_MISMATCH")
    if registered_at.tzinfo is None or registered_at.utcoffset() is None:
        raise MaturityObservationError("REGISTERED_AT_TIMEZONE_REQUIRED")
    registered = registered_at.astimezone(timezone.utc)
    issued = _time(prediction.get("issued_at"), "ISSUED_AT")
    due = _time(prediction.get("due_at"), "DUE_AT")
    if registered < issued:
        raise MaturityObservationError(
            "ISSUANCE_MANIFEST_TIME_ORDER_INVALID"
        )
    pre_maturity = registered < due
    event = {
        "schema_version": ISSUANCE_MANIFEST_SCHEMA_VERSION,
        "event_type": _ISSUANCE_MANIFEST_EVENT_TYPE,
        "prediction_id": prediction["prediction_id"],
        "prediction_event_hash": prediction_event_hash,
        "prediction_uri": _observation_reference(
            prediction_uri, "PREDICTION_URI"
        ),
        "prediction_file_sha256": sha256(prediction_bytes).hexdigest(),
        "prediction_size_bytes": len(prediction_bytes),
        "projection_hash": projection["projection_hash"],
        "projection_uri": _observation_reference(
            projection_uri, "PROJECTION_URI"
        ),
        "projection_file_sha256": sha256(projection_bytes).hexdigest(),
        "projection_size_bytes": len(projection_bytes),
        "issued_at": prediction["issued_at"],
        "due_at": prediction["due_at"],
        "registered_at": registered.isoformat(),
        "registration_status": (
            "PRE_MATURITY_REGISTERED"
            if pre_maturity
            else "HISTORICAL_AFTER_MATURITY_REGISTRATION_NOT_PROVEN"
        ),
        "pre_maturity_registered": pre_maturity,
        "previous_hash": _sha(previous_hash, "PREVIOUS_HASH"),
        "market_validation_claimed": False,
        "performance_metrics_available": False,
        "real_money_ready": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    _validate_issuance_manifest_event(event, allow_unhashed=True)
    event["event_hash"] = sha256(
        _canonical_issuance_manifest_event(event)
    ).hexdigest()
    _validate_issuance_manifest_event(event)
    return event


def _validate_maturity_ledger_event(
    event: Mapping[str, Any],
    *,
    prefix: str = "",
    allow_unhashed: bool = False,
) -> tuple[datetime, datetime]:
    expected_fields = (
        _MATURITY_LEDGER_FIELDS - {"event_hash"}
        if allow_unhashed
        else _MATURITY_LEDGER_FIELDS
    )
    if not isinstance(event, dict) or set(event) != expected_fields:
        raise MaturityObservationError(f"{prefix}LEDGER_FIELDS_INVALID")
    if event.get("schema_version") != MATURITY_LEDGER_SCHEMA_VERSION:
        raise MaturityObservationError(f"{prefix}LEDGER_SCHEMA_INVALID")
    if event.get("event_type") != _MATURITY_LEDGER_EVENT_TYPE:
        raise MaturityObservationError(f"{prefix}LEDGER_EVENT_TYPE_INVALID")

    prediction_id = event.get("prediction_id")
    if (
        not isinstance(prediction_id, str)
        or not prediction_id
        or prediction_id != prediction_id.strip()
        or len(prediction_id) > 128
    ):
        raise MaturityObservationError(f"{prefix}PREDICTION_ID_INVALID")
    for field in (
        "prediction_event_hash",
        "projection_hash",
        "observation_record_hash",
        "observation_file_sha256",
        "previous_hash",
    ):
        digest = _sha(event.get(field), f"{prefix}{field.upper()}")
        if event.get(field) != digest:
            raise MaturityObservationError(f"{prefix}{field.upper()}_INVALID")

    size = event.get("observation_size_bytes")
    if (
        isinstance(size, bool)
        or not isinstance(size, int)
        or size <= 0
        or size > _MAX_MATURITY_OBSERVATION_BYTES
    ):
        raise MaturityObservationError(
            f"{prefix}OBSERVATION_SIZE_BYTES_INVALID"
        )
    reference = _observation_reference(
        event.get("observation_uri"),
        f"{prefix}OBSERVATION_URI",
    )
    if event.get("observation_uri") != reference:
        raise MaturityObservationError(f"{prefix}OBSERVATION_URI_INVALID")

    recorded = _time(event.get("recorded_at"), f"{prefix}RECORDED_AT")
    cutoff = _time(event.get("source_cutoff_at"), f"{prefix}SOURCE_CUTOFF_AT")
    if cutoff > recorded:
        raise MaturityObservationError(f"{prefix}LEDGER_TIME_ORDER_INVALID")
    if event.get("final_outcome_status") != (
        "NOT_PROVEN_ADJUSTMENT_REVIEW_PENDING"
    ):
        raise MaturityObservationError(
            f"{prefix}FINAL_OUTCOME_STATUS_INVALID"
        )
    if (
        event.get("raw_reference_observations") != 1
        or event.get("matured_adjusted_outcomes") != 0
    ):
        raise MaturityObservationError(f"{prefix}LEDGER_COUNTS_INVALID")
    for field in (
        "adjusted_actual_return_pct",
        "direction_correct",
        "calibration_error",
    ):
        if event.get(field) is not None:
            raise MaturityObservationError(
                f"{prefix}{field.upper()}_PREMATURE"
            )
    for field in (
        "market_validation_claimed",
        "performance_metrics_available",
        "performance_gate_passed",
        "real_money_ready",
        "live_trading_enabled",
        "order_placement_allowed",
    ):
        if event.get(field) is not False:
            raise MaturityObservationError(
                f"{prefix}{field.upper()}_INVALID"
            )
    if not allow_unhashed:
        expected_hash = sha256(
            _canonical_maturity_ledger_event(event)
        ).hexdigest()
        if event.get("event_hash") != expected_hash:
            raise MaturityObservationError(f"{prefix}LEDGER_HASH_MISMATCH")
    return recorded, cutoff


def build_maturity_observation_event(
    observation: dict[str, Any],
    *,
    observation_bytes: bytes,
    observation_uri: str,
    trusted_prediction_event_hash: str,
    trusted_projection_hash: str,
    previous_hash: str,
) -> dict[str, Any]:
    """Seal one retained raw observation against independent trusted anchors."""
    validate_maturity_observation(observation)
    parsed = _strict_json_object(observation_bytes, "OBSERVATION")
    if parsed != observation:
        raise MaturityObservationError("OBSERVATION_BYTES_RECORD_MISMATCH")

    prediction_hash = _sha(
        trusted_prediction_event_hash,
        "TRUSTED_PREDICTION_EVENT_HASH",
    )
    projection_hash = _sha(
        trusted_projection_hash,
        "TRUSTED_PROJECTION_HASH",
    )
    if observation["prediction_event_hash"] != prediction_hash:
        raise MaturityObservationError(
            "PREDICTION_EVENT_HASH_TRUST_MISMATCH"
        )
    if observation["projection_hash"] != projection_hash:
        raise MaturityObservationError("PROJECTION_HASH_TRUST_MISMATCH")

    retained_uri = _observation_reference(
        observation_uri,
        "OBSERVATION_URI",
    )
    event = {
        "schema_version": MATURITY_LEDGER_SCHEMA_VERSION,
        "event_type": _MATURITY_LEDGER_EVENT_TYPE,
        "prediction_id": observation["prediction_id"],
        "prediction_event_hash": prediction_hash,
        "projection_hash": projection_hash,
        "observation_record_hash": observation["record_hash"],
        "observation_file_sha256": sha256(observation_bytes).hexdigest(),
        "observation_size_bytes": len(observation_bytes),
        "observation_uri": retained_uri,
        "recorded_at": observation["recorded_at"],
        "source_cutoff_at": observation["source_cutoff_at"],
        "final_outcome_status": observation["final_outcome_status"],
        "raw_reference_observations": observation["counts"][
            "raw_reference_observations"
        ],
        "matured_adjusted_outcomes": observation["counts"][
            "matured_adjusted_outcomes"
        ],
        "adjusted_actual_return_pct": None,
        "direction_correct": None,
        "calibration_error": None,
        "previous_hash": _sha(previous_hash, "PREVIOUS_HASH"),
        "market_validation_claimed": False,
        "performance_metrics_available": False,
        "performance_gate_passed": False,
        "real_money_ready": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    _validate_maturity_ledger_event(event, allow_unhashed=True)
    event["event_hash"] = sha256(
        _canonical_maturity_ledger_event(event)
    ).hexdigest()
    _validate_maturity_ledger_event(event)
    return event


def _derive_maturity_artifact_anchors(
    *,
    anchor_artifacts: list[Mapping[str, str]],
    evidence_root: Path,
) -> tuple[dict[str, str], dict[str, str]]:
    """Derive trusted hashes only after replaying retained forecast artifacts."""
    if not isinstance(anchor_artifacts, list):
        raise MaturityObservationError("ANCHOR_ARTIFACTS_LIST_REQUIRED")

    prediction_hashes: dict[str, str] = {}
    projection_hashes: dict[str, str] = {}
    seen_uris: set[str] = set()
    expected_previous = FORWARD_PREDICTION_GENESIS_HASH
    for index, pair in enumerate(anchor_artifacts):
        prefix = f"ANCHOR_{index}_"
        if not isinstance(pair, Mapping) or set(pair) != (
            _ANCHOR_ARTIFACT_FIELDS
        ):
            raise MaturityObservationError(
                f"{prefix}ARTIFACT_FIELDS_INVALID"
            )
        prediction_uri = _observation_reference(
            pair.get("prediction_uri"),
            f"{prefix}PREDICTION_URI",
        )
        projection_uri = _observation_reference(
            pair.get("projection_uri"),
            f"{prefix}PROJECTION_URI",
        )
        if (
            not prediction_uri.endswith(".json")
            or not projection_uri.endswith(".json")
            or prediction_uri == projection_uri
            or prediction_uri in seen_uris
            or projection_uri in seen_uris
        ):
            raise MaturityObservationError(
                f"{prefix}ARTIFACT_URI_INVALID"
            )

        prediction_raw = _read_retained_bytes(
            evidence_root,
            prediction_uri,
            field=f"{prefix}PREDICTION_ARTIFACT",
            max_bytes=_MAX_ANCHOR_ARTIFACT_BYTES,
            reference_validator=_observation_reference,
        )
        projection_raw = _read_retained_bytes(
            evidence_root,
            projection_uri,
            field=f"{prefix}PROJECTION_ARTIFACT",
            max_bytes=_MAX_ANCHOR_ARTIFACT_BYTES,
            reference_validator=_observation_reference,
        )
        prediction = _strict_json_object(
            prediction_raw,
            f"{prefix}PREDICTION_ARTIFACT",
        )
        projection = _strict_json_object(
            projection_raw,
            f"{prefix}PROJECTION_ARTIFACT",
        )
        try:
            validate_directional_outcome_projection(projection)
            verify_directional_projection_evidence(
                projection,
                evidence_root=evidence_root,
            )
        except (OutcomeLedgerError, KeyError, TypeError, ValueError) as exc:
            raise MaturityObservationError(
                f"{prefix}PROJECTION_ARTIFACT_INVALID"
            ) from exc

        source_bytes: dict[str, bytes] = {}
        for role in sorted(projection["source_bindings"]):
            binding = projection["source_bindings"][role]
            raw = _read_retained_bytes(
                evidence_root,
                binding["snapshot_uri"],
                field=f"{prefix}{role.upper()}_SOURCE",
                max_bytes=_MAX_ANCHOR_SOURCE_BYTES,
                reference_validator=_retained_snapshot_reference,
            )
            if (
                sha256(raw).hexdigest() != binding["sha256"]
                or len(raw) != binding["size_bytes"]
            ):
                raise MaturityObservationError(
                    f"{prefix}{role.upper()}_SOURCE_BINDING_MISMATCH"
                )
            source_bytes[role] = raw

        try:
            validation = validate_forward_prediction(
                prediction,
                now=datetime.now(timezone.utc),
                equity_source_bytes={
                    role: source_bytes[role]
                    for role in ("cash", "company", "etf", "actions")
                },
                index_source_raw=source_bytes["index"],
                holiday_calendar_raw=source_bytes["holiday_calendar"],
                model_spec_raw=source_bytes["model_spec"],
                expected_previous_event_hash=expected_previous,
            )
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            raise MaturityObservationError(
                f"{prefix}PREDICTION_ARTIFACT_INVALID"
            ) from exc

        prediction_id = validation["prediction_id"]
        if prediction_id in prediction_hashes:
            raise MaturityObservationError(
                f"{prefix}PREDICTION_ID_DUPLICATE"
            )
        forecast = prediction["prediction"]
        receipts = prediction["source_receipts"]
        expected_bindings = {
            role: receipts[role]["sha256"]
            for role in (
                "cash",
                "company",
                "etf",
                "actions",
                "index",
                "holiday_calendar",
            )
        }
        expected_bindings["model_spec"] = prediction["strategy"][
            "model_spec_sha256"
        ]
        if any(
            projection["source_bindings"][role]["sha256"]
            != expected_bindings[role]
            for role in expected_bindings
        ):
            raise MaturityObservationError(
                f"{prefix}PROJECTION_SOURCE_BINDING_MISMATCH"
            )
        expected_projection_values = {
            "prediction_id": prediction_id,
            "prediction_event_hash": validation["event_hash"],
            "symbol": forecast["symbol"],
            "isin": forecast["isin"],
            "forecast_direction": forecast["direction"],
            "issued_at": prediction["issued_at"],
            "source_cutoff_at": prediction["source_cutoff_at"],
            "entry_session_date": prediction["entry_session_date"],
            "due_session_date": prediction["due_session_date"],
            "due_at": prediction["due_at"],
            "entry_reference_close": forecast["entry_reference_close"],
            "entry_source_url": receipts["cash"]["url"],
            "entry_source_hash": receipts["cash"]["sha256"],
            "entry_source_size_bytes": receipts["cash"]["bytes"],
            "entry_source_row_hash": forecast["features"][
                "source_row_sha256"
            ],
            "price_basis": forecast["price_basis"],
        }
        if any(
            projection.get(field) != value
            for field, value in expected_projection_values.items()
        ):
            raise MaturityObservationError(
                f"{prefix}PROJECTION_PREDICTION_BINDING_MISMATCH"
            )

        prediction_hashes[prediction_id] = validation["event_hash"]
        projection_hashes[prediction_id] = projection["projection_hash"]
        expected_previous = validation["event_hash"]
        seen_uris.update({prediction_uri, projection_uri})
    return prediction_hashes, projection_hashes


def _verify_maturity_observation_chain_with_anchors(
    events: list[dict[str, Any]],
    *,
    trusted_prediction_hashes: Mapping[str, str],
    trusted_projection_hashes: Mapping[str, str],
) -> dict[str, Any]:
    """Verify chain order plus independent prediction/projection anchors."""
    if not isinstance(trusted_prediction_hashes, Mapping):
        raise MaturityObservationError("TRUSTED_PREDICTION_HASHES_REQUIRED")
    if not isinstance(trusted_projection_hashes, Mapping):
        raise MaturityObservationError("TRUSTED_PROJECTION_HASHES_REQUIRED")

    previous = MATURITY_LEDGER_GENESIS_HASH
    previous_recorded: datetime | None = None
    seen_record_hashes: set[str] = set()
    seen_uris: set[str] = set()
    latest_cutoff: dict[str, datetime] = {}
    for index, event in enumerate(events):
        prefix = f"ROW_{index}_"
        recorded, cutoff = _validate_maturity_ledger_event(
            event,
            prefix=prefix,
        )
        prediction_id = event["prediction_id"]
        trusted_prediction = trusted_prediction_hashes.get(prediction_id)
        trusted_projection = trusted_projection_hashes.get(prediction_id)
        if trusted_prediction is None:
            raise MaturityObservationError(
                f"{prefix}TRUSTED_PREDICTION_HASH_MISSING"
            )
        if trusted_projection is None:
            raise MaturityObservationError(
                f"{prefix}TRUSTED_PROJECTION_HASH_MISSING"
            )
        if event["prediction_event_hash"] != _sha(
            trusted_prediction,
            f"{prefix}TRUSTED_PREDICTION_HASH",
        ):
            raise MaturityObservationError(
                f"{prefix}PREDICTION_EVENT_HASH_TRUST_MISMATCH"
            )
        if event["projection_hash"] != _sha(
            trusted_projection,
            f"{prefix}TRUSTED_PROJECTION_HASH",
        ):
            raise MaturityObservationError(
                f"{prefix}PROJECTION_HASH_TRUST_MISMATCH"
            )
        if event["previous_hash"] != previous:
            raise MaturityObservationError(f"{prefix}LEDGER_CHAIN_BROKEN")
        if previous_recorded is not None and recorded < previous_recorded:
            raise MaturityObservationError(
                f"{prefix}RECORDED_ORDER_INVALID"
            )
        if event["observation_record_hash"] in seen_record_hashes:
            raise MaturityObservationError(
                f"{prefix}OBSERVATION_RECORD_HASH_DUPLICATE"
            )
        if event["observation_uri"] in seen_uris:
            raise MaturityObservationError(
                f"{prefix}OBSERVATION_URI_DUPLICATE"
            )
        prior_cutoff = latest_cutoff.get(prediction_id)
        if prior_cutoff is not None and cutoff <= prior_cutoff:
            raise MaturityObservationError(
                f"{prefix}SOURCE_CUTOFF_NOT_ADVANCED"
            )
        previous = event["event_hash"]
        previous_recorded = recorded
        latest_cutoff[prediction_id] = cutoff
        seen_record_hashes.add(event["observation_record_hash"])
        seen_uris.add(event["observation_uri"])

    return {
        "status": "VERIFIED" if events else "EMPTY",
        "verification_scope": (
            "HASH_CHAIN_TRUSTED_PREDICTION_PROJECTION_AND_RETAINED_OBSERVATION"
        ),
        "record_count": len(events),
        "head_hash": previous,
        "matured_adjusted_outcomes": 0,
        "performance_metrics_available": False,
        "real_money_ready": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }


def _publication_qualified_manifest_anchors(
    manifest_events: list[dict[str, Any]],
    publication_events: list[dict[str, Any]],
) -> tuple[dict[str, str], dict[str, str], set[str]]:
    receipts = {
        event["prediction_id"]: event for event in publication_events
    }
    prediction_hashes: dict[str, str] = {}
    projection_hashes: dict[str, str] = {}
    blocked: set[str] = set()
    for event in manifest_events:
        prediction_id = event["prediction_id"]
        receipt = receipts.get(prediction_id)
        qualifies = (
            not event["pre_maturity_registered"]
            or (
                receipt is not None
                and receipt["forward_oos_eligible"]
                and receipt["issuance_manifest_event_hash"]
                == event["event_hash"]
            )
        )
        if not qualifies:
            blocked.add(prediction_id)
            continue
        prediction_hashes[prediction_id] = event[
            "prediction_event_hash"
        ]
        projection_hashes[prediction_id] = event["projection_hash"]
    return prediction_hashes, projection_hashes, blocked


def verify_maturity_observation_chain(
    events: list[dict[str, Any]],
    *,
    issuance_manifest_uri: str,
    publication_receipt_uri: str | None = None,
    evidence_root: Path,
) -> dict[str, Any]:
    """Verify maturity against registered and independently published bytes."""
    manifest_events = read_issuance_artifact_manifest(
        issuance_manifest_uri, evidence_root=evidence_root
    )
    publication_events = (
        read_external_publication_receipts(
            publication_receipt_uri,
            issuance_manifest_uri=issuance_manifest_uri,
            evidence_root=evidence_root,
        )
        if publication_receipt_uri is not None
        else []
    )
    prediction_hashes, projection_hashes, blocked = (
        _publication_qualified_manifest_anchors(
            manifest_events, publication_events
        )
    )
    used_prediction_ids = {event.get("prediction_id") for event in events}
    if blocked & used_prediction_ids:
        raise MaturityObservationError(
            "EXTERNAL_PUBLICATION_BEFORE_HORIZON_REQUIRED"
        )
    result = _verify_maturity_observation_chain_with_anchors(
        events,
        trusted_prediction_hashes=prediction_hashes,
        trusted_projection_hashes=projection_hashes,
    )
    result["verification_scope"] = (
        "HASH_CHAIN_ISSUANCE_MANIFEST_REGISTERED_PREDICTION_PROJECTION_"
        "EXTERNAL_PUBLICATION_ELIGIBILITY_GATED_AND_RETAINED_OBSERVATION"
    )
    result["issuance_manifest_record_count"] = len(manifest_events)
    result["issuance_manifest_head_hash"] = (
        manifest_events[-1]["event_hash"]
        if manifest_events
        else ISSUANCE_MANIFEST_GENESIS_HASH
    )
    result["pre_maturity_registration_count"] = sum(
        event["pre_maturity_registered"] for event in manifest_events
    )
    result["historical_after_maturity_registration_count"] = sum(
        not event["pre_maturity_registered"] for event in manifest_events
    )
    result["external_publication_receipt_count"] = len(
        publication_events
    )
    result["forward_oos_publication_eligible_count"] = sum(
        event["forward_oos_eligible"] for event in publication_events
    )
    result["historical_publication_receipt_count"] = sum(
        not event["forward_oos_eligible"] for event in publication_events
    )
    result["pre_maturity_without_eligible_publication_count"] = len(
        blocked
    )
    return result


def _read_retained_bytes(
    evidence_root: Path,
    retained_uri: str,
    *,
    field: str,
    max_bytes: int,
    reference_validator: Callable[[Any, str], str],
) -> bytes:
    """Read one retained regular file without following path indirection."""
    try:
        root = Path(evidence_root).resolve(strict=True)
        if not root.is_dir():
            raise MaturityObservationError("EVIDENCE_ROOT_NOT_DIRECTORY")
        parts = reference_validator(retained_uri, f"{field}_URI").split("/")

        def checked_path() -> Path:
            candidate = root
            for part in parts:
                candidate = candidate / part
                info = candidate.lstat()
                reparse = getattr(info, "st_file_attributes", 0) & getattr(
                    stat,
                    "FILE_ATTRIBUTE_REPARSE_POINT",
                    0,
                )
                if stat.S_ISLNK(info.st_mode) or reparse:
                    raise MaturityObservationError(
                        f"{field}_RETAINED_LINK_FORBIDDEN"
                    )
            candidate.resolve(strict=True).relative_to(root)
            return candidate

        path = checked_path()
        before = path.stat()
        if not stat.S_ISREG(before.st_mode):
            raise MaturityObservationError(
                f"{field}_RETAINED_NOT_REGULAR"
            )
        flags = (
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0)
            | getattr(os, "O_BINARY", 0)
        )
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if (
                not stat.S_ISREG(opened.st_mode)
                or (before.st_dev, before.st_ino)
                != (opened.st_dev, opened.st_ino)
            ):
                raise MaturityObservationError(
                    f"{field}_RETAINED_CHANGED_DURING_READ"
                )
            raw = handle.read(max_bytes + 1)
            after = os.fstat(handle.fileno())
            retained = checked_path().stat()

        def identity(info: os.stat_result) -> tuple[int, ...]:
            return (
                info.st_dev,
                info.st_ino,
                info.st_size,
                info.st_mtime_ns,
                info.st_ctime_ns,
            )

        if (
            identity(opened) != identity(after)
            or identity(after) != identity(retained)
        ):
            raise MaturityObservationError(
                f"{field}_RETAINED_CHANGED_DURING_READ"
            )
        if len(raw) > max_bytes:
            raise MaturityObservationError(f"{field}_RETAINED_TOO_LARGE")
        return raw
    except MaturityObservationError:
        raise
    except (LedgerError, OSError, ValueError) as exc:
        raise MaturityObservationError(
            f"{field}_RETAINED_UNAVAILABLE"
        ) from exc


def _prospective_storage_path(
    evidence_root: Path,
    retained_uri: str,
    *,
    field: str,
    suffix: str,
    must_not_exist: bool,
) -> Path:
    """Resolve a regular retained target without following path indirection."""
    try:
        root = Path(evidence_root).resolve(strict=True)
        if not root.is_dir():
            raise MaturityObservationError("EVIDENCE_ROOT_NOT_DIRECTORY")
        reference = _observation_reference(retained_uri, f"{field}_URI")
        if not reference.endswith(suffix):
            raise MaturityObservationError(f"{field}_URI_INVALID")
        candidate = root
        for part in reference.split("/")[:-1]:
            candidate = candidate / part
            info = candidate.lstat()
            reparse = getattr(info, "st_file_attributes", 0) & getattr(
                stat,
                "FILE_ATTRIBUTE_REPARSE_POINT",
                0,
            )
            if stat.S_ISLNK(info.st_mode) or reparse:
                raise MaturityObservationError(
                    f"{field}_PARENT_LINK_FORBIDDEN"
                )
            if not stat.S_ISDIR(info.st_mode):
                raise MaturityObservationError(
                    f"{field}_PARENT_NOT_DIRECTORY"
                )
        target = candidate / reference.split("/")[-1]
        target.parent.resolve(strict=True).relative_to(root)
        try:
            info = target.lstat()
        except FileNotFoundError:
            info = None
        if info is not None:
            reparse = getattr(info, "st_file_attributes", 0) & getattr(
                stat,
                "FILE_ATTRIBUTE_REPARSE_POINT",
                0,
            )
            if stat.S_ISLNK(info.st_mode) or reparse:
                raise MaturityObservationError(f"{field}_LINK_FORBIDDEN")
            if must_not_exist:
                raise MaturityObservationError(
                    f"{field}_ALREADY_EXISTS_UNREGISTERED"
                )
            if not stat.S_ISREG(info.st_mode):
                raise MaturityObservationError(f"{field}_NOT_REGULAR")
        return target
    except MaturityObservationError:
        raise
    except (OSError, ValueError) as exc:
        raise MaturityObservationError(f"{field}_PATH_INVALID") from exc


def _write_new_prospective_artifact(
    path: Path,
    raw: bytes,
    *,
    field: str,
) -> None:
    """Create one transaction-owned artifact without overwriting anything."""
    descriptor: int | None = None
    created = False
    try:
        flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_BINARY", 0)
        )
        descriptor = os.open(path, flags, 0o644)
        created = True
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        if descriptor is not None:
            os.close(descriptor)
        if created:
            path.unlink(missing_ok=True)
        raise MaturityObservationError(f"{field}_WRITE_FAILED") from exc


def _fsync_directory(path: Path) -> None:
    """Best-effort directory durability on platforms that support it."""
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    try:
        descriptor = os.open(path, os.O_RDONLY | directory_flag)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _replace_manifest_atomically(
    path: Path,
    payload: bytes,
    *,
    failure_code: str = "ISSUANCE_MANIFEST_COMMIT_FAILED",
) -> None:
    """Make the fully validated manifest version the transaction commit point."""
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    except OSError as exc:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)
        raise MaturityObservationError(failure_code) from exc


def _manifest_storage_path(path: Path, evidence_root: Path) -> tuple[Path, str]:
    """Bind a manifest filesystem path to its retained repository URI."""
    try:
        root = Path(evidence_root).resolve(strict=True)
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        parent = candidate.parent.resolve(strict=True)
        target = parent / candidate.name
        relative = target.relative_to(root).as_posix()
    except (OSError, ValueError) as exc:
        raise MaturityObservationError(
            "ISSUANCE_MANIFEST_PATH_INVALID"
        ) from exc
    verified = _prospective_storage_path(
        root,
        relative,
        field="ISSUANCE_MANIFEST",
        suffix=".ndjson",
        must_not_exist=False,
    )
    return verified, relative


def verify_issuance_artifact_manifest(
    events: list[dict[str, Any]],
    *,
    evidence_root: Path,
) -> dict[str, Any]:
    """Verify manifest order, exact artifact bytes and full source replay."""
    if not isinstance(events, list):
        raise MaturityObservationError("ISSUANCE_MANIFEST_LIST_REQUIRED")
    previous = ISSUANCE_MANIFEST_GENESIS_HASH
    previous_registered: datetime | None = None
    seen_ids: set[str] = set()
    seen_uris: set[str] = set()
    anchor_artifacts: list[dict[str, str]] = []
    pre_maturity_count = 0
    historical_count = 0
    for index, event in enumerate(events):
        prefix = f"ISSUANCE_ROW_{index}_"
        _, _, registered = _validate_issuance_manifest_event(
            event, prefix=prefix
        )
        if event["previous_hash"] != previous:
            raise MaturityObservationError(
                f"{prefix}ISSUANCE_MANIFEST_CHAIN_BROKEN"
            )
        if (
            previous_registered is not None
            and registered < previous_registered
        ):
            raise MaturityObservationError(
                f"{prefix}ISSUANCE_REGISTERED_ORDER_INVALID"
            )
        if event["prediction_id"] in seen_ids:
            raise MaturityObservationError(
                f"{prefix}ISSUANCE_PREDICTION_ID_DUPLICATE"
            )
        if (
            event["prediction_uri"] in seen_uris
            or event["projection_uri"] in seen_uris
        ):
            raise MaturityObservationError(
                f"{prefix}ISSUANCE_ARTIFACT_URI_DUPLICATE"
            )
        prediction_raw = _read_retained_bytes(
            evidence_root,
            event["prediction_uri"],
            field=f"{prefix}PREDICTION_ARTIFACT",
            max_bytes=_MAX_ANCHOR_ARTIFACT_BYTES,
            reference_validator=_observation_reference,
        )
        projection_raw = _read_retained_bytes(
            evidence_root,
            event["projection_uri"],
            field=f"{prefix}PROJECTION_ARTIFACT",
            max_bytes=_MAX_ANCHOR_ARTIFACT_BYTES,
            reference_validator=_observation_reference,
        )
        if (
            len(prediction_raw) != event["prediction_size_bytes"]
            or sha256(prediction_raw).hexdigest()
            != event["prediction_file_sha256"]
        ):
            raise MaturityObservationError(
                f"{prefix}PREDICTION_ARTIFACT_MANIFEST_MISMATCH"
            )
        if (
            len(projection_raw) != event["projection_size_bytes"]
            or sha256(projection_raw).hexdigest()
            != event["projection_file_sha256"]
        ):
            raise MaturityObservationError(
                f"{prefix}PROJECTION_ARTIFACT_MANIFEST_MISMATCH"
            )
        expected = build_issuance_artifact_event(
            prediction_bytes=prediction_raw,
            projection_bytes=projection_raw,
            prediction_uri=event["prediction_uri"],
            projection_uri=event["projection_uri"],
            registered_at=registered,
            previous_hash=previous,
        )
        if event != expected:
            raise MaturityObservationError(
                f"{prefix}ISSUANCE_ARTIFACT_BINDING_MISMATCH"
            )
        anchor_artifacts.append({
            "prediction_uri": event["prediction_uri"],
            "projection_uri": event["projection_uri"],
        })
        previous = event["event_hash"]
        previous_registered = registered
        seen_ids.add(event["prediction_id"])
        seen_uris.update({
            event["prediction_uri"], event["projection_uri"]
        })
        if event["pre_maturity_registered"]:
            pre_maturity_count += 1
        else:
            historical_count += 1
    prediction_hashes, projection_hashes = (
        _derive_maturity_artifact_anchors(
            anchor_artifacts=anchor_artifacts,
            evidence_root=evidence_root,
        )
    )
    for index, event in enumerate(events):
        if (
            prediction_hashes.get(event["prediction_id"])
            != event["prediction_event_hash"]
            or projection_hashes.get(event["prediction_id"])
            != event["projection_hash"]
        ):
            raise MaturityObservationError(
                f"ISSUANCE_ROW_{index}_REPLAY_HASH_MISMATCH"
            )
    return {
        "status": "VERIFIED" if events else "EMPTY",
        "record_count": len(events),
        "head_hash": previous,
        "pre_maturity_registration_count": pre_maturity_count,
        "historical_after_maturity_registration_count": historical_count,
        "market_validation_claimed": False,
        "performance_metrics_available": False,
        "real_money_ready": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }


def _read_issuance_artifact_manifest_unlocked(
    manifest_uri: str,
    *,
    evidence_root: Path,
) -> list[dict[str, Any]]:
    reference = _observation_reference(
        manifest_uri, "ISSUANCE_MANIFEST_URI"
    )
    if not reference.endswith(".ndjson"):
        raise MaturityObservationError("ISSUANCE_MANIFEST_URI_INVALID")
    raw = _read_retained_bytes(
        evidence_root,
        reference,
        field="ISSUANCE_MANIFEST",
        max_bytes=_MAX_ISSUANCE_MANIFEST_BYTES,
        reference_validator=_observation_reference,
    )
    if not raw.endswith(b"\n"):
        raise MaturityObservationError("ISSUANCE_MANIFEST_TRUNCATED")
    events = [
        _strict_json_object(line, "ISSUANCE_MANIFEST_ROW")
        for line in raw.splitlines()
        if line.strip()
    ]
    verify_issuance_artifact_manifest(events, evidence_root=evidence_root)
    return events


def read_issuance_artifact_manifest(
    manifest_uri: str,
    *,
    evidence_root: Path,
) -> list[dict[str, Any]]:
    """Read only a complete manifest whose artifact bytes fully replay."""
    return _read_issuance_artifact_manifest_unlocked(
        manifest_uri, evidence_root=evidence_root
    )


def publish_prospective_issuance(
    path: Path,
    *,
    prediction_bytes: bytes,
    projection_bytes: bytes,
    prediction_uri: str,
    projection_uri: str,
    evidence_root: Path,
) -> dict[str, Any]:
    """Publish forecast artifacts with a system-timed manifest commit.

    The manifest replacement is the acceptance commit point.  Artifacts are
    created without overwrite while the manifest lock is held, the complete
    prospective chain is replayed, and only then is the validated manifest
    version installed atomically.  Orphan files are never trusted because all
    readers require the manifest entry.
    """
    manifest_path, manifest_uri = _manifest_storage_path(
        path, evidence_root
    )
    created_paths: list[Path] = []
    committed = False
    with _ledger_lock(manifest_path, exclusive=True):
        if manifest_path.exists():
            existing_raw = _read_retained_bytes(
                evidence_root,
                manifest_uri,
                field="ISSUANCE_MANIFEST",
                max_bytes=_MAX_ISSUANCE_MANIFEST_BYTES,
                reference_validator=_observation_reference,
            )
            if existing_raw and not existing_raw.endswith(b"\n"):
                raise MaturityObservationError(
                    "ISSUANCE_MANIFEST_TRUNCATED"
                )
            events = [
                _strict_json_object(line, "ISSUANCE_MANIFEST_ROW")
                for line in existing_raw.splitlines()
                if line.strip()
            ]
            verify_issuance_artifact_manifest(
                events, evidence_root=evidence_root
            )
        else:
            existing_raw = b""
            events = []

        registered_at = _system_utc_now()
        if (
            registered_at.tzinfo is None
            or registered_at.utcoffset() is None
        ):
            raise MaturityObservationError(
                "SYSTEM_REGISTRATION_TIME_INVALID"
            )
        event = build_issuance_artifact_event(
            prediction_bytes=prediction_bytes,
            projection_bytes=projection_bytes,
            prediction_uri=prediction_uri,
            projection_uri=projection_uri,
            registered_at=registered_at,
            previous_hash=(
                events[-1]["event_hash"]
                if events
                else ISSUANCE_MANIFEST_GENESIS_HASH
            ),
        )
        if not event["pre_maturity_registered"]:
            raise MaturityObservationError(
                "PROSPECTIVE_ISSUANCE_AFTER_HORIZON"
            )
        if any(
            prior["prediction_id"] == event["prediction_id"]
            for prior in events
        ):
            raise MaturityObservationError(
                "PROSPECTIVE_PREDICTION_ID_DUPLICATE"
            )
        used_uris = {
            uri
            for prior in events
            for uri in (prior["prediction_uri"], prior["projection_uri"])
        }
        if prediction_uri in used_uris or projection_uri in used_uris:
            raise MaturityObservationError(
                "PROSPECTIVE_ARTIFACT_URI_DUPLICATE"
            )

        prediction_path = _prospective_storage_path(
            evidence_root,
            prediction_uri,
            field="PREDICTION_ARTIFACT",
            suffix=".json",
            must_not_exist=True,
        )
        projection_path = _prospective_storage_path(
            evidence_root,
            projection_uri,
            field="PROJECTION_ARTIFACT",
            suffix=".json",
            must_not_exist=True,
        )
        try:
            _write_new_prospective_artifact(
                prediction_path,
                prediction_bytes,
                field="PREDICTION_ARTIFACT",
            )
            created_paths.append(prediction_path)
            _write_new_prospective_artifact(
                projection_path,
                projection_bytes,
                field="PROJECTION_ARTIFACT",
            )
            created_paths.append(projection_path)
            candidate = [*events, event]
            verify_issuance_artifact_manifest(
                candidate, evidence_root=evidence_root
            )
            encoded_event = json.dumps(
                event,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            ).encode("utf-8")
            payload = existing_raw + encoded_event + b"\n"
            if len(payload) > _MAX_ISSUANCE_MANIFEST_BYTES:
                raise MaturityObservationError(
                    "ISSUANCE_MANIFEST_RETAINED_TOO_LARGE"
                )
            _replace_manifest_atomically(manifest_path, payload)
            committed = True
            return event
        finally:
            if not committed:
                for created_path in reversed(created_paths):
                    created_path.unlink(missing_ok=True)


def append_issuance_artifact_manifest(
    path: Path,
    *,
    prediction_uri: str,
    projection_uri: str,
    registered_at: datetime,
    evidence_root: Path,
) -> dict[str, Any]:
    """Import an already-retained historical pair without forward claims."""
    with _ledger_lock(path, exclusive=True):
        if path.exists():
            raw = path.read_bytes()
            if raw and not raw.endswith(b"\n"):
                raise MaturityObservationError(
                    "ISSUANCE_MANIFEST_TRUNCATED"
                )
            events = [
                _strict_json_object(line, "ISSUANCE_MANIFEST_ROW")
                for line in raw.splitlines()
                if line.strip()
            ]
            verify_issuance_artifact_manifest(
                events, evidence_root=evidence_root
            )
        else:
            events = []
        prediction_raw = _read_retained_bytes(
            evidence_root,
            prediction_uri,
            field="PREDICTION_ARTIFACT",
            max_bytes=_MAX_ANCHOR_ARTIFACT_BYTES,
            reference_validator=_observation_reference,
        )
        projection_raw = _read_retained_bytes(
            evidence_root,
            projection_uri,
            field="PROJECTION_ARTIFACT",
            max_bytes=_MAX_ANCHOR_ARTIFACT_BYTES,
            reference_validator=_observation_reference,
        )
        event = build_issuance_artifact_event(
            prediction_bytes=prediction_raw,
            projection_bytes=projection_raw,
            prediction_uri=prediction_uri,
            projection_uri=projection_uri,
            registered_at=registered_at,
            previous_hash=(
                events[-1]["event_hash"]
                if events
                else ISSUANCE_MANIFEST_GENESIS_HASH
            ),
        )
        if event["pre_maturity_registered"]:
            raise MaturityObservationError(
                "PRE_MATURITY_REGISTRATION_REQUIRES_PROSPECTIVE_TRANSACTION"
            )
        candidate = [*events, event]
        verify_issuance_artifact_manifest(
            candidate, evidence_root=evidence_root
        )
        payload = json.dumps(
            event,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(payload + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event


def _canonical_publication_receipt_event(
    record: Mapping[str, Any],
) -> bytes:
    return _canonical(
        {key: value for key, value in record.items() if key != "event_hash"}
    )


def _publication_attestation(
    manifest_event: Mapping[str, Any],
) -> dict[str, Any]:
    _validate_issuance_manifest_event(manifest_event)
    return {
        "schema_version": _PUBLICATION_ATTESTATION_SCHEMA_VERSION,
        "prediction_id": manifest_event["prediction_id"],
        "issuance_manifest_event_hash": manifest_event["event_hash"],
        "prediction_event_hash": manifest_event["prediction_event_hash"],
        "projection_hash": manifest_event["projection_hash"],
        "registered_at": manifest_event["registered_at"],
        "due_at": manifest_event["due_at"],
        "execution_mode": "ANALYZE_PAPER",
        "market_validation_claimed": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }


def github_publication_comment_body(
    manifest_event: Mapping[str, Any],
) -> str:
    """Return the exact machine-readable body to publish on GitHub."""
    return _PUBLICATION_BODY_PREFIX + _canonical(
        _publication_attestation(manifest_event)
    ).decode("ascii")


def _github_publication_request_json(
    method: str,
    url: str,
    *,
    token: str,
    payload: bytes | None = None,
) -> bytes:
    """Issue one bounded GitHub JSON request without exposing credentials."""
    if (
        not isinstance(token, str)
        or not token
        or token != token.strip()
        or len(token) > 1024
        or "\r" in token
        or "\n" in token
    ):
        raise MaturityObservationError(
            "GITHUB_PUBLICATION_TOKEN_INVALID"
        )
    create_url = (
        "https://api.github.com/repos/"
        f"{_PUBLICATION_REPOSITORY}/issues/"
        f"{_PUBLICATION_PULL_REQUEST}/comments"
    )
    comment_url_prefix = (
        "https://api.github.com/repos/"
        f"{_PUBLICATION_REPOSITORY}/issues/comments/"
    )
    if method == "POST":
        if url != create_url or not isinstance(payload, bytes) or not payload:
            raise MaturityObservationError(
                "GITHUB_PUBLICATION_POST_REQUEST_INVALID"
            )
        expected_status = 201
        failure_code = "GITHUB_PUBLICATION_POST_FAILED"
    elif method == "GET":
        suffix = url.removeprefix(comment_url_prefix)
        if (
            url == suffix
            or not suffix.isdigit()
            or int(suffix) <= 0
            or payload is not None
        ):
            raise MaturityObservationError(
                "GITHUB_PUBLICATION_FETCH_REQUEST_INVALID"
            )
        expected_status = 200
        failure_code = "GITHUB_PUBLICATION_FETCH_FAILED"
    else:
        raise MaturityObservationError(
            "GITHUB_PUBLICATION_METHOD_INVALID"
        )
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": _GITHUB_PUBLICATION_USER_AGENT,
        "X-GitHub-Api-Version": _GITHUB_API_VERSION,
    }
    if method == "POST":
        headers["Content-Type"] = "application/json"
    request = Request(
        url,
        data=payload,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=30) as response:
            status = response.getcode()
            final_url = response.geturl()
            content_type = response.headers.get("Content-Type", "")
            raw = response.read(_MAX_PUBLICATION_RECEIPT_BYTES + 1)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise MaturityObservationError(failure_code) from exc
    if status != expected_status or final_url != url:
        raise MaturityObservationError(failure_code)
    if content_type.split(";", 1)[0].strip().lower() != "application/json":
        raise MaturityObservationError(
            "GITHUB_PUBLICATION_RESPONSE_CONTENT_TYPE_INVALID"
        )
    if not raw or len(raw) > _MAX_PUBLICATION_RECEIPT_BYTES:
        raise MaturityObservationError(
            "GITHUB_PUBLICATION_RESPONSE_BYTES_INVALID"
        )
    _strict_json_object(raw, "GITHUB_PUBLICATION_RESPONSE")
    return raw


def _parse_publication_attestation(body: Any) -> dict[str, Any]:
    if not isinstance(body, str) or not body.startswith(
        _PUBLICATION_BODY_PREFIX
    ):
        raise MaturityObservationError(
            "PUBLICATION_ATTESTATION_PREFIX_INVALID"
        )
    attestation = _strict_json_object(
        body[len(_PUBLICATION_BODY_PREFIX):].encode("utf-8"),
        "PUBLICATION_ATTESTATION",
    )
    if set(attestation) != _PUBLICATION_ATTESTATION_FIELDS:
        raise MaturityObservationError(
            "PUBLICATION_ATTESTATION_FIELDS_INVALID"
        )
    if (
        attestation.get("schema_version")
        != _PUBLICATION_ATTESTATION_SCHEMA_VERSION
        or attestation.get("execution_mode") != "ANALYZE_PAPER"
    ):
        raise MaturityObservationError(
            "PUBLICATION_ATTESTATION_SCHEMA_INVALID"
        )
    for field in (
        "market_validation_claimed",
        "live_trading_enabled",
        "order_placement_allowed",
    ):
        if attestation.get(field) is not False:
            raise MaturityObservationError(
                f"PUBLICATION_ATTESTATION_{field.upper()}_INVALID"
            )
    return attestation


def _validate_publication_receipt_event(
    event: Mapping[str, Any],
    *,
    prefix: str = "",
    allow_unhashed: bool = False,
) -> tuple[datetime, datetime, datetime]:
    expected_fields = (
        _PUBLICATION_RECEIPT_FIELDS - {"event_hash"}
        if allow_unhashed
        else _PUBLICATION_RECEIPT_FIELDS
    )
    if not isinstance(event, dict) or set(event) != expected_fields:
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_RECEIPT_FIELDS_INVALID"
        )
    if (
        event.get("schema_version")
        != PUBLICATION_RECEIPT_SCHEMA_VERSION
        or event.get("event_type") != _PUBLICATION_RECEIPT_EVENT_TYPE
    ):
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_RECEIPT_SCHEMA_INVALID"
        )
    prediction_id = event.get("prediction_id")
    if (
        not isinstance(prediction_id, str)
        or not prediction_id
        or prediction_id != prediction_id.strip()
        or len(prediction_id) > 128
    ):
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_PREDICTION_ID_INVALID"
        )
    for field in (
        "issuance_manifest_event_hash",
        "prediction_event_hash",
        "projection_hash",
        "source_sha256",
        "attestation_sha256",
        "previous_hash",
    ):
        digest = _sha(event.get(field), f"{prefix}{field.upper()}")
        if event.get(field) != digest:
            raise MaturityObservationError(
                f"{prefix}{field.upper()}_INVALID"
            )
    if (
        event.get("provider") != _PUBLICATION_PROVIDER
        or event.get("repository") != _PUBLICATION_REPOSITORY
        or event.get("pull_request_number")
        != _PUBLICATION_PULL_REQUEST
        or event.get("author_login") != _PUBLICATION_AUTHOR_LOGIN
    ):
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_AUTHORITY_INVALID"
        )
    comment_id = event.get("comment_id")
    if (
        isinstance(comment_id, bool)
        or not isinstance(comment_id, int)
        or comment_id <= 0
    ):
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_COMMENT_ID_INVALID"
        )
    source_url = (
        "https://api.github.com/repos/"
        f"{_PUBLICATION_REPOSITORY}/issues/comments/{comment_id}"
    )
    html_url = (
        f"https://github.com/{_PUBLICATION_REPOSITORY}/pull/"
        f"{_PUBLICATION_PULL_REQUEST}#issuecomment-{comment_id}"
    )
    if (
        event.get("source_url") != source_url
        or event.get("source_html_url") != html_url
    ):
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_SOURCE_URL_INVALID"
        )
    snapshot_uri = _observation_reference(
        event.get("source_snapshot_uri"),
        f"{prefix}PUBLICATION_SOURCE_SNAPSHOT",
    )
    if (
        event.get("source_snapshot_uri") != snapshot_uri
        or not snapshot_uri.endswith(".json")
    ):
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_SOURCE_SNAPSHOT_URI_INVALID"
        )
    source_size = event.get("source_size_bytes")
    if (
        isinstance(source_size, bool)
        or not isinstance(source_size, int)
        or source_size <= 0
        or source_size > _MAX_PUBLICATION_RECEIPT_BYTES
    ):
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_SOURCE_SIZE_INVALID"
        )
    due = _time(event.get("due_at"), f"{prefix}PUBLICATION_DUE_AT")
    published = _time(
        event.get("published_at"),
        f"{prefix}PUBLICATION_PUBLISHED_AT",
    )
    updated = _time(
        event.get("source_updated_at"),
        f"{prefix}PUBLICATION_SOURCE_UPDATED_AT",
    )
    observed = _time(
        event.get("first_observed_at"),
        f"{prefix}PUBLICATION_FIRST_OBSERVED_AT",
    )
    if updated != published:
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_EDITED_COMMENT_FORBIDDEN"
        )
    if observed < published:
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_OBSERVED_BEFORE_PUBLISHED"
        )
    eligible = event.get("forward_oos_eligible")
    if type(eligible) is not bool:
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_ELIGIBILITY_INVALID"
        )
    status = (
        "INDEPENDENT_GITHUB_PUBLICATION_BEFORE_HORIZON"
        if eligible
        else "HISTORICAL_PUBLICATION_NOT_FORWARD_OOS"
    )
    if (
        event.get("publication_status") != status
        or (eligible and not published < due)
    ):
        raise MaturityObservationError(
            f"{prefix}PUBLICATION_STATUS_INVALID"
        )
    for field in (
        "market_validation_claimed",
        "performance_metrics_available",
        "real_money_ready",
        "live_trading_enabled",
        "order_placement_allowed",
    ):
        if event.get(field) is not False:
            raise MaturityObservationError(
                f"{prefix}{field.upper()}_INVALID"
            )
    if not allow_unhashed:
        expected_hash = sha256(
            _canonical_publication_receipt_event(event)
        ).hexdigest()
        if event.get("event_hash") != expected_hash:
            raise MaturityObservationError(
                f"{prefix}PUBLICATION_RECEIPT_HASH_MISMATCH"
            )
    return published, observed, due


def build_external_publication_receipt_event(
    *,
    manifest_event: Mapping[str, Any],
    source_bytes: bytes,
    source_snapshot_uri: str,
    first_observed_at: datetime,
    previous_hash: str,
) -> dict[str, Any]:
    """Bind an issuance event to an unedited GitHub server timestamp."""
    _, due, registered = _validate_issuance_manifest_event(manifest_event)
    if (
        not isinstance(source_bytes, bytes)
        or not source_bytes
        or len(source_bytes) > _MAX_PUBLICATION_RECEIPT_BYTES
    ):
        raise MaturityObservationError(
            "PUBLICATION_SOURCE_BYTES_INVALID"
        )
    source = _strict_json_object(source_bytes, "PUBLICATION_SOURCE")
    comment_id = source.get("id")
    if (
        isinstance(comment_id, bool)
        or not isinstance(comment_id, int)
        or comment_id <= 0
    ):
        raise MaturityObservationError("PUBLICATION_COMMENT_ID_INVALID")
    source_url = (
        "https://api.github.com/repos/"
        f"{_PUBLICATION_REPOSITORY}/issues/comments/{comment_id}"
    )
    issue_url = (
        "https://api.github.com/repos/"
        f"{_PUBLICATION_REPOSITORY}/issues/"
        f"{_PUBLICATION_PULL_REQUEST}"
    )
    html_url = (
        f"https://github.com/{_PUBLICATION_REPOSITORY}/pull/"
        f"{_PUBLICATION_PULL_REQUEST}#issuecomment-{comment_id}"
    )
    if (
        source.get("url") != source_url
        or source.get("issue_url") != issue_url
        or source.get("html_url") != html_url
    ):
        raise MaturityObservationError("PUBLICATION_SOURCE_URL_INVALID")
    user = source.get("user")
    if (
        not isinstance(user, dict)
        or user.get("login") != _PUBLICATION_AUTHOR_LOGIN
        or user.get("type") != "User"
        or isinstance(user.get("id"), bool)
        or not isinstance(user.get("id"), int)
        or user.get("id") <= 0
        or source.get("author_association") != "OWNER"
    ):
        raise MaturityObservationError("PUBLICATION_AUTHOR_INVALID")
    published = _time(source.get("created_at"), "PUBLICATION_CREATED_AT")
    updated = _time(source.get("updated_at"), "PUBLICATION_UPDATED_AT")
    if (
        source.get("created_at") != source.get("updated_at")
        or published != updated
    ):
        raise MaturityObservationError(
            "PUBLICATION_EDITED_COMMENT_FORBIDDEN"
        )
    if published < registered:
        raise MaturityObservationError(
            "PUBLICATION_PRECEDES_ISSUANCE_MANIFEST"
        )
    if (
        first_observed_at.tzinfo is None
        or first_observed_at.utcoffset() is None
    ):
        raise MaturityObservationError(
            "PUBLICATION_FIRST_OBSERVED_TIMEZONE_REQUIRED"
        )
    observed = first_observed_at.astimezone(timezone.utc)
    if observed < published:
        raise MaturityObservationError(
            "PUBLICATION_OBSERVED_BEFORE_PUBLISHED"
        )
    body = source.get("body")
    attestation = _parse_publication_attestation(body)
    if attestation != _publication_attestation(manifest_event):
        raise MaturityObservationError(
            "PUBLICATION_ATTESTATION_MANIFEST_MISMATCH"
        )
    if body != github_publication_comment_body(manifest_event):
        raise MaturityObservationError(
            "PUBLICATION_ATTESTATION_NOT_CANONICAL"
        )
    eligible = (
        manifest_event["pre_maturity_registered"]
        and published < due
    )
    event = {
        "schema_version": PUBLICATION_RECEIPT_SCHEMA_VERSION,
        "event_type": _PUBLICATION_RECEIPT_EVENT_TYPE,
        "prediction_id": manifest_event["prediction_id"],
        "issuance_manifest_event_hash": manifest_event["event_hash"],
        "prediction_event_hash": manifest_event["prediction_event_hash"],
        "projection_hash": manifest_event["projection_hash"],
        "due_at": manifest_event["due_at"],
        "provider": _PUBLICATION_PROVIDER,
        "repository": _PUBLICATION_REPOSITORY,
        "pull_request_number": _PUBLICATION_PULL_REQUEST,
        "comment_id": comment_id,
        "author_login": _PUBLICATION_AUTHOR_LOGIN,
        "published_at": source["created_at"],
        "source_updated_at": source["updated_at"],
        "first_observed_at": observed.isoformat(),
        "source_url": source_url,
        "source_html_url": html_url,
        "source_snapshot_uri": _observation_reference(
            source_snapshot_uri,
            "PUBLICATION_SOURCE_SNAPSHOT_URI",
        ),
        "source_sha256": sha256(source_bytes).hexdigest(),
        "source_size_bytes": len(source_bytes),
        "attestation_sha256": sha256(body.encode("utf-8")).hexdigest(),
        "publication_status": (
            "INDEPENDENT_GITHUB_PUBLICATION_BEFORE_HORIZON"
            if eligible
            else "HISTORICAL_PUBLICATION_NOT_FORWARD_OOS"
        ),
        "forward_oos_eligible": eligible,
        "previous_hash": _sha(previous_hash, "PREVIOUS_HASH"),
        "market_validation_claimed": False,
        "performance_metrics_available": False,
        "real_money_ready": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    _validate_publication_receipt_event(event, allow_unhashed=True)
    event["event_hash"] = sha256(
        _canonical_publication_receipt_event(event)
    ).hexdigest()
    _validate_publication_receipt_event(event)
    return event


def _publication_receipt_storage_path(
    path: Path,
    evidence_root: Path,
) -> tuple[Path, str]:
    try:
        root = Path(evidence_root).resolve(strict=True)
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        parent = candidate.parent.resolve(strict=True)
        target = parent / candidate.name
        relative = target.relative_to(root).as_posix()
    except (OSError, ValueError) as exc:
        raise MaturityObservationError(
            "PUBLICATION_RECEIPT_PATH_INVALID"
        ) from exc
    verified = _prospective_storage_path(
        root,
        relative,
        field="PUBLICATION_RECEIPT_LEDGER",
        suffix=".ndjson",
        must_not_exist=False,
    )
    return verified, relative


def verify_external_publication_receipts(
    events: list[dict[str, Any]],
    *,
    issuance_manifest_uri: str,
    evidence_root: Path,
) -> dict[str, Any]:
    """Replay exact GitHub response bytes against issuance events."""
    if not isinstance(events, list):
        raise MaturityObservationError(
            "PUBLICATION_RECEIPT_LIST_REQUIRED"
        )
    manifest_events = read_issuance_artifact_manifest(
        issuance_manifest_uri, evidence_root=evidence_root
    )
    manifest_by_hash = {
        event["event_hash"]: event for event in manifest_events
    }
    previous = PUBLICATION_RECEIPT_GENESIS_HASH
    previous_observed: datetime | None = None
    seen_predictions: set[str] = set()
    seen_comments: set[int] = set()
    seen_snapshots: set[str] = set()
    forward_count = 0
    historical_count = 0
    for index, event in enumerate(events):
        prefix = f"PUBLICATION_ROW_{index}_"
        _, observed, _ = _validate_publication_receipt_event(
            event, prefix=prefix
        )
        if event["previous_hash"] != previous:
            raise MaturityObservationError(
                f"{prefix}PUBLICATION_RECEIPT_CHAIN_BROKEN"
            )
        if previous_observed is not None and observed < previous_observed:
            raise MaturityObservationError(
                f"{prefix}PUBLICATION_OBSERVED_ORDER_INVALID"
            )
        if event["prediction_id"] in seen_predictions:
            raise MaturityObservationError(
                f"{prefix}PUBLICATION_PREDICTION_ID_DUPLICATE"
            )
        if event["comment_id"] in seen_comments:
            raise MaturityObservationError(
                f"{prefix}PUBLICATION_COMMENT_ID_DUPLICATE"
            )
        if event["source_snapshot_uri"] in seen_snapshots:
            raise MaturityObservationError(
                f"{prefix}PUBLICATION_SOURCE_SNAPSHOT_DUPLICATE"
            )
        manifest_event = manifest_by_hash.get(
            event["issuance_manifest_event_hash"]
        )
        if manifest_event is None:
            raise MaturityObservationError(
                f"{prefix}PUBLICATION_MANIFEST_EVENT_MISSING"
            )
        source_raw = _read_retained_bytes(
            evidence_root,
            event["source_snapshot_uri"],
            field=f"{prefix}PUBLICATION_SOURCE",
            max_bytes=_MAX_PUBLICATION_RECEIPT_BYTES,
            reference_validator=_observation_reference,
        )
        if (
            len(source_raw) != event["source_size_bytes"]
            or sha256(source_raw).hexdigest() != event["source_sha256"]
        ):
            raise MaturityObservationError(
                f"{prefix}PUBLICATION_SOURCE_HASH_OR_SIZE_MISMATCH"
            )
        expected = build_external_publication_receipt_event(
            manifest_event=manifest_event,
            source_bytes=source_raw,
            source_snapshot_uri=event["source_snapshot_uri"],
            first_observed_at=observed,
            previous_hash=previous,
        )
        if event != expected:
            raise MaturityObservationError(
                f"{prefix}PUBLICATION_RECEIPT_BINDING_MISMATCH"
            )
        previous = event["event_hash"]
        previous_observed = observed
        seen_predictions.add(event["prediction_id"])
        seen_comments.add(event["comment_id"])
        seen_snapshots.add(event["source_snapshot_uri"])
        if event["forward_oos_eligible"]:
            forward_count += 1
        else:
            historical_count += 1
    return {
        "status": "VERIFIED" if events else "EMPTY",
        "record_count": len(events),
        "head_hash": previous,
        "forward_oos_eligible_count": forward_count,
        "historical_publication_count": historical_count,
        "market_validation_claimed": False,
        "performance_metrics_available": False,
        "real_money_ready": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }


def _read_external_publication_receipts_unlocked(
    receipt_uri: str,
    *,
    issuance_manifest_uri: str,
    evidence_root: Path,
) -> list[dict[str, Any]]:
    reference = _observation_reference(
        receipt_uri, "PUBLICATION_RECEIPT_LEDGER_URI"
    )
    if not reference.endswith(".ndjson"):
        raise MaturityObservationError(
            "PUBLICATION_RECEIPT_LEDGER_URI_INVALID"
        )
    raw = _read_retained_bytes(
        evidence_root,
        reference,
        field="PUBLICATION_RECEIPT_LEDGER",
        max_bytes=_MAX_PUBLICATION_RECEIPT_BYTES,
        reference_validator=_observation_reference,
    )
    if raw and not raw.endswith(b"\n"):
        raise MaturityObservationError(
            "PUBLICATION_RECEIPT_LEDGER_TRUNCATED"
        )
    events = [
        _strict_json_object(line, "PUBLICATION_RECEIPT_ROW")
        for line in raw.splitlines()
        if line.strip()
    ]
    verify_external_publication_receipts(
        events,
        issuance_manifest_uri=issuance_manifest_uri,
        evidence_root=evidence_root,
    )
    return events


def read_external_publication_receipts(
    receipt_uri: str,
    *,
    issuance_manifest_uri: str,
    evidence_root: Path,
) -> list[dict[str, Any]]:
    """Read exact external-publication receipts after full replay."""
    return _read_external_publication_receipts_unlocked(
        receipt_uri,
        issuance_manifest_uri=issuance_manifest_uri,
        evidence_root=evidence_root,
    )


def append_external_publication_receipt(
    path: Path,
    source_snapshot_uri: str,
    *,
    issuance_manifest_uri: str,
    evidence_root: Path,
) -> dict[str, Any]:
    """Append a system-observed, server-timestamped GitHub receipt."""
    receipt_path, receipt_uri = _publication_receipt_storage_path(
        path, evidence_root
    )
    with _ledger_lock(receipt_path, exclusive=True):
        if receipt_path.exists():
            existing_raw = _read_retained_bytes(
                evidence_root,
                receipt_uri,
                field="PUBLICATION_RECEIPT_LEDGER",
                max_bytes=_MAX_PUBLICATION_RECEIPT_BYTES,
                reference_validator=_observation_reference,
            )
            if existing_raw and not existing_raw.endswith(b"\n"):
                raise MaturityObservationError(
                    "PUBLICATION_RECEIPT_LEDGER_TRUNCATED"
                )
            events = [
                _strict_json_object(line, "PUBLICATION_RECEIPT_ROW")
                for line in existing_raw.splitlines()
                if line.strip()
            ]
            verify_external_publication_receipts(
                events,
                issuance_manifest_uri=issuance_manifest_uri,
                evidence_root=evidence_root,
            )
        else:
            existing_raw = b""
            events = []
        source_raw = _read_retained_bytes(
            evidence_root,
            source_snapshot_uri,
            field="PUBLICATION_SOURCE",
            max_bytes=_MAX_PUBLICATION_RECEIPT_BYTES,
            reference_validator=_observation_reference,
        )
        source = _strict_json_object(source_raw, "PUBLICATION_SOURCE")
        attestation = _parse_publication_attestation(source.get("body"))
        manifest_events = read_issuance_artifact_manifest(
            issuance_manifest_uri, evidence_root=evidence_root
        )
        manifest_event = next(
            (
                event for event in manifest_events
                if event["event_hash"]
                == attestation["issuance_manifest_event_hash"]
            ),
            None,
        )
        if manifest_event is None:
            raise MaturityObservationError(
                "PUBLICATION_MANIFEST_EVENT_MISSING"
            )
        observed = _system_utc_now()
        if observed.tzinfo is None or observed.utcoffset() is None:
            raise MaturityObservationError(
                "SYSTEM_PUBLICATION_OBSERVATION_TIME_INVALID"
            )
        event = build_external_publication_receipt_event(
            manifest_event=manifest_event,
            source_bytes=source_raw,
            source_snapshot_uri=source_snapshot_uri,
            first_observed_at=observed,
            previous_hash=(
                events[-1]["event_hash"]
                if events
                else PUBLICATION_RECEIPT_GENESIS_HASH
            ),
        )
        candidate = [*events, event]
        verify_external_publication_receipts(
            candidate,
            issuance_manifest_uri=issuance_manifest_uri,
            evidence_root=evidence_root,
        )
        encoded_event = json.dumps(
            event,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        payload = existing_raw + encoded_event + b"\n"
        if len(payload) > _MAX_PUBLICATION_RECEIPT_BYTES:
            raise MaturityObservationError(
                "PUBLICATION_RECEIPT_LEDGER_RETAINED_TOO_LARGE"
            )
        _replace_manifest_atomically(
            receipt_path,
            payload,
            failure_code="PUBLICATION_RECEIPT_LEDGER_COMMIT_FAILED",
        )
        return event


def publish_github_attestation_and_retain(
    path: Path,
    source_snapshot_uri: str,
    *,
    issuance_manifest_uri: str,
    prediction_id: str,
    github_token: str,
    evidence_root: Path,
) -> dict[str, Any]:
    """Publish and retain one canonical prospective GitHub attestation.

    The exact successful POST response is created without overwrite before an
    immediate GET of the comment is compared.  Only a byte-retained,
    semantically identical, fully replayed response reaches the receipt
    ledger.  If a remote POST succeeds but later validation fails, the raw
    response is deliberately left in place for explicit recovery; once those
    response bytes are retained, routine retry cannot silently repost it.
    """
    if (
        not isinstance(prediction_id, str)
        or not prediction_id
        or prediction_id != prediction_id.strip()
        or len(prediction_id) > 128
    ):
        raise MaturityObservationError(
            "PUBLICATION_PREDICTION_ID_INVALID"
        )
    receipt_path, receipt_uri = _publication_receipt_storage_path(
        path, evidence_root
    )
    with _ledger_lock(receipt_path, exclusive=True):
        if receipt_path.exists():
            existing_raw = _read_retained_bytes(
                evidence_root,
                receipt_uri,
                field="PUBLICATION_RECEIPT_LEDGER",
                max_bytes=_MAX_PUBLICATION_RECEIPT_BYTES,
                reference_validator=_observation_reference,
            )
            if existing_raw and not existing_raw.endswith(b"\n"):
                raise MaturityObservationError(
                    "PUBLICATION_RECEIPT_LEDGER_TRUNCATED"
                )
            events = [
                _strict_json_object(line, "PUBLICATION_RECEIPT_ROW")
                for line in existing_raw.splitlines()
                if line.strip()
            ]
            verify_external_publication_receipts(
                events,
                issuance_manifest_uri=issuance_manifest_uri,
                evidence_root=evidence_root,
            )
        else:
            existing_raw = b""
            events = []
        if any(event["prediction_id"] == prediction_id for event in events):
            raise MaturityObservationError(
                "PUBLICATION_RECEIPT_ALREADY_RECORDED"
            )
        source_path = _prospective_storage_path(
            Path(evidence_root),
            source_snapshot_uri,
            field="PUBLICATION_SOURCE",
            suffix=".json",
            must_not_exist=True,
        )
        manifest_events = read_issuance_artifact_manifest(
            issuance_manifest_uri, evidence_root=evidence_root
        )
        matches = [
            event for event in manifest_events
            if event["prediction_id"] == prediction_id
        ]
        if len(matches) != 1:
            raise MaturityObservationError(
                "PUBLICATION_MANIFEST_EVENT_MISSING"
            )
        manifest_event = matches[0]
        _, due, _ = _validate_issuance_manifest_event(manifest_event)
        if not manifest_event["pre_maturity_registered"]:
            raise MaturityObservationError(
                "PUBLICATION_PROSPECTIVE_MANIFEST_REQUIRED"
            )
        started = _system_utc_now()
        if started.tzinfo is None or started.utcoffset() is None:
            raise MaturityObservationError(
                "SYSTEM_PUBLICATION_OBSERVATION_TIME_INVALID"
            )
        if started.astimezone(timezone.utc) >= due:
            raise MaturityObservationError(
                "PUBLICATION_HORIZON_ALREADY_REACHED"
            )
        create_url = (
            "https://api.github.com/repos/"
            f"{_PUBLICATION_REPOSITORY}/issues/"
            f"{_PUBLICATION_PULL_REQUEST}/comments"
        )
        request_payload = _canonical(
            {"body": github_publication_comment_body(manifest_event)}
        )
        source_raw = _github_publication_request_json(
            "POST",
            create_url,
            token=github_token,
            payload=request_payload,
        )
        observed = _system_utc_now()
        _write_new_prospective_artifact(
            source_path,
            source_raw,
            field="PUBLICATION_SOURCE",
        )
        _fsync_directory(source_path.parent)
        if observed.tzinfo is None or observed.utcoffset() is None:
            raise MaturityObservationError(
                "SYSTEM_PUBLICATION_OBSERVATION_TIME_INVALID"
            )
        event = build_external_publication_receipt_event(
            manifest_event=manifest_event,
            source_bytes=source_raw,
            source_snapshot_uri=source_snapshot_uri,
            first_observed_at=observed,
            previous_hash=(
                events[-1]["event_hash"]
                if events
                else PUBLICATION_RECEIPT_GENESIS_HASH
            ),
        )
        fetched_raw = _github_publication_request_json(
            "GET",
            event["source_url"],
            token=github_token,
        )
        source = _strict_json_object(source_raw, "PUBLICATION_SOURCE")
        fetched = _strict_json_object(
            fetched_raw, "GITHUB_PUBLICATION_REFETCH"
        )
        if fetched != source:
            raise MaturityObservationError(
                "GITHUB_PUBLICATION_REFETCH_MISMATCH"
            )
        candidate = [*events, event]
        verify_external_publication_receipts(
            candidate,
            issuance_manifest_uri=issuance_manifest_uri,
            evidence_root=evidence_root,
        )
        encoded_event = json.dumps(
            event,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        payload = existing_raw + encoded_event + b"\n"
        if len(payload) > _MAX_PUBLICATION_RECEIPT_BYTES:
            raise MaturityObservationError(
                "PUBLICATION_RECEIPT_LEDGER_RETAINED_TOO_LARGE"
            )
        _replace_manifest_atomically(
            receipt_path,
            payload,
            failure_code="PUBLICATION_RECEIPT_LEDGER_COMMIT_FAILED",
        )
        return event


def _read_retained_observation_bytes(
    evidence_root: Path,
    observation_uri: str,
) -> bytes:
    return _read_retained_bytes(
        evidence_root,
        observation_uri,
        field="OBSERVATION",
        max_bytes=_MAX_MATURITY_OBSERVATION_BYTES,
        reference_validator=_observation_reference,
    )


def _load_retained_observation(
    event: Mapping[str, Any],
    *,
    evidence_root: Path,
) -> dict[str, Any]:
    raw = _read_retained_observation_bytes(
        evidence_root,
        event["observation_uri"],
    )
    if (
        len(raw) != event["observation_size_bytes"]
        or sha256(raw).hexdigest() != event["observation_file_sha256"]
    ):
        raise MaturityObservationError(
            "OBSERVATION_RETAINED_HASH_OR_SIZE_MISMATCH"
        )
    observation = _strict_json_object(raw, "OBSERVATION")
    validate_maturity_observation(observation)
    if (
        observation["prediction_id"] != event["prediction_id"]
        or observation["prediction_event_hash"]
        != event["prediction_event_hash"]
        or observation["projection_hash"] != event["projection_hash"]
        or observation["record_hash"] != event["observation_record_hash"]
        or observation["recorded_at"] != event["recorded_at"]
        or observation["source_cutoff_at"] != event["source_cutoff_at"]
        or observation["final_outcome_status"]
        != event["final_outcome_status"]
        or observation["counts"]["raw_reference_observations"]
        != event["raw_reference_observations"]
        or observation["counts"]["matured_adjusted_outcomes"]
        != event["matured_adjusted_outcomes"]
    ):
        raise MaturityObservationError(
            "OBSERVATION_LEDGER_BINDING_MISMATCH"
        )
    verify_maturity_evidence(observation, evidence_root=evidence_root)
    return observation


def _read_maturity_observation_ledger_unlocked(
    path: Path,
    *,
    issuance_manifest_uri: str,
    publication_receipt_uri: str | None,
    evidence_root: Path,
) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise MaturityObservationError("MATURITY_LEDGER_TRUNCATED")
    events = [
        _strict_json_object(line, "MATURITY_LEDGER_ROW")
        for line in raw.splitlines()
        if line.strip()
    ]
    verify_maturity_observation_chain(
        events,
        issuance_manifest_uri=issuance_manifest_uri,
        publication_receipt_uri=publication_receipt_uri,
        evidence_root=evidence_root,
    )
    for event in events:
        _load_retained_observation(event, evidence_root=evidence_root)
    return events


def read_maturity_observation_ledger(
    path: Path,
    *,
    issuance_manifest_uri: str,
    publication_receipt_uri: str | None = None,
    evidence_root: Path,
) -> list[dict[str, Any]]:
    """Read only after registered artifacts and retained bytes verify."""
    with _ledger_lock(path, exclusive=False):
        return _read_maturity_observation_ledger_unlocked(
            path,
            issuance_manifest_uri=issuance_manifest_uri,
            publication_receipt_uri=publication_receipt_uri,
            evidence_root=evidence_root,
        )


def append_maturity_observation(
    path: Path,
    observation_uri: str,
    *,
    issuance_manifest_uri: str,
    publication_receipt_uri: str | None = None,
    evidence_root: Path,
) -> dict[str, Any]:
    """Append one retained maturity observation after full-chain validation."""
    with _ledger_lock(path, exclusive=True):
        events = _read_maturity_observation_ledger_unlocked(
            path,
            issuance_manifest_uri=issuance_manifest_uri,
            publication_receipt_uri=publication_receipt_uri,
            evidence_root=evidence_root,
        )
        raw = _read_retained_observation_bytes(
            evidence_root,
            observation_uri,
        )
        observation = _strict_json_object(raw, "OBSERVATION")
        validate_maturity_observation(observation)
        prediction_id = observation["prediction_id"]
        manifest_events = read_issuance_artifact_manifest(
            issuance_manifest_uri, evidence_root=evidence_root
        )
        publication_events = (
            read_external_publication_receipts(
                publication_receipt_uri,
                issuance_manifest_uri=issuance_manifest_uri,
                evidence_root=evidence_root,
            )
            if publication_receipt_uri is not None
            else []
        )
        (
            trusted_prediction_hashes,
            trusted_projection_hashes,
            blocked,
        ) = _publication_qualified_manifest_anchors(
            manifest_events, publication_events
        )
        if prediction_id in blocked:
            raise MaturityObservationError(
                "EXTERNAL_PUBLICATION_BEFORE_HORIZON_REQUIRED"
            )
        trusted_prediction = trusted_prediction_hashes.get(prediction_id)
        trusted_projection = trusted_projection_hashes.get(prediction_id)
        if trusted_prediction is None:
            raise MaturityObservationError(
                "TRUSTED_PREDICTION_HASH_MISSING"
            )
        if trusted_projection is None:
            raise MaturityObservationError(
                "TRUSTED_PROJECTION_HASH_MISSING"
            )
        previous_hash = (
            events[-1]["event_hash"]
            if events
            else MATURITY_LEDGER_GENESIS_HASH
        )
        event = build_maturity_observation_event(
            observation,
            observation_bytes=raw,
            observation_uri=observation_uri,
            trusted_prediction_event_hash=trusted_prediction,
            trusted_projection_hash=trusted_projection,
            previous_hash=previous_hash,
        )
        _load_retained_observation(event, evidence_root=evidence_root)
        _verify_maturity_observation_chain_with_anchors(
            [*events, event],
            trusted_prediction_hashes=trusted_prediction_hashes,
            trusted_projection_hashes=trusted_projection_hashes,
        )
        payload = json.dumps(
            event,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(payload + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event
