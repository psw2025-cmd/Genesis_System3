"""
Angel One Index Options - Trade Lifecycle Logger

Tracks complete trade lifecycle from signal → plan → execution → PnL.
Provides detailed audit trail for monitoring and debugging.
"""

import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIFECYCLE_LOG_CSV = PROJECT_ROOT / "storage" / "live" / "angel_trade_lifecycle_log.csv"


class TradeLifecycleLogger:
    """Logs complete trade lifecycle events."""

    def __init__(self):
        self.log_path = LIFECYCLE_LOG_CSV
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(
        self,
        event_type: str,
        trade_id: str | None = None,
        underlying: str | None = None,
        strike: float | None = None,
        side: str | None = None,
        details: Dict[str, Any] | None = None,
    ) -> None:
        """
        Log a lifecycle event.

        Event types:
        - SIGNAL_GENERATED: AI signal created
        - TRADE_PLANNED: Trade plan created
        - TRADE_EXECUTED: Trade executed (DRY RUN or LIVE)
        - TRADE_EXITED: Trade exited (TP/SL/TIMEOUT)
        - PNL_COMPUTED: PnL computed for trade
        """
        event = {
            "ts": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "trade_id": trade_id or "",
            "underlying": underlying or "",
            "strike": strike or "",
            "side": side or "",
            "details": json.dumps(details) if details else "",
        }

        # Append to CSV
        df = pd.DataFrame([event])
        if self.log_path.exists():
            try:
                existing = pd.read_csv(self.log_path)
                df = pd.concat([existing, df], ignore_index=True)
            except Exception:
                pass

        df.to_csv(self.log_path, index=False)

    def get_trade_lifecycle(self, trade_id: str) -> pd.DataFrame:
        """Get all lifecycle events for a specific trade."""
        if not self.log_path.exists():
            return pd.DataFrame()

        try:
            df = pd.read_csv(self.log_path)
            return df[df["trade_id"] == trade_id].sort_values("ts")
        except Exception:
            return pd.DataFrame()

    def get_active_trades(self) -> pd.DataFrame:
        """Get all trades that are planned but not yet exited."""
        if not self.log_path.exists():
            return pd.DataFrame()

        try:
            df = pd.read_csv(self.log_path)
            executed = set(df[df["event_type"] == "TRADE_EXECUTED"]["trade_id"].unique())
            exited = set(df[df["event_type"] == "TRADE_EXITED"]["trade_id"].unique())
            active = executed - exited
            return df[df["trade_id"].isin(active)]
        except Exception:
            return pd.DataFrame()


# Global logger instance
_lifecycle_logger = None


def get_lifecycle_logger() -> TradeLifecycleLogger:
    """Get global lifecycle logger instance."""
    global _lifecycle_logger
    if _lifecycle_logger is None:
        _lifecycle_logger = TradeLifecycleLogger()
    return _lifecycle_logger


def generate_trade_id(underlying: str, strike: float, side: str, ts: str) -> str:
    """Generate unique trade ID."""
    return f"{underlying}_{strike}_{side}_{ts.replace(':', '').replace('-', '').replace(' ', '_')}"
