#!/usr/bin/env python3
"""
System3 Startup Verification
Quick check before starting autorun to ensure everything is ready.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, time as dt_time

PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("="*80)
print("SYSTEM3 STARTUP VERIFICATION")
print("="*80)
print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

# Check 1: Shutdown flag
shutdown_flag_file = PROJECT_ROOT / "system3_shutdown_flag.json"
if shutdown_flag_file.exists():
    try:
        with shutdown_flag_file.open("r") as f:
            shutdown_data = json.load(f)
        shutdown_date = shutdown_data.get("shutdown_date")
        today = datetime.now().strftime("%Y-%m-%d")
        
        if shutdown_date == today:
            print("⚠️  WARNING: Shutdown flag exists for today")
            print(f"   Shutdown time: {shutdown_data.get('shutdown_time')}")
            print("   This will prevent autorun from starting.")
            print("   ACTION: Delete shutdown flag if you want to restart today")
            print()
        else:
            print(f"✅ Shutdown flag from {shutdown_date} (OK, not today)")
            print()
    except Exception as e:
        print(f"⚠️  Could not read shutdown flag: {e}")
        print()
else:
    print("✅ No shutdown flag (OK for first run)")
    print()

# Check 2: Current time vs market hours
now = datetime.now()
current_time = now.time()
market_open = dt_time(9, 15)
market_close = dt_time(15, 30)

print(f"Current Time: {current_time.strftime('%H:%M:%S')}")
print(f"Market Open: {market_open.strftime('%H:%M:%S')}")
print(f"Market Close: {market_close.strftime('%H:%M:%S')}")
print()

if current_time < market_open:
    minutes_until_open = (datetime.combine(now.date(), market_open) - now).total_seconds() / 60
    print(f"✅ Pre-market: {minutes_until_open:.0f} minutes until market open")
    print("   Autorun will wait until 9:15 AM before starting autopilot")
    print()
elif market_open <= current_time <= market_close:
    print("✅ Market hours: Autorun will start autopilot immediately")
    print()
else:
    print("⚠️  After market hours: Autorun may not start autopilot")
    print("   (Expected behavior - autopilot only runs during market hours)")
    print()

# Check 3: Critical files
critical_files = [
    "system3_autorun_master.py",
    "system3_watchdog.py",
    "system3_live_day_autopilot.py",
    "START_AUTORUN_AND_WATCHDOG.bat",
]

all_exist = True
for file_name in critical_files:
    file_path = PROJECT_ROOT / file_name
    if file_path.exists():
        print(f"✅ {file_name}: EXISTS")
    else:
        print(f"❌ {file_name}: NOT FOUND")
        all_exist = False

print()

# Check 4: Safety flags
try:
    from config.live_trade_config import LIVE_TRADING_ENABLED, USE_LIVE_EXECUTION_ENGINE
    if LIVE_TRADING_ENABLED:
        print("❌ CRITICAL: LIVE_TRADING_ENABLED is True (must be False)")
    else:
        print("✅ LIVE_TRADING_ENABLED: False (DRY-RUN mode)")
    
    if USE_LIVE_EXECUTION_ENGINE:
        print("❌ CRITICAL: USE_LIVE_EXECUTION_ENGINE is True (must be False)")
    else:
        print("✅ USE_LIVE_EXECUTION_ENGINE: False (DRY-RUN mode)")
except Exception as e:
    print(f"⚠️  Could not check safety flags: {e}")

print()

# Final verdict
print("="*80)
if all_exist:
    print("✅ STARTUP VERIFICATION: READY TO START")
    print("="*80)
    print()
    print("You can now run: START_AUTORUN_AND_WATCHDOG.bat")
    print()
    print("Expected behavior:")
    print("1. Watchdog will start in a new window")
    print("2. Autorun master will start in current window")
    print("3. Pre-market phases (201-310) will run")
    print("4. System will wait until 9:15 AM")
    print("5. Autopilot will start automatically at 9:15 AM")
    print("6. System will run until 4:00 PM shutdown")
    print()
else:
    print("❌ STARTUP VERIFICATION: ISSUES DETECTED")
    print("="*80)
    print("Fix issues above before starting autorun")
print("="*80)

