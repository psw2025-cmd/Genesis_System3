"""Append-only, hash-chained equity forecast ledger.

The ledger records what the model issued before an outcome existed. It does not
fetch market data, evaluate alpha, or place broker orders.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from math import isfinite
import os
from pathlib import Path
import re
from typing import Any, Iterable


SCHEMA_VERSION = "equity-forecast-ledger-v1"
GENESIS_HASH = "0" * 64
_APPROVED_SOURCES = {"NSE", "BSE", "DHAN"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class LedgerError(ValueError):
    """Raised when a record cannot be trusted as an issued forecast."""


def _timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise LedgerError(f"{field}_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise LedgerError(f"{field}_INVALID") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LedgerError(f"{field}_TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _sha256(value: Any, field: str) -> str:
    digest = str(value).strip().lower()
    if not _SHA256_RE.fullmatch(digest):
        raise LedgerError(f"{field}_INVALID_SHA256")
    return digest


def _finite_number(value: Any, field: str, *, positive: bool = False) -> float:
    if isinstance(value, bool):
        raise LedgerError(f"{field}_INVALID")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise LedgerError(f"{field}_INVALID") from exc
    if not isfinite(number) or (positive and number <= 0):
        raise LedgerError(f"{field}_INVALID")
    return number


def _canonical(record: dict[str, Any]) -> bytes:
    payload = {key: value for key, value in record.items() if key != "event_hash"}
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def build_issued_forecast(
    forecast: dict[str, Any],
    *,
    previous_hash: str = GENESIS_HASH,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Validate and seal one forecast that existed before its due time."""
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise LedgerError("NOW_TIMEZONE_REQUIRED")
    current = current.astimezone(timezone.utc)

    issued = _timestamp(forecast.get("issued_at"), "ISSUED_AT")
    due = _timestamp(forecast.get("due_at"), "DUE_AT")
    observed = _timestamp(forecast.get("entry_observed_at"), "ENTRY_OBSERVED_AT")
    if not observed <= issued <= current < due:
        raise LedgerError("INVALID_FORECAST_TIME_ORDER")

    prediction_id = str(forecast.get("prediction_id", "")).strip()
    symbol = str(forecast.get("symbol", "")).strip().upper()
    model_name = str(forecast.get("model_name", "")).strip()
    model_version = str(forecast.get("model_version", "")).strip()
    snapshot_uri = str(forecast.get("entry_snapshot_uri", "")).strip()
    adjustment_basis = str(forecast.get("adjustment_basis", "")).strip()
    if not prediction_id:
        raise LedgerError("PREDICTION_ID_REQUIRED")
    if not symbol:
        raise LedgerError("SYMBOL_REQUIRED")
    if not model_name or not model_version:
        raise LedgerError("MODEL_IDENTITY_REQUIRED")
    if not snapshot_uri:
        raise LedgerError("ENTRY_SNAPSHOT_URI_REQUIRED")
    if not adjustment_basis:
        raise LedgerError("ADJUSTMENT_BASIS_REQUIRED")

    source = str(forecast.get("entry_source", "")).strip().upper()
    if source not in _APPROVED_SOURCES:
        raise LedgerError("ENTRY_SOURCE_UNVERIFIED")

    horizon_days = forecast.get("horizon_days")
    if isinstance(horizon_days, bool) or not isinstance(horizon_days, int):
        raise LedgerError("HORIZON_DAYS_INVALID")
    if horizon_days <= 0 or horizon_days > 730:
        raise LedgerError("HORIZON_DAYS_INVALID")
    elapsed_days = (due - issued).total_seconds() / 86400
    if abs(elapsed_days - horizon_days) > 1:
        raise LedgerError("HORIZON_DUE_MISMATCH")

    sealed = {
        "schema_version": SCHEMA_VERSION,
        "event_type": "EQUITY_FORECAST_ISSUED",
        "prediction_id": prediction_id,
        "symbol": symbol,
        "horizon_days": horizon_days,
        "issued_at": issued.isoformat(),
        "due_at": due.isoformat(),
        "entry_observed_at": observed.isoformat(),
        "entry_adjusted_close": _finite_number(
            forecast.get("entry_adjusted_close"),
            "ENTRY_ADJUSTED_CLOSE",
            positive=True,
        ),
        "predicted_return_pct": _finite_number(
            forecast.get("predicted_return_pct"),
            "PREDICTED_RETURN_PCT",
        ),
        "model_name": model_name,
        "model_version": model_version,
        "feature_hash": _sha256(forecast.get("feature_hash"), "FEATURE_HASH"),
        "entry_source": source,
        "entry_source_hash": _sha256(
            forecast.get("entry_source_hash"),
            "ENTRY_SOURCE_HASH",
        ),
        "entry_snapshot_uri": snapshot_uri,
        "adjustment_basis": adjustment_basis,
        "previous_hash": _sha256(previous_hash, "PREVIOUS_HASH"),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    sealed["event_hash"] = sha256(_canonical(sealed)).hexdigest()
    return sealed


def verify_chain(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Verify ordering, uniqueness and every content hash in a ledger."""
    previous = GENESIS_HASH
    seen: set[str] = set()
    count = 0
    for index, record in enumerate(records):
        if record.get("schema_version") != SCHEMA_VERSION:
            raise LedgerError(f"ROW_{index}_SCHEMA_INVALID")
        if record.get("event_type") != "EQUITY_FORECAST_ISSUED":
            raise LedgerError(f"ROW_{index}_EVENT_TYPE_INVALID")
        prediction_id = str(record.get("prediction_id", "")).strip()
        if not prediction_id or prediction_id in seen:
            raise LedgerError(f"ROW_{index}_PREDICTION_ID_DUPLICATE")
        if record.get("previous_hash") != previous:
            raise LedgerError(f"ROW_{index}_CHAIN_BROKEN")
        expected = sha256(_canonical(record)).hexdigest()
        if record.get("event_hash") != expected:
            raise LedgerError(f"ROW_{index}_HASH_MISMATCH")
        if record.get("live_trading_enabled") is not False:
            raise LedgerError(f"ROW_{index}_LIVE_FLAG_INVALID")
        if record.get("order_placement_allowed") is not False:
            raise LedgerError(f"ROW_{index}_ORDER_FLAG_INVALID")
        seen.add(prediction_id)
        previous = expected
        count += 1
    return {
        "status": "VERIFIED" if count else "EMPTY",
        "record_count": count,
        "head_hash": previous,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }


def read_ledger(path: Path) -> list[dict[str, Any]]:
    """Load and verify an NDJSON ledger."""
    if not path.exists():
        return []
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise LedgerError("LEDGER_TRUNCATED")
    try:
        records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LedgerError("LEDGER_INVALID_JSON") from exc
    verify_chain(records)
    return records


def append_issued_forecast(
    path: Path,
    forecast: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Append one fsync'd forecast after validating the full existing chain."""
    records = read_ledger(path)
    prediction_id = str(forecast.get("prediction_id", "")).strip()
    if any(row["prediction_id"] == prediction_id for row in records):
        raise LedgerError("PREDICTION_ID_DUPLICATE")
    previous_hash = records[-1]["event_hash"] if records else GENESIS_HASH
    sealed = build_issued_forecast(
        forecast,
        previous_hash=previous_hash,
        now=now,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        sealed,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(payload + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    verify_chain([*records, sealed])
    return sealed
