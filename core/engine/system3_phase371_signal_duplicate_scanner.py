"""
System3 Phase 371 - Signal Duplicate Scanner

Scans cleaned signal files for duplicate and conflicting signals.
Identifies exact duplicates and same-symbol conflicting signals.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_CLEAN = PROJECT_ROOT / "storage" / "live" / "clean"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

logger = logging.getLogger(__name__)


def scan_for_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    """Scan dataframe for duplicate signals."""
    dup_analysis = {
        "total_rows": len(df),
        "exact_duplicates": 0,
        "symbol_conflicts": 0,
        "duplicate_groups": [],
        "conflict_groups": [],
    }

    # Identify exact duplicates (all columns match)
    duplicates = df[df.duplicated(keep=False)]
    dup_analysis["exact_duplicates"] = len(duplicates)

    if len(duplicates) > 0:
        # Group duplicates
        dup_groups = duplicates.groupby(list(duplicates.columns)).size().reset_index(name="count")
        dup_analysis["duplicate_groups"] = dup_groups.to_dict("records")[:10]  # Top 10

    # Identify conflicting signals (same symbol, different signal)
    if "symbol" in df.columns and "signal" in df.columns:
        conflicts = df.groupby("symbol")["signal"].apply(lambda x: x.nunique() > 1)
        conflict_symbols = conflicts[conflicts].index.tolist()
        dup_analysis["symbol_conflicts"] = len(conflict_symbols)
        dup_analysis["conflict_groups"] = conflict_symbols[:10]  # Top 10

    return dup_analysis


def run_phase371(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute Phase 371: Signal Duplicate Scanner."""
    logger.info("=== Phase 371: Signal Duplicate Scanner ===")

    result = {
        "phase": 371,
        "name": "Signal Duplicate Scanner",
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "scan_results": [],
        "outputs": {},
    }

    try:
        # Scan cleaned files
        clean_files = list(STORAGE_CLEAN.glob("*_clean.csv"))

        if not clean_files:
            result["status"] = "warn"
            result["message"] = "No cleaned files found. Run Phase 370 first."
            return result

        for file_path in clean_files:
            logger.info(f"Scanning: {file_path.name}")

            df = pd.read_csv(file_path, on_bad_lines="skip", low_memory=False)
            dup_result = scan_for_duplicates(df)
            dup_result["file"] = file_path.name
            result["scan_results"].append(dup_result)

        # Write outputs
        json_output = STORAGE_METRICS / "duplicate_scan_371.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        result["outputs"]["json"] = str(json_output)

        md_output = REPORTS_DIR / "DUPLICATE_SCAN_371.md"
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# Signal Duplicate Scan - Phase 371\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for scan in result["scan_results"]:
                f.write(f"## {scan['file']}\n\n")
                f.write(f"- Total Rows: {scan['total_rows']}\n")
                f.write(f"- Exact Duplicates: {scan['exact_duplicates']}\n")
                f.write(f"- Symbol Conflicts: {scan['symbol_conflicts']}\n\n")

        result["outputs"]["report"] = str(md_output)
        logger.info(f"Phase 371 complete")
        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Phase 371 error: {e}", exc_info=True)
        return result


def main():
    """Standalone execution."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    result = run_phase371()
    print(f"\nPhase 371: {result['status'].upper()}")
    print(f"Scanned {len(result.get('scan_results', []))} file(s)")


if __name__ == "__main__":
    main()
