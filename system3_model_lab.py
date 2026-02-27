import pandas as pd
import os

# Parameters
per_trade_cost_abs = 0.0
per_trade_cost_pct = 0.0

# Load data
csv_path = 'storage/live/forward/phase221_forward_returns.csv'
if not os.path.exists(csv_path):
    print("Error: CSV file not found.")
    exit(1)

df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False)
if df.empty:
    print("Error: Empty CSV file.")
    exit(1)

# Check required columns
required_cols = ['signal', 'prob_BUY_PE', 'ce_pe_ratio', 'moneyness', 'fwd_ret_1', 'timestamp']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    print(f"Error: Missing required columns: {missing_cols}")
    exit(1)

main_horizon = 'fwd_ret_1'

# Train/validation split
df = df.sort_values('timestamp').reset_index(drop=True)
split_idx = int(len(df) * 0.7)
train_df = df.iloc[:split_idx]
valid_df = df.iloc[split_idx:]

def calculate_metrics(df_strategy, cost_abs, cost_pct):
    pnl = df_strategy['pnl']
    exposure = df_strategy['exposure']
    trades = (exposure != 0).sum()
    if trades == 0:
        return 0, 0, 0, 0, 0, 0, 0, 0, 0

    # Gross metrics
    total_pnl = pnl.sum()
    avg_pnl = pnl[exposure != 0].mean()
    win_rate = (pnl[exposure != 0] > 0).mean() * 100
    mean_pnl = pnl.mean()
    std_pnl = pnl.std()
    sharpe = mean_pnl / std_pnl if std_pnl > 0 else 0
    cum_pnl = pnl.cumsum()
    running_max = cum_pnl.expanding().max()
    drawdown = cum_pnl - running_max
    max_dd = drawdown.min()

    # Net metrics
    fwd_ret = df_strategy[main_horizon]
    cost_component = cost_abs + cost_pct * fwd_ret.abs()
    net_pnl = pnl - cost_component * exposure.abs()
    total_pnl_net = net_pnl.sum()
    avg_pnl_net = net_pnl[exposure != 0].mean()
    mean_pnl_net = net_pnl.mean()
    std_pnl_net = net_pnl.std()
    net_sharpe = mean_pnl_net / std_pnl_net if std_pnl_net > 0 else 0

    return trades, total_pnl, avg_pnl, win_rate, sharpe, max_dd, total_pnl_net, avg_pnl_net, net_sharpe


def run_strategy(df_subset, buy_cond, sell_cond):
    df_strat = df_subset.copy()
    df_strat['exposure'] = 0
    if buy_cond is not False:
        df_strat.loc[buy_cond, 'exposure'] = 1
    if sell_cond is not False:
        df_strat.loc[sell_cond, 'exposure'] = -1
    df_strat['pnl'] = df_strat['exposure'] * df_strat[main_horizon]
    return calculate_metrics(df_strat, per_trade_cost_abs, per_trade_cost_pct)

# Fixed strategies
results = []

# Strategy A – Follow signal as-is
metrics_a = run_strategy(df, df['signal'] == 'BUY', df['signal'] == 'SELL')
results.append({
    'Strategy': 'A (Follow Signal)', 'param_desc': 'N/A',
    'train_trades': run_strategy(train_df, train_df['signal'] == 'BUY', train_df['signal'] == 'SELL')[0],
    'train_total_pnl_net': run_strategy(train_df, train_df['signal'] == 'BUY', train_df['signal'] == 'SELL')[6],
    'train_sharpe_net': run_strategy(train_df, train_df['signal'] == 'BUY', train_df['signal'] == 'SELL')[8],
    'valid_trades': run_strategy(valid_df, valid_df['signal'] == 'BUY', valid_df['signal'] == 'SELL')[0],
    'valid_total_pnl_net': run_strategy(valid_df, valid_df['signal'] == 'BUY', valid_df['signal'] == 'SELL')[6],
    'valid_sharpe_net': run_strategy(valid_df, valid_df['signal'] == 'BUY', valid_df['signal'] == 'SELL')[8]
})

# Strategy B – Only SELL
metrics_b = run_strategy(df, False, df['signal'] == 'SELL')
results.append({
    'Strategy': 'B (Only SELL)', 'param_desc': 'N/A',
    'train_trades': run_strategy(train_df, False, train_df['signal'] == 'SELL')[0],
    'train_total_pnl_net': run_strategy(train_df, False, train_df['signal'] == 'SELL')[6],
    'train_sharpe_net': run_strategy(train_df, False, train_df['signal'] == 'SELL')[8],
    'valid_trades': run_strategy(valid_df, False, valid_df['signal'] == 'SELL')[0],
    'valid_total_pnl_net': run_strategy(valid_df, False, valid_df['signal'] == 'SELL')[6],
    'valid_sharpe_net': run_strategy(valid_df, False, valid_df['signal'] == 'SELL')[8]
})

# Variant 3: BUY if moneyness > 0.05, SELL if moneyness < -0.05
metrics_v3 = run_strategy(df, df['moneyness'] > 0.05, df['moneyness'] < -0.05)
results.append({
    'Strategy': 'V3 (moneyness >0.05 BUY, <-0.05 SELL)', 'param_desc': 'N/A',
    'train_trades': run_strategy(train_df, train_df['moneyness'] > 0.05, train_df['moneyness'] < -0.05)[0],
    'train_total_pnl_net': run_strategy(train_df, train_df['moneyness'] > 0.05, train_df['moneyness'] < -0.05)[6],
    'train_sharpe_net': run_strategy(train_df, train_df['moneyness'] > 0.05, train_df['moneyness'] < -0.05)[8],
    'valid_trades': run_strategy(valid_df, valid_df['moneyness'] > 0.05, valid_df['moneyness'] < -0.05)[0],
    'valid_total_pnl_net': run_strategy(valid_df, valid_df['moneyness'] > 0.05, valid_df['moneyness'] < -0.05)[6],
    'valid_sharpe_net': run_strategy(valid_df, valid_df['moneyness'] > 0.05, valid_df['moneyness'] < -0.05)[8]
})

# Variant 5: BUY if moneyness > 0.02 and prob_BUY_PE > 0.5, SELL if moneyness < -0.02 and prob_BUY_PE < 0.5
metrics_v5 = run_strategy(df, (df['moneyness'] > 0.02) & (df['prob_BUY_PE'] > 0.5), (df['moneyness'] < -0.02) & (df['prob_BUY_PE'] < 0.5))
results.append({
    'Strategy': 'V5 (moneyness>0.02 & prob>0.5 BUY, <-0.02 & <0.5 SELL)', 'param_desc': 'N/A',
    'train_trades': run_strategy(train_df, (train_df['moneyness'] > 0.02) & (train_df['prob_BUY_PE'] > 0.5), (train_df['moneyness'] < -0.02) & (train_df['prob_BUY_PE'] < 0.5))[0],
    'train_total_pnl_net': run_strategy(train_df, (train_df['moneyness'] > 0.02) & (train_df['prob_BUY_PE'] > 0.5), (train_df['moneyness'] < -0.02) & (train_df['prob_BUY_PE'] < 0.5))[6],
    'train_sharpe_net': run_strategy(train_df, (train_df['moneyness'] > 0.02) & (train_df['prob_BUY_PE'] > 0.5), (train_df['moneyness'] < -0.02) & (train_df['prob_BUY_PE'] < 0.5))[8],
    'valid_trades': run_strategy(valid_df, (valid_df['moneyness'] > 0.02) & (valid_df['prob_BUY_PE'] > 0.5), (valid_df['moneyness'] < -0.02) & (valid_df['prob_BUY_PE'] < 0.5))[0],
    'valid_total_pnl_net': run_strategy(valid_df, (valid_df['moneyness'] > 0.02) & (valid_df['prob_BUY_PE'] > 0.5), (valid_df['moneyness'] < -0.02) & (valid_df['prob_BUY_PE'] < 0.5))[6],
    'valid_sharpe_net': run_strategy(valid_df, (valid_df['moneyness'] > 0.02) & (valid_df['prob_BUY_PE'] > 0.5), (valid_df['moneyness'] < -0.02) & (valid_df['prob_BUY_PE'] < 0.5))[8]
})

# Parameter sweeps
# V1: prob_BUY_PE
for buy_thr in [0.6, 0.7, 0.8]:
    for sell_thr in [0.2, 0.3, 0.4]:
        param_desc = f'prob_BUY_PE >{buy_thr} BUY, <{sell_thr} SELL'
        buy_cond = df['prob_BUY_PE'] > buy_thr
        sell_cond = df['prob_BUY_PE'] < sell_thr
        train_metrics = run_strategy(train_df, train_df['prob_BUY_PE'] > buy_thr, train_df['prob_BUY_PE'] < sell_thr)
        valid_metrics = run_strategy(valid_df, valid_df['prob_BUY_PE'] > buy_thr, valid_df['prob_BUY_PE'] < sell_thr)
        results.append({
            'Strategy': 'V1 (prob_BUY_PE sweep)', 'param_desc': param_desc,
            'train_trades': train_metrics[0], 'train_total_pnl_net': train_metrics[6], 'train_sharpe_net': train_metrics[8],
            'valid_trades': valid_metrics[0], 'valid_total_pnl_net': valid_metrics[6], 'valid_sharpe_net': valid_metrics[8]
        })

# V2: ce_pe_ratio
for buy_ce_thr in [1.0, 1.1, 1.2]:
    for sell_ce_thr in [0.8, 0.9, 1.0]:
        param_desc = f'ce_pe_ratio >{buy_ce_thr} BUY, <{sell_ce_thr} SELL'
        buy_cond = df['ce_pe_ratio'] > buy_ce_thr
        sell_cond = df['ce_pe_ratio'] < sell_ce_thr
        train_metrics = run_strategy(train_df, train_df['ce_pe_ratio'] > buy_ce_thr, train_df['ce_pe_ratio'] < sell_ce_thr)
        valid_metrics = run_strategy(valid_df, valid_df['ce_pe_ratio'] > buy_ce_thr, valid_df['ce_pe_ratio'] < sell_ce_thr)
        results.append({
            'Strategy': 'V2 (ce_pe_ratio sweep)', 'param_desc': param_desc,
            'train_trades': train_metrics[0], 'train_total_pnl_net': train_metrics[6], 'train_sharpe_net': train_metrics[8],
            'valid_trades': valid_metrics[0], 'valid_total_pnl_net': valid_metrics[6], 'valid_sharpe_net': valid_metrics[8]
        })

# V4: prob_BUY_PE and ce_pe_ratio
for prob_buy_thr in [0.6, 0.7, 0.8]:
    for prob_sell_thr in [0.3, 0.4, 0.5]:
        for ce_buy_thr in [1.0, 1.1]:
            for ce_sell_thr in [0.9, 1.0]:
                param_desc = f'prob>{prob_buy_thr} & ce>{ce_buy_thr} BUY, prob<{prob_sell_thr} & ce<{ce_sell_thr} SELL'
                buy_cond = (df['prob_BUY_PE'] > prob_buy_thr) & (df['ce_pe_ratio'] > ce_buy_thr)
                sell_cond = (df['prob_BUY_PE'] < prob_sell_thr) & (df['ce_pe_ratio'] < ce_sell_thr)
                train_metrics = run_strategy(train_df, (train_df['prob_BUY_PE'] > prob_buy_thr) & (train_df['ce_pe_ratio'] > ce_buy_thr), (train_df['prob_BUY_PE'] < prob_sell_thr) & (train_df['ce_pe_ratio'] < ce_sell_thr))
                valid_metrics = run_strategy(valid_df, (valid_df['prob_BUY_PE'] > prob_buy_thr) & (valid_df['ce_pe_ratio'] > ce_buy_thr), (valid_df['prob_BUY_PE'] < prob_sell_thr) & (valid_df['ce_pe_ratio'] < ce_sell_thr))
                results.append({
                    'Strategy': 'V4 (prob & ce sweep)', 'param_desc': param_desc,
                    'train_trades': train_metrics[0], 'train_total_pnl_net': train_metrics[6], 'train_sharpe_net': train_metrics[8],
                    'valid_trades': valid_metrics[0], 'valid_total_pnl_net': valid_metrics[6], 'valid_sharpe_net': valid_metrics[8]
                })

# Save full results to CSV
df_results = pd.DataFrame(results)
df_results.to_csv('storage/live/meta/model_lab_results.csv', index=False)

# Filter and sort top strategies
top_strategies = df_results[
    (df_results['valid_trades'] >= 50)
].sort_values(by=['valid_total_pnl_net', 'valid_sharpe_net'], ascending=False).head(15)

print("Top 15 Strategies (sorted by valid_total_pnl_net, then valid_sharpe_net):")
print(top_strategies[['Strategy', 'param_desc', 'valid_trades', 'valid_total_pnl_net', 'valid_sharpe_net']].to_string(index=False))
