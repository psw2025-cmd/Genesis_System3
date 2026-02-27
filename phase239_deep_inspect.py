"""
PHASE B — DEEP INSPECTION: Why is Phase 239 enrichment 0%?

This script inspects both datasets and merge keys in detail.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
HEALED_DIR = STORAGE_LIVE / "healed"
FORWARD_DIR = STORAGE_LIVE / "forward"
ENRICHED_DIR = STORAGE_LIVE / "enriched"

# Add venv check
EXPECTED_VENV = "C:\\Genesis_System3\\venv\\Scripts\\python.exe"
if not sys.executable.lower().endswith("python.exe") or "venv" not in sys.executable:
    print(f"❌ VENV MISMATCH: {sys.executable}")
    print(f"   Expected: {EXPECTED_VENV}")
    sys.exit(1)
print(f"✅ VENV OK: {sys.executable}")

def inspect_dataset(name: str, filepath: Path) -> dict:
    """Deep inspect a dataset."""
    if not filepath.exists():
        print(f"\n❌ {name} NOT FOUND: {filepath}")
        return {}
    
    df = pd.read_csv(filepath)
    print(f"\n{'='*70}")
    print(f"DATASET: {name}")
    print(f"{'='*70}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nDTYPES:\n{df.dtypes}")
    
    # Merge keys
    merge_keys = ["ts", "underlying", "strike", "side", "expiry"]
    print(f"\n{'='*70}")
    print(f"MERGE KEYS ANALYSIS")
    print(f"{'='*70}")
    
    key_analysis = {}
    for key in merge_keys:
        if key in df.columns:
            col_data = df[key]
            null_count = col_data.isna().sum()
            unique_count = col_data.nunique()
            key_analysis[key] = {
                "present": True,
                "dtype": str(col_data.dtype),
                "null_count": int(null_count),
                "null_pct": round(null_count / len(df) * 100, 2),
                "unique": int(unique_count),
                "sample": col_data.dropna().head(3).tolist(),
            }
            print(f"\n✓ {key}")
            print(f"  dtype: {col_data.dtype}")
            print(f"  null: {null_count}/{len(df)} ({null_count/len(df)*100:.1f}%)")
            print(f"  unique: {unique_count}")
            print(f"  sample: {col_data.dropna().head(3).tolist()}")
        else:
            key_analysis[key] = {"present": False}
            print(f"\n✗ {key} — MISSING")
    
    return key_analysis

# 1. Inspect signals (Phase 221 output)
print("\n" + "="*70)
print("PHASE B1 — INSPECT DATASETS")
print("="*70)

signals_path = FORWARD_DIR / "phase221_forward_returns.csv"
orders_path = HEALED_DIR / "angel_virtual_orders_healed.csv"

signals_keys = inspect_dataset("SIGNALS (Phase 221)", signals_path)
orders_keys = inspect_dataset("ORDERS (Healed)", orders_path)

# 2. Sample rows with merge keys
print(f"\n{'='*70}")
print("SAMPLE ROWS - SIGNALS (first 5 with merge keys)")
print(f"{'='*70}")
df_sig = pd.read_csv(signals_path)
merge_cols = [c for c in ["ts", "underlying", "strike", "side", "expiry"] if c in df_sig.columns]
if merge_cols:
    print(df_sig[merge_cols].head(5).to_string())

print(f"\n{'='*70}")
print("SAMPLE ROWS - ORDERS (first 5 with merge keys)")
print(f"{'='*70}")
df_ord = pd.read_csv(orders_path)
merge_cols = [c for c in ["ts", "underlying", "strike", "side", "expiry"] if c in df_ord.columns]
if merge_cols:
    print(df_ord[merge_cols].head(5).to_string())

# 3. Check for EXACT KEY MISMATCH
print(f"\n{'='*70}")
print("MERGE KEY MISMATCH CHECK")
print(f"{'='*70}")

if "underlying" in df_sig.columns and "underlying" in df_ord.columns:
    sig_underlying = set(df_sig["underlying"].dropna().unique())
    ord_underlying = set(df_ord["underlying"].dropna().unique())
    
    print(f"\nSignals underlying: {sig_underlying}")
    print(f"Orders underlying: {ord_underlying}")
    print(f"Common: {sig_underlying & ord_underlying}")
    print(f"Only in signals: {sig_underlying - ord_underlying}")
    print(f"Only in orders: {ord_underlying - sig_underlying}")

if "strike" in df_sig.columns and "strike" in df_ord.columns:
    print(f"\nSignals strike dtype: {df_sig['strike'].dtype}")
    print(f"Orders strike dtype: {df_ord['strike'].dtype}")
    sig_strike = pd.to_numeric(df_sig["strike"], errors="coerce").dropna().unique()[:5]
    ord_strike = pd.to_numeric(df_ord["strike"], errors="coerce").dropna().unique()[:5]
    print(f"Signals strike sample: {sig_strike}")
    print(f"Orders strike sample: {ord_strike}")

if "side" in df_sig.columns and "side" in df_ord.columns:
    print(f"\nSignals side unique: {df_sig['side'].dropna().unique()}")
    print(f"Orders side unique: {df_ord['side'].dropna().unique()}")

if "expiry" in df_sig.columns and "expiry" in df_ord.columns:
    print(f"\nSignals expiry dtype: {df_sig['expiry'].dtype}")
    print(f"Orders expiry dtype: {df_ord['expiry'].dtype}")
    sig_expiry = df_sig['expiry'].dropna().unique()[:3]
    ord_expiry = df_ord['expiry'].dropna().unique()[:3]
    print(f"Signals expiry sample: {sig_expiry}")
    print(f"Orders expiry sample: {ord_expiry}")

if "ts" in df_sig.columns and "ts" in df_ord.columns:
    print(f"\nSignals ts dtype: {df_sig['ts'].dtype}")
    print(f"Orders ts dtype: {df_ord['ts'].dtype}")
    sig_ts = df_sig['ts'].dropna().unique()[:3]
    ord_ts = df_ord['ts'].dropna().unique()[:3]
    print(f"Signals ts sample: {sig_ts}")
    print(f"Orders ts sample: {ord_ts}")

print(f"\n{'='*70}")
print("INSPECTION COMPLETE")
print(f"{'='*70}")
