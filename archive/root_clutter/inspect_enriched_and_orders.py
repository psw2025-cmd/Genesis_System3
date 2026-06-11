#!/usr/bin/env python
 
"""
Inspect columns and possible merge keys for:
- storage/live/enriched/angel_virtual_orders_with_pnl.csv
- storage/live/angel_virtual_orders.csv
 
Goal: see which columns overlap so we can choose proper merge keys
for filling the 'symbol' column in enriched PnL.
"""
 
import os
from pathlib import Path
 
import pandas as pd
 
ROOT = Path(__file__).resolve().parent
STORAGE_LIVE = ROOT / "storage" / "live"
ENRICHED_PATH = STORAGE_LIVE / "enriched" / "angel_virtual_orders_with_pnl.csv"
RAW_ORDERS_PATH = STORAGE_LIVE / "angel_virtual_orders.csv"
 
 
def main():
    print("ROOT:", ROOT)
 
    if not ENRICHED_PATH.exists():
        print("[ERROR] Enriched PnL file not found:", ENRICHED_PATH)
        return
 
    if not RAW_ORDERS_PATH.exists():
        print("[ERROR] Raw orders file not found:", RAW_ORDERS_PATH)
        return
 
    print("\n=== ENRICHED PNL FILE ===")
    print("Path:", ENRICHED_PATH)
    df_enriched = pd.read_csv(ENRICHED_PATH)
    print("Shape:", df_enriched.shape)
    print("Columns:")
    print(sorted(df_enriched.columns.tolist()))
    print("\nFirst 3 rows:")
    print(df_enriched.head(3))
 
    print("\n=== RAW ORDERS FILE ===")
    print("Path:", RAW_ORDERS_PATH)
    df_raw = pd.read_csv(RAW_ORDERS_PATH)
    print("Shape:", df_raw.shape)
    print("Columns:")
    print(sorted(df_raw.columns.tolist()))
    print("\nFirst 3 rows:")
    print(df_raw.head(3))
 
    # Show common columns
    cols_enriched = set(df_enriched.columns)
    cols_raw = set(df_raw.columns)
    common = sorted(cols_enriched & cols_raw)
    only_enriched = sorted(cols_enriched - cols_raw)
    only_raw = sorted(cols_raw - cols_enriched)
 
    print("\n=== COLUMN OVERLAP ===")
    print("Common columns:")
    print(common)
    print("\nOnly in enriched:")
    print(only_enriched)
    print("\nOnly in raw orders:")
    print(only_raw)
 
    # Show uniqueness of likely key candidates in raw file
    key_candidates = ["order_id", "ts", "underlying", "expiry", "strike", "side", "token"]
    print("\n=== UNIQUENESS IN RAW ORDERS (for candidate keys) ===")
    for k in key_candidates:
        if k in df_raw.columns:
            n_unique = df_raw[k].nunique(dropna=False)
            n_rows = len(df_raw)
            print(f"{k}: unique={n_unique}, rows={n_rows}")
 
    print("\nDone.")
 
 
if __name__ == "__main__":
    main()
 