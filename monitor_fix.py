"""
Automated monitoring script for Ultra Model fix validation
Runs continuously until next signal cycle completes
"""

import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

ROOT_DIR = Path(__file__).resolve().parent
SIGNALS_CSV = ROOT_DIR / "storage" / "live" / "angel_index_ai_signals.csv"

def check_status():
    """Check current status of the fix"""
    now = datetime.now()
    print("\n" + "="*70)
    print(f"⏰ STATUS CHECK: {now.strftime('%H:%M:%S')}")
    print("="*70)
    
    try:
        # Check signals CSV
        df = pd.read_csv(SIGNALS_CSV, nrows=5)
        latest_ts = df['ts'].iloc[0] if 'ts' in df.columns else 'Unknown'
        
        # Parse timestamp
        try:
            signal_time = pd.to_datetime(latest_ts)
            age_minutes = (now - signal_time).total_seconds() / 60
            
            if age_minutes < 5:
                freshness = "🟢 FRESH (just generated!)"
            elif age_minutes < 30:
                freshness = f"🟡 {int(age_minutes)} minutes old"
            else:
                freshness = f"🔴 {int(age_minutes)} minutes old (waiting for new cycle)"
        except:
            freshness = "❓ Unknown"
        
        print(f"\n📄 Signals CSV Status:")
        print(f"   Last signal: {latest_ts}")
        print(f"   Freshness: {freshness}")
        print(f"   Columns: {len(df.columns)}")
        
        # Check for new features
        new_features = [
            'atm_dist_abs', 'atm_dist_pct', 'ce_pe_ratio', 'ce_pe_diff',
            'u_momentum_1', 'u_vol_short', 'u_moneyness_sq'
        ]
        
        present_count = sum(1 for f in new_features if f in df.columns)
        
        if present_count == 0:
            print(f"   Features: ❌ OLD (74 columns, no Ultra features)")
            print(f"   Status: ⏳ Waiting for next signal cycle")
        elif present_count < len(new_features):
            print(f"   Features: ⚠️  PARTIAL ({present_count}/{len(new_features)})")
        else:
            print(f"   Features: ✅ NEW (Ultra features present!)")
            
            # Check signal distribution if features are present
            df_full = pd.read_csv(SIGNALS_CSV)
            if 'signal' in df_full.columns:
                dist = df_full['signal'].value_counts()
                total = len(df_full)
                hold_pct = (dist.get('HOLD', 0) / total * 100) if total > 0 else 0
                
                print(f"\n📊 Signal Distribution:")
                for signal, count in dist.items():
                    pct = (count / total * 100) if total > 0 else 0
                    print(f"   {signal}: {count} ({pct:.1f}%)")
                
                if hold_pct > 70:
                    print(f"\n   ⚠️  HOLD still high: {hold_pct:.1f}% (was 79%)")
                elif hold_pct < 60:
                    print(f"\n   ✅ HOLD improved: {hold_pct:.1f}% (was 79%)")
                    print(f"   🎉 FIX SUCCESSFUL!")
                    return True  # Fix is working!
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    # Calculate time until next cycle
    next_cycle = now.replace(minute=15 if now.minute < 15 else 45, second=0, microsecond=0)
    if now.minute >= 45:
        next_cycle = (now + timedelta(hours=1)).replace(minute=15, second=0, microsecond=0)
    
    wait_minutes = (next_cycle - now).total_seconds() / 60
    
    print(f"\n⏳ Next signal cycle: {next_cycle.strftime('%H:%M')} ({int(wait_minutes)} min)")
    print("="*70)
    
    return False  # Not validated yet


def main():
    """Run continuous monitoring"""
    print("\n" + "="*70)
    print("🔍 ULTRA MODEL FIX - CONTINUOUS MONITORING")
    print("="*70)
    print("\nMonitoring signals CSV for new features...")
    print("Will check every 2 minutes until fix is validated.")
    print("Press Ctrl+C to stop monitoring.\n")
    
    check_interval = 120  # 2 minutes
    
    try:
        while True:
            validated = check_status()
            
            if validated:
                print("\n" + "="*70)
                print("✅ FIX VALIDATED SUCCESSFULLY!")
                print("="*70)
                print("\nUltra models are now working correctly.")
                print("Signal distribution has improved.")
                print("\nYou can now proceed with Phase 392 ensemble training.")
                break
            
            # Wait before next check
            print(f"\n💤 Sleeping {check_interval//60} minutes until next check...")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped by user.")
        print("You can run this script again anytime:")
        print("  C:\\Python310\\python.exe monitor_fix.py\n")


if __name__ == "__main__":
    main()
