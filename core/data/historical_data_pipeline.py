"""5-Year Historical Data Pipeline & Transaction Cost Modeling Engine for Genesis_System3.

Pulls, verifies, caches and backtests historical multi-year OHLCV candle datasets
with realistic institutional transaction frictions (Brokerage, STT, Exchange Turnover,
GST, Stamp Duty, and Execution Slippage).
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
HISTORICAL_DB_PATH = ROOT_DIR / "state" / "historical_market_data.db"


class InstitutionalCostModel:
    """Institutional Indian Options & Equities Transaction Cost Model."""

    def __init__(
        self,
        brokerage_per_order: float = 20.0,
        stt_rate_sell: float = 0.000625,  # 0.0625% on sell side option premium
        exchange_turnover_rate: float = 0.00053,  # 0.053% NSE turnover charges
        gst_rate: float = 0.18,  # 18% on (brokerage + exchange charges)
        stamp_duty_buy: float = 0.00003,  # 0.003% on buy side
        sebi_turnover_rate: float = 0.000001,  # ₹10 per crore
        slippage_rate: float = 0.0005,  # 0.05% execution slippage
    ):
        self.brokerage_per_order = brokerage_per_order
        self.stt_rate_sell = stt_rate_sell
        self.exchange_turnover_rate = exchange_turnover_rate
        self.gst_rate = gst_rate
        self.stamp_duty_buy = stamp_duty_buy
        self.sebi_turnover_rate = sebi_turnover_rate
        self.slippage_rate = slippage_rate

    def calculate_trade_friction(
        self,
        entry_price: float,
        exit_price: float,
        qty: int,
    ) -> Dict[str, float]:
        """Compute all regulatory & execution friction components for a round-trip trade."""
        buy_value = entry_price * qty
        sell_value = exit_price * qty
        turnover = buy_value + sell_value

        brokerage = self.brokerage_per_order * 2.0
        stt = sell_value * self.stt_rate_sell
        exchange_turnover = turnover * self.exchange_turnover_rate
        sebi_charges = turnover * self.sebi_turnover_rate
        stamp_duty = buy_value * self.stamp_duty_buy
        gst = (brokerage + exchange_turnover + sebi_charges) * self.gst_rate
        slippage = turnover * self.slippage_rate

        total_taxes_charges = brokerage + stt + exchange_turnover + sebi_charges + stamp_duty + gst
        total_friction = total_taxes_charges + slippage
        gross_pnl = (exit_price - entry_price) * qty
        net_pnl = gross_pnl - total_friction

        return {
            "gross_pnl": round(gross_pnl, 2),
            "net_pnl": round(net_pnl, 2),
            "total_friction": round(total_friction, 2),
            "brokerage": round(brokerage, 2),
            "stt": round(stt, 2),
            "exchange_turnover": round(exchange_turnover, 2),
            "gst": round(gst, 2),
            "stamp_duty": round(stamp_duty, 2),
            "slippage": round(slippage, 2),
        }


class HistoricalDataPipeline:
    """Ingests, caches and provides 5-year historical OHLCV data."""

    def __init__(self, db_path: Path = HISTORICAL_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.cost_model = InstitutionalCostModel()
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ohlcv_5y (
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    oi INTEGER DEFAULT 0,
                    source TEXT DEFAULT 'NSE_BHAVCOPY',
                    PRIMARY KEY (symbol, date)
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ohlcv_sym_date ON ohlcv_5y(symbol, date);")
        conn.close()

    def ingest_ohlcv_records(self, symbol: str, df: pd.DataFrame, source: str = "HISTORICAL_INGESTION") -> int:
        """Store historical records in SQLite database."""
        if df.empty:
            return 0
        conn = sqlite3.connect(self.db_path)
        records = []
        for idx, row in df.iterrows():
            date_str = str(idx) if isinstance(idx, (str, datetime)) else str(row.get("date") or row.get("timestamp") or "")
            if not date_str:
                continue
            records.append((
                symbol.upper(),
                date_str[:10],
                float(row["open"]),
                float(row["high"]),
                float(row["low"]),
                float(row["close"]),
                int(row.get("volume", 0)),
                int(row.get("oi", 0)),
                source,
            ))

        with conn:
            conn.executemany("""
                INSERT OR REPLACE INTO ohlcv_5y (
                    symbol, date, open, high, low, close, volume, oi, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
        conn.close()
        return len(records)

    def get_historical_df(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """Query historical OHLCV data for backtesting."""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT date, open, high, low, close, volume, oi FROM ohlcv_5y WHERE symbol = ?"
        params: List[Any] = [symbol.upper()]
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        query += " ORDER BY date ASC"

        df = pd.read_sql_query(query, conn, parse_dates=["date"], index_col="date")
        conn.close()
        return df

    def run_friction_aware_backtest(
        self,
        trades: List[Dict[str, Any]],
        initial_capital: float = 500000.0,
    ) -> Dict[str, Any]:
        """Evaluate trade series with institutional transaction friction."""
        processed_trades = []
        equity = initial_capital
        peak_equity = initial_capital
        max_drawdown = 0.0
        wins = 0
        losses = 0

        for trade in trades:
            entry = float(trade.get("entry_price") or 0.0)
            exit_ = float(trade.get("exit_price") or entry)
            qty = int(trade.get("qty") or 50)
            friction_res = self.cost_model.calculate_trade_friction(entry, exit_, qty)

            net_pnl = friction_res["net_pnl"]
            equity += net_pnl
            if equity > peak_equity:
                peak_equity = equity
            dd = (peak_equity - equity) / peak_equity if peak_equity > 0 else 0.0
            if dd > max_drawdown:
                max_drawdown = dd

            if net_pnl > 0:
                wins += 1
            else:
                losses += 1

            processed_trades.append({
                **trade,
                **friction_res,
                "portfolio_equity": round(equity, 2),
                "drawdown_pct": round(dd * 100, 2),
            })

        total_trades = len(processed_trades)
        win_rate = (wins / total_trades) if total_trades > 0 else 0.0
        total_net_pnl = equity - initial_capital

        return {
            "initial_capital": initial_capital,
            "final_equity": round(equity, 2),
            "total_net_pnl": round(total_net_pnl, 2),
            "total_trades": total_trades,
            "winning_trades": wins,
            "losing_trades": losses,
            "win_rate": round(win_rate, 4),
            "max_drawdown_pct": round(max_drawdown * 100, 2),
            "expectancy_per_trade": round(total_net_pnl / total_trades, 2) if total_trades > 0 else 0.0,
            "trades": processed_trades,
        }
