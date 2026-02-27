# System3 Autorun Validation Checklist

**Quick Reference**: Validation checklist for `START_AUTORUN_AND_WATCHDOG.bat`

---

## Pre-Flight Checklist

Before running `START_AUTORUN_AND_WATCHDOG.bat`, verify:

- [ ] `storage/meta/system3_live_thresholds.json` exists
- [ ] `storage/clean/angel_index_ai_signals_with_forward_ev_ready.csv` exists
- [ ] `core/validation/validate_live_thresholds.py` exists
- [ ] `core/validation/pre_market_signal_dryrun.py` exists
- [ ] `core/engine/system3_signal_engine_self_test.py` exists
- [ ] `system3_watchdog.py` exists
- [ ] `system3_autorun_master.py` exists
- [ ] Virtual environment is set up correctly

---

## Expected Behavior

### ✅ Success Path

1. Pre-market checks run (3 checks)
2. All checks pass
3. Watchdog starts in separate window
4. Master starts in current window
5. System runs normally

**Time**: ~7-11 seconds for checks

### ❌ Failure Path

1. Pre-market check fails
2. Script stops immediately
3. Clear error message shown
4. Watchdog and master do NOT start
5. User must fix issue and re-run

---

## Error Messages

### Threshold Validation Failed
```
PRE-MARKET CHECK FAILED - Threshold validation failed
DO NOT START MARKET SESSION - Fix threshold issues first
```

**Action**: Check `storage/meta/system3_live_thresholds.json`

### Pre-Market Dry-Run Failed
```
PRE-MARKET CHECK FAILED - Signal dry-run failed
DO NOT START MARKET SESSION - Review pre-market report
```

**Action**: Check `storage/logs/system3_pre_market_check_YYYYMMDD.md`

### Self-Test Failed
```
PRE-MARKET CHECK FAILED - Signal engine self-test failed
DO NOT START MARKET SESSION - Fix signal engine issues first
```

**Action**: Check signal engine dependencies and imports

---

## Validation Test

Run integration test:
```batch
run_integration_test.bat
```

Or manually:
```batch
python test_autorun_integration.py
```

---

## Quick Validation

### Test 1: File Existence
```batch
dir START_AUTORUN_AND_WATCHDOG.bat
dir storage\meta\system3_live_thresholds.json
dir core\validation\validate_live_thresholds.py
```

### Test 2: Python Path
```batch
C:\Genesis_System3\venv\Scripts\python.exe --version
```

### Test 3: Individual Checks
```batch
C:\Genesis_System3\venv\Scripts\python.exe core\validation\validate_live_thresholds.py
C:\Genesis_System3\venv\Scripts\python.exe core\validation\pre_market_signal_dryrun.py
C:\Genesis_System3\venv\Scripts\python.exe core\engine\system3_signal_engine_self_test.py
```

---

## Status

✅ **VALIDATED AND READY**

All scenarios tested and validated.

---

**Last Updated**: 2025-12-04

