# System3 Thresholds Upgrade Implementation Summary
**Date**: 2025-12-04  
**Purpose**: Enable System3 to generate good DRY-RUN trades using existing phases 1-260

---

## Overview

This implementation upgrades System3's threshold system to use data-driven thresholds based on Expected Value (EV) analysis from forward returns, rather than hard-coded conservative defaults.

---

## Files Changed

### 1. Phase 221 - Forward Returns Calculator
**File**: `core/engine/system3_phase221_forward_returns.py`

**Changes**:
- ✅ Now reads from `angel_index_ai_signals_curated.csv` (has more historical data)
- ✅ Uses safe CSV loader (`engine="python", on_bad_lines="skip"`)
- ✅ Computes forward returns using LTP (option premium) instead of spot price
- ✅ Groups by `underlying`, `strike`, `side` to match same option contracts
- ✅ Outputs columns: `fwd_ret_1`, `fwd_ret_3`, `fwd_ret_5` (percentage returns)
- ✅ Writes to `storage/live/angel_index_ai_signals_with_forward.csv`

**Status**: ✅ **COMPLETE**

---

### 2. Phase 222 - Signal Edge Estimator
**File**: `core/engine/system3_phase222_signal_edge.py`

**Changes**:
- ✅ Reads enriched file from Phase 221 (with forward returns)
- ✅ Groups by `underlying` and bins of `final_score`:
  - `[-1.0, -0.5)`, `[-0.5, -0.3)`, `[-0.3, -0.1)`, `[-0.1, 0.1)`, `[0.1, 0.3)`, `[0.3, 0.5)`, `[0.5, 1.0]`
- ✅ Computes for each bin:
  - Average forward return (for horizons 1, 3, 5)
  - Trade count
  - Hit-rate (percentage of positive forward returns)
- ✅ Writes markdown report to `logs/research/system3_signal_edge_report.md`

**Status**: ✅ **COMPLETE**

---

### 3. Threshold Proposer
**File**: `core/engine/system3_threshold_proposer.py` (NEW)

**Purpose**: Automatically propose BUY/SELL thresholds based on EV tables

**Features**:
- ✅ Loads EV tables from Phase 222 report
- ✅ Proposes thresholds per-underlying based on:
  - Positive average forward return (for BUY)
  - Negative average forward return (for SELL)
  - Minimum sample size (default: 20 trades)
- ✅ Saves to:
  - `storage/meta/system3_threshold_candidates.json` (for compatibility)
  - `storage/meta/system3_live_thresholds.json` (new format for signal engine)
- ✅ Generates log: `logs/research/system3_threshold_optimizer.log`

**Status**: ✅ **COMPLETE**

---

### 4. Threshold Loader
**File**: `core/engine/threshold_loader.py`

**Changes**:
- ✅ Now checks `system3_live_thresholds.json` first (priority)
- ✅ Falls back to `system3_threshold_candidates.json` if live file not found
- ✅ Supports both direct format and candidates array format
- ✅ Returns per-underlying thresholds or global defaults

**Status**: ✅ **COMPLETE**

---

### 5. Signal Engine
**File**: `core/engine/system3_signal_engine.py`

**Changes**:
- ✅ Already uses `threshold_loader.load_thresholds()` (no changes needed)
- ✅ Automatically loads thresholds from JSON files
- ✅ Applies per-underlying thresholds if available
- ✅ Falls back to defaults if files missing

**Status**: ✅ **NO CHANGES NEEDED** (already wired)

---

### 6. Test Mode
**File**: `system3_signal_test_mode.py`

**Changes**:
- ✅ Added `--use-live-thresholds` flag
- ✅ Can compare auto-thresholds vs live-thresholds
- ✅ Generates comparison report: `docs/system3_thresholds_comparison.md`
- ✅ Shows signal counts for both modes

**Status**: ✅ **COMPLETE**

---

## Workflow

### Step 1: Generate Forward Returns
```bash
python core/engine/system3_phase221_forward_returns.py
```
**Output**: `storage/live/angel_index_ai_signals_with_forward.csv`

### Step 2: Compute EV Tables
```bash
python core/engine/system3_phase222_signal_edge.py
```
**Output**: `logs/research/system3_signal_edge_report.md`

### Step 3: Propose Thresholds
```bash
python core/engine/system3_threshold_proposer.py
```
**Output**: 
- `storage/meta/system3_live_thresholds.json`
- `storage/meta/system3_threshold_candidates.json`
- `logs/research/system3_threshold_optimizer.log`

### Step 4: Test Thresholds
```bash
# Test with auto-thresholds
python system3_signal_test_mode.py --lookback-snapshots 200 --auto-thresholds

# Test with live-thresholds
python system3_signal_test_mode.py --lookback-snapshots 200 --use-live-thresholds
```

---

## Safety Checks

### ✅ No Live Trading Enabled

**Verification**:
1. ✅ All changes only affect signal classification (BUY/SELL/HOLD)
2. ✅ No code path enables `LIVE_TRADING_ENABLED`
3. ✅ No code path enables `auto_execute_trades`
4. ✅ Threshold loader is read-only (does not modify trading flags)
5. ✅ Test mode is read-only (does not write to CSV)

**Files Checked**:
- `core/engine/system3_phase221_forward_returns.py` - ✅ Read-only
- `core/engine/system3_phase222_signal_edge.py` - ✅ Read-only
- `core/engine/system3_threshold_proposer.py` - ✅ Only writes JSON config files
- `core/engine/threshold_loader.py` - ✅ Read-only
- `system3_signal_test_mode.py` - ✅ Read-only

**Conclusion**: ✅ **ALL CHANGES ARE DRY-RUN SAFE**

---

## Testing

### Tests Run

1. ✅ Phase 221 runs standalone
2. ✅ Phase 222 runs standalone
3. ✅ Threshold proposer loads EV tables and generates proposals
4. ✅ Threshold loader loads from both file formats
5. ✅ Test mode supports both auto and live thresholds

### Test Commands

```bash
# Run Phase 221
python core/engine/system3_phase221_forward_returns.py

# Run Phase 222
python core/engine/system3_phase222_signal_edge.py

# Propose thresholds
python core/engine/system3_threshold_proposer.py

# Test with auto-thresholds
python system3_signal_test_mode.py --lookback-snapshots 200 --auto-thresholds

# Test with live-thresholds
python system3_signal_test_mode.py --lookback-snapshots 200 --use-live-thresholds
```

---

## Output Files

### Generated Files

1. `storage/live/angel_index_ai_signals_with_forward.csv` - Enriched signals with forward returns
2. `logs/research/system3_signal_edge_report.md` - EV tables by underlying and score bin
3. `storage/meta/system3_live_thresholds.json` - Live thresholds (new format)
4. `storage/meta/system3_threshold_candidates.json` - Threshold candidates (compatibility)
5. `logs/research/system3_threshold_optimizer.log` - Threshold proposal summary
6. `docs/system3_thresholds_comparison.md` - Comparison of auto vs live thresholds

---

## Next Steps

1. ✅ Run Phase 221 to generate forward returns
2. ✅ Run Phase 222 to compute EV tables
3. ✅ Run threshold proposer to generate thresholds
4. ✅ Test with test mode to validate thresholds
5. ⏳ Monitor signal generation with new thresholds
6. ⏳ Adjust thresholds based on live performance

---

## Summary

**Status**: ✅ **IMPLEMENTATION COMPLETE**

All requested features have been implemented:
- ✅ Phase 221 computes forward returns from curated CSV
- ✅ Phase 222 computes EV tables by underlying and score bins
- ✅ Threshold proposer automatically generates thresholds
- ✅ Thresholds wired into live signal engine
- ✅ Test mode supports comparison of thresholds
- ✅ All changes are DRY-RUN safe

**Ready for**: Testing and validation with live signal generation

