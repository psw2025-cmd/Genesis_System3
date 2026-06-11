"""
SYSTEM3 MASTER PNL PIPELINE REPAIR & VALIDATION
Complete Phases 220 → 221 → 239 with bulletproof join logic
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_ARCHIVE = PROJECT_ROOT / "storage" / "live" / "archive"

# Create output directories
(STORAGE_LIVE / "forward").mkdir(parents=True, exist_ok=True)
(STORAGE_LIVE / "enriched").mkdir(parents=True, exist_ok=True)
(STORAGE_LIVE / "healed").mkdir(parents=True, exist_ok=True)
(STORAGE_LIVE / "meta").mkdir(parents=True, exist_ok=True)

VIRTUAL_ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders.csv"
PHASE220_OUTPUT = STORAGE_LIVE / "forward" / "phase220_aggregated_signals.csv"
PHASE221_OUTPUT = STORAGE_LIVE / "forward" / "phase221_forward_returns.csv"
PHASE239_OUTPUT = STORAGE_LIVE / "enriched" / "angel_virtual_orders_with_pnl.csv"

print(f"\n{'='*80}")
print("SYSTEM3 MASTER PNL PIPELINE REPAIR & VALIDATION")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*80}\n")

# ============================================================================
# PHASE 0: VIRTUAL ORDERS TIMESTAMP INTEGRITY & DATA HEALING
# ============================================================================
print(f"\n{'='*80}")
print("PHASE 0: VIRTUAL ORDERS TIMESTAMP INTEGRITY & DATA HEALING")
print(f"{'='*80}\n")

try:
    orders_df = pd.read_csv(VIRTUAL_ORDERS_CSV, engine="python", on_bad_lines="skip")
    print(f"[AUDIT] Virtual Orders Input:")
    print(f"  Total rows: {len(orders_df)}")
    print(f"  Columns: {orders_df.columns.tolist()}")
    
    # Parse timestamps
    orders_df['ts'] = pd.to_datetime(orders_df['ts'], errors='coerce')
    
    valid_ts = orders_df['ts'].notna().sum()
    null_ts = orders_df['ts'].isna().sum()
    
    print(f"\n[TIMESTAMP AUDIT]")
    print(f"  Valid timestamps: {valid_ts} ({100*valid_ts/len(orders_df):.1f}%)")
    print(f"  NULL timestamps: {null_ts} ({100*null_ts/len(orders_df):.1f}%)")
    
    unique_dates = orders_df['ts'].dt.date.nunique()
    print(f"\n[FINAL] Virtual Orders Validation:")
    print(f"  Rows with valid ts: {valid_ts}")
    print(f"  Unique dates: {unique_dates}")
    
except Exception as e:
    print(f"[ERROR] Phase 0 failed: {e}")
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
        archive_files = list(archive_dir.glob("*.csv"))
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
        
        # Deduplicate
        subset_cols = [c for c in aggregated_df.columns if c in ['ts', 'underlying', 'strike', 'side']]
        if subset_cols:
            aggregated_df = aggregated_df.drop_duplicates(subset=subset_cols, keep='last')
        
        print(f"  After deduplication: {len(aggregated_df)} rows")
        
        # Parse timestamps
        aggregated_df['ts'] = pd.to_datetime(aggregated_df['ts'], errors='coerce')
        aggregated_df = aggregated_df.sort_values('ts')
        
        # Convert numeric columns
        for col in ['strike', 'ltp', 'final_score', 'ai_score']:
            if col in aggregated_df.columns:
                aggregated_df[col] = pd.to_numeric(aggregated_df[col], errors='coerce')
        
        # Validation
        null_ts = aggregated_df['ts'].isna().sum()
        null_strike = aggregated_df['strike'].isna().sum() if 'strike' in aggregated_df.columns else 0
        unique_dates = aggregated_df['ts'].dt.date.nunique() if null_ts < len(aggregated_df) else 0
        date_range = (aggregated_df['ts'].min(), aggregated_df['ts'].max()) if null_ts < len(aggregated_df) else (None, None)
        
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
        print("[WARNING] No archive files found, using existing phase220 output or creating empty")
        aggregated_df = None

except Exception as e:
    print(f"[ERROR] Phase 220 failed: {e}")
    import traceback
    traceback.print_exc()
    aggregated_df = None

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
        print("[WARNING] No aggregated signals from Phase 220")
        forward_df = None

except Exception as e:
    print(f"[ERROR] Phase 221 failed: {e}")
    import traceback
    traceback.print_exc()
    forward_df = None

# ============================================================================
# PHASE 239: VIRTUAL PNL ENRICHMENT (4-STAGE BULLETPROOF JOIN)
# ============================================================================
print(f"\n{'='*80}")
print("PHASE 239: VIRTUAL PNL ENRICHMENT (4-STAGE BULLETPROOF JOIN)")
print(f"{'='*80}\n")

try:
    if forward_df is not None and len(forward_df) > 0:
        # Load virtual orders (fresh)
        enrich_orders = pd.read_csv(VIRTUAL_ORDERS_CSV, engine="python", on_bad_lines="skip")
        enrich_orders['ts'] = pd.to_datetime(enrich_orders['ts'], errors='coerce')
        
        # Convert numeric columns
        enrich_orders['strike'] = pd.to_numeric(enrich_orders['strike'], errors='coerce')
        enrich_orders['ltp'] = pd.to_numeric(enrich_orders['ltp'], errors='coerce')
        enrich_orders['lots'] = pd.to_numeric(enrich_orders['lots'], errors='coerce').fillna(1)
        
        # Normalize underlying and side
        if 'underlying' in enrich_orders.columns:
            enrich_orders['underlying'] = enrich_orders['underlying'].astype(str).str.upper().str.strip()
        if 'side' not in enrich_orders.columns:
            enrich_orders['side'] = 'HOLD'
        enrich_orders['side'] = enrich_orders['side'].astype(str).str.upper().str.strip()
        
        print(f"\n[INPUT]")
        print(f"  Virtual orders: {len(enrich_orders)}")
        print(f"  Forward signals: {len(forward_df)}")
        
        # Initialize forward columns in orders
        forward_cols = [c for c in forward_df.columns if c.startswith('fwd_ret_')]
        for col in forward_cols:
            if col not in enrich_orders.columns:
                enrich_orders[col] = np.nan
        
        stage_results = {}
        total_matched = 0
        
        # STAGE 1: Exact match (ts, underlying, strike, side, expiry)
        print(f"\n[STAGE 1] Exact Match (ts, underlying, strike, side, expiry)")
        try:
            merge_keys = ['ts', 'underlying', 'strike', 'side', 'expiry']
            merge_keys = [k for k in merge_keys if k in enrich_orders.columns and k in forward_df.columns]
            
            if merge_keys:
                merged_s1 = enrich_orders.merge(
                    forward_df[merge_keys + forward_cols],
                    on=merge_keys,
                    how='left',
                    suffixes=('', '_match')
                )
                
                # Copy forward columns where they match
                matched_mask = merged_s1[forward_cols[0]].notna() & enrich_orders[forward_cols[0]].isna()
                stage1_matched = matched_mask.sum()
                
                for col in forward_cols:
                    enrich_orders.loc[matched_mask, col] = merged_s1.loc[matched_mask, col]
                
                total_matched += stage1_matched
                stage_results['exact'] = stage1_matched
                print(f"  Matched: {stage1_matched}")
            else:
                print(f"  Skipped (no matching keys)")
                stage_results['exact'] = 0
        except Exception as e:
            print(f"  [ERROR] {str(e)[:80]}")
            stage_results['exact'] = 0
        
        # STAGE 2: AsOf join (±2 seconds, grouped by underlying/strike/side)
        print(f"\n[STAGE 2] AsOf Join (±2 seconds, underlying/strike/side)")
        try:
            unmatched = enrich_orders[enrich_orders[forward_cols[0]].isna()].copy()
            if len(unmatched) > 0:
                unmatched_idx = unmatched.index
                
                # Drop rows with null ts for merge_asof (required)
                unmatched_valid = unmatched[unmatched['ts'].notna()].copy()
                if len(unmatched_valid) > 0:
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
                        
                        # Identify new matches (where forward columns now have values)
                        stage2_matched = 0
                        for idx, row in merged_s2.iterrows():
                            orig_idx = unmatched_idx[idx]
                            for col in forward_cols:
                                merge_col = col + '_match' if col + '_match' in merged_s2.columns else col
                                if pd.notna(merged_s2.loc[idx, merge_col]):
                                    enrich_orders.loc[orig_idx, col] = merged_s2.loc[idx, merge_col]
                                    stage2_matched += 1
                                    break  # Count each row only once
                        
                        total_matched += stage2_matched
                        stage_results['asof_2s'] = stage2_matched
                        print(f"  Matched: {stage2_matched}")
                    except Exception as e:
                        print(f"  [ERROR] {str(e)[:80]}")
                        stage_results['asof_2s'] = 0
            else:
                print(f"  Skipped (no unmatched rows)")
                stage_results['asof_2s'] = 0
        except Exception as e:
            print(f"  [ERROR] {str(e)[:80]}")
            stage_results['asof_2s'] = 0
        
        # STAGE 3: Date-only match (date + underlying + side)
        print(f"\n[STAGE 3] Date-Only Match (date + underlying + side)")
        try:
            unmatched = enrich_orders[enrich_orders[forward_cols[0]].isna()].copy()
            if len(unmatched) > 0:
                unmatched_idx = unmatched.index
                
                unmatched['date'] = unmatched['ts'].dt.date
                forward_sorted = forward_df.copy()
                forward_sorted['date'] = forward_sorted['ts'].dt.date
                
                date_keys = ['date', 'underlying', 'side']
                date_keys = [c for c in date_keys if (c == 'date' or c in unmatched.columns and c in forward_sorted.columns)]
                
                if date_keys:
                    merged_s3 = unmatched.merge(
                        forward_sorted[date_keys + forward_cols],
                        on=date_keys,
                        how='left',
                        suffixes=('', '_match')
                    )
                    
                    stage3_matched = 0
                    for idx, row in merged_s3.iterrows():
                        orig_idx = unmatched_idx[idx]
                        for col in forward_cols:
                            match_col = col + '_match' if col + '_match' in merged_s3.columns else col
                            if pd.notna(merged_s3.loc[idx, match_col]):
                                enrich_orders.loc[orig_idx, col] = merged_s3.loc[idx, match_col]
                                stage3_matched += 1
                                break
                    
                    total_matched += stage3_matched
                    stage_results['date_only'] = stage3_matched
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
        print(f"\n[STAGE 4] Nearest Timestamp Fallback (±5 seconds, underlying + side only)")
        try:
            unmatched = enrich_orders[enrich_orders[forward_cols[0]].isna()].copy()
            if len(unmatched) > 0:
                unmatched_idx = unmatched.index
                
                forward_sorted = forward_df.sort_values('ts').reset_index(drop=True)
                unmatched_sorted = unmatched.sort_values('ts').reset_index(drop=True)
                
                by_cols_s4 = ['underlying', 'side']
                by_cols_s4 = [c for c in by_cols_s4 if c in unmatched_sorted.columns and c in forward_sorted.columns]
                
                try:
                    if by_cols_s4:
                        merged_s4 = pd.merge_asof(
                            unmatched_sorted,
                            forward_sorted[by_cols_s4 + ['ts'] + forward_cols].sort_values('ts'),
                            on='ts',
                            by=by_cols_s4,
                            direction='nearest',
                            tolerance=pd.Timedelta(seconds=5),
                            suffixes=('', '_match')
                        )
                    else:
                        merged_s4 = pd.merge_asof(
                            unmatched_sorted,
                            forward_sorted[['ts'] + forward_cols].sort_values('ts'),
                            on='ts',
                            direction='nearest',
                            tolerance=pd.Timedelta(seconds=5),
                            suffixes=('', '_match')
                        )
                    
                    stage4_matched = 0
                    for idx, row in merged_s4.iterrows():
                        orig_idx = unmatched_idx[idx]
                        for col in forward_cols:
                            match_col = col + '_match' if col + '_match' in merged_s4.columns else col
                            if pd.notna(merged_s4.loc[idx, match_col]):
                                enrich_orders.loc[orig_idx, col] = merged_s4.loc[idx, match_col]
                                stage4_matched += 1
                                break
                    
                    total_matched += stage4_matched
                    stage_results['nearest'] = stage4_matched
                    print(f"  Matched: {stage4_matched}")
                except Exception as e:
                    print(f"  [ERROR] {str(e)[:80]}")
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
            enrich_orders[pnl_col] = (enrich_orders[col] * enrich_orders['lots']).round(6)
        
        # Final validation
        match_rate = 100 * total_matched / len(enrich_orders)
        has_fwd = enrich_orders[forward_cols[0]].notna().sum()
        
        print(f"\n[FINAL RESULTS]")
        print(f"  Total matched: {total_matched}")
        print(f"  Orders with forward returns: {has_fwd}")
        print(f"  Match rate: {match_rate:.1f}%")
        print(f"  Stage breakdown:")
        for stage, count in stage_results.items():
            print(f"    {stage}: {count}")
        
        # Save Phase 239 output
        enrich_orders.to_csv(PHASE239_OUTPUT, index=False, encoding='utf-8')
        print(f"\n[OUTPUT] Saved to: {PHASE239_OUTPUT}")
        
        # Create validation JSON
        validation = {
            "timestamp": datetime.now().isoformat(),
            "total_orders": len(enrich_orders),
            "matched": has_fwd,
            "match_rate_pct": match_rate,
            "stage_breakdown": stage_results,
            "forward_columns": forward_cols,
        }
        
        with open(STORAGE_LIVE / "meta" / "PHASE239_FINAL_VALIDATION.json", 'w') as f:
            json.dump(validation, f, indent=2)
        
    else:
        print("[WARNING] No forward returns from Phase 221")

except Exception as e:
    print(f"[ERROR] Phase 239 failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
print("MASTER PIPELINE REPAIR COMPLETE")
print(f"{'='*80}\n")
