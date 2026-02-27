# System3 Market Hours Analysis - December 2, 2025

**Analysis Date**: 2025-12-02  
**Market Hours**: 9:15 AM - 3:30 PM IST  
**Status**: ⚠️ **CRITICAL ISSUES IDENTIFIED**

---

## 📊 EXECUTIVE SUMMARY

### Key Findings:
1. ❌ **Only 30 signals generated** during entire market day (9:15 AM - 3:30 PM)
2. ❌ **100% HOLD signals** - No BUY or SELL signals generated
3. ❌ **Zero trend/volatility/momentum scores** - All components contributing zero
4. ❌ **OP3 failing** - CSV parsing errors preventing trade decision analysis
5. ⚠️ **Autopilot restart loop** after 4 PM (now fixed)

---

## 🔍 DETAILED ANALYSIS

### 1. Signal Generation Volume

**Expected**: ~720 snapshots (30-second intervals × 6.25 hours)  
**Actual**: **30 signals** (archived at 3:30 PM)

**Analysis**:
- Autopilot started at 9:15 AM ✅
- Only 30 signals were generated and archived at 3:30 PM
- This suggests autopilot may have stopped running or signals weren't being written

**Evidence**:
```
2025-12-02 09:15:48,888 [INFO] Starting OP2: Live Signal Generation (DRY-RUN autopilot)...
2025-12-02 15:30:15,477 [INFO] Signals archived: {'rows': 30}
```

---

### 2. Signal Distribution

**From Archived CSV** (`angel_index_ai_signals_20251202_153015_before_new_day.csv`):

| Signal Type | Count | Percentage |
|------------|-------|------------|
| **HOLD** | 29 | 96.67% |
| **SELL_CE** | 1 | 3.33% |
| **BUY** | 0 | 0% |
| **SELL** | 0 | 0% |

**Critical Issue**: **NO BUY SIGNALS** generated despite 6+ hours of market activity.

---

### 3. Score Component Analysis

**From Score Attribution Report** (`logs/research/system3_score_component_attribution.md`):

| Component | Mean Contribution | Correlation | Mean Abs Value |
|-----------|------------------|-------------|---------------|
| **ai_score** | 10.790 | 0.545 | 0.470 |
| **greeks_score** | 6.881 | 0.893 | 0.342 |
| **trend_score** | 0.035 | 0.614 | **0.001** ⚠️ |
| **breakout_score** | 0.035 | -0.161 | **0.001** ⚠️ |
| **volatility_score** | 0.000 | 0.000 | **0.000** ❌ |
| **momentum_score** | 0.000 | 0.000 | **0.000** ❌ |

**Critical Findings**:
- ✅ `ai_score` and `greeks_score` are working (non-zero contributions)
- ❌ `trend_score`, `volatility_score`, `momentum_score` are **essentially ZERO**
- ❌ `breakout_score` is near-zero (0.001)

**Root Cause**: Historical feature enrichment is **NOT WORKING** as expected.

---

### 4. Threshold Analysis

**Current Thresholds** (from `signal_scorer.py`):
- `buy_threshold`: **0.40**
- `sell_threshold`: **-0.40**

**Threshold Candidates** (from `storage/meta/system3_threshold_candidates.json`):
- Even with thresholds as low as **0.4 / -0.3**, only **1 SELL** signal found
- **0 BUY** signals found with any threshold combination

**Analysis**: Final scores are not reaching BUY threshold (0.40) because:
1. `trend_score`, `volatility_score`, `momentum_score` are zero
2. Only `ai_score` and `greeks_score` are contributing
3. Weighted combination is not strong enough to cross threshold

---

### 5. Model Performance

**From Label Quality Report** (`logs/ml/system3_label_quality_report.md`):
- **Total Rows**: 30
- **HOLD**: 29 (96.67%)
- **SELL_CE**: 1 (3.33%)
- **Imbalance Ratio**: 29.00 ⚠️

**Model Status**:
- ✅ Model is training (no crashes)
- ⚠️ Severe class imbalance (all HOLD)
- ❌ Model cannot learn from HOLD-only data

---

### 6. OP3 Failure (Trade Decision Analysis)

**Error**: `Error tokenizing data. C error: Expected 74 fields in line 32, saw 77`

**Frequency**: Every hourly OP cycle (7 times during market hours)

**Impact**:
- ❌ Trade decision analysis cannot run
- ❌ Cannot identify actionable signals
- ❌ Cannot generate trade plans

**Root Cause**: Malformed CSV line in signal file (line 32 has wrong column count)

---

### 7. Autopilot Restart Loop (After 4 PM)

**Issue**: Master script was restarting repeatedly after 4:00 PM shutdown

**Evidence**:
```
2025-12-02 16:00:54,653 [INFO] Starting OP2: Live Signal Generation...
2025-12-02 16:00:54,670 [INFO] Stopping autopilot...
2025-12-02 16:02:24,723 [INFO] Starting OP2: Live Signal Generation...
2025-12-02 16:02:24,731 [INFO] Stopping autopilot...
... (repeated 20+ times)
```

**Status**: ✅ **FIXED** (watchdog now respects market hours)

---

## 🎯 ROOT CAUSE ANALYSIS

### Primary Issues:

1. **Historical Feature Enrichment Not Working**
   - `load_recent_signal_history()` may not be finding history
   - `compute_short_history_features()` may not be computing features correctly
   - History file may be empty or malformed

2. **Low Signal Volume**
   - Only 30 signals in 6+ hours suggests autopilot stopped or wasn't writing
   - Expected: ~720 snapshots (30-second intervals)

3. **Zero Component Scores**
   - `trend_score`, `volatility_score`, `momentum_score` = 0.000
   - These components are not contributing to final score
   - Only `ai_score` and `greeks_score` are working

4. **Thresholds Too Strict**
   - Even with `buy_threshold = 0.40`, no BUY signals
   - Final scores are not reaching threshold due to missing components

5. **CSV Parsing Errors**
   - Malformed line 32 in signal CSV
   - Preventing OP3 from running

---

## 🔧 RECOMMENDED FIXES

### Priority 1: Fix Historical Feature Enrichment

**Action**: Verify `load_recent_signal_history()` and `compute_short_history_features()` are working

**Check**:
1. Does `storage/live/angel_index_ai_signals.csv` exist during autopilot run?
2. Is history being loaded correctly?
3. Are short-history features being computed and merged?

**Fix**: Ensure history file exists and is readable before computing features

---

### Priority 2: Increase Signal Generation Volume

**Action**: Verify autopilot is running continuously and writing signals

**Check**:
1. Is autopilot loop running every 30 seconds?
2. Are signals being appended to CSV?
3. Are there any errors preventing signal generation?

**Fix**: Add logging to confirm autopilot is running and signals are being written

---

### Priority 3: Fix CSV Parsing Errors

**Action**: Clean malformed line 32 in signal CSV

**Fix**: Run `system3_history_cleaner.py` to remove malformed rows

---

### Priority 4: Lower Thresholds Temporarily

**Action**: Reduce thresholds to generate more signals for testing

**Suggested**:
- `buy_threshold`: 0.40 → **0.30**
- `sell_threshold`: -0.40 → **-0.30**

**Purpose**: Generate signals to test system, then recalibrate based on results

---

### Priority 5: Add Diagnostic Logging

**Action**: Add detailed logging for:
- History loading (file exists, rows loaded)
- Feature computation (features computed, values)
- Score calculation (component values, final score)
- Signal generation (BUY/SELL/HOLD counts)

---

## 📈 EXPECTED IMPROVEMENTS

After fixes:
1. ✅ Historical features contributing non-zero values
2. ✅ 700+ signals generated per day
3. ✅ BUY/SELL signals generated (not just HOLD)
4. ✅ OP3 running successfully
5. ✅ Model learning from diverse signals

---

## 🎯 NEXT STEPS

1. **Immediate**: Fix CSV parsing error (run history cleaner)
2. **Today**: Verify historical feature enrichment is working
3. **Today**: Add diagnostic logging to autopilot
4. **Tomorrow**: Test with lower thresholds
5. **This Week**: Monitor signal generation volume and distribution

---

## 📝 SUMMARY

**System Status**: ⚠️ **OPERATIONAL BUT NOT GENERATING ACTIONABLE SIGNALS**

**Key Metrics**:
- Signal Volume: ❌ **30 signals** (expected: 720)
- BUY Signals: ❌ **0** (expected: 50-100)
- SELL Signals: ❌ **0** (expected: 50-100)
- Component Scores: ⚠️ **2/6 working** (ai_score, greeks_score)
- Model Training: ✅ **Working** (but learning from HOLD-only data)

**Overall Assessment**: System is running but **not generating actionable signals** due to:
1. Missing historical feature enrichment
2. Low signal volume
3. Zero component scores
4. Strict thresholds

**Action Required**: **HIGH PRIORITY** - Fix historical feature enrichment and increase signal volume before next market session.

