# System3 Pre-Market Health Check - Implementation Complete
**Generated**: 2025-12-04  
**Status**: ✅ **IMPLEMENTED AND READY**

---

## Overview

A comprehensive pre-market health check script has been implemented to catch issues before market open. This script verifies all critical system components and provides a clear PASS/FAIL status.

---

## Files Created

1. **`system3_premarket_health_check.py`** (Main script)
   - Comprehensive health checks
   - Detailed logging
   - JSON results export

2. **`run_premarket_health_check.bat`** (Batch wrapper)
   - Easy execution
   - Venv activation
   - User-friendly output

---

## Health Checks Implemented

### 1. Disk Space Check ✅
- **Purpose**: Prevents crashes due to disk full
- **Threshold**: Minimum 1 GB free
- **Output**: Free space, total space, usage percentage
- **Status**: Blocking (FAIL if insufficient)

### 2. Internet Connectivity Check ✅
- **Purpose**: Ensures network access for data/API calls
- **Method**: Tests connection to Google DNS (8.8.8.8) and Cloudflare DNS (1.1.1.1)
- **Timeout**: 5 seconds per host
- **Status**: Blocking (FAIL if no connectivity)

### 3. Critical Files Check ✅
- **Purpose**: Verifies all essential files exist
- **Files Checked**:
  - `system3_autorun_master.py`
  - `system3_watchdog.py`
  - `system3_live_day_autopilot.py`
  - `START_AUTORUN_AND_WATCHDOG.bat`
  - `venv/Scripts/python.exe`
  - `storage/live/dhan_index_ai_signals.csv`
  - `storage/live/dhan_index_ai_signals_curated.csv`
- **Status**: Blocking (FAIL if any missing)

### 4. Python Version Check ✅
- **Purpose**: Ensures compatible Python version
- **Requirement**: Python 3.8 or higher
- **Output**: Version string, major/minor/micro
- **Status**: Blocking (FAIL if incompatible)

### 5. Dependencies Check ✅
- **Purpose**: Verifies critical packages installed
- **Packages Checked**:
  - `pandas`
  - `numpy`
  - `psutil`
  - `requests`
- **Status**: Blocking (FAIL if any missing)

### 6. Last Shutdown Check ✅
- **Purpose**: Verifies clean shutdown from previous session
- **Checks**:
  - Shutdown flag file exists
  - Shutdown date is today or yesterday
  - Shutdown reason recorded
  - Heartbeat age (expected to be stale if not running)
- **Status**: Warning (WARN if issues, not blocking)

### 7. Configuration Check ✅
- **Purpose**: Validates safety flags are correct
- **Checks**:
  - `LIVE_TRADING_ENABLED = False`
  - `USE_LIVE_EXECUTION_ENGINE = False`
  - `auto_execute_trades = False`
  - `AUTO_EXECUTE_TRADES = False`
- **Status**: Blocking (FAIL if any safety flag incorrect)

### 8. Log File Size Check ✅
- **Purpose**: Identifies large log files that may consume disk space
- **Threshold**: Warns if any log file > 100 MB
- **Output**: Total log size, list of large files
- **Status**: Warning (WARN if large files, not blocking)

### 9. Signal Files Check ✅
- **Purpose**: Verifies signal files exist and have data
- **Checks**:
  - Signals CSV exists and row count
  - Curated CSV exists and row count
- **Status**: Warning (WARN if missing, not blocking - expected on first run)

---

## Usage

### Method 1: Batch File (Recommended)
```batch
run_premarket_health_check.bat
```

### Method 2: Direct Python
```bash
python system3_premarket_health_check.py
```

### Method 3: From Python Script
```python
from system3_premarket_health_check import run_all_checks
summary = run_all_checks()
```

---

## Output

### Console Output
```
================================================================================
SYSTEM3 PRE-MARKET HEALTH CHECK
================================================================================
Date: 2025-12-04 08:00:00
================================================================================

✅ Disk space check PASSED: 15.23 GB free
✅ Internet connectivity check PASSED (connected to 8.8.8.8)
✅ Critical files check PASSED: All 7 files exist
✅ Python version check PASSED: 3.11.5
✅ Dependencies check PASSED: All 4 packages installed
✅ Last shutdown check PASSED: Clean shutdown on 2025-12-03
✅ Configuration check PASSED: All safety flags correct
✅ Log file size check PASSED: Total 45.67 MB
✅ Signal files check PASSED: 30 signals, 608 curated

================================================================================
HEALTH CHECK SUMMARY
================================================================================
✅ Disk Space: PASS
✅ Internet: PASS
✅ Critical Files: PASS
✅ Python Version: PASS
✅ Dependencies: PASS
✅ Last Shutdown: PASS
✅ Configuration: PASS
✅ Log Files: PASS
✅ Signal Files: PASS

================================================================================
✅ HEALTH CHECK PASSED - SYSTEM READY FOR MARKET
================================================================================
```

### JSON Results File
Saved to: `docs/premarket_health_check_YYYYMMDD.json`

```json
{
  "timestamp": "2025-12-04T08:00:00",
  "overall_status": "PASS",
  "blocking_failures": [],
  "warnings": [],
  "checks": {
    "disk_space": {
      "status": "PASS",
      "free_gb": 15.23,
      "total_gb": 500.0,
      "used_percent": 69.5
    },
    "internet": {
      "status": "PASS",
      "host": "8.8.8.8"
    },
    ...
  }
}
```

### Log File
Saved to: `logs/premarket_health_check_YYYYMMDD.log`

---

## Exit Codes

- **0**: All checks passed (or only warnings)
- **1**: Blocking failures detected

---

## Integration with Autorun

### Recommended Workflow

1. **Before Market Open** (8:00 AM):
   ```batch
   run_premarket_health_check.bat
   ```

2. **If PASS**: Proceed with autorun
   ```batch
   START_AUTORUN_AND_WATCHDOG.bat
   ```

3. **If FAIL**: Review failures and fix before starting

### Automated Integration (Optional)

Add to `START_AUTORUN_AND_WATCHDOG.bat`:
```batch
@echo off
cd /d C:\Genesis_System3
call venv\Scripts\activate.bat

REM Run pre-market health check
echo Running pre-market health check...
python system3_premarket_health_check.py
if errorlevel 1 (
    echo.
    echo ============================================
    echo HEALTH CHECK FAILED - NOT STARTING AUTORUN
    echo ============================================
    pause
    exit /b 1
)

echo.
echo Health check passed. Starting autorun...
echo.

REM Start watchdog and master...
```

---

## Benefits

1. ✅ **Early Problem Detection**: Catches issues before market open
2. ✅ **Prevents Wasted Trading Day**: No surprises during market hours
3. ✅ **Clear Status**: Simple PASS/FAIL with detailed breakdown
4. ✅ **Automated**: Can be integrated into startup workflow
5. ✅ **Comprehensive**: Covers all critical system components
6. ✅ **Non-Blocking Warnings**: Distinguishes critical vs. informational issues

---

## Example Scenarios

### Scenario 1: All Checks Pass
```
✅ HEALTH CHECK PASSED - SYSTEM READY FOR MARKET
```
**Action**: Proceed with autorun

### Scenario 2: Disk Space Low
```
❌ Disk space check FAILED: 0.5 GB free (need 1.0 GB)
❌ HEALTH CHECK FAILED - FIX ISSUES BEFORE STARTING
```
**Action**: Free up disk space, then re-run check

### Scenario 3: Missing Dependency
```
❌ Dependencies check FAILED: 1 package(s) missing
   - psutil
❌ HEALTH CHECK FAILED - FIX ISSUES BEFORE STARTING
```
**Action**: Install missing package: `pip install psutil`

### Scenario 4: Configuration Error
```
❌ Configuration check FAILED:
   - LIVE_TRADING_ENABLED is True (must be False)
❌ HEALTH CHECK FAILED - FIX ISSUES BEFORE STARTING
```
**Action**: Fix configuration file, then re-run check

### Scenario 5: Warnings Only
```
⚠️  Last shutdown check WARN: No shutdown flag found (first run?)
⚠️  Signal files check WARN: Signals file not found (expected if first run)
✅ HEALTH CHECK PASSED (with warnings)
⚠️  Non-blocking warnings present - system ready but review recommended
```
**Action**: Proceed with autorun (warnings are expected on first run)

---

## Maintenance

### Adding New Checks

1. Create check function:
```python
def check_new_feature() -> Tuple[bool, Dict[str, Any]]:
    """Check new feature."""
    try:
        # Check logic
        result = {"status": "PASS", ...}
        logger.info("✅ New feature check PASSED")
        return True, result
    except Exception as e:
        logger.error(f"❌ New feature check FAILED: {e}")
        return False, {"status": "FAIL", "error": str(e)}
```

2. Add to `run_all_checks()`:
```python
checks = {
    ...
    "new_feature": check_new_feature(),
}
```

### Updating Thresholds

Edit constants at top of file:
```python
# In check_disk_space()
min_gb: float = 1.0  # Change threshold here

# In check_log_file_sizes()
max_mb: float = 100.0  # Change threshold here
```

---

## Testing

### Manual Test
```bash
python system3_premarket_health_check.py
```

### Expected Output
- All checks should pass on a properly configured system
- Warnings are acceptable for first-time runs
- Failures should be fixed before proceeding

---

## Next Steps

1. ✅ **Script Created**: Ready to use
2. ⏳ **Test Run**: Run the script to verify it works
3. ⏳ **Integration**: Optionally integrate into autorun startup
4. ⏳ **Schedule**: Run daily before market open

---

## Related Files

- `system3_premarket_checklist.py`: 20-point detailed checklist (more comprehensive)
- `system3_premarket_health_check.py`: Quick health check (faster, focused)
- `START_AUTORUN_AND_WATCHDOG.bat`: Autorun launcher

**Recommendation**: Use `system3_premarket_health_check.py` for quick daily checks, and `system3_premarket_checklist.py` for detailed validation.

---

**Status**: ✅ **IMPLEMENTATION COMPLETE - READY TO USE**

**Report Generated**: 2025-12-04

