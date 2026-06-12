"""
System3 Phase 331 - Signal Input Integrity Scanner

Detects structural issues in live signal CSVs before they are used by trade planning phases.
Checks: missing columns, NaNs in key fields, zero rows, mixed dtypes.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Signal CSV files to check
SIGNAL_FILES = [
    "storage/live/dhan_index_ai_signals.csv",
    "storage/live/dhan_index_ai_signals_curated.csv",
    "storage/live/dhan_index_ai_signals_with_forward.csv",
]

# Required columns for each file
REQUIRED_COLUMNS = {
    "dhan_index_ai_signals.csv": ["underlying", "symbol", "signal", "final_score", "ts"],
    "dhan_index_ai_signals_curated.csv": ["underlying", "symbol", "signal", "final_score", "ts", "pred_label"],
    "dhan_index_ai_signals_with_forward.csv": [
        "underlying",
        "symbol",
        "signal",
        "final_score",
        "ts",
        "fwd_ret_1",
        "fwd_ret_3",
        "fwd_ret_5",
    ],
}

# Key columns that should not have NaN values
CRITICAL_COLUMNS = ["underlying", "symbol", "signal", "final_score", "ts"]


def check_file_integrity(file_path: Path, required_cols: List[str]) -> Dict[str, Any]:
    """
    Check integrity of a single signal CSV file.

    Returns:
        Dict with status and issues found
    """
    issues = []
    warnings = []

    # Check file existence
    if not file_path.exists():
        return {
            "status": "ERROR",
            "issues": [f"File not found: {file_path}"],
            "warnings": [],
            "row_count": 0,
        }

    try:
        # Load CSV
        df = pd.read_csv(file_path, low_memory=False)

        # Check 1: Non-zero rows
        row_count = len(df)
        if row_count == 0:
            issues.append("File has zero rows (excluding header)")

        # Check 2: Required columns present
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f"Missing required columns: {missing_cols}")

        # Check 3: NaN values in critical columns
        for col in CRITICAL_COLUMNS:
            if col in df.columns:
                nan_count = df[col].isna().sum()
                if nan_count > 0:
                    warnings.append(f"Column '{col}' has {nan_count} NaN values ({nan_count/row_count*100:.1f}%)")

        # Check 4: Type consistency for numeric columns
        numeric_cols = ["final_score", "spot", "ltp", "strike"]
        for col in numeric_cols:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors="raise")
                except Exception:
                    non_numeric_count = pd.to_numeric(df[col], errors="coerce").isna().sum()
                    if non_numeric_count > 0:
                        warnings.append(f"Column '{col}' has {non_numeric_count} non-numeric values")

        # Check 5: Signal column values
        if "signal" in df.columns:
            valid_signals = ["BUY", "SELL", "HOLD", "BUY_CE", "BUY_PE", "SELL_CE", "SELL_PE"]
            invalid_signals = df[~df["signal"].isin(valid_signals)]["signal"].unique()
            if len(invalid_signals) > 0:
                warnings.append(f"Unexpected signal values: {list(invalid_signals)[:5]}")

        # Determine status
        if issues:
            status = "WARN"
        elif warnings:
            status = "WARN"
        else:
            status = "OK"

        return {
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "row_count": row_count,
            "columns": list(df.columns),
        }

    except Exception as e:
        logger.error(f"Error checking {file_path}: {e}")
        return {
            "status": "ERROR",
            "issues": [f"Failed to read file: {str(e)}"],
            "warnings": [],
            "row_count": 0,
        }


def run_phase331_signal_integrity(root_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Phase 331: Signal Input Integrity Scanner

    Returns:
        Dict with phase status and results
    """
    logger.info("=" * 70)
    logger.info("PHASE 331: Signal Input Integrity Scanner")
    logger.info("=" * 70)

    root = Path(root_path) if root_path else PROJECT_ROOT

    results = {}
    all_issues = []
    all_warnings = []

    # Check each signal file
    for rel_path in SIGNAL_FILES:
        file_path = root / rel_path
        file_name = Path(rel_path).name

        logger.info(f"Checking: {file_name}")

        required_cols = REQUIRED_COLUMNS.get(file_name, [])
        check_result = check_file_integrity(file_path, required_cols)

        results[file_name] = check_result

        # Log results
        logger.info(f"  Status: {check_result['status']}")
        logger.info(f"  Rows: {check_result['row_count']}")

        if check_result["issues"]:
            for issue in check_result["issues"]:
                logger.warning(f"  ISSUE: {issue}")
                all_issues.append(f"{file_name}: {issue}")

        if check_result["warnings"]:
            for warning in check_result["warnings"]:
                logger.warning(f"  WARN: {warning}")
                all_warnings.append(f"{file_name}: {warning}")

    # Write diagnostics report
    diagnostics_dir = root / "storage" / "live" / "diagnostics"
    diagnostics_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": datetime.now().isoformat(),
        "phase": 331,
        "status": "WARN" if (all_issues or all_warnings) else "OK",
        "files_checked": len(SIGNAL_FILES),
        "total_issues": len(all_issues),
        "total_warnings": len(all_warnings),
        "results": results,
        "issues": all_issues,
        "warnings": all_warnings,
    }

    report_file = diagnostics_dir / "signal_integrity_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Diagnostics written to: {report_file}")

    # Summary
    logger.info("=" * 70)
    logger.info(f"Phase 331 Complete: {report['status']}")
    logger.info(f"Files checked: {len(SIGNAL_FILES)}")
    logger.info(f"Issues: {len(all_issues)}")
    logger.info(f"Warnings: {len(all_warnings)}")
    logger.info("=" * 70)

    return {
        "phase": 331,
        "status": report["status"],
        "outputs": report,
    }


def run_phase_331(**kwargs) -> str:
    """Wrapper for autorun integration - returns status string."""
    result = run_phase331_signal_integrity(**kwargs)
    return result.get("status", "ERROR")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    result = run_phase331_signal_integrity()
    print(f"\nPhase 331 Status: {result['status']}")
