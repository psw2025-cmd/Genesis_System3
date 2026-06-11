#!/usr/bin/env python3
"""
CONTINUOUS LIVE MONITORING - Full Day Tracking
Run this in background to monitor system performance throughout the day
"""
import pandas as pd
import os
import time
from datetime import datetime
import json

def check_processes():
    """Check if system3 processes are running"""
    try:
        import subprocess
        result = subprocess.run(['powershell', '-Command', 
                               'Get-Process python* -ErrorAction SilentlyContinue | Measure-Object | Select-Object -ExpandProperty Count'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            try:
                count = int(result.stdout.strip())
                return count
            except:
                return 0
    except Exception as e:
        pass
    return 0

def get_file_age(filepath):
    """Get file age in minutes"""
    if not os.path.exists(filepath):
        return None
    age_seconds = time.time() - os.path.getmtime(filepath)
    return age_seconds / 60

def main():
    """Main monitoring loop"""
    
    print("="*100)
    print("  SYSTEM3 CONTINUOUS MONITORING")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Press Ctrl+C to stop")
    print("="*100)
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            now = datetime.now()
            
            print(f"\n{'='*100}")
            print(f"  UPDATE #{iteration} - {now.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*100}")
            
            # 1. Check if system is running
            num_processes = check_processes()
            print(f"\n🔍 System Status: {num_processes} Python processes running")
            
            if num_processes == 0:
                print("   ⚠️  WARNING: No Python processes detected!")
            elif num_processes < 5:
                print("   ⚠️  WARNING: Fewer processes than expected")
            else:
                print("   ✅ System appears healthy")
            
            # 2. Check heartbeat
            hb_file = 'system3_daily_heartbeat.json'
            hb_age = get_file_age(hb_file)
            
            if hb_age is None:
                print(f"\n💔 Heartbeat: File not found")
            elif hb_age < 2:
                print(f"\n💚 Heartbeat: FRESH ({hb_age:.1f} min ago)")
                try:
                    with open(hb_file, 'r') as f:
                        hb = json.load(f)
                    print(f"   Last update: {hb.get('last_update', 'Unknown')}")
                    print(f"   Status: {hb.get('status', 'Unknown')}")
                    print(f"   Cycle: {hb.get('cycle_count', 'Unknown')}")
                except:
                    pass
            else:
                print(f"\n💛 Heartbeat: STALE ({hb_age:.1f} min ago)")
            
            # 3. Check signal file freshness
            sig_file = 'storage/live/angel_index_ai_signals_curated.csv'
            sig_age = get_file_age(sig_file)
            
            if sig_age is None:
                print(f"\n📊 Signals: No file")
            elif sig_age < 10:
                try:
                    signals = pd.read_csv(sig_file)
                    print(f"\n📊 Signals: {len(signals)} rows (updated {sig_age:.1f} min ago)")
                    
                    if 'signal' in signals.columns:
                        sig_dist = signals['signal'].value_counts().to_dict()
                        print(f"   Distribution: {sig_dist}")
                except Exception as e:
                    print(f"\n📊 Signals: Error reading - {e}")
            else:
                print(f"\n📊 Signals: STALE ({sig_age:.1f} min ago)")
            
            # 4. Check orders
            ord_file = 'storage/live/angel_virtual_orders_with_pnl.csv'
            if os.path.exists(ord_file):
                try:
                    orders = pd.read_csv(ord_file)
                    print(f"\n📋 Orders: {len(orders)} total")
                    
                    # Get recent orders (last 10 min)
                    if 'ts' in orders.columns:
                        orders['ts'] = pd.to_datetime(orders['ts'])
                        recent = orders[orders['ts'] > (now - pd.Timedelta(minutes=10))]
                        
                        if len(recent) > 0:
                            print(f"   Recent (last 10 min): {len(recent)} orders")
                            print(f"   Latest: {recent['ts'].max()}")
                        else:
                            print(f"   Recent (last 10 min): 0 orders")
                except Exception as e:
                    print(f"\n📋 Orders: Error - {e}")
            else:
                print(f"\n📋 Orders: No file")
            
            # 5. Quick PnL summary
            pnl_file = 'storage/live/angel_index_ai_pnl_log.csv'
            if os.path.exists(pnl_file):
                try:
                    pnl = pd.read_csv(pnl_file)
                    
                    if 'pnl_pct' in pnl.columns and len(pnl) > 0:
                        total_pnl = pnl['pnl_pct'].sum()
                        winners = len(pnl[pnl['pnl_pct'] > 0])
                        losers = len(pnl[pnl['pnl_pct'] < 0])
                        
                        status_icon = "💰" if total_pnl > 0 else "📉"
                        print(f"\n{status_icon} PnL: {total_pnl:+.2f}% ({len(pnl)} trades: {winners}W/{losers}L)")
                except Exception as e:
                    print(f"\n💰 PnL: Error - {e}")
            
            # 6. Check for errors in latest log
            log_dir = 'logs'
            if os.path.exists(log_dir):
                try:
                    # Find most recent log file
                    log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir) 
                                if f.endswith('.log')]
                    
                    if log_files:
                        latest_log = max(log_files, key=os.path.getmtime)
                        log_age = get_file_age(latest_log)
                        
                        # Read last 50 lines for errors
                        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            recent_lines = lines[-50:] if len(lines) > 50 else lines
                            
                            errors = [l for l in recent_lines if 'ERROR' in l.upper() or 'EXCEPTION' in l.upper()]
                            warnings = [l for l in recent_lines if 'WARNING' in l.upper() or 'WARN' in l.upper()]
                            
                            if errors:
                                print(f"\n⚠️  Errors in log: {len(errors)} (last {log_age:.1f} min)")
                                print(f"   Latest: {errors[-1].strip()[:100]}")
                            elif warnings:
                                print(f"\n⚠️  Warnings in log: {len(warnings)}")
                            else:
                                print(f"\n✅ No errors in recent logs")
                except Exception as e:
                    print(f"\n📝 Logs: Error checking - {e}")
            
            # 7. Next update countdown
            print(f"\n⏰ Next update in 2 minutes...")
            print(f"{'='*100}\n")
            
            # Sleep for 2 minutes
            time.sleep(120)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*100)
        print("  MONITORING STOPPED")
        print(f"  Ran for {iteration} iterations ({iteration * 2} minutes)")
        print("="*100)

if __name__ == '__main__':
    main()
