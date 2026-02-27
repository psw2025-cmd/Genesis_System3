"""
Angel One Index Options - Daily Learning Digest

Daily report in /reports/real_learning_daily/
SAFE MODE ONLY - Read-only report generation.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from core.engine.angel_unified_outcome_logger_v3 import get_outcome_stats
from core.engine.angel_misfire_classifier_v2 import generate_misfire_report

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
DAILY_LEARNING_DIR = REPORTS_DIR / "real_learning_daily"

DAILY_LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def generate_daily_learning_digest() -> Path:
    """
    Generate daily learning digest report.

    Output: /reports/real_learning_daily/daily_digest_YYYYMMDD.txt

    Returns:
        Path to saved report
    """
    print("=== ANGEL ONE INDEX OPTIONS - DAILY LEARNING DIGEST ===")
    print("[INFO] SAFE MODE - Read-only report generation\n")

    today = datetime.utcnow().strftime("%Y%m%d")
    report_path = DAILY_LEARNING_DIR / f"daily_digest_{today}.txt"

    # Get outcome stats
    outcome_stats = get_outcome_stats()

    # Get misfire report
    misfire_report = generate_misfire_report()

    # Generate report
    with report_path.open("w", encoding="utf-8") as f:
        f.write("=== ANGEL ONE INDEX OPTIONS - DAILY LEARNING DIGEST ===\n")
        f.write(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")

        # Outcome Summary
        f.write("=== OUTCOME SUMMARY ===\n")
        if outcome_stats["status"] == "SUCCESS":
            f.write(f"Total Outcomes: {outcome_stats['total_outcomes']}\n")
            if "win_rate" in outcome_stats:
                f.write(f"Win Rate: {outcome_stats['win_rate']:.1f}%\n")
                f.write(f"Average PnL: {outcome_stats['avg_pnl']:.2f}%\n")
                f.write(f"Total PnL: {outcome_stats['total_pnl']:.2f}%\n")

            if "by_underlying" in outcome_stats:
                f.write("\nBy Underlying:\n")
                for u, data in outcome_stats["by_underlying"].items():
                    f.write(
                        f"  {u}: {data['count']} trades, win_rate={data['win_rate']:.1f}%, avg_pnl={data['avg_pnl']:.2f}%\n"
                    )
        else:
            f.write(f"{outcome_stats.get('message', 'No outcome data')}\n")

        # Misfire Summary
        f.write("\n=== MISFIRE SUMMARY ===\n")
        if misfire_report["status"] == "SUCCESS":
            f.write(f"Total Misfires: {misfire_report['total_misfires']}\n")
            f.write("\nBy Type:\n")
            for misfire_type, count in misfire_report["by_type"].items():
                f.write(f"  {misfire_type}: {count}\n")
            f.write("\nBy Severity:\n")
            for severity, count in misfire_report["by_severity"].items():
                f.write(f"  {severity}: {count}\n")
        else:
            f.write(f"{misfire_report.get('message', 'No misfires')}\n")

        # Key Insights
        f.write("\n=== KEY INSIGHTS ===\n")
        if outcome_stats["status"] == "SUCCESS" and "win_rate" in outcome_stats:
            win_rate = outcome_stats["win_rate"]
            if win_rate > 60:
                f.write("• Strong performance - high win rate\n")
            elif win_rate < 40:
                f.write("• Weak performance - low win rate, review signals\n")
            else:
                f.write("• Moderate performance - room for improvement\n")

        if misfire_report["status"] == "SUCCESS" and misfire_report["total_misfires"] > 0:
            f.write(f"• {misfire_report['total_misfires']} misfires detected - review classification\n")

        f.write("\n=== END OF DIGEST ===\n")

    # Print summary to console
    print(f"[GENERATED] Daily learning digest: {report_path}")

    if outcome_stats["status"] == "SUCCESS":
        print(f"\n[SUMMARY] Total outcomes: {outcome_stats['total_outcomes']}")
        if "win_rate" in outcome_stats:
            print(f"[SUMMARY] Win rate: {outcome_stats['win_rate']:.1f}%")

    if misfire_report["status"] == "SUCCESS":
        print(f"[SUMMARY] Total misfires: {misfire_report['total_misfires']}")

    return report_path


def main() -> None:
    """Main entry point."""
    report_path = generate_daily_learning_digest()
    print(f"\n[SUCCESS] Daily learning digest saved to: {report_path}")


if __name__ == "__main__":
    main()
