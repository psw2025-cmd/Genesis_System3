# SIGNAL PIPELINE SNAPSHOT — PHASE 361

**Generated:** 2025-12-10T07:51:55.489371  
**Status:** OK  
**Message:** 2722 signals across 3 files  

## Summary

- **Files Analyzed:** 4
- **Files Found:** 3
- **Total Signal Rows:** 2722
- **Issues Detected:** 2

## File Analysis

### signals

❌ **File not found**

### curated

✅ **File exists**

- **Rows:** 297
- **Columns:** 126
- **Signal Distribution:**
  - HOLD: 247
  - BUY_CE: 8
  - SELL: 6
  - BUY: 5
- **Unique Symbols:** 196
- **Underlyings:** NIFTY, SENSEX, FINNIFTY, BANKNIFTY, MIDCPNIFTY, 0.0
- **Issues:**
  - ⚠️ High missing values (>50%): ['fwd_ret_1', 'fwd_ret_3', 'fwd_ret_5', 'reconciled_label', 'index_exch', 'opt_exch', 'token', 'expected_move_score', 'pred_confidence', 'spot_roll_std_5', 'ltp_roll_std_5', 'u_moneyness_sq', 'u_moneyness_cube', 'u_moneyness_sqrt', 'u_momentum_1', 'u_momentum_3', 'u_momentum_5', 'u_momentum_10', 'u_spot_momentum_1', 'u_spot_momentum_3', 'u_spot_momentum_5', 'u_spot_momentum_10', 'u_momentum_ratio_1_5', 'u_vol_short', 'u_vol_long', 'u_vol_ratio', 'u_spot_vol_short', 'u_spot_vol_long', 'u_spot_vol_ratio', 'u_regime_high_vol', 'u_regime_low_vol', 'u_hour', 'u_minute', 'confidence', 'u_moneyness_x_score', 'u_moneyness_x_conf', 'u_score_x_conf', 'u_is_win', 'u_rolling_win_rate_5', 'u_rolling_win_rate_10', 'u_ltp_percentile', 'fwd_ret_2', 'timestamp', 'score', 'pred_proba', 'rho', 'data_source']

### with_forward

✅ **File exists**

- **Rows:** 2415
- **Columns:** 128
- **Signal Distribution:**
  - HOLD: 1998
  - SELL: 149
  - BUY: 84
  - BUY_CE: 41
  - signal: 15
- **Unique Symbols:** 197
- **Underlyings:** 0.0, underlying, MIDCPNIFTY, FINNIFTY, BANKNIFTY, NIFTY, SENSEX
- **Issues:**
  - ⚠️ High missing values (>50%): ['moneyness', 'vwap', 'ml_prediction', 'ml_probability', 'prob_BUY_CE', 'prob_BUY_PE', 'prob_HOLD', 'ce_pe_ratio', 'atm_dist_pct', 'atm_dist_abs', 'ce_pe_diff', 'spot_chg_1_pct', 'ltp_chg_1_pct', 'fwd_ret_3', 'reconciled_label', 'spot_roll_std_5', 'ltp_roll_std_5', 'u_moneyness_sq', 'u_moneyness_cube', 'u_moneyness_sqrt', 'u_momentum_1', 'u_momentum_3', 'u_momentum_5', 'u_momentum_10', 'u_spot_momentum_1', 'u_spot_momentum_3', 'u_spot_momentum_5', 'u_spot_momentum_10', 'u_momentum_ratio_1_5', 'u_vol_short', 'u_vol_long', 'u_vol_ratio', 'u_spot_vol_short', 'u_spot_vol_long', 'u_spot_vol_ratio', 'u_regime_high_vol', 'u_regime_low_vol', 'u_hour', 'u_minute', 'confidence', 'u_moneyness_x_score', 'u_moneyness_x_conf', 'u_score_x_conf', 'u_is_win', 'u_rolling_win_rate_5', 'u_rolling_win_rate_10', 'u_ltp_percentile', 'timestamp', 'score', 'pred_proba', 'rho', 'data_source']

### virtual_orders

✅ **File exists**

- **Rows:** 10
- **Columns:** 12
- **Unique Symbols:** 5

