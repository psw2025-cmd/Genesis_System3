"""Buffered, partitioned Parquet writer for the market-data lake.

Buffers MarketDataRecord rows per (instrument_type, trading_date) partition and
flushes each buffer as one Parquet part-file, either to GCS (production, Cloud
Run) or to a local directory (dev/test, when no bucket/client is configured -
mirrors this repo's existing "local execution is dev/test only, never
production truth" rule from AGENTS.md).
"""
from __future__ import annotations

import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Protocol

import pandas as pd

from .partitioning import MarketDataRecord, default_part_filename, part_object_path
from .secrets import gcs_bucket_name

logger = logging.getLogger("system3.data_lake.gcs_parquet_writer")


class BlobUploader(Protocol):
    """Minimal surface this writer needs from a GCS client - lets tests inject
    a fake without depending on real google-cloud-storage credentials."""

    def upload_bytes(self, bucket: str, object_path: str, data: bytes) -> str:
        ...


class GcsBlobUploader:
    """Thin real adapter over google.cloud.storage, imported lazily so this
    module still imports cleanly in environments without the package."""

    def upload_bytes(self, bucket: str, object_path: str, data: bytes) -> str:
        from google.cloud import storage

        client = storage.Client()
        blob = client.bucket(bucket).blob(object_path)
        blob.upload_from_string(data, content_type="application/octet-stream")
        return f"gs://{bucket}/{object_path}"


class LocalFileUploader:
    """Dev/test fallback: writes under a local root instead of GCS."""

    def __init__(self, root: str | os.PathLike = "storage/market_data_lake_dev"):
        self.root = Path(root)

    def upload_bytes(self, bucket: str, object_path: str, data: bytes) -> str:
        dest = self.root / bucket / object_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return str(dest)


class PartitionedParquetWriter:
    def __init__(
        self,
        uploader: BlobUploader | None = None,
        bucket: str | None = None,
        max_buffer_rows: int = 5000,
    ):
        self._uploader = uploader or self._default_uploader()
        self._bucket = bucket or gcs_bucket_name()
        self._max_buffer_rows = max_buffer_rows
        self._buffers: dict[tuple[str, str], list[dict]] = defaultdict(list)

    @staticmethod
    def _default_uploader() -> BlobUploader:
        if os.getenv("K_SERVICE") or os.getenv("CLOUD_MODE"):
            return GcsBlobUploader()
        logger.warning(
            "PartitionedParquetWriter: no K_SERVICE/CLOUD_MODE detected - "
            "writing locally under storage/market_data_lake_dev/ (dev/test only, "
            "not production truth; see AGENTS.md)."
        )
        return LocalFileUploader()

    def add(self, record: MarketDataRecord) -> None:
        key = (record.instrument_type, record.trading_date())
        self._buffers[key].append(record.to_row())
        if len(self._buffers[key]) >= self._max_buffer_rows:
            self._flush_key(key)

    def flush_all(self) -> list[str]:
        written = []
        for key in list(self._buffers.keys()):
            path = self._flush_key(key)
            if path:
                written.append(path)
        return written

    def _flush_key(self, key: tuple[str, str]) -> str | None:
        rows = self._buffers.pop(key, None)
        if not rows:
            return None
        instrument_type, trading_date = key
        df = pd.DataFrame(rows)
        buf = df.to_parquet(index=False)  # pandas returns bytes when path=None
        object_path = part_object_path(instrument_type, trading_date, default_part_filename())
        location = self._uploader.upload_bytes(self._bucket, object_path, buf)
        logger.info(
            "flushed %d rows for %s/%s -> %s", len(rows), instrument_type, trading_date, location
        )
        return location

    def pending_row_count(self) -> int:
        return sum(len(rows) for rows in self._buffers.values())
