"""
Angel One Index Options - Intraday PnL Monitor

Monitors PnL of active trades in real-time during market hours.
Provides alerts and updates on trade performance.
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
EXEC_LOG_CSV = LIVE_DIR / "angel_index_ai_trades_exec_log.csv"
SIGNALS_CSV = LIVE_DIR / "angel_index_ai_signals.csv"


class IntradayPnLMonitor:
    """Monitors intraday PnL for active trades."""

    def __init__(self):
        self.exec_log_path = EXEC_LOG_CSV
        self.signals_path = SIGNALS_CSV

    def get_active_trades(self) -> pd.DataFrame:
        """Get all executed trades that haven't been closed."""
        if not self.exec_log_path.exists():
            return pd.DataFrame()

        try:
            df = pd.read_csv(self.exec_log_path)
            # Filter for DRY_RUN or LIVE mode (exclude closed)
            df = df[df.get("mode", "DRY_RUN") != "CLOSED"]
            return df
        except Exception:
            return pd.DataFrame()

    def compute_current_pnl(self, trade_row: pd.Series) -> dict:
        """
        Compute current PnL for a trade based on latest signal price.

        Returns dict with:
        - current_price: latest LTP
        - entry_price: entry price
        - pnl_pct: current PnL %
        - unrealized_pnl: unrealized PnL amount
        """
        if not self.signals_path.exists():
            return {
                "current_price": trade_row.get("entry_price", 0.0),
                "entry_price": trade_row.get("entry_price", 0.0),
                "pnl_pct": 0.0,
                "unrealized_pnl": 0.0,
                "status": "NO_DATA",
            }

        try:
            df_sig = pd.read_csv(self.signals_path)
            underlying = trade_row["underlying"]
            strike = float(trade_row["strike"])
            opt_type = trade_row["option_type"]

            # Find latest signal for this option
            mask = (df_sig["underlying"] == underlying) & (df_sig["strike"] == strike) & (df_sig["side"] == opt_type)
            latest = df_sig[mask].sort_values("ts").tail(1)

            if latest.empty:
                return {
                    "current_price": trade_row.get("entry_price", 0.0),
                    "entry_price": trade_row.get("entry_price", 0.0),
                    "pnl_pct": 0.0,
                    "unrealized_pnl": 0.0,
                    "status": "NO_SIGNAL",
                }

            current_price = float(latest.iloc[0]["ltp"])
            entry_price = float(trade_row.get("entry_price", 0.0))
            qty = int(trade_row.get("quantity", 1))

            if entry_price > 0:
                pnl_pct = ((current_price - entry_price) / entry_price) * 100.0
                unrealized_pnl = (current_price - entry_price) * qty
            else:
                pnl_pct = 0.0
                unrealized_pnl = 0.0

            return {
                "current_price": current_price,
                "entry_price": entry_price,
                "pnl_pct": pnl_pct,
                "unrealized_pnl": unrealized_pnl,
                "status": "ACTIVE",
            }
        except Exception as e:
            return {
                "current_price": trade_row.get("entry_price", 0.0),
                "entry_price": trade_row.get("entry_price", 0.0),
                "pnl_pct": 0.0,
                "unrealized_pnl": 0.0,
                "status": f"ERROR: {e}",
            }

    def monitor_all_trades(self) -> pd.DataFrame:
        """Monitor all active trades and return PnL summary."""
        active = self.get_active_trades()
        if active.empty:
            return pd.DataFrame()

        results = []
        for _, trade in active.iterrows():
            pnl_info = self.compute_current_pnl(trade)
            results.append(
                {
                    "trade_id": f"{trade['underlying']}_{trade['strike']}_{trade['option_type']}",
                    "underlying": trade["underlying"],
                    "strike": trade["strike"],
                    "option_type": trade["option_type"],
                    "entry_price": pnl_info["entry_price"],
                    "current_price": pnl_info["current_price"],
                    "pnl_pct": pnl_info["pnl_pct"],
                    "unrealized_pnl": pnl_info["unrealized_pnl"],
                    "status": pnl_info["status"],
                }
            )

        return pd.DataFrame(results)

    def print_monitor_summary(self) -> None:
        """Print intraday PnL monitor summary."""
        print("=== INTRADAY PnL MONITOR ===")
        df = self.monitor_all_trades()

        if df.empty:
            print("[MONITOR] No active trades.")
            return

        print(f"\nActive trades: {len(df)}")
        print("\n--- Per Trade ---")
        for _, row in df.iterrows():
            print(
                f"{row['underlying']} {row['strike']} {row['option_type']}: "
                f"Entry={row['entry_price']:.2f}, Current={row['current_price']:.2f}, "
                f"PnL={row['pnl_pct']:.2f}%"
            )

        # Summary
        total_pnl = df["unrealized_pnl"].sum()
        avg_pnl = df["pnl_pct"].mean()
        winning = (df["pnl_pct"] > 0).sum()
        losing = (df["pnl_pct"] < 0).sum()

        print("\n--- Summary ---")
        print(f"Total unrealized PnL: {total_pnl:.2f}")
        print(f"Average PnL %: {avg_pnl:.2f}%")
        print(f"Winning trades: {winning}, Losing trades: {losing}")


def main() -> None:
    """Main entry point for intraday PnL monitor."""
    monitor = IntradayPnLMonitor()
    monitor.print_monitor_summary()


if __name__ == "__main__":
    main()
