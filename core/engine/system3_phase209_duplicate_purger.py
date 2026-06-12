"""
System3 Phase 209 - Training Data Duplicate Purger

Removes duplicate rows from curated training data.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "data_cleaning"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_duplicate_purger.log"

CURATED_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_curated.csv"


def run_phase209(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 209: Training Data Duplicate Purger.

    Returns:
        dict: {
            "phase": 209,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "original_rows": int,
                "deduplicated_rows": int,
                "purged_count": int,
            },
            "errors": [],
        }
    """
    errors = []

    try:
        if not CURATED_CSV.exists():
            return {
                "phase": 209,
                "status": "WARN",
                "details": "Curated CSV not found",
                "outputs": {"original_rows": 0, "deduplicated_rows": 0, "purged_count": 0},
                "errors": [],
            }

        # Load with robust parser
        try:
            df = pd.read_csv(CURATED_CSV)
        except Exception:
            df = pd.read_csv(CURATED_CSV, engine="python", on_bad_lines="skip")

        original_rows = len(df)

        # Filter out header rows before deduplication
        header_rows_removed = 0
        if "pred_label" in df.columns:
            before = len(df)
            df = df[df["pred_label"] != "pred_label"]
            header_rows_removed += before - len(df)
        if "underlying" in df.columns:
            before = len(df)
            df = df[df["underlying"] != "underlying"]
            header_rows_removed += before - len(df)

        # Filter out header rows (rows where column names appear as values)
        if "pred_label" in df.columns:
            # Remove rows where pred_label equals the column name itself
            df = df[df["pred_label"] != "pred_label"]
        if "underlying" in df.columns:
            # Remove rows where underlying equals the column name itself
            df = df[df["underlying"] != "underlying"]

        # Identify duplicates based on composite key
        key_cols = ["ts", "underlying", "strike", "side", "expiry"]
        available_cols = [col for col in key_cols if col in df.columns]

        if len(available_cols) < 3:
            return {
                "phase": 209,
                "status": "WARN",
                "details": "Insufficient columns for deduplication",
                "outputs": {
                    "original_rows": original_rows,
                    "deduplicated_rows": len(df),
                    "purged_count": original_rows - len(df),
                },
                "errors": [],
            }

        # Keep most recent row per key (if ts exists, sort by it)
        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
            df = df.sort_values("ts", na_position="last")

        # Drop duplicates, keeping last (most recent)
        df_dedup = df.drop_duplicates(subset=available_cols, keep="last")

        deduplicated_rows = len(df_dedup)
        purged_count = original_rows - deduplicated_rows

        # Backup and rewrite
        if purged_count > 0:
            backup_path = CURATED_CSV.with_suffix(".csv.bak")
            df.to_csv(backup_path, index=False)
            df_dedup.to_csv(CURATED_CSV, index=False)

        # Log
        with LOG_PATH.open("w", encoding="utf-8") as f:
            f.write(f"System3 Duplicate Purger Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"File: {CURATED_CSV}\n")
            f.write(f"Original Rows: {original_rows}\n")
            f.write(f"Header Rows Removed: {header_rows_removed}\n")
            f.write(f"Deduplicated Rows: {deduplicated_rows}\n")
            f.write(f"Purged Count: {purged_count}\n")
            f.write(f"Key Columns: {', '.join(available_cols)}\n")
            if purged_count > 0 or header_rows_removed > 0:
                f.write(f"\nBackup created: {backup_path}\n")

        status = "OK"
        details = f"Purged {purged_count} duplicates and {header_rows_removed} header rows from {original_rows} rows"

        return {
            "phase": 209,
            "status": status,
            "details": details,
            "outputs": {
                "original_rows": original_rows,
                "deduplicated_rows": deduplicated_rows,
                "purged_count": purged_count,
                "log_path": str(LOG_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 209,
            "status": "ERROR",
            "details": f"Phase 209 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 209 - TRAINING DATA DUPLICATE PURGER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase209()

    print(f"Phase 209: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nLog: {result['outputs']['log_path']}")
        print(f"Original: {result['outputs']['original_rows']}")
        print(f"Deduplicated: {result['outputs']['deduplicated_rows']}")
        print(f"Purged: {result['outputs']['purged_count']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
