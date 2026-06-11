# BATCH FILES QUICK REFERENCE - OPERATOR CHEAT SHEET

**Last Updated:** December 6, 2025  
**System:** Genesis System3 AI Trading (Paper Trading Only)

---

## 🚀 QUICK START (3 Steps)

### Step 1: Pre-Market Safety Check (8:00 AM IST)
```batch
c:\Genesis_System3\system3_daily_safety_check.bat
```
**What it does:**
- Validates 3 critical safety checks (threshold sanity, signal dry-run, engine self-test)
- Exits 0 if SAFE; exits 1 if BLOCKED
- Takes ~2-3 minutes

**Expected Output:**
```
[1/3] Running static threshold sanity check...
[2/3] Running pre-market signal dry-run...
[3/3] Running signal engine self-test...

ALL CHECKS PASSED - SAFE TO START MARKET SESSION
You can now run: START_AUTORUN_AND_WATCHDOG.bat
```

**If it FAILS:** Fix reported issue, re-run until PASS

---

### Step 2: Launch System (8:15 AM IST - RIGHT AFTER PASS)
```batch
c:\Genesis_System3\START_AUTORUN_AND_WATCHDOG.bat
```
**What it does:**
- ✅ Validates virtual environment
- ✅ Auto-installs missing dependencies
- ✅ Checks data freshness (auto-heals if stale)
- ✅ Verifies DRY-RUN mode (paper trading only)
- ✅ Spawns watchdog in NEW window (monitors autorun)
- ✅ Launches autorun master (trading engine)

**Two Windows Will Open:**
- **Window 1:** "System3 Watchdog" (monitoring window)
- **Window 2:** Current window with autorun master running

**Expected Output:**
```
PHASE 1: ENVIRONMENT VALIDATION AND AUTO-REPAIR ... OK
PHASE 2: DATA FRESHNESS & AUTO-HEAL HOOK ... OK
PHASE 3: SAFETY VERIFICATION (DRY-RUN) ... OK
PHASE 4: START WATCHDOG (NEW WINDOW) ... OK
PHASE 5: LAUNCH AUTORUN MASTER

Running autorun master with continuous monitoring...
Logs: logs\system3_autorun_master_*.log
Heartbeat: system3_daily_heartbeat.json
Press Ctrl+C here for graceful stop.
```

**Keep Both Windows Open** during trading session (9:15 AM - 3:30 PM IST)

---

### Step 3: Monitor & Log (During Trading 9:15 AM - 3:30 PM IST)
```batch
REM Check logs (inside venv from any terminal):
dir logs\system3_autorun_master_*.log

REM View heartbeat (every 60 seconds):
type system3_daily_heartbeat.json | more

REM Check freshness (manual check):
python check_heartbeat_freshness.py
```

**Expected Heartbeat Output:**
```json
{
  "_version": "2.0.0",
  "_last_updated": "2025-12-06T13:45:23.456Z",
  "system_info": { ... },
  "ai_controller": { ... },
  "phase_registry": { "total_phases": 257, "phase_range": "31-330" },
  ...
}
```

---

## ⏹️ SHUTDOWN (3:30 PM IST)

### Graceful Stop:
```
In Window 2 (autorun master): Press Ctrl+C
```

Expected:
```
^C
[Interrupt] Stopping gracefully...
================================================================================
AUTORUN MASTER STOPPED
================================================================================
OK Shutdown complete. Review logs if needed.
```

Then:
- **Window 2** closes automatically
- **Window 1** (watchdog) closes automatically
- Both log files saved to `logs\` folder

### Force Stop (if needed):
```
Alt+F4 both windows, or:
taskkill /im python.exe /f
```

---

## 📋 FILE REFERENCE

### ✅ KEEP (Active Production Files)

| File | Purpose | When | Command |
|------|---------|------|---------|
| `system3_daily_safety_check.bat` | Pre-market gating (3 checks) | 08:00 AM | `system3_daily_safety_check.bat` |
| `START_AUTORUN_AND_WATCHDOG.bat` | Production launcher | 08:15 AM | `START_AUTORUN_AND_WATCHDOG.bat` |
| `heartbeat_maintenance.bat` | Scheduled monitoring | Via Windows Task Scheduler | (automatic) |

### ⚠️ DEPRECATED (Archive Only - Do NOT Use)

| File | Reason | Replacement |
|------|--------|-------------|
| `SYSTEM3_DAILY_START.bat` | Overlaps 80% with master launcher | `START_AUTORUN_AND_WATCHDOG.bat` |
| `start_system3_autorun.bat` | Missing preflight checks; no watchdog | `START_AUTORUN_AND_WATCHDOG.bat` |
| `start_system3_env.bat` | Old pattern; launches manual menu only | `START_AUTORUN_AND_WATCHDOG.bat` |

---

## 🔧 TROUBLESHOOTING

### Problem: "ERROR: Virtual environment not found"
**Solution:**
```batch
cd C:\Genesis_System3
python -m venv venv
Re-run START_AUTORUN_AND_WATCHDOG.bat
```

### Problem: "ERROR: Failed to install [package]"
**Solution:**
```batch
REM Manually install:
C:\Genesis_System3\venv\Scripts\python.exe -m pip install psutil pandas numpy joblib python-dotenv

REM Retry launcher
START_AUTORUN_AND_WATCHDOG.bat
```

### Problem: "ERROR: System NOT in DRY-RUN mode"
**Solution:**
```batch
REM Check .env file:
type .env

REM Ensure:
LIVE_TRADING_ENABLED=False

REM Retry launcher
START_AUTORUN_AND_WATCHDOG.bat
```

### Problem: "Heartbeat freshness check failed"
**Solution:**
```batch
REM Check file exists:
dir system3_daily_heartbeat.json

REM Check age (should be < 180 seconds):
C:\Genesis_System3\venv\Scripts\python.exe check_heartbeat_freshness.py

REM If missing, restart system:
START_AUTORUN_AND_WATCHDOG.bat
```

### Problem: "Watchdog window won't open"
**Solution:**
```batch
REM Check logs for errors:
dir /O-D logs\

REM View latest log:
type logs\system3_watchdog_*.log

REM Verify system3_watchdog.py exists:
dir system3_watchdog.py
```

### Problem: "Autorun master crashed"
**Solution:**
- Watchdog should auto-restart within 10 seconds
- Check watchdog window for restart message
- If watchdog also crashed, manually restart:
  ```batch
  START_AUTORUN_AND_WATCHDOG.bat
  ```

---

## 📊 MONITORING COMMANDS (During Trading)

### Check Heartbeat Freshness (Should be < 180s old)
```batch
C:\Genesis_System3\venv\Scripts\python.exe check_heartbeat_freshness.py
```
**Success:** `✅ Heartbeat fresh: age=42s threshold=180s`  
**Failure:** `❌ Heartbeat stale: age=241s threshold=180s` → Watchdog should restart

### View Latest Heartbeat
```batch
type system3_daily_heartbeat.json | more
```

### View Trading Logs
```batch
type logs\system3_autorun_master_*.log | more
```

### View Phase Progress
```batch
C:\Genesis_System3\venv\Scripts\python.exe -c "import json; hb=json.load(open('system3_daily_heartbeat.json')); print(f\"Phase {hb['phase_registry']['current_phase']} of {hb['phase_registry']['complete']}\")"
```

### Check System Health
```batch
C:\Genesis_System3\venv\Scripts\python.exe -c "import json; hb=json.load(open('system3_daily_heartbeat.json')); print(f\"CPU: {hb['health_monitoring']['cpu_percent']}% | Memory: {hb['health_monitoring']['memory_mb']} MB | Disk: {hb['health_monitoring']['disk_free_gb']} GB\")"
```

---

## 🛡️ SAFETY FEATURES

### DRY-RUN (Paper Trading) Mode
- **Always enforced** by START_AUTORUN_AND_WATCHDOG.bat
- Checks `LIVE_TRADING_ENABLED=False` from `.env`
- **Exits 1 if LIVE mode detected** – system won't start

### Watchdog Monitoring
- Runs in separate window
- Automatically restarts autorun if it crashes
- Checks heartbeat freshness every 10 seconds
- Alerts on stale heartbeat (> 180s old)

### Continuous Heartbeat
- Updates every 60 seconds (HEARTBEAT_CONTINUOUS=1)
- Includes 100+ fields: system info, AI controller state, phases, health metrics
- v2.0.0 schema frozen; 21 required sections validated

### Pre-Market Gating
- `system3_daily_safety_check.bat` runs 3 sequential checks
- Must PASS all 3 before system startup
- **DO NOT** start trading session if any check fails

---

## 📈 PERFORMANCE EXPECTATIONS

| Metric | Expected | Threshold |
|--------|----------|-----------|
| Startup time | 30-60 seconds | < 120s |
| Heartbeat update interval | 60 seconds | < 120s |
| Watchdog restart latency | 5-10 seconds | < 30s |
| System CPU usage | 5-15% | < 50% |
| System memory usage | 200-500 MB | < 2 GB |
| Disk I/O (logs) | ~10 MB/day | < 100 MB/week |
| Heartbeat file size | 50-150 KB | < 1 MB |

---

## 📝 LOG LOCATIONS

```
Logs Directory: c:\Genesis_System3\logs\

Key Log Files:
├─ system3_autorun_master_YYYY-MM-DD_HHMM.log
├─ system3_watchdog_YYYY-MM-DD_HHMM.log
├─ system3_daily_start_YYYY-MM-DD_HHMM.log
├─ phase_*.log (individual phase logs)
└─ errors_*.log (error summary)

Heartbeat Archive:
└─ storage\heartbeat_archive\heartbeat_YYYY-MM-DD_HHMM.json
```

---

## 🔄 WINDOWS TASK SCHEDULER (Optional)

### Setup Heartbeat Monitoring (Every 5 Minutes)
```batch
REM Run this once in admin PowerShell:
schtasks /create /tn "System3\Heartbeat-Freshness" /tr "C:\Genesis_System3\heartbeat_maintenance.bat" /sc minute /mo 5
```

### Setup Heartbeat Archive (Every Hour)
```batch
schtasks /create /tn "System3\Heartbeat-Archive" /tr "C:\Genesis_System3\heartbeat_maintenance.bat" /sc hour
```

### View Scheduled Tasks
```batch
schtasks /query /tn "System3\*" /v
```

### Disable a Task
```batch
schtasks /change /tn "System3\Heartbeat-Freshness" /disable
```

---

## ❓ FREQUENTLY ASKED QUESTIONS

### Q: Do I need to run both safety_check and START_AUTORUN_AND_WATCHDOG?
**A:** YES. Always run `system3_daily_safety_check.bat` first (pre-market gating), then `START_AUTORUN_AND_WATCHDOG.bat` (production startup). Safety checks prevent dangerous configurations from entering trading.

### Q: Can I run START_AUTORUN_AND_WATCHDOG without safety_check?
**A:** Technically yes, but **NOT RECOMMENDED**. Safety checks are critical gating. Always run them first.

### Q: What if safety_check fails?
**A:** Fix the reported issue (e.g., invalid thresholds, broken signal engine), then re-run until PASS before starting trader.

### Q: Why are there two windows?
**A:** 
- **Watchdog window:** Monitors autorun, auto-restarts if crashed, alerts on stale heartbeat
- **Autorun window:** Runs trading engine, logs all activity, updates heartbeat every 60s

Both must stay open during trading hours.

### Q: How do I stop the system gracefully?
**A:** Press `Ctrl+C` in the autorun master window (the one with active logs). Watchdog auto-closes 10 seconds later.

### Q: Can I run multiple instances?
**A:** NO. One instance per system. Multiple instances share same heartbeat file and will conflict.

### Q: What's the heartbeat for?
**A:** Central monitoring hub: system health, AI controller state, phase progress, market context, error tracking. Updated every 60s. Checked by watchdog for freshness (must be < 180s old).

### Q: Can I schedule automatic startup?
**A:** YES, use Windows Task Scheduler. Recommend scheduling START_AUTORUN_AND_WATCHDOG.bat at 08:15 AM every trading day. Heartbeat monitoring already optional via heartbeat_maintenance.bat.

### Q: How do I view past trades/signals?
**A:** Check logs directory:
```batch
dir /O-D logs\
type logs\system3_autorun_master_YYYY-MM-DD_HHMM.log | more
```

### Q: What's "DRY-RUN"?
**A:** Paper trading mode. No real money is traded. Safety check enforced by START_AUTORUN_AND_WATCHDOG.bat ensures LIVE_TRADING_ENABLED=False before starting.

---

## 📞 SUPPORT

For detailed analysis, see: `BATCH_FILES_MICRO_ANALYSIS.md`  
For phase references, see: `PHASE_GAPS_ANALYSIS.md`  
For validation results, see: `VALIDATION_REPORT.md`

---

**END OF QUICK REFERENCE**
