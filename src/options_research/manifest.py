"""SQLite manifest and per-file integrity verification."""
from __future__ import annotations

import sqlite3
from datetime import date
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
        self.db.execute(f"INSERT OR REPLACE INTO objects ({','.join(self.COLUMNS)}) VALUES ({marks})", values)
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


def pick_column(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    mapping = {str(column).lower(): str(column) for column in frame.columns}
    return next((mapping[name.lower()] for name in candidates if name.lower() in mapping), None)


def safe_text(series: pd.Series) -> pd.Series:
    """Normalize object, Arrow string and categorical columns without fillna category errors."""
    return series.astype("string").fillna("").str.upper().str.strip()


def resolve_record_path(manifest: Manifest, record: dict) -> tuple[Path, bool]:
    """Resolve paths after a GitHub artifact moves to a different runner directory.

    Manifest rows contain the original absolute path. Reused workflow artifacts
    preserve the relative data layout but not the original runner prefix.
    """
    raw = Path(str(record.get("path") or ""))
    if raw.exists():
        return raw, False
    if record.get("source") == "NSE_FO_EOD":
        try:
            day = date.fromisoformat(str(record.get("start_date") or ""))
            candidate = manifest.path.parent / "nse_fo_eod" / str(day.year) / f"{day:%Y%m%d}_fo.parquet"
            if candidate.exists():
                return candidate, True
        except Exception:
            pass
    return raw, False


def verify_data(manifest: Manifest, limit: int | None = None) -> dict:
    records = [row for row in manifest.records() if row.get("status") in {"DOWNLOADED", "EXISTS_VALID"}]
    if limit:
        records = records[:limit]
    counters = {
        "files_checked": 0,
        "rows_checked": 0,
        "rebased_manifest_paths": 0,
        "sha_mismatches": 0,
        "missing_files": 0,
        "unreadable_files": 0,
        "empty_files": 0,
        "duplicate_rows": 0,
        "traded_rows_checked": 0,
        "no_trade_rows": 0,
        "partial_traded_ohlc_rows": 0,
        "invalid_traded_option_ohlc_rows": 0,
        "invalid_traded_futures_ohlc_rows": 0,
        "invalid_traded_unclassified_ohlc_rows": 0,
        "negative_volume_oi_rows": 0,
        "missing_required_column_files": 0,
        "missing_ohlc_schema_files": 0,
        "missing_volume_oi_schema_files": 0,
    }
    for record in records:
        path, rebased = resolve_record_path(manifest, record)
        counters["rebased_manifest_paths"] += int(rebased)
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

        open_col = pick_column(frame, ("open", "OpnPric", "OPEN"))
        high_col = pick_column(frame, ("high", "HghPric", "HIGH"))
        low_col = pick_column(frame, ("low", "LwPric", "LOW"))
        close_col = pick_column(frame, ("close", "ClsPric", "CLOSE"))
        volume_col = pick_column(frame, ("volume", "TtlTradgVol", "CONTRACTS"))
        oi_col = pick_column(frame, ("oi", "OpnIntrst", "OPEN_INT"))
        instrument_col = pick_column(frame, ("instrument", "FinInstrmTp", "INSTRUMENT"))
        option_type_col = pick_column(frame, ("option_type", "OptnTp", "OPTION_TYP"))

        if not volume_col or not oi_col:
            counters["missing_volume_oi_schema_files"] += 1
        volume = pd.to_numeric(frame[volume_col], errors="coerce") if volume_col else pd.Series(0, index=frame.index)
        oi = pd.to_numeric(frame[oi_col], errors="coerce") if oi_col else pd.Series(0, index=frame.index)
        counters["negative_volume_oi_rows"] += int(((volume < 0) | (oi < 0)).fillna(False).sum())

        if all((open_col, high_col, low_col, close_col)):
            ohlc = frame[[open_col, high_col, low_col, close_col]].apply(pd.to_numeric, errors="coerce")
            ohlc.columns = ["open", "high", "low", "close"]
            traded = volume.fillna(0) > 0
            counters["traded_rows_checked"] += int(traded.sum())
            counters["no_trade_rows"] += int((~traded).sum())

            complete_traded = traded & ohlc.notna().all(axis=1) & (ohlc > 0).all(axis=1)
            partial_traded = traded & ~complete_traded
            invalid_traded = complete_traded & (
                (ohlc["high"] < ohlc[["open", "close", "low"]].max(axis=1))
                | (ohlc["low"] > ohlc[["open", "close", "high"]].min(axis=1))
            )
            counters["partial_traded_ohlc_rows"] += int(partial_traded.sum())

            instrument = safe_text(frame[instrument_col]) if instrument_col else pd.Series("", index=frame.index)
            option_type = safe_text(frame[option_type_col]) if option_type_col else pd.Series("", index=frame.index)
            option_mask = instrument.isin({"IDO", "STO", "OPTIDX", "OPTSTK"}) | option_type.isin({"CE", "PE", "CALL", "PUT"})
            futures_mask = instrument.isin({"IDF", "STF", "FUTIDX", "FUTSTK"}) | instrument.str.contains("FUT", regex=False)
            counters["invalid_traded_option_ohlc_rows"] += int((invalid_traded & option_mask).sum())
            counters["invalid_traded_futures_ohlc_rows"] += int((invalid_traded & ~option_mask & futures_mask).sum())
            counters["invalid_traded_unclassified_ohlc_rows"] += int((invalid_traded & ~option_mask & ~futures_mask).sum())
        else:
            counters["missing_ohlc_schema_files"] += 1

    quarantine_rows = (
        counters["invalid_traded_option_ohlc_rows"]
        + counters["invalid_traded_futures_ohlc_rows"]
        + counters["invalid_traded_unclassified_ohlc_rows"]
    )
    structural_failure_keys = {
        "sha_mismatches", "missing_files", "unreadable_files", "empty_files", "duplicate_rows",
        "partial_traded_ohlc_rows", "negative_volume_oi_rows", "missing_required_column_files",
        "missing_ohlc_schema_files", "missing_volume_oi_schema_files",
    }
    structural_failures = sum(counters[key] for key in structural_failure_keys)
    if structural_failures > 0 or counters["files_checked"] == 0:
        status = "FAIL"
    elif quarantine_rows > 0:
        status = "PASS_WITH_QUARANTINE"
    else:
        status = "PASS"
    return {
        "status": status,
        "manifest_valid_records": len(records),
        "quarantined_invalid_market_rows": quarantine_rows,
        "structural_failure_count": structural_failures,
        **counters,
    }
