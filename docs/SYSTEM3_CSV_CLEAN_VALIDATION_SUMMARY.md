# System3 Clean CSV Validation Summary
**Generated**: 2025-12-04 21:34:56

## File Summary

- **Clean CSV Rows**: 596
- **EV-Ready CSV Rows**: 232
- **SELL Anomalies**: 2

## Validation Results

### Greeks Validation

- **Delta**: ✅ PASS
  - Out of range [-1, 1]: 0 rows
- **Vega**: ✅ PASS
  - Negative values: 0 rows
- **Theta**: ✅ PASS
  - Positive values: 8 rows
  - Large positive (>10): 0 rows

### Implied Volatility Validation

- **IV**: ✅ PASS
  - Out of range [0, 3]: 0 rows
- **IV Estimate**: ✅ PASS
  - Out of range [0, 3]: 0 rows

### Probabilities Validation

- **Individual Probabilities**: ✅ PASS
  - Out of range [0, 1]: 0 rows
- **Probability Sum**: ✅ PASS
  - Mean: 1.0000
  - Std: 0.0000
  - Bad sums (|sum - 1| > 0.05): 0 rows

### Moneyness Validation

- **Status**: ✅ PASS
  - Zero values (should be rare): 0 rows
  - Inconsistent with spot/strike: 0 rows

### Forward Returns Validation

- **Coverage**:
  - fwd_ret_1: 93.3%
  - fwd_ret_3: 80.5%
  - fwd_ret_5: 69.1%
- **Outliers (|ret| > 1.0)**: ✅ PASS
  - Outlier count: 0 rows

## Critical Issues Resolution

### Moneyness Fix
- ✅ Moneyness recalculated as spot/strike
- Zero values: 0 (should be 0 or very low)

### Outlier Removal
- ✅ Rows with |forward_return| > 1.0 removed
- Outliers remaining: 0 (should be 0)

### SELL Signal Anomalies
- ⚠️ Anomalies detected: 2 rows
- Saved to: `storage/clean/angel_index_ai_signals_sell_anomalies.csv`
- **Action Required**: Review these rows manually

## Overall Status

✅ **ALL VALIDATIONS PASSED** - Clean CSV is ready for use

## Next Steps

1. Review SELL anomalies if any detected
2. Use `storage/clean/angel_index_ai_signals_with_forward_clean.csv` for general analysis
3. Use `storage/clean/angel_index_ai_signals_with_forward_ev_ready.csv` for EV analysis and training
