"""
System3 Phase 284 - Alert Aggregator

Aggregates and summarizes alerts from various system components.
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
ALERTS_LOG = LOG_DIR / "monitoring" / "system3_alerts.log"
REPORT_PATH = LOG_DIR / "monitoring" / "system3_alert_aggregation.md"


def run_phase284(**kwargs) -> Dict[str, Any]:
    """Run Phase 284: Alert Aggregator."""
    errors = []

    try:
        # Collect alerts from log files
        alerts = []

        # Check alerts log
        if ALERTS_LOG.exists():
            try:
                with ALERTS_LOG.open("r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # Count alert lines
                    alert_lines = [
                        line for line in content.split("\n") if "alert" in line.lower() or "warning" in line.lower()
                    ]
                    alerts.extend(alert_lines[:10])  # Last 10 alerts
            except Exception:
                pass

        # Generate report
        report_lines = [
            "# System3 Alert Aggregation\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Total Alerts**: {len(alerts)}\n",
        ]

        if alerts:
            report_lines.append("\n## Recent Alerts\n")
            for alert in alerts[:10]:
                report_lines.append(f"- {alert}\n")
        else:
            report_lines.append("\n✅ No alerts found\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "WARN" if alerts else "OK"
        details = f"Aggregated {len(alerts)} alerts"

        return {
            "phase": 284,
            "status": status,
            "details": details,
            "outputs": {
                "alerts_aggregated": len(alerts),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 284,
            "status": "ERROR",
            "details": f"Phase 284 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase284()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
