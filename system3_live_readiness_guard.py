import pandas as pd
import json
import os
from datetime import datetime

# Load data
csv_path = 'storage/live/forward/phase221_forward_returns.csv'
if not os.path.exists(csv_path):
    state = {
        "timestamp": datetime.now().isoformat(),
        "ready_for_live": False,
        "reasons": ["missing_forward_returns_data"]
    }
    os.makedirs('storage/live/meta', exist_ok=True)
    with open('storage/live/meta/live_readiness_state.json', 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)
    print("LIVE READINESS: BLOCKED – reasons: missing_forward_returns_data")
    exit(0)

df = pd.read_csv(csv_path, encoding='utf-8', low_memory=False)
if df.empty:
    state = {
        "timestamp": datetime.now().isoformat(),
        "ready_for_live": False,
        "reasons": ["empty_forward_returns_data"]
    }
    os.makedirs('storage/live/meta', exist_ok=True)
    with open('storage/live/meta/live_readiness_state.json', 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)
    print("LIVE READINESS: BLOCKED – reasons: empty_forward_returns_data")
    exit(0)

main_horizon = 'fwd_ret_1'
n_rows = len(df)
fwd_ret_1_count = df[main_horizon].notna().sum()

# Strategy A – Follow signal as-is
df_a = df.copy()
df_a['exposure'] = 0
df_a.loc[df_a['signal'] == 'BUY', 'exposure'] = 1
df_a.loc[df_a['signal'] == 'SELL', 'exposure'] = -1
df_a['pnl'] = df_a['exposure'] * df_a[main_horizon]

trades_A = (df_a['exposure'] != 0).sum()
total_pnl_A = df_a['pnl'].sum()
avg_pnl_A = (df_a.loc[df_a['exposure'] != 0, 'pnl'].mean() if trades_A > 0 else 0)
win_rate_A = (df_a.loc[df_a['exposure'] != 0, 'pnl'] > 0).mean() * 100 if trades_A > 0 else 0

# Max drawdown for A
cum_pnl_A = df_a['pnl'].cumsum()
running_max_A = cum_pnl_A.expanding().max()
drawdown_A = cum_pnl_A - running_max_A
max_dd_A = drawdown_A.min()

# Strategy B – Only SELL
df_b = df.copy()
df_b['exposure'] = 0
df_b.loc[df_b['signal'] == 'SELL', 'exposure'] = -1
df_b['pnl'] = df_b['exposure'] * df_b[main_horizon]

trades_B = (df_b['exposure'] != 0).sum()
total_pnl_B = df_b['pnl'].sum()
avg_pnl_B = (df_b.loc[df_b['exposure'] != 0, 'pnl'].mean() if trades_B > 0 else 0)
win_rate_B = (df_b.loc[df_b['exposure'] != 0, 'pnl'] > 0).mean() * 100 if trades_B > 0 else 0

# Overall stats
mean_ret = df[main_horizon].mean()
median_ret = df[main_horizon].median()
std_ret = df[main_horizon].std()
sharpe = mean_ret / std_ret if std_ret > 0 else 0

# Thresholds
min_trades = 200
min_total_pnl = 0.0
min_win_rate = 0.55
min_sharpe = 0.3
max_drawdown_limit = -0.1

# Check conditions for Strategy A
ready_for_live = True
reasons = []

if trades_A < min_trades:
    ready_for_live = False
    reasons.append("too_few_trades")

if total_pnl_A < min_total_pnl:
    ready_for_live = False
    reasons.append("negative_total_pnl")

if win_rate_A < min_win_rate:
    ready_for_live = False
    reasons.append("low_win_rate")

if sharpe < min_sharpe:
    ready_for_live = False
    reasons.append("low_sharpe")

if max_dd_A < max_drawdown_limit:
    ready_for_live = False
    reasons.append("excessive_drawdown")

# JSON output
state = {
    "timestamp": datetime.now().isoformat(),
    "n_rows": int(n_rows),
    "strategy_A": {
        "trades": int(trades_A),
        "total_pnl": float(total_pnl_A),
        "avg_pnl_per_trade": float(avg_pnl_A),
        "win_rate": float(win_rate_A),
        "max_drawdown": float(max_dd_A),
    },
    "overall": {
        "mean_fwd_ret_1": float(mean_ret),
        "median_fwd_ret_1": float(median_ret),
        "std_fwd_ret_1": float(std_ret),
        "sharpe_like": float(sharpe),
    },
    "thresholds": {
        "min_trades": min_trades,
        "min_total_pnl": min_total_pnl,
        "min_win_rate": min_win_rate,
        "min_sharpe": min_sharpe,
        "max_drawdown_limit": max_drawdown_limit,
    },
    "ready_for_live": ready_for_live,
    "reasons": reasons
}

os.makedirs('storage/live/meta', exist_ok=True)
with open('storage/live/meta/live_readiness_state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2)

# Console summary
print(f"Strategy A: trades={trades_A}, total_pnl={total_pnl_A:.6f}, win_rate={win_rate_A:.2f}%, sharpe={sharpe:.4f}, max_drawdown={max_dd_A:.6f}")
print(f"Thresholds: min_trades={min_trades}, min_total_pnl={min_total_pnl}, min_win_rate={min_win_rate}, min_sharpe={min_sharpe}, max_drawdown_limit={max_drawdown_limit}")

if ready_for_live:
    print("LIVE READINESS: PASSED – all thresholds met.")
else:
    print(f"LIVE READINESS: BLOCKED – reasons: {', '.join(reasons)}")
