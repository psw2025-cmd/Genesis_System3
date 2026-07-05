"""
System3 Phase 314 - Data Lineage Tracker

Tracks origin and lineage of key live and training data files.
"""

import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Output directory
HEALTH_DIR = PROJECT_ROOT / "storage" / "system_health"
HEALTH_DIR.mkdir(parents=True, exist_ok=True)

LINEAGE_LOG = HEALTH_DIR / "data_lineage_log.jsonl"

# Key files to track
KEY_FILES = [
    "storage/live/dhan_index_ai_signals.csv",
    "storage/live/dhan_index_ai_signals_curated.csv",
    "storage/live/dhan_index_ai_signals_with_forward.csv",
    "storage/live/dhan_index_ai_pnl_log.csv",
]


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file."""
    if not file_path.exists():
        return ""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        return ""


def count_rows(file_path: Path) -> int:
    """Count rows in CSV file."""
    if not file_path.exists():
        return 0
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for line in f) - 1  # Subtract header
    except:
        return 0


def track_file_lineage(
    file_path: str, producer_phase: int, producer_script: str, input_files: List[str] = None, mode: str = "unknown"
) -> None:
    """
    Track lineage of a data file.

    Args:
        file_path: Relative path to file
        producer_phase: Phase number that produced this file
        producer_script: Script name that produced this file
        input_files: List of input files used
        mode: pre_market, live, eod, etc.
    """
    full_path = PROJECT_ROOT / file_path

    record = {
        "timestamp": datetime.now().isoformat(),
        "file_path": file_path,
        "producer_phase": producer_phase,
        "producer_script": producer_script,
        "input_files": input_files or [],
        "row_count": count_rows(full_path),
        "sha256": compute_file_hash(full_path),
        "mode": mode,
    }

    try:
        with open(LINEAGE_LOG, "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        logger.warning(f"Failed to write lineage record: {e}")


def run_phase314(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 314: Data Lineage Tracker

    Returns:
        dict: {
            "phase": 314,
            "status": "OK" | "WARN" | "ERROR",
            "details": "description of execution",
            "outputs": {"lineage_log": path, "files_tracked": N},
            "errors": []
        }
    """
    errors = []
    outputs = {}

    try:
        logger.info("Phase 314: Data lineage tracker initialized")

        # Track current state of key files
        tracked_count = 0
        for file_path in KEY_FILES:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                track_file_lineage(
                    file_path=file_path,
                    producer_phase=314,
                    producer_script="system3_phase314_data_lineage_tracker.py",
                    input_files=[],
                    mode="snapshot",
                )
                tracked_count += 1

        # Create daily summary
        today = datetime.now().strftime("%Y%m%d")
        summary_file = PROJECT_ROOT / f"SYSTEM3_DATA_LINEAGE_DAILY_SUMMARY.md"

        # Read recent lineage records
        recent_records = []
        if LINEAGE_LOG.exists():
            try:
                with open(LINEAGE_LOG, "r") as f:
                    lines = f.readlines()
                    # Get last 100 records
                    for line in lines[-100:]:
                        try:
                            recent_records.append(json.loads(line))
                        except:
                            pass
            except:
                pass

        # Create summary
        summary_lines = [
            "# System3 Data Lineage Daily Summary",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Total Records:** {len(recent_records)}",
            "",
            "## Recent File Updates",
            "",
        ]

        for record in recent_records[-20:]:  # Last 20
            summary_lines.append(
                f"- {record['timestamp']}: `{record['file_path']}` "
                f"(Phase {record['producer_phase']}, {record['row_count']} rows)"
            )

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("\n".join(summary_lines))

        outputs = {
            "lineage_log": str(LINEAGE_LOG),
            "files_tracked": tracked_count,
            "summary_file": str(summary_file),
            "total_records": len(recent_records),
        }

        return {
            "phase": 314,
            "status": "OK",
            "details": f"Data lineage tracker active: {tracked_count} files tracked",
            "outputs": outputs,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Phase 314 error: {e}")
        return {
            "phase": 314,
            "status": "ERROR",
            "details": f"Phase 314 failed: {str(e)}",
            "outputs": outputs,
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase314()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
