"""
Analyze Signal Distribution in Clean EV-Ready CSV

This script analyzes the distribution of final_score to determine feasible thresholds.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CSV_EV_READY = PROJECT_ROOT / "storage" / "clean" / "angel_index_ai_signals_with_forward_ev_ready.csv"

print("="*80)
print("SIGNAL DISTRIBUTION ANALYSIS - CLEAN EV-READY CSV")
print("="*80)
print(f"File: {CSV_EV_READY}")
print("="*80)
print()

# Load CSV
df = pd.read_csv(CSV_EV_READY, engine="python", on_bad_lines="skip")

# Convert final_score to numeric
df["final_score"] = pd.to_numeric(df["final_score"], errors="coerce")
df = df.dropna(subset=["final_score"])

print(f"📊 Overall Statistics:")
print(f"  Total Rows: {len(df):,}")
print(f"  Valid final_score: {df['final_score'].notna().sum():,}")
print()

# Overall distribution
print(f"📈 Final Score Distribution (Overall):")
stats = df["final_score"].describe()
print(f"  Mean: {stats['mean']:.6f}")
print(f"  Median: {stats['50%']:.6f}")
print(f"  Std: {stats['std']:.6f}")
print(f"  Min: {stats['min']:.6f}")
print(f"  25%: {stats['25%']:.6f}")
print(f"  75%: {stats['75%']:.6f}")
print(f"  Max: {stats['max']:.6f}")
print()

# Count signals at different thresholds
print(f"🔍 Signal Counts at Different Thresholds:")
thresholds = {
    "BUY >= 0.1": (df["final_score"] >= 0.1).sum(),
    "BUY >= 0.2": (df["final_score"] >= 0.2).sum(),
    "BUY >= 0.3": (df["final_score"] >= 0.3).sum(),
    "BUY >= 0.4": (df["final_score"] >= 0.4).sum(),
    "BUY >= 0.5": (df["final_score"] >= 0.5).sum(),
    "SELL <= -0.1": (df["final_score"] <= -0.1).sum(),
    "SELL <= -0.2": (df["final_score"] <= -0.2).sum(),
    "SELL <= -0.3": (df["final_score"] <= -0.3).sum(),
    "SELL <= -0.4": (df["final_score"] <= -0.4).sum(),
    "SELL <= -0.5": (df["final_score"] <= -0.5).sum(),
}

for threshold, count in thresholds.items():
    pct = (count / len(df) * 100) if len(df) > 0 else 0
    print(f"  {threshold:20s}: {count:4,} ({pct:5.1f}%)")
print()

# Distribution by underlying
if "underlying" in df.columns:
    print(f"📊 Final Score Distribution by Underlying:")
    print()
    
    for underlying in df["underlying"].unique():
        df_underlying = df[df["underlying"] == underlying]
        score = df_underlying["final_score"]
        
        print(f"  {underlying}:")
        print(f"    Count: {len(df_underlying):,}")
        print(f"    Mean: {score.mean():.6f}")
        print(f"    Median: {score.median():.6f}")
        print(f"    Min: {score.min():.6f}")
        print(f"    Max: {score.max():.6f}")
        print(f"    BUY >= 0.1: {(score >= 0.1).sum():,}")
        print(f"    BUY >= 0.4: {(score >= 0.4).sum():,}")
        print(f"    SELL <= -0.1: {(score <= -0.1).sum():,}")
        print(f"    SELL <= -0.4: {(score <= -0.4).sum():,}")
        print()

# Recommended thresholds based on distribution
print(f"💡 Recommended Thresholds (Based on Distribution):")
print()

# Find thresholds that give reasonable signal counts (5-20% of data)
total = len(df)
target_min = max(5, int(total * 0.05))  # At least 5% or 5 signals
target_max = int(total * 0.20)  # At most 20%

# Find BUY threshold
buy_thresholds = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
for thr in buy_thresholds:
    count = (df["final_score"] >= thr).sum()
    if target_min <= count <= target_max:
        print(f"  BUY >= {thr}: {count:,} signals ({count/total*100:.1f}%) ✅ RECOMMENDED")
    elif count > 0:
        print(f"  BUY >= {thr}: {count:,} signals ({count/total*100:.1f}%)")
print()

# Find SELL threshold
sell_thresholds = [-0.1, -0.15, -0.2, -0.25, -0.3, -0.35, -0.4]
for thr in sell_thresholds:
    count = (df["final_score"] <= thr).sum()
    if target_min <= count <= target_max:
        print(f"  SELL <= {thr}: {count:,} signals ({count/total*100:.1f}%) ✅ RECOMMENDED")
    elif count > 0:
        print(f"  SELL <= {thr}: {count:,} signals ({count/total*100:.1f}%)")
print()

print("="*80)
print("ANALYSIS COMPLETE")
print("="*80)

