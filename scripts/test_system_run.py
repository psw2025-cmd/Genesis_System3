"""
Quick test script to run the system for a short duration and capture output.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.run_live_chain import LiveChainRunner


def main():
    print("=" * 80)
    print("  TESTING LIVE PAPER TRADING SYSTEM")
    print("=" * 80)
    print()

    # Initialize runner
    print("[1] Initializing system...")
    runner = LiveChainRunner(
        refresh_interval=5,
        use_websocket=False,  # Use REST only for testing
        prefer_weekly=True,
        sim_mode=False,
        ignore_market_hours=True,
    )
    print("[OK] System initialized")
    print()

    # Run for 1 minute (12 cycles at 5s interval)
    print("[2] Running system for 1 minute (12 cycles)...")
    print("[INFO] Watch for cycle messages below...")
    print()
    print("=" * 80)

    try:
        results = runner.run(duration_minutes=1, max_cycles=12)

        print()
        print("=" * 80)
        print("[3] TEST COMPLETE")
        print("=" * 80)
        print(f"Total cycles completed: {runner.cycle_count}")
        print(f"Results collected: {len(results)}")

        if results:
            print("\nLast cycle result:")
            last = results[-1]
            print(f"  - Cycle: {last.get('cycle', 'N/A')}")
            print(f"  - QC Passed: {last.get('qc_passed', 'N/A')}")
            print(f"  - Top Underlying: {last.get('top_underlying', 'N/A')}")
            print(f"  - Trade Action: {last.get('trade_action', 'N/A')}")

            if "paper_trading" in last:
                pt = last["paper_trading"]
                print(f"  - PnL: Rs {pt.get('total_pnl', 0):,.2f}")
                print(f"  - Trades: {pt.get('total_trades', 0)}")

        return 0

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        return 0
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
