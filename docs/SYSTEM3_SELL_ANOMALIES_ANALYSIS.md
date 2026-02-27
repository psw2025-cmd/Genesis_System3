# System3 SELL Signal Anomalies Analysis

**Date**: 2025-12-04  
**File**: `storage/clean/angel_index_ai_signals_sell_anomalies.csv`  
**Anomaly Count**: 2 rows

---

## Summary

Two SELL signals were detected with **extremely high positive forward returns** (151.8%), which is contradictory - SELL signals should have negative or neutral forward returns if the signal is correct.

---

## Anomaly Details

### Row 1
- **Underlying**: NIFTY
- **Strike**: 26250.0
- **Side**: CE (Call)
- **Symbol**: NIFTY02DEC2526250CE
- **Timestamp**: 2025-12-01 18:07:36.025676
- **Signal**: SELL
- **Pred Label**: SELL_CE
- **Spot**: 26175.75
- **Strike**: 26250.0
- **Moneyness**: 0.9971714285714286 (slightly OTM)
- **Final Score**: -0.3547046525816979 (negative, indicating SELL)
- **Forward Returns**:
  - `fwd_ret_1`: 0.0 (missing)
  - `fwd_ret_3`: 1.517751479289941 (151.8% - **EXTREME**)
  - `fwd_ret_5`: 1.517751479289941 (151.8% - **EXTREME**)

### Row 2
- **Underlying**: NIFTY
- **Strike**: 26250.0
- **Side**: CE (Call)
- **Symbol**: NIFTY02DEC2526250CE
- **Timestamp**: 2025-12-01 19:05:49.452158
- **Signal**: SELL
- **Pred Label**: SELL_CE
- **Spot**: 26175.75
- **Strike**: 26250.0
- **Moneyness**: 0.9971714285714286 (slightly OTM)
- **Final Score**: -0.3355864492757249 (negative, indicating SELL)
- **Forward Returns**:
  - `fwd_ret_1`: 1.517751479289941 (151.8% - **EXTREME**)
  - `fwd_ret_3`: 1.517751479289941 (151.8% - **EXTREME**)
  - `fwd_ret_5`: 1.517751479289941 (151.8% - **EXTREME**)

---

## Key Observations

1. **Same Option**: Both anomalies are for the **exact same option** (NIFTY 26250 CE, expiry 02DEC2025)
2. **Different Timestamps**: One at 18:07:36, one at 19:05:49 (same day, ~1 hour apart)
3. **Extreme Returns**: Both have forward returns of **151.8%**, which is unrealistic for options
4. **Signal Logic**: Both have negative `final_score` (-0.35, -0.34), correctly indicating SELL
5. **Contradiction**: SELL signal with 151.8% positive forward return means:
   - Signal said "SELL" (price should go down)
   - But price actually went **UP by 151.8%**
   - This suggests either:
     - **Data error** in forward returns calculation
     - **Signal was wrong** (should have been BUY, not SELL)
     - **Forward returns are incorrect** (possibly from wrong option or wrong time)

---

## Root Cause Analysis

### Hypothesis 1: Forward Returns Calculation Error
- **Likelihood**: HIGH
- **Evidence**: 151.8% return is unrealistic for a 1-day, 3-day, or 5-day period
- **Possible Causes**:
  - Forward returns calculated from wrong option
  - Forward returns calculated from wrong timestamp
  - Division error or unit conversion error
  - Data corruption

### Hypothesis 2: Signal Logic Error
- **Likelihood**: LOW
- **Evidence**: Both signals have consistent negative `final_score` (-0.35, -0.34)
- **Possible Causes**:
  - Signal generation logic incorrectly labeled as SELL when should be BUY
  - But this doesn't explain the extreme forward returns

### Hypothesis 3: Data Corruption
- **Likelihood**: MEDIUM
- **Evidence**: Both rows have identical forward return values (1.517751479289941)
- **Possible Causes**:
  - Forward returns copied incorrectly
  - Default value used instead of actual calculation
  - CSV corruption during write

---

## Impact Assessment

### On EV Analysis
- **Impact**: LOW (only 2 rows out of 232 EV-ready rows)
- **Mitigation**: These rows were correctly excluded from EV-ready CSV
- **Status**: ✅ Handled correctly

### On Signal Quality
- **Impact**: MEDIUM (only 2 SELL signals in entire dataset)
- **Concern**: If these are the only SELL signals, we can't validate SELL signal quality
- **Status**: ⚠️ Need more SELL signals to validate

### On System Reliability
- **Impact**: LOW (anomalies detected and isolated)
- **Status**: ✅ System correctly identified and isolated anomalies

---

## Recommendations

### Immediate Actions

1. **✅ DONE**: Anomalies isolated in separate CSV file
2. **✅ DONE**: Excluded from EV-ready CSV (correctly handled)
3. **⚠️ TODO**: Investigate forward returns calculation for this specific option
4. **⚠️ TODO**: Verify if forward returns are correct by checking:
   - Actual option price at forward timestamps
   - Whether forward returns are from correct option
   - Whether timestamps are correct

### Long-term Actions

1. **Add Forward Returns Validation**:
   - Flag forward returns > 50% as suspicious
   - Cross-validate forward returns with actual market data
   - Add unit tests for forward returns calculation

2. **Improve SELL Signal Generation**:
   - Generate more SELL signals to validate quality
   - Review SELL signal thresholds
   - Ensure SELL signals have negative or neutral forward returns

3. **Data Quality Monitoring**:
   - Add automated checks for extreme forward returns
   - Alert on forward returns > 100%
   - Track forward returns distribution over time

---

## Conclusion

The SELL anomalies are **correctly identified and isolated**. The extreme forward returns (151.8%) are likely **data errors** rather than actual market movements. The cleaning pipeline correctly:

1. ✅ Detected the anomalies
2. ✅ Saved them for manual review
3. ✅ Excluded them from EV-ready CSV
4. ✅ Preserved them for investigation

**Status**: ✅ **Handled Correctly** - No action required for EV analysis, but should investigate root cause for data quality improvement.

---

**Next Steps**: Proceed with EV analysis using the clean EV-ready CSV (232 rows, no anomalies).

