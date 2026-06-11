# Auto-Trading Batch Files Guide – December 8, 2025

**Current Time: Monday 09:31:21 AM**  
**Market Status: OPEN (started 9:29 AM)**  
**Mode: DRY-RUN ONLY (NO REAL TRADING)**

---

## 🎯 MAIN ENTRY POINTS FOR AUTO-TRADING

### 1. **PRIMARY: START_AUTORUN_AND_WATCHDOG.bat** ⭐ RECOMMENDED FOR FULL AUTO

**File:** `C:\Genesis_System3\START_AUTORUN_AND_WATCHDOG.bat` (6.66 KB)

**Purpose:** Complete autonomous system with dual process management
- Starts Master process (system3_autorun_master.py)
- Starts Watchdog process (system3_watchdog.py)
- Monitors both processes throughout trading day
- Auto-restarts if either crashes
- Full error recovery

**Use When:** You want full automated trading day with zero manual intervention

**Command:**
```batch
START_AUTORUN_AND_WATCHDOG.bat
```

**What It Does:**
1. Activates venv
2. Launches watchdog in separate window (monitoring process)
3. Launches master in another window (trading automation)
4. Both run simultaneously until 4:00 PM auto-shutdown
5. Handles crash recovery automatically

**Execution Flow:**
```
09:15 AM → Pre-market checks
09:20 AM → Load Ultra models
09:25 AM → Initialize signals
09:30 AM → DRY-RUN autopilot starts
10:00 AM → Phase 220-260 cycle
12:00 PM → Phase refresh
02:00 PM → Phase 220-260 cycle
03:30 PM → Archive signals
03:35 PM → EOD learning
04:00 PM → AUTO-SHUTDOWN
```

---

### 2. **ALTERNATIVE: RESTART_SYSTEM3_AUTORUN.bat** (RESTART ONLY)

**File:** `C:\Genesis_System3\RESTART_SYSTEM3_AUTORUN.bat` (1.33 KB)

**Purpose:** Restart master + watchdog if they crash

**Use When:** System crashed and you need to restart without killing everything

**Command:**
```batch
RESTART_SYSTEM3_AUTORUN.bat
```

**What It Does:**
1. Stops any existing python.exe processes
2. Starts watchdog in new window
3. Starts master in current window
4. Resumes trading automation

---

### 3. **QUICK DAILY: system3_ultra_daily_full.bat** (DAILY CHECK)

**File:** `C:\Genesis_System3\system3_ultra_daily_full.bat` (0.61 KB)

**Purpose:** 10-15 minute full daily review (non-trading)

**Use When:** After market close to check system health

**Command:**
```batch
system3_ultra_daily_full.bat
```

**What It Does:**
1. Runs system3_ultra_master_monitor.ps1 in "full" mode
2. Comprehensive system analysis
3. No trading, just monitoring
4. Good for EOD checklist

---

## 📋 BATCH FILE BREAKDOWN BY CATEGORY

### AUTO-TRADING ORCHESTRATION (START HERE)
| File | Size | Purpose | Status |
|------|------|---------|--------|
| `START_AUTORUN_AND_WATCHDOG.bat` | 6.66 KB | **MAIN ENTRY** – Full auto trading | ✅ PRIMARY |
| `RESTART_SYSTEM3_AUTORUN.bat` | 1.33 KB | Restart crashed processes | ✅ BACKUP |
| `start_system3_autorun.bat` | 0.63 KB | Quick master restart | ✅ LITE |
| `system3_live_day_autopilot.bat` | 0.92 KB | DRY-RUN trading mode | ✅ TESTING |

### MONITORING & HEALTH CHECKS
| File | Size | Purpose | When To Use |
|------|------|---------|------------|
| `system3_ultra_master_monitor.bat` | 0.68 KB | Interactive menu monitor | Mid-day check |
| `system3_ultra_daily_full.bat` | 0.61 KB | Full daily report | EOD summary |
| `system3_ultra_daily_quick.bat` | 0.62 KB | Quick 2min check | Hourly status |
| `system3_ultra_daily_all.bat` | 0.57 KB | Deep analysis | Deep diagnostics |
| `monitor_ultra_system.bat` | 0.62 KB | Ultra models status | Model verification |

### PRE-MARKET & DAILY SETUP
| File | Size | Purpose | When To Use |
|------|------|---------|------------|
| `SYSTEM3_DAILY_START.bat` | 9.36 KB | Full morning startup | 09:00 AM |
| `run_premarket_health_check.bat` | 0.72 KB | Pre-open verification | 09:15 AM |
| `run_monday_premarket.bat` | 0.84 KB | Monday specific checks | Monday 09:15 AM |
| `system3_daily_safety_check.bat` | 2.58 KB | Safety gate verification | Before trading |

### VALIDATION & TESTING
| File | Size | Purpose | Status |
|------|------|---------|--------|
| `run_comprehensive_validation.bat` | 0.33 KB | Full system test | Quick validation |
| `run_full_verification_with_env.bat` | 0.38 KB | Env + system verify | Setup check |
| `run_paper_trading_e2e_test.bat` | 2.54 KB | End-to-end sim | Full simulation |
| `system3_full_validation.bat` | 2.86 KB | Comprehensive check | Before market |

### SIGNAL & DATA MANAGEMENT
| File | Size | Purpose | When To Use |
|------|------|---------|------------|
| `run_clean_signals_and_validate.bat` | 1.85 KB | Clean + validate signals | Daily maintenance |
| `run_post_close_audit.bat` | 0.81 KB | EOD audit | 04:00 PM |
| `system3_verification_checklist.bat` | 4.25 KB | Signal verification | QA check |
| `run_csv_audit.bat` | 0.32 KB | CSV data audit | Data integrity |

### PHASE EXECUTORS
| File | Size | Purpose | Manual Use |
|------|------|---------|------------|
| `run_phases_301_310_diagnostics.bat` | 0.67 KB | Phases 301-310 | Post-market |
| `test_phases_101_130.bat` | 4.79 KB | Phases 101-130 test | Development |
| `test_phases_131_200.bat` | 13.72 KB | Phases 131-200 test | Development |
| `run_phase221.bat` | 0.68 KB | Phase 221 only | Single phase |
| `run_phase222.bat` | 0.68 KB | Phase 222 only | Single phase |

### SIMULATION & DEMO
| File | Size | Purpose | For Learning |
|------|------|---------|--------------|
| `SIMULATE_LIVE_MARKET_DEMO.bat` | 20.32 KB | Full market simulation | Demo/Testing |
| `run_pnl_simulator.bat` | 0.67 KB | PnL calculation sim | Risk analysis |

---

## 🚀 QUICK START - FULL AUTO-TRADING TODAY

### Step 1: Verify System Ready
```batch
system3_daily_safety_check.bat
```
Wait for "✓ SYSTEM READY FOR TRADING" message.

### Step 2: Start Full Auto-Trading
```batch
START_AUTORUN_AND_WATCHDOG.bat
```
This launches TWO windows:
- **Window 1:** Watchdog (monitoring)
- **Window 2:** Master (trading automation)

Both run simultaneously. Leave them open.

### Step 3: Monitor Throughout Day
- Check `system3_daily_heartbeat.json` every 30min
- Or run `system3_ultra_daily_quick.bat` for status

### Step 4: Auto-Shutdown at 4:00 PM
System automatically stops at 4:00 PM.

---

## 📊 TIME-BASED EXECUTION SCHEDULE

**Auto-triggered by Master process (no manual action needed):**

| Time | Action | File | Status |
|------|--------|------|--------|
| **09:15 AM** | Pre-market checks | phase 201-210 | Auto |
| **09:20 AM** | Load Ultra models | phase 215-220 | Auto |
| **09:25 AM** | Initialize signals | phase 220 | Auto |
| **09:30 AM** | **DRY-RUN TRADING STARTS** | autopilot | Auto |
| **Every 30min** | Phase 220-260 cycle | phase cycle | Auto |
| **Every 2hrs** | Curated file refresh | training update | Auto |
| **Every 1hr** | OP1, OP2, OP3 loops | operator cycles | Auto |
| **03:30 PM** | Archive signals | archival phase | Auto |
| **03:35 PM** | EOD learning | phase 394 | Auto |
| **04:00 PM** | **AUTO-SHUTDOWN** | graceful stop | Auto |

---

## ⚠️ SAFETY CHECKLIST

Before running `START_AUTORUN_AND_WATCHDOG.bat`, verify:

- ✅ `LIVE_TRADING_ENABLED = False` (DRY-RUN mode)
- ✅ No real broker connections active
- ✅ venv available at `C:\Genesis_System3\venv\Scripts\python.exe`
- ✅ Phase 390 balanced dataset exists: `storage/datasets/phase_390_balanced_features.csv`
- ✅ Phase 391 XGBoost models exist: `models/xgboost_v1/*.pkl`
- ✅ Phases 201-310 are loadable

**Run quick check:**
```batch
run_premarket_health_check.bat
```

---

## 🔧 IF SOMETHING CRASHES

### Watchdog Crashes
Master will continue running (watchdog is non-critical).

### Master Crashes
Watchdog detects and restarts master automatically.

### Both Crash
Run:
```batch
RESTART_SYSTEM3_AUTORUN.bat
```

### Hung Process
Kill and restart:
```batch
taskkill /F /IM python.exe
START_AUTORUN_AND_WATCHDOG.bat
```

---

## 📝 LOG FILES

All activities logged to:
- `logs/system3_autorun_master_20251208.log` (Master log)
- `logs/system3_watchdog_*.log` (Watchdog log)
- `system3_daily_heartbeat.json` (Health status)

Check logs for errors:
```batch
type logs\system3_autorun_master_20251208.log
```

---

## 📌 SUMMARY

**For full auto-trading today, run ONLY THIS:**

```batch
START_AUTORUN_AND_WATCHDOG.bat
```

**That's it.** The system runs completely autonomous from 09:30 AM to 04:00 PM.

- ✅ No manual intervention needed
- ✅ Watchdog monitors both processes
- ✅ Auto-restarts on crash
- ✅ DRY-RUN safe (no real trading)
- ✅ Auto-shutdown at 4:00 PM
- ✅ Logs saved for review

---

**File Generated:** December 8, 2025, 09:31 AM  
**Market Status:** OPEN ✅  
**Trading Mode:** DRY-RUN (SAFE) ✅  
**Recommended File:** `START_AUTORUN_AND_WATCHDOG.bat` ⭐  

