# 🚀 RUN_FULL_SYSTEM_PRODUCTION.bat - Complete System Runner

## Overview

This is a **production-grade batch file** that orchestrates the complete Genesis System3 trading system in the correct sequence:

1. ✅ **Environment Validation** - Checks Python, venv, requirements
2. ✅ **Pre-Flight Checks** - Market hours, API credentials
3. ✅ **Backtesting** - Runs historical backtests (if data available)
4. ✅ **Paper Trading** - Starts live paper trading with real data
5. ✅ **Monitoring** - Real-time status, PnL, positions, signals

---

## 🎯 Usage

### **Basic Usage (Default Settings)**
```batch
RUN_FULL_SYSTEM_PRODUCTION.bat
```

**Default Configuration:**
- Refresh Interval: 5 seconds
- No max cycles (runs until stopped)
- No duration limit (runs until stopped)

### **With Custom Parameters**
```batch
RUN_FULL_SYSTEM_PRODUCTION.bat [REFRESH] [MAX_CYCLES] [DURATION]
```

**Examples:**
```batch
REM Run with 10-second refresh, max 100 cycles, 60 minutes duration
RUN_FULL_SYSTEM_PRODUCTION.bat 10 100 60

REM Run with 5-second refresh, unlimited cycles, 30 minutes duration
RUN_FULL_SYSTEM_PRODUCTION.bat 5 "" 30

REM Run with 3-second refresh, unlimited cycles, unlimited duration
RUN_FULL_SYSTEM_PRODUCTION.bat 3
```

**Parameters:**
- `REFRESH` - Refresh interval in seconds (default: 5)
- `MAX_CYCLES` - Maximum number of cycles (default: unlimited)
- `DURATION` - Run duration in minutes (default: unlimited)

---

## 📋 What It Does

### **Phase 1: Environment Validation**
- ✅ Checks Python installation
- ✅ Creates/activates virtual environment
- ✅ Installs/verifies requirements
- ✅ Checks critical files exist

### **Phase 2: Pre-Flight Checks**
- ✅ Checks market hours (OPEN/CLOSED)
- ✅ Verifies API credentials
- ✅ Validates configuration files

### **Phase 3: Backtesting**
- ✅ Checks for historical data
- ✅ Runs synthetic backtester (if available)
- ✅ Runs strategy backtester (if available)
- ✅ Generates backtest reports

**Note:** Backtesting only runs if historical data is available in `storage/live/angel_index_ai_signals_with_forward.csv`

### **Phase 4: Initialize Data Files**
- ✅ Creates PnL tracking file
- ✅ Creates positions file
- ✅ Creates health status file

### **Phase 5: Start Paper Trading**
- ✅ Stops any existing processes
- ✅ Starts paper trading system in background
- ✅ Waits for initialization
- ✅ Verifies system is running

### **Phase 6: Monitoring**
- ✅ Real-time system status
- ✅ PnL summary (total, realized, unrealized)
- ✅ Open positions count
- ✅ Top trade signal
- ✅ Process health check
- ✅ Auto-refresh every 5 seconds

---

## 📊 Output Files

### **Logs**
- `logs/full_system_YYYYMMDD_HHMMSS.log` - Main system log
- `logs/paper_trading_YYYYMMDD_HHMMSS.log` - Paper trading log

### **Status Files**
- `outputs/health.json` - System health status
- `outputs/pnl_live.json` - PnL tracking
- `outputs/positions_live.json` - Open positions
- `outputs/top_trade_signal.json` - Current best signal

### **Backtest Results** (if backtesting runs)
- `storage/backtest/angel_backtest_trades_detailed.csv`
- `storage/backtest/angel_backtest_summary.csv`

---

## 🔧 Features

### **Production-Grade Features:**
- ✅ **Error Handling** - Graceful error handling at each phase
- ✅ **Logging** - Comprehensive logging to file and console
- ✅ **Process Management** - Stops existing processes before starting
- ✅ **Status Monitoring** - Real-time status updates
- ✅ **Clean Shutdown** - Proper cleanup on exit
- ✅ **Market Hours Detection** - Auto-detects market status
- ✅ **Background Execution** - Paper trading runs in background
- ✅ **Health Checks** - Verifies system is running correctly

### **Safety Features:**
- ✅ **Paper Trading Only** - No live trading (safety enforced)
- ✅ **Process Verification** - Checks if processes are running
- ✅ **Graceful Shutdown** - Clean exit on Ctrl+C
- ✅ **Error Recovery** - Continues even if backtesting fails

---

## 🎮 Controls

### **During Monitoring:**
- **Ctrl+C** - Stop monitoring (system continues in background)
- **Close Window** - Stop everything (cleanup runs automatically)

### **To Stop Paper Trading:**
1. Close the "Paper Trading Engine" window, OR
2. Run: `taskkill /F /FI "WINDOWTITLE eq Paper Trading Engine*"`

---

## 📈 Monitoring Display

The monitoring screen shows:

```
====================================================================
  GENESIS SYSTEM3 - LIVE MONITOR
  [Date] [Time]
====================================================================

[SYSTEM STATUS]
-------------------------------------------------------------------
Status: RUNNING
Cycles Completed: 42
Data Fetch Success Rate: 98.5%

[PNL SUMMARY]
-------------------------------------------------------------------
Total PnL: 1250.50
Realized: 800.25
Unrealized: 450.25
Trades: 15
Win Rate: 73.3%

[OPEN POSITIONS]
-------------------------------------------------------------------
Open Positions: 3

[TOP SIGNAL]
-------------------------------------------------------------------
Action: TRADE
Strategy: IRON_CONDOR
Confidence: 85.2%
```

---

## ⚠️ Prerequisites

1. **Python 3.8+** installed and in PATH
2. **Virtual Environment** (will be created if missing)
3. **Requirements** installed (will be installed if missing)
4. **API Credentials** in `config/.env` (for live data)
5. **Historical Data** (optional, for backtesting)

---

## 🔍 Troubleshooting

### **System Won't Start**
- Check Python is installed: `python --version`
- Check virtual environment: `venv\Scripts\python.exe --version`
- Check requirements: `pip list`

### **Backtesting Not Running**
- Check if historical data exists: `storage\live\angel_index_ai_signals_with_forward.csv`
- Backtesting is optional - system will continue without it

### **Paper Trading Not Starting**
- Check logs: `logs\paper_trading_*.log`
- Check API credentials: `config\.env`
- Check market hours (system works in off-hours too)

### **No Data Being Fetched**
- Verify API credentials are correct
- Check internet connection
- Check market hours (if market is closed, system will wait)

---

## 📝 Example Session

```batch
C:\Genesis_System3> RUN_FULL_SYSTEM_PRODUCTION.bat 5 100 60

====================================================================
  GENESIS SYSTEM3 - PRODUCTION FULL SYSTEM RUNNER
====================================================================

[PHASE 1/6] ENVIRONMENT VALIDATION
[OK] Python found
[OK] Virtual environment activated
[OK] Requirements verified

[PHASE 2/6] PRE-FLIGHT CHECKS
[OK] Market is OPEN - Will use live data
[OK] API credentials found

[PHASE 3/6] BACKTESTING
[INFO] Historical signals found - Running backtest...
[OK] Synthetic backtest completed
[OK] Strategy backtest completed

[PHASE 4/6] INITIALIZE DATA FILES
[OK] Data files initialized

[PHASE 5/6] STARTING PAPER TRADING SYSTEM
[OK] Paper trading system started

[PHASE 6/6] MONITORING AND STATUS
====================================================================
  LIVE SYSTEM MONITOR - LIVE MODE
====================================================================

[SYSTEM STATUS]
Status: RUNNING
Cycles: 1

[PNL SUMMARY]
Total PnL: 0.00
Trades: 0

...
```

---

## ✅ Status

**Production-Ready:** ✅ Yes  
**Error Handling:** ✅ Comprehensive  
**Logging:** ✅ Full logging  
**Monitoring:** ✅ Real-time  
**Backtesting:** ✅ Integrated  
**Paper Trading:** ✅ Enabled  
**Safety:** ✅ Paper trading only (no live trades)

---

**Created:** 2026-02-04  
**Version:** 1.0.0  
**Status:** Production Ready
