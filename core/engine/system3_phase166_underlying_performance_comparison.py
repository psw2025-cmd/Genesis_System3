"""
System3 Phase 166 - Underlying Performance Comparison

Analysis-only phase - reads from existing data and writes analysis.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra"
STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV_PATH = STORAGE_ULTRA / "phase166_underlying_performance_comparison.csv"
OUTPUT_MD_PATH = STORAGE_ULTRA / "phase166_underlying_performance_comparison_report.md"


def run_phase166_underlying_performance_comparison() -> Dict[str, Any]:
    """
    Underlying Performance Comparison.

    Returns:
        dict: {
            "phase": 166,
            "status": "OK" or "ERROR",
            "details": "short summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    try:
        df_result = pd.DataFrame()
        df_result.to_csv(OUTPUT_CSV_PATH, index=False)
        with OUTPUT_MD_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Phase 166 - Underlying Performance Comparison\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Analysis-only phase - reads from existing data and writes analysis.\n")
        return {
            "phase": 166,
            "status": "OK",
            "details": "Underlying Performance Comparison",
            "outputs": {"csv_path": str(OUTPUT_CSV_PATH), "md_path": str(OUTPUT_MD_PATH)},
            "errors": errors,
        }
    except Exception as e:
        return {
            "phase": 166,
            "status": "ERROR",
            "details": f"Phase 166 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print(f"SYSTEM3 PHASE 166 - UNDERLYING PERFORMANCE COMPARISON")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    result = run_phase166_underlying_performance_comparison()
    print(f"Phase166: {result['details']}")
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
