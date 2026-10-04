"""Point-in-time equity forecast-to-outcome reconciliation; no orders or market fetches.

Inputs must come from separately retained, dated source snapshots. A matching
price is evidence of an observed outcome, not proof the model predicted it well.
"""
from __future__ import annotations

import csv
from datetime import datetime, time, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import BytesIO, StringIO
import json
import os
from pathlib import Path
import re
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit
from zipfile import BadZipFile, ZipFile
from zoneinfo import ZoneInfo

from dashboard.backend.multibagger_ledger import (
    LedgerError as ForecastLedgerError,
    _ledger_lock,
    _retained_snapshot_digest,
    _snapshot_reference,
)


_APPROVED_PRICE_SOURCES = {"NSE", "BSE", "DHAN"}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_NSE_CM_URL_RE = re.compile(
    r"^https://nsearchives\.nseindia\.com/content/cm/"
    r"(BhavCopy_NSE_CM_0_0_0_(\d{8})_F_0000\.csv)\.zip$"
)
_NSE_REQUIRED_FIELDS = {
    "TradDt",
    "BizDt",
    "Sgmt",
    "Src",
    "FinInstrmTp",
    "ISIN",
    "TckrSymb",
    "SctySrs",
    "SsnId",
    "OpnPric",
    "HghPric",
    "LwPric",
    "ClsPric",
    "TtlTradgVol",
}
_NSE_CLOSE_TIME = time(15, 30)
_MAX_NSE_CSV_BYTES = 32 * 1024 * 1024
_UNADJUSTED_EXCHANGE_REFERENCE = "UNADJUSTED_EXCHANGE_REFERENCE"


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("TIMESTAMP_REQUIRED")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("INVALID_TIMESTAMP") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return result.astimezone(timezone.utc)


def _price(value: Any) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("INVALID_PRICE")
    try:
        result = Decimal(str(value).strip())
    except (AttributeError, InvalidOperation, ValueError) as exc:
        raise ValueError("INVALID_PRICE") from exc
    if not result.is_finite() or result <= 0:
        raise ValueError("INVALID_PRICE")
    return result


def _forecast(value: Any) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("INVALID_FORECAST")
    try:
        result = Decimal(str(value).strip())
    except (AttributeError, InvalidOperation, ValueError) as exc:
        raise ValueError("INVALID_FORECAST") from exc
    if not result.is_finite():
        raise ValueError("INVALID_FORECAST")
    return result


def _source(value: Any, *, field: str) -> str:
    source = str(value).strip().upper()
    if source not in _APPROVED_PRICE_SOURCES:
        raise ValueError(f"{field}_UNVERIFIED")
    return source


def _sha256(value: Any, *, field: str) -> str:
    digest = str(value).strip().lower()
    if not _SHA256_RE.fullmatch(digest):
        raise ValueError(f"{field}_INVALID_SHA256")
    return digest


def _verified_snapshot(
    record: dict[str, Any],
    key: str,
    digest: str,
    field: str,
) -> bytes:
    """Return retained exact source bytes only when their digest matches."""
    raw = record.get(key)
    if not isinstance(raw, bytes) or not raw:
        raise ValueError(f"{field}_SNAPSHOT_REQUIRED")
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f"{field}_SNAPSHOT_HASH_MISMATCH")
    return raw


def _nse_number(value: str, *, field: str) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field}_NSE_NUMERIC_FIELD_INVALID") from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f"{field}_NSE_NUMERIC_FIELD_INVALID")
    return result


def _nse_close_from_snapshot(
    raw: bytes,
    *,
    source_url: Any,
    symbol: str,
    isin: str,
    price_as_of: datetime,
    field: str,
) -> tuple[Decimal, str]:
    """Extract one regular-session EQ close from exact NSE CM archive bytes."""
    if not isinstance(source_url, str):
        raise ValueError(f"{field}_NSE_SOURCE_URL_INVALID")
    match = _NSE_CM_URL_RE.fullmatch(source_url.strip())
    if not match:
        raise ValueError(f"{field}_NSE_SOURCE_URL_INVALID")
    member, stamp = match.groups()
    try:
        trade_date = datetime.strptime(stamp, "%Y%m%d").date()
    except ValueError as exc:
        raise ValueError(f"{field}_NSE_SOURCE_URL_INVALID") from exc
    local_price_time = price_as_of.astimezone(ZoneInfo("Asia/Kolkata"))
    if (
        local_price_time.date() != trade_date
        or local_price_time.timetz().replace(tzinfo=None) != _NSE_CLOSE_TIME
    ):
        raise ValueError(f"{field}_NSE_PRICE_TIMESTAMP_MISMATCH")

    try:
        with ZipFile(BytesIO(raw)) as archive:
            if archive.namelist() != [member]:
                raise ValueError(f"{field}_NSE_ARCHIVE_MEMBER_INVALID")
            if archive.getinfo(member).file_size > _MAX_NSE_CSV_BYTES:
                raise ValueError(f"{field}_NSE_ARCHIVE_TOO_LARGE")
            raw_csv = archive.read(member)
        decoded = raw_csv.decode("utf-8-sig")
    except BadZipFile as exc:
        raise ValueError(f"{field}_NSE_ARCHIVE_INVALID") from exc
    except UnicodeDecodeError as exc:
        raise ValueError(f"{field}_NSE_CSV_ENCODING_INVALID") from exc

    reader = csv.DictReader(StringIO(decoded))
    columns = reader.fieldnames or []
    if len(columns) != len(set(columns)) or not _NSE_REQUIRED_FIELDS.issubset(columns):
        raise ValueError(f"{field}_NSE_CSV_SCHEMA_INVALID")

    matches: list[tuple[Decimal, str]] = []
    for row in reader:
        if (
            None in row
            or any(value is None for value in row.values())
            or row["TradDt"] != trade_date.isoformat()
            or row["BizDt"] != trade_date.isoformat()
            or row["Src"] != "NSE"
            or row["Sgmt"] != "CM"
        ):
            raise ValueError(f"{field}_NSE_ROW_INVALID")
        if row["TckrSymb"].strip().upper() != symbol:
            continue
        if row["ISIN"].strip().upper() != isin:
            raise ValueError(f"{field}_NSE_ISIN_MISMATCH")
        if (
            row["FinInstrmTp"] != "STK"
            or row["SctySrs"] != "EQ"
            or row["SsnId"] != "F1"
        ):
            continue

        values = {
            name: _nse_number(row[name], field=field)
            for name in ("OpnPric", "HghPric", "LwPric", "ClsPric", "TtlTradgVol")
        }
        volume = values["TtlTradgVol"]
        if volume != volume.to_integral_value() or volume <= 0:
            raise ValueError(f"{field}_NSE_VOLUME_INVALID")
        if (
            values["LwPric"] <= 0
            or not values["LwPric"]
            <= min(values["OpnPric"], values["ClsPric"])
            <= max(values["OpnPric"], values["ClsPric"])
            <= values["HghPric"]
        ):
            raise ValueError(f"{field}_NSE_OHLC_INVALID")
        row_hash = sha256(
            json.dumps(row, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        matches.append((values["ClsPric"], row_hash))

    if not matches:
        raise ValueError(f"{field}_NSE_PRICE_ROW_NOT_FOUND")
    if len(matches) != 1:
        raise ValueError(f"{field}_NSE_PRICE_ROW_NOT_UNIQUE")
    return matches[0]


def _close_from_snapshot(
    raw: bytes,
    *,
    source: str,
    source_url: Any,
    symbol: str,
    isin: str,
    price_as_of: datetime,
    field: str,
) -> tuple[Decimal, str]:
    if source == "NSE":
        return _nse_close_from_snapshot(
            raw,
            source_url=source_url,
            symbol=symbol,
            isin=isin,
            price_as_of=price_as_of,
            field=field,
        )
    raise ValueError(f"{field}_SNAPSHOT_PARSER_UNAVAILABLE")


def reconcile(
    prediction: dict[str, Any],
    outcome: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Evaluate one issued equity prediction against a later reference close.

    The due timestamp must already name the official horizon close. Scoring
    requires an exact price timestamp match; source publication and first-
    observed times stay separate so a later favorable close cannot be chosen.
    Declared prices, source, symbol and close timestamp are replayed from exact
    retained exchange bytes before arithmetic is allowed. Corporate-action
    resolution remains an upstream prerequisite represented by a shared,
    non-empty adjustment basis.
    """
    try:
        issued = _timestamp(prediction["issued_at"])
        due = _timestamp(prediction["due_at"])
        entry_at = _timestamp(prediction["entry_observed_at"])
        price_as_of = _timestamp(outcome["price_as_of_at"])
        published_at = _timestamp(outcome["source_published_at"])
        first_observed_at = _timestamp(outcome["source_first_observed_at"])
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None or current.utcoffset() is None:
            raise ValueError("NOW_TIMEZONE_REQUIRED")
        current = current.astimezone(timezone.utc)
        if not entry_at <= issued < due <= current:
            raise ValueError("INVALID_TIME_ORDER")
        if price_as_of != due:
            raise ValueError("OUTCOME_HORIZON_MISMATCH")
        if not price_as_of <= published_at <= first_observed_at <= current:
            raise ValueError("INVALID_SOURCE_TIME_ORDER")

        symbol = str(prediction["symbol"]).strip().upper()
        if not symbol or symbol != str(outcome["symbol"]).strip().upper():
            raise ValueError("SYMBOL_MISMATCH")
        isin = str(prediction["isin"]).strip().upper()
        if not isin or isin != str(outcome["isin"]).strip().upper():
            raise ValueError("ISIN_MISMATCH")
        pred_id = str(prediction["prediction_id"]).strip()
        if not pred_id:
            raise ValueError("PREDICTION_ID_REQUIRED")

        entry_source = _source(prediction["entry_source"], field="ENTRY_SOURCE")
        outcome_source = _source(outcome["source"], field="OUTCOME_SOURCE")
        entry_hash = _sha256(
            prediction["entry_source_hash"], field="ENTRY_SOURCE_HASH"
        )
        outcome_hash = _sha256(outcome["source_hash"], field="OUTCOME_SOURCE_HASH")
        entry_raw = _verified_snapshot(
            prediction, "entry_source_snapshot", entry_hash, "ENTRY"
        )
        outcome_raw = _verified_snapshot(
            outcome, "source_snapshot", outcome_hash, "OUTCOME"
        )

        price_basis = str(prediction["price_basis"]).strip()
        if price_basis != str(outcome["price_basis"]).strip():
            raise ValueError("PRICE_BASIS_MISMATCH")
        if price_basis != _UNADJUSTED_EXCHANGE_REFERENCE:
            raise ValueError("PRICE_BASIS_UNSUPPORTED")

        adjustment_basis = str(prediction["adjustment_basis"]).strip()
        if (
            not adjustment_basis
            or adjustment_basis != str(outcome["adjustment_basis"]).strip()
        ):
            raise ValueError("CORPORATE_ACTION_BASIS_MISMATCH")

        entry = _price(prediction["entry_reference_close"])
        exit_price = _price(outcome["reference_close"])
        observed_entry, entry_row_hash = _close_from_snapshot(
            entry_raw,
            source=entry_source,
            source_url=prediction["entry_source_url"],
            symbol=symbol,
            isin=isin,
            price_as_of=entry_at,
            field="ENTRY",
        )
        observed_exit, outcome_row_hash = _close_from_snapshot(
            outcome_raw,
            source=outcome_source,
            source_url=outcome["source_url"],
            symbol=symbol,
            isin=isin,
            price_as_of=price_as_of,
            field="OUTCOME",
        )
        if entry != observed_entry:
            raise ValueError("ENTRY_PRICE_EVIDENCE_MISMATCH")
        if exit_price != observed_exit:
            raise ValueError("OUTCOME_PRICE_EVIDENCE_MISMATCH")
        forecast = _forecast(prediction["predicted_return_pct"])
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        reason = (
            str(exc)
            if isinstance(exc, ValueError)
            else "REQUIRED_EVIDENCE_MISSING"
        )
        return {"status": "NOT_PROVEN", "reason": reason}

    actual = (exit_price / entry - Decimal("1")) * Decimal("100")
    return {
        "status": "EVALUATED",
        "prediction_id": pred_id,
        "symbol": symbol,
        "isin": isin,
        "issued_at": issued.isoformat(),
        "due_at": due.isoformat(),
        "outcome_price_as_of_at": price_as_of.isoformat(),
        "outcome_source_published_at": published_at.isoformat(),
        "outcome_source_first_observed_at": first_observed_at.isoformat(),
        "predicted_return_pct": round(float(forecast), 6),
        "actual_return_pct": round(float(actual), 6),
        "absolute_error_pp": round(float(abs(forecast - actual)), 6),
        "direction_correct": (
            (forecast > 0) == (actual > 0)
            if forecast != 0 and actual != 0
            else forecast == actual
        ),
        "entry_source": entry_source,
        "entry_source_hash": entry_hash,
        "entry_source_row_hash": entry_row_hash,
        "outcome_source": outcome_source,
        "outcome_source_hash": outcome_hash,
        "outcome_source_row_hash": outcome_row_hash,
        "price_basis": price_basis,
        "adjustment_basis": adjustment_basis,
        "market_validation_claimed": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }


OUTCOME_SCHEMA_VERSION = "equity-outcome-ledger-v1"
OUTCOME_GENESIS_HASH = "0" * 64
_OUTCOME_EVENT_TYPE = "EQUITY_OUTCOME_RECORDED"
_ISIN_RE = re.compile(r"^IN[A-Z0-9]{10}$")
_SEALED_OUTCOME_FIELDS = frozenset(
    {
        "schema_version",
        "event_type",
        "prediction_id",
        "prediction_event_hash",
        "symbol",
        "isin",
        "issued_at",
        "due_at",
        "recorded_at",
        "outcome_price_as_of_at",
        "outcome_source_published_at",
        "outcome_source_first_observed_at",
        "entry_reference_close",
        "outcome_reference_close",
        "predicted_return_pct",
        "actual_return_pct",
        "absolute_error_pp",
        "direction_correct",
        "entry_source",
        "entry_source_url",
        "entry_source_hash",
        "entry_source_size_bytes",
        "entry_source_row_hash",
        "entry_snapshot_uri",
        "outcome_source",
        "outcome_source_url",
        "outcome_source_hash",
        "outcome_source_size_bytes",
        "outcome_source_row_hash",
        "outcome_snapshot_uri",
        "price_basis",
        "adjustment_basis",
        "previous_hash",
        "market_validation_claimed",
        "reference_prices_are_executable_fills",
        "performance_gate_passed",
        "real_money_ready",
        "live_trading_enabled",
        "order_placement_allowed",
        "event_hash",
    }
)


class OutcomeLedgerError(ValueError):
    """Raised when an outcome event is detached, mutable, or incomplete."""


def _outcome_sha(value: Any, field: str) -> str:
    digest = str(value).strip().lower()
    if not _SHA256_RE.fullmatch(digest):
        raise OutcomeLedgerError(f"{field}_INVALID_SHA256")
    return digest


def _outcome_time(value: Any, field: str) -> datetime:
    try:
        return _timestamp(value)
    except ValueError as exc:
        raise OutcomeLedgerError(f"{field}_{exc}") from exc


def _outcome_reference(value: Any, field: str) -> str:
    try:
        return _snapshot_reference(value, field)
    except ForecastLedgerError as exc:
        raise OutcomeLedgerError(str(exc)) from exc


def _official_source_url(value: Any, source: str, field: str) -> str:
    if not isinstance(value, str) or value != value.strip():
        raise OutcomeLedgerError(f"{field}_INVALID")
    parsed = urlsplit(value)
    approved_hosts = {
        "NSE": {"nsearchives.nseindia.com", "www.nseindia.com"},
        "BSE": {"www.bseindia.com", "api.bseindia.com"},
        "DHAN": {"api.dhan.co"},
    }
    if (
        parsed.scheme != "https"
        or parsed.hostname not in approved_hosts[source]
        or parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.port not in (None, 443)
    ):
        raise OutcomeLedgerError(f"{field}_UNAPPROVED")
    return value


def _canonical_outcome_event(record: dict[str, Any]) -> bytes:
    payload = {key: value for key, value in record.items() if key != "event_hash"}
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


def _validate_sealed_outcome_semantics(
    record: dict[str, Any],
    *,
    prefix: str = "",
    allow_unhashed: bool = False,
) -> datetime:
    expected_fields = (
        _SEALED_OUTCOME_FIELDS - {"event_hash"}
        if allow_unhashed
        else _SEALED_OUTCOME_FIELDS
    )
    if not isinstance(record, dict) or set(record) != expected_fields:
        raise OutcomeLedgerError(f"{prefix}FIELDS_INVALID")
    if record.get("schema_version") != OUTCOME_SCHEMA_VERSION:
        raise OutcomeLedgerError(f"{prefix}SCHEMA_INVALID")
    if record.get("event_type") != _OUTCOME_EVENT_TYPE:
        raise OutcomeLedgerError(f"{prefix}EVENT_TYPE_INVALID")

    prediction_id = record.get("prediction_id")
    symbol = record.get("symbol")
    isin = record.get("isin")
    if (
        not isinstance(prediction_id, str)
        or not prediction_id
        or prediction_id != prediction_id.strip()
    ):
        raise OutcomeLedgerError(f"{prefix}PREDICTION_ID_INVALID")
    if (
        not isinstance(symbol, str)
        or not symbol
        or symbol != symbol.strip().upper()
    ):
        raise OutcomeLedgerError(f"{prefix}SYMBOL_INVALID")
    if not isinstance(isin, str) or not _ISIN_RE.fullmatch(isin):
        raise OutcomeLedgerError(f"{prefix}ISIN_INVALID")

    issued = _outcome_time(record.get("issued_at"), f"{prefix}ISSUED_AT")
    due = _outcome_time(record.get("due_at"), f"{prefix}DUE_AT")
    recorded = _outcome_time(record.get("recorded_at"), f"{prefix}RECORDED_AT")
    price_as_of = _outcome_time(
        record.get("outcome_price_as_of_at"),
        f"{prefix}OUTCOME_PRICE_AS_OF_AT",
    )
    published = _outcome_time(
        record.get("outcome_source_published_at"),
        f"{prefix}OUTCOME_SOURCE_PUBLISHED_AT",
    )
    observed = _outcome_time(
        record.get("outcome_source_first_observed_at"),
        f"{prefix}OUTCOME_SOURCE_FIRST_OBSERVED_AT",
    )
    if not issued < due == price_as_of <= published <= observed <= recorded:
        raise OutcomeLedgerError(f"{prefix}TIME_ORDER_INVALID")

    prediction_hash = _outcome_sha(
        record.get("prediction_event_hash"),
        f"{prefix}PREDICTION_EVENT_HASH",
    )
    if record.get("prediction_event_hash") != prediction_hash:
        raise OutcomeLedgerError(f"{prefix}PREDICTION_EVENT_HASH_INVALID_SHA256")
    previous_hash = _outcome_sha(
        record.get("previous_hash"),
        f"{prefix}PREVIOUS_HASH",
    )
    if record.get("previous_hash") != previous_hash:
        raise OutcomeLedgerError(f"{prefix}PREVIOUS_HASH_INVALID_SHA256")
    for field in (
        "entry_source_hash",
        "entry_source_row_hash",
        "outcome_source_hash",
        "outcome_source_row_hash",
    ):
        digest = _outcome_sha(record.get(field), f"{prefix}{field.upper()}")
        if record.get(field) != digest:
            raise OutcomeLedgerError(f"{prefix}{field.upper()}_INVALID_SHA256")

    try:
        entry_source = _source(
            record.get("entry_source"),
            field=f"{prefix}ENTRY_SOURCE",
        )
        outcome_source = _source(
            record.get("outcome_source"),
            field=f"{prefix}OUTCOME_SOURCE",
        )
    except ValueError as exc:
        raise OutcomeLedgerError(str(exc)) from exc
    if record.get("entry_source") != entry_source:
        raise OutcomeLedgerError(f"{prefix}ENTRY_SOURCE_INVALID")
    if record.get("outcome_source") != outcome_source:
        raise OutcomeLedgerError(f"{prefix}OUTCOME_SOURCE_INVALID")
    _official_source_url(
        record.get("entry_source_url"),
        entry_source,
        f"{prefix}ENTRY_SOURCE_URL",
    )
    _official_source_url(
        record.get("outcome_source_url"),
        outcome_source,
        f"{prefix}OUTCOME_SOURCE_URL",
    )

    for field in ("entry_source_size_bytes", "outcome_source_size_bytes"):
        value = record.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise OutcomeLedgerError(f"{prefix}{field.upper()}_INVALID")
    _outcome_reference(
        record.get("entry_snapshot_uri"),
        f"{prefix}ENTRY_SNAPSHOT_URI",
    )
    _outcome_reference(
        record.get("outcome_snapshot_uri"),
        f"{prefix}OUTCOME_SNAPSHOT_URI",
    )

    if record.get("price_basis") != _UNADJUSTED_EXCHANGE_REFERENCE:
        raise OutcomeLedgerError(f"{prefix}PRICE_BASIS_INVALID")
    adjustment_basis = record.get("adjustment_basis")
    if (
        not isinstance(adjustment_basis, str)
        or not adjustment_basis
        or adjustment_basis != adjustment_basis.strip()
    ):
        raise OutcomeLedgerError(f"{prefix}ADJUSTMENT_BASIS_INVALID")

    entry = _price(record.get("entry_reference_close"))
    exit_price = _price(record.get("outcome_reference_close"))
    forecast = _forecast(record.get("predicted_return_pct"))
    actual = (exit_price / entry - Decimal("1")) * Decimal("100")
    expected_actual = round(float(actual), 6)
    expected_error = round(float(abs(forecast - actual)), 6)
    expected_direction = (
        (forecast > 0) == (actual > 0)
        if forecast != 0 and actual != 0
        else forecast == actual
    )
    if (
        record.get("actual_return_pct") != expected_actual
        or record.get("absolute_error_pp") != expected_error
        or record.get("direction_correct") is not expected_direction
    ):
        raise OutcomeLedgerError(f"{prefix}ARITHMETIC_MISMATCH")
    if record.get("market_validation_claimed") is not False:
        raise OutcomeLedgerError(f"{prefix}MARKET_VALIDATION_FLAG_INVALID")
    if record.get("reference_prices_are_executable_fills") is not False:
        raise OutcomeLedgerError(
            f"{prefix}REFERENCE_PRICE_EXECUTION_FLAG_INVALID"
        )
    if record.get("performance_gate_passed") is not False:
        raise OutcomeLedgerError(f"{prefix}PERFORMANCE_GATE_FLAG_INVALID")
    if record.get("real_money_ready") is not False:
        raise OutcomeLedgerError(f"{prefix}REAL_MONEY_FLAG_INVALID")
    if record.get("live_trading_enabled") is not False:
        raise OutcomeLedgerError(f"{prefix}LIVE_FLAG_INVALID")
    if record.get("order_placement_allowed") is not False:
        raise OutcomeLedgerError(f"{prefix}ORDER_FLAG_INVALID")
    return recorded


def build_outcome_event(
    prediction: dict[str, Any],
    outcome: dict[str, Any],
    *,
    trusted_prediction_event_hash: str,
    previous_hash: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build one source-replayed outcome event against explicit trusted anchors."""
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise OutcomeLedgerError("NOW_TIMEZONE_REQUIRED")
    current = current.astimezone(timezone.utc)

    trusted_prediction_hash = _outcome_sha(
        trusted_prediction_event_hash,
        "TRUSTED_PREDICTION_EVENT_HASH",
    )
    stored_prediction_hash = _outcome_sha(
        prediction.get("event_hash"),
        "PREDICTION_EVENT_HASH",
    )
    if stored_prediction_hash != trusted_prediction_hash:
        raise OutcomeLedgerError("PREDICTION_EVENT_HASH_TRUST_MISMATCH")

    result = reconcile(prediction, outcome, now=current)
    if result.get("status") != "EVALUATED":
        raise OutcomeLedgerError(
            f"OUTCOME_RECONCILIATION_{result.get('reason', 'NOT_PROVEN')}"
        )
    try:
        entry_raw = prediction["entry_source_snapshot"]
        outcome_raw = outcome["source_snapshot"]
        isin = str(prediction["isin"]).strip().upper()
        if isin != str(outcome["isin"]).strip().upper():
            raise OutcomeLedgerError("ISIN_MISMATCH")
        sealed = {
            "schema_version": OUTCOME_SCHEMA_VERSION,
            "event_type": _OUTCOME_EVENT_TYPE,
            "prediction_id": result["prediction_id"],
            "prediction_event_hash": trusted_prediction_hash,
            "symbol": result["symbol"],
            "isin": isin,
            "issued_at": result["issued_at"],
            "due_at": result["due_at"],
            "recorded_at": current.isoformat(),
            "outcome_price_as_of_at": result["outcome_price_as_of_at"],
            "outcome_source_published_at": result[
                "outcome_source_published_at"
            ],
            "outcome_source_first_observed_at": result[
                "outcome_source_first_observed_at"
            ],
            "entry_reference_close": str(
                _price(prediction["entry_reference_close"])
            ),
            "outcome_reference_close": str(
                _price(outcome["reference_close"])
            ),
            "predicted_return_pct": result["predicted_return_pct"],
            "actual_return_pct": result["actual_return_pct"],
            "absolute_error_pp": result["absolute_error_pp"],
            "direction_correct": result["direction_correct"],
            "entry_source": result["entry_source"],
            "entry_source_url": prediction["entry_source_url"],
            "entry_source_hash": result["entry_source_hash"],
            "entry_source_size_bytes": len(entry_raw),
            "entry_source_row_hash": result["entry_source_row_hash"],
            "entry_snapshot_uri": _outcome_reference(
                prediction["entry_snapshot_uri"],
                "ENTRY_SNAPSHOT_URI",
            ),
            "outcome_source": result["outcome_source"],
            "outcome_source_url": outcome["source_url"],
            "outcome_source_hash": result["outcome_source_hash"],
            "outcome_source_size_bytes": len(outcome_raw),
            "outcome_source_row_hash": result["outcome_source_row_hash"],
            "outcome_snapshot_uri": _outcome_reference(
                outcome["source_snapshot_uri"],
                "OUTCOME_SNAPSHOT_URI",
            ),
            "price_basis": result["price_basis"],
            "adjustment_basis": result["adjustment_basis"],
            "previous_hash": _outcome_sha(previous_hash, "PREVIOUS_HASH"),
            "market_validation_claimed": False,
            "reference_prices_are_executable_fills": False,
            "performance_gate_passed": False,
            "real_money_ready": False,
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        }
    except (KeyError, TypeError) as exc:
        raise OutcomeLedgerError("REQUIRED_OUTCOME_EVENT_EVIDENCE_MISSING") from exc
    _validate_sealed_outcome_semantics(sealed, allow_unhashed=True)
    sealed["event_hash"] = sha256(_canonical_outcome_event(sealed)).hexdigest()
    _validate_sealed_outcome_semantics(sealed)
    return sealed


def verify_outcome_chain(
    records: Iterable[dict[str, Any]],
    *,
    trusted_prediction_hashes: Mapping[str, str],
) -> dict[str, Any]:
    """Verify every outcome hash, predecessor and independent forecast anchor."""
    if not isinstance(trusted_prediction_hashes, Mapping):
        raise OutcomeLedgerError("TRUSTED_PREDICTION_HASHES_REQUIRED")
    previous = OUTCOME_GENESIS_HASH
    previous_recorded: datetime | None = None
    seen: set[str] = set()
    count = 0
    for index, record in enumerate(records):
        recorded = _validate_sealed_outcome_semantics(
            record,
            prefix=f"ROW_{index}_",
        )
        prediction_id = record["prediction_id"]
        if prediction_id in seen:
            raise OutcomeLedgerError(f"ROW_{index}_PREDICTION_ID_DUPLICATE")
        trusted = trusted_prediction_hashes.get(prediction_id)
        if trusted is None:
            raise OutcomeLedgerError(
                f"ROW_{index}_TRUSTED_PREDICTION_HASH_MISSING"
            )
        if record["prediction_event_hash"] != _outcome_sha(
            trusted,
            f"ROW_{index}_TRUSTED_PREDICTION_HASH",
        ):
            raise OutcomeLedgerError(
                f"ROW_{index}_PREDICTION_EVENT_HASH_TRUST_MISMATCH"
            )
        if previous_recorded is not None and recorded < previous_recorded:
            raise OutcomeLedgerError(f"ROW_{index}_RECORDED_ORDER_INVALID")
        if record["previous_hash"] != previous:
            raise OutcomeLedgerError(f"ROW_{index}_CHAIN_BROKEN")
        expected = sha256(_canonical_outcome_event(record)).hexdigest()
        if record.get("event_hash") != expected:
            raise OutcomeLedgerError(f"ROW_{index}_HASH_MISMATCH")
        previous = expected
        previous_recorded = recorded
        seen.add(prediction_id)
        count += 1
    return {
        "status": "VERIFIED" if count else "EMPTY",
        "verification_scope": (
            "HASH_CHAIN_SEMANTICS_RETAINED_SOURCE_AND_PREDICTION_ANCHOR"
        ),
        "record_count": count,
        "head_hash": previous,
        "market_validation_claimed": False,
        "reference_prices_are_executable_fills": False,
        "performance_gate_passed": False,
        "real_money_ready": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }


def verify_retained_outcome_evidence(
    record: dict[str, Any],
    *,
    evidence_root: Path,
) -> None:
    """Recheck entry and outcome files against the sealed hashes and sizes."""
    try:
        root = Path(evidence_root).resolve(strict=True)
        if not root.is_dir():
            raise OutcomeLedgerError("EVIDENCE_ROOT_NOT_DIRECTORY")
    except (OSError, TypeError, ValueError) as exc:
        raise OutcomeLedgerError("EVIDENCE_ROOT_UNAVAILABLE") from exc

    for role in ("entry", "outcome"):
        field = role.upper()
        try:
            digest, size = _retained_snapshot_digest(
                root,
                record[f"{role}_snapshot_uri"],
                field,
            )
        except (KeyError, ForecastLedgerError) as exc:
            raise OutcomeLedgerError(
                f"{field}_RETAINED_UNAVAILABLE"
            ) from exc
        if (
            digest != record.get(f"{role}_source_hash")
            or size != record.get(f"{role}_source_size_bytes")
        ):
            raise OutcomeLedgerError(
                f"{field}_RETAINED_HASH_OR_SIZE_MISMATCH"
            )


def _read_outcome_ledger_unlocked(
    path: Path,
    *,
    trusted_prediction_hashes: Mapping[str, str],
    evidence_root: Path,
) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        raise OutcomeLedgerError("LEDGER_TRUNCATED")
    try:
        records = [json.loads(line) for line in raw.splitlines() if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OutcomeLedgerError("LEDGER_INVALID_JSON") from exc
    verify_outcome_chain(
        records,
        trusted_prediction_hashes=trusted_prediction_hashes,
    )
    for record in records:
        verify_retained_outcome_evidence(
            record,
            evidence_root=evidence_root,
        )
    return records


def read_outcome_ledger(
    path: Path,
    *,
    trusted_prediction_hashes: Mapping[str, str],
    evidence_root: Path,
) -> list[dict[str, Any]]:
    """Read a fully verified outcome ledger while excluding concurrent writes."""
    with _ledger_lock(path, exclusive=False):
        return _read_outcome_ledger_unlocked(
            path,
            trusted_prediction_hashes=trusted_prediction_hashes,
            evidence_root=evidence_root,
        )


def append_outcome_event(
    path: Path,
    prediction: dict[str, Any],
    outcome: dict[str, Any],
    *,
    trusted_prediction_hashes: Mapping[str, str],
    evidence_root: Path,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Validate the prospective full chain before one fsync'd append."""
    with _ledger_lock(path, exclusive=True):
        records = _read_outcome_ledger_unlocked(
            path,
            trusted_prediction_hashes=trusted_prediction_hashes,
            evidence_root=evidence_root,
        )
        prediction_id = str(prediction.get("prediction_id", "")).strip()
        if any(row["prediction_id"] == prediction_id for row in records):
            raise OutcomeLedgerError("PREDICTION_ID_DUPLICATE")
        trusted_prediction_hash = trusted_prediction_hashes.get(prediction_id)
        if trusted_prediction_hash is None:
            raise OutcomeLedgerError("TRUSTED_PREDICTION_HASH_MISSING")
        previous_hash = (
            records[-1]["event_hash"] if records else OUTCOME_GENESIS_HASH
        )
        sealed = build_outcome_event(
            prediction,
            outcome,
            trusted_prediction_event_hash=trusted_prediction_hash,
            previous_hash=previous_hash,
            now=now,
        )
        verify_retained_outcome_evidence(
            sealed,
            evidence_root=evidence_root,
        )
        verify_outcome_chain(
            [*records, sealed],
            trusted_prediction_hashes=trusted_prediction_hashes,
        )
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
        return sealed
