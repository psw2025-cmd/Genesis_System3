# BUY Decision Diagnostic - Root Cause Analysis
**Analysis Date**: 2025-12-04  
**Question**: Why were there NO BUY signals generated?

---

## Executive Summary

**Root Cause**: ✅ **IDENTIFIED**  
**Reason**: All `final_score` values are below the BUY threshold of 0.40

**Findings**:
- 30 signals generated (all HOLD)
- `final_score` range: -0.1619 to +0.1387
- BUY threshold: 0.40 (default) or 0.40 (tuned)
- All scores are below threshold → All signals = HOLD

**Status**: ✅ **SYSTEM WORKING AS DESIGNED** (conservative behavior, not a bug)

---

## Signal Analysis

### Signals File: `storage/live/dhan_index_ai_signals.csv`

**Total Signals**: 30  
**BUY Signals**: 0  
**SELL Signals**: 0  
**HOLD Signals**: 30 (100%)

**Evidence**:
```
Row 2: final_score=0.1387, signal=HOLD
Row 3: final_score=-0.1619, signal=HOLD
Row 4: final_score=0.1034, signal=HOLD
Row 5: final_score=-0.1217, signal=HOLD
...
All 30 rows: signal=HOLD
```

---

## Threshold Analysis

### Default Thresholds

**Code Location**: `core/engine/scoring_engine/signal_scorer.py`  
**Default Values**:
- `buy_threshold`: 0.40
- `sell_threshold`: -0.40

**Evidence**:
```python
def generate_signals(
    df: pd.DataFrame,
    buy_threshold: float = 0.40,
    sell_threshold: float = -0.40,
    ...
):
```

### Tuned Thresholds

**File**: `storage/meta/system3_tuned_thresholds.json`  
**Values**:
- `buy`: 0.4
- `sell`: -0.3

**Evidence**:
```json
{
  "default": {"buy": 0.4, "sell": -0.3},
  "BANKNIFTY": {"buy": 0.4, "sell": -0.3},
  ...
}
```

### Threshold Comparison

| Threshold Type | Buy | Sell | Used? |
|----------------|-----|------|-------|
| Default (code) | 0.40 | -0.40 | ✅ Yes (if tuned not loaded) |
| Tuned (JSON) | 0.40 | -0.30 | ✅ Yes (if loaded) |

**Result**: Both use 0.40 for BUY threshold.

---

## Final Score Distribution

### Statistics

**Min**: -0.1619  
**Max**: +0.1387  
**Mean**: ~0.0 (slightly positive)  
**Median**: ~0.0

**Above BUY Threshold (0.40)**: 0 signals  
**Below SELL Threshold (-0.40)**: 0 signals  
**In HOLD Range**: 30 signals (100%)

### Score Distribution Table

| Score Range | Count | Signal |
|-------------|-------|--------|
| > 0.40 (BUY) | 0 | - |
| 0.00 to 0.40 | 15 | HOLD |
| -0.40 to 0.00 | 15 | HOLD |
| < -0.40 (SELL) | 0 | - |

---

## Model Output Analysis

### AI Model Status

**Model Produced Predictions**: ✅ YES  
**Evidence**: All signals have `pred_label` and `pred_confidence` values

**Example**:
```
pred_label=HOLD, pred_confidence=0.1387
pred_label=HOLD, pred_confidence=0.1619
```

### Score Components

**Components Used**:
- `ai_score`: AI model output
- `greeks_score`: Greeks-based score
- `final_score`: Combined score

**Example Calculation** (Row 2):
- `ai_score`: 0.1121
- `greeks_score`: 0.3737
- `final_score`: 0.1387

**Analysis**: Scores are low but non-zero, indicating the model is working but producing conservative predictions.

---

## Decision Engine Analysis

### Signal Generation Logic

**Code Location**: `core/engine/scoring_engine/signal_scorer.py`

**Logic**:
```python
if final_score > buy_threshold:
    return "BUY"
elif final_score < sell_threshold:
    return "SELL"
else:
    return "HOLD"
```

**Applied to Data**:
- All `final_score` values: -0.1619 to +0.1387
- BUY threshold: 0.40
- Result: All signals = HOLD ✅ **CORRECT**

### Decision Engine Status

**Status**: ✅ **WORKING CORRECTLY**  
**Evidence**: Signals correctly assigned based on thresholds

---

## Curated File Analysis

### Curated File: `storage/live/dhan_index_ai_signals_curated.csv`

**Total Rows**: 610 (includes historical data)  
**Columns**: 86 (72 base + 14 curated columns)  
**Latest Signals**: Same 30 signals from today

**Analysis**: Curated file contains the same signals, no filtering occurred.

**Evidence**: Curated file has additional columns (`ml_prediction`, `ml_probability`, `moneyness`, etc.) but same signal values.

---

## Autopilot Safety Filters

### Pre-Market Checks

**Status**: ✅ PASSED (after fixes)  
**Evidence**:
```
2025-12-03 21:13:13 [INFO] [OK] Market warmup scanner: PASS
2025-12-03 21:13:13 [INFO] [OK] Environment guard complete
```

**Note**: Early run (09:15:13) had encoding error, but this was fixed.

### Safety Flags

**DRY-RUN Mode**: ✅ CONFIRMED  
**Live Trading**: ❌ DISABLED  
**Auto Execute**: ❌ DISABLED

**Evidence**:
```
LIVE_TRADING_ENABLED: False
USE_LIVE_EXECUTION_ENGINE: False
auto_execute_trades: False
Ultra AUTO_EXECUTE_TRADES: False
```

**Impact**: Safety filters did NOT block signals (they only block execution).

---

## Root Cause Conclusion

### Primary Root Cause

**Reason**: **Conservative Model Output**

1. ✅ Model generated predictions
2. ✅ Score engine computed `final_score`
3. ✅ Decision engine applied thresholds correctly
4. ❌ All scores below BUY threshold (0.40)
5. ✅ Result: All signals = HOLD (correct behavior)

### Why Scores Are Low

**Possible Reasons**:
1. **Market Conditions**: Low volatility, neutral market regime
2. **Model Training**: Model trained on conservative data
3. **Feature Values**: Input features indicate low edge
4. **Threshold Calibration**: Thresholds set conservatively for safety

**Evidence**: Scores are non-zero but small, indicating the model is working but detecting low edge conditions.

---

## Verification

### Model Produced Signals?
✅ **YES** - 30 signals generated

### Signals Had final_score > Threshold?
❌ **NO** - All scores < 0.40

### Decision Engine Filtered Everything?
❌ **NO** - Decision engine worked correctly, assigned HOLD based on thresholds

### Curated Maker Removed Signals?
❌ **NO** - Curated file contains same signals

### Autopilot Rejected Signals?
❌ **NO** - Autopilot safety filters only block execution, not signal generation

---

## Final Verdict

**Status**: ✅ **SYSTEM WORKING AS DESIGNED**

**Conclusion**: The system correctly generated signals, computed scores, and applied thresholds. All signals were assigned HOLD because the `final_score` values were below the BUY threshold. This is **conservative behavior**, not a bug.

**Recommendation**: 
- If more aggressive trading is desired, consider lowering the BUY threshold (with caution)
- Monitor model performance and adjust thresholds based on backtesting
- Current behavior is appropriate for DRY-RUN safety

