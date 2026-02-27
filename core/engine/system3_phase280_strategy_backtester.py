"""
System3 Phase 280 - Strategy Backtester

Backtests trading strategies on historical data.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
SIGNALS_CSV = STORAGE_LIVE / "angel_index_ai_signals_with_forward.csv"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_strategy_backtest.md"


def run_phase280(**kwargs) -> Dict[str, Any]:
    """Run Phase 280: Strategy Backtester."""
    errors = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 280,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"backtest_pnl": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        try:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {
                "phase": 280,
                "status": "WARN",
                "details": f"Error loading CSV: {e}",
                "outputs": {"backtest_pnl": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [str(e)],
            }

        if df.empty:
            return {
                "phase": 280,
                "status": "WARN",
                "details": "No data to backtest",
                "outputs": {"backtest_pnl": 0.0, "report_file": str(REPORT_PATH)},
                "errors": [],
            }

        # Simple backtest: simulate trades based on signals
        backtest_pnl = 0.0
        trades_taken = 0

        if "pred_label" in df.columns and "forward_return_1" in df.columns:
            # Simulate BUY signals
            buy_signals = df[df["pred_label"] == "BUY"]
            if len(buy_signals) > 0:
                backtest_pnl += buy_signals["forward_return_1"].sum()
                trades_taken += len(buy_signals)

            # Simulate SELL signals (inverse)
            sell_signals = df[df["pred_label"] == "SELL"]
            if len(sell_signals) > 0:
                backtest_pnl -= sell_signals["forward_return_1"].sum()
                trades_taken += len(sell_signals)

        # Generate report
        report_lines = [
            "# System3 Strategy Backtest\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Total PnL**: {backtest_pnl:.2f}\n",
            f"**Trades Taken**: {trades_taken}\n",
        ]

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK"
        details = f"Backtest PnL: {backtest_pnl:.2f} ({trades_taken} trades)"

        return {
            "phase": 280,
            "status": status,
            "details": details,
            "outputs": {
                "backtest_pnl": float(backtest_pnl),
                "trades_taken": trades_taken,
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 280,
            "status": "ERROR",
            "details": f"Phase 280 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase280()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
