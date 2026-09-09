"""Buffered partitioned Parquet writer for laptop-authoritative market data."""
from __future__ import annotations

import logging
import os
from collections import defaultdict
from pathlib import Path
from typing import Protocol

import pandas as pd

from .partitioning import MarketDataRecord, default_part_filename, part_object_path
from .secrets import data_lake_root

logger = logging.getLogger("system3.data_lake.local_parquet_writer")


class ByteUploader(Protocol):
    def upload_bytes(self, namespace: str, object_path: str, data: bytes) -> str:
        ...


class LocalFileUploader:
    def __init__(self, root: str | os.PathLike | None = None):
        self.root = Path(root) if root is not None else data_lake_root()

    def upload_bytes(self, namespace: str, object_path: str, data: bytes) -> str:
        dest = self.root / namespace / object_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return str(dest.resolve())


class PartitionedParquetWriter:
    def __init__(
        self,
        uploader: ByteUploader | None = None,
        bucket: str | None = None,
        max_buffer_rows: int = 5000,
    ):
        self._uploader = uploader or LocalFileUploader()
        self._namespace = bucket or os.getenv("SYSTEM3_DATA_LAKE_NAMESPACE", "system3").strip() or "system3"
        self._max_buffer_rows = max_buffer_rows
        self._buffers: dict[tuple[str, str], list[dict]] = defaultdict(list)

    def add(self, record: MarketDataRecord) -> None:
        key = (record.instrument_type, record.trading_date())
        self._buffers[key].append(record.to_row())
        if len(self._buffers[key]) >= self._max_buffer_rows:
            self._flush_key(key)

    def flush_all(self) -> list[str]:
        written: list[str] = []
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
        data = pd.DataFrame(rows).to_parquet(index=False)
        object_path = part_object_path(instrument_type, trading_date, default_part_filename())
        location = self._uploader.upload_bytes(self._namespace, object_path, data)
        logger.info("flushed %d rows for %s/%s -> %s", len(rows), instrument_type, trading_date, location)
        return location

    def pending_row_count(self) -> int:
        return sum(len(rows) for rows in self._buffers.values())
