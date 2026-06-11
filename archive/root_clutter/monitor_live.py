#!/usr/bin/env python3
"""
Live monitoring of System3 Autorun execution
Shows: Phases running, Signals generated, Orders placed, Predictions made
"""
import os
import time
import json
from pathlib import Path

def monitor():
    log_file = Path(r"c:\Genesis_System3\system3_live_run.log")
    last_pos = 0
    
    print("\n" + "="*70)
    print("  SYSTEM3 LIVE EXECUTION MONITOR")
    print("="*70 + "\n")
    
    while True:
        try:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_pos)
                    new_lines = f.readlines()
                    last_pos = f.tell()
                    
                    if new_lines:
                        print(f"\n[{time.strftime('%H:%M:%S')}] New output:")
                        print("-" * 70)
                        for line in new_lines[-20:]:  # Show last 20 new lines
                            line = line.rstrip()
                            if 'Phase' in line and 'OK' in line:
                                print(f"  ✓ {line}")
                            elif 'Phase' in line and 'WARN' in line:
                                print(f"  ⚠ {line}")
                            elif 'Signal' in line or 'signal' in line.lower():
                                print(f"  📊 {line}")
                            elif 'Order' in line or 'order' in line.lower():
                                print(f"  💰 {line}")
                            elif 'Heartbeat' in line:
                                print(f"  💓 {line}")
                            else:
                                print(f"     {line}")
                        print("-" * 70)
            
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == '__main__':
    monitor()
