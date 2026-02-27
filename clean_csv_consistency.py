

import pandas as pd


def clean_csv_consistency(file_path, output_path):
    print(f"Loading CSV file: {file_path}")
    df = pd.read_csv(file_path)
    print(f"Original dataset shape: {df.shape}")

    # Remove duplicates
    df = df.drop_duplicates()
    print(f"After removing duplicates: {df.shape}")

    # Handle missing values
    # Critical columns: drop rows with missing spot, ltp,
    # entry_price, stop_loss, target_price
    critical_price_cols = ['spot', 'ltp', 'entry_price',
                           'stop_loss', 'target_price']
    for col in critical_price_cols:
        if col in df.columns:
            df = df.dropna(subset=[col])
    print(f"After dropping rows with missing critical prices: {df.shape}")

    # For probabilities, clip to [0,1] and fill missing with 0.5
    prob_cols = ['prob_BUY_CE', 'prob_BUY_PE', 'prob_HOLD',
                 'ml_probability', 'pred_proba']
    for col in prob_cols:
        if col in df.columns:
            df[col] = (pd.to_numeric(df[col], errors='coerce')
                       .clip(0, 1).fillna(0.5))

    # For Greeks, cap to reasonable ranges and fill missing with 0
    greek_cols = ['delta', 'gamma', 'theta', 'vega', 'rho']
    for col in greek_cols:
        if col in df.columns:
            df[col] = (pd.to_numeric(df[col], errors='coerce')
                       .clip(-10, 10).fillna(0))

    # For IV, fill missing with median
    iv_cols = ['iv_estimate', 'iv']
    for col in iv_cols:
        if col in df.columns:
            numeric_series = pd.to_numeric(df[col], errors='coerce')
            df[col] = numeric_series.fillna(numeric_series.median())

    # For forward returns, fill missing with 0 (assuming no return if missing)
    fwd_cols = ['fwd_ret_1', 'fwd_ret_2', 'fwd_ret_3',
                'fwd_ret_5', 'fwd_ret_10', 'fwd_ret_15']
    for col in fwd_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # For other numeric columns, fill with median or 0
    numeric_cols = ['rsi', 'macd', 'macd_signal', 'macd_histogram',
                    'sma_5', 'sma_10', 'sma_20', 'trend_score',
                    'multi_tf_trend_score', 'trend_strength',
                    'momentum_score', 'breakout_score', 'roc_1',
                    'roc_3', 'roc_5', 'roc_10', 'acceleration',
                    'momentum_strength', 'volatility_score',
                    'ai_score', 'greeks_score', 'final_score',
                    'signal_strength', 'entry_confidence',
                    'risk_amount', 'trailing_sl', 'time_to_expiry',
                    'ce_pe_ratio', 'atm_dist_pct', 'atm_dist_abs',
                    'ce_pe_diff', 'spot_chg_1_pct', 'ltp_chg_1_pct',
                    'expected_move_score', 'pred_confidence',
                    'spot_roll_std_5', 'ltp_roll_std_5',
                    'u_moneyness_sq', 'u_moneyness_cube',
                    'u_moneyness_sqrt', 'u_momentum_1',
                    'u_momentum_3', 'u_momentum_5', 'u_momentum_10',
                    'u_spot_momentum_1', 'u_spot_momentum_3',
                    'u_spot_momentum_5', 'u_spot_momentum_10',
                    'u_momentum_ratio_1_5', 'u_vol_short',
                    'u_vol_long', 'u_vol_ratio', 'u_spot_vol_short',
                    'u_spot_vol_long', 'u_spot_vol_ratio',
                    'u_regime_high_vol', 'u_regime_low_vol',
                    'u_hour', 'u_minute', 'confidence',
                    'u_moneyness_x_score', 'u_moneyness_x_conf',
                    'u_score_x_conf', 'u_is_win',
                    'u_rolling_win_rate_5', 'u_rolling_win_rate_10',
                    'u_ltp_percentile', 'score', 'rho']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (pd.to_numeric(df[col], errors='coerce')
                       .fillna(df[col].median() if df[col].notna().any() else 0))

    # For categorical columns, fill missing with 'unknown'
    cat_cols = ['underlying', 'strike', 'side', 'symbol', 'ts',
                'moneyness', 'iv_percentile', 'iv_rank',
                'iv_change_rate', 'iv_spike', 'supertrend',
                'supertrend_direction', 'vwap', 'price_vs_vwap',
                'trend_1m', 'trend_3m', 'trend_5m', 'trend_15m',
                'momentum_direction', 'volatility_regime',
                'regime_transition', 'ml_prediction', 'signal',
                'entry_buy', 'entry_sell', 'entry_hold',
                'exit_sl_hit', 'exit_target_hit', 'exit_signal',
                'reconciled_label', 'index_exch', 'opt_exch',
                'expiry', 'token', 'pred_label', 'data_source']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna('unknown')

    # Fix inconsistencies: if BUY_CE prob < 0.5 set to HOLD
    if 'signal' in df.columns and 'prob_BUY_CE' in df.columns:
        mask = (df['signal'] == 'BUY_CE') & (df['prob_BUY_CE'] < 0.5)
        df.loc[mask, 'signal'] = 'HOLD'
    if 'signal' in df.columns and 'prob_BUY_PE' in df.columns:
        mask = ((df['signal'] == 'BUY_PE') &
                (df['prob_BUY_PE'] < 0.5))
        df.loc[mask, 'signal'] = 'HOLD'

    # Ensure timestamps are valid
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])

    print(f"Final dataset shape: {df.shape}")
    df.to_csv(output_path, index=False)
    print(f"Cleaned CSV saved to: {output_path}")

    return df


if __name__ == "__main__":
    input_file = "storage/live/angel_index_ai_signals_with_forward.csv"
    output_file = ("storage/live/angel_index_ai_signals_with_forward_"
                   "cleaned.csv")
    clean_csv_consistency(input_file, output_file)
