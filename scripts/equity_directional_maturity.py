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
from typing import Any, Mapping
from urllib.parse import urlsplit

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
    capture as capture_instruments,
)


SCHEMA_VERSION = "equity-directional-maturity-observation-v1"
INDEX_URL_PREFIX = (
    "https://nsearchives.nseindia.com/content/indices/ind_close_all_"
)
CM_URL_PREFIX = "https://nsearchives.nseindia.com/content/cm/"
SOURCE_ROLES = {"outcome_cash", "company", "etf", "actions", "index"}
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


def validate_maturity_observation(record: dict[str, Any]) -> dict[str, Any]:
    """Validate immutable semantics without turning a raw reference into a score."""
    if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
        raise MaturityObservationError("RECORD_FIELDS_INVALID")
    if record.get("schema_version") != SCHEMA_VERSION:
        raise MaturityObservationError("SCHEMA_VERSION_INVALID")
    expected = sha256(
        _canonical({key: value for key, value in record.items() if key != "record_hash"})
    ).hexdigest()
    if record.get("record_hash") != expected:
        raise MaturityObservationError("RECORD_HASH_MISMATCH")
    if set(record.get("source_receipts", {})) != SOURCE_ROLES:
        raise MaturityObservationError("SOURCE_RECEIPT_ROLES_INVALID")
    if record.get("final_outcome_status") != (
        "NOT_PROVEN_ADJUSTMENT_REVIEW_PENDING"
    ):
        raise MaturityObservationError("FINAL_OUTCOME_STATUS_INVALID")
    counts = record.get("counts")
    if counts != {
        "immutable_predictions": 1,
        "raw_reference_observations": 1,
        "matured_adjusted_outcomes": 0,
    }:
        raise MaturityObservationError("COUNTS_INVALID")
    raw = record.get("raw_reference", {})
    if (
        raw.get("status")
        != "RAW_REFERENCE_OBSERVED_ADJUSTMENT_REVIEW_PENDING"
        or raw.get("actual_return_pct") is not None
        or raw.get("absolute_error_pp") is not None
        or raw.get("direction_correct") is not None
        or raw.get("matured_outcomes") != 0
    ):
        raise MaturityObservationError("RAW_REFERENCE_SEMANTICS_INVALID")
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
