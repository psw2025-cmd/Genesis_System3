"""
Angel One Index Options - Daily Auto-Reports Generator

Generates automated daily reports (read-only).
AUTO-UPDATE: DISABLED - Only reads and reports.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

from core.engine.angel_real_outcome_logger import load_outcomes, get_outcome_summary
from core.engine.angel_daily_learning_report import generate_daily_learning_report
from core.engine.angel_rolling_learning_dashboard import generate_rolling_dashboard

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_daily_auto_report() -> Dict[str, Any]:
    """
    Generate comprehensive daily auto-report (read-only).

    Returns:
        Dict with report paths and summary
    """
    print("=== ANGEL ONE INDEX OPTIONS - DAILY AUTO-REPORTS ===")
    print("[INFO] READ-ONLY MODE - No auto-updates\n")

    reports_generated = []

    # 1. Daily Learning Report
    try:
        daily_report_path = generate_daily_learning_report()
        reports_generated.append(
            {
                "type": "daily_learning",
                "path": str(daily_report_path),
                "status": "SUCCESS",
            }
        )
        print(f"[GENERATED] Daily learning report: {daily_report_path}")
    except Exception as e:
        reports_generated.append(
            {
                "type": "daily_learning",
                "path": None,
                "status": "ERROR",
                "error": str(e),
            }
        )
        print(f"[ERROR] Daily learning report failed: {e}")

    # 2. Rolling 7-Day Dashboard
    try:
        dashboard = generate_rolling_dashboard(days=7)
        if dashboard["status"] == "SUCCESS":
            from core.engine.angel_rolling_learning_dashboard import save_dashboard_csv

            dashboard_path = save_dashboard_csv(dashboard)
            reports_generated.append(
                {
                    "type": "rolling_dashboard",
                    "path": str(dashboard_path),
                    "status": "SUCCESS",
                }
            )
            print(f"[GENERATED] Rolling dashboard: {dashboard_path}")
        else:
            reports_generated.append(
                {
                    "type": "rolling_dashboard",
                    "path": None,
                    "status": "NO_DATA",
                    "message": dashboard.get("message", "No data available"),
                }
            )
    except Exception as e:
        reports_generated.append(
            {
                "type": "rolling_dashboard",
                "path": None,
                "status": "ERROR",
                "error": str(e),
            }
        )
        print(f"[ERROR] Rolling dashboard failed: {e}")

    # 3. Quick Summary Report
    try:
        summary_path = _generate_quick_summary()
        reports_generated.append(
            {
                "type": "quick_summary",
                "path": str(summary_path),
                "status": "SUCCESS",
            }
        )
        print(f"[GENERATED] Quick summary: {summary_path}")
    except Exception as e:
        reports_generated.append(
            {
                "type": "quick_summary",
                "path": None,
                "status": "ERROR",
                "error": str(e),
            }
        )

    return {
        "status": "SUCCESS",
        "reports": reports_generated,
        "generated_at": datetime.utcnow().isoformat(),
    }


def _generate_quick_summary() -> Path:
    """Generate quick summary report."""
    today = datetime.utcnow().strftime("%Y%m%d")
    summary_path = REPORTS_DIR / f"daily_quick_summary_{today}.txt"

    summary = get_outcome_summary()

    with summary_path.open("w", encoding="utf-8") as f:
        f.write("=== ANGEL ONE INDEX OPTIONS - QUICK SUMMARY ===\n")
        f.write(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
        f.write(f"Total Trades: {summary['total_trades']}\n")
        f.write(f"Win Rate: {summary['win_rate']:.1f}%\n")
        f.write(f"Average PnL: {summary['avg_pnl']:.2f}%\n")
        f.write(f"Total PnL: {summary['total_pnl']:.2f}%\n")

    return summary_path


def schedule_daily_reports() -> Dict[str, Any]:
    """
    Schedule daily reports (read-only check).

    Returns:
        Dict with scheduling info
    """
    # This is a placeholder for future scheduling
    # Currently, reports are generated on-demand via menu

    return {
        "status": "MANUAL",
        "message": "Daily reports are generated manually via menu option 40.",
        "auto_schedule": False,  # ❌ DISABLED
    }


def main() -> None:
    """Main entry point."""
    result = generate_daily_auto_report()

    if result["status"] == "SUCCESS":
        print(f"\n[SUCCESS] Generated {len(result['reports'])} reports")
        print(f"[INFO] All reports are READ-ONLY. No auto-updates performed.")
    else:
        print(f"[ERROR] Report generation failed")


if __name__ == "__main__":
    main()
