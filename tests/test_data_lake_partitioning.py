import json
from datetime import datetime, timezone

import pytest

from core.data.lake.partitioning import (
    MarketDataRecord,
    part_object_path,
    partition_prefix,
)


def test_trading_date_uses_ist_calendar_date_of_source_timestamp():
    # 2026-01-01 19:00 UTC = 2026-01-02 00:30 IST - crosses the day boundary,
    # which is exactly the case point-in-time partitioning must get right.
    source = datetime(2026, 1, 1, 19, 0, tzinfo=timezone.utc)
    receive = datetime(2026, 1, 1, 19, 0, 5, tzinfo=timezone.utc)
    record = MarketDataRecord(
        instrument_type="index", symbol="NIFTY", payload={}, receive_ts_utc=receive, source_ts_utc=source
    )
    assert record.trading_date() == "2026-01-02"


def test_falls_back_to_receive_ts_when_no_source_ts():
    # 10:00 UTC = 15:30 IST, same calendar day either way.
    receive = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    record = MarketDataRecord(instrument_type="equity", symbol="SBIN", payload={}, receive_ts_utc=receive)
    assert record.trading_date() == "2026-01-01"
    assert record.freshness_seconds() is None


def test_naive_datetime_rejected():
    with pytest.raises(ValueError):
        MarketDataRecord(
            instrument_type="index", symbol="NIFTY", payload={}, receive_ts_utc=datetime(2026, 1, 1)
        )


def test_freshness_seconds_is_receive_minus_source():
    source = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    receive = datetime(2026, 1, 1, 10, 0, 3, tzinfo=timezone.utc)
    record = MarketDataRecord(
        instrument_type="depth", symbol="NIFTY", payload={}, receive_ts_utc=receive, source_ts_utc=source
    )
    assert record.freshness_seconds() == pytest.approx(3.0)


def test_partition_prefix_and_object_path_layout():
    assert partition_prefix("option_chain", "2026-08-27") == "market_data/option_chain/2026-08-27"
    assert (
        part_object_path("option_chain", "2026-08-27", "part-1.parquet")
        == "market_data/option_chain/2026-08-27/part-1.parquet"
    )


def test_partition_prefix_rejects_path_separators():
    with pytest.raises(ValueError):
        partition_prefix("bad/type", "2026-08-27")


def test_to_row_includes_lineage_fields():
    source = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    receive = datetime(2026, 1, 1, 10, 0, 1, tzinfo=timezone.utc)
    record = MarketDataRecord(
        instrument_type="future", symbol="NIFTY-FUT", payload={"ltp": 100.5}, receive_ts_utc=receive, source_ts_utc=source
    )
    row = record.to_row()
    assert row["source_ts_utc"] == source.isoformat()
    assert row["receive_ts_utc"] == receive.isoformat()
    assert row["freshness_seconds"] == pytest.approx(1.0)
    assert json.loads(row["payload_json"]) == {"ltp": 100.5}
