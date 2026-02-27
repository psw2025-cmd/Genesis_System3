"""
Test Script for System3 Signal Engine

Tests all components and verifies non-zero scores.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.engine.system3_signal_engine import run_signal_engine
from core.utils.logger import logger


def create_test_snapshot() -> pd.DataFrame:
    """Create a test snapshot with sample data that simulates market movement."""
    # Create data with varying market conditions to trigger different signals
    base_time = datetime.now()
    
    test_data = {
        "ts": [base_time.isoformat()] * 12,
        "underlying": ["NIFTY", "NIFTY", "NIFTY", "NIFTY", 
                      "BANKNIFTY", "BANKNIFTY", "BANKNIFTY", "BANKNIFTY",
                      "FINNIFTY", "FINNIFTY", "FINNIFTY", "FINNIFTY"],
        "expiry": ["30DEC2025"] * 12,
        "strike": [23000.0, 23050.0, 23100.0, 23150.0,  # NIFTY - ATM and OTM
                   48000.0, 48050.0, 48100.0, 48150.0,  # BANKNIFTY
                   21000.0, 21050.0, 21100.0, 21150.0], # FINNIFTY
        "side": ["CE", "PE", "CE", "PE", "CE", "PE", "CE", "PE", "CE", "PE", "CE", "PE"],
        # Vary LTPs to simulate different market conditions
        # Higher LTPs for ITM, lower for OTM
        "ltp": [200.0, 50.0, 150.0, 80.0,   # NIFTY - bullish setup (CE higher)
                250.0, 60.0, 180.0, 90.0,   # BANKNIFTY - bullish setup
                190.0, 55.0, 160.0, 85.0],  # FINNIFTY - bullish setup
        # Spot prices - create upward trend scenario
        "spot": [23100.0, 23100.0, 23100.0, 23100.0,  # NIFTY - above strikes (bullish)
                 48100.0, 48100.0, 48100.0, 48100.0,  # BANKNIFTY - above strikes
                 21100.0, 21100.0, 21100.0, 21100.0]  # FINNIFTY - above strikes
    }
    return pd.DataFrame(test_data)


def test_signal_engine():
    """Test the complete signal engine."""
    print("=" * 70)
    print("SYSTEM3 SIGNAL ENGINE TEST")
    print("=" * 70)
    print()
    
    # Create test snapshot
    print("[1/5] Creating test snapshot...")
    df_snap = create_test_snapshot()
    print(f"✓ Created snapshot with {len(df_snap)} rows")
    print()
    
    # Process through signal engine
    print("[2/5] Processing through signal engine...")
    try:
        df_signals = run_signal_engine(df_snap)
        print(f"✓ Processed {len(df_signals)} signals")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()
    
    # Verify non-zero scores
    print("[3/5] Verifying non-zero scores...")
    if df_signals.empty:
        print("✗ No signals generated")
        return False
    
    zero_scores = (df_signals["final_score"] == 0.0).sum()
    total_signals = len(df_signals)
    
    if zero_scores == total_signals:
        print(f"✗ All {total_signals} signals have zero scores")
        return False
    else:
        print(f"✓ {total_signals - zero_scores}/{total_signals} signals have non-zero scores")
    print()
    
    # Verify BUY/SELL signals
    print("[4/5] Verifying BUY/SELL signals...")
    buy_count = len(df_signals[df_signals["signal"] == "BUY"])
    sell_count = len(df_signals[df_signals["signal"] == "SELL"])
    hold_count = len(df_signals[df_signals["signal"] == "HOLD"])
    
    print(f"✓ Signals: BUY={buy_count}, SELL={sell_count}, HOLD={hold_count}")
    
    if buy_count == 0 and sell_count == 0:
        print("⚠ Warning: No BUY or SELL signals generated (all HOLD)")
    print()
    
    # Display results
    print("[5/5] Displaying results...")
    print()
    display_cols = [
        "underlying", "strike", "side", "signal", "final_score",
        "pred_label", "pred_confidence"
    ]
    available_cols = [col for col in display_cols if col in df_signals.columns]
    
    print(df_signals[available_cols].to_string(index=False))
    print()
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total signals: {len(df_signals)}")
    print(f"Non-zero scores: {total_signals - zero_scores}/{total_signals}")
    print(f"BUY signals: {buy_count}")
    print(f"SELL signals: {sell_count}")
    print(f"HOLD signals: {hold_count}")
    print()
    
    # Test passes if:
    # 1. Non-zero scores are generated
    # 2. At least some signals are generated (even if all HOLD, that's OK for test data)
    # 3. Scores are in valid range
    
    score_range_valid = (
        (df_signals["final_score"] >= -1.0).all() and 
        (df_signals["final_score"] <= 1.0).all()
    )
    
    if zero_scores < total_signals and score_range_valid:
        if buy_count > 0 or sell_count > 0:
            print("✓ TEST PASSED (with BUY/SELL signals)")
        else:
            print("✓ TEST PASSED (non-zero scores generated, all HOLD due to test data)")
            print("  Note: To generate BUY/SELL, use real market data with stronger trends")
        return True
    else:
        print("✗ TEST FAILED")
        return False


if __name__ == "__main__":
    success = test_signal_engine()
    sys.exit(0 if success else 1)

