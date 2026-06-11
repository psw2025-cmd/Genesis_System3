#!/usr/bin/env python3
"""
System3 CSV Ultra Audit - Comprehensive Quality Control
Analyzes angel_index_ai_signals_with_forward.csv in extreme detail
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import json

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CSV_FILE = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals_with_forward.csv"
OUTPUT_REPORT = PROJECT_ROOT / "docs" / "SYSTEM3_CSV_ULTRA_AUDIT_REPORT.md"

print("="*80)
print("SYSTEM3 CSV ULTRA AUDIT - COMPREHENSIVE QUALITY CONTROL")
print("="*80)
print(f"File: {CSV_FILE}")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

# Load CSV with multiple strategies
def load_csv_robust():
    """Load CSV with multiple fallback strategies."""
    strategies = [
        lambda: pd.read_csv(CSV_FILE, engine="python", on_bad_lines="skip"),
        lambda: pd.read_csv(CSV_FILE, engine="python", on_bad_lines="skip", low_memory=False),
        lambda: pd.read_csv(CSV_FILE, sep=",", engine="python", on_bad_lines="skip"),
    ]
    
    for i, strategy in enumerate(strategies):
        try:
            df = strategy()
            print(f"✅ Loaded CSV using strategy {i+1}")
            return df
        except Exception as e:
            print(f"⚠️ Strategy {i+1} failed: {e}")
            continue
    
    return None

# Load data
df = load_csv_robust()
if df is None:
    print("❌ Failed to load CSV file")
    sys.exit(1)

print(f"\n📊 BASIC STATISTICS")
print("-"*80)
print(f"Total Rows: {len(df):,}")
print(f"Total Columns: {len(df.columns)}")
print(f"File Size: {CSV_FILE.stat().st_size / 1024:.2f} KB")
print()

# Column analysis
print("📋 COLUMN ANALYSIS")
print("-"*80)
print(f"Column Names ({len(df.columns)} total):")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:3d}. {col}")
print()

# Data type analysis
print("🔍 DATA TYPE ANALYSIS")
print("-"*80)
dtype_counts = df.dtypes.value_counts()
for dtype, count in dtype_counts.items():
    print(f"  {dtype}: {count} columns")
print()

# Missing values analysis
print("❌ MISSING VALUES ANALYSIS")
print("-"*80)
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    "Column": missing.index,
    "Missing Count": missing.values,
    "Missing %": missing_pct.values
})
missing_df = missing_df[missing_df["Missing Count"] > 0].sort_values("Missing Count", ascending=False)

if len(missing_df) > 0:
    print(f"Columns with missing values ({len(missing_df)}):")
    for _, row in missing_df.head(20).iterrows():
        print(f"  {row['Column']:40s}: {row['Missing Count']:6,} ({row['Missing %']:6.2f}%)")
    if len(missing_df) > 20:
        print(f"  ... and {len(missing_df) - 20} more columns with missing values")
else:
    print("  ✅ No missing values found")
print()

# Duplicate rows
print("🔄 DUPLICATE ROWS ANALYSIS")
print("-"*80)
duplicate_count = df.duplicated().sum()
print(f"Total Duplicate Rows: {duplicate_count:,}")
if duplicate_count > 0:
    print(f"  ⚠️ WARNING: {duplicate_count} duplicate rows found")
    # Check for duplicate headers
    if duplicate_count > len(df) * 0.1:
        print(f"  ⚠️ CRITICAL: High duplicate rate ({duplicate_count/len(df)*100:.1f}%) - possible header duplication")
else:
    print("  ✅ No duplicate rows")
print()

# Critical columns check
print("🎯 CRITICAL COLUMNS CHECK")
print("-"*80)
critical_columns = [
    "underlying", "strike", "side", "final_score", "signal",
    "fwd_ret_1", "fwd_ret_3", "fwd_ret_5",
    "ts", "ltp", "spot", "expiry"
]

for col in critical_columns:
    if col in df.columns:
        missing = df[col].isnull().sum()
        pct = (missing / len(df) * 100) if len(df) > 0 else 0
        status = "✅" if missing == 0 else f"⚠️ ({missing} missing, {pct:.1f}%)"
        print(f"  {col:25s}: {status}")
    else:
        print(f"  {col:25s}: ❌ MISSING")
print()

# Forward returns analysis
print("📈 FORWARD RETURNS ANALYSIS")
print("-"*80)
forward_cols = [col for col in df.columns if "fwd_ret" in col.lower() or "forward" in col.lower()]
if forward_cols:
    print(f"Forward Return Columns Found: {len(forward_cols)}")
    for col in forward_cols:
        non_null = df[col].notna().sum()
        pct = (non_null / len(df) * 100) if len(df) > 0 else 0
        if non_null > 0:
            mean_val = df[col].mean()
            std_val = df[col].std()
            print(f"  {col:25s}: {non_null:6,} values ({pct:5.1f}%), mean={mean_val:.4f}, std={std_val:.4f}")
        else:
            print(f"  {col:25s}: ⚠️ All null")
else:
    print("  ⚠️ No forward return columns found")
print()

# final_score analysis
print("📊 FINAL_SCORE ANALYSIS")
print("-"*80)
if "final_score" in df.columns:
    # Convert to numeric
    df["final_score"] = pd.to_numeric(df["final_score"], errors="coerce")
    
    non_null = df["final_score"].notna().sum()
    null_count = df["final_score"].isna().sum()
    
    if non_null > 0:
        score_stats = df["final_score"].describe()
        print(f"  Non-null values: {non_null:,} ({non_null/len(df)*100:.1f}%)")
        print(f"  Null values: {null_count:,} ({null_count/len(df)*100:.1f}%)")
        print(f"  Mean: {score_stats['mean']:.6f}")
        print(f"  Std: {score_stats['std']:.6f}")
        print(f"  Min: {score_stats['min']:.6f}")
        print(f"  25%: {score_stats['25%']:.6f}")
        print(f"  50%: {score_stats['50%']:.6f}")
        print(f"  75%: {score_stats['75%']:.6f}")
        print(f"  Max: {score_stats['max']:.6f}")
        
        # Count by threshold ranges
        buy_count = (df["final_score"] >= 0.4).sum()
        sell_count = (df["final_score"] <= -0.3).sum()
        hold_count = len(df) - buy_count - sell_count
        
        print(f"\n  Threshold Analysis:")
        print(f"    BUY (>= 0.4): {buy_count:,} ({buy_count/len(df)*100:.1f}%)")
        print(f"    SELL (<= -0.3): {sell_count:,} ({sell_count/len(df)*100:.1f}%)")
        print(f"    HOLD: {hold_count:,} ({hold_count/len(df)*100:.1f}%)")
    else:
        print("  ⚠️ All final_score values are null")
else:
    print("  ❌ final_score column not found")
print()

# Signal distribution
print("📡 SIGNAL DISTRIBUTION")
print("-"*80)
if "signal" in df.columns:
    signal_counts = df["signal"].value_counts()
    print(f"Signal Types ({len(signal_counts)}):")
    for signal, count in signal_counts.items():
        pct = (count / len(df) * 100) if len(df) > 0 else 0
        print(f"  {str(signal):20s}: {count:6,} ({pct:5.1f}%)")
else:
    print("  ⚠️ signal column not found")
print()

# Underlying distribution
print("🏢 UNDERLYING DISTRIBUTION")
print("-"*80)
if "underlying" in df.columns:
    underlying_counts = df["underlying"].value_counts()
    print(f"Underlyings ({len(underlying_counts)}):")
    for underlying, count in underlying_counts.items():
        pct = (count / len(df) * 100) if len(df) > 0 else 0
        print(f"  {str(underlying):15s}: {count:6,} ({pct:5.1f}%)")
else:
    print("  ⚠️ underlying column not found")
print()

# Timestamp analysis
print("⏰ TIMESTAMP ANALYSIS")
print("-"*80)
if "ts" in df.columns:
    try:
        df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
        valid_ts = df["ts"].notna().sum()
        print(f"  Valid timestamps: {valid_ts:,} ({valid_ts/len(df)*100:.1f}%)")
        
        if valid_ts > 0:
            min_ts = df["ts"].min()
            max_ts = df["ts"].max()
            print(f"  Earliest: {min_ts}")
            print(f"  Latest: {max_ts}")
            print(f"  Time span: {max_ts - min_ts}")
    except Exception as e:
        print(f"  ⚠️ Error parsing timestamps: {e}")
else:
    print("  ⚠️ ts column not found")
print()

# Data quality issues
print("🚨 DATA QUALITY ISSUES")
print("-"*80)
issues = []

# Check for duplicate headers
if duplicate_count > len(df) * 0.1:
    issues.append(f"CRITICAL: High duplicate rate ({duplicate_count/len(df)*100:.1f}%)")

# Check for empty rows
empty_rows = df.isnull().all(axis=1).sum()
if empty_rows > 0:
    issues.append(f"WARNING: {empty_rows} completely empty rows")

# Check for string values in numeric columns
numeric_cols = ["strike", "ltp", "spot", "final_score"]
for col in numeric_cols:
    if col in df.columns:
        # Try to convert to numeric
        converted = pd.to_numeric(df[col], errors="coerce")
        non_numeric = converted.isna().sum() - df[col].isna().sum()
        if non_numeric > 0:
            issues.append(f"WARNING: {non_numeric} non-numeric values in {col}")

# Check for forward returns consistency
if forward_cols:
    for col in forward_cols:
        if df[col].notna().sum() == 0:
            issues.append(f"WARNING: {col} is completely empty")

if issues:
    for issue in issues:
        print(f"  ⚠️ {issue}")
else:
    print("  ✅ No major data quality issues detected")
print()

# Generate report
print("📝 GENERATING DETAILED REPORT...")
print("-"*80)

report_content = f"""# System3 CSV Ultra Audit Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**File Analyzed**: `{CSV_FILE.name}`  
**File Size**: {CSV_FILE.stat().st_size / 1024:.2f} KB

---

## Executive Summary

- **Total Rows**: {len(df):,}
- **Total Columns**: {len(df.columns)}
- **Duplicate Rows**: {duplicate_count:,}
- **Data Quality**: {'⚠️ ISSUES FOUND' if issues else '✅ GOOD'}

---

## Detailed Analysis

### Column List ({len(df.columns)} columns)

"""
for i, col in enumerate(df.columns, 1):
    report_content += f"{i:3d}. `{col}`\n"

report_content += f"""

### Missing Values

"""
if len(missing_df) > 0:
    report_content += "| Column | Missing Count | Missing % |\n"
    report_content += "|--------|---------------|-----------|\n"
    for _, row in missing_df.iterrows():
        report_content += f"| `{row['Column']}` | {row['Missing Count']:,} | {row['Missing %']:.2f}% |\n"
else:
    report_content += "✅ No missing values\n"

report_content += f"""

### Critical Columns Status

"""
for col in critical_columns:
    if col in df.columns:
        missing = df[col].isnull().sum()
        pct = (missing / len(df) * 100) if len(df) > 0 else 0
        status = "✅" if missing == 0 else f"⚠️ ({missing} missing)"
        report_content += f"- `{col}`: {status}\n"
    else:
        report_content += f"- `{col}`: ❌ MISSING\n"

report_content += f"""

### Forward Returns Status

"""
if forward_cols:
    report_content += "| Column | Non-Null | Coverage | Mean | Std |\n"
    report_content += "|--------|----------|----------|------|-----|\n"
    for col in forward_cols:
        non_null = df[col].notna().sum()
        pct = (non_null / len(df) * 100) if len(df) > 0 else 0
        if non_null > 0:
            mean_val = df[col].mean()
            std_val = df[col].std()
            report_content += f"| `{col}` | {non_null:,} | {pct:.1f}% | {mean_val:.4f} | {std_val:.4f} |\n"
        else:
            report_content += f"| `{col}` | 0 | 0% | N/A | N/A |\n"
else:
    report_content += "⚠️ No forward return columns found\n"

report_content += f"""

### Data Quality Issues

"""
if issues:
    for issue in issues:
        report_content += f"- ⚠️ {issue}\n"
else:
    report_content += "✅ No major issues detected\n"

report_content += f"""

---

**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status**: {'⚠️ REVIEW REQUIRED' if issues else '✅ PASSED'}
"""

OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_REPORT.write_text(report_content, encoding="utf-8")

print(f"✅ Report generated: {OUTPUT_REPORT}")
print()
print("="*80)
print("AUDIT COMPLETE")
print("="*80)

