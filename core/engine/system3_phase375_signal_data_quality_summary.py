"""
System3 Phase 375 - Signal Data Quality Summary

Comprehensive summary of all data quality phases (370-374).
Reports before/after metrics and quality improvements.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

logger = logging.getLogger(__name__)


def load_phase_results(phase_num: int) -> Dict[str, Any]:
    """Load results from a previous phase."""
    metrics_files = {
        370: "schema_normalization_370.json",
        371: "duplicate_scan_371.json",
        372: "conflict_resolution_372.json",
        373: "curated_build_373.json",
        374: "freshness_check_374.json",
    }

    file_path = STORAGE_METRICS / metrics_files.get(phase_num, "")

    if not file_path.exists():
        return {"status": "not_run"}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_phase375(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute Phase 375: Signal Data Quality Summary."""
    logger.info("=== Phase 375: Signal Data Quality Summary ===")

    result = {
        "phase": 375,
        "name": "Signal Data Quality Summary",
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "phase_results": {},
        "quality_score": 0,
        "outputs": {},
    }

    try:
        # Load results from phases 370-374
        for phase_num in [370, 371, 372, 373, 374]:
            result["phase_results"][f"phase_{phase_num}"] = load_phase_results(phase_num)

        # Calculate quality score
        score = 100

        phase_370 = result["phase_results"].get("phase_370", {})
        if phase_370.get("status") == "warn":
            score -= 20

        phase_374 = result["phase_results"].get("phase_374", {})
        stale_count = phase_374.get("stale_count", 0)
        if stale_count > 0:
            score -= stale_count * 10

        result["quality_score"] = max(0, score)

        if result["quality_score"] < 70:
            result["status"] = "warn"

        # Write outputs
        json_output = STORAGE_METRICS / "data_quality_summary_375.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        result["outputs"]["json"] = str(json_output)

        md_output = REPORTS_DIR / "DATA_QUALITY_SUMMARY_375.md"
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# Signal Data Quality Summary - Phase 375\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Quality Score: {result['quality_score']}/100\n\n")
            f.write("---\n\n")
            f.write("## Phase Results\n\n")

            for phase_key, phase_data in result["phase_results"].items():
                phase_num = phase_key.split("_")[1]
                status = phase_data.get("status", "unknown")
                status_emoji = "✅" if status == "ok" else ("⚠️" if status == "warn" else "❌")
                f.write(f"{status_emoji} **Phase {phase_num}**: {status}\n")

            f.write("\n---\n\n")
            f.write("## Recommendations\n\n")

            if result["quality_score"] >= 80:
                f.write("✅ Data quality is excellent. Proceed with model training.\n")
            elif result["quality_score"] >= 60:
                f.write("⚠️ Data quality is acceptable but has issues. Review warnings.\n")
            else:
                f.write("❌ Data quality is poor. Address critical issues before training.\n")

        result["outputs"]["report"] = str(md_output)
        logger.info(f"Phase 375 complete: quality_score={result['quality_score']}")
        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Phase 375 error: {e}", exc_info=True)
        return result


def main():
    """Standalone execution."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    result = run_phase375()
    print(f"\nPhase 375: {result['status'].upper()}")
    print(f"Quality Score: {result['quality_score']}/100")


if __name__ == "__main__":
    main()
