"""
Shared context for all System3 routers.
Import this in each router instead of duplicating state.
"""
from __future__ import annotations
import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytz

IST = pytz.timezone("Asia/Kolkata")

# Root directory
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Timeouts
BROKER_IO_TIMEOUT_S  = 8.0
SCANNER_IO_TIMEOUT_S = 120.0
TRUTH_IO_TIMEOUT_S   = 45.0

# Common paths
OUTPUTS_DIR      = ROOT_DIR / "src" / "outputs"
STATE_DIR        = ROOT_DIR / "state"
GAIN_RANK_FILE   = STATE_DIR / "gain_rank_history.json"
VAL_DIR          = STATE_DIR / "market_validations"
KILL_SWITCH_FILE = ROOT_DIR / "config" / "kill_switch.json"
RISK_CONFIG_FILE = ROOT_DIR / "config" / "system3_risk_config.yml"


async def run_blocking(fn, *args, timeout: float = 15.0, **kwargs):
    """Run sync I/O in a worker thread with a hard timeout."""
    return await asyncio.wait_for(
        asyncio.to_thread(fn, *args, **kwargs), timeout=timeout
    )


def market_closed_response(segment: str = "NIFTY") -> Dict[str, Any]:
    """Standard response for market-closed state."""
    return {
        "status": "market_closed",
        "market_open": False,
        "note": "Market closed — data from last session",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def load_json_file(path: Path, default=None):
    """Safe JSON file load with default."""
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return default if default is not None else {}


def is_market_open_now() -> bool:
    """Check market hours — Mon-Fri, 9:15-15:30 IST."""
    try:
        from utils.market_hours import is_market_open
        open_now, _ = is_market_open()
        return bool(open_now)
    except Exception:
        now = datetime.now(IST)
        if now.weekday() >= 5:
            return False
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        return market_open <= now <= market_close
