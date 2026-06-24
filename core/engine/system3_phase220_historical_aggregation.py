"""
System3 Phase 220 - Historical Curated Signals Aggregation

Aggregates archived curated signals across multiple days to create a proper
time-series dataset for forward return computation.

This phase MUST run before Phase 221 to ensure multi-day signals are available.
"""

import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.utils.timestamp_parser import (
    normalize_timestamp_column_strict,
    normalize_timestamp_column_strict_enhanced,
)

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
METRICS_DIR = PROJECT_ROOT / "storage" / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIRS = [
    STORAGE_LIVE / "archive",
    STORAGE_LIVE / "archive" / "signals",
    STORAGE_LIVE / "archive" / "curated",
    STORAGE_LIVE / "old",
    STORAGE_LIVE / "backup",
    STORAGE_LIVE / "raw_backup",
]
OUTPUT_CSV = STORAGE_LIVE / "dhan_index_ai_signals_curated_full.csv"
VALIDATION_JSON = STORAGE_LIVE / "meta" / "PHASE220_AGGREGATION_VALIDATION.json"
VALIDATION_JSON.parent.mkdir(parents=True, exist_ok=True)

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_phase220_historical_aggregation.log"


def _log(message: str) -> None:
    """Log message to file and console."""
    log_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    print(log_msg)
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(log_msg + "\n")
    except Exception:
        pass


def find_curated_archives(days_back: int = 14) -> list:
    """Find all curated signal archive files within date range."""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    found_files = []

    patterns = [
        "dhan_index_ai_signals_curated*.csv",
        "*curated*.csv",
        "dhan_index_ai_signals_*.csv",
    ]

    for archive_dir in ARCHIVE_DIRS:
        if not archive_dir.exists():
            continue

        for pattern in patterns:
            for file_path in archive_dir.glob(pattern):
                # Skip if file is the output file itself
                if file_path == OUTPUT_CSV:
                    continue

                # Check file modified time
                try:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime >= cutoff_date:
                        found_files.append(file_path)
                except Exception as e:
                    _log(f"WARN: Could not check {file_path}: {e}")

    # Also check current curated file
    current_curated = STORAGE_LIVE / "dhan_index_ai_signals_curated.csv"
    if current_curated.exists():
        found_files.append(current_curated)

    # Deduplicate by absolute path
    found_files = list(set(found_files))
    found_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return found_files


def load_and_merge_signals(file_paths: list) -> pd.DataFrame:
    """Load all signal files and merge into single dataset with enhanced NULL timestamp recovery."""
    all_dfs = []
    file_stats = {}
    total_null_dropped = 0

    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path, engine="python", on_bad_lines="skip")

            if df.empty:
                continue

            original_count = len(df)

            # Normalize timestamp column with enhanced recovery
            if "timestamp" in df.columns and "ts" not in df.columns:
                df["ts"] = df["timestamp"]
            elif "ts" not in df.columns:
                _log(f"WARN: {file_path.name} has no ts/timestamp column - skipping")
                continue

            # Enhanced timestamp normalization with recovery
            metrics_path = METRICS_DIR / f"phase220_ts_metrics_{file_path.stem}.json"
            df, ts_metrics = normalize_timestamp_column_strict_enhanced(
                df,
                col_name="ts",
                fallback_col="timestamp",
                metrics_path=metrics_path,
                name=f"phase220_{file_path.stem}_ts",
            )

            # Recovery for NULL timestamps
            null_mask = df["ts"].isna()
            if null_mask.any():
                # Attempt recovery from other columns
                recovery_cols = ["timestamp", "created_at", "signal_time"]
                for recovery_col in recovery_cols:
                    if recovery_col in df.columns:
                        recovered = df.loc[null_mask & df[recovery_col].notna(), recovery_col]
                        if len(recovered) > 0:
                            df.loc[recovered.index, "ts"] = recovered
                            null_mask = df["ts"].isna()

                # Log recovery statistics
                recovered_count = original_count - len(df) + null_mask.sum()
                if recovered_count > 0:
                    _log(f"Recovered {recovered_count} timestamps from {file_path.name}")

            # Drop remaining NULL timestamps (should be minimal now)
            null_count = df["ts"].isna().sum()
            if null_count > 0:
                df = df.dropna(subset=["ts"])
                total_null_dropped += null_count
                _log(f"WARN: Dropped {null_count} rows with NULL timestamps from {file_path.name}")

            if ts_metrics.get("nat_count", 0) > 0:
                _log(
                    f"WARN: {file_path.name} had {ts_metrics['nat_count']} NaT ({ts_metrics['nat_rate']*100:.2f}%) after parsing"
                )

            # Track stats
            date_str = df["ts"].dt.date.mode()[0] if not df["ts"].isna().all() else "unknown"
            file_stats[str(file_path)] = {
                "rows": len(df),
                "original_rows": original_count,
                "null_timestamps_dropped": null_count,
                "date": str(date_str),
                "columns": list(df.columns),
            }

            all_dfs.append(df)
            _log(f"Loaded {len(df)} rows from {file_path.name} (date: {date_str})")

        except Exception as e:
            _log(f"ERROR loading {file_path.name}: {e}")
            continue

    if not all_dfs:
        raise ValueError("No valid curated signal files found")

    # Concatenate all dataframes
    merged_df = pd.concat(all_dfs, ignore_index=True)
    _log(f"Merged {len(all_dfs)} files into {len(merged_df)} total rows")

    # Remove duplicates based on key columns
    key_cols = ["ts", "underlying", "strike", "side"]
    key_cols = [c for c in key_cols if c in merged_df.columns]

    if key_cols:
        before_dedup = len(merged_df)
        merged_df = merged_df.drop_duplicates(subset=key_cols, keep="first")
        deduped = before_dedup - len(merged_df)
        if deduped > 0:
            _log(f"Removed {deduped} duplicate rows")

    # Log total NULL timestamp drops
    if total_null_dropped > 0:
        _log(f"WARNING: Total NULL timestamps dropped across all files: {total_null_dropped}")

    return merged_df, file_stats


def validate_output(df: pd.DataFrame) -> dict:
    """Validate the aggregated dataset."""
    errors = []
    warnings = []

    # Check required columns
    required_cols = ["ts", "underlying", "strike", "side"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    # Check timestamp coverage
    df_ts = pd.to_datetime(df["ts"], errors="coerce")
    min_date = df_ts.min()
    max_date = df_ts.max()
    unique_dates = df_ts.dt.date.nunique()

    if unique_dates < 2:
        warnings.append(f"Only {unique_dates} unique date(s) - need multiple days for forward returns")

    # Check for nulls in key columns
    for col in required_cols:
        if col in df.columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                warnings.append(f"{col}: {null_count} null values ({null_count/len(df)*100:.1f}%)")

    return {
        "total_rows": len(df),
        "unique_dates": int(unique_dates),
        "date_range": {
            "min": str(min_date),
            "max": str(max_date),
        },
        "columns": list(df.columns),
        "errors": errors,
        "warnings": warnings,
    }


def run_phase220(days_back: int = 14) -> dict:
    """Run Phase 220: Historical Signal Aggregation."""
    _log("=" * 70)
    _log("SYSTEM3 PHASE 220 - HISTORICAL CURATED SIGNALS AGGREGATION")
    _log("=" * 70)
    _log(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    _log("")

    start_time = time.time()

    try:
        # Step 1: Find archives
        _log(f"Step 1: Searching for curated signal archives (last {days_back} days)...")
        archive_files = find_curated_archives(days_back=days_back)

        if not archive_files:
            return {
                "phase": 220,
                "status": "ERROR",
                "details": "No curated signal archives found",
                "outputs": {},
                "errors": ["No archive files found in search paths"],
            }

        _log(f"Found {len(archive_files)} curated signal files")

        # Step 2: Load and merge
        _log("\nStep 2: Loading and merging signal files...")
        merged_df, file_stats = load_and_merge_signals(archive_files)

        # Step 3: Validate
        _log("\nStep 3: Validating aggregated dataset...")
        validation = validate_output(merged_df)

        # Log validation results
        _log(f"Total rows: {validation['total_rows']}")
        _log(f"Unique dates: {validation['unique_dates']}")
        _log(f"Date range: {validation['date_range']['min']} to {validation['date_range']['max']}")

        for warning in validation["warnings"]:
            _log(f"WARNING: {warning}")

        for error in validation["errors"]:
            _log(f"ERROR: {error}")

        if validation["errors"]:
            return {
                "phase": 220,
                "status": "ERROR",
                "details": "Validation failed",
                "outputs": validation,
                "errors": validation["errors"],
            }

        # Step 4: Write output
        _log("\nStep 4: Writing aggregated dataset...")
        OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        merged_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
        _log(f"Wrote {len(merged_df)} rows to {OUTPUT_CSV}")

        # Step 5: Write validation JSON
        duration = time.time() - start_time

        # Metrics for null merge keys
        merge_key_cols = [c for c in ["ts", "underlying", "strike", "side", "expiry"] if c in merged_df.columns]
        null_key_rows = merged_df[merge_key_cols].isna().any(axis=1).sum() if merge_key_cols else 0
        null_key_rate = null_key_rows / len(merged_df) if len(merged_df) else 0.0
        null_warn = null_key_rate > 0.01
        if null_warn:
            _log(f"WARNING: Null merge keys detected: {null_key_rows} rows ({null_key_rate:.2%})")
        merge_metrics = {
            "timestamp": datetime.now().isoformat(),
            "phase": 220,
            "total_rows": int(len(merged_df)),
            "null_key_rows": int(null_key_rows),
            "null_key_rate": round(null_key_rate, 6),
            "threshold": 0.01,
            "status": "WARN" if null_warn else "OK",
            "production_blocker": null_warn,
            "duration_seconds": round(duration, 4),
        }
        metrics_path = METRICS_DIR / "phase_220_key_quality.json"
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        with metrics_path.open("w", encoding="utf-8") as f:
            json.dump(merge_metrics, f, indent=2)

        validation_data = {
            "timestamp": datetime.now().isoformat(),
            "phase": 220,
            "files_processed": len(archive_files),
            "file_stats": file_stats,
            "output": validation,
            "output_file": str(OUTPUT_CSV),
            "duration_seconds": round(duration, 4),
            "metrics_file": str(metrics_path),
        }

        with VALIDATION_JSON.open("w", encoding="utf-8") as f:
            json.dump(validation_data, f, indent=2)

        _log(f"Validation report: {VALIDATION_JSON}")

        status = "OK" if validation["unique_dates"] >= 2 and not null_warn else "WARN"

        _log("\n" + "=" * 70)
        _log(f"Phase 220: {status}")
        _log("=" * 70)

        return {
            "phase": 220,
            "status": status,
            "details": f"Aggregated {len(archive_files)} files into {len(merged_df)} rows across {validation['unique_dates']} dates",
            "outputs": {
                "output_file": str(OUTPUT_CSV),
                "validation_file": str(VALIDATION_JSON),
                "metrics_file": str(metrics_path),
                "total_rows": len(merged_df),
                "unique_dates": validation["unique_dates"],
                "date_range": validation["date_range"],
                "duration_seconds": round(duration, 4),
            },
            "errors": validation["errors"],
            "warnings": validation["warnings"]
            + ([f"Null merge keys: {null_key_rows} rows ({null_key_rate:.2%})"] if null_warn else []),
        }

    except Exception as e:
        import traceback

        error_msg = f"Phase 220 failed: {e}"
        trace = traceback.format_exc()
        _log(f"ERROR: {error_msg}")
        _log(trace)
        return {
            "phase": 220,
            "status": "ERROR",
            "details": error_msg,
            "outputs": {},
            "errors": [error_msg],
        }


if __name__ == "__main__":
    result = run_phase220()
    print(f"\nPhase {result['phase']}: {result['status']} - {result['details']}")
