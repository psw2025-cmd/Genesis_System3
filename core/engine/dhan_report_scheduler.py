"""
Dhan Index Options - Report Auto-Scheduler

Schedules automatic report generation (read-only).
AUTO-UPDATE: DISABLED - Only schedules, never executes automatically.
"""

from datetime import datetime, time
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
SCHEDULER_CONFIG_JSON = CONFIG_DIR / "report_scheduler_config.json"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)


class ReportScheduler:
    """Report scheduler (read-only, no auto-execution)."""

    def __init__(self):
        self.auto_schedule_enabled = False  # ❌ DISABLED by default
        self.scheduled_reports = {
            "daily_learning_report": {"time": "18:00", "enabled": False},
            "weekly_summary": {"time": "18:00", "day": "friday", "enabled": False},
            "rolling_dashboard": {"time": "18:00", "enabled": False},
        }

    def get_schedule_status(self) -> Dict[str, Any]:
        """
        Get current schedule status (read-only).

        Returns:
            Dict with schedule information
        """
        return {
            "auto_schedule_enabled": self.auto_schedule_enabled,
            "scheduled_reports": self.scheduled_reports,
            "message": "Auto-scheduling is DISABLED. Reports must be generated manually via menu.",
        }

    def show_schedule(self) -> None:
        """Show current schedule (read-only)."""
        print("=== ANGEL ONE INDEX OPTIONS - REPORT SCHEDULER ===")
        print("[INFO] READ-ONLY MODE - No auto-execution\n")

        status = self.get_schedule_status()

        print(f"Auto-Schedule: {'✅ ENABLED' if status['auto_schedule_enabled'] else '❌ DISABLED'}")
        print("\n=== SCHEDULED REPORTS ===")

        for report_name, config in status["scheduled_reports"].items():
            enabled_icon = "✅" if config.get("enabled", False) else "❌"
            print(f"{enabled_icon} {report_name}:")
            print(f"   Time: {config.get('time', 'N/A')}")
            if "day" in config:
                print(f"   Day: {config.get('day', 'N/A')}")
            print(f"   Enabled: {config.get('enabled', False)}")

        print(f"\n{status['message']}")


def main() -> None:
    """Main entry point."""
    scheduler = ReportScheduler()
    scheduler.show_schedule()


if __name__ == "__main__":
    main()
