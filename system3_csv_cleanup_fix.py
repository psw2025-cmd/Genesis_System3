#!/usr/bin/env python3
"""
System3 CSV Cleanup and Fix Script
Removes duplicate headers and fixes data quality issues
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CSV_FILE = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals_with_forward.csv"
BACKUP_FILE = CSV_FILE.with_suffix(".csv.backup")
CLEANED_FILE = CSV_FILE.with_suffix(".csv.cleaned")

print("="*80)
print("SYSTEM3 CSV CLEANUP AND FIX")
print("="*80)
print(f"File: {CSV_FILE}")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

# Step 1: Backup original file
print("1. Creating backup...")
if CSV_FILE.exists():
    import shutil
    shutil.copy2(CSV_FILE, BACKUP_FILE)
    print(f"   ✅ Backup created: {BACKUP_FILE.name}")
else:
    print("   ❌ File not found!")
    sys.exit(1)

# Step 2: Load CSV with robust parsing
print("\n2. Loading CSV...")
try:
    df = pd.read_csv(CSV_FILE, engine="python", on_bad_lines="skip", low_memory=False)
    print(f"   ✅ Loaded {len(df):,} rows, {len(df.columns)} columns")
except Exception as e:
    print(f"   ❌ Failed to load: {e}")
    sys.exit(1)

# Step 3: Remove duplicate header rows
print("\n3. Removing duplicate header rows...")
header_cols = df.columns.tolist()
initial_count = len(df)

# Check for rows that match header exactly
def is_header_row(row):
    """Check if row matches header."""
    row_values = [str(v) for v in row.values]
    header_values = [str(c) for c in header_cols]
    return row_values == header_values

# Remove duplicate headers
mask = df.apply(is_header_row, axis=1)
duplicate_headers = mask.sum()
df_cleaned = df[~mask].copy()

print(f"   Found {duplicate_headers} duplicate header rows")
print(f"   Removed {duplicate_headers} rows")
print(f"   Remaining rows: {len(df_cleaned):,}")

# Step 4: Filter incomplete rows
print("\n4. Filtering incomplete rows...")
critical_cols = ["final_score", "underlying", "strike", "side"]
rows_before = len(df_cleaned)

# Check for rows with missing critical columns
df_cleaned = df_cleaned.dropna(subset=critical_cols)

rows_removed = rows_before - len(df_cleaned)
print(f"   Removed {rows_removed} rows with missing critical columns")
print(f"   Remaining rows: {len(df_cleaned):,}")

# Step 5: Check forward returns coverage
print("\n5. Analyzing forward returns coverage...")
forward_cols = [col for col in df_cleaned.columns if "fwd_ret" in col.lower() or "forward" in col.lower()]
if forward_cols:
    print(f"   Forward return columns found: {forward_cols}")
    for col in forward_cols:
        non_null = df_cleaned[col].notna().sum()
        pct = (non_null / len(df_cleaned) * 100) if len(df_cleaned) > 0 else 0
        print(f"     {col}: {non_null:,} values ({pct:.1f}%)")
else:
    print("   ⚠️ No forward return columns found")

# Step 6: Convert final_score to numeric
print("\n6. Converting final_score to numeric...")
if "final_score" in df_cleaned.columns:
    df_cleaned["final_score"] = pd.to_numeric(df_cleaned["final_score"], errors="coerce")
    non_null = df_cleaned["final_score"].notna().sum()
    print(f"   ✅ Converted to numeric: {non_null:,} valid values")
else:
    print("   ⚠️ final_score column not found")

# Step 7: Save cleaned file
print("\n7. Saving cleaned file...")
try:
    df_cleaned.to_csv(CLEANED_FILE, index=False)
    print(f"   ✅ Cleaned file saved: {CLEANED_FILE.name}")
    print(f"   Rows: {len(df_cleaned):,}")
    print(f"   Columns: {len(df_cleaned.columns)}")
except Exception as e:
    print(f"   ❌ Failed to save: {e}")
    sys.exit(1)

# Step 8: Summary
print("\n" + "="*80)
print("CLEANUP SUMMARY")
print("="*80)
print(f"Original rows: {initial_count:,}")
print(f"Duplicate headers removed: {duplicate_headers}")
print(f"Incomplete rows removed: {rows_removed}")
print(f"Final rows: {len(df_cleaned):,}")
print(f"Rows removed: {initial_count - len(df_cleaned):,} ({((initial_count - len(df_cleaned))/initial_count*100):.1f}%)")
print()
print("Next steps:")
print("  1. Review cleaned file: " + str(CLEANED_FILE))
print("  2. If OK, replace original: copy cleaned file to original location")
print("  3. Fix Phase 221 to prevent duplicate headers")
print("="*80)

