import os
from pathlib import Path
from datetime import datetime
import shutil
from typing import List

import pandas as pd

from core.engine.ai_model.ml_predictor import (
    CURATED_TRAINING_PATH,
    LIVE_TRAINING_PATH,
)
from core.tools.system3_history_cleaner import clean_all_history_files
from core.utils.logger import logger

# Enable/disable curated training export
ENABLE_CURATED_EXPORT = True
CURATED_LOOKBACK_DAYS = 5


def _open_prep_log() -> Path:
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d")
    log_path = logs_dir / f"system3_prep_for_new_day_{ts}.log"
    return log_path


def _log(lines: List[str]) -> None:
    """Write messages to both stdout and the daily prep log."""
    log_path = _open_prep_log()
    with log_path.open("a", encoding="utf-8") as f:
        for line in lines:
            print(line)
            f.write(line + "\n")


def archive_old_live_signals() -> dict:
    """
    If storage/live/angel_index_ai_signals.csv exists,
    move it into storage/live/archive/ with a timestamped name.

    Returns a dict summary with keys:
      - 'found': bool
      - 'src': str | None
      - 'dst': str | None
      - 'rows': int | None
    """
    root = Path(__file__).resolve().parent
    live_csv = root / LIVE_TRAINING_PATH
    archive_dir = root / "storage" / "live" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    if live_csv.exists():
        # Try to count rows for logging (safe best-effort)
        rows = None
        try:
            df_preview = pd.read_csv(live_csv, engine="python", on_bad_lines="skip")
            rows = len(df_preview)
        except Exception:
            rows = None

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst_name = f"angel_index_ai_signals_{ts}_before_new_day.csv"
        dst = archive_dir / dst_name
        shutil.move(str(live_csv), str(dst))
        return {"found": True, "src": str(live_csv), "dst": str(dst), "rows": rows}

    return {"found": False, "src": str(live_csv), "dst": None, "rows": None}


def build_curated_training_from_archive(root: Path) -> None:
    """
    Scan storage/live/archive for recent CSVs and build a curated training file
    using robust CSV loading (engine='python', on_bad_lines='skip').
    """
    if not ENABLE_CURATED_EXPORT:
        _log(["[INFO] Curated training export is disabled. Skipping."])
        return

    archive_dir = root / "storage" / "live" / "archive"
    if not archive_dir.exists():
        _log(["[INFO] No archive directory found for curated export. Skipping."])
        return

    csv_files = sorted(
        [p for p in archive_dir.glob("angel_index_ai_signals_*.csv") if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not csv_files:
        _log(["[INFO] No archived live signal CSV files found. Skipping curated export."])
        return

    # Limit to last CURATED_LOOKBACK_DAYS by modification time
    selected_files: List[Path] = []
    cutoff = datetime.now().timestamp() - CURATED_LOOKBACK_DAYS * 24 * 3600
    for p in csv_files:
        if p.stat().st_mtime >= cutoff:
            selected_files.append(p)
    if not selected_files:
        selected_files = csv_files[:CURATED_LOOKBACK_DAYS]

    _log(
        [
            "[INFO] Building curated training dataset from archive files:",
            *[f"  - {p}" for p in selected_files],
        ]
    )

    frames = []
    for p in selected_files:
        try:
            df = pd.read_csv(p, engine="python", on_bad_lines="skip")
            if not df.empty:
                frames.append(df)
        except Exception as e:
            _log([f"[WARN] Failed to read archived CSV {p}: {e}"])

    if not frames:
        _log(["[WARN] No usable rows found in archive; curated training dataset not created."])
        return

    full_df = pd.concat(frames, ignore_index=True)

    # Drop clearly malformed rows (missing essential columns)
    essential_cols = [c for c in ["ts", "spot", "underlying"] if c in full_df.columns]
    if essential_cols:
        before = len(full_df)
        full_df = full_df.dropna(subset=essential_cols)
        after = len(full_df)
        _log(
            [
                f"[INFO] Curated dataset rows before dropna({essential_cols}): {before}",
                f"[INFO] Curated dataset rows after dropna: {after}",
            ]
        )

    if full_df.empty:
        _log(["[WARN] Curated dataset is empty after cleaning; not writing file."])
        return

    curated_path = root / CURATED_TRAINING_PATH
    curated_path.parent.mkdir(parents=True, exist_ok=True)
    full_df.to_csv(curated_path, index=False)
    _log([f"[OK] Curated training dataset written to: {curated_path} (rows={len(full_df)})"])


def run_history_cleanup_phase() -> None:
    """Run the CSV history cleaner across live + archive files and log results."""
    logger.info("=== HISTORY CLEANUP PHASE: CLEANING MALFORMED ROWS ===")
    results = clean_all_history_files()
    for r in results:
        logger.info(
            "Cleaned file: %(path)s | status=%(status)s | total=%(total_rows)s | "
            "kept=%(kept_rows)s | dropped=%(dropped_rows)s | width=%(expected_width)s",
            r,
        )
    logger.info("=== HISTORY CLEANUP PHASE COMPLETE ===")


def main() -> None:
    print("=== SYSTEM3 NEW DAY PREP ===")
    root = Path(__file__).resolve().parent
    print(f"Repo root: {root}")

    summary = archive_old_live_signals()
    if summary["found"]:
        _log(
            [
                "Archived existing live signals CSV:",
                f"  From: {summary['src']}",
                f"  To  : {summary['dst']}",
                f"  Rows: {summary['rows']}",
            ]
        )
    else:
        _log(["No existing live signals CSV found. Nothing to archive."])

    # Clean malformed rows from live + archive history before building curated set
    run_history_cleanup_phase()

    # Optionally build curated training dataset from recent archive
    build_curated_training_from_archive(root)

    print()
    print("Prep done. You can now run:")
    print("  system3_live_day_autopilot.bat")


if __name__ == "__main__":
    main()
