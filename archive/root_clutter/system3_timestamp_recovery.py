"""
SYSTEM3 VIRTUAL ORDERS TIMESTAMP RECOVERY & HEALING
Complete recovery pipeline for missing timestamps in virtual orders
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"

VIRTUAL_ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders.csv"
HEALED_OUTPUT = STORAGE_LIVE / "healed" / "angel_virtual_orders_healed.csv"
HEARTBEAT_FILE = PROJECT_ROOT / "system3_daily_heartbeat.json"

# Create output directory
HEALED_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

print(f"\n{'='*80}")
print("VIRTUAL ORDERS TIMESTAMP RECOVERY & HEALING")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*80}\n")

# Load virtual orders
print("[STEP 1] Loading virtual orders...")
orders_df = pd.read_csv(VIRTUAL_ORDERS_CSV, engine="python", on_bad_lines="skip")
print(f"  Total rows: {len(orders_df)}")
print(f"  Columns: {orders_df.columns.tolist()}")

# Parse existing timestamps
orders_df['ts'] = pd.to_datetime(orders_df['ts'], errors='coerce')
orders_df['expiry'] = pd.to_datetime(orders_df['expiry'], errors='coerce')

# Audit
valid_ts = orders_df['ts'].notna().sum()
null_ts = orders_df['ts'].isna().sum()

print(f"\n[STEP 2] Timestamp Audit:")
print(f"  Valid timestamps: {valid_ts} ({100*valid_ts/len(orders_df):.1f}%)")
print(f"  NULL timestamps: {null_ts} ({100*null_ts/len(orders_df):.1f}%)")

# Strategy 1: Use nearby valid timestamps
print(f"\n[STEP 3] Recovery Strategy 1: Interpolate from nearby valid rows")
recovery_1 = 0

for i in range(len(orders_df)):
    if pd.isna(orders_df.loc[i, 'ts']):
        # Look backward for valid timestamp
        for j in range(i-1, max(i-10, -1), -1):
            if pd.notna(orders_df.loc[j, 'ts']):
                # Use previous timestamp + small offset
                orders_df.loc[i, 'ts'] = orders_df.loc[j, 'ts'] + timedelta(seconds=1)
                recovery_1 += 1
                break
        
        # If still null, look forward
        if pd.isna(orders_df.loc[i, 'ts']):
            for j in range(i+1, min(i+10, len(orders_df))):
                if pd.notna(orders_df.loc[j, 'ts']):
                    # Use next timestamp - small offset
                    orders_df.loc[i, 'ts'] = orders_df.loc[j, 'ts'] - timedelta(seconds=1)
                    recovery_1 += 1
                    break

print(f"  Recovered from nearby rows: {recovery_1}")

# Strategy 2: Use heartbeat file
print(f"\n[STEP 4] Recovery Strategy 2: Use heartbeat snapshots")
recovery_2 = 0

try:
    if HEARTBEAT_FILE.exists():
        with open(HEARTBEAT_FILE, 'r') as f:
            heartbeat = json.load(f)
            if 'snapshot_timestamp' in heartbeat:
                hb_ts = pd.to_datetime(heartbeat['snapshot_timestamp'], errors='coerce')
                if pd.notna(hb_ts):
                    # Find remaining nulls and use heartbeat timestamp
                    null_mask = orders_df['ts'].isna()
                    orders_df.loc[null_mask, 'ts'] = hb_ts
                    recovery_2 = null_mask.sum()
                    print(f"  Recovered from heartbeat: {recovery_2}")
except Exception as e:
    print(f"  [SKIP] Heartbeat recovery: {str(e)[:60]}")

# Strategy 3: Use current date + sequence number for ordering
print(f"\n[STEP 5] Recovery Strategy 3: Generate synthetic timestamps from sequence")
recovery_3 = 0

remaining_null = orders_df['ts'].isna().sum()
if remaining_null > 0:
    # Get base date from expiry column if available
    if 'expiry' in orders_df.columns and orders_df['expiry'].notna().any():
        base_date = orders_df[orders_df['expiry'].notna()]['expiry'].dt.date.min()
    else:
        base_date = pd.Timestamp.now().date()
    
    base_ts = pd.Timestamp(base_date) + timedelta(hours=9)  # Market open time
    
    null_indices = orders_df[orders_df['ts'].isna()].index
    for idx, orig_idx in enumerate(null_indices):
        orders_df.loc[orig_idx, 'ts'] = base_ts + timedelta(seconds=idx)
        recovery_3 += 1
    
    print(f"  Generated synthetic timestamps: {recovery_3}")

# Final audit
final_valid = orders_df['ts'].notna().sum()
final_null = orders_df['ts'].isna().sum()

print(f"\n[STEP 6] Final Timestamp Audit:")
print(f"  Valid timestamps after healing: {final_valid} ({100*final_valid/len(orders_df):.1f}%)")
print(f"  Remaining NULL: {final_null} ({100*final_null/len(orders_df):.1f}%)")
print(f"  Total recovered: {final_valid - valid_ts}")
print(f"    From nearby: {recovery_1}")
print(f"    From heartbeat: {recovery_2}")
print(f"    Synthetic: {recovery_3}")

# Data quality checks
print(f"\n[STEP 7] Data Quality Validation:")
print(f"  Date range: {orders_df['ts'].min()} to {orders_df['ts'].max()}")
print(f"  Unique dates: {orders_df['ts'].dt.date.nunique()}")

# Check for duplicates
dup_count = orders_df.duplicated(subset=['ts', 'underlying', 'strike', 'side']).sum()
print(f"  Exact duplicates: {dup_count}")

# Sample of healed data
print(f"\n[STEP 8] Sample of healed data (first 10 rows):")
print(orders_df[['ts', 'underlying', 'strike', 'side', 'expiry', 'lots']].head(10).to_string())

# Save healed version
orders_df.to_csv(HEALED_OUTPUT, index=False, encoding='utf-8')
print(f"\n[OUTPUT] Healed orders saved to: {HEALED_OUTPUT}")

# Create healing report
healing_report = {
    "timestamp": datetime.now().isoformat(),
    "input_file": str(VIRTUAL_ORDERS_CSV),
    "output_file": str(HEALED_OUTPUT),
    "total_rows": len(orders_df),
    "original_valid_ts": valid_ts,
    "original_null_ts": null_ts,
    "recovery_strategies": {
        "nearby_interpolation": int(recovery_1),
        "heartbeat_snapshot": int(recovery_2),
        "synthetic_generation": int(recovery_3),
    },
    "final_valid_ts": int(final_valid),
    "final_null_ts": int(final_null),
    "date_range": {
        "min": orders_df['ts'].min().isoformat(),
        "max": orders_df['ts'].max().isoformat(),
    },
    "unique_dates": int(orders_df['ts'].dt.date.nunique()),
    "duplicates": int(dup_count),
}

report_file = STORAGE_LIVE / "meta" / "TIMESTAMP_RECOVERY_REPORT.json"
report_file.parent.mkdir(parents=True, exist_ok=True)
with open(report_file, 'w') as f:
    json.dump(healing_report, f, indent=2, default=str)

print(f"\n[REPORT] Saved to: {report_file}")

print(f"\n{'='*80}")
print("TIMESTAMP RECOVERY COMPLETE")
print(f"{'='*80}\n")
