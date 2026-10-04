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
from math import isfinite
import re
from typing import Any
from zipfile import BadZipFile, ZipFile
from zoneinfo import ZoneInfo


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
    trade_date = datetime.strptime(stamp, "%Y%m%d").date()
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
    price_as_of: datetime,
    field: str,
) -> tuple[Decimal, str]:
    if source == "NSE":
        return _nse_close_from_snapshot(
            raw,
            source_url=source_url,
            symbol=symbol,
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
            price_as_of=entry_at,
            field="ENTRY",
        )
        observed_exit, outcome_row_hash = _close_from_snapshot(
            outcome_raw,
            source=outcome_source,
            source_url=outcome["source_url"],
            symbol=symbol,
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
