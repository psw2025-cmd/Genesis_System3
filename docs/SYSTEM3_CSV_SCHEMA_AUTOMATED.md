# System3 CSV Schema Audit - Automated Report
**Generated**: 2025-12-04 21:34:54
**File**: `dhan_index_ai_signals_with_forward.csv`

## Schema Overview

- **Total Rows**: 608
- **Total Columns**: 89

## Column List

| # | Column Name | Data Type | Non-Null Count | Null % |
|---|-------------|-----------|----------------|--------|
| 1 | `underlying` | object | 608 | 0.0% |
| 2 | `index_exch` | object | 608 | 0.0% |
| 3 | `opt_exch` | object | 608 | 0.0% |
| 4 | `spot` | object | 608 | 0.0% |
| 5 | `expiry` | object | 608 | 0.0% |
| 6 | `strike` | float64 | 600 | 1.3% |
| 7 | `side` | object | 608 | 0.0% |
| 8 | `symbol` | object | 608 | 0.0% |
| 9 | `token` | object | 608 | 0.0% |
| 10 | `ltp` | float64 | 600 | 1.3% |
| 11 | `time_to_expiry` | object | 275 | 54.8% |
| 12 | `iv_estimate` | object | 275 | 54.8% |
| 13 | `iv` | object | 275 | 54.8% |
| 14 | `delta` | object | 275 | 54.8% |
| 15 | `gamma` | object | 275 | 54.8% |
| 16 | `theta` | object | 275 | 54.8% |
| 17 | `vega` | object | 275 | 54.8% |
| 18 | `trend_score` | object | 275 | 54.8% |
| 19 | `multi_tf_trend_score` | object | 275 | 54.8% |
| 20 | `rsi` | object | 275 | 54.8% |
| 21 | `macd` | object | 275 | 54.8% |
| 22 | `macd_signal` | object | 275 | 54.8% |
| 23 | `macd_histogram` | object | 275 | 54.8% |
| 24 | `vwap` | object | 5 | 99.2% |
| 25 | `price_vs_vwap` | object | 275 | 54.8% |
| 26 | `supertrend` | object | 275 | 54.8% |
| 27 | `supertrend_direction` | object | 275 | 54.8% |
| 28 | `sma_5` | object | 275 | 54.8% |
| 29 | `sma_10` | object | 275 | 54.8% |
| 30 | `sma_20` | object | 275 | 54.8% |
| 31 | `trend_strength` | object | 275 | 54.8% |
| 32 | `trend_1m` | object | 275 | 54.8% |
| 33 | `trend_3m` | object | 275 | 54.8% |
| 34 | `trend_5m` | object | 275 | 54.8% |
| 35 | `trend_15m` | object | 275 | 54.8% |
| 36 | `iv_percentile` | object | 275 | 54.8% |
| 37 | `iv_rank` | object | 275 | 54.8% |
| 38 | `volatility_regime` | object | 275 | 54.8% |
| 39 | `volatility_score` | object | 275 | 54.8% |
| 40 | `iv_change_rate` | object | 275 | 54.8% |
| 41 | `iv_spike` | object | 275 | 54.8% |
| 42 | `regime_transition` | object | 275 | 54.8% |
| 43 | `breakout_score` | object | 275 | 54.8% |
| 44 | `momentum_score` | object | 275 | 54.8% |
| 45 | `roc_1` | object | 275 | 54.8% |
| 46 | `roc_3` | object | 275 | 54.8% |
| 47 | `roc_5` | object | 275 | 54.8% |
| 48 | `roc_10` | object | 275 | 54.8% |
| 49 | `acceleration` | object | 275 | 54.8% |
| 50 | `momentum_strength` | object | 275 | 54.8% |
| 51 | `momentum_direction` | object | 275 | 54.8% |
| 52 | `ml_prediction` | float64 | 30 | 95.1% |
| 53 | `ml_probability` | float64 | 30 | 95.1% |
| 54 | `ai_score` | object | 275 | 54.8% |
| 55 | `greeks_score` | object | 275 | 54.8% |
| 56 | `final_score` | object | 275 | 54.8% |
| 57 | `signal` | object | 275 | 54.8% |
| 58 | `signal_strength` | object | 275 | 54.8% |
| 59 | `entry_buy` | object | 275 | 54.8% |
| 60 | `entry_sell` | object | 275 | 54.8% |
| 61 | `entry_hold` | object | 275 | 54.8% |
| 62 | `entry_confidence` | object | 275 | 54.8% |
| 63 | `stop_loss` | object | 275 | 54.8% |
| 64 | `target_price` | object | 275 | 54.8% |
| 65 | `risk_amount` | object | 275 | 54.8% |
| 66 | `entry_price` | object | 275 | 54.8% |
| 67 | `exit_sl_hit` | object | 275 | 54.8% |
| 68 | `exit_target_hit` | object | 275 | 54.8% |
| 69 | `trailing_sl` | object | 275 | 54.8% |
| 70 | `exit_signal` | object | 275 | 54.8% |
| 71 | `ts` | object | 270 | 55.6% |
| 72 | `pred_label` | object | 608 | 0.0% |
| 73 | `expected_move_score` | object | 608 | 0.0% |
| 74 | `pred_confidence` | object | 608 | 0.0% |
| 75 | `moneyness` | object | 333 | 45.2% |
| 76 | `ce_pe_ratio` | object | 333 | 45.2% |
| 77 | `atm_dist_pct` | object | 333 | 45.2% |
| 78 | `atm_dist_abs` | object | 333 | 45.2% |
| 79 | `ce_pe_diff` | object | 333 | 45.2% |
| 80 | `spot_chg_1_pct` | object | 333 | 45.2% |
| 81 | `ltp_chg_1_pct` | object | 333 | 45.2% |
| 82 | `spot_roll_std_5` | object | 333 | 45.2% |
| 83 | `ltp_roll_std_5` | object | 333 | 45.2% |
| 84 | `prob_BUY_CE` | object | 333 | 45.2% |
| 85 | `prob_BUY_PE` | object | 333 | 45.2% |
| 86 | `prob_HOLD` | object | 333 | 45.2% |
| 87 | `fwd_ret_1` | float64 | 560 | 7.9% |
| 88 | `fwd_ret_3` | float64 | 484 | 20.4% |
| 89 | `fwd_ret_5` | float64 | 416 | 31.6% |

## Bad Rows Detected

### Duplicate Header Rows: 8

Row indices with duplicate headers:
- Row 64: signal='signal', pred_label='pred_label'
- Row 275: signal='nan', pred_label='pred_label'
- Row 276: signal='nan', pred_label='pred_label'
- Row 277: signal='nan', pred_label='pred_label'
- Row 30: signal='signal', pred_label='pred_label'
- Row 31: signal='signal', pred_label='pred_label'
- Row 62: signal='signal', pred_label='pred_label'
- Row 63: signal='signal', pred_label='pred_label'

### Invalid Rows (All NaN): 0

None detected.

## Column Categories

### Identifiers / Keys (8 columns)

`underlying`, `index_exch`, `opt_exch`, `expiry`, `strike`, `side`, `symbol`, `token`

### Market Data (5 columns)

`spot`, `ltp`, `time_to_expiry`, `iv_estimate`, `iv`

### Greeks (4 columns)

`delta`, `gamma`, `theta`, `vega`

### Technical Indicators (18 columns)

`trend_score`, `multi_tf_trend_score`, `rsi`, `macd`, `macd_signal`, `macd_histogram`, `vwap`, `price_vs_vwap`, `supertrend`, `supertrend_direction`, `sma_5`, `sma_10`, `sma_20`, `trend_strength`, `trend_1m`, `trend_3m`, `trend_5m`, `trend_15m`

### Volatility Metrics (7 columns)

`iv_percentile`, `iv_rank`, `volatility_regime`, `volatility_score`, `iv_change_rate`, `iv_spike`, `regime_transition`

### Momentum Features (9 columns)

`breakout_score`, `momentum_score`, `roc_1`, `roc_3`, `roc_5`, `roc_10`, `acceleration`, `momentum_strength`, `momentum_direction`

### ML Outputs (6 columns)

`ml_prediction`, `ml_probability`, `ai_score`, `prob_BUY_CE`, `prob_BUY_PE`, `prob_HOLD`

### Scores (5 columns)

`greeks_score`, `final_score`, `signal_strength`, `expected_move_score`, `pred_confidence`

### Signals (5 columns)

`signal`, `entry_buy`, `entry_sell`, `entry_hold`, `pred_label`

### Trade Planning (9 columns)

`entry_confidence`, `stop_loss`, `target_price`, `risk_amount`, `entry_price`, `exit_sl_hit`, `exit_target_hit`, `trailing_sl`, `exit_signal`

### Derived Features (9 columns)

`moneyness`, `ce_pe_ratio`, `atm_dist_pct`, `atm_dist_abs`, `ce_pe_diff`, `spot_chg_1_pct`, `ltp_chg_1_pct`, `spot_roll_std_5`, `ltp_roll_std_5`

### Forward Returns (3 columns)

`fwd_ret_1`, `fwd_ret_3`, `fwd_ret_5`

### Metadata (1 columns)

`ts`
