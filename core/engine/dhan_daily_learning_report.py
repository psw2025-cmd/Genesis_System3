"""
Dhan Index Options - End-of-Day Learning Report

Generates comprehensive daily learning report.
AUTO-UPDATE: DISABLED - Only reads and reports.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from core.engine.dhan_misfire_detector import detect_misfires
from core.engine.dhan_real_outcome_logger import get_outcome_summary, load_outcomes

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_daily_learning_report() -> Path:
    """
    Generate end-of-day learning report.

    Returns:
        Path to saved report
    """
    today = datetime.utcnow().strftime("%Y%m%d")
    report_path = REPORTS_DIR / f"dhan_daily_learning_report_{today}.txt"

    # Load data
    df_outcomes = load_outcomes()
    if df_outcomes.empty:
        with report_path.open("w", encoding="utf-8") as f:
            f.write("=== ANGEL ONE INDEX OPTIONS - DAILY LEARNING REPORT ===\n")
            f.write(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("No outcome data available for today.\n")
        return report_path

    # Filter to today
    if "timestamp" in df_outcomes.columns:
        df_outcomes["date"] = pd.to_datetime(df_outcomes["timestamp"], errors="coerce").dt.date
        today_date = datetime.utcnow().date()
        df_today = df_outcomes[df_outcomes["date"] == today_date]
    else:
        df_today = df_outcomes

    # Generate report
    with report_path.open("w", encoding="utf-8") as f:
        f.write("=== ANGEL ONE INDEX OPTIONS - DAILY LEARNING REPORT ===\n")
        f.write(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")

        # Summary
        f.write("=== SUMMARY ===\n")
        summary = get_outcome_summary()
        f.write(f"Total Trades: {summary['total_trades']}\n")
        f.write(f"Win Rate: {summary['win_rate']:.1f}%\n")
        f.write(f"Average PnL: {summary['avg_pnl']:.2f}%\n")
        f.write(f"Total PnL: {summary['total_pnl']:.2f}%\n\n")

        # Today's trades
        f.write("=== TODAY'S TRADES ===\n")
        if not df_today.empty:
            f.write(f"Trades Today: {len(df_today)}\n")
            if "pnl_pct" in df_today.columns:
                today_pnl = df_today["pnl_pct"].sum()
                today_win_rate = (df_today["pnl_pct"] > 0).sum() / len(df_today) * 100
                f.write(f"Today's PnL: {today_pnl:.2f}%\n")
                f.write(f"Today's Win Rate: {today_win_rate:.1f}%\n")
        else:
            f.write("No trades today.\n")
        f.write("\n")

        # Signal quality
        f.write("=== SIGNAL QUALITY ===\n")
        if "signal_confidence" in df_today.columns:
            avg_conf = df_today["signal_confidence"].mean()
            f.write(f"Average Confidence: {avg_conf:.3f}\n")
        if "score" in df_today.columns:
            avg_score = df_today["score"].abs().mean()
            f.write(f"Average Score: {avg_score:.3f}\n")
        f.write("\n")

        # Misfires
        f.write("=== MISFIRES ===\n")
        misfires = detect_misfires()
        if not misfires.empty:
            f.write(f"False Positives: {len(misfires[misfires['misfire_type'] == 'FALSE_POSITIVE'])}\n")
            f.write(f"False Negatives: {len(misfires[misfires['misfire_type'] == 'FALSE_NEGATIVE'])}\n")
        else:
            f.write("No misfires detected.\n")
        f.write("\n")

        # Regime
        f.write("=== MARKET REGIME ===\n")
        if "regime" in df_today.columns:
            regime_counts = df_today["regime"].value_counts()
            for regime, count in regime_counts.items():
                f.write(f"{regime}: {count} trades\n")
        f.write("\n")

        # Per underlying
        f.write("=== PER UNDERLYING ===\n")
        if "underlying" in df_today.columns:
            for underlying in df_today["underlying"].unique():
                df_u = df_today[df_today["underlying"] == underlying]
                f.write(f"\n{underlying}:\n")
                f.write(f"  Trades: {len(df_u)}\n")
                if "pnl_pct" in df_u.columns:
                    u_pnl = df_u["pnl_pct"].sum()
                    u_win_rate = (df_u["pnl_pct"] > 0).sum() / len(df_u) * 100 if len(df_u) > 0 else 0
                    f.write(f"  PnL: {u_pnl:.2f}%\n")
                    f.write(f"  Win Rate: {u_win_rate:.1f}%\n")

    return report_path


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - DAILY LEARNING REPORT ===")
    print("[INFO] AUTO-UPDATE: DISABLED - Report only\n")

    report_path = generate_daily_learning_report()
    print(f"[SAVE] Daily learning report saved to: {report_path}")

    # Print summary to console
    summary = get_outcome_summary()
    print(f"\n[SUMMARY] Total trades: {summary['total_trades']}")
    print(f"[SUMMARY] Win rate: {summary['win_rate']:.1f}%")
    print(f"[SUMMARY] Avg PnL: {summary['avg_pnl']:.2f}%")


if __name__ == "__main__":
    main()
