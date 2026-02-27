"""
Angel One Index Options - Executor LIVE Mode Preparation

Prepares the executor for LIVE mode (but keeps it disabled for safety).
This module contains all the infrastructure needed for real order execution,
but requires explicit enablement in automation config.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any

from core.engine.angel_automation_config import AUTOMATION_CONFIG
from core.engine.angel_safety_checks import get_safety_validator


class LiveExecutorPrep:
    """
    Prepares for LIVE order execution (disabled by default).

    This class contains all the logic needed for real order execution,
    but will only execute if explicitly enabled in automation config.
    """

    def __init__(self):
        self.validator = get_safety_validator()

    def build_live_order_payload(self, trade_row: pd.Series) -> Dict[str, Any] | None:
        """
        Build Angel One API order payload for LIVE execution.

        Returns None if validation fails or LIVE mode is disabled.
        """
        # Safety check: LIVE mode must be explicitly enabled
        if not AUTOMATION_CONFIG.auto_execute_trades:
            return None

        # Validate trade plan
        validation = self.validator.validate_trade_plan(trade_row)
        if not validation["valid"]:
            return None

        # Check daily limits
        limit_check = self.validator.validate_daily_trade_limit(1, trade_row.get("underlying"))
        if not limit_check["allowed"]:
            return None

        # Build order payload (Angel One API format)
        underlying = trade_row["underlying"]
        strike = float(trade_row["strike"])
        opt_type = "CE" if trade_row.get("pred_label") == "BUY_CE" else "PE"
        qty = int(trade_row.get("quantity", 1))

        # Map underlying to Angel One exchange and symbol
        exchange_map = {
            "NIFTY": "NFO",
            "BANKNIFTY": "NFO",
            "FINNIFTY": "NFO",
            "MIDCPNIFTY": "NFO",
            "SENSEX": "BFO",
        }

        exchange = exchange_map.get(underlying, "NFO")

        # Build symbol (format: UNDERLYINGYYMMDDSTRIKETYPE)
        # This is a placeholder - actual symbol format depends on Angel One API
        # You'll need to implement proper symbol construction based on expiry
        expiry = trade_row.get("expiry", "")
        symbol = f"{underlying}{expiry}{int(strike)}{opt_type}"

        payload = {
            "exchange": exchange,
            "symbol": symbol,
            "transaction_type": "BUY",
            "order_type": "MARKET",  # or "LIMIT" with price
            "quantity": qty,
            "product_type": "INTRADAY",  # or "DELIVERY"
            "validity": "DAY",
            "price": float(trade_row.get("entry_price", 0.0)),  # for LIMIT orders
            "trigger_price": 0.0,  # for SL orders
        }

        return payload

    def execute_live_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a LIVE order via Angel One API.

        Currently returns a placeholder response.
        In production, this would call the actual Angel One API.
        """
        # Safety: LIVE mode must be explicitly enabled
        if not AUTOMATION_CONFIG.auto_execute_trades:
            return {
                "success": False,
                "error": "LIVE execution is disabled in automation config",
            }

        # Additional safety: double-check automation status
        automation_check = self.validator.validate_automation_enabled()
        if automation_check.get("warnings"):
            # Even if enabled, warn about LIVE mode
            print("[WARNING] LIVE execution requested - ensure this is intentional!")

        # Placeholder for actual API call
        # In production, this would be:
        # from core.brokers.angel_one.broker import AngelOneBroker
        # broker = AngelOneBroker()
        # response = broker.place_order(payload)
        # return response

        return {
            "success": False,
            "error": "LIVE execution not yet implemented - use DRY RUN mode",
            "payload": payload,
        }

    def validate_live_mode_ready(self) -> Dict[str, Any]:
        """Check if system is ready for LIVE mode."""
        result = {
            "ready": False,
            "checks": [],
            "warnings": [],
        }

        # Check 1: Automation config
        if AUTOMATION_CONFIG.auto_execute_trades:
            result["checks"].append("✓ Auto-execution enabled")
        else:
            result["checks"].append("✗ Auto-execution disabled")
            result["warnings"].append("Enable auto_execute_trades in automation config")

        # Check 2: Safety validator
        try:
            validator = get_safety_validator()
            result["checks"].append("✓ Safety validator available")
        except Exception as e:
            result["checks"].append(f"✗ Safety validator error: {e}")
            result["warnings"].append("Safety validator not available")

        # Check 3: Broker connection (placeholder)
        result["checks"].append("⚠ Broker connection check not implemented")

        # Check 4: Daily limits configured
        if AUTOMATION_CONFIG.max_trades_per_day > 0:
            result["checks"].append(f"✓ Daily limit: {AUTOMATION_CONFIG.max_trades_per_day}")
        else:
            result["warnings"].append("Daily trade limit not set")

        result["ready"] = len(result["warnings"]) == 0

        return result


def main() -> None:
    """Main entry point for LIVE executor prep."""
    print("=== ANGEL ONE EXECUTOR - LIVE MODE PREPARATION ===")
    print("\n[INFO] LIVE mode is currently DISABLED for safety.")
    print("[INFO] This module prepares infrastructure but requires explicit enablement.\n")

    prep = LiveExecutorPrep()
    readiness = prep.validate_live_mode_ready()

    print("=== LIVE MODE READINESS CHECK ===")
    for check in readiness["checks"]:
        print(f"  {check}")

    if readiness["warnings"]:
        print("\nWarnings:")
        for warn in readiness["warnings"]:
            print(f"  ⚠ {warn}")

    print(f"\nOverall Status: {'READY' if readiness['ready'] else 'NOT READY'}")
    print("\n[SAFETY] LIVE mode will remain disabled until:")
    print("  1. Automation config explicitly enables it")
    print("  2. All safety checks pass")
    print("  3. Manual confirmation provided")


if __name__ == "__main__":
    main()
