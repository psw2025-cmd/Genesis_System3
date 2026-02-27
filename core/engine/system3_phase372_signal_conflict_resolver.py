"""
System3 Phase 372 - Signal Conflict Resolver

Resolves conflicting signals by keeping most confident/recent signal per symbol.
Creates deduplicated signal files.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_CLEAN = PROJECT_ROOT / "storage" / "live" / "clean"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

logger = logging.getLogger(__name__)


def resolve_conflicts(df: pd.DataFrame) -> pd.DataFrame:
    """Resolve conflicts by keeping highest confidence signal per symbol."""
    if "symbol" not in df.columns:
        return df

    # Remove exact duplicates first
    df = df.drop_duplicates()

    # Resolve symbol conflicts - keep highest confidence
    if "confidence" in df.columns:
        df = df.sort_values("confidence", ascending=False).groupby("symbol").first().reset_index()
    elif "score" in df.columns:
        df = df.sort_values("score", ascending=False).groupby("symbol").first().reset_index()
    else:
        df = df.groupby("symbol").first().reset_index()

    return df


def run_phase372(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute Phase 372: Signal Conflict Resolver."""
    logger.info("=== Phase 372: Signal Conflict Resolver ===")

    result = {
        "phase": 372,
        "name": "Signal Conflict Resolver",
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "resolution_results": [],
        "outputs": {},
    }

    try:
        clean_files = list(STORAGE_CLEAN.glob("*_clean.csv"))

        for file_path in clean_files:
            df_before = pd.read_csv(file_path, on_bad_lines="skip", low_memory=False)
            rows_before = len(df_before)

            df_after = resolve_conflicts(df_before)
            rows_after = len(df_after)

            # Write deduplicated file
            dedup_path = STORAGE_CLEAN / file_path.name.replace("_clean", "_dedup")
            df_after.to_csv(dedup_path, index=False)

            result["resolution_results"].append(
                {
                    "file": file_path.name,
                    "rows_before": rows_before,
                    "rows_after": rows_after,
                    "rows_removed": rows_before - rows_after,
                    "dedup_file": dedup_path.name,
                }
            )

            logger.info(f"Resolved {file_path.name}: {rows_before} → {rows_after} rows")

        # Write outputs
        json_output = STORAGE_METRICS / "conflict_resolution_372.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        result["outputs"]["json"] = str(json_output)

        md_output = REPORTS_DIR / "CONFLICT_RESOLUTION_372.md"
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# Signal Conflict Resolution - Phase 372\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for res in result["resolution_results"]:
                f.write(f"## {res['file']}\n\n")
                f.write(f"- Rows Before: {res['rows_before']}\n")
                f.write(f"- Rows After: {res['rows_after']}\n")
                f.write(f"- Rows Removed: {res['rows_removed']}\n")
                f.write(f"- Output: `{res['dedup_file']}`\n\n")

        result["outputs"]["report"] = str(md_output)
        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Phase 372 error: {e}", exc_info=True)
        return result


def main():
    """Standalone execution."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    result = run_phase372()
    print(f"\nPhase 372: {result['status'].upper()}")
    for res in result.get("resolution_results", []):
        print(f"  {res['file']}: {res['rows_removed']} rows removed")


if __name__ == "__main__":
    main()
