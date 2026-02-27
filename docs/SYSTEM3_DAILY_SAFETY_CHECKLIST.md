# System3 Daily Safety Checklist

**Purpose**: Ensure the System3 signal pipeline is safe and stable before, during, and after market hours.

**Last Updated**: 2025-12-04

---

## Overview

The System3 Daily Safety Checklist is a comprehensive set of automated checks that validate:

1. **Static Threshold Sanity** - Thresholds JSON structure and signal counts
2. **Pre-Market Dry-Run** - Signal generation with today's data and safety checks
3. **Signal Engine Self-Test** - Pipeline validation without broker APIs
4. **Post-Close Audit** - Consistency verification of logged signals

---

## Pre-Market Checks (Before Market Opens)

### Quick Start

Run the complete daily safety checklist:

```batch
system3_daily_safety_check.bat
```

This runs all three pre-market checks in sequence:
1. Static threshold validation
2. Pre-market signal dry-run
3. Signal engine self-test

### Individual Checks

#### 1. Static Threshold Sanity Check

**Command**:
```batch
run_validate_live_thresholds.bat
```

**What it does**:
- Loads `storage/meta/system3_live_thresholds.json`
- Validates JSON structure (global + per_underlying)
- Verifies thresholds are numeric and in sane ranges (-1.0 to +1.0)
- Counts signals at thresholds using EV-ready CSV
- Validates signal counts match expectations (40 BUY, 39 SELL ± 2)

**Expected Output**:
- ✅ PASS: Thresholds valid, signal counts match
- ❌ FAIL: Invalid structure, out-of-range values, or signal count mismatch

**What to do if FAIL**:
- Check `storage/meta/system3_live_thresholds.json` for syntax errors
- Verify thresholds are in range [-1.0, 1.0]
- Review signal distribution analysis if counts don't match

#### 2. Pre-Market Signal Dry-Run

**Command**:
```batch
run_pre_market_check.bat
```

**What it does**:
- Loads latest snapshot from `storage/live/angel_index_ai_signals.csv`
- Applies live thresholds (global + per_underlying)
- Computes signal counts per underlying
- Analyzes score distribution near thresholds
- Performs safety checks:
  - Total signals = 0 → FAIL (thresholds too tight)
  - One underlying > 80% of signals → WARN (dominance)
  - Any underlying > 50 signals → WARN (possible bug)

**Expected Output**:
- ✅ SAFE TO START: All checks passed
- ❌ NOT SAFE TO START: Failures detected

**Report Location**:
- `storage/logs/system3_pre_market_check_YYYYMMDD.md`

**What to do if FAIL**:
- Review pre-market report for details
- Check if thresholds are appropriate for current market regime
- Consider adjusting thresholds if too tight/loose

#### 3. Signal Engine Self-Test

**Command**:
```batch
python core/engine/system3_signal_engine_self_test.py
```

**What it does**:
- Loads thresholds without broker APIs
- Creates test snapshot with sample data
- Runs through complete signal pipeline
- Verifies required columns are present
- Checks signal distribution
- Validates thresholds are applied correctly

**Expected Output**:
- ✅ PASS: Pipeline works, thresholds applied
- ❌ FAIL: Pipeline errors or threshold mismatches

**What to do if FAIL**:
- Review error messages
- Check signal engine imports and dependencies
- Verify threshold loader is working

---

## During Market Hours

### Runtime Safety Guards

The live signal engine includes automatic safety guards:

- **Signal Rate Limits**: Max 10 signals per minute per underlying
- **Position Limits**: Max 50 open positions, 100 pending signals
- **Safety Trip Logging**: All safety trips logged to `storage/logs/system3_live_safety_trips_YYYYMMDD.log`

**Safety Guard Module**: `core/validation/live_safety_guard.py`

**Integration**: Safety guards are automatically called during signal generation in `core/engine/system3_signal_engine.py`

---

## Post-Close Checks (After Market Closes)

### Post-Close Signal Audit

**Command**:
```batch
run_post_close_audit.bat
```

**What it does**:
- Loads today's signals from `storage/live/angel_index_ai_signals.csv`
- Verifies each signal decision matches its score and thresholds
- Checks for missing essential fields
- Computes daily diagnostics:
  - Total signals by type (BUY/SELL/HOLD)
  - Signals per underlying
  - Score distribution statistics
- Detects anomalies:
  - Signals with scores that don't match thresholds
  - Missing required fields
  - Score = 0 with BUY/SELL signals

**Expected Output**:
- ✅ PASS: All signals consistent, no anomalies
- ⚠️ PASS WITH WARNINGS: No inconsistencies, but warnings present
- ❌ FAIL: Inconsistencies detected

**Report Location**:
- `storage/logs/system3_post_close_audit_YYYYMMDD.md`

**What to do if FAIL**:
- Review inconsistencies in report
- Check for threshold changes during market hours
- Investigate any score/threshold mismatches

---

## Complete Daily Workflow

### Morning (Before Market Opens)

1. **Run Daily Safety Checklist**:
   ```batch
   system3_daily_safety_check.bat
   ```

2. **If all checks pass**:
   - ✅ Safe to start market session
   - Run `START_AUTORUN_AND_WATCHDOG.bat`

3. **If any check fails**:
   - ❌ DO NOT START market session
   - Review failure reasons
   - Fix issues (thresholds, data, pipeline)
   - Re-run checks until all pass

### During Market Hours

- Safety guards automatically monitor signal generation
- Safety trips are logged to `storage/logs/system3_live_safety_trips_YYYYMMDD.log`
- Monitor logs for any safety warnings

### Evening (After Market Closes)

1. **Run Post-Close Audit**:
   ```batch
   run_post_close_audit.bat
   ```

2. **Review Audit Report**:
   - Check for inconsistencies
   - Review daily diagnostics
   - Investigate any anomalies

---

## File Locations

### Configuration Files
- `storage/meta/system3_live_thresholds.json` - Live thresholds
- `storage/clean/angel_index_ai_signals_with_forward_ev_ready.csv` - EV-ready data

### Log Files
- `storage/logs/system3_pre_market_check_YYYYMMDD.md` - Pre-market reports
- `storage/logs/system3_live_safety_trips_YYYYMMDD.log` - Safety trip logs
- `storage/logs/system3_post_close_audit_YYYYMMDD.md` - Post-close audits

### Signal Files
- `storage/live/angel_index_ai_signals.csv` - Live signals log

---

## Troubleshooting

### Check 1 Fails: Static Threshold Validation

**Common Issues**:
- JSON syntax errors
- Missing required keys (global, per_underlying)
- Thresholds out of range

**Solutions**:
1. Validate JSON syntax: `python -m json.tool storage/meta/system3_live_thresholds.json`
2. Check file structure matches expected format
3. Verify thresholds are in range [-1.0, 1.0]

### Check 2 Fails: Pre-Market Dry-Run

**Common Issues**:
- No signals generated (thresholds too tight)
- One underlying dominates all signals
- Excessive signal counts

**Solutions**:
1. Review pre-market report for details
2. Adjust thresholds if too tight/loose
3. Check market regime (volatility, trends)

### Check 3 Fails: Self-Test

**Common Issues**:
- Import errors
- Pipeline crashes
- Missing columns

**Solutions**:
1. Check Python environment and dependencies
2. Review error traceback
3. Verify signal engine imports

### Post-Close Audit Fails

**Common Issues**:
- Signal/score mismatches
- Missing required fields
- Threshold changes during market hours

**Solutions**:
1. Review inconsistencies in audit report
2. Check for threshold file changes
3. Investigate score calculation issues

---

## Safety Limits Configuration

Safety limits are defined in `core/validation/live_safety_guard.py`:

```python
MAX_SIGNALS_PER_MINUTE_PER_UNDERLYING = 10
MAX_TOTAL_OPEN_POSITIONS = 50
MAX_PENDING_SIGNALS = 100
```

To adjust limits, modify these constants and restart the signal engine.

---

## Expected Signal Counts

Based on clean EV-ready CSV (232 rows):

- **Global BUY** (>= 0.1): ~40 signals (17.2%)
- **Global SELL** (<= -0.1): ~39 signals (16.8%)
- **Total**: ~79 signals (34%)

**Per-Underlying**:
- NIFTY: 17 BUY, 15 SELL (32 total)
- BANKNIFTY: 6 BUY, 8 SELL (14 total)
- FINNIFTY: 6 BUY, 5 SELL (11 total)
- MIDCPNIFTY: 7 BUY, 5 SELL (12 total)
- SENSEX: 4 BUY, 6 SELL (10 total)

**Tolerance**: ±2 signals for dataset changes

---

## Summary

✅ **Before Market**: Run `system3_daily_safety_check.bat`  
✅ **During Market**: Safety guards automatically monitor  
✅ **After Market**: Run `run_post_close_audit.bat`

**Status Indicators**:
- ✅ PASS: Safe to proceed
- ⚠️ WARN: Proceed with caution, review warnings
- ❌ FAIL: DO NOT PROCEED, fix issues first

---

**Last Updated**: 2025-12-04

