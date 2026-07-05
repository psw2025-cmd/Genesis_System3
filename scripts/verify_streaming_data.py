"""
Verify that the system is using streaming data, not static data
Tests that data changes between cycles
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.sim.replay_engine import ReplayEngine


def test_streaming_data():
    """Test that replay engine generates different data each cycle."""
    print("\n" + "=" * 80)
    print("  STREAMING DATA VERIFICATION TEST")
    print("=" * 80 + "\n")

    # Initialize replay engine
    try:
        engine = ReplayEngine()
        print("[OK] Replay engine initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize: {e}")
        return False

    # Generate snapshots for 3 consecutive cycles
    print("\n[TEST] Generating snapshots for 3 consecutive cycles...")

    snapshots = []
    for cycle in range(3):
        snapshot = engine.generate_snapshot(scenario="TREND_UP", cycle=cycle, total_cycles=10, inject_errors=False)
        snapshots.append(snapshot)
        print(f"  Cycle {cycle}: Generated data for {len(snapshot)} underlyings")

    # Verify data is different between cycles
    print("\n[TEST] Verifying data changes between cycles...")

    all_different = True
    for underlying in snapshots[0].keys():
        df1 = snapshots[0][underlying]
        df2 = snapshots[1][underlying]
        df3 = snapshots[2][underlying]

        # Check if prices are different
        if len(df1) > 0 and len(df2) > 0:
            # Get first contract's LTP
            ltp1 = df1["ltp"].iloc[0] if "ltp" in df1.columns else None
            ltp2 = df2["ltp"].iloc[0] if "ltp" in df2.columns else None
            ltp3 = df3["ltp"].iloc[0] if "ltp" in df3.columns else None

            if ltp1 is not None and ltp2 is not None:
                diff1_2 = abs(ltp1 - ltp2)
                diff2_3 = abs(ltp2 - ltp3)

                if diff1_2 == 0 and diff2_3 == 0:
                    print(f"  [WARNING] {underlying}: Prices not changing between cycles!")
                    all_different = False
                else:
                    print(
                        f"  [OK] {underlying}: LTP changed - Cycle 0: {ltp1:.2f}, Cycle 1: {ltp2:.2f}, Cycle 2: {ltp3:.2f}"
                    )

            # Check timestamps
            if "fetch_timestamp" in df1.columns and "fetch_timestamp" in df2.columns:
                ts1 = df1["fetch_timestamp"].iloc[0]
                ts2 = df2["fetch_timestamp"].iloc[0]
                if ts1 == ts2:
                    print(f"  [WARNING] {underlying}: Timestamps not changing!")
                    all_different = False
                else:
                    print(f"  [OK] {underlying}: Timestamps changing - {ts1} -> {ts2}")

    # Check volume changes
    print("\n[TEST] Verifying volume changes...")
    for underlying in snapshots[0].keys():
        df1 = snapshots[0][underlying]
        df2 = snapshots[1][underlying]

        if "volume" in df1.columns and "volume" in df2.columns:
            vol1 = df1["volume"].sum()
            vol2 = df2["volume"].sum()
            if vol1 == vol2:
                print(f"  [WARNING] {underlying}: Volume not changing!")
            else:
                print(f"  [OK] {underlying}: Volume changed - {vol1} -> {vol2}")

    print("\n" + "=" * 80)
    if all_different:
        print("  RESULT: [OK] STREAMING DATA VERIFIED - Data changes between cycles")
    else:
        print("  RESULT: [WARNING] Some data may be static")
    print("=" * 80 + "\n")

    return all_different


if __name__ == "__main__":
    test_streaming_data()
