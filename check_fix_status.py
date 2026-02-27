"""
Quick status checker for Ultra Model feature fix
Run this after each signal generation cycle to verify the fix
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent
SIGNALS_CSV = ROOT_DIR / "storage" / "live" / "angel_index_ai_signals.csv"

print("\n" + "="*60)
print("ULTRA MODEL FIX - STATUS CHECK")
print("="*60)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

try:
    df = pd.read_csv(SIGNALS_CSV, nrows=10)
    
    # Check timestamp
    latest_ts = df['ts'].iloc[0] if 'ts' in df.columns else 'Unknown'
    print(f"Latest signal timestamp: {latest_ts}")
    print(f"Total columns: {len(df.columns)}")
    print()
    
    # Check for new features
    required_features = [
        'atm_dist_abs', 'atm_dist_pct', 'ce_pe_ratio', 'ce_pe_diff',
        'u_momentum_1', 'u_vol_short', 'u_moneyness_sq', 'u_ltp_percentile'
    ]
    
    present = sum(1 for f in required_features if f in df.columns)
    
    print(f"Feature Status: {present}/{len(required_features)} present")
    
    if present == 0:
        print("❌ NEW FEATURES NOT YET PRESENT")
        print("   → Waiting for next signal generation cycle")
        print("   → Check again in 5-10 minutes")
    elif present < len(required_features):
        print(f"⚠️  PARTIAL ({present}/{len(required_features)} features)")
        missing = [f for f in required_features if f not in df.columns]
        print(f"   Missing: {', '.join(missing[:3])}...")
    else:
        print("✅ ALL NEW FEATURES PRESENT!")
        
        # Check signal distribution
        if 'signal' in df.columns:
            print()
            # Read more rows for distribution
            df_full = pd.read_csv(SIGNALS_CSV)
            dist = df_full['signal'].value_counts()
            total = len(df_full)
            
            hold_pct = (dist.get('HOLD', 0) / total * 100) if total > 0 else 0
            
            print(f"Signal Distribution (last {total} signals):")
            for signal, count in dist.items():
                pct = (count / total * 100) if total > 0 else 0
                print(f"  {signal}: {count} ({pct:.1f}%)")
            
            print()
            if hold_pct > 70:
                print(f"⚠️  HOLD % still high: {hold_pct:.1f}%")
                print("   → Ultra models may still be falling back")
                print("   → Check logs for 'USING_ULTRA_MODEL' messages")
            elif hold_pct < 60:
                print(f"✅ HOLD % improved: {hold_pct:.1f}% (was 79%)")
                print("   → Ultra models working correctly!")
            else:
                print(f"📊 HOLD %: {hold_pct:.1f}% (monitoring...)")

except Exception as e:
    print(f"❌ Error reading signals: {e}")

print()
print("="*60)
