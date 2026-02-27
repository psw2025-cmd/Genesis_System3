# Signal Schema Normalization - Phase 370

**Generated:** 2025-12-10 07:51:57

---

## Summary

**Files Processed:** 2
**Files Repaired:** 2
**Status:** OK

---

## Repair Results

### ❌ angel_index_ai_signals.csv

**Status:** not_found
**Rows Before:** 0
**Rows After:** 0

**Error:** File does not exist

### ✅ angel_index_ai_signals_curated.csv

**Status:** ok
**Backup Created:** ✅ Yes
**Backup Path:** `C:\Genesis_System3\storage\live\raw_backup\angel_index_ai_signals_curated_backup_20251210_075156.csv`
**Normalized:** ✅ Yes
**Clean File:** `C:\Genesis_System3\storage\live\clean\angel_index_ai_signals_curated_clean.csv`
**Columns Removed:** side, ts, moneyness, iv_estimate, iv_percentile, iv_rank, iv_change_rate, iv_spike, rsi, macd, macd_signal, macd_histogram, sma_5, sma_10, sma_20, supertrend, supertrend_direction, vwap, price_vs_vwap, trend_score, multi_tf_trend_score, trend_strength, trend_1m, trend_3m, trend_5m, trend_15m, momentum_score, breakout_score, roc_1, roc_3, roc_5, roc_10, acceleration, momentum_strength, momentum_direction, volatility_regime, volatility_score, regime_transition, ml_prediction, ml_probability, ai_score, prob_BUY_CE, prob_BUY_PE, prob_HOLD, greeks_score, final_score, signal_strength, entry_buy, entry_sell, entry_hold, entry_confidence, entry_price, stop_loss, target_price, risk_amount, trailing_sl, exit_sl_hit, exit_target_hit, exit_signal, ce_pe_ratio, atm_dist_pct, atm_dist_abs, ce_pe_diff, spot_chg_1_pct, ltp_chg_1_pct, reconciled_label, index_exch, opt_exch, token, expected_move_score, pred_confidence, spot_roll_std_5, ltp_roll_std_5, u_moneyness_sq, u_moneyness_cube, u_moneyness_sqrt, u_momentum_1, u_momentum_3, u_momentum_5, u_momentum_10, u_spot_momentum_1, u_spot_momentum_3, u_spot_momentum_5, u_spot_momentum_10, u_momentum_ratio_1_5, u_vol_short, u_vol_long, u_vol_ratio, u_spot_vol_short, u_spot_vol_long, u_spot_vol_ratio, u_regime_high_vol, u_regime_low_vol, u_hour, u_minute, u_moneyness_x_score, u_moneyness_x_conf, u_score_x_conf, u_is_win, u_rolling_win_rate_5, u_rolling_win_rate_10, u_ltp_percentile
**Rows Before:** 297
**Rows After:** 297

**Issues Detected:**
- Extra columns: iv_percentile, entry_price, u_spot_momentum_10, u_minute, momentum_strength, ce_pe_ratio, trend_strength, multi_tf_trend_score, trend_5m, iv_spike, trend_score, prob_BUY_CE, iv_estimate, volatility_score, price_vs_vwap, u_momentum_1, ltp_chg_1_pct, reconciled_label, final_score, breakout_score, ai_score, roc_3, atm_dist_pct, exit_target_hit, vwap, u_rolling_win_rate_10, u_spot_momentum_1, entry_confidence, u_moneyness_cube, u_spot_vol_long, u_momentum_3, spot_roll_std_5, acceleration, u_spot_vol_ratio, exit_sl_hit, ts, u_momentum_ratio_1_5, macd, u_moneyness_sq, u_spot_momentum_3, ml_prediction, trend_1m, trailing_sl, macd_signal, ce_pe_diff, prob_HOLD, momentum_direction, expected_move_score, token, target_price, entry_hold, trend_3m, roc_10, u_vol_short, supertrend_direction, risk_amount, u_moneyness_sqrt, u_vol_long, volatility_regime, regime_transition, u_rolling_win_rate_5, u_ltp_percentile, entry_buy, u_momentum_10, pred_confidence, spot_chg_1_pct, u_hour, roc_5, opt_exch, roc_1, ml_probability, u_spot_vol_short, sma_20, prob_BUY_PE, index_exch, u_score_x_conf, trend_15m, exit_signal, greeks_score, u_is_win, macd_histogram, ltp_roll_std_5, u_vol_ratio, moneyness, u_spot_momentum_5, iv_rank, iv_change_rate, momentum_score, sma_5, sma_10, u_regime_high_vol, stop_loss, signal_strength, atm_dist_abs, side, u_momentum_5, rsi, u_moneyness_x_score, supertrend, u_moneyness_x_conf, entry_sell, u_regime_low_vol

### ✅ angel_index_ai_signals_with_forward.csv

**Status:** ok
**Backup Created:** ✅ Yes
**Backup Path:** `C:\Genesis_System3\storage\live\raw_backup\angel_index_ai_signals_with_forward_backup_20251210_075157.csv`
**Normalized:** ✅ Yes
**Clean File:** `C:\Genesis_System3\storage\live\clean\angel_index_ai_signals_with_forward_clean.csv`
**Columns Removed:** side, ts, moneyness, iv_estimate, iv_percentile, iv_rank, iv_change_rate, iv_spike, rsi, macd, macd_signal, macd_histogram, sma_5, sma_10, sma_20, supertrend, supertrend_direction, vwap, price_vs_vwap, trend_score, multi_tf_trend_score, trend_strength, trend_1m, trend_3m, trend_5m, trend_15m, momentum_score, breakout_score, roc_1, roc_3, roc_5, roc_10, acceleration, momentum_strength, momentum_direction, volatility_regime, volatility_score, regime_transition, ml_prediction, ml_probability, ai_score, prob_BUY_CE, prob_BUY_PE, prob_HOLD, greeks_score, final_score, signal_strength, entry_buy, entry_sell, entry_hold, entry_confidence, entry_price, stop_loss, target_price, risk_amount, trailing_sl, exit_sl_hit, exit_target_hit, exit_signal, ce_pe_ratio, atm_dist_pct, atm_dist_abs, ce_pe_diff, spot_chg_1_pct, ltp_chg_1_pct, reconciled_label, index_exch, opt_exch, token, expected_move_score, pred_confidence, spot_roll_std_5, ltp_roll_std_5, u_moneyness_sq, u_moneyness_cube, u_moneyness_sqrt, u_momentum_1, u_momentum_3, u_momentum_5, u_momentum_10, u_spot_momentum_1, u_spot_momentum_3, u_spot_momentum_5, u_spot_momentum_10, u_momentum_ratio_1_5, u_vol_short, u_vol_long, u_vol_ratio, u_spot_vol_short, u_spot_vol_long, u_spot_vol_ratio, u_regime_high_vol, u_regime_low_vol, u_hour, u_minute, u_moneyness_x_score, u_moneyness_x_conf, u_score_x_conf, u_is_win, u_rolling_win_rate_5, u_rolling_win_rate_10, u_ltp_percentile, fwd_ret_10, fwd_ret_15
**Rows Before:** 2415
**Rows After:** 2415

**Issues Detected:**
- Extra columns: fwd_ret_10, trend_strength, iv_spike, prob_BUY_CE, volatility_score, price_vs_vwap, entry_confidence, u_moneyness_cube, u_spot_vol_long, u_momentum_3, acceleration, exit_sl_hit, u_moneyness_sq, trend_1m, ce_pe_diff, momentum_direction, expected_move_score, target_price, entry_hold, supertrend_direction, u_moneyness_sqrt, u_vol_long, volatility_regime, u_rolling_win_rate_5, u_ltp_percentile, entry_buy, u_momentum_10, pred_confidence, spot_chg_1_pct, roc_5, ml_probability, u_spot_vol_short, sma_20, prob_BUY_PE, index_exch, u_score_x_conf, trend_15m, exit_signal, macd_histogram, ltp_roll_std_5, moneyness, iv_rank, iv_change_rate, stop_loss, signal_strength, atm_dist_abs, side, rsi, u_momentum_5, supertrend, u_spot_momentum_5, u_moneyness_x_score, u_regime_low_vol, iv_percentile, entry_price, u_minute, ce_pe_ratio, multi_tf_trend_score, trend_5m, trend_score, u_momentum_1, ltp_chg_1_pct, reconciled_label, breakout_score, ai_score, roc_3, atm_dist_pct, exit_target_hit, vwap, u_rolling_win_rate_10, fwd_ret_15, u_spot_momentum_1, spot_roll_std_5, u_spot_vol_ratio, ts, u_momentum_ratio_1_5, macd, u_spot_momentum_3, ml_prediction, trailing_sl, macd_signal, prob_HOLD, token, trend_3m, roc_10, u_moneyness_x_conf, risk_amount, regime_transition, u_hour, opt_exch, roc_1, greeks_score, u_is_win, u_vol_ratio, momentum_score, sma_5, sma_10, u_spot_momentum_10, entry_sell, u_vol_short, u_regime_high_vol, final_score, momentum_strength, iv_estimate

---

## Next Steps

1. Review cleaned files in `storage/live/clean/`
2. Run Phase 371 (Duplicate Scanner) on cleaned files
3. Original files backed up in `storage/live/raw_backup/`
