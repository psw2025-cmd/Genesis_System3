"""
System3 Phase 287 - Resource Usage Monitor

Monitors system resource usage: CPU, memory, disk, file sizes.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import psutil

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "monitoring"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_resource_usage.md"


def run_phase287(**kwargs) -> Dict[str, Any]:
    """Run Phase 287: Resource Usage Monitor."""
    errors = []

    try:
        # Monitor system resources
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(PROJECT_ROOT))

        # Calculate log directory size
        log_size = 0
        logs_dir = PROJECT_ROOT / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.rglob("*.log"):
                try:
                    log_size += log_file.stat().st_size
                except Exception:
                    pass

        # Generate report
        report_lines = [
            "# System3 Resource Usage Monitor\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**CPU Usage**: {cpu_percent:.1f}%\n",
            f"**Memory Usage**: {memory.percent:.1f}%\n",
            f"**Disk Usage**: {disk.percent:.1f}%\n",
            f"**Log Directory Size**: {log_size / (1024*1024):.2f} MB\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"CPU: {cpu_percent:.1f}%, Memory: {memory.percent:.1f}%"

        return {
            "phase": 287,
            "status": status,
            "details": details,
            "outputs": {
                "cpu_percent": float(cpu_percent),
                "memory_percent": float(memory.percent),
                "disk_percent": float(disk.percent),
                "log_size_mb": float(log_size / (1024 * 1024)),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except ImportError:
        # psutil not available
        return {
            "phase": 287,
            "status": "WARN",
            "details": "psutil not available, skipping resource monitoring",
            "outputs": {"report_file": str(REPORT_PATH)},
            "errors": [],
        }
    except Exception as e:
        return {
            "phase": 287,
            "status": "ERROR",
            "details": f"Phase 287 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase287()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
