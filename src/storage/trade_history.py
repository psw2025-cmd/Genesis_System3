"""
Trade History Storage - Stores all paper trades
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger


class TradeHistoryStore:
    """
    Stores trade history to CSV and JSON.
    """

    def __init__(self):
        """Initialize trade history store."""
        self.output_dir = ROOT_DIR / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.trades_csv = self.output_dir / "paper_trades_live.csv"
        self.positions_json = self.output_dir / "positions_live.json"
        self.pnl_json = self.output_dir / "pnl_live.json"

    def save_trade(self, trade: Dict):
        """
        Save a single trade to CSV with consistent column structure.

        Args:
            trade: Trade dict from PaperExecutor
        """
        # Define standard columns (always present)
        standard_columns = [
            "position_id",
            "action",
            "timestamp",
            "time_ist",
            "underlying",
            "strike",
            "option_type",
            "price",
            "qty",
            "strategy",
        ]

        # Optional columns for CLOSE actions
        optional_columns = ["exit_reason", "realized_pnl", "realized_pnl_pct", "entry_price", "exit_price"]

        # Build trade data with standard columns first
        trade_data = {}
        for col in standard_columns:
            trade_data[col] = trade.get(col, None)

        # Add optional columns if present in trade dict
        for col in optional_columns:
            if col in trade:
                trade_data[col] = trade.get(col, None)

        df = pd.DataFrame([trade_data])

        # Read existing file to get all columns (for consistency)
        if self.trades_csv.exists():
            try:
                existing_df = pd.read_csv(self.trades_csv, nrows=1)
                all_columns = list(existing_df.columns)
                # Ensure all standard columns exist
                for col in standard_columns:
                    if col not in all_columns:
                        all_columns.append(col)
                # Ensure optional columns exist
                for col in optional_columns:
                    if col not in all_columns:
                        all_columns.append(col)
                # Reorder: standard first, then optional
                ordered_cols = standard_columns + [c for c in optional_columns if c in all_columns]
                # Add any other columns that might exist
                for col in all_columns:
                    if col not in ordered_cols:
                        ordered_cols.append(col)
                # Ensure df has all columns
                for col in ordered_cols:
                    if col not in df.columns:
                        df[col] = None
                df = df[ordered_cols]
            except:
                # If can't read existing, use standard structure
                all_columns = standard_columns + optional_columns
                for col in all_columns:
                    if col not in df.columns:
                        df[col] = None
                df = df[all_columns]
        else:
            # New file: use standard + optional structure
            all_columns = standard_columns + optional_columns
            for col in all_columns:
                if col not in df.columns:
                    df[col] = None
            df = df[all_columns]

        # Append to CSV
        if self.trades_csv.exists():
            df.to_csv(self.trades_csv, mode="a", header=False, index=False)
        else:
            df.to_csv(self.trades_csv, mode="w", header=True, index=False)

    def save_positions(self, positions: List[Dict], summary: Dict):
        """
        Save current positions to JSON.

        Args:
            positions: List of open positions
            summary: Positions summary
        """
        data = {
            "timestamp_ist": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S IST"),
            "open_positions": positions,
            "summary": summary,
        }

        with open(self.positions_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def save_pnl(self, pnl_summary: Dict):
        """
        Save PnL summary to JSON.

        Args:
            pnl_summary: PnL summary from PnLTracker
        """
        with open(self.pnl_json, "w", encoding="utf-8") as f:
            json.dump(pnl_summary, f, indent=2, default=str)

    def get_trade_history_df(self) -> pd.DataFrame:
        """Get trade history as DataFrame."""
        if self.trades_csv.exists():
            try:
                return pd.read_csv(self.trades_csv)
            except:
                return pd.DataFrame()
        return pd.DataFrame()
