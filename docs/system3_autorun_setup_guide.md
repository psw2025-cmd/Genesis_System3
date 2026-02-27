# System3 Autorun Master - Setup Guide

**Status**: ✅ **READY FOR USE**  
**Date**: 2025-12-02

---

## Overview

The System3 Autorun Master provides **100% autonomous full-day automation** for System3 trading operations. It runs completely hands-free, even after laptop restarts.

### Features

- ✅ **Pre-Market**: Runs phases 201-260 automatically
- ✅ **9:15 AM**: Starts DRY-RUN autopilot automatically
- ✅ **Every 30min**: Runs phases 220-260 during market hours
- ✅ **Every 2hr**: Refreshes curated training file
- ✅ **Hourly**: Runs OP1, OP2, OP3 cycles
- ✅ **3:30 PM**: Auto-archives signals
- ✅ **3:35 PM**: Runs EOD learning
- ✅ **4:00 PM**: Auto-shutdown
- ✅ **Watchdog**: Auto-restarts if master dies
- ✅ **Heartbeat**: Updates every 60 seconds
- ✅ **100% DRY-RUN Safe**: Never places real orders

---

## Files Created

1. **`system3_autorun_master.py`** - Main automation script
2. **`start_system3_autorun.bat`** - Batch launcher
3. **`system3_watchdog.py`** - Watchdog monitor
4. **`silent_start.vbs`** - Invisible startup script
5. **`system3_daily_heartbeat.json`** - Heartbeat file (auto-created)

---

## Installation Steps

### Step 1: Install Required Package

```bash
pip install psutil
```

### Step 2: Verify Safety Settings

Ensure all safety flags are disabled:

```python
# config/live_trade_config.py
LIVE_TRADING_ENABLED = False
USE_LIVE_EXECUTION_ENGINE = False

# core/engine/angel_automation_config.py
AUTOMATION_CONFIG.auto_execute_trades = False

# core/config/system3_ultra_safety.json
{
  "AUTO_EXECUTE_TRADES": false
}
```

### Step 3: Test Run (Optional)

Test the master script manually first:

```bash
cd C:\Genesis_System3
venv\Scripts\activate
python system3_autorun_master.py
```

Press Ctrl+C to stop. Verify it runs correctly.

---

## Setup for Auto-Start on Windows Startup

### Method 1: Task Scheduler (Recommended)

1. Open **Task Scheduler** (search "Task Scheduler" in Windows)
2. Click **Create Basic Task**
3. Name: `System3 Autorun Master`
4. Trigger: **When the computer starts**
5. Action: **Start a program**
6. Program: `C:\Genesis_System3\silent_start.vbs`
7. Click **Finish**

### Method 2: Startup Folder

1. Press `Win + R`
2. Type: `shell:startup`
3. Create a shortcut to `C:\Genesis_System3\silent_start.vbs`
4. Rename shortcut to `System3 Autorun`

### Method 3: Registry (Advanced)

1. Press `Win + R`
2. Type: `regedit`
3. Navigate to: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
4. Create new String Value: `System3Autorun`
5. Value data: `C:\Genesis_System3\silent_start.vbs`

---

## Setup Watchdog (Optional but Recommended)

The watchdog ensures the master script restarts if it crashes.

### Option 1: Task Scheduler

1. Create another task: `System3 Watchdog`
2. Trigger: **When the computer starts**
3. Action: Start `C:\Genesis_System3\system3_watchdog.py`
4. Run with highest privileges

### Option 2: Manual Start

```bash
cd C:\Genesis_System3
venv\Scripts\activate
python system3_watchdog.py
```

---

## Daily Schedule

| Time | Action |
|------|--------|
| **Pre-Market** | Run phases 201-260 |
| **9:15 AM** | Start DRY-RUN autopilot |
| **Every 30min** | Run phases 220-260 |
| **Every 2hr** | Refresh curated training file |
| **Every 1hr** | Run OP1, OP2, OP3 cycle |
| **3:30 PM** | Archive signals |
| **3:35 PM** | EOD learning |
| **4:00 PM** | Auto-shutdown |

---

## Monitoring

### Heartbeat File

Check `system3_daily_heartbeat.json` for current status:

```json
{
  "timestamp": "2025-12-02T10:30:00",
  "status": "running",
  "autopilot_running": true,
  "last_phase_run": "2025-12-02T10:00:00",
  "last_curated_refresh": "2025-12-02T09:00:00",
  "last_op_cycle": "2025-12-02T10:00:00"
}
```

### Log Files

- **Master Log**: `logs/system3_autorun_master_YYYYMMDD.log`
- **Watchdog Log**: `logs/system3_watchdog_YYYYMMDD.log`

### Check if Running

```bash
# Check processes
tasklist | findstr python

# Or use PowerShell
Get-Process python | Where-Object {$_.CommandLine -like "*system3_autorun_master*"}
```

---

## Troubleshooting

### Master Not Starting

1. Check `logs/system3_autorun_master_YYYYMMDD.log` for errors
2. Verify virtual environment is activated
3. Check Python path in batch file
4. Verify all safety checks pass

### Watchdog Not Restarting

1. Check `logs/system3_watchdog_YYYYMMDD.log`
2. Verify `psutil` is installed: `pip install psutil`
3. Check if watchdog has permissions to start processes

### Heartbeat Not Updating

1. Check if master script is running
2. Verify write permissions on `system3_daily_heartbeat.json`
3. Check disk space

### Autopilot Not Starting

1. Check if market is open (9:15 AM - 3:30 PM)
2. Verify it's a weekday
3. Check `system3_live_day_autopilot.py` exists
4. Review master log for errors

---

## Safety Guarantees

### ✅ DRY-RUN Only

- All safety checks run before starting
- Autopilot uses DRY-RUN mode only
- No real orders can be placed
- All execution flags are verified disabled

### ✅ Auto-Recovery

- Watchdog restarts master if it crashes
- Heartbeat tracks system health
- Logs all operations for audit

### ✅ Graceful Shutdown

- Auto-shutdown at 4:00 PM
- Cleanly stops autopilot process
- Archives all data before shutdown

---

## Manual Control

### Stop Master

```bash
# Find process
tasklist | findstr python

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Restart Master

```bash
cd C:\Genesis_System3
venv\Scripts\activate
python system3_autorun_master.py
```

### Check Status

```bash
# View heartbeat
type system3_daily_heartbeat.json

# View latest log
type logs\system3_autorun_master_20251202.log | more
```

---

## File Locations

| File | Path |
|------|------|
| Master Script | `C:\Genesis_System3\system3_autorun_master.py` |
| Batch Launcher | `C:\Genesis_System3\start_system3_autorun.bat` |
| Watchdog | `C:\Genesis_System3\system3_watchdog.py` |
| Silent Start | `C:\Genesis_System3\silent_start.vbs` |
| Heartbeat | `C:\Genesis_System3\system3_daily_heartbeat.json` |
| Master Log | `C:\Genesis_System3\logs\system3_autorun_master_YYYYMMDD.log` |
| Watchdog Log | `C:\Genesis_System3\logs\system3_watchdog_YYYYMMDD.log` |

---

## Verification Checklist

Before enabling auto-start:

- [ ] All safety flags verified disabled
- [ ] Test run successful (manual start)
- [ ] Watchdog tested (optional)
- [ ] Heartbeat file created and updating
- [ ] Log files being written
- [ ] Autopilot starts at 9:15 AM
- [ ] Phases run on schedule
- [ ] Shutdown works at 4:00 PM

---

## Support

For issues or questions:
1. Check log files first
2. Review this guide
3. Verify all safety settings
4. Check system requirements

---

**Status**: ✅ **READY FOR PRODUCTION**  
**Last Updated**: 2025-12-02

