"""SQLite manifest and per-file integrity verification."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from .contracts import REQUIRED_DATA, sha256_file


class Manifest:
    COLUMNS = [
        "object_key", "source", "symbol", "start_date", "end_date", "status", "rows", "bytes",
        "sha256", "path", "http_status", "error", "updated_utc",
    ]

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.db = sqlite3.connect(path)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS objects (
              object_key TEXT PRIMARY KEY, source TEXT NOT NULL, symbol TEXT,
              start_date TEXT, end_date TEXT, status TEXT NOT NULL,
              rows INTEGER NOT NULL DEFAULT 0, bytes INTEGER NOT NULL DEFAULT 0,
              sha256 TEXT, path TEXT, http_status INTEGER, error TEXT, updated_utc TEXT NOT NULL
            )
        """)
        self.db.commit()

    def status(self, key: str) -> str | None:
        row = self.db.execute("SELECT status FROM objects WHERE object_key=?", (key,)).fetchone()
        return row[0] if row else None

    def upsert(self, **row: object) -> None:
        values = [row.get(column) for column in self.COLUMNS]
        marks = ",".join("?" for _ in self.COLUMNS)
        self.db.execute(
            f"INSERT OR REPLACE INTO objects ({','.join(self.COLUMNS)}) VALUES ({marks})", values,
        )
        self.db.commit()

    def records(self) -> list[dict]:
        rows = self.db.execute(f"SELECT {','.join(self.COLUMNS)} FROM objects")
        return [dict(zip(self.COLUMNS, row)) for row in rows]

    def summary(self) -> dict:
        counts = dict(self.db.execute("SELECT status, COUNT(*) FROM objects GROUP BY status").fetchall())
        rows, total_bytes = self.db.execute(
            "SELECT COALESCE(SUM(rows),0), COALESCE(SUM(bytes),0) FROM objects "
            "WHERE status IN ('DOWNLOADED','EXISTS_VALID')"
        ).fetchone()
        return {"status_counts": counts, "valid_rows": int(rows), "valid_bytes": int(total_bytes)}


def read_data_file(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    if path.name.endswith(".csv.gz"):
        return pd.read_csv(path, compression="gzip", low_memory=False)
    raise ValueError(f"unsupported data file: {path}")


def verify_data(manifest: Manifest, limit: int | None = None) -> dict:
    records = [row for row in manifest.records() if row.get("status") in {"DOWNLOADED", "EXISTS_VALID"}]
    if limit:
        records = records[:limit]
    counters = {
        "files_checked": 0, "rows_checked": 0, "sha_mismatches": 0, "missing_files": 0,
        "unreadable_files": 0, "empty_files": 0, "duplicate_rows": 0, "invalid_ohlc_rows": 0,
        "negative_volume_oi_rows": 0, "missing_required_column_files": 0,
    }
    for record in records:
        path = Path(str(record.get("path") or ""))
        if not path.exists():
            counters["missing_files"] += 1
            continue
        counters["files_checked"] += 1
        if record.get("sha256") and sha256_file(path) != record["sha256"]:
            counters["sha_mismatches"] += 1
        try:
            frame = read_data_file(path)
        except Exception:
            counters["unreadable_files"] += 1
            continue
        counters["rows_checked"] += len(frame)
        if frame.empty:
            counters["empty_files"] += 1
            continue
        counters["duplicate_rows"] += int(frame.duplicated().sum())
        if record.get("source") == "DHAN_ROLLING":
            missing = set(REQUIRED_DATA + ["timestamp", "underlying", "option_type"]) - set(frame.columns)
            counters["missing_required_column_files"] += int(bool(missing))
        if {"open", "high", "low", "close"}.issubset(frame.columns):
            ohlc = frame[["open", "high", "low", "close"]].apply(pd.to_numeric, errors="coerce")
            invalid = (
                (ohlc["high"] < ohlc[["open", "close", "low"]].max(axis=1))
                | (ohlc["low"] > ohlc[["open", "close", "high"]].min(axis=1))
                | (ohlc < 0).any(axis=1)
            )
            counters["invalid_ohlc_rows"] += int(invalid.fillna(False).sum())
        for column in ("volume", "oi"):
            if column in frame.columns:
                counters["negative_volume_oi_rows"] += int(
                    (pd.to_numeric(frame[column], errors="coerce") < 0).fillna(False).sum()
                )
    failures = sum(value for key, value in counters.items() if key not in {"files_checked", "rows_checked"})
    return {
        "status": "PASS" if failures == 0 and counters["files_checked"] > 0 else "FAIL",
        "manifest_valid_records": len(records), **counters,
    }
