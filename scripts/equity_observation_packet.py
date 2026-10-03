"""Bind retained NSE cash observations to current identity and action snapshots.

This is a source-capture adapter, not a strategy or adjusted-return calculator.
It never issues predictions, qualifies historical universe membership or orders.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import BytesIO, StringIO
import csv
import json
import re
from zipfile import BadZipFile, ZipFile
from zoneinfo import ZoneInfo

from scripts.equity_corporate_action_scope import capture as capture_actions, review
from scripts.equity_instrument_scope import capture as capture_instruments

VERSION = "nse-equity-observation-packet-v1"
CM_URL = "https://nsearchives.nseindia.com/content/cm/"
MAX_CSV_BYTES = 32 * 1024 * 1024
REQUIRED = {"TradDt", "BizDt", "Sgmt", "Src", "FinInstrmTp", "ISIN",
            "TckrSymb", "SctySrs", "SsnId", "OpnPric", "HghPric",
            "LwPric", "ClsPric", "TtlTradgVol"}


def _time(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Explicit timezone required")
    return result.astimezone(timezone.utc)


def _verify(raw: bytes, receipt: dict, as_of: datetime) -> datetime:
    if (not raw or receipt.get("raw_sha256") != sha256(raw).hexdigest()
            or receipt.get("bytes") != len(raw)
            or receipt.get("http_status") != 200
            or receipt.get("final_url") != receipt.get("url")):
        raise ValueError("Source bytes or HTTP receipt mismatch")
    observed = _time(receipt["first_observed_at"])
    if observed > as_of:
        raise ValueError("Source observed after packet cutoff")
    return observed


def _number(value: str) -> Decimal:
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Invalid cash numeric field") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("Non-finite or negative cash numeric field")
    return result


def build_packet(sources: dict[str, bytes], receipts: dict[str, dict], *,
                 as_of: str, now: datetime | None = None) -> dict:
    cutoff = _time(as_of)
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or cutoff > current:
        raise ValueError("Packet cutoff must not be in the future")
    observed = {name: _verify(raw, receipts[name], cutoff)
                for name, raw in sources.items()}
    cm = receipts["cash"]
    match = re.fullmatch(re.escape(CM_URL) +
                        r"(BhavCopy_NSE_CM_0_0_0_(\d{8})_F_0000\.csv)\.zip",
                        cm["url"])
    if not match:
        raise ValueError("Unsupported official cash archive URL")
    member, stamp = match.groups()
    trade_date = datetime.strptime(stamp, "%Y%m%d").date()
    if trade_date > observed["cash"].astimezone(ZoneInfo("Asia/Kolkata")).date():
        raise ValueError("Cash session is after first observation")
    try:
        with ZipFile(BytesIO(sources["cash"])) as archive:
            if archive.namelist() != [member]:
                raise ValueError("Unexpected cash archive member")
            if archive.getinfo(member).file_size > MAX_CSV_BYTES:
                raise ValueError("Cash CSV exceeds size limit")
            raw_csv = archive.read(member)
    except BadZipFile as exc:
        raise ValueError("Invalid cash archive") from exc

    identity = capture_instruments(sources["company"], sources["etf"],
                                   equity_receipt=receipts["company"],
                                   etf_receipt=receipts["etf"])
    actions = capture_actions(sources["actions"],
                              dict(receipts["actions"], source_url=receipts["actions"]["url"]))
    if not actions["start"] <= trade_date < actions["end"]:
        raise ValueError("Action capture must cover cash date and a later horizon")
    reader = csv.DictReader(StringIO(raw_csv.decode("utf-8-sig")))
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)) or not REQUIRED.issubset(fields):
        raise ValueError("Unsupported or duplicate cash columns")
    counts, seen, observations = Counter(), set(), []
    for row in reader:
        counts["source_rows"] += 1
        if (None in row or any(value is None for value in row.values())
                or row["TradDt"] != trade_date.isoformat()
                or row["BizDt"] != trade_date.isoformat()
                or row["Src"] != "NSE" or row["Sgmt"] != "CM"):
            raise ValueError("Cash row date/source/segment or shape mismatch")
        if row["FinInstrmTp"] != "STK" or row["SctySrs"] != "EQ" or row["SsnId"] != "F1":
            counts["non_regular_stock_eq_excluded"] += 1
            continue
        symbol, isin = row["TckrSymb"].strip(), row["ISIN"].strip()
        if not symbol or not isin or (symbol, isin) in seen:
            raise ValueError("Missing or duplicate cash identity")
        seen.add((symbol, isin))
        values = {name: _number(row[name]) for name in
                  ("OpnPric", "HghPric", "LwPric", "ClsPric", "TtlTradgVol")}
        volume = values["TtlTradgVol"]
        if volume != volume.to_integral_value():
            raise ValueError("Cash volume must be integral")
        if volume == 0:
            counts["untraded_excluded"] += 1
            continue
        if (values["LwPric"] <= 0 or not values["LwPric"] <=
                min(values["OpnPric"], values["ClsPric"]) <=
                max(values["OpnPric"], values["ClsPric"]) <= values["HghPric"]):
            raise ValueError("Inconsistent traded cash OHLC")
        classification = identity.classify(symbol, isin, issued_at=as_of)
        counts[classification] += 1
        if classification != "COMPANY_EQ_IDENTITY_MATCHED":
            continue
        action_review = review(actions, symbol, isin, trade_date, actions["end"])
        observations.append({
            "symbol": symbol, "isin": isin, "series": "EQ", "session_id": "F1",
            "trade_date": trade_date.isoformat(), "currency": "INR",
            "open": str(values["OpnPric"]), "high": str(values["HghPric"]),
            "low": str(values["LwPric"]), "close": str(values["ClsPric"]),
            "volume": int(volume), "price_basis": "UNADJUSTED_EXCHANGE_REFERENCE",
            "canonical_source_row_sha256": sha256(json.dumps(
                row, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "classification": classification, "action_review": action_review,
        })
    if not counts["source_rows"]:
        raise ValueError("Empty cash CSV")
    return {
        "schema_version": VERSION, "as_of": cutoff.isoformat(),
        "trade_date": trade_date.isoformat(), "source_receipts": receipts,
        "cash_csv_sha256": sha256(raw_csv).hexdigest(),
        "cash_csv_bytes": len(raw_csv), "counts": dict(counts),
        "company_eq_observation_count": len(observations),
        "identity_scope": "CURRENT_MASTER_AT_CAPTURE_NOT_HISTORICAL_UNIVERSE",
        "identity_receipt_sha256": identity.receipt_sha256,
        "action_scope": {"start": actions["start"].isoformat(),
                         "end": actions["end"].isoformat(),
                         "records": actions["unique_records"],
                         "complete_action_coverage": False},
        "observations": observations, "adjusted_prices_proven": False,
        "exchange_publication_time": None,
        "qualified_candidates": 0, "forward_predictions": 0, "forward_outcomes": 0,
        "source_observation_is_prediction": False,
        "live_trading_enabled": False, "orders_allowed": False,
    }
