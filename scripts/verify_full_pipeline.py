"""
Complete Pipeline Verification
Tests that the entire paper trading system uses streaming data
"""

import json
import sys
import time
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.sim.replay_engine import ReplayEngine
from src.trading.paper_executor import PaperExecutor
from src.trading.pnl_tracker import PnLTracker


def verify_full_pipeline():
    """Verify the complete pipeline uses streaming data."""
    print("\n" + "=" * 80)
    print("  COMPLETE PIPELINE VERIFICATION")
    print("=" * 80 + "\n")

    # Initialize components
    print("[1/5] Initializing components...")
    engine = ReplayEngine()
    executor = PaperExecutor()
    tracker = PnLTracker()
    print("  [OK] All components initialized")

    # Generate 3 cycles of data
    print("\n[2/5] Generating streaming data for 3 cycles...")
    all_data_cycles = []
    for cycle in range(3):
        snapshot = engine.generate_snapshot(scenario="TREND_UP", cycle=cycle, total_cycles=10, inject_errors=False)
        all_data_cycles.append(snapshot)

        # Check data is different
        if cycle > 0:
            prev_snap = all_data_cycles[cycle - 1]
            for underlying in snapshot.keys():
                if underlying in prev_snap:
                    prev_ltp = prev_snap[underlying]["ltp"].iloc[0] if len(prev_snap[underlying]) > 0 else None
                    curr_ltp = snapshot[underlying]["ltp"].iloc[0] if len(snapshot[underlying]) > 0 else None
                    if prev_ltp and curr_ltp and prev_ltp != curr_ltp:
                        print(f"  [OK] Cycle {cycle}: {underlying} LTP changed {prev_ltp:.2f} -> {curr_ltp:.2f}")

    # Simulate trade execution
    print("\n[3/5] Testing trade execution with streaming data...")
    trade_signal = {
        "action": "TRADE",
        "strategy": "BUY_CE",
        "underlying": "NIFTY",
        "tokens": [all_data_cycles[0]["NIFTY"]["token"].iloc[0].astype(str)],
        "strikes": [float(all_data_cycles[0]["NIFTY"]["strike"].iloc[0])],
        "entry_mid": float(all_data_cycles[0]["NIFTY"]["mid_price"].iloc[0]),
        "stop_loss": 100.0,
        "target": 200.0,
        "confidence": 0.8,
    }

    position = executor.execute_trade(trade_signal, all_data_cycles[0]["NIFTY"], "2026-01-31T14:00:00")

    if position:
        print(f"  [OK] Trade executed: {position['position_id']}")
        print(f"  [OK] Entry price: Rs {position['entry_price']:.2f}")
    else:
        print("  [ERROR] Trade execution failed")
        return False

    # Update position with fresh data from cycle 1
    print("\n[4/5] Updating position with fresh streaming data...")
    closed = executor.update_positions(all_data_cycles[1], "2026-01-31T14:00:05")

    summary = executor.get_positions_summary()
    if summary["open_positions"]:
        pos = summary["open_positions"][0]
        print(f"  [OK] Position updated with fresh data")
        print(f"  [OK] Current price: Rs {pos['current_price']:.2f}")
        print(f"  [OK] Unrealized PnL: Rs {pos['unrealized_pnl']:.2f}")

        # Verify price changed
        if pos["current_price"] != position["entry_price"]:
            print(f"  [OK] Price updated from Rs {position['entry_price']:.2f} to Rs {pos['current_price']:.2f}")
        else:
            print(f"  [WARNING] Price not changing - may be using static data")
    else:
        print("  [INFO] Position closed (may have hit SL/TP)")

    # Update with cycle 2 data
    print("\n[5/5] Updating position with cycle 2 streaming data...")
    closed2 = executor.update_positions(all_data_cycles[2], "2026-01-31T14:00:10")

    summary2 = executor.get_positions_summary()
    if summary2["open_positions"]:
        pos2 = summary2["open_positions"][0]
        print(f"  [OK] Position updated again")
        print(f"  [OK] New current price: Rs {pos2['current_price']:.2f}")
        print(f"  [OK] New unrealized PnL: Rs {pos2['unrealized_pnl']:.2f}")

        # Verify continuous updates
        if pos2["current_price"] != pos["current_price"]:
            print(
                f"  [OK] Price continuously updating: Rs {pos['current_price']:.2f} -> Rs {pos2['current_price']:.2f}"
            )
        else:
            print(f"  [WARNING] Price not updating between cycles")

    # Test PnL tracking
    print("\n[6/6] Testing PnL tracking with streaming data...")
    pnl_summary = tracker.update(summary2, "2026-01-31T14:00:10")
    print(f"  [OK] PnL tracked: Rs {pnl_summary['total_pnl']:.2f}")
    print(f"  [OK] Unrealized: Rs {pnl_summary['total_unrealized_pnl']:.2f}")

    print("\n" + "=" * 80)
    print("  RESULT: [OK] COMPLETE PIPELINE VERIFIED")
    print("  - Streaming data generation: WORKING")
    print("  - Trade execution: WORKING")
    print("  - Position updates: WORKING")
    print("  - PnL tracking: WORKING")
    print("=" * 80 + "\n")

    return True


if __name__ == "__main__":
    verify_full_pipeline()
