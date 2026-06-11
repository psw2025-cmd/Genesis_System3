"""
System3 Production Pipeline Orchestrator
Integrates Phases 220 → 221 → 239 into Autorun Cycle

This module orchestrates the complete PnL enrichment pipeline:
- Phase 220: Historical signal aggregation (multi-day)
- Phase 221: Forward returns computation (5 horizons)
- Phase 239: PnL enrichment (4-stage bulletproof join)

Designed for:
- Every market cycle (every 30 minutes)
- Before OP2 execution
- With self-healing BEFORE Phase 239
- With performance monitoring (< 2s, < 2s, < 3s targets)
- With automatic validation reports
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import json
import logging
import time
from typing import Dict, Any, Tuple, Optional

from core.utils.timestamp_parser import parse_system3_timestamp

# Setup logging
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.absolute()
STORAGE_LIVE = ROOT_DIR / "storage" / "live"
HEALED_DIR = STORAGE_LIVE / "healed"
FORWARD_DIR = STORAGE_LIVE / "forward"
ENRICHED_DIR = STORAGE_LIVE / "enriched"
META_DIR = STORAGE_LIVE / "meta"
ARCHIVE_DIR = ROOT_DIR / "storage" / "live" / "archive"
REPORTS_DIR = ROOT_DIR / "runtime_reports"
METRICS_DIR = ROOT_DIR / "storage" / "metrics"

# Ensure directories exist
for dir_path in [HEALED_DIR, FORWARD_DIR, ENRICHED_DIR, META_DIR, REPORTS_DIR, METRICS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Performance thresholds (seconds)
PHASE_220_TARGET = 2.0
PHASE_221_TARGET = 2.0
PHASE_239_TARGET = 3.0


def normalize_timestamps(df: pd.DataFrame, column: str = "ts", label: Optional[str] = None) -> pd.DataFrame:
    """Normalize timestamps with canonical parser and metrics."""
    fallback_series = None
    if column not in df.columns and "timestamp" in df.columns:
        df = df.copy()
        df[column] = df["timestamp"]
    
    if column not in df.columns:
        return df

    df = df.copy()
    fallback_series = df["timestamp"] if "timestamp" in df.columns else None
    metrics_label = label or f"pipeline_{column}"
    metrics_path = METRICS_DIR / f"{metrics_label}_metrics.json"
    df[column] = parse_system3_timestamp(
        df[column], name=metrics_label, metrics_path=metrics_path, allow_fallback=fallback_series
    )
    return df


class ProductionPipelineOrchestrator:
    """Orchestrates the complete Phase 220-221-239 pipeline."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.execution_report = {
            "timestamp": datetime.now().isoformat(),
            "phases_executed": [],
            "timings": {},
            "warnings": [],
            "errors": [],
            "statistics": {},
            "performance_alerts": []
        }
    
    def log(self, level: str, message: str):
        """Unified logging with report capture."""
        if level == "info":
            logger.info(message)
        elif level == "warning":
            logger.warning(message)
            self.execution_report["warnings"].append(message)
        elif level == "error":
            logger.error(message)
            self.execution_report["errors"].append(message)
    
    def check_performance(self, phase: str, duration: float, target: float):
        """Check if phase execution meets performance target."""
        self.execution_report["timings"][phase] = duration

        if duration > target:
            alert = f"⚠️ {phase} took {duration:.2f}s (target: {target:.2f}s)"
            self.execution_report["performance_alerts"].append(alert)
            self.log("warning", alert)
        else:
            self.log("info", f"✓ {phase} completed in {duration:.2f}s (within {target:.2f}s target)")
    
    def run_phase_220(self) -> Tuple[bool, str]:
        """
        Phase 220: Historical Signal Aggregation (Multi-Day)
        
        Inputs: storage/live/archive/*.csv (multiple days)
        Output: storage/live/forward/phase220_aggregated_signals.csv
        Target: < 2 seconds
        """
        self.log("info", "=" * 70)
        self.log("info", "PHASE 220: HISTORICAL SIGNAL AGGREGATION")
        self.log("info", "=" * 70)
        
        start_time = time.time()
        
        try:
            # Find all archive signal files
            archive_files = sorted(ARCHIVE_DIR.glob("angel_index_ai_signals_*.csv"))
            
            if not archive_files:
                self.log("warning", "No archive signal files found")
                return False, ""
            
            self.log("info", f"Found {len(archive_files)} archive files")
            
            # Load and concatenate all files
            dfs = []
            for file_path in archive_files:
                try:
                    df = pd.read_csv(file_path)
                    df = normalize_timestamps(df, "ts", label=f"phase220_archive_{file_path.stem}")
                    dfs.append(df)
                except Exception as e:
                    self.log("warning", f"Failed to load {file_path.name}: {e}")
            
            if not dfs:
                self.log("error", "No archive files could be loaded")
                return False, ""
            
            # Concatenate all dataframes
            df_all = pd.concat(dfs, ignore_index=True)
            before_count = len(df_all)
            
            self.log("info", f"Loaded {before_count} total rows from {len(dfs)} files")
            
            # Remove duplicates
            df_all = df_all.drop_duplicates(subset=["ts", "underlying", "strike", "side"], keep="first")
            after_dedup = len(df_all)
            dedup_count = before_count - after_dedup
            
            self.log("info", f"Removed {dedup_count} duplicates ({dedup_count/before_count*100:.1f}%)")
            
            # Drop rows with NULL timestamps (critical for join)
            df_all = df_all.dropna(subset=["ts"])
            after_clean = len(df_all)
            dropped_count = after_dedup - after_clean
            
            if dropped_count > 0:
                self.log("warning", f"Dropped {dropped_count} rows with NULL timestamps")
            
            # Sort by timestamp
            df_all = df_all.sort_values("ts").reset_index(drop=True)
            
            # Get unique dates
            df_all["date"] = pd.to_datetime(df_all["ts"]).dt.date
            unique_dates = df_all["date"].nunique()
            
            # Save output
            output_path = FORWARD_DIR / "phase220_aggregated_signals.csv"
            df_all.to_csv(output_path, index=False)
            
            duration = time.time() - start_time
            
            self.log("info", f"✓ Phase 220 complete: {output_path}")
            self.log("info", f"  Output: {after_clean} rows across {unique_dates} unique dates")
            self.log("info", f"  Duration: {duration:.2f}s")
            
            # Store statistics (convert numpy types to native Python)
            self.execution_report["statistics"]["phase220"] = {
                "input_files": int(len(archive_files)),
                "input_rows": int(before_count),
                "duplicates_removed": int(dedup_count),
                "null_timestamps_dropped": int(dropped_count),
                "output_rows": int(after_clean),
                "unique_dates": int(unique_dates),
                "dedup_rate": float(dedup_count / before_count if before_count > 0 else 0)
            }
            
            self.check_performance("Phase 220", duration, PHASE_220_TARGET)
            self.execution_report["phases_executed"].append("Phase 220")
            
            return True, str(output_path)
        
        except Exception as e:
            self.log("error", f"Phase 220 failed: {e}")
            import traceback
            self.log("error", traceback.format_exc())
            return False, ""
    
    def run_phase_221(self, input_path: str) -> Tuple[bool, str]:
        """
        Phase 221: Forward Returns Computation
        
        Inputs: Phase 220 output (aggregated signals)
        Output: storage/live/forward/phase221_forward_returns.csv
        Target: < 2 seconds
        Horizons: 1, 2, 5, 10, 15 periods
        """
        self.log("info", "=" * 70)
        self.log("info", "PHASE 221: FORWARD RETURNS COMPUTATION")
        self.log("info", "=" * 70)
        
        start_time = time.time()
        
        try:
            # Load Phase 220 output
            df = pd.read_csv(input_path)
            df = normalize_timestamps(df, "ts", label="phase221_input_ts")
            
            self.log("info", f"Loaded {len(df)} rows from Phase 220")
            
            # Compute forward returns for 5 horizons
            horizons = [1, 2, 5, 10, 15]
            
            for horizon in horizons:
                col_name = f"fwd_ret_{horizon}"
                
                # Compute forward return: (price[t+h] - price[t]) / price[t]
                # Assuming 'ltp' column exists
                if "ltp" in df.columns:
                    df[col_name] = df.groupby(["underlying", "strike", "side"])["ltp"].shift(-horizon)
                    df[col_name] = (df[col_name] - df["ltp"]) / df["ltp"].replace(0, np.nan)
                else:
                    # No price data, fill with 0
                    df[col_name] = 0.0
            
            # Calculate coverage statistics
            coverage_stats = {}
            for horizon in horizons:
                col_name = f"fwd_ret_{horizon}"
                valid_count = df[col_name].notna().sum()
                coverage_pct = valid_count / len(df) * 100 if len(df) > 0 else 0
                coverage_stats[f"H{horizon}"] = {
                    "valid": valid_count,
                    "coverage": coverage_pct
                }
                self.log("info", f"  {col_name}: {valid_count}/{len(df)} ({coverage_pct:.1f}%)")
            
            # Fill NaN with 0 (for rows without sufficient future data)
            for horizon in horizons:
                col = f"fwd_ret_{horizon}"
                df[col] = df[col].fillna(0.0)
            
            # Save output
            output_path = FORWARD_DIR / "phase221_forward_returns.csv"
            df.to_csv(output_path, index=False)
            
            duration = time.time() - start_time
            
            avg_coverage = np.mean([s["coverage"] for s in coverage_stats.values()])
            
            self.log("info", f"✓ Phase 221 complete: {output_path}")
            self.log("info", f"  Output: {len(df)} rows with {len(horizons)} horizons")
            self.log("info", f"  Average coverage: {avg_coverage:.1f}%")
            self.log("info", f"  Duration: {duration:.2f}s")
            
            # Store statistics (convert numpy types to native Python)
            coverage_stats_clean = {}
            for k, v in coverage_stats.items():
                coverage_stats_clean[k] = {
                    "valid": int(v["valid"]),
                    "coverage": float(v["coverage"])
                }
            
            self.execution_report["statistics"]["phase221"] = {
                "input_rows": int(len(df)),
                "horizons": horizons,
                "coverage_stats": coverage_stats_clean,
                "avg_coverage": float(avg_coverage)
            }
            
            self.check_performance("Phase 221", duration, PHASE_221_TARGET)
            self.execution_report["phases_executed"].append("Phase 221")
            
            return True, str(output_path)
        
        except Exception as e:
            self.log("error", f"Phase 221 failed: {e}")
            import traceback
            self.log("error", traceback.format_exc())
            return False, ""
    
    def run_phase_239(self, signals_path: str, orders_path: str) -> Tuple[bool, str]:
        """
        Phase 239: PnL Enrichment (4-Stage Bulletproof Join)
        
        Inputs:
          - Phase 221 output (signals with forward returns)
          - Healed virtual orders
        Output: storage/live/enriched/angel_virtual_orders_with_pnl.csv
        Target: < 3 seconds
        
        4-Stage Join Strategy:
          1. Exact match (5 keys: ts, underlying, strike, side, expiry)
          2. AsOf join (±2 seconds tolerance)
          3. Date-only match (date, underlying, side)
          4. Nearest timestamp (±5 seconds)
        """
        self.log("info", "=" * 70)
        self.log("info", "PHASE 239: PNL ENRICHMENT (4-STAGE JOIN)")
        self.log("info", "=" * 70)
        
        start_time = time.time()
        
        try:
            # First, apply merge key normalization
            try:
                from core.engine.merge_key_normalizer import normalize_signals, normalize_orders
                
                # Load signals (Phase 221 output)
                signals = pd.read_csv(signals_path)
                signals, _ = normalize_signals(signals)
                
                # Load virtual orders (healed)
                orders = pd.read_csv(orders_path)
                orders, _ = normalize_orders(orders)
                
                self.log("info", f"Applied merge key normalization to {len(signals)} signals and {len(orders)} orders")
            except Exception as e:
                self.log("warning", f"Failed to apply normalization: {e} — falling back to raw data")
                # Fallback if normalizer not available
                signals = pd.read_csv(signals_path)
                signals = normalize_timestamps(signals, "ts", label="phase239_signals_ts")
                
                orders = pd.read_csv(orders_path)
                orders = normalize_timestamps(orders, "ts", label="phase239_orders_ts")
                
                self.log("info", f"Loaded {len(signals)} signals and {len(orders)} orders")
            
            # Validate merge keys
            merge_keys = ["ts", "underlying", "strike", "side", "expiry"]
            missing_signal_keys = [k for k in merge_keys if k not in signals.columns]
            missing_order_keys = [k for k in merge_keys if k not in orders.columns]
            
            if missing_signal_keys:
                self.log("error", f"Signals missing merge keys: {missing_signal_keys}")
                return False, ""
            if missing_order_keys:
                self.log("error", f"Orders missing merge keys: {missing_order_keys}")
                return False, ""
            
            # Drop rows with NULL merge keys (explicit accounting)
            sig_null = int(signals[merge_keys].isna().any(axis=1).sum())
            ord_null = int(orders[merge_keys].isna().any(axis=1).sum())
            if sig_null:
                self.log("warning", f"Phase 239: Dropping {sig_null} signal rows with null merge keys")
            if ord_null:
                self.log("warning", f"Phase 239: Dropping {ord_null} order rows with null merge keys")
            signals = signals.dropna(subset=merge_keys)
            orders = orders.dropna(subset=merge_keys)

            self.log("info", f"After validation: {len(signals)} signals, {len(orders)} orders")
            
            # Preserve original order index  
            orders["_orig_idx"] = orders.index
            
            # Initialize match tracking
            unmatched_orders = orders.copy()
            all_matches = []
            stage_stats = {}
            
            # STAGE 1: Exact match (5 keys)
            self.log("info", "Stage 1: Exact match on 5 keys...")
            stage1_start = time.time()
            
            matched = pd.merge(
                unmatched_orders,
                signals,
                on=merge_keys,
                how="inner",
                suffixes=("", "_signal")
            )
            
            stage1_count = len(matched)
            all_matches.append(matched)
            
            if stage1_count > 0:
                matched_indices = matched["_orig_idx"].unique()
                unmatched_orders = unmatched_orders[~unmatched_orders["_orig_idx"].isin(matched_indices)]
            
            stage1_duration = time.time() - stage1_start
            stage_stats["stage1_exact"] = {"matches": stage1_count, "duration": stage1_duration}
            self.log("info", f"  Stage 1: {stage1_count} matches in {stage1_duration:.2f}s")
            
            # STAGE 2: AsOf join (±2 seconds)
            if len(unmatched_orders) > 0:
                self.log("info", f"Stage 2: AsOf join (±2s) for {len(unmatched_orders)} remaining orders...")
                stage2_start = time.time()
                
                # Sort by timestamp
                unmatched_sorted = unmatched_orders.sort_values("ts").reset_index(drop=True)
                signals_sorted = signals.sort_values("ts").reset_index(drop=True)
                
                # AsOf merge with tolerance
                matched = pd.merge_asof(
                    unmatched_sorted,
                    signals_sorted,
                    on="ts",
                    by=["underlying", "strike", "side", "expiry"],
                    direction="nearest",
                    tolerance=pd.Timedelta(seconds=2)
                )
                
                # Filter out NaN joins
                matched = matched.dropna(subset=["fwd_ret_1"])  # Check if signal data exists
                
                stage2_count = len(matched)
                all_matches.append(matched)
                
                if stage2_count > 0:
                    matched_indices = matched["_orig_idx"].unique()
                    unmatched_orders = unmatched_orders[~unmatched_orders["_orig_idx"].isin(matched_indices)]
                
                stage2_duration = time.time() - stage2_start
                stage_stats["stage2_asof"] = {"matches": stage2_count, "duration": stage2_duration}
                self.log("info", f"  Stage 2: {stage2_count} matches in {stage2_duration:.2f}s")
            else:
                stage_stats["stage2_asof"] = {"matches": 0, "duration": 0}
            
            # STAGE 3: Date-only match
            if len(unmatched_orders) > 0:
                self.log("info", f"Stage 3: Date-only match for {len(unmatched_orders)} remaining orders...")
                stage3_start = time.time()
                
                # Extract date
                unmatched_orders["date"] = pd.to_datetime(unmatched_orders["ts"]).dt.date
                signals["date"] = pd.to_datetime(signals["ts"]).dt.date
                
                matched = pd.merge(
                    unmatched_orders,
                    signals,
                    on=["date", "underlying", "side"],
                    how="inner",
                    suffixes=("", "_signal")
                )
                
                stage3_count = len(matched)
                all_matches.append(matched)
                
                if stage3_count > 0:
                    matched_indices = matched["_orig_idx"].unique()
                    unmatched_orders = unmatched_orders[~unmatched_orders["_orig_idx"].isin(matched_indices)]
                
                stage3_duration = time.time() - stage3_start
                stage_stats["stage3_date"] = {"matches": stage3_count, "duration": stage3_duration}
                self.log("info", f"  Stage 3: {stage3_count} matches in {stage3_duration:.2f}s")
            else:
                stage_stats["stage3_date"] = {"matches": 0, "duration": 0}
            
            # STAGE 4: Nearest timestamp (±5 seconds)
            if len(unmatched_orders) > 0:
                self.log("info", f"Stage 4: Nearest timestamp (±5s) for {len(unmatched_orders)} remaining orders...")
                stage4_start = time.time()
                
                unmatched_sorted = unmatched_orders.sort_values("ts").reset_index(drop=True)
                signals_sorted = signals.sort_values("ts").reset_index(drop=True)
                
                matched = pd.merge_asof(
                    unmatched_sorted,
                    signals_sorted,
                    on="ts",
                    by=["underlying", "side"],
                    direction="nearest",
                    tolerance=pd.Timedelta(seconds=5)
                )
                
                matched = matched.dropna(subset=["fwd_ret_1"])
                
                stage4_count = len(matched)
                all_matches.append(matched)
                
                stage4_duration = time.time() - stage4_start
                stage_stats["stage4_nearest"] = {"matches": stage4_count, "duration": stage4_duration}
                self.log("info", f"  Stage 4: {stage4_count} matches in {stage4_duration:.2f}s")
            else:
                stage_stats["stage4_nearest"] = {"matches": 0, "duration": 0}
            
            # Combine all matches
            if all_matches:
                df_enriched = pd.concat(all_matches, ignore_index=True)
                df_enriched = df_enriched.drop_duplicates(subset=["_orig_idx"], keep="first")
            else:
                df_enriched = pd.DataFrame()
            
            total_matches = sum(s["matches"] for s in stage_stats.values())
            unique_enriched = len(df_enriched)
            enrichment_rate = unique_enriched / len(orders) * 100 if len(orders) > 0 else 0
            
            self.log("info", f"✓ Total matches: {total_matches}, Unique enriched orders: {unique_enriched}")
            self.log("info", f"  Enrichment rate: {enrichment_rate:.1f}%")
            
            # Compute PnL for all horizons
            horizons = [1, 2, 5, 10, 15]
            for horizon in horizons:
                fwd_ret_col = f"fwd_ret_{horizon}"
                pnl_col = f"pnl_{horizon}"
                
                if fwd_ret_col in df_enriched.columns and "quantity" in df_enriched.columns:
                    # Convert to numeric
                    df_enriched[fwd_ret_col] = pd.to_numeric(df_enriched[fwd_ret_col], errors='coerce')
                    df_enriched["quantity"] = pd.to_numeric(df_enriched["quantity"], errors='coerce')
                    
                    # PnL = forward_return * quantity * ltp
                    if "ltp" in df_enriched.columns:
                        df_enriched["ltp"] = pd.to_numeric(df_enriched["ltp"], errors='coerce')
                        df_enriched[pnl_col] = df_enriched[fwd_ret_col] * df_enriched["quantity"] * df_enriched["ltp"]
                    else:
                        df_enriched[pnl_col] = df_enriched[fwd_ret_col] * df_enriched["quantity"]

                    df_enriched[pnl_col] = df_enriched[pnl_col].fillna(0.0)
            
            # Restore original order (merge back with all orders)
            df_final = orders.merge(
                df_enriched[[col for col in df_enriched.columns if col.startswith("pnl_") or col.startswith("fwd_ret_")] + ["_orig_idx"]],
                left_index=True,
                right_on="_orig_idx",
                how="left"
            )
            
            # Fill NaN PnL with 0
            for horizon in horizons:
                pnl_col = f"pnl_{horizon}"
                fwd_ret_col = f"fwd_ret_{horizon}"
                if pnl_col in df_final.columns:
                    df_final[pnl_col] = df_final[pnl_col].fillna(0.0)
                if fwd_ret_col in df_final.columns:
                    df_final[fwd_ret_col] = df_final[fwd_ret_col].fillna(0.0)
            
            # Drop helper column
            if "_orig_idx" in df_final.columns:
                df_final = df_final.drop(columns=["_orig_idx"])
            
            # Save output
            output_path = ENRICHED_DIR / "angel_virtual_orders_with_pnl.csv"
            df_final.to_csv(output_path, index=False)
            
            duration = time.time() - start_time
            
            self.log("info", f"✓ Phase 239 complete: {output_path}")
            self.log("info", f"  Output: {len(df_final)} rows with {len(horizons)} PnL columns")
            self.log("info", f"  Duration: {duration:.2f}s")
            
            # Store statistics (convert numpy types to native Python)
            stage_stats_clean = {}
            for k, v in stage_stats.items():
                stage_stats_clean[k] = {
                    "matches": int(v["matches"]),
                    "duration": float(v["duration"])
                }
            
            self.execution_report["statistics"]["phase239"] = {
                "input_signals": int(len(signals)),
                "input_orders": int(len(orders)),
                "total_matches": int(total_matches),
                "unique_enriched": int(unique_enriched),
                "enrichment_rate": float(enrichment_rate),
                "stage_breakdown": stage_stats_clean,
                "output_rows": int(len(df_final))
            }
            
            self.check_performance("Phase 239", duration, PHASE_239_TARGET)
            self.execution_report["phases_executed"].append("Phase 239")
            
            return True, str(output_path)
        
        except Exception as e:
            self.log("error", f"Phase 239 failed: {e}")
            import traceback
            self.log("error", traceback.format_exc())
            return False, ""
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Run complete Phase 220 → 221 → 239 pipeline.
        
        Returns: Execution report with all metrics and statistics
        """
        self.log("info", "=" * 70)
        self.log("info", "PRODUCTION PIPELINE ORCHESTRATOR - STARTING")
        self.log("info", "=" * 70)
        
        overall_start = time.time()
        
        # Run self-healing first
        self.log("info", "Running self-healing before pipeline execution...")
        try:
            from system3_self_healing import run_self_healing
            healing_report = run_self_healing(verbose=self.verbose)
            self.execution_report["self_healing"] = {
                "repairs_applied": len(healing_report.get("repairs_applied", [])),
                "warnings": len(healing_report.get("warnings", [])),
                "errors": len(healing_report.get("errors", []))
            }
        except Exception as e:
            self.log("warning", f"Self-healing failed: {e}")
        
        # Phase 220: Aggregation
        phase220_success, phase220_output = self.run_phase_220()
        if not phase220_success:
            self.log("error", "Pipeline failed at Phase 220")
            return self.execution_report
        
        # Phase 221: Forward Returns
        phase221_success, phase221_output = self.run_phase_221(phase220_output)
        if not phase221_success:
            self.log("error", "Pipeline failed at Phase 221")
            return self.execution_report
        
        # Phase 239: PnL Enrichment
        orders_path = HEALED_DIR / "angel_virtual_orders_healed.csv"
        if not orders_path.exists():
            self.log("error", f"Virtual orders not found at {orders_path}")
            return self.execution_report
        
        phase239_success, phase239_output = self.run_phase_239(phase221_output, str(orders_path))
        if not phase239_success:
            self.log("error", "Pipeline failed at Phase 239")
            return self.execution_report
        
        # Calculate total duration
        total_duration = time.time() - overall_start
        self.execution_report["total_duration_seconds"] = total_duration
        
        # Save execution report
        report_path = META_DIR / f"pipeline_execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            json.dump(self.execution_report, f, indent=2)
        
        # Generate runtime validation reports
        self.log("info", "=" * 70)
        self.log("info", "GENERATING RUNTIME VALIDATION REPORTS")
        self.log("info", "=" * 70)
        
        try:
            from system3_runtime_reports import generate_runtime_reports
            validation_reports = generate_runtime_reports()
            self.execution_report["validation_reports_generated"] = validation_reports
            self.log("info", f"✓ Generated {len(validation_reports)} validation reports")
        except Exception as e:
            self.log("warning", f"Failed to generate validation reports: {e}")
        
        self.log("info", "=" * 70)
        self.log("info", f"PIPELINE COMPLETE in {total_duration:.2f}s")
        self.log("info", f"Report saved: {report_path}")
        self.log("info", f"Phases executed: {', '.join(self.execution_report['phases_executed'])}")
        self.log("info", f"Performance alerts: {len(self.execution_report['performance_alerts'])}")
        self.log("info", f"Warnings: {len(self.execution_report['warnings'])}")
        self.log("info", f"Errors: {len(self.execution_report['errors'])}")
        self.log("info", "=" * 70)
        
        return self.execution_report


def run_production_pipeline(verbose: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run complete pipeline.
    
    Usage:
        from system3_production_pipeline import run_production_pipeline
        report = run_production_pipeline()
        if report["errors"]:
            print("Pipeline had errors!")
    """
    orchestrator = ProductionPipelineOrchestrator(verbose=verbose)
    return orchestrator.run_full_pipeline()


if __name__ == "__main__":
    # Run pipeline when executed directly
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    
    report = run_production_pipeline(verbose=True)
    
    # Exit with error code if errors occurred
    if report["errors"]:
        sys.exit(1)
    else:
        sys.exit(0)
