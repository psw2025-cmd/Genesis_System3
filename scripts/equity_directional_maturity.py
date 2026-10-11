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
from pathlib import Path
import re
from typing import Any, Mapping
from urllib.parse import parse_qs, urlsplit

from dashboard.backend.multibagger_ledger import (
    LedgerError,
    _retained_snapshot_digest,
    _snapshot_reference,
)
from dashboard.backend.multibagger_outcome import (
    OutcomeLedgerError,
    reconcile_directional_reference,
    validate_directional_outcome_projection,
)
from scripts.equity_corporate_action_scope import capture as capture_actions
from scripts.equity_corporate_action_scope import review as review_actions
from scripts.equity_instrument_scope import (
    EQUITY_URL,
    ETF_URL,
    VERSION as INSTRUMENT_SCOPE_VERSION,
    capture as capture_instruments,
)


SCHEMA_VERSION = "equity-directional-maturity-observation-v1"
INDEX_URL_PREFIX = (
    "https://nsearchives.nseindia.com/content/indices/ind_close_all_"
)
CM_URL_PREFIX = "https://nsearchives.nseindia.com/content/cm/"
SOURCE_ROLES = {"outcome_cash", "company", "etf", "actions", "index"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
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
