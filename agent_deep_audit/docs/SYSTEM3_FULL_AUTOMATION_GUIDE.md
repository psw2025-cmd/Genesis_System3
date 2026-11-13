# System3 Full Automation Guide

**Last Updated**: 2025-12-04  
**Status**: ✅ **FULLY AUTOMATED**

---

## Overview

System3 now includes **full automation** of all safety checks and validations. You no longer need to manually run multiple files - everything happens automatically when you start `START_AUTORUN_AND_WATCHDOG.bat`.

---

## How It Works

### Single Command to Start Everything

Simply run:
```batch
START_AUTORUN_AND_WATCHDOG.bat
```

This single command now:

1. **Automatically runs all pre-market safety checks** (before starting autorun)
2. **Starts the watchdog** (monitors master)
3. **Starts the autorun master** (runs all phases and autopilot)
4. **Automatically runs post-close audit** (after market closes)

---

## Automated Pre-Market Checks

When you run `START_AUTORUN_AND_WATCHDOG.bat`, it **automatically** runs:

### 1. Static Threshold Validation ✅
- Validates thresholds JSON structure
- Verifies signal counts match expectations
- **If FAIL**: Autorun will NOT start

### 2. Pre-Market Signal Dry-Run ✅
- Tests signal generation with today's data
- Performs safety checks (zero signals, dominance, excessive counts)
- **If FAIL**: Autorun will NOT start

### 3. Signal Engine Self-Test ✅
- Tests complete signal pipeline
- Validates thresholds are applied correctly
- **If FAIL**: Autorun will NOT start

**All checks must pass** before autorun starts. If any check fails, you'll see a clear error message and the autorun will not start.

---

## Automated Post-Close Audit

After market closes (4:00 PM), the autorun master **automatically** runs:

### Post-Close Signal Audit ✅
- Verifies all signals are consistent with thresholds
- Checks for missing fields
- Computes daily diagnostics
- Generates audit report

**Report Location**: `storage/logs/system3_post_close_audit_YYYYMMDD.md`

---

## Runtime Safety Guards

During market hours, safety guards are **automatically active**:

- **Signal Rate Limits**: Max 10 signals/minute/underlying
- **Position Limits**: Max 50 open positions, 100 pending signals
- **Safety Trip Logging**: All trips logged to `storage/logs/system3_live_safety_trips_YYYYMMDD.log`

**No manual action required** - these guards are integrated into the signal engine.

---

## Complete Daily Workflow

### Morning (Before Market Opens)

**Single Command**:
```batch
START_AUTORUN_AND_WATCHDOG.bat
```

**What Happens**:
1. ✅ Pre-market checks run automatically
2. ✅ If all pass → Autorun starts
3. ✅ If any fail → Autorun does NOT start (you see error message)

**You Don't Need To**:
- ❌ Manually run `run_validate_live_thresholds.bat`
- ❌ Manually run `run_pre_market_check.bat`
- ❌ Manually run self-test
- ❌ Check anything manually

**Everything is automated!**

### During Market Hours

**Automatic**:
- ✅ Safety guards monitor signal generation
- ✅ Safety trips are logged automatically
- ✅ Phases run on schedule
- ✅ Autopilot runs continuously

**You Don't Need To**:
- ❌ Monitor anything manually
- ❌ Check safety logs manually
- ❌ Run any commands

**Everything runs automatically!**

### Evening (After Market Closes)

**Automatic**:
- ✅ Post-close audit runs at 4:00 PM
- ✅ Audit report is generated automatically
- ✅ System shuts down gracefully

**You Don't Need To**:
- ❌ Manually run `run_post_close_audit.bat`
- ❌ Check anything manually

**Everything is automated!**

---

## What If Pre-Market Checks Fail?

If any pre-market check fails, you'll see:

```
============================================================================
PRE-MARKET CHECK FAILED - [Reason]
============================================================================

DO NOT START MARKET SESSION - [Action required]
```

**What To Do**:
1. Read the error message
2. Fix the issue (thresholds, data, pipeline)
3. Re-run `START_AUTORUN_AND_WATCHDOG.bat`
4. Checks will run again automatically

**Common Issues**:
- **Threshold validation fails**: Check `storage/meta/system3_live_thresholds.json`
- **Pre-market dry-run fails**: Review `storage/logs/system3_pre_market_check_YYYYMMDD.md`
- **Self-test fails**: Check signal engine dependencies

---

## Manual Override (If Needed)

If you need to run checks manually (for debugging):

### Pre-Market Checks
```batch
system3_daily_safety_check.bat
```

### Post-Close Audit
```batch
run_post_close_audit.bat
```

But **normally you don't need to** - everything is automated!

---

## File Locations

### Pre-Market Reports
- `storage/logs/system3_pre_market_check_YYYYMMDD.md`

### Safety Trip Logs
- `storage/logs/system3_live_safety_trips_YYYYMMDD.log`

### Post-Close Audit Reports
- `storage/logs/system3_post_close_audit_YYYYMMDD.md`

---

## Summary

✅ **Fully Automated**:
- Pre-market checks run automatically before autorun starts
- Runtime safety guards are always active
- Post-close audit runs automatically after market closes

✅ **Single Command**:
- Just run `START_AUTORUN_AND_WATCHDOG.bat`
- Everything else happens automatically

✅ **Safe by Default**:
- Autorun won't start if pre-market checks fail
- Safety guards prevent issues during market hours
- Post-close audit verifies everything worked correctly

**You can now start System3 with a single command and everything is automated!**

---

**Last Updated**: 2025-12-04

