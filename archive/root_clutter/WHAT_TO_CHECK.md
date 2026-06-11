# 🔍 What To Check - System Not Updating

## Current Issue
Files are showing as **STALE** (not updating). Here's what to check:

## ✅ Step-by-Step Diagnosis

### 1. Check the "Trading System" Window

Look at the **"Administrator: Trading System"** window that was opened. You should see:

**✅ GOOD Signs:**
- Messages like "Fetching data for NIFTY..."
- "Exported X contracts to chain_raw_live.csv"
- "Cycle completed"
- Numbers updating

**❌ BAD Signs:**
- Window is completely blank/black
- Error messages (API errors, connection errors)
- "Stuck" at one message
- No activity for minutes

### 2. Check File Update Status

Run this to check if files are updating:
```batch
CHECK_STATUS_NOW.bat
```

This will:
- Show when files were last modified
- Wait 10 seconds and check if they update
- Tell you if system is working or stuck

### 3. Common Issues and Fixes

#### Issue: Trading System Window is Blank/Black
**Cause:** System may be stuck in initialization or crashed
**Fix:** 
1. Close the "Trading System" window
2. Run `FULL_SYSTEM_RUN_AND_MONITOR.bat` again
3. Wait 30-60 seconds for initialization

#### Issue: API Connection Errors
**Cause:** Broker API connection failed
**Fix:**
1. Check internet connection
2. Verify broker credentials in config
3. System will use virtual data if API fails (may be slower)

#### Issue: Files Update But Very Slowly
**Cause:** Market is closed, system using virtual/simulation data
**Fix:** This is normal - virtual data updates slower than live data

#### Issue: System Stuck at "Initializing..."
**Cause:** WebSocket connection hanging
**Fix:**
1. System should auto-fallback to REST API
2. Wait 30 more seconds
3. If still stuck, restart system

### 4. Quick Fix - Restart System

If files are still not updating after 2-3 minutes:

1. **Close all trading system windows**
2. **Run:** `FULL_SYSTEM_RUN_AND_MONITOR.bat`
3. **Wait 30-60 seconds** for initialization
4. **Check files again** using `CHECK_STATUS_NOW.bat`

## Expected Behavior

### ✅ System Working Correctly:
- Files update every 5 seconds (live data) or 10-30 seconds (virtual data)
- Trading System window shows activity
- No error messages
- Monitor shows "✅ FRESH" for all files

### ⚠️ System Needs Attention:
- Files not updating for 1+ minutes
- Trading System window shows errors
- Monitor shows "⚠️ STALE" warnings

## Next Steps

1. **Run:** `CHECK_STATUS_NOW.bat` to see current status
2. **Check:** Trading System window for errors
3. **If stuck:** Restart with `FULL_SYSTEM_RUN_AND_MONITOR.bat`
4. **Monitor:** Use the monitor to verify everything works
