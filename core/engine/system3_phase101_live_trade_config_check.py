"""
System3 Phase 101 - Live Trading Config + Sanity Check

Central config layer for live trading (Mode 1 Angel Only) + a check script
that can be run before market to verify configuration.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import config
try:
    from config.live_trade_config import (
        LIVE_TRADING_ENABLED,
        MAX_LIVE_TRADES_PER_DAY,
        MAX_LIVE_TRADES_PER_UNDERLYING,
        MAX_RISK_PER_TRADE_RUPEES,
        DEFAULT_LOTS_PER_TRADE,
        LIVE_ALLOWED_UNDERLYINGS,
        ANGEL_PRODUCT_TYPE,
        ANGEL_ORDER_VARIETY,
        ANGEL_ALLOWED_ORDER_TYPES,
    )
except ImportError as e:
    print(f"[PH101] ERROR: Failed to import live_trade_config: {e}")
    sys.exit(1)

# Paths
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_LIVE.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON = STORAGE_LIVE / "phase101_live_trade_config_snapshot.json"


def run_phase101(**kwargs) -> dict:
    """
    Validate live trading configuration and create snapshot.

    Returns:
        dict: {
            "phase": 101,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },
            "errors": [],
        }
    """
    errors = []
    warnings = []

    # Validate LIVE_TRADING_ENABLED is False by default
    if LIVE_TRADING_ENABLED:
        warnings.append("WARNING: LIVE_TRADING_ENABLED=True")

    # Validate limits are positive integers
    if MAX_LIVE_TRADES_PER_DAY <= 0:
        errors.append("MAX_LIVE_TRADES_PER_DAY must be positive")

    if MAX_LIVE_TRADES_PER_UNDERLYING <= 0:
        errors.append("MAX_LIVE_TRADES_PER_UNDERLYING must be positive")

    if MAX_RISK_PER_TRADE_RUPEES <= 0:
        errors.append("MAX_RISK_PER_TRADE_RUPEES must be positive")

    if DEFAULT_LOTS_PER_TRADE <= 0:
        errors.append("DEFAULT_LOTS_PER_TRADE must be positive")

    # Validate underlyings list is non-empty
    if not LIVE_ALLOWED_UNDERLYINGS or len(LIVE_ALLOWED_UNDERLYINGS) == 0:
        errors.append("LIVE_ALLOWED_UNDERLYINGS must be non-empty")

    # Validate Angel settings
    if not ANGEL_PRODUCT_TYPE:
        errors.append("ANGEL_PRODUCT_TYPE must be set")

    if not ANGEL_ORDER_VARIETY:
        errors.append("ANGEL_ORDER_VARIETY must be set")

    if not ANGEL_ALLOWED_ORDER_TYPES or len(ANGEL_ALLOWED_ORDER_TYPES) == 0:
        errors.append("ANGEL_ALLOWED_ORDER_TYPES must be non-empty")

    # Create snapshot
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "LIVE_TRADING_ENABLED": LIVE_TRADING_ENABLED,
        "MAX_LIVE_TRADES_PER_DAY": MAX_LIVE_TRADES_PER_DAY,
        "MAX_LIVE_TRADES_PER_UNDERLYING": MAX_LIVE_TRADES_PER_UNDERLYING,
        "MAX_RISK_PER_TRADE_RUPEES": MAX_RISK_PER_TRADE_RUPEES,
        "DEFAULT_LOTS_PER_TRADE": DEFAULT_LOTS_PER_TRADE,
        "LIVE_ALLOWED_UNDERLYINGS": LIVE_ALLOWED_UNDERLYINGS,
        "ANGEL_PRODUCT_TYPE": ANGEL_PRODUCT_TYPE,
        "ANGEL_ORDER_VARIETY": ANGEL_ORDER_VARIETY,
        "ANGEL_ALLOWED_ORDER_TYPES": ANGEL_ALLOWED_ORDER_TYPES,
        "status": "OK" if not errors else "ERROR",
        "warnings": warnings,
        "errors": errors,
    }

    # Write snapshot
    try:
        with OUTPUT_JSON.open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
    except Exception as e:
        errors.append(f"Failed to write snapshot: {e}")

    # Determine status
    if errors:
        status = "ERROR"
        details = f"Config validation failed: {len(errors)} error(s)"
    elif warnings:
        status = "OK"
        details = f"Config check OK with {len(warnings)} warning(s)"
    else:
        status = "OK"
        details = "Config check OK"

    return {
        "phase": 101,
        "status": status,
        "details": details,
        "outputs": {
            "snapshot_path": str(OUTPUT_JSON),
            "live_trading_enabled": LIVE_TRADING_ENABLED,
            "max_trades_per_day": MAX_LIVE_TRADES_PER_DAY,
            "max_trades_per_underlying": MAX_LIVE_TRADES_PER_UNDERLYING,
            "allowed_underlyings": LIVE_ALLOWED_UNDERLYINGS,
        },
        "errors": errors,
        "warnings": warnings,
    }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 101 - LIVE TRADING CONFIG CHECK")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase101()

    # Print summary
    print(f"Phase101: {result['details']}")
    if result.get("warnings"):
        for warning in result["warnings"]:
            print(f"  [WARN] {warning}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    print(f"\nSnapshot saved to: {result['outputs']['snapshot_path']}")

    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
