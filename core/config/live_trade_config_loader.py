"""
System3 Phase 234 - Live Trading Config Loader

Load and validate live trading configuration.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.utils.logger import logger

CONFIG_PATH = PROJECT_ROOT / "config" / "live_trade_config.json"

# Safe defaults (all flags must be false)
DEFAULT_CONFIG = {
    "LIVE_TRADING_ENABLED": False,
    "USE_ANGELONE_LIVE_EXECUTION": False,
    "MAX_DAILY_LOSS": 5000,
    "MAX_OPEN_POSITIONS": 3,
    "MAX_LOTS_PER_TRADE": 1,
    "AUTO_SQUARE_OFF_TIME": "15:20",
    "SYMBOL_WHITELIST": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"],
    "MIN_SCORE_FOR_TRADE": 0.12,
}


def load_live_trade_config() -> Dict[str, Any]:
    """
    Load live trading configuration from JSON file.

    Returns:
        dict: Configuration with safe defaults if file missing/invalid
    """
    if not CONFIG_PATH.exists():
        logger.warning(f"Live trade config not found: {CONFIG_PATH}. Using safe defaults.")
        return DEFAULT_CONFIG.copy()

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            config = json.load(f)

        # Ensure safe defaults for critical flags
        result = DEFAULT_CONFIG.copy()
        result.update(config)

        # CRITICAL: Force these to False if somehow set to True
        result["LIVE_TRADING_ENABLED"] = False
        result["USE_ANGELONE_LIVE_EXECUTION"] = False

        return result

    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON in live trade config: {e}. Using safe defaults.")
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        logger.warning(f"Error loading live trade config: {e}. Using safe defaults.")
        return DEFAULT_CONFIG.copy()


if __name__ == "__main__":
    config = load_live_trade_config()
    print("Loaded config:")
    for key, val in config.items():
        print(f"  {key}: {val}")
