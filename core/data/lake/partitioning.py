"""Point-in-time partition path and record schema for the market-data lake.

Partition layout: market_data/{instrument_type}/{date}/{filename}
`date` is the NSE/BSE trading date the event belongs to (Asia/Kolkata calendar
date of `source_ts_utc`), not the date it was received - this is what makes
point-in-time queries safe: a record ingested late (broker replay, backfill,
after-hours catch-up) still lands in the partition for the day the market
event actually happened, so a query "as of trading day D" can never pick up
a record that didn't exist yet on day D (no forward/look-ahead leakage) and
never miss a late-arriving record that truly belongs to day D.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

import pytz

IST = pytz.timezone("Asia/Kolkata")

InstrumentType = Literal["index", "equity", "future", "option_chain", "depth"]


@dataclass(frozen=True)
class MarketDataRecord:
    """One ingested market-data event with dual timestamps for lineage.

    - source_ts_utc: exchange/broker-reported event time (tz-aware UTC).
      This is the point-in-time truth; None only if the feed genuinely does
      not supply one (must be surfaced, never silently defaulted to receive
      time - that would fabricate a source timestamp and defeat lineage).
    - receive_ts_utc: local wall-clock time this process observed the
      message (tz-aware UTC). Always set.
    """

    instrument_type: InstrumentType
    symbol: str
    payload: dict[str, Any]
    receive_ts_utc: datetime
    source_ts_utc: datetime | None = None
    schema_version: str = "v1"
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.receive_ts_utc.tzinfo is None:
            raise ValueError("receive_ts_utc must be timezone-aware")
        if self.source_ts_utc is not None and self.source_ts_utc.tzinfo is None:
            raise ValueError("source_ts_utc must be timezone-aware when provided")

    def freshness_seconds(self) -> float | None:
        if self.source_ts_utc is None:
            return None
        return (self.receive_ts_utc - self.source_ts_utc).total_seconds()

    def trading_date(self) -> str:
        """Trading-day partition key: IST calendar date of source_ts_utc,
        falling back to receive_ts_utc (flagged via `extra`) only when the
        feed truly supplied no source timestamp."""
        basis = self.source_ts_utc or self.receive_ts_utc
        return basis.astimezone(IST).strftime("%Y-%m-%d")

    def to_row(self) -> dict[str, Any]:
        """Flat dict suitable for a pyarrow/pandas record - one row per event.

        `payload` is JSON-encoded rather than kept as a nested struct: tick,
        depth, and option-chain messages have different field shapes, and
        pyarrow's struct-column inference either fails outright (an empty
        dict has no fields to infer) or silently unions/nulls mismatched
        shapes across a batch. A JSON string column is schema-stable across
        every instrument type and still fully queryable downstream (BigQuery
        JSON functions, DuckDB read_parquet + json_extract, etc.)."""
        return {
            "instrument_type": self.instrument_type,
            "symbol": self.symbol,
            "source_ts_utc": self.source_ts_utc.isoformat() if self.source_ts_utc else None,
            "receive_ts_utc": self.receive_ts_utc.isoformat(),
            "freshness_seconds": self.freshness_seconds(),
            "schema_version": self.schema_version,
            "payload_json": json.dumps(self.payload, default=str),
            **self.extra,
        }


def partition_prefix(instrument_type: str, trading_date: str) -> str:
    """`market_data/{instrument_type}/{date}` - the GCS "directory" a batch's
    Parquet part-files are written under. No trailing slash."""
    if "/" in instrument_type or "/" in trading_date:
        raise ValueError("instrument_type/trading_date must not contain '/'")
    return f"market_data/{instrument_type}/{trading_date}"


def part_object_path(instrument_type: str, trading_date: str, part_filename: str) -> str:
    return f"{partition_prefix(instrument_type, trading_date)}/{part_filename}"


def default_part_filename(now_utc: datetime | None = None) -> str:
    now_utc = now_utc or datetime.now(timezone.utc)
    return f"part-{now_utc.strftime('%Y%m%dT%H%M%S%f')}.parquet"
