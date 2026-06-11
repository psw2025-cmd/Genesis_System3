import pandas as pd
import numpy as np

# STEP 1 – Load and basic sanity checks
print("=== STEP 1: Load and Basic Sanity Checks ===")

df = pd.read_csv('storage/live/forward/phase221_forward_returns.csv',
                 encoding='utf-8', low_memory=False)

print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

fwd_ret_cols = [col for col in df.columns if col.startswith('fwd_ret_')]
print("\nNon-null entries in fwd_ret_* columns:")
for col in fwd_ret_cols:
    non_null = df[col].notna().sum()
    print(f"{col}: {non_null}")

print("\nValue counts for pred_label:")
print(df['pred_label'].value_counts())

print("\nValue counts for signal:")
print(df['signal'].value_counts())

print("\nValue counts for underlying:")
print(df['underlying'].value_counts())

if 'volatility_regime' in df.columns:
    print("\nValue counts for volatility_regime:")
    print(df['volatility_regime'].value_counts())
else:
    print("\nvolatility_regime column not found")

# STEP 2 – Realized PnL per signal type
print("\n=== STEP 2: Realized PnL per Signal Type ===")

main_horizon = 'fwd_ret_1'

print(f"\nUsing {main_horizon} as main horizon")

print("\nPer pred_label:")
pred_stats = []
for label in df['pred_label'].unique():
    subset = df[df['pred_label'] == label]
    count = len(subset)
    avg = subset[main_horizon].mean()
    median = subset[main_horizon].median()
    win_rate = (subset[main_horizon] > 0).mean() * 100
    pred_stats.append([label, count, avg, median, win_rate])
    print(f"{label}: count={count}, avg={avg:.6f}, "
          f"median={median:.6f}, win_rate={win_rate:.2f}%")

print("\nPer signal:")
signal_stats = []
for sig in df['signal'].unique():
    subset = df[df['signal'] == sig]
    count = len(subset)
    avg = subset[main_horizon].mean()
    median = subset[main_horizon].median()
    win_rate = (subset[main_horizon] > 0).mean() * 100
    signal_stats.append([sig, count, avg, median, win_rate])
    print(f"{sig}: count={count}, avg={avg:.6f}, "
          f"median={median:.6f}, win_rate={win_rate:.2f}%")

overall_mean = df[main_horizon].mean()
overall_median = df[main_horizon].median()
overall_std = df[main_horizon].std()
sharpe = overall_mean / overall_std if overall_std > 0 else np.nan

print(f"\nOverall: mean={overall_mean:.6f}, "
      f"median={overall_median:.6f}, std={overall_std:.6f}, "
      f"sharpe={sharpe:.4f}")

# STEP 3 – "Trade as model says" vs "Do nothing"
print("\n=== STEP 3: Trade Strategies ===")

# Strategy A – Follow signal as-is
df_a = df.copy()
df_a['exposure'] = 0
df_a.loc[df_a['signal'] == 'BUY', 'exposure'] = 1
df_a.loc[df_a['signal'] == 'SELL', 'exposure'] = -1
df_a['pnl'] = df_a['exposure'] * df_a[main_horizon]

# Strategy B – Only trade SELL
df_b = df.copy()
df_b['exposure'] = 0
df_b.loc[df_b['signal'] == 'SELL', 'exposure'] = -1
df_b['pnl'] = df_b['exposure'] * df_b[main_horizon]

# Strategy C – Do nothing
df_c = df.copy()
df_c['exposure'] = 0
df_c['pnl'] = 0

strategies = [
    ('A - Follow signal', df_a),
    ('B - Only SELL', df_b),
    ('C - Do nothing', df_c)
]

strategy_results = []

for name, df_strat in strategies:
    trades = (df_strat['exposure'] != 0).sum()
    total_pnl = df_strat['pnl'].sum()
    avg_pnl_per_trade = (df_strat.loc[df_strat['exposure'] != 0, 'pnl']
                         .mean() if trades > 0 else 0)
    win_rate = (df_strat.loc[df_strat['exposure'] != 0, 'pnl'] > 0
                ).mean() * 100 if trades > 0 else 0

    # Max drawdown
    cum_pnl = df_strat['pnl'].cumsum()
    running_max = cum_pnl.expanding().max()
    drawdown = cum_pnl - running_max
    max_drawdown = drawdown.min()

    strategy_results.append([name, trades, total_pnl,
                             avg_pnl_per_trade, win_rate, max_drawdown])

print("\nStrategy Summary:")
print("strategy, trades, total_pnl, avg_pnl_per_trade, "
      "win_rate, max_drawdown")
for row in strategy_results:
    print(f"{row[0]}, {row[1]}, {row[2]:.6f}, {row[3]:.6f}, "
          f"{row[4]:.2f}%, {row[5]:.6f}")

# STEP 4 – Feature–return relationships
print("\n=== STEP 4: Feature-Return Relationships ===")

features_to_check = ['pred_confidence', 'prob_BUY_PE', 'prob_BUY_CE',
                     'ce_pe_ratio', 'moneyness']

# Add other continuous features with high variance
numeric_cols = df.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    if (col not in features_to_check and col != main_horizon and
        df[col].var() > df[col].mean() * 0.1):  # arbitrary threshold
        features_to_check.append(col)

correlations = []
for feat in features_to_check:
    if feat in df.columns and df[feat].notna().sum() > 10:
        corr = df[feat].corr(df[main_horizon])
        correlations.append([feat, corr])

correlations.sort(key=lambda x: abs(x[1]), reverse=True)

print(f"\nCorrelations with {main_horizon}:")
for feat, corr in correlations[:10]:  # top 10
    print(f"{feat}: {corr:.4f}")

# STEP 5 – Underlying / volatility breakdown
print("\n=== STEP 5: Underlying / Volatility Breakdown ===")

print("\nPer Underlying:")
underlying_stats = []
for und in df['underlying'].unique():
    subset = df[df['underlying'] == und]
    count = len(subset)
    avg = subset[main_horizon].mean()
    win_rate = (subset[main_horizon] > 0).mean() * 100
    underlying_stats.append([und, count, avg, win_rate])
    print(f"{und}: count={count}, avg={avg:.6f}, "
          f"win_rate={win_rate:.2f}%")

if 'volatility_regime' in df.columns:
    print("\nPer Volatility Regime:")
    vol_stats = []
    for vol in df['volatility_regime'].dropna().unique():
        subset = df[df['volatility_regime'] == vol]
        count = len(subset)
        avg = subset[main_horizon].mean()
        win_rate = (subset[main_horizon] > 0).mean() * 100
        vol_stats.append([vol, count, avg, win_rate])
        print(f"{vol}: count={count}, avg={avg:.6f}, "
              f"win_rate={win_rate:.2f}%")

# STEP 6 – Final conclusion block
print("\n=== STEP 6: Final Conclusion ===")

strat_a_total = strategy_results[0][2]
strat_b_total = strategy_results[1][2]

print(f"Strategy A overall gain/loss: {strat_a_total:.6f}")
print(f"Strategy B overall gain/loss: {strat_b_total:.6f}")

if underlying_stats:
    best_und = max(underlying_stats, key=lambda x: x[2])
    worst_und = min(underlying_stats, key=lambda x: x[2])
    print(f"Best underlying by average {main_horizon}: "
          f"{best_und[0]} ({best_und[2]:.6f})")
    print(f"Worst underlying by average {main_horizon}: "
          f"{worst_und[0]} ({worst_und[2]:.6f})")

if 'volatility_regime' in df.columns and vol_stats:
    best_vol = max(vol_stats, key=lambda x: x[2])
    worst_vol = min(vol_stats, key=lambda x: x[2])
    print(f"Best volatility regime by average {main_horizon}: "
          f"{best_vol[0]} ({best_vol[2]:.6f})")
    print(f"Worst volatility regime by average {main_horizon}: "
          f"{worst_vol[0]} ({worst_vol[2]:.6f})")
