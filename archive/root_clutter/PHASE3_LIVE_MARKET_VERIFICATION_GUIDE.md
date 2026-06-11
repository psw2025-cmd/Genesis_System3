# 🧪 PHASE 3 - END-TO-END LIVE-TIME VERIFICATION GUIDE

**Purpose:** Manual verification that the double-click flow works correctly during real market conditions.

**When to use:** After Phase 1 & 2 are complete, to validate the entire autorun + watchdog system during live trading hours.

**Expected Duration:** 15-30 minutes per test (can run before/during/after market)

---

## SECTION 1: PRE-TEST CHECKLIST

Before running any tests, ensure:

- [ ] Phase 1 (Venv Enforcement) is complete
  - Test: `python tools/system3_venv_sanity_check.py` returns ✅ PASS
  
- [ ] Phase 2 (Watchdog Self-Healing) is hardened
  - Watchdog code has stale heartbeat detection, restart caps, file lock handling
  
- [ ] No python processes running
  ```powershell
  tasklist | findstr python.exe
  # Should return nothing
  ```

- [ ] BAT file is updated with venv sanity check
  - Verify: `START_AUTORUN_AND_WATCHDOG.bat` calls `system3_venv_sanity_check.py`

---

## SECTION 2: TEST PLAN A - PRE-MARKET STARTUP (5-10 minutes)

**Objective:** Verify clean startup outside market hours with no side effects.

**Time Window:** Any time before 9:15 AM or after 4:00 PM IST (India market hours)

### Test A1: Clean Startup

```powershell
# Navigate to project
cd C:\Genesis_System3

# Kill any existing processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Double-click to start (simulating user action)
.\START_AUTORUN_AND_WATCHDOG.bat
```

**Expected Output:**
```
================================================
SYSTEM3 AUTORUN + WATCHDOG
================================================
One-click start | Fully autonomous | DRY-RUN enforced
================================================

================================================
PHASE 1: ENVIRONMENT VALIDATION AND AUTO-REPAIR
================================================

OK Virtual environment located
OK Virtual environment activated
OK Python environment ready
OK Venv sanity check passed
...
[After ~10 seconds, processes should start]
```

**Verification:**
```powershell
# In another PowerShell window, check processes are running
tasklist | findstr python.exe
# Should show 2-3 python.exe processes

# Check heartbeat file exists and updates
Get-Item C:\Genesis_System3\system3_daily_heartbeat.json | Select-Object LastWriteTime

# Check logs have entries
Get-Item C:\Genesis_System3\logs\system3_autorun_master_*.log | Get-Content -Tail 5
Get-Item C:\Genesis_System3\logs\system3_watchdog_*.log | Get-Content -Tail 5
```

**Pass Criteria:**
- ✅ Venv sanity check passes
- ✅ All 4 phases complete without errors
- ✅ 2-3 python processes running
- ✅ Heartbeat file created and updating
- ✅ Logs contain entries (no errors)

**If Failed:**
- ❌ Check `VENV_SANITY_STATUS.md` for venv issues
- ❌ Review `logs/system3_autorun_master_*.log` for startup errors
- ❌ See `VENV_RECOVERY_GUIDE.md` if dependencies missing

---

### Test A2: Running During Off-Hours (Expected Behavior)

**Objective:** Verify system gracefully idles when outside market hours.

**Expected Behavior (Outside 9:15-16:00):**
- Autorun master: Runs but waits for market hours
- Watchdog: Runs but does NOT restart master if it stops
- Heartbeat: Updates every 2 minutes
- Logs: Show "Outside market hours - not executing phases"

**Verification:**
```powershell
# Wait 2 minutes, then check heartbeat age
python -c "
from datetime import datetime
import json

with open('system3_daily_heartbeat.json') as f:
    hb = json.load(f)

ts = hb.get('system_info', {}).get('timestamp')
if ts:
    hb_time = datetime.fromisoformat(ts)
    age = (datetime.now() - hb_time).total_seconds()
    print(f'Heartbeat age: {int(age)}s')
    if age < 120:
        print('✅ PASS: Heartbeat updating')
    else:
        print('❌ FAIL: Heartbeat stale')
"
```

**Pass Criteria:**
- ✅ Heartbeat updates every 2-3 minutes (< 120 seconds)
- ✅ Logs show no phase execution (normal off-hours)
- ✅ No CPU spike (idle state)

---

## SECTION 3: TEST PLAN B - DURING MARKET HOURS (10-15 minutes)

**Objective:** Verify autorun executes phases and generates real signals/trades during market hours.

**Time Window:** 9:15 AM - 3:50 PM IST (India market hours)

### Test B1: Pre-Market Phase Execution

```powershell
# Start system 30-60 minutes before market open (9:15 AM)
cd C:\Genesis_System3
.\START_AUTORUN_AND_WATCHDOG.bat
```

**Expected Output (9:00 - 9:15 AM):**
```
PHASE 1: ENVIRONMENT VALIDATION...
PHASE 2: DATA FRESHNESS...
PHASE 3: SAFETY VERIFICATION...
PHASE 4: START WATCHDOG...

Running autorun master with continuous monitoring...
Logs: logs\system3_autorun_master_*.log
Heartbeat: system3_daily_heartbeat.json
```

**Verification (8:50 - 9:10 AM):**
```powershell
# Check for premarket phase execution (201-310)
python -c "
import json
from pathlib import Path

hb_file = Path('system3_daily_heartbeat.json')
if hb_file.exists():
    with hb_file.open() as f:
        hb = json.load(f)
    
    phases = hb.get('phases_executed_today', [])
    print(f'Phases executed so far: {len(phases)}')
    if phases:
        print(f'Latest phases: {phases[-5:]}')
    
    mode = hb.get('system_info', {}).get('mode')
    print(f'Mode: {mode}')
"
```

**Pass Criteria (9:15 AM - Market Open):**
- ✅ Premarket phases (201-310) executed
- ✅ Mode shows "FULLY_AUTONOMOUS"
- ✅ No errors in logs
- ✅ Heartbeat updates every 2-3 minutes

---

### Test B2: Live Execution (During Market)

**Objective:** Verify OP cycles run and generate signals.

**Expected During Market (9:15 AM - 3:50 PM):**
- OP1 (Signal generation): Every 30 minutes
- OP2 (Live loop): Running continuously
- OP3 (Learning): Periodic updates

**Verification (Run every 15 minutes during market):**

```powershell
# Quick health check
python tools/system3_live_runtime_verification.py --verbose

# Expected: All checks ✅ OK or ℹ️ INFO
```

**Detailed Check - Signal Generation:**
```powershell
# Check if signals are being generated
Get-ChildItem C:\Genesis_System3\storage\signals\*.csv -ErrorAction SilentlyContinue | `
  Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-5) } | `
  Select-Object Name, LastWriteTime

# Expected: Recent CSV files (within last 5 minutes)
```

**Detailed Check - Virtual Orders:**
```powershell
python -c "
import json
from datetime import datetime

try:
    with open('storage/virtual_trades.json') as f:
        trades = json.load(f)
    
    if isinstance(trades, list):
        print(f'Virtual trades recorded: {len(trades)}')
        if trades:
            latest = trades[-1]
            print(f'Latest trade: {latest.get(\"symbol\")} {latest.get(\"action\")} @ {latest.get(\"price\")}')
    else:
        print('Virtual trades not in expected format')
except Exception as e:
    print(f'Could not read virtual trades: {e}')
"
```

**Pass Criteria (During Market):**
- ✅ OP cycles running (visible in logs)
- ✅ Signals generated (files update every 30 min)
- ✅ Virtual orders recorded (if in signal generation phase)
- ✅ Heartbeat fresh (< 120 seconds old)
- ✅ No restarts (unless triggered by stale HB)

**If Issues Found:**
- Check: `python tools/system3_live_runtime_verification.py --verbose`
- Check logs: `logs/system3_autorun_master_*.log`
- If hung: Watchdog should auto-restart within 2 minutes

---

### Test B3: Mid-Run Restart (Watchdog Self-Healing)

**Objective:** Verify watchdog detects hangs and restarts master.

**Setup:**
1. Ensure system running during market hours
2. Let it run normally for 5 minutes (establish baseline heartbeat)

**Simulate a Hang:**
```powershell
# Kill the master process (watchdog should detect and restart)
Get-Process python | Where-Object { $_.CommandLine -like "*autorun_master*" } | Stop-Process -Force

# Immediately check watchdog logs
Get-Content logs\system3_watchdog_*.log -Tail 20 | findstr /I "restart"
```

**Expected (Within 2 minutes):**
```
[INFO] Master is NOT running - attempting restart...
[INFO] Master restart successful (total restarts: 1/5)
```

**Verification:**
```powershell
# Check master was restarted
tasklist | findstr python.exe
# Should still show multiple python processes

# Check heartbeat updates after restart
Start-Sleep -Seconds 10
python -c "
import json
from datetime import datetime

with open('system3_daily_heartbeat.json') as f:
    hb = json.load(f)

ts = hb.get('system_info', {}).get('timestamp')
hb_time = datetime.fromisoformat(ts)
age = (datetime.now() - hb_time).total_seconds()
print(f'Heartbeat updated {int(age)}s ago')
print(f'✅ PASS: Watchdog successfully restarted master' if age < 30 else '❌ FAIL: Heartbeat not updating')
"
```

**Pass Criteria:**
- ✅ Watchdog detects master stopped
- ✅ Watchdog restarts master within 2 minutes
- ✅ Heartbeat resumes updating
- ✅ No manual intervention needed

---

## SECTION 4: TEST PLAN C - POST-MARKET SHUTDOWN (5 minutes)

**Objective:** Verify graceful shutdown at EOD.

**Time Window:** After 3:50 PM IST (end of trading day)

**Expected Behavior:**
- Autorun finishes final phases (3:30-4:00 PM)
- Autorun shuts down gracefully at 4:00 PM
- Watchdog sees heartbeat stale (>10 min) → understands graceful shutdown → does NOT restart
- No zombie/orphan processes

**Verification:**
```powershell
# Check shutdown log
Get-Content logs\system3_autorun_master_*.log -Tail 20 | findstr /I "shutdown"

# Expected:
# [INFO] EOD Shutdown: Graceful exit at 16:00:00

# Verify no running processes (or only watchdog remaining)
tasklist | findstr python.exe

# Verify shutdown flag was set
Get-Content system3_shutdown_flag.json
```

**Pass Criteria:**
- ✅ Autorun logs show graceful shutdown
- ✅ Shutdown flag file exists
- ✅ No master process running
- ✅ Watchdog still running (monitoring for next day)

---

## SECTION 5: TEST PLAN D - MULTIPLE RESTARTS (10 minutes)

**Objective:** Verify system can handle repeated start/stop cycles (user restarting during day).

### Test D1: Restart During Market

```powershell
# While system running, stop it
Ctrl+C  # In the BAT window

# Check graceful shutdown
Start-Sleep -Seconds 5

# Restart immediately
.\START_AUTORUN_AND_WATCHDOG.bat
```

**Expected:**
- First startup takes full 30 seconds (all phases)
- Restart is quick (re-activates venv, checks already pass)
- No duplicate processes
- No errors in logs

**Pass Criteria:**
- ✅ Second startup completes without errors
- ✅ No duplicate python processes
- ✅ Heartbeat resumes from restart point (may have 10-30s gap)

---

### Test D2: Verify Restart Caps

**Objective:** Ensure watchdog doesn't restart infinitely if master keeps crashing.

```powershell
# During market hours, kill master multiple times rapidly
for ($i = 1; $i -le 6; $i++) {
    Get-Process python | Where-Object { $_.CommandLine -like "*autorun_master*" } | Stop-Process -Force
    Start-Sleep -Seconds 10
    Write-Host "Killed master (iteration $i)"
}

# After 5 kills, watchdog should stop trying
Get-Content logs\system3_watchdog_*.log -Tail 30 | findstr /I "max restarts"
```

**Expected (After 5 restarts):**
```
[ERROR] Max restarts reached (5) for 2025-12-08. Stopping watchdog.
```

**Pass Criteria:**
- ✅ Watchdog caps restarts at 5 per day
- ✅ Does not loop infinitely
- ✅ Logs reason for stopping

---

## SECTION 6: RUNTIME MONITORING COMMANDS

Use these during/after tests to check system health:

### Quick Status
```powershell
python tools/system3_live_runtime_verification.py
```

### Detailed Status with Report
```powershell
python tools/system3_live_runtime_verification.py --report --verbose
# Creates: SYSTEM3_LIVE_RUNTIME_REPORT.md
```

### Watchdog Status
```powershell
python tools/system3_watchdog_status_reporter.py
# Creates/updates: WATCHDOG_RUNTIME_STATUS.md
```

### Venv Check
```powershell
python tools/system3_venv_sanity_check.py --report
# Creates: VENV_SANITY_STATUS.md
```

### Real-Time Log Monitoring
```powershell
# Watch autorun master log
Get-Content logs\system3_autorun_master_*.log -Wait -Tail 20

# Watch watchdog log
Get-Content logs\system3_watchdog_*.log -Wait -Tail 20
```

---

## SECTION 7: TROUBLESHOOTING DURING TESTS

### Issue: Venv sanity check fails

**Solution:**
1. Check: `VENV_SANITY_STATUS.md`
2. Follow: `VENV_RECOVERY_GUIDE.md`
3. Restart system

---

### Issue: Heartbeat not updating

**Check:**
```powershell
# Is master process alive?
tasklist | findstr "python.exe"

# Is it hung? Check CPU
Get-Process python | Select-Object ProcessName, CPU

# Check log for errors
Get-Content logs\system3_autorun_master_*.log -Tail 50 | findstr /I error
```

**Action:**
- If master gone: Watchdog should restart within 2 minutes
- If master hung: Watchdog should detect stale HB + idle CPU → restart
- If nothing: Check logs for root cause

---

### Issue: Too many python processes

**Check:**
```powershell
tasklist | findstr python.exe
# Should be 2-3, max 4 with one subprocess

# Kill all and restart
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
.\START_AUTORUN_AND_WATCHDOG.bat
```

---

### Issue: Signals not generating

**Check:**
1. Verify market hours: Is it 9:15 AM - 3:50 PM?
2. Check logs for OP2 errors
3. Verify data freshness:
   ```powershell
   Get-Item storage\live\*_snapshot.csv | Select-Object LastWriteTime
   ```
4. If stale: System should auto-refresh via Phase 201 (or manual run)

---

## SECTION 8: SUCCESS CRITERIA (All Tests)

To consider Phase 3 **COMPLETE & PRODUCTION READY**:

- [ ] Test A1: Clean startup works, all phases pass
- [ ] Test A2: Off-hours heartbeat updates normally
- [ ] Test B1: Premarket phases execute correctly
- [ ] Test B2: Live execution generates signals/trades
- [ ] Test B3: Watchdog auto-restarts hung master
- [ ] Test C: EOD shutdown graceful, no orphans
- [ ] Test D1: Restart during market works
- [ ] Test D2: Restart cap prevents infinite loops
- [ ] Runtime monitoring commands work
- [ ] All reports generate without errors

---

## SECTION 9: FINAL SIGN-OFF

After all tests pass:

1. **Collect Evidence:**
   - `VENV_SANITY_STATUS.md` (final check)
   - `WATCHDOG_RUNTIME_STATUS.md` (final status)
   - `SYSTEM3_LIVE_RUNTIME_REPORT.md` (final verification)
   - Screenshots of heartbeat updates
   - Sample logs from `logs/` directory

2. **Document Results:**
   - Create `PHASE3_VERIFICATION_COMPLETE.md` summarizing all tests
   - Note any issues found + how they were resolved
   - Confirm no safety flags were inadvertently changed

3. **Ready for Production:**
   - User can now confidently:
     - Double-click `START_AUTORUN_AND_WATCHDOG.bat` before market
     - System runs autonomously all day
     - Watchdog monitors & self-heals
     - EOD shutdown is graceful
     - Next day, same flow repeats

---

**Test Guide Created:** 2025-12-08  
**Applicable To:** System3 Autorun + Watchdog  
**Expected Duration:** 30-60 minutes for full Phase 3 validation
