# System3 December 4, 2025 - Issues and Fixes
**Analysis Date**: December 4, 2025, 7:13 PM IST  
**Market Session**: 9:15 AM - 3:30 PM IST  
**Status**: ⚠️ **SYSTEM STOPPED PREMATURELY**

---

## Executive Summary

The System3 autorun session ran successfully from 7:23 AM until approximately 12:13 PM, when it stopped responding. Two main issues were identified:

1. **Phase 223 (Threshold Optimizer)**: Repeated errors starting at 9:45 AM (5 failures)
2. **System Crash**: Complete system stop around noon (no graceful shutdown)

---

## Issue #1: Phase 223 Threshold Optimizer - Repeated Errors

### Problem
Phase 223 started failing at 9:45 AM and continued to fail in all subsequent runs (5 total failures).

### Root Cause Analysis

**Code Location**: `core/engine/system3_phase223_threshold_optimizer.py`

**Potential Causes**:

1. **File Locking Issue** (Most Likely):
   - Phase 223 reads `angel_index_ai_signals_with_forward.csv`
   - Phase 221 writes to this file every 30 minutes
   - If Phase 221 is writing while Phase 223 tries to read, file may be locked
   - Windows file locking can cause `pd.read_csv()` to fail

2. **Data Type Issue**:
   - Line 78: `score_range = df["final_score"].quantile([0.1, 0.9])`
   - If `final_score` column has mixed types or NaN values, quantile may fail
   - However, this variable is never used, so unlikely to be the issue

3. **Empty DataFrame**:
   - If CSV is empty or corrupted, operations may fail
   - But code has checks for missing columns

### Error Details
- **First Error**: 9:45:59 AM
- **Last Error**: 11:46:27 AM
- **Error Count**: 5 consecutive failures
- **Error Message**: Not logged in detail (only "Phase 223: ERROR")

### Impact
- ⚠️ **Non-Critical**: Other phases continue to run
- ⚠️ **Threshold Optimization**: Not updating during market hours
- ⚠️ **May Affect**: Threshold tuning accuracy

### Fix Required

**Option 1: Add File Lock Retry Logic** (Recommended)
```python
import time
import os

def run_phase223(**kwargs) -> Dict[str, Any]:
    errors = []
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # Check if file is locked
            signals_file = SIGNALS_CSV if SIGNALS_CSV.exists() else ...
            
            # Try to open file exclusively
            try:
                with open(signals_file, 'r') as test_file:
                    pass  # File is readable
            except (PermissionError, IOError):
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return {
                        "phase": 223,
                        "status": "WARN",
                        "details": "Signals file locked, skipping this run",
                        "outputs": {},
                        "errors": [],
                    }
            
            # Load data
            df = pd.read_csv(signals_file, engine="python", on_bad_lines="skip")
            # ... rest of code
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                errors.append(str(e))
                return {
                    "phase": 223,
                    "status": "ERROR",
                    "details": f"Phase 223 failed after {max_retries} attempts: {e}",
                    "outputs": {},
                    "errors": errors,
                }
```

**Option 2: Better Error Logging**
```python
except Exception as e:
    import traceback
    error_details = traceback.format_exc()
    logger.error(f"Phase 223 error: {error_details}")
    return {
        "phase": 223,
        "status": "ERROR",
        "details": f"Phase 223 failed: {e}",
        "outputs": {},
        "errors": [str(e), error_details],
    }
```

**Option 3: Skip Unused Code**
```python
# Line 78 - Remove unused quantile calculation
# score_range = df["final_score"].quantile([0.1, 0.9])  # REMOVED - never used
```

---

## Issue #2: System Crash - Complete Stop

### Problem
System stopped responding around 12:13 PM (last heartbeat update). No graceful shutdown occurred.

### Timeline
- **Last Phase Run**: 11:46:27 AM
- **Last Heartbeat**: 12:13:07 PM
- **Market Close**: 3:30 PM (missed)
- **Scheduled Shutdown**: 4:00 PM (missed)

### Root Cause Analysis

**Possible Causes**:

1. **Python Process Crash** (Most Likely):
   - No exception logged in autorun master log
   - Process may have been killed by OS or crashed silently
   - Could be memory exhaustion, segmentation fault, or unhandled exception

2. **Watchdog Not Detecting Crash**:
   - Watchdog log shows only 6 entries (startup only)
   - Watchdog should check every 60 seconds
   - Should have detected stale heartbeat (> 3 minutes)
   - But crash occurred at 12:13 PM, which is **after market hours** (market closes 3:30 PM)
   - Watchdog only restarts during market hours (9:15 AM - 4:00 PM)
   - **Wait**: 12:13 PM is still during market hours! Watchdog should have restarted.

3. **Network/API Issue**:
   - SmartAPI connection may have been lost
   - Autopilot may have hung waiting for API response
   - No timeout handling

4. **Resource Exhaustion**:
   - Memory leak
   - File handle leak
   - Too many open connections

### Watchdog Behavior Issue

**Code Location**: `system3_watchdog.py`

**Expected Behavior**:
- Check every 60 seconds
- Detect if master process is running
- Detect if heartbeat is stale (> 3 minutes)
- Restart master if needed (during market hours)

**Actual Behavior**:
- Only 6 log entries (startup only)
- No monitoring activity logged
- Did not detect crash
- Did not restart master

**Possible Issues**:
1. Watchdog loop may have crashed silently
2. Watchdog may not be logging monitoring activity
3. Watchdog may have stopped checking

### Fix Required

**Option 1: Enhanced Watchdog Logging**
```python
def check_master():
    """Check if master is running."""
    logger.info(f"[{datetime.now()}] Checking master status...")
    
    if not is_master_running():
        logger.warning("Master process not found!")
        if is_market_hours():
            logger.info("Market hours - attempting restart...")
            start_master()
        else:
            logger.info("Outside market hours - not restarting")
    
    # Check heartbeat staleness
    heartbeat_age = check_heartbeat_staleness()
    if heartbeat_age > 180:  # 3 minutes
        logger.warning(f"Heartbeat stale: {heartbeat_age} seconds old")
        if is_market_hours():
            logger.info("Market hours - attempting restart...")
            start_master()
```

**Option 2: Add Process Monitoring**
```python
import psutil

def is_master_running():
    """Check if master process is running."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'system3_autorun_master.py' in ' '.join(cmdline):
                # Check if process is actually responsive
                if proc.is_running() and proc.status() == psutil.STATUS_RUNNING:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False
```

**Option 3: Add Crash Detection**
```python
def check_crash_logs():
    """Check for Python crash logs."""
    crash_logs = list(Path("logs").glob("crash_*.log"))
    if crash_logs:
        logger.error(f"Found crash logs: {crash_logs}")
        return True
    return False
```

---

## Recommendations

### Immediate Actions (Before Next Market Day)

1. **Fix Phase 223**:
   - Add file lock retry logic
   - Add better error logging
   - Remove unused code (quantile calculation)
   - Test Phase 223 independently

2. **Fix Watchdog**:
   - Add detailed logging for monitoring activity
   - Verify heartbeat staleness detection works
   - Test restart logic
   - Ensure watchdog continues running even if master crashes

3. **Add Crash Detection**:
   - Add Python crash logging
   - Check Windows Event Viewer for system errors
   - Monitor system resources (memory, CPU)

4. **Test Before Next Market Day**:
   - Run Phase 223 independently
   - Test watchdog restart logic
   - Verify heartbeat updates correctly
   - Test graceful shutdown at 4:00 PM

### Long-Term Improvements

1. **Enhanced Error Handling**:
   - Add retry logic for all file operations
   - Better exception handling and logging
   - Graceful degradation on errors

2. **Improved Monitoring**:
   - Add system resource monitoring
   - Alert on system hangs
   - Better crash detection

3. **Resilience**:
   - Make all phases more resilient to failures
   - Add timeout handling for API calls
   - Better cleanup on exit

---

## Testing Plan

### Phase 223 Fix Testing
```bash
# Test Phase 223 independently
python core/engine/system3_phase223_threshold_optimizer.py

# Test with locked file (simulate)
# Run Phase 221 and Phase 223 simultaneously
```

### Watchdog Testing
```bash
# Test watchdog restart logic
# 1. Start watchdog
# 2. Start autorun master
# 3. Kill autorun master process
# 4. Verify watchdog detects and restarts
```

### System Crash Testing
```bash
# Test graceful shutdown
# 1. Start autorun system
# 2. Wait until 4:00 PM
# 3. Verify shutdown flag is written
# 4. Verify clean exit
```

---

## Files Modified

1. `core/engine/system3_phase223_threshold_optimizer.py` - Add retry logic, better error handling
2. `system3_watchdog.py` - Enhanced logging, better crash detection
3. `system3_autorun_master.py` - Better exception handling, crash recovery

---

## Status

- ⚠️ **Phase 223**: Needs fix (file locking issue)
- ⚠️ **Watchdog**: Needs fix (not detecting crashes)
- ⚠️ **System Crash**: Needs investigation (root cause unknown)

**Next Steps**: Implement fixes and test before next market day.

---

**Document Created**: December 4, 2025, 7:13 PM IST  
**Status**: ⚠️ **FIXES REQUIRED BEFORE NEXT MARKET DAY**

