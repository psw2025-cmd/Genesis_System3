"""
System3 Phase 374 - Signal History Freshness Checker

Monitors data freshness and triggers warnings for stale files.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

logger = logging.getLogger(__name__)

FRESHNESS_THRESHOLD_HOURS = 24


def run_phase374(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute Phase 374: Signal History Freshness Checker."""
    logger.info("=== Phase 374: Signal History Freshness Checker ===")

    result = {
        "phase": 374,
        "name": "Signal History Freshness Checker",
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "freshness_results": [],
        "stale_count": 0,
        "outputs": {},
    }

    try:
        target_files = [
            "dhan_index_ai_signals.csv",
            "dhan_index_ai_signals_curated.csv",
            "dhan_index_ai_signals_with_forward.csv",
        ]

        for filename in target_files:
            file_path = STORAGE_LIVE / filename

            if not file_path.exists():
                result["freshness_results"].append({"file": filename, "status": "missing"})
                continue

            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            age_hours = (datetime.now() - mod_time).total_seconds() / 3600
            is_stale = age_hours > FRESHNESS_THRESHOLD_HOURS

            if is_stale:
                result["stale_count"] += 1

            result["freshness_results"].append(
                {
                    "file": filename,
                    "status": "stale" if is_stale else "fresh",
                    "age_hours": round(age_hours, 2),
                    "last_modified": mod_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        if result["stale_count"] > 0:
            result["status"] = "warn"

        # Write outputs
        json_output = STORAGE_METRICS / "freshness_check_374.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        result["outputs"]["json"] = str(json_output)

        md_output = REPORTS_DIR / "FRESHNESS_CHECK_374.md"
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# Signal Freshness Check - Phase 374\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Stale Files:** {result['stale_count']}\n\n")
            for fr in result["freshness_results"]:
                status_emoji = "✅" if fr["status"] == "fresh" else "⚠️"
                f.write(f"{status_emoji} **{fr['file']}**: {fr['status']} ({fr.get('age_hours', 'N/A')}h)\n")

        result["outputs"]["report"] = str(md_output)
        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Phase 374 error: {e}", exc_info=True)
        return result


def main():
    """Standalone execution."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    result = run_phase374()
    print(f"\nPhase 374: {result['status'].upper()}")
    print(f"Stale files: {result['stale_count']}")


if __name__ == "__main__":
    main()
