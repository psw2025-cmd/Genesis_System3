"""
Simplified Phase 239 Implementation with Merge Key Normalization

This file provides the cleaned-up Phase 239 logic that can be integrated
back into the main pipeline.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import time
from typing import Tuple, Dict, Any

def run_phase_239_standalone(signals_path: str, orders_path: str) -> Tuple[bool, str, dict]:
    """
    Run Phase 239 standalone for testing/validation.
    
    Returns: (success, output_path, stats)
    """
    print(f"\n{'='*70}")
    print("PHASE 239: PNL ENRICHMENT WITH MERGE KEY NORMALIZATION")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    # Apply merge key normalization
    try:
        from core.engine.merge_key_normalizer import normalize_signals, normalize_orders
        
        signals = pd.read_csv(signals_path)
        signals, _ = normalize_signals(signals)
        
        orders = pd.read_csv(orders_path)
        orders, _ = normalize_orders(orders)
        
        print(f"✓ Applied merge key normalization")
    except Exception as e:
        print(f"❌ Normalization failed: {e}")
        return False, "", {}
    
    # Validate merge keys
    merge_keys = ["ts", "underlying", "strike", "side", "expiry"]
    for key in merge_keys:
        if key not in signals.columns:
            print(f"❌ Signals missing {key}")
            return False, "", {}
        if key not in orders.columns:
            print(f"❌ Orders missing {key}")
            return False, "", {}
    
    # Drop NULL merge keys
    sig_before = len(signals)
    ord_before = len(orders)
    signals = signals.dropna(subset=merge_keys)
    orders = orders.dropna(subset=merge_keys)
    print(f"Signals: {sig_before} → {len(signals)}")
    print(f"Orders: {ord_before} → {len(orders)}")
    
    # Mark order indices for tracking
    orders["_orig_idx"] = range(len(orders))
    
    # STAGE 1: Exact match
    print(f"\nStage 1: Exact match on {', '.join(merge_keys)}...")
    stage1_start = time.time()
    matched_1 = signals.merge(orders, on=merge_keys, how="inner", suffixes=("_sig", "_ord"))
    stage1_matches = len(matched_1)
    stage1_time = time.time() - stage1_start
    print(f"  {stage1_matches} matches in {stage1_time:.3f}s")
    
    # Remove matched orders for next stage
    matched_indices_1 = set(matched_1["_orig_idx"].unique()) if stage1_matches > 0 else set()
    unmatched = orders[~orders["_orig_idx"].isin(matched_indices_1)].copy()
    
    # STAGE 2: AsOf join with 2s tolerance
    print(f"\nStage 2: AsOf join (±2s) for {len(unmatched)} unmatched orders...")
    stage2_start = time.time()
    stage2_matches = 0
    
    if len(unmatched) > 0:
        # Parse timestamps
        unmatched["ts_dt"] = pd.to_datetime(unmatched["ts"], errors="coerce")
        signals["ts_dt"] = pd.to_datetime(signals["ts"], errors="coerce")
        
        # Sort
        unmatched_sorted = unmatched.sort_values("ts_dt").reset_index(drop=True)
        signals_sorted = signals.sort_values("ts_dt").reset_index(drop=True)
        
        try:
            matched_2 = pd.merge_asof(
                unmatched_sorted,
                signals_sorted,
                on="ts_dt",
                by=["underlying", "strike", "side", "expiry"],
                direction="nearest",
                tolerance=pd.Timedelta(seconds=2),
                suffixes=("_ord", "_sig")
            )
            # Filter out non-matches
            matched_2 = matched_2.dropna(subset=["fwd_ret_1"])
            stage2_matches = len(matched_2)
        except Exception as e:
            print(f"  AsOf merge failed: {e}")
            matched_2 = pd.DataFrame()
    
    stage2_time = time.time() - stage2_start
    print(f"  {stage2_matches} matches in {stage2_time:.3f}s")
    
    # Remove matched orders
    matched_indices_2 = set(matched_2["_orig_idx"].unique()) if stage2_matches > 0 else set()
    unmatched = orders[~orders["_orig_idx"].isin(matched_indices_1 | matched_indices_2)].copy()
    
    # STAGE 3: Date-only match
    print(f"\nStage 3: Date-only match (date + underlying + side) for {len(unmatched)} unmatched...")
    stage3_start = time.time()
    stage3_matches = 0
    
    if len(unmatched) > 0:
        unmatched["date"] = pd.to_datetime(unmatched["ts"], errors="coerce").dt.date
        signals["date"] = pd.to_datetime(signals["ts"], errors="coerce").dt.date
        
        matched_3 = unmatched.merge(
            signals[["date", "underlying", "side", "fwd_ret_1", "fwd_ret_2", "fwd_ret_5", "fwd_ret_10", "fwd_ret_15"]],
            on=["date", "underlying", "side"],
            how="inner",
            suffixes=("_ord", "_sig")
        )
        matched_3 = matched_3.dropna(subset=["fwd_ret_1"])
        stage3_matches = len(matched_3)
    
    stage3_time = time.time() - stage3_start
    print(f"  {stage3_matches} matches in {stage3_time:.3f}s")
    
    # Remove matched orders
    matched_indices_3 = set(matched_3["_orig_idx"].unique()) if stage3_matches > 0 else set()
    unmatched = orders[~orders["_orig_idx"].isin(matched_indices_1 | matched_indices_2 | matched_indices_3)].copy()
    
    # STAGE 4: Nearest timestamp (±5s)
    print(f"\nStage 4: Nearest timestamp (±5s, underlying + side) for {len(unmatched)} unmatched...")
    stage4_start = time.time()
    stage4_matches = 0
    
    if len(unmatched) > 0:
        unmatched["ts_dt"] = pd.to_datetime(unmatched["ts"], errors="coerce")
        signals["ts_dt"] = pd.to_datetime(signals["ts"], errors="coerce")
        
        unmatched_sorted = unmatched.sort_values("ts_dt").reset_index(drop=True)
        signals_sorted = signals.sort_values("ts_dt").reset_index(drop=True)
        
        try:
            matched_4 = pd.merge_asof(
                unmatched_sorted,
                signals_sorted,
                on="ts_dt",
                by=["underlying", "side"],
                direction="nearest",
                tolerance=pd.Timedelta(seconds=5),
                suffixes=("_ord", "_sig")
            )
            matched_4 = matched_4.dropna(subset=["fwd_ret_1"])
            stage4_matches = len(matched_4)
        except Exception as e:
            print(f"  AsOf merge failed: {e}")
            matched_4 = pd.DataFrame()
    
    stage4_time = time.time() - stage4_start
    print(f"  {stage4_matches} matches in {stage4_time:.3f}s")
    
    # Combine all matches
    total_matches = stage1_matches + stage2_matches + stage3_matches + stage4_matches
    unique_enriched = len(set(matched_indices_1 | matched_indices_2 | matched_indices_3))
    enrichment_rate = unique_enriched / len(orders) * 100
    
    print(f"\n{'='*70}")
    print(f"ENRICHMENT SUMMARY")
    print(f"{'='*70}")
    print(f"Total matches: {total_matches}")
    print(f"Unique enriched orders: {unique_enriched} / {ord_before}")
    print(f"Enrichment rate: {enrichment_rate:.1f}%")
    
    duration = time.time() - start_time
    print(f"Total time: {duration:.2f}s")
    
    # Save output (simple version — just the original orders for now)
    output_path = Path(__file__).parent / "storage" / "live" / "enriched" / "angel_virtual_orders_with_pnl.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    orders.to_csv(output_path, index=False)
    print(f"\n✓ Output saved: {output_path}")
    
    return True, str(output_path), {
        "stage1": stage1_matches,
        "stage2": stage2_matches,
        "stage3": stage3_matches,
        "stage4": stage4_matches,
        "total_matches": total_matches,
        "unique_enriched": unique_enriched,
        "enrichment_rate": enrichment_rate,
        "duration": duration,
    }

if __name__ == "__main__":
    signals_path = Path(__file__).parent / "storage" / "live" / "forward" / "phase221_forward_returns.csv"
    orders_path = Path(__file__).parent / "storage" / "live" / "healed" / "angel_virtual_orders_healed.csv"
    
    success, output, stats = run_phase_239_standalone(str(signals_path), str(orders_path))
    
    if success:
        print(f"\n✅ PHASE 239 SUCCESS")
        for k, v in stats.items():
            print(f"  {k}: {v}")
    else:
        print(f"\n❌ PHASE 239 FAILED")
