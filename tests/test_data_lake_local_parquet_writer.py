import io
from datetime import datetime, timezone

import pandas as pd

from core.data.lake.local_parquet_writer import PartitionedParquetWriter
from core.data.lake.partitioning import MarketDataRecord


class FakeUploader:
    def __init__(self):
        self.uploads = []

    def upload_bytes(self, namespace, object_path, data):
        self.uploads.append((namespace, object_path, data))
        return f"local://{namespace}/{object_path}"


def _record(symbol="NIFTY", ts_hour=10):
    ts = datetime(2026, 8, 27, ts_hour, 0, 0, tzinfo=timezone.utc)
    return MarketDataRecord(instrument_type="index", symbol=symbol, payload={"ltp": 100.0}, receive_ts_utc=ts, source_ts_utc=ts)


def test_add_buffers_until_flush_all():
    uploader = FakeUploader()
    writer = PartitionedParquetWriter(uploader=uploader, bucket="test", max_buffer_rows=1000)
    writer.add(_record()); writer.add(_record())
    assert writer.pending_row_count() == 2
    assert writer.flush_all()
    assert writer.pending_row_count() == 0


def test_auto_flushes_when_buffer_full():
    uploader = FakeUploader(); writer = PartitionedParquetWriter(uploader=uploader, bucket="test", max_buffer_rows=2)
    writer.add(_record()); writer.add(_record())
    assert writer.pending_row_count() == 0
    assert len(uploader.uploads) == 1


def test_flushed_bytes_are_valid_parquet_with_lineage_columns():
    uploader = FakeUploader(); writer = PartitionedParquetWriter(uploader=uploader, bucket="test")
    writer.add(_record()); writer.flush_all()
    _, object_path, data = uploader.uploads[0]
    assert object_path.startswith("market_data/index/2026-08-27/part-")
    df = pd.read_parquet(io.BytesIO(data))
    assert list(df["symbol"]) == ["NIFTY"]
    assert {"source_ts_utc", "receive_ts_utc", "freshness_seconds"}.issubset(df.columns)


def test_flush_empty():
    assert PartitionedParquetWriter(uploader=FakeUploader(), bucket="test").flush_all() == []
