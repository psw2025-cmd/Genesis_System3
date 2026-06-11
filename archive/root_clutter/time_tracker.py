#!/usr/bin/env python3
"""
System3 Market Time Tracker - Continuous Time Monitoring
Monitors trading hours and logs status every 5 minutes
Monday-Friday, 09:15 AM to 04:00 PM
"""

import os
import sys
import time
import json
from datetime import datetime, time as dt_time
from pathlib import Path

# Setup paths
ROOT = Path(__file__).parent
LOG_FILE = ROOT / "logs" / "time_tracker.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Market hours configuration
MARKET_START = dt_time(9, 15)  # 09:15 AM
MARKET_CLOSE = dt_time(16, 0)  # 04:00 PM (16:00)
TRADING_DAYS = [0, 1, 2, 3, 4]  # Monday=0, Friday=4

def log_time_check(message=""):
    """Log current time with message"""
    now = datetime.now()
    day_name = now.strftime("%A")
    time_str = now.strftime("%H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")
    
    log_entry = f"[{date_str} {time_str}] {message}".strip()
    
    # Log to file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")
    
    # Print to console
    print(f"{time_str} | {log_entry}")
    
    return now

def is_trading_time(dt):
    """Check if time is within market hours"""
    weekday = dt.weekday()
    current_time = dt.time()
    
    if weekday not in TRADING_DAYS:
        return False, "MARKET_CLOSED (Weekend)"
    
    if current_time < MARKET_START:
        return False, "PRE_MARKET"
    elif current_time >= MARKET_CLOSE:
        return False, "POST_MARKET"
    else:
        return True, "MARKET_OPEN"

def get_time_until_close(dt):
    """Get minutes until market close"""
    if dt.date() != datetime.now().date():
        return 0
    
    close_time = datetime.combine(dt.date(), MARKET_CLOSE)
    if dt > close_time:
        return 0
    
    delta = close_time - dt
    minutes = int(delta.total_seconds() / 60)
    return minutes

def main():
    """Main time tracking loop"""
    
    print("=" * 70)
    print("SYSTEM3 - MARKET TIME TRACKER")
    print("=" * 70)
    print(f"Market hours: Monday-Friday, 09:15 AM to 04:00 PM (16:00)")
    print(f"Log file: {LOG_FILE}")
    print("=" * 70)
    print()
    
    log_time_check("=== TIME TRACKER STARTED ===")
    
    check_interval = 300  # 5 minutes
    last_status = None
    
    try:
        while True:
            now = datetime.now()
            is_open, status = is_trading_time(now)
            
            # Detailed status
            if is_open:
                mins_left = get_time_until_close(now)
                detail = f"TRADING ACTIVE - {mins_left} min until close (04:00 PM)"
                status_icon = "✅"
            elif status == "PRE_MARKET":
                detail = "Pre-market - waiting for 09:15 AM open"
                status_icon = "⏳"
            elif status == "POST_MARKET":
                detail = "Market closed - will resume Monday 09:15 AM"
                status_icon = "🔴"
            else:
                detail = f"Weekend/Holiday - {status}"
                status_icon = "🔴"
            
            # Log status change
            if status != last_status:
                log_time_check(f"{status_icon} STATUS: {detail}")
                last_status = status
            
            # Brief status every 5 minutes
            time.sleep(check_interval)
            
            now = datetime.now()
            is_open, _ = is_trading_time(now)
            
            if is_open:
                mins_left = get_time_until_close(now)
                log_time_check(f"⏱️  {mins_left} minutes until market close")
            
    except KeyboardInterrupt:
        log_time_check("=== TIME TRACKER STOPPED BY USER ===")
        print("\n\nTime tracker stopped.")
        sys.exit(0)
    except Exception as e:
        log_time_check(f"ERROR: {str(e)}")
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
