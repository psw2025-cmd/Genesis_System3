#!/usr/bin/env python3
"""
System3 CSV Deep Validation - Data Quality & Quant Analysis
Comprehensive validation of angel_index_ai_signals_with_forward.csv
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CSV_FILE = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals_with_forward.csv"
OUTPUT_REPORT = PROJECT_ROOT / "docs" / "SYSTEM3_CSV_DEEP_VALIDATION_REPORT.md"

print("="*80)
print("SYSTEM3 CSV DEEP VALIDATION - DATA QUALITY & QUANT ANALYSIS")
print("="*80)
print(f"File: {CSV_FILE}")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

# ============================================================================
# 1) LOAD & BASIC OVERVIEW
# ============================================================================

print("="*80)
print("1) LOAD & BASIC OVERVIEW")
print("="*80)

try:
    df = pd.read_csv(CSV_FILE, engine="python", on_bad_lines="skip")
    print(f"✅ CSV loaded successfully")
except Exception as e:
    print(f"❌ Failed to load CSV: {e}")
    sys.exit(1)

print(f"\n📊 BASIC STATISTICS")
print(f"  Total Rows: {len(df):,}")
print(f"  Total Columns: {len(df.columns)}")
print(f"  Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

print(f"\n📋 COLUMN LIST ({len(df.columns)} columns)")
for i, col in enumerate(df.columns, 1):
    dtype = str(df[col].dtype)
    non_null = df[col].notna().sum()
    pct = (non_null / len(df) * 100) if len(df) > 0 else 0
    print(f"  {i:3d}. {col:40s} [{dtype:10s}] {non_null:6,} ({pct:5.1f}%)")

print(f"\n🔍 DATA TYPE SUMMARY")
dtype_counts = df.dtypes.value_counts()
for dtype, count in dtype_counts.items():
    print(f"  {dtype}: {count} columns")

# Identify numeric vs object columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
object_cols = df.select_dtypes(include=['object']).columns.tolist()

print(f"\n  Numeric columns: {len(numeric_cols)}")
print(f"  Object columns: {len(object_cols)}")

# Identify columns that should be numeric but are object
should_be_numeric = [
    'spot', 'strike', 'ltp', 'iv', 'iv_estimate', 'delta', 'gamma', 'theta', 'vega',
    'rsi', 'macd', 'macd_signal', 'macd_histogram', 'trend_score', 'multi_tf_trend_score',
    'iv_percentile', 'iv_rank', 'volatility_score', 'breakout_score', 'momentum_score',
    'roc_1', 'roc_3', 'roc_5', 'roc_10', 'acceleration', 'momentum_strength',
    'ml_probability', 'ai_score', 'greeks_score', 'final_score', 'signal_strength',
    'entry_confidence', 'stop_loss', 'target_price', 'risk_amount', 'entry_price',
    'expected_move_score', 'pred_confidence', 'moneyness', 'ce_pe_ratio',
    'atm_dist_pct', 'atm_dist_abs', 'ce_pe_diff', 'spot_chg_1_pct', 'ltp_chg_1_pct',
    'spot_roll_std_5', 'ltp_roll_std_5', 'prob_BUY_CE', 'prob_BUY_PE', 'prob_HOLD',
    'fwd_ret_1', 'fwd_ret_3', 'fwd_ret_5'
]

should_be_numeric_but_object = [col for col in should_be_numeric if col in object_cols]

if should_be_numeric_but_object:
    print(f"\n  ⚠️ Columns that should be numeric but are object ({len(should_be_numeric_but_object)}):")
    for col in should_be_numeric_but_object:
        print(f"    - {col}")
else:
    print(f"\n  ✅ All expected numeric columns are numeric")

# ============================================================================
# 2) HEADER & SCHEMA VALIDATION
# ============================================================================

print("\n" + "="*80)
print("2) HEADER & SCHEMA VALIDATION")
print("="*80)

# Check for duplicate column names
duplicate_cols = df.columns[df.columns.duplicated()].tolist()
if duplicate_cols:
    print(f"  ⚠️ Duplicate column names found: {duplicate_cols}")
else:
    print(f"  ✅ No duplicate column names")

# Check for rows that look like duplicate headers
header_cols = df.columns.tolist()
header_row_values = [str(c) for c in header_cols]

def is_header_row(row):
    """Check if row matches header exactly."""
    row_values = [str(v) for v in row.values]
    return row_values == header_row_values

mask_header_rows = df.apply(is_header_row, axis=1)
duplicate_header_count = mask_header_rows.sum()

if duplicate_header_count > 0:
    print(f"\n  ⚠️ Duplicate header rows found: {duplicate_header_count}")
    header_row_indices = df[mask_header_rows].index.tolist()
    print(f"    Row indices: {header_row_indices[:10]}{'...' if len(header_row_indices) > 10 else ''}")
    
    # Show sample of suspected bad rows
    print(f"\n  Sample duplicate header rows:")
    for idx in header_row_indices[:3]:
        row = df.loc[idx]
        print(f"    Row {idx}: {row.iloc[0]}, {row.iloc[1]}, {row.iloc[2]}, ...")
else:
    print(f"\n  ✅ No duplicate header rows detected")

# Check for literal "signal" in signal column (indicator of header row)
if "signal" in df.columns:
    signal_is_header = df["signal"] == "signal"
    signal_header_count = signal_is_header.sum()
    if signal_header_count > 0:
        print(f"\n  ⚠️ Rows with signal='signal' (likely header rows): {signal_header_count}")
        signal_header_indices = df[signal_is_header].index.tolist()
        print(f"    Row indices: {signal_header_indices[:10]}{'...' if len(signal_header_indices) > 10 else ''}")

# Schema categorization
print(f"\n📋 SCHEMA CATEGORIZATION")
schema_categories = {
    "Identifiers": ["underlying", "index_exch", "opt_exch", "symbol", "token", "expiry", "strike", "side"],
    "Market Data": ["spot", "ltp", "time_to_expiry", "iv", "iv_estimate"],
    "Greeks": ["delta", "gamma", "theta", "vega"],
    "Technical Indicators": ["rsi", "macd", "macd_signal", "macd_histogram", "trend_score", "multi_tf_trend_score",
                            "vwap", "price_vs_vwap", "supertrend", "supertrend_direction", "sma_5", "sma_10", "sma_20"],
    "Volatility Metrics": ["iv_percentile", "iv_rank", "volatility_regime", "volatility_score", "iv_change_rate", "iv_spike"],
    "Momentum Features": ["breakout_score", "momentum_score", "roc_1", "roc_3", "roc_5", "roc_10", 
                          "acceleration", "momentum_strength", "momentum_direction"],
    "ML Outputs": ["ml_prediction", "ml_probability", "ai_score", "prob_BUY_CE", "prob_BUY_PE", "prob_HOLD"],
    "Scores": ["greeks_score", "final_score", "signal_strength", "expected_move_score", "pred_confidence"],
    "Signals": ["signal", "pred_label", "entry_buy", "entry_sell", "entry_hold"],
    "Trade Planning": ["entry_confidence", "stop_loss", "target_price", "risk_amount", "entry_price",
                       "exit_sl_hit", "exit_target_hit", "trailing_sl", "exit_signal"],
    "Derived Features": ["moneyness", "ce_pe_ratio", "atm_dist_pct", "atm_dist_abs", "ce_pe_diff",
                         "spot_chg_1_pct", "ltp_chg_1_pct", "spot_roll_std_5", "ltp_roll_std_5"],
    "Forward Returns": ["fwd_ret_1", "fwd_ret_3", "fwd_ret_5"],
    "Metadata": ["ts", "regime_transition", "trend_strength", "trend_1m", "trend_3m", "trend_5m", "trend_15m"]
}

for category, cols in schema_categories.items():
    found_cols = [c for c in cols if c in df.columns]
    if found_cols:
        print(f"  {category:25s}: {len(found_cols)} columns")
        if len(found_cols) <= 5:
            print(f"    {', '.join(found_cols)}")
        else:
            print(f"    {', '.join(found_cols[:5])} ... ({len(found_cols)-5} more)")

# ============================================================================
# 3) TYPE CONVERSION & CLEANING
# ============================================================================

print("\n" + "="*80)
print("3) TYPE CONVERSION & CLEANING")
print("="*80)

df_clean = df.copy()
conversion_report = []

# Convert all numeric columns
for col in should_be_numeric:
    if col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            before_nulls = df_clean[col].isna().sum()
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            after_nulls = df_clean[col].isna().sum()
            new_nulls = after_nulls - before_nulls
            conversion_report.append({
                "column": col,
                "before_type": "object",
                "after_type": str(df_clean[col].dtype),
                "new_nulls": new_nulls,
                "null_pct": (new_nulls / len(df_clean) * 100) if len(df_clean) > 0 else 0
            })

if conversion_report:
    print(f"\n  TYPE CONVERSION REPORT ({len(conversion_report)} columns converted)")
    print(f"  {'Column':<30s} {'Before':<10s} {'After':<10s} {'New Nulls':<12s} {'Null %':<10s}")
    print(f"  {'-'*30} {'-'*10} {'-'*10} {'-'*12} {'-'*10}")
    for report in conversion_report:
        print(f"  {report['column']:<30s} {report['before_type']:<10s} {report['after_type']:<10s} "
              f"{report['new_nulls']:>10,} {report['null_pct']:>8.2f}%")
else:
    print(f"\n  ✅ No type conversions needed")

# Drop duplicate header rows
rows_before_drop = len(df_clean)
if duplicate_header_count > 0:
    df_clean = df_clean[~mask_header_rows].copy()
    rows_dropped = rows_before_drop - len(df_clean)
    print(f"\n  ✅ Dropped {rows_dropped} duplicate header rows")
    print(f"     Rows remaining: {len(df_clean):,}")

if signal_header_count > 0:
    df_clean = df_clean[~signal_is_header].copy()
    rows_dropped = rows_before_drop - len(df_clean)
    print(f"  ✅ Dropped {signal_header_count} rows with signal='signal'")
    print(f"     Rows remaining: {len(df_clean):,}")

# ============================================================================
# 4) INTERNAL CONSISTENCY CHECKS
# ============================================================================

print("\n" + "="*80)
print("4) INTERNAL CONSISTENCY CHECKS")
print("="*80)

issues_found = []

# Greeks validation
print(f"\n🔍 GREEKS VALIDATION")

if "delta" in df_clean.columns:
    delta = pd.to_numeric(df_clean["delta"], errors="coerce")
    delta_out_of_range = ((delta < -1) | (delta > 1)).sum()
    if delta_out_of_range > 0:
        print(f"  ⚠️ Delta out of range [-1, 1]: {delta_out_of_range} rows")
        issues_found.append(f"Delta out of range: {delta_out_of_range} rows")
        # Show examples
        bad_delta = df_clean[((delta < -1) | (delta > 1))].head(3)
        print(f"    Examples:")
        for idx, row in bad_delta.iterrows():
            print(f"      Row {idx}: delta={row['delta']}")
    else:
        print(f"  ✅ Delta values in valid range [-1, 1]")

if "vega" in df_clean.columns:
    vega = pd.to_numeric(df_clean["vega"], errors="coerce")
    negative_vega = (vega < 0).sum()
    if negative_vega > 0:
        print(f"  ⚠️ Negative vega values: {negative_vega} rows")
        issues_found.append(f"Negative vega: {negative_vega} rows")
        bad_vega = df_clean[vega < 0].head(3)
        print(f"    Examples:")
        for idx, row in bad_vega.iterrows():
            print(f"      Row {idx}: vega={row['vega']}")
    else:
        print(f"  ✅ All vega values >= 0")

if "theta" in df_clean.columns:
    theta = pd.to_numeric(df_clean["theta"], errors="coerce")
    positive_theta = (theta > 0).sum()
    large_positive_theta = (theta > 10).sum()
    if large_positive_theta > 0:
        print(f"  ⚠️ Large positive theta (>10): {large_positive_theta} rows")
        issues_found.append(f"Large positive theta: {large_positive_theta} rows")
        bad_theta = df_clean[theta > 10].head(3)
        print(f"    Examples:")
        for idx, row in bad_theta.iterrows():
            print(f"      Row {idx}: theta={row['theta']}")
    elif positive_theta > 0:
        print(f"  ⚠️ Positive theta values: {positive_theta} rows (unusual but may be valid)")
    else:
        print(f"  ✅ All theta values <= 0 (expected)")

# IV validation
print(f"\n🔍 IMPLIED VOLATILITY VALIDATION")

iv_cols = ["iv", "iv_estimate"]
for iv_col in iv_cols:
    if iv_col in df_clean.columns:
        iv = pd.to_numeric(df_clean[iv_col], errors="coerce")
        iv_out_of_range = ((iv < 0) | (iv > 3)).sum()
        iv_nan = iv.isna().sum()
        if iv_out_of_range > 0:
            print(f"  ⚠️ {iv_col} out of range [0, 3]: {iv_out_of_range} rows")
            issues_found.append(f"{iv_col} out of range: {iv_out_of_range} rows")
            bad_iv = df_clean[((iv < 0) | (iv > 3))].head(3)
            print(f"    Examples:")
            for idx, row in bad_iv.iterrows():
                print(f"      Row {idx}: {iv_col}={row[iv_col]}")
        else:
            print(f"  ✅ {iv_col} values in valid range [0, 3] (or NaN: {iv_nan})")

# Probabilities validation
print(f"\n🔍 PROBABILITIES VALIDATION")

prob_cols = ["prob_BUY_CE", "prob_BUY_PE", "prob_HOLD"]
prob_data = {}
for prob_col in prob_cols:
    if prob_col in df_clean.columns:
        prob = pd.to_numeric(df_clean[prob_col], errors="coerce")
        prob_data[prob_col] = prob
        
        # Check range [0, 1]
        out_of_range = ((prob < 0) | (prob > 1)).sum()
        if out_of_range > 0:
            print(f"  ⚠️ {prob_col} out of range [0, 1]: {out_of_range} rows")
            issues_found.append(f"{prob_col} out of range: {out_of_range} rows")
        else:
            print(f"  ✅ {prob_col} values in valid range [0, 1]")

# Check probability sum
if len(prob_data) == 3:
    prob_sum = prob_data["prob_BUY_CE"] + prob_data["prob_BUY_PE"] + prob_data["prob_HOLD"]
    prob_sum_valid = prob_sum.notna()
    
    if prob_sum_valid.sum() > 0:
        prob_sum_stats = prob_sum[prob_sum_valid].describe()
        print(f"\n  Probability sum statistics:")
        print(f"    Mean: {prob_sum_stats['mean']:.4f}")
        print(f"    Std: {prob_sum_stats['std']:.4f}")
        print(f"    Min: {prob_sum_stats['min']:.4f}")
        print(f"    Max: {prob_sum_stats['max']:.4f}")
        
        prob_sum_bad = (prob_sum_valid & (np.abs(prob_sum - 1) > 0.05)).sum()
        if prob_sum_bad > 0:
            print(f"  ⚠️ Rows where |prob_sum - 1| > 0.05: {prob_sum_bad}")
            issues_found.append(f"Probability sum != 1: {prob_sum_bad} rows")
            bad_prob_sum = df_clean[prob_sum_valid & (np.abs(prob_sum - 1) > 0.05)].head(3)
            print(f"    Examples:")
            for idx, row in bad_prob_sum.iterrows():
                print(f"      Row {idx}: sum={prob_sum.loc[idx]:.4f}, "
                      f"CE={row['prob_BUY_CE']:.4f}, PE={row['prob_BUY_PE']:.4f}, HOLD={row['prob_HOLD']:.4f}")
        else:
            print(f"  ✅ All probability sums close to 1.0")

# Moneyness & ATM distance validation
print(f"\n🔍 MONEYNESS & ATM DISTANCE VALIDATION")

if all(col in df_clean.columns for col in ["moneyness", "spot", "strike", "side"]):
    moneyness = pd.to_numeric(df_clean["moneyness"], errors="coerce")
    spot = pd.to_numeric(df_clean["spot"], errors="coerce")
    strike = pd.to_numeric(df_clean["strike"], errors="coerce")
    side = df_clean["side"]
    
    # Calculate expected moneyness
    expected_moneyness = spot / strike
    
    # Check consistency
    valid_mask = moneyness.notna() & spot.notna() & strike.notna() & (strike > 0)
    if valid_mask.sum() > 0:
        moneyness_diff = np.abs(moneyness[valid_mask] - expected_moneyness[valid_mask])
        large_diff = (moneyness_diff > 0.1).sum()
        
        if large_diff > 0:
            print(f"  ⚠️ Moneyness inconsistent with spot/strike: {large_diff} rows")
            issues_found.append(f"Moneyness inconsistency: {large_diff} rows")
            bad_moneyness = df_clean[valid_mask & (moneyness_diff > 0.1)].head(3)
            print(f"    Examples:")
            for idx, row in bad_moneyness.iterrows():
                print(f"      Row {idx}: moneyness={row['moneyness']:.4f}, "
                      f"expected={expected_moneyness.loc[idx]:.4f}, "
                      f"spot={row['spot']}, strike={row['strike']}, side={row['side']}")
        else:
            print(f"  ✅ Moneyness consistent with spot/strike")

# Forward returns validation
print(f"\n🔍 FORWARD RETURNS VALIDATION")

forward_cols = ["fwd_ret_1", "fwd_ret_3", "fwd_ret_5"]
forward_data = {}

for fwd_col in forward_cols:
    if fwd_col in df_clean.columns:
        fwd_ret = pd.to_numeric(df_clean[fwd_col], errors="coerce")
        forward_data[fwd_col] = fwd_ret
        
        non_null = fwd_ret.notna().sum()
        pct = (non_null / len(df_clean) * 100) if len(df_clean) > 0 else 0
        
        print(f"\n  {fwd_col}:")
        print(f"    Non-null values: {non_null:,} ({pct:.1f}%)")
        
        if non_null > 0:
            stats = fwd_ret.describe()
            print(f"    Mean: {stats['mean']:.6f}")
            print(f"    Std: {stats['std']:.6f}")
            print(f"    Min: {stats['min']:.6f}")
            print(f"    25%: {stats['25%']:.6f}")
            print(f"    50%: {stats['50%']:.6f}")
            print(f"    75%: {stats['75%']:.6f}")
            print(f"    Max: {stats['max']:.6f}")
            
            # Check for extreme outliers
            extreme_outliers = (np.abs(fwd_ret) > 5).sum()
            if extreme_outliers > 0:
                print(f"    ⚠️ Extreme outliers (|return| > 5): {extreme_outliers}")
                issues_found.append(f"{fwd_col} extreme outliers: {extreme_outliers} rows")
                bad_fwd = df_clean[np.abs(fwd_ret) > 5].head(3)
                print(f"      Examples:")
                for idx, row in bad_fwd.iterrows():
                    print(f"        Row {idx}: {fwd_col}={row[fwd_col]:.4f}, "
                          f"underlying={row.get('underlying', 'N/A')}, "
                          f"strike={row.get('strike', 'N/A')}")

# ============================================================================
# 5) SIGNAL & LABEL ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("5) SIGNAL & LABEL ANALYSIS")
print("="*80)

# Signal value counts
if "signal" in df_clean.columns:
    signal_counts = df_clean["signal"].value_counts()
    signal_nan = df_clean["signal"].isna().sum()
    
    print(f"\n📡 SIGNAL DISTRIBUTION")
    print(f"  Total rows: {len(df_clean):,}")
    print(f"  NaN signals: {signal_nan:,} ({signal_nan/len(df_clean)*100:.1f}%)")
    print(f"\n  Signal value counts:")
    for signal, count in signal_counts.items():
        pct = (count / len(df_clean) * 100) if len(df_clean) > 0 else 0
        print(f"    {str(signal):20s}: {count:6,} ({pct:5.1f}%)")

# Pred label value counts
if "pred_label" in df_clean.columns:
    pred_counts = df_clean["pred_label"].value_counts()
    pred_nan = df_clean["pred_label"].isna().sum()
    
    print(f"\n📊 PRED_LABEL DISTRIBUTION")
    print(f"  NaN pred_labels: {pred_nan:,} ({pred_nan/len(df_clean)*100:.1f}%)")
    print(f"\n  Pred_label value counts:")
    for label, count in pred_counts.items():
        pct = (count / len(df_clean) * 100) if len(df_clean) > 0 else 0
        print(f"    {str(label):20s}: {count:6,} ({pct:5.1f}%)")

# Signal vs Forward Returns analysis
print(f"\n📈 SIGNAL vs FORWARD RETURNS ANALYSIS")

if "signal" in df_clean.columns and forward_data:
    valid_signals = df_clean["signal"].dropna()
    valid_signals = valid_signals[valid_signals != "signal"]  # Remove header rows
    
    for signal_val in valid_signals.unique():
        signal_mask = (df_clean["signal"] == signal_val)
        
        print(f"\n  Signal: {signal_val}")
        print(f"    Count: {signal_mask.sum():,}")
        
        for fwd_col in forward_cols:
            if fwd_col in forward_data:
                fwd_ret = forward_data[fwd_col]
                signal_fwd = fwd_ret[signal_mask & fwd_ret.notna()]
                
                if len(signal_fwd) > 0:
                    mean_ret = signal_fwd.mean()
                    median_ret = signal_fwd.median()
                    std_ret = signal_fwd.std()
                    print(f"    {fwd_col}:")
                    print(f"      Samples: {len(signal_fwd):,}")
                    print(f"      Mean: {mean_ret:.6f}")
                    print(f"      Median: {median_ret:.6f}")
                    print(f"      Std: {std_ret:.6f}")

# ============================================================================
# 6) OUTPUT SUMMARY
# ============================================================================

print("\n" + "="*80)
print("6) VALIDATION SUMMARY")
print("="*80)

print(f"\n📊 SCHEMA SUMMARY")
print(f"  Total Columns: {len(df_clean.columns)}")
print(f"  Numeric Columns: {len(df_clean.select_dtypes(include=[np.number]).columns)}")
print(f"  Object Columns: {len(df_clean.select_dtypes(include=['object']).columns)}")
print(f"  Rows After Cleaning: {len(df_clean):,}")

print(f"\n🔧 TYPE CONVERSION REPORT")
if conversion_report:
    print(f"  Columns converted: {len(conversion_report)}")
    total_new_nulls = sum(r["new_nulls"] for r in conversion_report)
    print(f"  Total new nulls created: {total_new_nulls:,}")
else:
    print(f"  ✅ No conversions needed")

print(f"\n🚨 DATA QUALITY ISSUES FOUND")
if issues_found:
    print(f"  Total issues: {len(issues_found)}")
    for i, issue in enumerate(issues_found, 1):
        print(f"    {i}. {issue}")
else:
    print(f"  ✅ No major data quality issues detected")

print(f"\n📈 SIGNAL vs FORWARD RETURNS")
if "signal" in df_clean.columns and forward_data:
    for fwd_col in forward_cols:
        if fwd_col in forward_data:
            fwd_ret = forward_data[fwd_col]
            coverage = (fwd_ret.notna().sum() / len(df_clean) * 100) if len(df_clean) > 0 else 0
            print(f"  {fwd_col}: {fwd_ret.notna().sum():,} values ({coverage:.1f}% coverage)")

# ============================================================================
# NEXT STEPS
# ============================================================================

print("\n" + "="*80)
print("NEXT STEPS - Making Dataset Ready for Model Training & Backtesting")
print("="*80)

next_steps = []

if duplicate_header_count > 0:
    next_steps.append(f"✅ Remove {duplicate_header_count} duplicate header rows (already done in cleaned DataFrame)")

if conversion_report:
    next_steps.append(f"✅ Convert {len(conversion_report)} columns to numeric (already done)")

if issues_found:
    next_steps.append("⚠️ Review and fix data quality issues listed above")
    for issue in issues_found:
        if "out of range" in issue.lower():
            next_steps.append(f"  - Fix: {issue}")
        elif "inconsistency" in issue.lower():
            next_steps.append(f"  - Investigate: {issue}")

# Forward returns coverage
if forward_data:
    min_coverage = min((fwd.notna().sum() / len(df_clean) * 100) for fwd in forward_data.values() if len(df_clean) > 0)
    if min_coverage < 50:
        next_steps.append(f"⚠️ Low forward returns coverage ({min_coverage:.1f}%) - consider filtering to rows with forward returns")

# Missing critical columns
critical_cols = ["final_score", "signal", "fwd_ret_1"]
missing_critical = [col for col in critical_cols if col not in df_clean.columns]
if missing_critical:
    next_steps.append(f"❌ Missing critical columns: {', '.join(missing_critical)}")

# Data completeness
if len(df_clean) < 100:
    next_steps.append(f"⚠️ Low row count ({len(df_clean):,}) - may need more data for reliable analysis")

# Recommendations
next_steps.append("\n📋 RECOMMENDATIONS:")
next_steps.append("  1. Filter to rows with complete forward returns for EV analysis")
next_steps.append("  2. Remove rows with extreme outliers in forward returns")
next_steps.append("  3. Ensure probability columns sum to 1.0 (normalize if needed)")
next_steps.append("  4. Validate moneyness calculations match spot/strike ratios")
next_steps.append("  5. Check Greeks are within expected ranges (delta [-1,1], vega >= 0, theta <= 0)")
next_steps.append("  6. For model training: use only rows with forward returns as labels")
next_steps.append("  7. For backtesting: ensure forward returns are from future snapshots (not lookahead bias)")

for step in next_steps:
    print(f"  {step}")

print("\n" + "="*80)
print("VALIDATION COMPLETE")
print("="*80)

# Save detailed report
report_content = f"""# System3 CSV Deep Validation Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**File**: `{CSV_FILE.name}`

## Summary

- **Total Rows**: {len(df):,} (original), {len(df_clean):,} (after cleaning)
- **Total Columns**: {len(df.columns)}
- **Duplicate Headers Removed**: {duplicate_header_count}
- **Type Conversions**: {len(conversion_report)}
- **Data Quality Issues**: {len(issues_found)}

## Detailed Report

See console output for complete analysis.

## Next Steps

{chr(10).join('1. ' + step.replace('✅ ', '').replace('⚠️ ', '').replace('❌ ', '') for step in next_steps if step and not step.startswith('📋'))}
"""

OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_REPORT.write_text(report_content, encoding="utf-8")

print(f"\n✅ Detailed report saved: {OUTPUT_REPORT}")

