# System3 CSV Deep Validation - Results Analysis
**Date**: 2025-12-04  
**File**: `angel_index_ai_signals_with_forward.csv`  
**Validation Script**: `system3_csv_deep_validation.py`

---

## Executive Summary

The deep validation script successfully analyzed the CSV file and identified several data quality issues. While the overall structure is sound, there are critical problems that need attention before using this dataset for EV analysis, threshold optimization, and model training.

**Overall Status**: ⚠️ **DATA QUALITY ISSUES DETECTED** - Requires fixes before production use

---

## 1. File Statistics

### Basic Metrics
- **Total Rows**: 608 (original), 603 (after cleaning)
- **Total Columns**: 89
- **Memory Usage**: 2.39 MB
- **Rows Dropped**: 5 (duplicate header rows)

### Data Completeness
- **Complete Rows**: ~275 rows (45.2%) have full data (Greeks, IV, indicators)
- **Partial Rows**: ~333 rows (54.8%) have missing data
- **Forward Returns Coverage**:
  - `fwd_ret_1`: 560 values (92.9%) ✅ Good
  - `fwd_ret_3`: 484 values (80.3%) ⚠️ Moderate
  - `fwd_ret_5`: 416 values (69.0%) ⚠️ Low

---

## 2. Critical Issues

### 🔴 CRITICAL: Moneyness Inconsistency (330 rows)

**Issue**: 330 rows have `moneyness=0.0000` when it should equal `spot/strike`.

**Impact**: 
- **HIGH** - This indicates a calculation error or data corruption
- Moneyness is critical for options analysis
- Affects 54.7% of all rows (330/603)

**Examples**:
```
Row 278: moneyness=0.0000, expected=1.0009, spot=59752.7, strike=59700.0, side=CE
Row 279: moneyness=0.0000, expected=1.0009, spot=59752.7, strike=59700.0, side=PE
Row 280: moneyness=0.0000, expected=0.9992, spot=59752.7, strike=59800.0, side=CE
```

**Root Cause**: Likely a calculation error in the signal generation pipeline. Moneyness should be calculated as `spot / strike` for all options.

**Fix Required**:
```python
# Recalculate moneyness
df['moneyness'] = df['spot'] / df['strike']
```

**Action**: **URGENT** - Fix moneyness calculation in signal generation pipeline

---

### 🟡 MEDIUM: Missing Signal Values (333 rows, 55.2%)

**Issue**: 333 rows (55.2%) have NaN signals.

**Impact**:
- **MEDIUM** - Cannot perform signal-based EV analysis on these rows
- May indicate incomplete signal generation
- These rows still have forward returns, so they can be used for other analyses

**Distribution**:
- HOLD: 268 rows (44.4%)
- SELL: 2 rows (0.3%)
- NaN: 333 rows (55.2%)

**Analysis**:
- The 2 SELL signals have **extremely high forward returns** (mean 0.76 for fwd_ret_1, 1.52 for fwd_ret_3/5)
- This suggests SELL signals may be working correctly (selling before price drops)
- Need more SELL signals to validate this pattern

**Action**: Investigate why 55% of rows have no signal. Check signal generation logic.

---

### 🟡 MEDIUM: Forward Returns Coverage Declining

**Issue**: Forward returns coverage decreases with time horizon.

**Coverage**:
- `fwd_ret_1`: 92.9% (560/603) ✅
- `fwd_ret_3`: 80.3% (484/603) ⚠️
- `fwd_ret_5`: 69.0% (416/603) ⚠️

**Impact**:
- **MEDIUM** - Cannot perform 5-day EV analysis on 31% of rows
- This is expected (newer rows don't have 5-day forward returns yet)
- For EV analysis, filter to rows with all 3 forward returns (416 rows available)

**Action**: For Phase 222 (EV analysis), filter to rows with complete forward returns:
```python
df_ev = df[df['fwd_ret_1'].notna() & df['fwd_ret_3'].notna() & df['fwd_ret_5'].notna()].copy()
# This gives 416 rows for EV analysis
```

---

### 🟢 LOW: Positive Theta Values (8 rows)

**Issue**: 8 rows have positive theta values (unusual but may be valid).

**Impact**:
- **LOW** - Theta is typically negative (time decay)
- Positive theta can occur in certain market conditions (e.g., deep ITM options near expiry)
- May be valid, but worth reviewing

**Action**: Review these 8 rows manually to confirm they're valid.

---

## 3. Data Quality Metrics

### Type Conversion Results
- **Columns Converted**: 47 (from object to numeric)
- **New Nulls Created**: 220 total
- **Conversion Success Rate**: ~99.6% (only 220 nulls from 47 columns × 603 rows = 28,341 conversions)

**Breakdown**:
- Most columns: 5 new nulls each (0.82%) - likely from the 5 duplicate header rows
- `spot`, `expected_move_score`, `pred_confidence`: 8 new nulls (1.32%)
- Derived features (`moneyness`, etc.): 3 new nulls (0.49%)

**Status**: ✅ Type conversion successful with minimal data loss

---

## 4. Validation Checks Results

### ✅ Greeks Validation - PASS
- **Delta**: All values in range [-1, 1] ✅
- **Vega**: All values >= 0 ✅
- **Theta**: 8 positive values (unusual but may be valid) ⚠️

### ✅ Implied Volatility Validation - PASS
- **iv**: All values in range [0, 3] ✅
- **iv_estimate**: All values in range [0, 3] ✅
- **Note**: 333 rows have NaN IV (expected for rows without full data)

### ✅ Probabilities Validation - PASS
- **prob_BUY_CE**: All values in range [0, 1] ✅
- **prob_BUY_PE**: All values in range [0, 1] ✅
- **prob_HOLD**: All values in range [0, 1] ✅
- **Probability Sum**: Mean=1.0000, Std=0.0000 ✅ Perfect!

### ⚠️ Moneyness Validation - FAIL
- **330 rows** have moneyness=0.0000 when it should match spot/strike
- **Root Cause**: Calculation error or missing calculation
- **Fix**: Recalculate moneyness as `spot / strike`

---

## 5. Signal Analysis

### Signal Distribution
```
HOLD:  268 rows (44.4%)
SELL:    2 rows ( 0.3%)
NaN:   333 rows (55.2%)
```

**Key Observations**:
1. **Very few SELL signals** (only 2) - Need more data to validate SELL signal quality
2. **No BUY signals** - This aligns with Phase 223 findings (0 BUY candidates)
3. **High NaN rate** - 55% of rows have no signal

### Signal vs Forward Returns Analysis

#### HOLD Signals (268 rows)
- **fwd_ret_1**: Mean=0.0091, Median=0.0000, Std=0.1073
- **fwd_ret_3**: Mean=0.0300, Median=0.0000, Std=0.1660
- **fwd_ret_5**: Mean=0.0547, Median=0.0067, Std=0.1969

**Analysis**: HOLD signals show slightly positive forward returns on average, which is expected (holding during small moves).

#### SELL Signals (2 rows) ⚠️ **SMALL SAMPLE SIZE**
- **fwd_ret_1**: Mean=0.7589, Median=0.7589, Std=1.0732
- **fwd_ret_3**: Mean=1.5178, Median=1.5178, Std=0.0000
- **fwd_ret_5**: Mean=1.5178, Median=1.5178, Std=0.0000

**Analysis**: 
- ⚠️ **CRITICAL ISSUE**: SELL signals have **extremely high positive forward returns**
- This suggests SELL signals are **backwards** - selling when price is about to go up
- However, sample size is too small (only 2 rows) to draw conclusions
- Need more SELL signals to validate

**Hypothesis**: The 2 SELL signals may be:
1. Data errors
2. Incorrectly labeled
3. Edge cases that need review

**Action**: **URGENT** - Review these 2 SELL signal rows manually. If they're valid, investigate why SELL signals have positive forward returns.

### Pred Label Distribution
```
HOLD:        598 rows (99.2%)
pred_label:    3 rows ( 0.5%) ⚠️ Header rows
SELL_CE:       2 rows ( 0.3%)
```

**Issue**: 3 rows have "pred_label" as the value (likely header rows that weren't caught)

**Action**: Remove these 3 rows in addition to the 5 already removed.

---

## 6. Forward Returns Statistics

### fwd_ret_1 (1-day forward returns)
- **Coverage**: 92.9% (560/603)
- **Mean**: 0.008070 (0.8% average return)
- **Std**: 0.097587 (9.8% volatility)
- **Range**: -0.328 to 1.518
- **Outliers**: Max=1.518 (151.8% return) - **EXTREME OUTLIER**

### fwd_ret_3 (3-day forward returns)
- **Coverage**: 80.3% (484/603)
- **Mean**: 0.025256 (2.5% average return)
- **Std**: 0.153503 (15.4% volatility)
- **Range**: -0.312 to 1.518
- **Outliers**: Max=1.518 (151.8% return) - **SAME EXTREME OUTLIER**

### fwd_ret_5 (5-day forward returns)
- **Coverage**: 69.0% (416/603)
- **Mean**: 0.045797 (4.6% average return)
- **Std**: 0.182606 (18.3% volatility)
- **Range**: -0.365 to 1.518
- **Outliers**: Max=1.518 (151.8% return) - **SAME EXTREME OUTLIER**

### ⚠️ Extreme Outlier Detection

**Issue**: One or more rows have `fwd_ret_1`, `fwd_ret_3`, and `fwd_ret_5` all equal to **1.517751** (151.8% return).

**Impact**:
- **HIGH** - This is an unrealistic return for options
- Will skew EV analysis significantly
- Likely a data error or calculation error

**Action**: **URGENT** - Identify and review rows with `fwd_ret_1 > 1.0` or `fwd_ret_3 > 1.0` or `fwd_ret_5 > 1.0`. These are likely errors.

**Code to Find Outliers**:
```python
extreme_outliers = df[
    (df['fwd_ret_1'].abs() > 1.0) | 
    (df['fwd_ret_3'].abs() > 1.0) | 
    (df['fwd_ret_5'].abs() > 1.0)
]
print(f"Extreme outliers: {len(extreme_outliers)} rows")
```

---

## 7. Recommendations

### Immediate Actions (Critical)

1. **Fix Moneyness Calculation** 🔴
   - Recalculate moneyness as `spot / strike` for all rows
   - Update signal generation pipeline to ensure moneyness is always calculated
   - Re-run validation after fix

2. **Review SELL Signal Forward Returns** 🔴
   - The 2 SELL signals have extremely high positive forward returns (151.8%)
   - This suggests either:
     - Data error
     - Incorrect signal labeling
     - Backwards logic (selling when should buy)
   - **Action**: Review these 2 rows manually and investigate signal generation logic

3. **Remove Extreme Outliers** 🔴
   - Identify rows with forward returns > 100% (abs > 1.0)
   - Review these rows manually
   - Either fix the data or remove from analysis

4. **Remove Additional Header Rows** 🟡
   - Remove 3 rows where `pred_label == "pred_label"`
   - These are duplicate header rows that weren't caught

### Data Quality Improvements

5. **Filter for EV Analysis**
   - Use only rows with complete forward returns (416 rows)
   - This ensures consistent EV analysis across all time horizons

6. **Investigate Missing Signals**
   - 55% of rows have no signal
   - Determine if this is expected or indicates a problem
   - Check signal generation logic

7. **Increase Signal Diversity**
   - Currently only 2 SELL signals (0.3%)
   - Need more SELL signals to validate SELL signal quality
   - Consider adjusting thresholds if SELL signals are too rare

### For Model Training

8. **Create Clean Training Dataset**
   - Filter to rows with:
     - Complete forward returns (all 3)
     - Valid signals (not NaN)
     - Correct moneyness (recalculated)
     - No extreme outliers
   - This should give ~200-300 clean rows for training

9. **Handle Missing Data**
   - 45% of rows have complete data (Greeks, IV, indicators)
   - Consider:
     - Using only complete rows for training
     - Or imputing missing values
     - Or using separate models for complete vs incomplete rows

### For Backtesting

10. **Temporal Validation**
    - Ensure forward returns are from future time points
    - Verify no lookahead bias
    - Validate timestamp ordering

---

## 8. Data Quality Scorecard

| Category | Status | Score | Notes |
|----------|--------|-------|-------|
| **Schema** | ✅ PASS | 10/10 | All columns present, no duplicates |
| **Type Conversion** | ✅ PASS | 9/10 | 47 columns converted, minimal data loss |
| **Greeks Validation** | ⚠️ WARN | 8/10 | 8 positive theta (may be valid) |
| **IV Validation** | ✅ PASS | 10/10 | All values in valid range |
| **Probabilities** | ✅ PASS | 10/10 | Perfect sum to 1.0 |
| **Moneyness** | 🔴 FAIL | 2/10 | 330 rows incorrect (0.0000) |
| **Forward Returns** | ⚠️ WARN | 7/10 | Good coverage but extreme outliers |
| **Signal Quality** | ⚠️ WARN | 5/10 | 55% NaN, only 2 SELL signals |
| **Overall** | ⚠️ **NEEDS FIXES** | **6.5/10** | Critical issues must be addressed |

---

## 9. Next Steps

### Phase 1: Critical Fixes (Do First)
1. ✅ Fix moneyness calculation
2. ✅ Remove extreme outliers (forward returns > 100%)
3. ✅ Review SELL signal forward returns
4. ✅ Remove additional header rows (pred_label == "pred_label")

### Phase 2: Data Quality (Do Second)
5. ✅ Re-run validation after fixes
6. ✅ Filter to clean dataset for EV analysis
7. ✅ Investigate missing signals (55% NaN)

### Phase 3: Analysis (Do Third)
8. ✅ Run Phase 222 (EV analysis) on clean dataset
9. ✅ Run Phase 223 (threshold optimization) with validated data
10. ✅ Generate training dataset for model training

---

## 10. Conclusion

The CSV file has a **solid structure** but requires **critical fixes** before use:

**Critical Issues**:
1. 🔴 Moneyness calculation error (330 rows)
2. 🔴 Extreme outliers in forward returns (151.8% return)
3. 🔴 SELL signals have backwards forward returns (need investigation)

**Data Quality**:
- ✅ Schema is correct
- ✅ Type conversion successful
- ✅ Most validations pass
- ⚠️ Signal generation needs improvement (55% NaN)

**Recommendation**: 
- **DO NOT USE** for EV analysis or threshold optimization until critical issues are fixed
- **FIX CRITICAL ISSUES FIRST** (moneyness, outliers, SELL signals)
- **RE-RUN VALIDATION** after fixes
- **THEN PROCEED** with Phase 222 and 223

---

**Report Generated**: 2025-12-04  
**Next Review**: After applying critical fixes

