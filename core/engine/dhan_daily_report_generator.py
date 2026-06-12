"""
Dhan Index Options - Daily Auto-Report Generator

Generates comprehensive daily reports including:
- Signal statistics
- Trade execution summary
- PnL performance
- Risk metrics
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SIGNALS_CSV = LIVE_DIR / "dhan_index_ai_signals.csv"
TRADES_PLAN_CSV = LIVE_DIR / "dhan_index_ai_trades_plan.csv"
EXEC_LOG_CSV = LIVE_DIR / "dhan_index_ai_trades_exec_log.csv"
PNL_LOG_CSV = LIVE_DIR / "dhan_index_ai_pnl_log.csv"


class DailyReportGenerator:
    """Generates daily trading reports."""

    def __init__(self):
        self.reports_dir = REPORTS_DIR

    def generate_report(self, date: str | None = None) -> str:
        """
        Generate daily report for specified date (or today if None).

        Returns path to generated report file.
        """
        if date is None:
            date = datetime.utcnow().date().isoformat()

        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append(f"ANGEL ONE INDEX OPTIONS - DAILY REPORT")
        report_lines.append(f"Date: {date}")
        report_lines.append(f"Generated: {datetime.utcnow().isoformat()}")
        report_lines.append("=" * 80)
        report_lines.append("")

        # 1. Signal Statistics
        report_lines.append("## 1. SIGNAL STATISTICS")
        report_lines.append("-" * 80)
        signal_stats = self._get_signal_stats(date)
        report_lines.extend(signal_stats)
        report_lines.append("")

        # 2. Trade Execution Summary
        report_lines.append("## 2. TRADE EXECUTION SUMMARY")
        report_lines.append("-" * 80)
        exec_summary = self._get_execution_summary(date)
        report_lines.extend(exec_summary)
        report_lines.append("")

        # 3. PnL Performance
        report_lines.append("## 3. PnL PERFORMANCE")
        report_lines.append("-" * 80)
        pnl_summary = self._get_pnl_summary(date)
        report_lines.extend(pnl_summary)
        report_lines.append("")

        # 4. Risk Metrics
        report_lines.append("## 4. RISK METRICS")
        report_lines.append("-" * 80)
        risk_metrics = self._get_risk_metrics(date)
        report_lines.extend(risk_metrics)
        report_lines.append("")

        # 5. Recommendations
        report_lines.append("## 5. RECOMMENDATIONS")
        report_lines.append("-" * 80)
        recommendations = self._get_recommendations(date)
        report_lines.extend(recommendations)
        report_lines.append("")

        report_lines.append("=" * 80)

        # Save report
        report_text = "\n".join(report_lines)
        report_path = self.reports_dir / f"daily_report_{date}.txt"
        report_path.write_text(report_text, encoding="utf-8")

        return str(report_path)

    def _get_signal_stats(self, date: str) -> list[str]:
        """Get signal statistics for the day."""
        lines = []
        if not SIGNALS_CSV.exists():
            lines.append("No signal data available.")
            return lines

        try:
            df = pd.read_csv(SIGNALS_CSV)
            if "ts" in df.columns:
                df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
                df["date"] = df["ts"].dt.date.astype(str)
                df = df[df["date"] == date]

            if df.empty:
                lines.append("No signals for this date.")
                return lines

            total = len(df)
            buy_ce = (df.get("pred_label", "") == "BUY_CE").sum()
            buy_pe = (df.get("pred_label", "") == "BUY_PE").sum()
            hold = (df.get("pred_label", "") == "HOLD").sum()

            lines.append(f"Total signals: {total}")
            lines.append(f"BUY_CE: {buy_ce} ({buy_ce/total*100:.1f}%)")
            lines.append(f"BUY_PE: {buy_pe} ({buy_pe/total*100:.1f}%)")
            lines.append(f"HOLD: {hold} ({hold/total*100:.1f}%)")

            if "pred_confidence" in df.columns:
                avg_conf = df["pred_confidence"].mean()
                lines.append(f"Average confidence: {avg_conf:.3f}")
        except Exception as e:
            lines.append(f"Error computing signal stats: {e}")

        return lines

    def _get_execution_summary(self, date: str) -> list[str]:
        """Get trade execution summary for the day."""
        lines = []
        if not EXEC_LOG_CSV.exists():
            lines.append("No execution data available.")
            return lines

        try:
            df = pd.read_csv(EXEC_LOG_CSV)
            if "ts_exec" in df.columns:
                df["ts_exec"] = pd.to_datetime(df["ts_exec"], errors="coerce")
                df["date"] = df["ts_exec"].dt.date.astype(str)
                df = df[df["date"] == date]

            if df.empty:
                lines.append("No executions for this date.")
                return lines

            total = len(df)
            lines.append(f"Total executions: {total}")

            if "underlying" in df.columns:
                by_underlying = df.groupby("underlying").size()
                lines.append("\nBy underlying:")
                for u, count in by_underlying.items():
                    lines.append(f"  {u}: {count}")

            if "mode" in df.columns:
                dry_run = (df["mode"] == "DRY_RUN").sum()
                live = (df["mode"] == "LIVE").sum()
                lines.append(f"\nDRY RUN: {dry_run}, LIVE: {live}")
        except Exception as e:
            lines.append(f"Error computing execution summary: {e}")

        return lines

    def _get_pnl_summary(self, date: str) -> list[str]:
        """Get PnL summary for the day."""
        lines = []
        if not PNL_LOG_CSV.exists():
            lines.append("No PnL data available.")
            return lines

        try:
            df = pd.read_csv(PNL_LOG_CSV)
            pnl_col = "pnl_pct" if "pnl_pct" in df.columns else "pct_pnl"

            if pnl_col not in df.columns:
                lines.append("No PnL column found.")
                return lines

            # Filter by date if possible
            if "exit_ts" in df.columns:
                df["exit_ts"] = pd.to_datetime(df["exit_ts"], errors="coerce")
                df["date"] = df["exit_ts"].dt.date.astype(str)
                df = df[df["date"] == date]

            if df.empty:
                lines.append("No PnL data for this date.")
                return lines

            total_trades = len(df)
            total_pnl = df[pnl_col].sum()
            avg_pnl = df[pnl_col].mean()
            win_rate = (df[pnl_col] > 0).sum() / total_trades * 100 if total_trades > 0 else 0

            lines.append(f"Total trades: {total_trades}")
            lines.append(f"Total PnL: {total_pnl:.2f}%")
            lines.append(f"Average PnL: {avg_pnl:.2f}%")
            lines.append(f"Win rate: {win_rate:.1f}%")

            if "underlying" in df.columns:
                by_underlying = df.groupby("underlying")[pnl_col].agg(["count", "sum", "mean"])
                lines.append("\nBy underlying:")
                for u, row in by_underlying.iterrows():
                    lines.append(
                        f"  {u}: {int(row['count'])} trades, " f"Total={row['sum']:.2f}%, Avg={row['mean']:.2f}%"
                    )
        except Exception as e:
            lines.append(f"Error computing PnL summary: {e}")

        return lines

    def _get_risk_metrics(self, date: str) -> list[str]:
        """Get risk metrics for the day."""
        lines = []
        lines.append("Risk metrics:")
        lines.append("  - Max trades per day: 20 (configurable)")
        lines.append("  - Max trades per underlying: 5 (configurable)")
        lines.append("  - Current thresholds: Very conservative")
        lines.append("  - Auto-execution: DISABLED (DRY RUN only)")
        return lines

    def _get_recommendations(self, date: str) -> list[str]:
        """Get recommendations based on day's performance."""
        lines = []
        lines.append("Recommendations:")
        lines.append("  1. Review signal quality and model performance")
        lines.append("  2. Monitor trade execution success rate")
        lines.append("  3. Adjust thresholds based on PnL performance")
        lines.append("  4. Continue conservative mode until sufficient data collected")
        return lines


def main() -> None:
    """Main entry point for daily report generator."""
    print("=== ANGEL ONE INDEX OPTIONS - DAILY REPORT GENERATOR ===")
    generator = DailyReportGenerator()
    report_path = generator.generate_report()
    print(f"Daily report generated: {report_path}")
    print("\nReport preview:")
    print("-" * 80)
    with open(report_path, "r", encoding="utf-8") as f:
        print(f.read()[:2000])  # First 2000 chars
    print("-" * 80)


if __name__ == "__main__":
    main()
