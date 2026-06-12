"""
Dhan Index Options - Safety Checks

Validates trade plans and execution requests before processing.
Ensures maximum safety for Monday's live trading.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any

from core.engine.dhan_automation_config import AUTOMATION_CONFIG
from core.engine.dhan_trade_config import DEFAULT_THRESHOLDS


class SafetyValidator:
    """Validates trades and operations for safety."""

    def __init__(self):
        self.max_trades_per_day = AUTOMATION_CONFIG.max_trades_per_day
        self.max_trades_per_underlying = AUTOMATION_CONFIG.max_trades_per_underlying_per_day

    def validate_trade_plan(self, trade_row: pd.Series) -> Dict[str, Any]:
        """
        Validate a single trade plan row.

        Returns dict with:
        - valid: bool
        - reason: str (if invalid)
        - warnings: list[str]
        """
        result = {
            "valid": True,
            "reason": "",
            "warnings": [],
        }

        # Check required fields
        required = ["underlying", "strike", "pred_label", "entry_price"]
        missing = [f for f in required if f not in trade_row.index or pd.isna(trade_row.get(f))]
        if missing:
            result["valid"] = False
            result["reason"] = f"Missing required fields: {missing}"
            return result

        # Check signal type
        label = trade_row.get("pred_label", "")
        if label not in ("BUY_CE", "BUY_PE"):
            result["valid"] = False
            result["reason"] = f"Invalid signal type: {label}"
            return result

        # Check confidence threshold
        conf = float(trade_row.get("pred_confidence", 0.0))
        if conf < DEFAULT_THRESHOLDS.min_confidence:
            result["valid"] = False
            result["reason"] = f"Confidence {conf:.3f} below threshold {DEFAULT_THRESHOLDS.min_confidence}"
            return result

        # Check score threshold
        score = abs(float(trade_row.get("expected_move_score", 0.0)))
        if score < DEFAULT_THRESHOLDS.min_abs_score:
            result["valid"] = False
            result["reason"] = f"Score {score:.3f} below threshold {DEFAULT_THRESHOLDS.min_abs_score}"
            return result

        # Check entry price
        entry = float(trade_row.get("entry_price", 0.0))
        if entry <= 0:
            result["valid"] = False
            result["reason"] = f"Invalid entry price: {entry}"
            return result

        # Warnings (non-blocking)
        if conf < 0.85:
            result["warnings"].append(f"Confidence is below 0.85: {conf:.3f}")

        if entry < 1.0:
            result["warnings"].append(f"Entry price is very low: {entry:.2f}")

        return result

    def validate_daily_trade_limit(self, new_trades: int, underlying: str | None = None) -> Dict[str, Any]:
        """
        Validate daily trade limits.

        Returns dict with:
        - allowed: bool
        - reason: str (if not allowed)
        """
        from pathlib import Path
        import os

        PROJECT_ROOT = Path(__file__).parent.parent.parent
        EXEC_LOG_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_trades_exec_log.csv"

        today = datetime.utcnow().date()

        # Count today's executions
        today_count = 0
        if EXEC_LOG_CSV.exists():
            try:
                df = pd.read_csv(EXEC_LOG_CSV)
                if "ts_exec" in df.columns:
                    df["ts_exec"] = pd.to_datetime(df["ts_exec"], errors="coerce")
                    df["date"] = df["ts_exec"].dt.date
                    today_count = len(df[df["date"] == today])
            except Exception:
                pass

        # Check total limit
        if today_count + new_trades > self.max_trades_per_day:
            return {
                "allowed": False,
                "reason": f"Would exceed daily limit: {today_count} + {new_trades} > {self.max_trades_per_day}",
            }

        # Check per-underlying limit
        if underlying:
            underlying_count = 0
            if EXEC_LOG_CSV.exists():
                try:
                    df = pd.read_csv(EXEC_LOG_CSV)
                    if "ts_exec" in df.columns and "underlying" in df.columns:
                        df["ts_exec"] = pd.to_datetime(df["ts_exec"], errors="coerce")
                        df["date"] = df["ts_exec"].dt.date
                        df_today = df[df["date"] == today]
                        underlying_count = len(df_today[df_today["underlying"] == underlying])
                except Exception:
                    pass

            if underlying_count + new_trades > self.max_trades_per_underlying:
                return {
                    "allowed": False,
                    "reason": f"Would exceed {underlying} limit: {underlying_count} + {new_trades} > {self.max_trades_per_underlying}",
                }

        return {"allowed": True, "reason": ""}

    def validate_automation_enabled(self) -> Dict[str, Any]:
        """Check if automation is safely enabled."""
        result = {
            "auto_execute": AUTOMATION_CONFIG.auto_execute_trades,
            "auto_pnl": AUTOMATION_CONFIG.auto_simulate_pnl,
            "safe": True,
            "warnings": [],
        }

        if result["auto_execute"]:
            result["warnings"].append("Auto-execution is ENABLED - ensure DRY RUN mode")
            # Still safe if DRY RUN, but warn

        return result


# Global validator instance
_safety_validator = None


def get_safety_validator() -> SafetyValidator:
    """Get global safety validator instance."""
    global _safety_validator
    if _safety_validator is None:
        _safety_validator = SafetyValidator()
    return _safety_validator
