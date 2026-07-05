"""
Test Tri-State System - 5 minute simulation test
"""

import sys
import time
from datetime import datetime
from pathlib import Path

import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger
from scripts.smart_live_chain_runner import SmartLiveChainRunner

IST = pytz.timezone("Asia/Kolkata")


def main():
    """Run 5-minute test of tri-state system."""
    print("=" * 80)
    print("  TRI-STATE SYSTEM TEST - 5 MINUTE SIMULATION")
    print("=" * 80)
    print()
    print("Testing:")
    print("  1. Tri-state logic (LIVE/SIMULATION/MARKET_CLOSED)")
    print("  2. File updates every cycle")
    print("  3. Heartbeat mode when market closed")
    print("  4. Monitor logic")
    print()

    # Create runner
    runner = SmartLiveChainRunner(refresh_interval=5, market_check_interval=30, use_websocket=False)

    # Run for 5 minutes
    print("Starting 5-minute test run...")
    print()

    runner.run(duration_minutes=5)

    print()
    print("=" * 80)
    print("  TEST COMPLETE")
    print("=" * 80)
    print()
    print("Check outputs/ for:")
    print("  - chain_raw_live.csv (should update every 5s)")
    print("  - qc_report_live.json")
    print("  - top_trade_signal.json")
    print()
    print("Check logs for:")
    print("  - SIM_MODE ACTIVE messages")
    print("  - Mode switch messages")
    print("  - Cycle completion messages")
    print()


if __name__ == "__main__":
    main()
