# 🔍 Micro-Level Monitor Guide

## Overview

This guide explains how to run and monitor the system at micro-level detail, ensuring everything works correctly without warnings, with all data showing correctly, and with auto-triggers functioning properly.

## Quick Start

### Option 1: Full System Run and Monitor (Recommended)

**File:** `FULL_SYSTEM_RUN_AND_MONITOR.bat`

This is the **complete solution** that:
1. ✅ Starts the trading system automatically
2. ✅ Monitors everything continuously
3. ✅ Checks for warnings/errors
4. ✅ Verifies data updates automatically
5. ✅ Tests auto-triggers
6. ✅ Provides proof everything works

**Usage:**
```batch
FULL_SYSTEM_RUN_AND_MONITOR.bat
```

**What it does:**
- Starts trading system in background window
- Waits 20 seconds for initialization
- Runs micro-level monitoring for 10 minutes
- Shows real-time status of all components
- Generates report at the end

### Option 2: Monitor Only (System Already Running)

**File:** `RUN_SIMPLE_MICRO_MONITOR.bat`

Use this if the trading system is already running.

**Usage:**
```batch
RUN_SIMPLE_MICRO_MONITOR.bat
```

**What it does:**
- Monitors existing system
- Checks files, content, and auto-updates
- Runs until you press Ctrl+C
- Generates report when stopped

### Option 3: Advanced Monitor with Custom Duration

**File:** `scripts\simple_micro_monitor.py`

**Usage:**
```batch
venv\Scripts\python.exe scripts\simple_micro_monitor.py --duration 15 --interval 5
```

**Parameters:**
- `--duration N`: Monitor for N minutes (0 = infinite)
- `--interval N`: Check every N seconds (default: 10)

## What Gets Monitored

### 1. Data Files
- ✅ `chain_raw_live.csv` - Option chain data
- ✅ `pnl_live.json` - Profit/Loss summary
- ✅ `positions_live.json` - Open positions
- ✅ `top_trade_signal.json` - Trade signals

**Checks:**
- File exists
- File is fresh (< 60 seconds old)
- File size is reasonable

### 2. Data Content
- ✅ PnL data structure and values
- ✅ Positions data structure
- ✅ Data validity and completeness

**Checks:**
- JSON files are valid
- Required fields present
- Data values are reasonable

### 3. Auto-Update Triggers
- ✅ Data files update automatically
- ✅ File modification times change
- ✅ File sizes change (data is being written)

**Checks:**
- Monitors file for 7 seconds
- Detects if file is updated
- Verifies auto-trigger is working

### 4. System Components
- ✅ Paper Executor
- ✅ PnL Tracker
- ✅ Trade History Store

**Checks:**
- Components can be imported
- Components initialize correctly
- No errors during initialization

## Monitoring Output

### Example Output

```
[14:30:15 IST] CHECK
--------------------------------------------------------------------------------
[FILES]
  ✅ chain_raw_live.csv: FRESH (3.2s old, 245678 bytes)
  ✅ pnl_live.json: FRESH (2.1s old, 1234 bytes)
  ✅ positions_live.json: FRESH (2.0s old, 567 bytes)
  ✅ top_trade_signal.json: FRESH (1.8s old, 890 bytes)

[CONTENT]
  ✅ PnL: Valid (Total: Rs 1250.50, Trades: 5)
  ✅ Positions: Valid (2 open)

[AUTO-UPDATE]
  [WAIT] Monitoring for 7 seconds...
  ✅ Auto-updating: File updated
     Size: 245678 → 245890 bytes
     Age: 0.5s

  ✅ ALL CHECKS PASSED - NO WARNINGS
```

## Reports

### Report Location
`outputs\micro_monitor_report.json`

### Report Contents
```json
{
  "start_time": "2024-01-15T14:30:00+05:30",
  "end_time": "2024-01-15T14:40:00+05:30",
  "duration_minutes": 10.0,
  "checks_performed": 60,
  "all_passed": true,
  "issues_count": 0
}
```

## Troubleshooting

### Issue: Files are Missing
**Solution:** 
- Ensure trading system is running
- Check if system has initialized (wait 20-30 seconds)
- Verify `outputs` directory exists

### Issue: Files are Stale
**Solution:**
- Check if trading system is still running
- Verify system is fetching data (check logs)
- Restart trading system if needed

### Issue: Data Not Auto-Updating
**Solution:**
- Verify trading system is running
- Check refresh interval (should be 5 seconds)
- Check system logs for errors
- Restart trading system

### Issue: Content Errors
**Solution:**
- Check file permissions
- Verify JSON/CSV files are not corrupted
- Check system logs for data export errors

## Best Practices

1. **Run Full System Monitor First**
   - Use `FULL_SYSTEM_RUN_AND_MONITOR.bat` to ensure everything starts correctly

2. **Monitor for Sufficient Duration**
   - Minimum 5 minutes to catch intermittent issues
   - Recommended 10 minutes for thorough check

3. **Check Reports**
   - Review `micro_monitor_report.json` after monitoring
   - Look for patterns in issues

4. **Fix Issues Immediately**
   - Don't ignore warnings
   - Address issues before they become problems

5. **Regular Monitoring**
   - Run monitor periodically
   - Especially after system changes
   - Before important trading sessions

## Success Criteria

✅ **All checks pass** - No warnings or errors  
✅ **All files fresh** - Data is updating  
✅ **Auto-triggers working** - Files update automatically  
✅ **Data content valid** - All data structures correct  
✅ **Components working** - All system components functional  

## Next Steps

After successful monitoring:
1. ✅ System is ready for production
2. ✅ All components verified
3. ✅ Auto-triggers confirmed working
4. ✅ Data flow validated
5. ✅ No warnings or errors

You can now use the system with confidence!
