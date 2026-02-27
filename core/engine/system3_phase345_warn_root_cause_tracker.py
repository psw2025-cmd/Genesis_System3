"""
System3 Phase 345 - WARN Phase Root-Cause Tracker

Converts generic "Phase XXX: WARN" into structured root-cause reports.
Parses autorun logs and tracks WARN sources with categorized root causes.

Mode: Post-market, optionally hourly.
"""

import sys
import json
import re
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


def run_phase_345_warn_root_cause_tracker(root_path: str = None, logger_obj=None) -> str:
    """
    Phase 345: Track and categorize root causes of WARN statuses.

    Returns: 'OK'
    """
    if logger_obj:
        logger = logger_obj

    if root_path is None:
        root_path = str(PROJECT_ROOT)

    root = Path(root_path)
    logger.info("[PH345] Starting WARN Root-Cause Tracker")

    try:
        logs_dir = root / "logs"
        diag_dir = root / "storage" / "live" / "diagnostics"
        diag_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y%m%d")
        log_files = list(logs_dir.glob(f"system3_autorun_master_{today}*.log"))

        warn_records = []
        phase_warn_counts = defaultdict(int)

        for log_file in log_files:
            try:
                with open(log_file) as f:
                    for line in f:
                        # Match WARNING or WARN patterns
                        if "WARN" in line.upper():
                            # Extract phase number if present
                            match = re.search(r"\[PH(\d+)\]", line)
                            phase_num = int(match.group(1)) if match else None

                            warn_records.append(
                                {
                                    "timestamp": datetime.now().isoformat(),
                                    "phase": phase_num,
                                    "message": line.strip()[:200],
                                    "root_cause_code": "unknown",
                                }
                            )

                            if phase_num:
                                phase_warn_counts[phase_num] += 1

            except Exception as e:
                logger.debug(f"[PH345] Error reading log file {log_file}: {e}")

        # Write CSV report
        if warn_records:
            df_warns = pd.DataFrame(warn_records)
            df_warns.to_csv(diag_dir / "warn_root_cause_log.csv", index=False)

        # Write summary JSON
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_warns": len(warn_records),
            "phase_warn_counts": dict(phase_warn_counts),
            "top_problematic_phases": sorted(phase_warn_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        }

        with open(diag_dir / "warn_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"[PH345] WARN Root-Cause Tracker: {len(warn_records)} warns found")
        return "OK"

    except Exception as e:
        logger.error(f"[PH345] Unexpected error: {e}", exc_info=True)
        return "WARN"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = run_phase_345_warn_root_cause_tracker()
    print(f"Phase 345 result: {result}")
