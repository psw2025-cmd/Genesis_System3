"""
SYSTEM3 MASTER PNL PIPELINE REPAIR - HARDENED VERSION
Complete Phases 220 → 221 → 239 with bulletproof error prevention
Hardening: timestamp normalization, index-safe joins, JSON serialization
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_ARCHIVE = PROJECT_ROOT / "storage" / "live" / "archive"

# Create output directories
(STORAGE_LIVE / "forward").mkdir(parents=True, exist_ok=True)
(STORAGE_LIVE / "enriched").mkdir(parents=True, exist_ok=True)
(STORAGE_LIVE / "healed").mkdir(parents=True, exist_ok=True)
(STORAGE_LIVE / "meta").mkdir(parents=True, exist_ok=True)

VIRTUAL_ORDERS_HEALED = STORAGE_LIVE / "healed" / "angel_virtual_orders_healed.csv"
PHASE220_OUTPUT = STORAGE_LIVE / "forward" / "phase220_aggregated_signals.csv"
PHASE221_OUTPUT = STORAGE_LIVE / "forward" / "phase221_forward_returns.csv"
PHASE239_OUTPUT = STORAGE_LIVE / "enriched" / "angel_virtual_orders_with_pnl.csv"

def normalize_timestamps(df, ts_col='ts', expiry_col='expiry'):
    """Shared timestamp parser - normalize ts and expiry columns"""
    if ts_col in df.columns:
        df[ts_col] = pd.to_datetime(df[ts_col], errors='coerce')
    if expiry_col in df.columns:
        df[expiry_col] = pd.to_datetime(df[expiry_col], errors='coerce')
    return df

print(f"\n{'='*80}")
print("SYSTEM3 MASTER PNL PIPELINE REPAIR - HARDENED VERSION")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*80}\n")

# ============================================================================
# PHASE 0: VIRTUAL ORDERS VALIDATION (USE HEALED VERSION)
# ============================================================================
print(f"\n{'='*80}")
print("PHASE 0: VIRTUAL ORDERS VALIDATION & MERGE KEY CLEANING")
print(f"{'='*80}\n")

try:
    # Use healed version if available, else original
    if VIRTUAL_ORDERS_HEALED.exists():
        orders_df = pd.read_csv(VIRTUAL_ORDERS_HEALED, engine="python", on_bad_lines="skip")
        print(f"[INPUT] Using healed orders: {VIRTUAL_ORDERS_HEALED}")
    else:
        orders_df = pd.read_csv(STORAGE_LIVE / "angel_virtual_orders.csv", engine="python", on_bad_lines="skip")
        print(f"[INPUT] Using original orders")
    
    print(f"  Total rows: {len(orders_df)}")
    
    # HARDENING #1: Always normalize timestamps using shared parser
    orders_df = normalize_timestamps(orders_df, ts_col='ts', expiry_col='expiry')
    
    # Normalize other key columns
    orders_df['underlying'] = orders_df['underlying'].astype(str).str.upper().str.strip()
    orders_df['side'] = orders_df['side'].astype(str).str.upper().str.strip()
    orders_df['strike'] = pd.to_numeric(orders_df['strike'], errors='coerce')
    orders_df['lots'] = pd.to_numeric(orders_df['lots'], errors='coerce').fillna(1)
    
    # HARDENING #2: Drop any rows with null merge keys before Phase 239
    merge_key_cols = ['ts', 'underlying', 'strike', 'side', 'expiry']
    merge_key_mask = orders_df[merge_key_cols].notna().all(axis=1)
    orders_before = len(orders_df)
    orders_df = orders_df[merge_key_mask].copy()
    orders_dropped = orders_before - len(orders_df)
    
    print(f"\n[MERGE KEY VALIDATION]")
    print(f"  Rows before cleaning: {orders_before}")
    print(f"  Rows with complete merge keys: {len(orders_df)}")
    print(f"  Rows dropped (null keys): {orders_dropped}")
    print(f"  Valid timestamps: {orders_df['ts'].notna().sum()}")
    print(f"  Valid underlyings: {orders_df['underlying'].notna().sum()}")
    print(f"  Valid strikes: {orders_df['strike'].notna().sum()}")
    print(f"  Valid sides: {orders_df['side'].notna().sum()}")
    print(f"  Valid expiries: {orders_df['expiry'].notna().sum()}")
    
except Exception as e:
    print(f"[ERROR] Phase 0 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# PHASE 220: HISTORICAL AGGREGATION (MULTI-DAY)
# ============================================================================
print(f"\n{'='*80}")
print("PHASE 220: HISTORICAL AGGREGATION (MULTI-DAY)")
print(f"{'='*80}\n")

try:
    archive_dir = STORAGE_ARCHIVE
    all_files = []
    
    if archive_dir.exists():
        archive_files = sorted(list(archive_dir.glob("*.csv")))
    else:
        archive_files = []
    
    print(f"[INPUT] Found {len(archive_files)} archive files")
    
    aggregated_dfs = []
    for csv_file in archive_files:
        try:
            df = pd.read_csv(csv_file, engine="python", on_bad_lines="skip", nrows=None)
            if len(df) > 0:
                print(f"  Loaded: {csv_file.name} ({len(df)} rows)")
                aggregated_dfs.append(df)
        except Exception as e:
            print(f"  [SKIP] {csv_file.name}: {str(e)[:50]}")
    
    if aggregated_dfs:
        aggregated_df = pd.concat(aggregated_dfs, ignore_index=True)
        print(f"\nConcatenating {len(aggregated_dfs)} archive files...")
        print(f"  Before deduplication: {len(aggregated_df)} rows")
        
        # HARDENING #1: Normalize timestamps in aggregated signals
        aggregated_df = normalize_timestamps(aggregated_df, ts_col='ts', expiry_col='expiry')
        
        # Deduplicate
        subset_cols = [c for c in aggregated_df.columns if c in ['ts', 'underlying', 'strike', 'side']]
        if subset_cols:
            aggregated_df = aggregated_df.drop_duplicates(subset=subset_cols, keep='last')
        
        print(f"  After deduplication: {len(aggregated_df)} rows")
        
        # Sort and convert numeric columns
        aggregated_df = aggregated_df.sort_values('ts')
        for col in ['strike', 'ltp', 'final_score', 'ai_score']:
            if col in aggregated_df.columns:
                aggregated_df[col] = pd.to_numeric(aggregated_df[col], errors='coerce')
        
        # Drop rows with null ts (required for Phase 221)
        aggregated_df = aggregated_df[aggregated_df['ts'].notna()].copy()
        
        # Validation
        null_ts = aggregated_df['ts'].isna().sum()
        null_strike = aggregated_df['strike'].isna().sum() if 'strike' in aggregated_df.columns else 0
        unique_dates = aggregated_df['ts'].dt.date.nunique()
        date_range = (aggregated_df['ts'].min(), aggregated_df['ts'].max())
        
        print(f"\n[VALIDATION Phase 220]:")
        print(f"  Total rows: {len(aggregated_df)}")
        print(f"  Unique dates: {unique_dates}")
        print(f"  Date range: {date_range[0]} to {date_range[1]}")
        print(f"  NULL ts: {null_ts}")
        print(f"  NULL strike: {null_strike}")
        
        # Save Phase 220 output
        aggregated_df.to_csv(PHASE220_OUTPUT, index=False, encoding='utf-8')
        print(f"\n[OUTPUT] Saved to: {PHASE220_OUTPUT}")
        
    else:
        print("[ERROR] No archive files found")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Phase 220 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# PHASE 221: FORWARD RETURNS COMPUTATION
# ============================================================================
print(f"\n{'='*80}")
print("PHASE 221: FORWARD RETURNS COMPUTATION")
print(f"{'='*80}\n")

try:
    if aggregated_df is not None and len(aggregated_df) > 0:
        forward_df = aggregated_df.copy()
        
        # Ensure numeric columns
        forward_df['ltp'] = pd.to_numeric(forward_df['ltp'], errors='coerce')
        
        # Sort by timestamp
        forward_df = forward_df.sort_values('ts').reset_index(drop=True)
        
        # Compute forward returns
        forward_horizons = [1, 2, 5, 10, 15]
        
        for horizon in forward_horizons:
            col_name = f'fwd_ret_{horizon}'
            # Shift price data backward by horizon periods to compute forward return
            shifted_price = forward_df['ltp'].shift(-horizon)
            current_price = forward_df['ltp']
            
            # Compute percentage return
            forward_df[col_name] = ((shifted_price - current_price) / current_price * 100).round(6)
        
        # Validation
        coverage = {}
        for horizon in forward_horizons:
            col_name = f'fwd_ret_{horizon}'
            non_null = forward_df[col_name].notna().sum()
            pct = 100 * non_null / len(forward_df)
            coverage[col_name] = (non_null, pct)
        
        print(f"\n[VALIDATION Phase 221]:")
        print(f"  Total rows: {len(forward_df)}")
        for col_name, (non_null, pct) in coverage.items():
            print(f"  {col_name}: {non_null}/{len(forward_df)} ({pct:.1f}%)")
        
        # Save Phase 221 output
        forward_df.to_csv(PHASE221_OUTPUT, index=False, encoding='utf-8')
        print(f"\n[OUTPUT] Saved to: {PHASE221_OUTPUT}")
        
    else:
        print("[ERROR] No aggregated signals from Phase 220")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Phase 221 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# PHASE 239: VIRTUAL PNL ENRICHMENT (4-STAGE BULLETPROOF JOIN)
# ============================================================================
print(f"\n{'='*80}")
print("PHASE 239: VIRTUAL PNL ENRICHMENT (4-STAGE BULLETPROOF JOIN)")
print(f"{'='*80}\n")

try:
    if forward_df is not None and len(forward_df) > 0:
        # Fresh load with hardening
        enrich_orders = orders_df.copy()  # Use cleaned orders from Phase 0
        
        print(f"\n[INPUT]")
        print(f"  Virtual orders: {len(enrich_orders)}")
        print(f"  Forward signals: {len(forward_df)}")
        
        # Initialize forward columns in orders
        forward_cols = [c for c in forward_df.columns if c.startswith('fwd_ret_')]
        for col in forward_cols:
            if col not in enrich_orders.columns:
                enrich_orders[col] = np.nan
        
        # Track matches with SAFE INDEXING
        stage_results = {}
        total_matched = 0
        matched_mask = pd.Series([False] * len(enrich_orders), index=enrich_orders.index)
        
        # STAGE 1: Exact match (ts, underlying, strike, side, expiry)
        print(f"\n[STAGE 1] Exact Match (ts, underlying, strike, side, expiry)")
        try:
            merge_keys = ['ts', 'underlying', 'strike', 'side', 'expiry']
            merge_keys = [k for k in merge_keys if k in enrich_orders.columns and k in forward_df.columns]
            
            if merge_keys and len(enrich_orders) > 0:
                merged_s1 = enrich_orders.reset_index().merge(
                    forward_df[merge_keys + forward_cols].reset_index(),
                    on=merge_keys,
                    how='left',
                    suffixes=('', '_match')
                )
                
                # HARDENING #2: Use reset_index() safely with original index column
                orig_indices = merged_s1['index'].values
                new_matches = merged_s1[forward_cols[0] + '_match'].notna() & enrich_orders.loc[orig_indices, forward_cols[0]].isna().values
                
                stage1_matched = new_matches.sum()
                
                # Copy forward columns where they match (use original index!)
                for col in forward_cols:
                    match_col = col + '_match'
                    if match_col in merged_s1.columns:
                        enrich_orders.loc[orig_indices[new_matches], col] = merged_s1.loc[new_matches, match_col].values
                
                matched_mask = matched_mask | pd.Series(new_matches, index=orig_indices)
                total_matched += stage1_matched
                stage_results['exact'] = int(stage1_matched)
                print(f"  Matched: {stage1_matched}")
            else:
                print(f"  Skipped (no matching keys or empty dataframe)")
                stage_results['exact'] = 0
        except Exception as e:
            print(f"  [ERROR] {str(e)[:80]}")
            stage_results['exact'] = 0
        
        # STAGE 2: AsOf join (±2 seconds, grouped by underlying/strike/side)
        print(f"\n[STAGE 2] AsOf Join (±2 seconds, underlying/strike/side)")
        try:
            unmatched_mask = ~matched_mask
            if unmatched_mask.sum() > 0:
                unmatched = enrich_orders[unmatched_mask].copy()
                unmatched_orig_idx = unmatched.index
                
                # Drop rows with null ts for merge_asof (required)
                unmatched_valid = unmatched[unmatched['ts'].notna()].copy()
                if len(unmatched_valid) > 0:
                    unmatched_valid_orig_idx = unmatched_valid.index
                    unmatched_valid = unmatched_valid.sort_values('ts').reset_index(drop=True)
                    forward_sorted = forward_df.sort_values('ts').reset_index(drop=True)
                    
                    by_cols = ['underlying', 'strike', 'side']
                    by_cols = [c for c in by_cols if c in unmatched_valid.columns and c in forward_sorted.columns]
                    
                    try:
                        if by_cols:
                            merged_s2 = pd.merge_asof(
                                unmatched_valid,
                                forward_sorted[by_cols + ['ts'] + forward_cols].sort_values('ts'),
                                on='ts',
                                by=by_cols,
                                direction='nearest',
                                tolerance=pd.Timedelta(seconds=2),
                                suffixes=('', '_match')
                            )
                        else:
                            merged_s2 = pd.merge_asof(
                                unmatched_valid,
                                forward_sorted[['ts'] + forward_cols].sort_values('ts'),
                                on='ts',
                                direction='nearest',
                                tolerance=pd.Timedelta(seconds=2),
                                suffixes=('', '_match')
                            )
                        
                        # HARDENING #2: Map back using ORIGINAL index safely
                        stage2_matched = 0
                        for local_idx, row in merged_s2.iterrows():
                            orig_idx = unmatched_valid_orig_idx[local_idx]
                            for col in forward_cols:
                                match_col = col + '_match'
                                if match_col in merged_s2.columns and pd.notna(merged_s2.loc[local_idx, match_col]):
                                    enrich_orders.loc[orig_idx, col] = merged_s2.loc[local_idx, match_col]
                                    matched_mask.loc[orig_idx] = True
                                    stage2_matched += 1
                                    break
                        
                        total_matched += stage2_matched
                        stage_results['asof_2s'] = int(stage2_matched)
                        print(f"  Matched: {stage2_matched}")
                    except Exception as e:
                        print(f"  [ERROR] {str(e)[:80]}")
                        stage_results['asof_2s'] = 0
                else:
                    print(f"  Skipped (no valid timestamps)")
                    stage_results['asof_2s'] = 0
            else:
                print(f"  Skipped (no unmatched rows)")
                stage_results['asof_2s'] = 0
        except Exception as e:
            print(f"  [ERROR] {str(e)[:80]}")
            stage_results['asof_2s'] = 0
        
        # STAGE 3: Date-only match (date + underlying + side) - INDEX SAFE
        print(f"\n[STAGE 3] Date-Only Match (date + underlying + side)")
        try:
            unmatched_mask_s3 = ~matched_mask
            if unmatched_mask_s3.sum() > 0:
                unmatched = enrich_orders[unmatched_mask_s3].copy()
                unmatched_orig_idx = unmatched.index
                
                unmatched['date'] = unmatched['ts'].dt.date
                forward_s3 = forward_df.copy()
                forward_s3['date'] = forward_s3['ts'].dt.date
                
                date_keys = ['date', 'underlying', 'side']
                date_keys = [c for c in date_keys if c in unmatched.columns and c in forward_s3.columns]
                
                if date_keys:
                    # HARDENING #2: Reset index and track original index
                    unmatched_reset = unmatched.reset_index().rename(columns={'index': '_orig_idx'})
                    merged_s3 = unmatched_reset.merge(
                        forward_s3[date_keys + forward_cols],
                        on=date_keys,
                        how='left',
                        suffixes=('', '_match')
                    )
                    
                    stage3_matched = 0
                    for local_idx, row in merged_s3.iterrows():
                        orig_idx = merged_s3.loc[local_idx, '_orig_idx']
                        for col in forward_cols:
                            match_col = col + '_match'
                            if match_col in merged_s3.columns and pd.notna(merged_s3.loc[local_idx, match_col]):
                                enrich_orders.loc[orig_idx, col] = merged_s3.loc[local_idx, match_col]
                                matched_mask.loc[orig_idx] = True
                                stage3_matched += 1
                                break
                    
                    total_matched += stage3_matched
                    stage_results['date_only'] = int(stage3_matched)
                    print(f"  Matched: {stage3_matched}")
                else:
                    print(f"  Skipped (no date keys)")
                    stage_results['date_only'] = 0
            else:
                print(f"  Skipped (no unmatched rows)")
                stage_results['date_only'] = 0
        except Exception as e:
            print(f"  [ERROR] {str(e)[:80]}")
            stage_results['date_only'] = 0
        
        # STAGE 4: Nearest timestamp fallback (±5 seconds, underlying + side only)
        print(f"\n[STAGE 4] Nearest Timestamp Fallback (±5 seconds, underlying + side)")
        try:
            unmatched_mask_s4 = ~matched_mask
            if unmatched_mask_s4.sum() > 0:
                unmatched = enrich_orders[unmatched_mask_s4].copy()
                unmatched_valid = unmatched[unmatched['ts'].notna()].copy()
                if len(unmatched_valid) > 0:
                    unmatched_valid_orig_idx = unmatched_valid.index
                    unmatched_valid = unmatched_valid.sort_values('ts').reset_index(drop=True)
                    forward_sorted = forward_df.sort_values('ts').reset_index(drop=True)
                    
                    by_cols_s4 = ['underlying', 'side']
                    by_cols_s4 = [c for c in by_cols_s4 if c in unmatched_valid.columns and c in forward_sorted.columns]
                    
                    try:
                        if by_cols_s4:
                            merged_s4 = pd.merge_asof(
                                unmatched_valid,
                                forward_sorted[by_cols_s4 + ['ts'] + forward_cols].sort_values('ts'),
                                on='ts',
                                by=by_cols_s4,
                                direction='nearest',
                                tolerance=pd.Timedelta(seconds=5),
                                suffixes=('', '_match')
                            )
                        else:
                            merged_s4 = pd.merge_asof(
                                unmatched_valid,
                                forward_sorted[['ts'] + forward_cols].sort_values('ts'),
                                on='ts',
                                direction='nearest',
                                tolerance=pd.Timedelta(seconds=5),
                                suffixes=('', '_match')
                            )
                        
                        stage4_matched = 0
                        for local_idx, row in merged_s4.iterrows():
                            orig_idx = unmatched_valid_orig_idx[local_idx]
                            for col in forward_cols:
                                match_col = col + '_match'
                                if match_col in merged_s4.columns and pd.notna(merged_s4.loc[local_idx, match_col]):
                                    enrich_orders.loc[orig_idx, col] = merged_s4.loc[local_idx, match_col]
                                    matched_mask.loc[orig_idx] = True
                                    stage4_matched += 1
                                    break
                        
                        total_matched += stage4_matched
                        stage_results['nearest'] = int(stage4_matched)
                        print(f"  Matched: {stage4_matched}")
                    except Exception as e:
                        print(f"  [ERROR] {str(e)[:80]}")
                        stage_results['nearest'] = 0
                else:
                    print(f"  Skipped (no valid timestamps)")
                    stage_results['nearest'] = 0
            else:
                print(f"  Skipped (no unmatched rows)")
                stage_results['nearest'] = 0
        except Exception as e:
            print(f"  [ERROR] {str(e)[:80]}")
            stage_results['nearest'] = 0
        
        # Compute PnL columns
        print(f"\n[PNL COMPUTATION]")
        for col in forward_cols:
            pnl_col = col.replace('fwd_ret_', 'pnl_')
            # Ensure numeric types before multiplication
            fwd_ret = pd.to_numeric(enrich_orders[col], errors='coerce')
            lots = pd.to_numeric(enrich_orders['lots'], errors='coerce').fillna(1)
            enrich_orders[pnl_col] = (fwd_ret * lots).round(6)
        
        # Final validation
        has_fwd = enrich_orders[forward_cols[0]].notna().sum()
        match_rate = 100 * has_fwd / len(enrich_orders) if len(enrich_orders) > 0 else 0
        
        print(f"\n[FINAL RESULTS]")
        print(f"  Total processed: {len(enrich_orders)}")
        print(f"  Orders with forward returns: {has_fwd}")
        print(f"  Match rate: {match_rate:.1f}%")
        print(f"  Stage breakdown:")
        for stage, count in stage_results.items():
            print(f"    {stage}: {count}")
        
        # Save Phase 239 output
        enrich_orders.to_csv(PHASE239_OUTPUT, index=False, encoding='utf-8')
        print(f"\n[OUTPUT] Saved to: {PHASE239_OUTPUT}")
        
        # Create validation JSON - HARDENING #3: Convert numpy types to native Python
        validation = {
            "timestamp": datetime.now().isoformat(),
            "total_orders": int(len(enrich_orders)),
            "matched": int(has_fwd),
            "match_rate_pct": float(match_rate),
            "stage_breakdown": {k: int(v) for k, v in stage_results.items()},
            "forward_columns": forward_cols,
        }
        
        with open(STORAGE_LIVE / "meta" / "PHASE239_FINAL_VALIDATION.json", 'w') as f:
            json.dump(validation, f, indent=2)
        
    else:
        print("[ERROR] No forward returns from Phase 221")
        sys.exit(1)

except Exception as e:
    print(f"[ERROR] Phase 239 failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n{'='*80}")
print("MASTER PIPELINE REPAIR - HARDENED - COMPLETE")
print(f"{'='*80}\n")
