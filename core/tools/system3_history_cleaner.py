"""
System3 history cleaner - remove malformed CSV rows with wrong column counts.

This module is intentionally lightweight and uses only the Python standard
library (csv, os, glob, datetime, pathlib) so it can be reused from
maintenance scripts without pulling in heavy dependencies.
"""

from __future__ import annotations

import csv
import glob
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any


LOGS_DIR = Path("logs")


@dataclass
class CleanResult:
    path: str
    status: str
    total_rows: int = 0
    kept_rows: int = 0
    dropped_rows: int = 0
    expected_width: int = 0


def _history_log_path() -> Path:
    """
    Per-spec cleaning report path:
      logs/data_cleaning/cleaning_report_YYYYMMDD.log
    """
    data_clean_dir = LOGS_DIR / "data_cleaning"
    data_clean_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d")
    return data_clean_dir / f"cleaning_report_{ts}.log"


def _append_history_log(lines: List[str]) -> None:
    log_path = _history_log_path()
    with log_path.open("a", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")


def get_header_and_width(path: str) -> Tuple[List[str], int]:
    """
    Read the header row of a CSV file and return (fields, expected_width).
    """
    p = Path(path)
    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return [], 0
    return header, len(header)


def clean_csv_file(path: str, backup: bool = True) -> Dict[str, Any]:
    """
    Remove malformed rows (wrong column count) from a CSV file.

    - Keeps the header row as-is.
    - Keeps only rows where len(row) == expected_width (from header).
    - Optionally creates a .bak copy before overwriting.
    """
    p = Path(path)
    if not p.exists():
        result = CleanResult(path=str(p), status="missing")
        _append_history_log(
            [
                "==== CLEANED FILE ====",
                f"file: {result.path}",
                "original_rows: 0",
                "cleaned_rows: 0",
                "removed_rows: 0",
                "removed_line_numbers (1-based including header): []",
            ]
        )
        return asdict(result)

    header, expected_width = get_header_and_width(str(p))
    if expected_width == 0:
        result = CleanResult(path=str(p), status="empty", expected_width=0)
        _append_history_log(
            [
                "==== CLEANED FILE ====",
                f"file: {result.path}",
                "original_rows: 0",
                "cleaned_rows: 0",
                "removed_rows: 0",
                "removed_line_numbers (1-based including header): []",
            ]
        )
        return asdict(result)

    total_rows = 0  # includes header
    kept_rows = 0  # includes header
    dropped_rows = 0
    removed_line_numbers: List[int] = []

    # Backup original if requested
    if backup:
        backup_path = p.with_suffix(p.suffix + ".bak")
        try:
            if backup_path.exists():
                backup_path.unlink()
            p.replace(backup_path)
            src_for_read = backup_path
        except Exception:
            # If backup fails for any reason, still try to clean in-place
            src_for_read = p
    else:
        src_for_read = p

    # Stream read from src_for_read, write cleaned content to temporary file
    tmp_path = p.with_suffix(p.suffix + ".tmp")
    with (
        src_for_read.open("r", encoding="utf-8", newline="") as src,
        tmp_path.open("w", encoding="utf-8", newline="") as dst,
    ):
        reader = csv.reader(src)
        writer = csv.writer(dst)

        # Write header as-is (line 1)
        writer.writerow(header)
        kept_rows += 1
        total_rows += 1

        # Process remaining rows, tracking line numbers (1-based, header = line 1)
        line_no = 1
        for row in reader:
            line_no += 1
            total_rows += 1
            if len(row) == expected_width:
                writer.writerow(row)
                kept_rows += 1
            else:
                dropped_rows += 1
                removed_line_numbers.append(line_no)

    # Replace original with cleaned tmp
    try:
        if p.exists():
            p.unlink()
        tmp_path.replace(p)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)  # type: ignore[call-arg]

    result = CleanResult(
        path=str(p),
        status="cleaned",
        total_rows=total_rows,
        kept_rows=kept_rows,
        dropped_rows=dropped_rows,
        expected_width=expected_width,
    )

    # Logging per spec
    original_rows = result.total_rows
    cleaned_rows = result.kept_rows
    removed_rows = result.dropped_rows

    _append_history_log(
        [
            "==== CLEANED FILE ====",
            f"file: {result.path}",
            f"original_rows: {original_rows}",
            f"cleaned_rows: {cleaned_rows}",
            f"removed_rows: {removed_rows}",
            "removed_line_numbers (1-based including header): "
            + (str(removed_line_numbers) if removed_line_numbers else "[]"),
        ]
    )

    return asdict(result)


def clean_all_history_files() -> List[Dict[str, Any]]:
    """
    Clean malformed rows from the main live history file and all archived CSVs.
    """
    results: List[Dict[str, Any]] = []

    # Main live file
    live_path = os.path.join("storage", "live", "dhan_index_ai_signals.csv")
    results.append(clean_csv_file(live_path, backup=True))

    # Archived CSVs
    archive_glob = os.path.join("storage", "live", "archive", "*.csv")
    for path in sorted(glob.glob(archive_glob)):
        results.append(clean_csv_file(path, backup=True))

    return results
