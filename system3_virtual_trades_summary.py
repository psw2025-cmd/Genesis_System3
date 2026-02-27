"""
System3 Phase 240 - Virtual PnL Daily Report

Produce daily PnL summaries by underlying and overall.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
INPUT_CSV = STORAGE_LIVE / "angel_virtual_orders_with_pnl.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_virtual_trades_pnl_report.md"


def run_phase240() -> dict:
    """Run Phase 240: Virtual PnL Daily Report."""
    if not INPUT_CSV.exists():
        report = f"""# System3 Virtual Trades PnL Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Status

⚠️ **No virtual trades available** (file not found: `{INPUT_CSV}`)

This is expected if no virtual trades have been enriched yet.
"""
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write(report)
        return {
            "phase": 240,
            "status": "WARN",
            "details": "No virtual trades available",
            "outputs": {},
            "errors": []
        }
    
    try:
        df = pd.read_csv(INPUT_CSV, engine="python", on_bad_lines="skip")
        
        if df.empty:
            report = f"""# System3 Virtual Trades PnL Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Status

⚠️ **No virtual trades available** (file is empty)
"""
            with REPORT_PATH.open("w", encoding="utf-8") as f:
                f.write(report)
            return {
                "phase": 240,
                "status": "WARN",
                "details": "File is empty",
                "outputs": {},
                "errors": []
            }
        
        # Find PnL column (prefer pnl_1)
        pnl_col = None
        for col in ["pnl_1", "pnl_3", "pnl_5"]:
            if col in df.columns:
                pnl_col = col
                break
        
        if pnl_col is None:
            pnl_col = [c for c in df.columns if "pnl" in c.lower()][0] if any("pnl" in c.lower() for c in df.columns) else None
        
        if pnl_col is None:
            return {
                "phase": 240,
                "status": "WARN",
                "details": "No PnL column found",
                "outputs": {},
                "errors": []
            }
        
        # Parse dates
        if "ts" in df.columns:
            df["date"] = pd.to_datetime(df["ts"], errors="coerce").dt.date
        
        # Overall summary
        total_trades = len(df)
        wins = len(df[df[pnl_col] > 0]) if pnl_col else 0
        losses = len(df[df[pnl_col] < 0]) if pnl_col else 0
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        total_pnl = df[pnl_col].sum() if pnl_col else 0
        avg_pnl = df[pnl_col].mean() if pnl_col else 0
        
        # Per-day summary
        daily_summary = []
        if "date" in df.columns:
            for date, group in df.groupby("date"):
                daily_trades = len(group)
                daily_wins = len(group[group[pnl_col] > 0]) if pnl_col else 0
                daily_losses = len(group[group[pnl_col] < 0]) if pnl_col else 0
                daily_win_rate = (daily_wins / daily_trades * 100) if daily_trades > 0 else 0
                daily_pnl = group[pnl_col].sum() if pnl_col else 0
                daily_summary.append({
                    "date": date,
                    "trades": daily_trades,
                    "wins": daily_wins,
                    "losses": daily_losses,
                    "win_rate": daily_win_rate,
                    "total_pnl": daily_pnl
                })
        
        # Per-underlying summary
        underlying_summary = []
        if "underlying" in df.columns:
            for underlying, group in df.groupby("underlying"):
                und_trades = len(group)
                und_wins = len(group[group[pnl_col] > 0]) if pnl_col else 0
                und_losses = len(group[group[pnl_col] < 0]) if pnl_col else 0
                und_win_rate = (und_wins / und_trades * 100) if und_trades > 0 else 0
                und_pnl = group[pnl_col].sum() if pnl_col else 0
                underlying_summary.append({
                    "underlying": underlying,
                    "trades": und_trades,
                    "wins": und_wins,
                    "losses": und_losses,
                    "win_rate": und_win_rate,
                    "total_pnl": und_pnl
                })
        
        # Generate report
        report_lines = [
            "# System3 Virtual Trades PnL Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**PnL Column Used**: {pnl_col}\n",
            "\n## Overall Summary\n",
            f"| Metric | Value |\n",
            f"|--------|-------|\n",
            f"| Total Trades | {total_trades} |\n",
            f"| Wins | {wins} |\n",
            f"| Losses | {losses} |\n",
            f"| Win Rate | {win_rate:.2f}% |\n",
            f"| Total PnL | {total_pnl:.2f} |\n",
            f"| Avg PnL | {avg_pnl:.2f} |\n",
        ]
        
        if daily_summary:
            report_lines.extend([
                "\n## Per-Day Summary\n",
                "| Date | Trades | Wins | Losses | Win Rate | Total PnL |\n",
                "|------|--------|------|--------|----------|-----------|\n"
            ])
            for day in daily_summary:
                report_lines.append(
                    f"| {day['date']} | {day['trades']} | {day['wins']} | {day['losses']} | "
                    f"{day['win_rate']:.2f}% | {day['total_pnl']:.2f} |\n"
                )
        
        if underlying_summary:
            report_lines.extend([
                "\n## Per-Underlying Summary\n",
                "| Underlying | Trades | Wins | Losses | Win Rate | Total PnL |\n",
                "|------------|--------|------|--------|----------|-----------|\n"
            ])
            for und in underlying_summary:
                report_lines.append(
                    f"| {und['underlying']} | {und['trades']} | {und['wins']} | {und['losses']} | "
                    f"{und['win_rate']:.2f}% | {und['total_pnl']:.2f} |\n"
                )
        
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)
        
        return {
            "phase": 240,
            "status": "OK",
            "details": f"Generated report: {total_trades} trades, {win_rate:.1f}% win rate",
            "outputs": {
                "total_trades": total_trades,
                "win_rate": win_rate,
                "report_file": str(REPORT_PATH)
            },
            "errors": []
        }
        
    except Exception as e:
        error_msg = f"Error generating report: {e}"
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write(f"# System3 Virtual Trades PnL Report\n\n**ERROR**: {error_msg}\n")
        return {
            "phase": 240,
            "status": "ERROR",
            "details": error_msg,
            "outputs": {},
            "errors": [error_msg]
        }


if __name__ == "__main__":
    result = run_phase240()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")

