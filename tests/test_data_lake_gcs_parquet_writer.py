import io
from datetime import datetime, timezone

import pandas as pd

from core.data.lake.gcs_parquet_writer import PartitionedParquetWriter
from core.data.lake.partitioning import MarketDataRecord


class FakeUploader:
    def __init__(self):
        self.uploads: list[tuple[str, str, bytes]] = []

    def upload_bytes(self, bucket: str, object_path: str, data: bytes) -> str:
        self.uploads.append((bucket, object_path, data))
        return f"gs://{bucket}/{object_path}"


def _record(symbol="NIFTY", ts_hour=10):
    ts = datetime(2026, 8, 27, ts_hour, 0, 0, tzinfo=timezone.utc)
    return MarketDataRecord(
        instrument_type="index", symbol=symbol, payload={"ltp": 100.0}, receive_ts_utc=ts, source_ts_utc=ts
    )


def test_add_buffers_until_flush_all():
    uploader = FakeUploader()
    writer = PartitionedParquetWriter(uploader=uploader, bucket="test-bucket", max_buffer_rows=1000)
    writer.add(_record())
    writer.add(_record())
    assert writer.pending_row_count() == 2
    assert uploader.uploads == []

    written = writer.flush_all()
    assert len(written) == 1
    assert writer.pending_row_count() == 0
    assert len(uploader.uploads) == 1


def test_auto_flushes_when_buffer_full():
    uploader = FakeUploader()
    writer = PartitionedParquetWriter(uploader=uploader, bucket="test-bucket", max_buffer_rows=2)
    writer.add(_record())
    writer.add(_record())  # hits max_buffer_rows -> auto flush
    assert writer.pending_row_count() == 0
    assert len(uploader.uploads) == 1


def test_partitions_by_instrument_type_and_trading_date_separately():
    uploader = FakeUploader()
    writer = PartitionedParquetWriter(uploader=uploader, bucket="test-bucket")
    writer.add(_record(symbol="NIFTY"))
    equity = MarketDataRecord(
        instrument_type="equity",
        symbol="SBIN",
        payload={},
        receive_ts_utc=datetime(2026, 8, 27, 10, 0, tzinfo=timezone.utc),
        source_ts_utc=datetime(2026, 8, 27, 10, 0, tzinfo=timezone.utc),
    )
    writer.add(equity)
    written = writer.flush_all()
    assert len(written) == 2  # two distinct (instrument_type, trading_date) partitions


def test_flushed_bytes_are_valid_parquet_with_lineage_columns():
    uploader = FakeUploader()
    writer = PartitionedParquetWriter(uploader=uploader, bucket="test-bucket")
    writer.add(_record())
    writer.flush_all()

    _, object_path, data = uploader.uploads[0]
    assert object_path.startswith("market_data/index/2026-08-27/part-")
    df = pd.read_parquet(io.BytesIO(data))
    assert list(df["symbol"]) == ["NIFTY"]
    assert "source_ts_utc" in df.columns
    assert "receive_ts_utc" in df.columns
    assert "freshness_seconds" in df.columns


def test_flush_all_with_nothing_buffered_returns_empty():
    writer = PartitionedParquetWriter(uploader=FakeUploader(), bucket="test-bucket")
    assert writer.flush_all() == []
