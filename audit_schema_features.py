import pandas as pd
import os

# Files to check
files = [
    'storage/live/forward/phase221_forward_returns.csv',
    'storage/live/angel_virtual_orders.csv',
    'storage/live/enriched/angel_virtual_orders_with_pnl.csv'
]

# Expected columns
expected_cols = [
    'underlying', 'index_exch', 'opt_exch', 'spot', 'expiry', 'strike', 'side',
    'symbol', 'token', 'ltp', 'ts', 'timestamp', 'date',
    'pred_label', 'pred_confidence', 'prob_BUY_CE', 'prob_BUY_PE', 'prob_HOLD',
    'signal', 'signal_strength', 'fwd_ret_1', 'fwd_ret_2', 'fwd_ret_5', 'fwd_ret_10', 'fwd_ret_15',
    'entry_price', 'exit_price', 'pnl_1', 'pnl_2', 'pnl_5', 'pnl_10', 'pnl_15'
]

# Model features
model_features = [
    'prob_BUY_PE', 'prob_BUY_CE', 'prob_HOLD',
    'ce_pe_ratio', 'moneyness', 'atm_dist_abs',
    'pred_label', 'pred_confidence',
    'volatility_regime', 'ai_score', 'final_score'
]

results = {}

for file_path in files:
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            shape = df.shape
            cols = list(df.columns)
            dtypes = df.dtypes.to_dict()

            # Check missing expected cols
            missing_cols = [col for col in expected_cols if col not in cols]

            # Check NaN rates for merge keys
            merge_keys = ['underlying', 'expiry', 'strike', 'side', 'ts']
            nan_rates = {}
            for key in merge_keys:
                if key in df.columns:
                    nan_rate = df[key].isna().mean()
                    nan_rates[key] = nan_rate

            # For phase221, check model features
            feature_stats = {}
            if 'phase221' in file_path:
                for feat in model_features:
                    if feat in df.columns:
                        non_null = df[feat].notna().mean()
                        min_val = df[feat].min()
                        max_val = df[feat].max()
                        mean_val = df[feat].mean()
                        feature_stats[feat] = {
                            'non_null_pct': non_null,
                            'min': min_val,
                            'max': max_val,
                            'mean': mean_val
                        }

            results[file_path] = {
                'shape': shape,
                'columns': cols,
                'dtypes': dtypes,
                'missing_expected_cols': missing_cols,
                'merge_key_nan_rates': nan_rates,
                'feature_stats': feature_stats
            }
        except Exception as e:
            results[file_path] = {'error': str(e)}
    else:
        results[file_path] = {'error': 'File not found'}

# Print results
import json
print(json.dumps(results, indent=2, default=str))
