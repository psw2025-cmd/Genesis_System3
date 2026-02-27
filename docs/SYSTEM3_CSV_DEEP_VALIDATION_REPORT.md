# System3 CSV Deep Validation Report
**Generated**: 2025-12-04 21:00:57  
**File**: `angel_index_ai_signals_with_forward.csv`  
**Status**: ⚠️ **DATA QUALITY ISSUES DETECTED**

## Executive Summary

- **Total Rows**: 608 (original), 603 (after cleaning)
- **Total Columns**: 89
- **Duplicate Headers Removed**: 5 rows (signal='signal')
- **Type Conversions**: 47 columns converted to numeric
- **New Nulls Created**: 220 total
- **Data Quality Issues**: 1 critical (moneyness inconsistency: 330 rows)

## Critical Findings

### 🔴 CRITICAL: Moneyness Inconsistency (330 rows, 54.7%)
- **Issue**: 330 rows have `moneyness=0.0000` when it should equal `spot/strike`
- **Fix**: Recalculate as `df['moneyness'] = df['spot'] / df['strike']`
- **Impact**: HIGH - Affects options analysis accuracy

### 🔴 CRITICAL: Extreme Outliers in Forward Returns
- **Issue**: Rows with forward returns > 151% (1.517751)
- **Impact**: HIGH - Will skew EV analysis significantly
- **Action**: Identify and review rows with `abs(fwd_ret) > 1.0`

### 🟡 MEDIUM: Missing Signals (333 rows, 55.2%)
- **Issue**: 55% of rows have NaN signals
- **Impact**: MEDIUM - Cannot perform signal-based EV analysis
- **Distribution**: HOLD: 268 (44.4%), SELL: 2 (0.3%), NaN: 333 (55.2%)

### 🟡 MEDIUM: SELL Signal Anomaly
- **Issue**: 2 SELL signals have extremely high positive forward returns (151.8%)
- **Impact**: MEDIUM - Suggests backwards logic or data error
- **Action**: Review these 2 rows manually

## Data Quality Metrics

### Forward Returns Coverage
- `fwd_ret_1`: 560 values (92.9%) ✅ Good
- `fwd_ret_3`: 484 values (80.3%) ⚠️ Moderate  
- `fwd_ret_5`: 416 values (69.0%) ⚠️ Low

### Validation Results
- ✅ Greeks: Delta [-1,1], Vega >= 0, Theta mostly <= 0 (8 positive)
- ✅ IV: All values in range [0, 3]
- ✅ Probabilities: Perfect sum to 1.0 (Mean=1.0000, Std=0.0000)
- ⚠️ Moneyness: 330 rows incorrect (0.0000 instead of spot/strike)

### Signal Distribution
- HOLD: 268 rows (44.4%)
- SELL: 2 rows (0.3%) ⚠️ Too few for validation
- NaN: 333 rows (55.2%) ⚠️ High missing rate

## Detailed Analysis

See `docs/SYSTEM3_CSV_DEEP_VALIDATION_ANALYSIS.md` for comprehensive analysis.

## Immediate Actions Required

1. **🔴 URGENT**: Fix moneyness calculation
   ```python
   df['moneyness'] = df['spot'] / df['strike']
   ```

2. **🔴 URGENT**: Remove extreme outliers
   ```python
   df_clean = df[(df['fwd_ret_1'].abs() <= 1.0) & 
                 (df['fwd_ret_3'].abs() <= 1.0) & 
                 (df['fwd_ret_5'].abs() <= 1.0)]
   ```

3. **🔴 URGENT**: Review SELL signal forward returns (2 rows with 151.8% returns)

4. **🟡 MEDIUM**: Remove additional header rows (3 rows where pred_label == "pred_label")

5. **🟡 MEDIUM**: Investigate missing signals (55% NaN rate)

## Recommendations

1. ✅ Filter to rows with complete forward returns for EV analysis (416 rows available)
2. ✅ Remove rows with extreme outliers in forward returns
3. ✅ Fix moneyness calculation before any analysis
4. ✅ Review SELL signal logic (backwards forward returns)
5. ✅ Use only complete rows (with all features) for model training
6. ✅ Ensure forward returns are from future snapshots (no lookahead bias)

## Next Steps

**DO NOT USE** for EV analysis or threshold optimization until critical issues are fixed.

1. Fix critical issues (moneyness, outliers, SELL signals)
2. Re-run validation: `run_deep_validation.bat`
3. Review analysis: `docs/SYSTEM3_CSV_DEEP_VALIDATION_ANALYSIS.md`
4. Proceed with Phase 222 and 223 only after fixes are applied
