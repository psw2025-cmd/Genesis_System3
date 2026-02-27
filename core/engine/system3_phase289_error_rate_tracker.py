"""
System3 Phase 289 - Error Rate Tracker

Tracks error rates across system components.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import re

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs"

REPORT_PATH = LOG_DIR / "monitoring" / "system3_error_rate_tracker.md"


def run_phase289(**kwargs) -> Dict[str, Any]:
    """Run Phase 289: Error Rate Tracker."""
    errors = []

    try:
        # Scan log files for errors
        error_count = 0
        error_types = {}

        if LOG_DIR.exists():
            for log_file in LOG_DIR.rglob("*.log"):
                try:
                    with log_file.open("r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        # Count error patterns
                        error_matches = re.findall(r"(?i)(error|exception|failed|traceback)", content)
                        error_count += len(error_matches)

                        # Categorize errors
                        if "ERROR" in content.upper():
                            error_types["ERROR"] = error_types.get("ERROR", 0) + content.upper().count("ERROR")
                        if "EXCEPTION" in content.upper():
                            error_types["EXCEPTION"] = error_types.get("EXCEPTION", 0) + content.upper().count(
                                "EXCEPTION"
                            )
                except Exception:
                    pass

        # Calculate error rate (simplified)
        error_rate = error_count / 1000.0 if error_count > 0 else 0.0  # Normalized

        # Generate report
        report_lines = [
            "# System3 Error Rate Tracker\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Total Errors Found**: {error_count}\n",
            f"**Error Rate**: {error_rate:.4f}\n",
        ]

        if error_types:
            report_lines.append("\n## Error Types\n")
            for err_type, count in error_types.items():
                report_lines.append(f"- {err_type}: {count}\n")

        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "WARN" if error_count > 10 else "OK"
        details = f"Tracked {error_count} errors (rate: {error_rate:.4f})"

        return {
            "phase": 289,
            "status": status,
            "details": details,
            "outputs": {
                "error_count": error_count,
                "error_rate": float(error_rate),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 289,
            "status": "ERROR",
            "details": f"Phase 289 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase289()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
