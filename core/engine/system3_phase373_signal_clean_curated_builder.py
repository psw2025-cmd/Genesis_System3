"""
System3 Phase 373 - Clean Signal Curated Builder

Creates final curated signal files from deduplicated data.
Consolidates all data quality improvements into production-ready files.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import shutil
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_CLEAN = PROJECT_ROOT / "storage" / "live" / "clean"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

logger = logging.getLogger(__name__)


def run_phase373(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute Phase 373: Clean Signal Curated Builder."""
    logger.info("=== Phase 373: Clean Signal Curated Builder ===")

    result = {
        "phase": 373,
        "name": "Clean Signal Curated Builder",
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "curated_files": [],
        "outputs": {},
    }

    try:
        dedup_files = list(STORAGE_CLEAN.glob("*_dedup.csv"))

        for file_path in dedup_files:
            df = pd.read_csv(file_path, on_bad_lines="skip", low_memory=False)

            # Create curated version in main storage
            curated_name = file_path.name.replace("_clean_dedup", "_curated_final")
            curated_path = STORAGE_LIVE / curated_name

            df.to_csv(curated_path, index=False)

            result["curated_files"].append(
                {"source": file_path.name, "output": curated_name, "rows": len(df), "columns": len(df.columns)}
            )

            logger.info(f"Created curated file: {curated_name} ({len(df)} rows)")

        # Write outputs
        json_output = STORAGE_METRICS / "curated_build_373.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        result["outputs"]["json"] = str(json_output)

        md_output = REPORTS_DIR / "CURATED_BUILD_373.md"
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# Clean Signal Curated Build - Phase 373\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Curated Files Created:** {len(result['curated_files'])}\n\n")
            for cf in result["curated_files"]:
                f.write(f"- `{cf['output']}` ({cf['rows']} rows, {cf['columns']} cols)\n")

        result["outputs"]["report"] = str(md_output)
        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Phase 373 error: {e}", exc_info=True)
        return result


def main():
    """Standalone execution."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    result = run_phase373()
    print(f"\nPhase 373: {result['status'].upper()}")
    print(f"Created {len(result.get('curated_files', []))} curated file(s)")


if __name__ == "__main__":
    main()
