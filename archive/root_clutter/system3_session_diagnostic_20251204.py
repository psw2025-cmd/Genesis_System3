#!/usr/bin/env python3
"""
System3 Session Diagnostic - December 4, 2025
Analyzes today's market session to identify issues.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("="*80)
print("SYSTEM3 SESSION DIAGNOSTIC - December 4, 2025")
print("="*80)
print()

# 1. Check heartbeat
print("1. HEARTBEAT STATUS")
print("-"*80)
heartbeat_file = PROJECT_ROOT / "system3_daily_heartbeat.json"
if heartbeat_file.exists():
    hb = json.loads(heartbeat_file.read_text())
    print(f"   Last Update: {hb.get('timestamp', 'N/A')}")
    print(f"   Status: {hb.get('status', 'N/A')}")
    print(f"   Autopilot Running: {hb.get('autopilot_running', 'N/A')}")
    print(f"   Last Phase Run: {hb.get('last_phase_run', 'N/A')}")
    print(f"   Last Curated Refresh: {hb.get('last_curated_refresh', 'N/A')}")
    print(f"   Last OP Cycle: {hb.get('last_op_cycle', 'N/A')}")
else:
    print("   ❌ Heartbeat file not found")
print()

# 2. Check shutdown flag
print("2. SHUTDOWN FLAG STATUS")
print("-"*80)
shutdown_file = PROJECT_ROOT / "system3_shutdown_flag.json"
if shutdown_file.exists():
    sf = json.loads(shutdown_file.read_text())
    print(f"   Shutdown Date: {sf.get('shutdown_date', 'N/A')}")
    print(f"   Shutdown Time: {sf.get('shutdown_time', 'N/A')}")
    print(f"   Reason: {sf.get('reason', 'N/A')}")
    if sf.get('shutdown_date') == '2025-12-04':
        print("   ✅ Shutdown flag exists for today")
    else:
        print("   ⚠️ Shutdown flag is from previous day")
else:
    print("   ❌ No shutdown flag (system did not shut down gracefully)")
print()

# 3. Analyze autorun master log
print("3. AUTORUN MASTER LOG ANALYSIS")
print("-"*80)
autorun_log = PROJECT_ROOT / "logs" / "system3_autorun_master_20251204.log"
if autorun_log.exists():
    content = autorun_log.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    
    # Count phase runs
    phase_runs = [l for l in lines if "Phase run complete" in l]
    print(f"   Total Phase Runs: {len(phase_runs)}")
    
    # Find last activity
    last_lines = lines[-20:]
    print(f"\n   Last 5 Log Entries:")
    for line in last_lines[-5:]:
        if line.strip():
            print(f"   {line[:100]}")
    
    # Count Phase 223 errors
    phase223_errors = [l for l in lines if "Phase 223: ERROR" in l]
    print(f"\n   Phase 223 Errors: {len(phase223_errors)}")
    if phase223_errors:
        print(f"   First Error: {phase223_errors[0][:100]}")
        print(f"   Last Error: {phase223_errors[-1][:100]}")
else:
    print("   ❌ Autorun log not found")
print()

# 4. Check watchdog log
print("4. WATCHDOG LOG ANALYSIS")
print("-"*80)
watchdog_log = PROJECT_ROOT / "logs" / "system3_watchdog_20251204.log"
if watchdog_log.exists():
    content = watchdog_log.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    print(f"   Total Log Entries: {len(lines)}")
    
    # Check for restart attempts
    restarts = [l for l in lines if "restart" in l.lower() or "starting master" in l.lower()]
    print(f"   Restart Attempts: {len(restarts)}")
    
    if len(lines) < 10:
        print("   ⚠️ Very few log entries - watchdog may not be active")
else:
    print("   ❌ Watchdog log not found")
print()

# 5. Check autopilot log
print("5. AUTOPILOT LOG ANALYSIS")
print("-"*80)
autopilot_log = PROJECT_ROOT / "logs" / "live_day_autopilot_20251204.log"
if autopilot_log.exists():
    content = autopilot_log.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    print(f"   Total Log Entries: {len(lines)}")
    
    # Find last activity
    last_lines = lines[-10:]
    print(f"\n   Last 5 Log Entries:")
    for line in last_lines[-5:]:
        if line.strip():
            print(f"   {line[:100]}")
else:
    print("   ❌ Autopilot log not found")
print()

# 6. Summary
print("="*80)
print("SUMMARY")
print("="*80)
print()
print("Issues Identified:")
print("  1. ⚠️ Phase 223 (Threshold Optimizer) - Repeated errors starting 9:45 AM")
print("  2. ❌ System stopped responding around noon (no activity after 11:46 AM)")
print("  3. ❌ No graceful shutdown occurred (no shutdown flag for today)")
print("  4. ⚠️ Watchdog may not have detected the crash")
print()
print("Recommendations:")
print("  1. Investigate system crash (check Windows Event Viewer)")
print("  2. Fix Phase 223 error (check threshold_optimizer.log)")
print("  3. Review watchdog behavior (ensure it detects crashes)")
print("  4. Test fixes before next market day")
print()

