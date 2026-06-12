"""
Dhan Index Options - Weekly Summary Report

Generates weekly summary report (read-only).
AUTO-UPDATE: DISABLED - Only reads and reports.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

from core.engine.dhan_real_outcome_logger import load_outcomes

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_weekly_summary(days: int = 7) -> Path:
    """
    Generate weekly summary report.

    Args:
        days: Number of days to include (default: 7)

    Returns:
        Path to saved report
    """
    df = load_outcomes()
    if df.empty:
        report_path = REPORTS_DIR / f"weekly_summary_{datetime.utcnow().strftime('%Y%m%d')}.txt"
        with report_path.open("w", encoding="utf-8") as f:
            f.write("=== ANGEL ONE INDEX OPTIONS - WEEKLY SUMMARY ===\n")
            f.write(f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("No outcome data available.\n")
        return report_path

    # Filter to last N days
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        cutoff = datetime.utcnow() - timedelta(days=days)
        df = df[df["timestamp"] >= cutoff]

    report_path = REPORTS_DIR / f"weekly_summary_{datetime.utcnow().strftime('%Y%m%d')}.txt"

    with report_path.open("w", encoding="utf-8") as f:
        f.write("=== ANGEL ONE INDEX OPTIONS - WEEKLY SUMMARY ===\n")
        f.write(f"Period: Last {days} days\n")
        f.write(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")

        if df.empty:
            f.write("No trades in this period.\n")
            return report_path

        # Overall stats
        f.write("=== OVERALL STATISTICS ===\n")
        total_trades = len(df)
        if "pnl_pct" in df.columns:
            win_rate = (df["pnl_pct"] > 0).sum() / total_trades * 100 if total_trades > 0 else 0.0
            avg_pnl = df["pnl_pct"].mean()
            total_pnl = df["pnl_pct"].sum()
            max_win = df["pnl_pct"].max()
            max_loss = df["pnl_pct"].min()

            f.write(f"Total Trades: {total_trades}\n")
            f.write(f"Win Rate: {win_rate:.1f}%\n")
            f.write(f"Average PnL: {avg_pnl:.2f}%\n")
            f.write(f"Total PnL: {total_pnl:.2f}%\n")
            f.write(f"Best Trade: {max_win:.2f}%\n")
            f.write(f"Worst Trade: {max_loss:.2f}%\n\n")

        # Per underlying
        if "underlying" in df.columns:
            f.write("=== PER UNDERLYING ===\n")
            for underlying in df["underlying"].unique():
                df_u = df[df["underlying"] == underlying]
                f.write(f"\n{underlying}:\n")
                f.write(f"  Trades: {len(df_u)}\n")
                if "pnl_pct" in df_u.columns:
                    u_pnl = df_u["pnl_pct"].sum()
                    u_win_rate = (df_u["pnl_pct"] > 0).sum() / len(df_u) * 100 if len(df_u) > 0 else 0.0
                    f.write(f"  PnL: {u_pnl:.2f}%\n")
                    f.write(f"  Win Rate: {u_win_rate:.1f}%\n")

        # Daily breakdown
        if "timestamp" in df.columns:
            f.write("\n=== DAILY BREAKDOWN ===\n")
            df["date"] = df["timestamp"].dt.date
            daily_stats = (
                df.groupby("date")
                .agg(
                    {
                        "pnl_pct": ["sum", "count"] if "pnl_pct" in df.columns else ["count"],
                    }
                )
                .reset_index()
            )
            daily_stats.columns = ["date", "pnl", "trades"] if "pnl_pct" in df.columns else ["date", "trades"]
            for _, row in daily_stats.iterrows():
                if "pnl_pct" in df.columns:
                    f.write(f"{row['date']}: {row['trades']} trades, PnL: {row['pnl']:.2f}%\n")
                else:
                    f.write(f"{row['date']}: {row['trades']} trades\n")

    return report_path


def main() -> None:
    """Main entry point."""
    print("=== ANGEL ONE INDEX OPTIONS - WEEKLY SUMMARY REPORT ===")
    print("[INFO] READ-ONLY MODE - No auto-updates\n")

    report_path = generate_weekly_summary(days=7)
    print(f"[SAVE] Weekly summary saved to: {report_path}")


if __name__ == "__main__":
    main()
