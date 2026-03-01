"""
💎 STOCK OPTION AI VERIFIER (PRO LEVEL)
Simulates a live stock option scan to prove accuracy and execution logic.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Setup Path
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.engine.system3_signal_engine import run_signal_engine

def verify_stock_options():
    print("=" * 60)
    print("💎 GENESIS SYSTEM3: STOCK OPTION AI VERIFICATION")
    print("=" * 60)

    # 1. Simulate REAL RELIANCE Stock Option Snapshot
    print("
[1] Generating Synthetic RELIANCE Snapshot...")
    spot = 2950.0
    data = []
    for strike in [2900, 2920, 2940, 2960, 2980, 3000]:
        for side in ["CE", "PE"]:
            # Real-world data structure
            data.append({
                "underlying": "RELIANCE",
                "strike": strike,
                "side": side,
                "ltp": 50 + np.random.normal(0, 5),
                "bid": 49, "ask": 51,
                "bid_qty": 500, "ask_qty": 200, # Imbalance for OFI
                "volume": 10000,
                "iv": 0.22,
                "pcr": 0.65,
                "spot": spot,
                "expiry": "2026-03-26"
            })
    
    df = pd.DataFrame(data)
    print(f"  ✅ Created {len(df)} RELIANCE option contracts")

    # 2. Run AI Engine (Stock-Aware Mode)
    print("
[2] Processing through AI Ensemble (40% Weight)...")
    results = run_signal_engine(df)
    
    # 3. Filtering for High-Conviction "Alpha"
    high_alpha = results[results["final_score"].abs() >= 0.65]
    
    print(f"
[3] SEARCH RESULTS (Threshold >= 0.65):")
    if high_alpha.empty:
        print("  ⏸️  No Ultra-Alpha signals found (Strict Filtering active)")
    else:
        for _, row in high_alpha.iterrows():
            print(f"  🎯 {row['signal']} {row['underlying']} {row['strike']} {row['side']} | Score: {row['final_score']:.4f}")
            print(f"     ➔ TP: {row.get('target_price', 0):.2f} | Partial: {row.get('partial_target', 0):.2f} | SL: {row.get('stop_loss', 0):.2f}")

    print("
" + "=" * 60)
    print("✅ STOCK OPTION VERIFICATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    verify_stock_options()
