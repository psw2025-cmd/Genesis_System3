"""
System3 Phase 370 - Signal Schema Auto-Normalizer

Non-destructively repairs signal CSV files with schema mismatches.
Archives originals with timestamps before any modifications.
"""

import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_CLEAN = STORAGE_LIVE / "clean"
STORAGE_ARCHIVE = STORAGE_LIVE / "raw_backup"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Create directories
STORAGE_CLEAN.mkdir(parents=True, exist_ok=True)
STORAGE_ARCHIVE.mkdir(parents=True, exist_ok=True)
STORAGE_METRICS.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)

# Expected schema for signal files (from Phase 339 requirements)
EXPECTED_COLUMNS = [
    "underlying",
    "symbol",
    "signal",
    "spot",
    "expiry",
    "strike",
    "ltp",
    "iv",
    "delta",
    "gamma",
    "theta",
    "vega",
    "rho",
    "confidence",
    "score",
    "pred_label",
    "pred_proba",
    "fwd_ret_1",
    "fwd_ret_2",
    "fwd_ret_3",
    "fwd_ret_5",
    "time_to_expiry",
    "timestamp",
    "data_source",
]


def backup_file(source_path: Path) -> Tuple[bool, str]:
    """Create timestamped backup of original file."""
    if not source_path.exists():
        return False, f"Source file not found: {source_path}"

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{source_path.stem}_backup_{timestamp}{source_path.suffix}"
        backup_path = STORAGE_ARCHIVE / backup_filename

        shutil.copy2(source_path, backup_path)
        logger.info(f"Backed up: {source_path.name} → {backup_path.name}")

        return True, str(backup_path)

    except Exception as e:
        logger.error(f"Backup failed for {source_path}: {e}")
        return False, str(e)


def detect_schema_issues(df: pd.DataFrame, expected_cols: List[str]) -> Dict[str, Any]:
    """Detect schema mismatches between actual and expected columns."""
    actual_cols = set(df.columns)
    expected_set = set(expected_cols)

    issues = {
        "missing_columns": list(expected_set - actual_cols),
        "extra_columns": list(actual_cols - expected_set),
        "has_issues": False,
    }

    issues["has_issues"] = bool(issues["missing_columns"] or issues["extra_columns"])

    return issues


def normalize_schema(df: pd.DataFrame, expected_cols: List[str]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Normalize dataframe to expected schema."""
    normalization_log = {"columns_added": [], "columns_removed": [], "columns_reordered": False}

    df_normalized = df.copy()

    # Add missing columns with NaN
    for col in expected_cols:
        if col not in df_normalized.columns:
            df_normalized[col] = np.nan
            normalization_log["columns_added"].append(col)
            logger.info(f"Added missing column: {col}")

    # Remove extra columns that are not in expected schema
    extra_cols = [col for col in df_normalized.columns if col not in expected_cols]
    if extra_cols:
        df_normalized = df_normalized.drop(columns=extra_cols)
        normalization_log["columns_removed"] = extra_cols
        logger.info(f"Removed extra columns: {extra_cols}")

    # Reorder columns to match expected schema
    available_cols = [col for col in expected_cols if col in df_normalized.columns]
    df_normalized = df_normalized[available_cols]
    normalization_log["columns_reordered"] = True

    return df_normalized, normalization_log


def repair_signal_file(file_path: Path, expected_cols: List[str]) -> Dict[str, Any]:
    """Repair a single signal file with schema normalization."""
    repair_result = {
        "file": file_path.name,
        "status": "ok",
        "backed_up": False,
        "normalized": False,
        "issues_detected": {},
        "normalization_log": {},
        "rows_before": 0,
        "rows_after": 0,
    }

    if not file_path.exists():
        repair_result["status"] = "error"
        repair_result["error"] = "File not found"
        return repair_result

    try:
        # Load original file
        df_original = pd.read_csv(file_path, on_bad_lines="skip", low_memory=False)
        repair_result["rows_before"] = len(df_original)

        # Detect schema issues
        issues = detect_schema_issues(df_original, expected_cols)
        repair_result["issues_detected"] = issues

        if not issues["has_issues"]:
            repair_result["status"] = "ok"
            repair_result["message"] = "No schema issues detected"
            repair_result["rows_after"] = len(df_original)
            return repair_result

        # Backup original file
        backup_success, backup_path = backup_file(file_path)
        repair_result["backed_up"] = backup_success
        repair_result["backup_path"] = backup_path if backup_success else None

        if not backup_success:
            repair_result["status"] = "warn"
            repair_result["message"] = "Backup failed, skipping normalization for safety"
            return repair_result

        # Normalize schema
        df_normalized, norm_log = normalize_schema(df_original, expected_cols)
        repair_result["normalization_log"] = norm_log
        repair_result["normalized"] = True
        repair_result["rows_after"] = len(df_normalized)

        # Write normalized file to clean directory
        clean_filename = f"{file_path.stem}_clean{file_path.suffix}"
        clean_path = STORAGE_CLEAN / clean_filename

        df_normalized.to_csv(clean_path, index=False)
        repair_result["clean_path"] = str(clean_path)

        logger.info(f"Normalized {file_path.name} → {clean_path.name}")
        logger.info(f"  Added columns: {len(norm_log['columns_added'])}")
        logger.info(f"  Removed columns: {len(norm_log.get('columns_removed', []))}")

        return repair_result

    except Exception as e:
        repair_result["status"] = "error"
        repair_result["error"] = str(e)
        logger.error(f"Error repairing {file_path}: {e}", exc_info=True)
        return repair_result


def run_phase370(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute Phase 370: Signal Schema Auto-Normalizer.

    Returns:
        dict: {
            "status": "ok" | "warn" | "error",
            "files_processed": int,
            "files_repaired": int,
            "outputs": {"json": path, "report": path}
        }
    """
    logger.info("=== Phase 370: Signal Schema Auto-Normalizer ===")

    result = {
        "phase": 370,
        "name": "Signal Schema Auto-Normalizer",
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "files_processed": 0,
        "files_repaired": 0,
        "repair_results": [],
        "outputs": {},
    }

    try:
        # Target signal files
        signal_files = [
            STORAGE_LIVE / "dhan_index_ai_signals.csv",
            STORAGE_LIVE / "dhan_index_ai_signals_curated.csv",
            STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv",
        ]

        # Process each file
        for file_path in signal_files:
            if file_path.exists():
                logger.info(f"Processing: {file_path.name}")
                repair_res = repair_signal_file(file_path, EXPECTED_COLUMNS)
                result["repair_results"].append(repair_res)
                result["files_processed"] += 1

                if repair_res.get("normalized"):
                    result["files_repaired"] += 1
            else:
                logger.warning(f"File not found: {file_path}")
                result["repair_results"].append(
                    {"file": file_path.name, "status": "not_found", "error": "File does not exist"}
                )

        # Check if any repairs failed
        failed_repairs = [r for r in result["repair_results"] if r["status"] == "error"]
        if failed_repairs:
            result["status"] = "warn"
            result["message"] = f"{len(failed_repairs)} file(s) failed to repair"

        # Write JSON output
        json_output = STORAGE_METRICS / "schema_normalization_370.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        result["outputs"]["json"] = str(json_output)
        logger.info(f"JSON written to: {json_output}")

        # Write Markdown report
        md_output = REPORTS_DIR / "SIGNAL_SCHEMA_NORMALIZATION_370.md"
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# Signal Schema Normalization - Phase 370\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            f.write(f"## Summary\n\n")
            f.write(f"**Files Processed:** {result['files_processed']}\n")
            f.write(f"**Files Repaired:** {result['files_repaired']}\n")
            f.write(f"**Status:** {result['status'].upper()}\n\n")

            f.write("---\n\n")
            f.write("## Repair Results\n\n")

            for repair_res in result["repair_results"]:
                status_emoji = (
                    "✅" if repair_res["status"] == "ok" else ("⚠️" if repair_res["status"] == "warn" else "❌")
                )
                f.write(f"### {status_emoji} {repair_res['file']}\n\n")
                f.write(f"**Status:** {repair_res['status']}\n")

                if repair_res.get("backed_up"):
                    f.write(f"**Backup Created:** ✅ Yes\n")
                    f.write(f"**Backup Path:** `{repair_res.get('backup_path', 'N/A')}`\n")

                if repair_res.get("normalized"):
                    f.write(f"**Normalized:** ✅ Yes\n")
                    f.write(f"**Clean File:** `{repair_res.get('clean_path', 'N/A')}`\n")

                    norm_log = repair_res.get("normalization_log", {})
                    if norm_log.get("columns_added"):
                        f.write(f"**Columns Added:** {', '.join(norm_log['columns_added'])}\n")
                    if norm_log.get("columns_removed"):
                        f.write(f"**Columns Removed:** {', '.join(norm_log['columns_removed'])}\n")

                f.write(f"**Rows Before:** {repair_res.get('rows_before', 0)}\n")
                f.write(f"**Rows After:** {repair_res.get('rows_after', 0)}\n")

                issues = repair_res.get("issues_detected", {})
                if issues.get("has_issues"):
                    f.write("\n**Issues Detected:**\n")
                    if issues.get("missing_columns"):
                        f.write(f"- Missing columns: {', '.join(issues['missing_columns'])}\n")
                    if issues.get("extra_columns"):
                        f.write(f"- Extra columns: {', '.join(issues['extra_columns'])}\n")

                if repair_res.get("error"):
                    f.write(f"\n**Error:** {repair_res['error']}\n")

                f.write("\n")

            f.write("---\n\n")
            f.write("## Next Steps\n\n")
            f.write("1. Review cleaned files in `storage/live/clean/`\n")
            f.write("2. Run Phase 371 (Duplicate Scanner) on cleaned files\n")
            f.write("3. Original files backed up in `storage/live/raw_backup/`\n")

        result["outputs"]["report"] = str(md_output)
        logger.info(f"Report written to: {md_output}")

        logger.info(f"Phase 370 complete: {result['files_repaired']}/{result['files_processed']} files repaired")
        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Phase 370 error: {e}", exc_info=True)
        return result


def main():
    """Standalone execution."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    result = run_phase370()

    print("\n" + "=" * 60)
    print("PHASE 370 - SIGNAL SCHEMA AUTO-NORMALIZER")
    print("=" * 60)
    print(f"Status: {result['status'].upper()}")
    print(f"Files Processed: {result['files_processed']}")
    print(f"Files Repaired: {result['files_repaired']}")

    if result.get("outputs"):
        print("\nOutputs:")
        for key, path in result["outputs"].items():
            print(f"  {key}: {path}")

    print("=" * 60)


if __name__ == "__main__":
    main()
