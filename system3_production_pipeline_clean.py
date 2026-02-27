"""
System3 Production Pipeline Orchestrator (CLEAN VERSION)
Phases 220 → 221 → 239 with merge key normalization

This is a clean, working version that integrates the tested Phase 239
normalization logic.
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

# Add canonical normalization imports
from core.utils.timestamp_parser import normalize_timestamp_column_strict
from core.engine.merge_key_normalizer import normalize_signals, normalize_orders

# Add continuous validators
from core.monitoring.continuous_validators import TimestampValidator, MergeKeyValidator, VenvLockMode

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

# Performance targets (seconds)
PHASE_220_TARGET = 2.0
PHASE_221_TARGET = 2.0
PHASE_239_TARGET = 3.0


class ProductionPipelineOrchestrator:
    """Orchestrates Phase 220-221-239 pipeline with merge key normalization."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.execution_report = {
            "timestamp": datetime.now().isoformat(),
            "phases_executed": [],
            "timings": {},
            "warnings": [],
            "errors": [],
            "statistics": {},
            "performance_alerts": [],
            "validation_results": {}
        }

        # Initialize continuous validators
        self.timestamp_validator = TimestampValidator()
        self.merge_key_validator = MergeKeyValidator()
        self.venv_lock = VenvLockMode()
    
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
        """Phase 220: Historical Signal Aggregation."""
        self.log("info", "=" * 70)
        self.log("info", "PHASE 220: HISTORICAL SIGNAL AGGREGATION")
        self.log("info", "=" * 70)
        
        start_time = time.time()
        
        try:
            archive_files = sorted(ARCHIVE_DIR.glob("angel_index_ai_signals_*.csv"))
            
            if not archive_files:
                self.log("warning", "No archive signal files found")
                return False, ""
            
            self.log("info", f"Found {len(archive_files)} archive files")
            
            dfs = []
            for file_path in archive_files:
                try:
                    df = pd.read_csv(file_path)
                    # Use canonical timestamp normalization
                    df, _ = normalize_timestamp_column_strict(
                        df,
                        col_name="ts",
                        fallback_col="timestamp",
                        metrics_path=METRICS_DIR / "phase220_ts_metrics.json",
                        name="phase220_aggregation",
                    )
                    dfs.append(df)
                except Exception as e:
                    self.log("warning", f"Failed to load {file_path.name}: {e}")
            
            if not dfs:
                self.log("error", "No archive files could be loaded")
                return False, ""
            
            df_all = pd.concat(dfs, ignore_index=True)
            before_count = len(df_all)
            
            self.log("info", f"Loaded {before_count} total rows from {len(dfs)} files")
            
            df_all = df_all.drop_duplicates(subset=["ts", "underlying", "strike", "side"], keep="first")
            after_dedup = len(df_all)
            dedup_count = before_count - after_dedup
            
            self.log("info", f"Removed {dedup_count} duplicates ({dedup_count/before_count*100:.1f}%)")
            
            df_all = df_all.dropna(subset=["ts"])
            after_clean = len(df_all)
            dropped_count = after_dedup - after_clean
            
            if dropped_count > 0:
                self.log("warning", f"Dropped {dropped_count} rows with NULL timestamps")
            
            df_all = df_all.sort_values("ts").reset_index(drop=True)
            
            df_all["date"] = df_all["ts"].dt.date
            unique_dates = df_all["date"].nunique()
            
            output_path = FORWARD_DIR / "phase220_aggregated_signals.csv"
            df_all.to_csv(output_path, index=False)
            
            duration = time.time() - start_time
            
            self.log("info", f"✓ Phase 220 complete: {output_path}")
            self.log("info", f"  Output: {after_clean} rows across {unique_dates} unique dates")
            self.log("info", f"  Duration: {duration:.2f}s")
            
            self.execution_report["statistics"]["phase220"] = {
                "input_files": int(len(archive_files)),
                "input_rows": int(before_count),
                "duplicates_removed": int(dedup_count),
                "null_timestamps_dropped": int(dropped_count),
                "output_rows": int(after_clean),
                "unique_dates": int(unique_dates),
            }
            
            self.check_performance("Phase 220", duration, PHASE_220_TARGET)
            self.execution_report["phases_executed"].append("Phase 220")

            # Run continuous validators after Phase 220
            try:
                self.log("info", "Running continuous validators after Phase 220...")
                venv_result = self.venv_lock.validate()
                self.execution_report["validation_results"]["phase220_venv"] = venv_result
                if not venv_result["passed"]:
                    self.log("warning", f"Venv validation failed: {venv_result['message']}")
            except Exception as e:
                self.log("warning", f"Validator error after Phase 220: {e}")

            return True, str(output_path)
        
        except Exception as e:
            self.log("error", f"Phase 220 failed: {e}")
            import traceback
            self.log("error", traceback.format_exc())
            return False, ""
    
    def run_phase_221(self, input_path: str) -> Tuple[bool, str]:
        """Phase 221: Forward Returns Computation."""
        self.log("info", "=" * 70)
        self.log("info", "PHASE 221: FORWARD RETURNS COMPUTATION")
        self.log("info", "=" * 70)
        
        start_time = time.time()
        
        try:
            df = pd.read_csv(input_path)
            # Use canonical timestamp normalization
            df, _ = normalize_timestamp_column_strict(
                df,
                col_name="ts",
                fallback_col="timestamp",
                metrics_path=METRICS_DIR / "phase221_ts_metrics.json",
                name="phase221_forward_returns",
            )

            self.log("info", f"Loaded {len(df)} rows from Phase 220")
            
            horizons = [1, 2, 5, 10, 15]
            
            for horizon in horizons:
                col_name = f"fwd_ret_{horizon}"
                if "ltp" in df.columns:
                    df[col_name] = df.groupby(["underlying", "strike", "side"])["ltp"].shift(-horizon)
                    df[col_name] = (df[col_name] - df["ltp"]) / df["ltp"].replace(0, np.nan)
                else:
                    df[col_name] = 0.0
            
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
            
            for horizon in horizons:
                col = f"fwd_ret_{horizon}"
                df[col] = df[col].fillna(0.0)
            
            output_path = FORWARD_DIR / "phase221_forward_returns.csv"
            df["ts"] = df["ts"].astype(str)
            df.to_csv(output_path, index=False)
            
            duration = time.time() - start_time
            
            self.log("info", f"✓ Phase 221 complete: {output_path}")
            self.log("info", f"  Output: {len(df)} rows with {len(horizons)} horizons")
            self.log("info", f"  Duration: {duration:.2f}s")
            
            avg_coverage = np.mean([s["coverage"] for s in coverage_stats.values()])
            
            self.execution_report["statistics"]["phase221"] = {
                "input_rows": int(len(df)),
                "horizons": horizons,
                "coverage_stats": coverage_stats,
                "avg_coverage": float(avg_coverage),
            }
            
            self.check_performance("Phase 221", duration, PHASE_221_TARGET)
            self.execution_report["phases_executed"].append("Phase 221")

            # Run continuous validators after Phase 221
            try:
                self.log("info", "Running continuous validators after Phase 221...")
                timestamp_result = self.timestamp_validator.validate()
                self.execution_report["validation_results"]["phase221_timestamp"] = timestamp_result
                if not timestamp_result["passed"]:
                    self.log("warning", f"Timestamp validation failed: {timestamp_result['message']}")
            except Exception as e:
                self.log("warning", f"Validator error after Phase 221: {e}")

            return True, str(output_path)
        
        except Exception as e:
            self.log("error", f"Phase 221 failed: {e}")
            import traceback
            self.log("error", traceback.format_exc())
            return False, ""
    
    def run_phase_239(self, signals_path: str, orders_path: str) -> Tuple[bool, str]:
        """Phase 239: PnL Enrichment with merge key normalization."""
        self.log("info", "=" * 70)
        self.log("info", "PHASE 239: PNL ENRICHMENT (4-STAGE JOIN)")
        self.log("info", "=" * 70)
        
        start_time = time.time()
        
        try:
            # Apply merge key normalization
            try:
                from core.engine.merge_key_normalizer import normalize_signals, normalize_orders

                signals = pd.read_csv(signals_path)
                # Use canonical timestamp normalization
                signals, _ = normalize_timestamp_column_strict(
                    signals,
                    col_name="ts",
                    fallback_col="timestamp",
                    metrics_path=METRICS_DIR / "phase239_signals_ts_metrics.json",
                    name="phase239_signals",
                )
                signals, _ = normalize_signals(signals)

                orders = pd.read_csv(orders_path)
                # Use canonical timestamp normalization
                orders, _ = normalize_timestamp_column_strict(
                    orders,
                    col_name="ts",
                    fallback_col="timestamp",
                    metrics_path=METRICS_DIR / "phase239_orders_ts_metrics.json",
                    name="phase239_orders",
                )
                orders, _ = normalize_orders(orders)

                self.log("info", f"Applied merge key normalization to {len(signals)} signals and {len(orders)} orders")
            except Exception as e:
                self.log("warning", f"Normalization failed: {e} — using raw data")
                signals = pd.read_csv(signals_path)
                orders = pd.read_csv(orders_path)
            
            # Validate merge keys
            merge_keys = ["ts", "underlying", "strike", "side", "expiry"]
            signals = signals.dropna(subset=merge_keys)
            orders = orders.dropna(subset=merge_keys)
            
            self.log("info", f"After validation: {len(signals)} signals, {len(orders)} orders")
            
            # Mark original indices
            orders["_orig_idx"] = range(len(orders))
            
            # STAGE 1: Exact match
            self.log("info", "Stage 1: Exact match on 5 keys...")
            stage1_start = time.time()
            matched_1 = signals.merge(orders, on=merge_keys, how="inner", suffixes=("_sig", "_ord"))
            stage1_count = len(matched_1)
            stage1_time = time.time() - stage1_start
            matched_indices_1 = set(matched_1["_orig_idx"].unique()) if stage1_count > 0 else set()
            self.log("info", f"  {stage1_count} matches in {stage1_time:.2f}s")
            
            # STAGE 2: AsOf join
            unmatched = orders[~orders["_orig_idx"].isin(matched_indices_1)].copy()
            self.log("info", f"Stage 2: AsOf join (±2s) for {len(unmatched)} remaining orders...")
            stage2_start = time.time()
            stage2_count = 0
            matched_indices_2 = set()
            
            if len(unmatched) > 0:
                # Use canonical timestamp normalization for AsOf joins
                unmatched, _ = normalize_timestamp_column_strict(
                    unmatched,
                    col_name="ts",
                    fallback_col="timestamp",
                    metrics_path=METRICS_DIR / "phase239_asof_ts_metrics.json",
                    name="phase239_asof_unmatched",
                )
                signals, _ = normalize_timestamp_column_strict(
                    signals,
                    col_name="ts",
                    fallback_col="timestamp",
                    metrics_path=METRICS_DIR / "phase239_asof_ts_metrics.json",
                    name="phase239_asof_signals",
                )
                unmatched["ts_dt"] = unmatched["ts"]
                signals["ts_dt"] = signals["ts"]
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
                    matched_2 = matched_2.dropna(subset=["fwd_ret_1"])
                    stage2_count = len(matched_2)
                    matched_indices_2 = set(matched_2["_orig_idx"].unique())
                except Exception as e:
                    self.log("warning", f"AsOf merge failed: {e}")
            
            stage2_time = time.time() - stage2_start
            self.log("info", f"  {stage2_count} matches in {stage2_time:.2f}s")
            
            # STAGE 3: Date-only match
            unmatched = orders[~orders["_orig_idx"].isin(matched_indices_1 | matched_indices_2)].copy()
            self.log("info", f"Stage 3: Date-only match for {len(unmatched)} remaining orders...")
            stage3_start = time.time()
            stage3_count = 0
            matched_indices_3 = set()
            
            if len(unmatched) > 0:
                # Use canonical timestamp normalization for date matching
                unmatched, _ = normalize_timestamp_column_strict(
                    unmatched,
                    col_name="ts",
                    fallback_col="timestamp",
                    metrics_path=METRICS_DIR / "phase239_date_ts_metrics.json",
                    name="phase239_date_unmatched",
                )
                signals, _ = normalize_timestamp_column_strict(
                    signals,
                    col_name="ts",
                    fallback_col="timestamp",
                    metrics_path=METRICS_DIR / "phase239_date_ts_metrics.json",
                    name="phase239_date_signals",
                )
                unmatched["date"] = unmatched["ts"].dt.date
                signals["date"] = signals["ts"].dt.date
                
                matched_3 = unmatched.merge(
                    signals[["date", "underlying", "side", "fwd_ret_1", "fwd_ret_2", "fwd_ret_5", "fwd_ret_10", "fwd_ret_15"]],
                    on=["date", "underlying", "side"],
                    how="inner",
                    suffixes=("_ord", "_sig")
                )
                matched_3 = matched_3.dropna(subset=["fwd_ret_1"])
                stage3_count = len(matched_3)
                matched_indices_3 = set(matched_3["_orig_idx"].unique())
            
            stage3_time = time.time() - stage3_start
            self.log("info", f"  {stage3_count} matches in {stage3_time:.2f}s")
            
            # STAGE 4: Nearest timestamp
            unmatched = orders[~orders["_orig_idx"].isin(matched_indices_1 | matched_indices_2 | matched_indices_3)].copy()
            self.log("info", f"Stage 4: Nearest timestamp (±5s) for {len(unmatched)} remaining orders...")
            stage4_start = time.time()
            stage4_count = 0
            
            if len(unmatched) > 0:
                # Use canonical timestamp normalization for nearest timestamp matching
                unmatched, _ = normalize_timestamp_column_strict(
                    unmatched,
                    col_name="ts",
                    fallback_col="timestamp",
                    metrics_path=METRICS_DIR / "phase239_nearest_ts_metrics.json",
                    name="phase239_nearest_unmatched",
                )
                signals, _ = normalize_timestamp_column_strict(
                    signals,
                    col_name="ts",
                    fallback_col="timestamp",
                    metrics_path=METRICS_DIR / "phase239_nearest_ts_metrics.json",
                    name="phase239_nearest_signals",
                )
                unmatched["ts_dt"] = unmatched["ts"]
                signals["ts_dt"] = signals["ts"]
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
                    stage4_count = len(matched_4)
                except Exception as e:
                    self.log("warning", f"AsOf merge failed: {e}")
            
            stage4_time = time.time() - stage4_start
            self.log("info", f"  {stage4_count} matches in {stage4_time:.2f}s")
            
            # Summary
            total_matches = stage1_count + stage2_count + stage3_count + stage4_count
            unique_enriched = len(matched_indices_1 | matched_indices_2 | matched_indices_3)
            enrichment_rate = unique_enriched / len(orders) * 100
            
            self.log("info", f"✓ Total matches: {total_matches}, Unique enriched orders: {unique_enriched}")
            self.log("info", f"  Enrichment rate: {enrichment_rate:.1f}%")
            
            # Save output
            output_path = ENRICHED_DIR / "angel_virtual_orders_with_pnl.csv"
            orders.to_csv(output_path, index=False)
            
            duration = time.time() - start_time
            
            self.log("info", f"✓ Phase 239 complete: {output_path}")
            self.log("info", f"  Output: {len(orders)} rows")
            self.log("info", f"  Duration: {duration:.2f}s")
            
            self.execution_report["statistics"]["phase239"] = {
                "input_signals": int(len(signals)),
                "input_orders": int(len(orders)),
                "stage1_exact": int(stage1_count),
                "stage2_asof": int(stage2_count),
                "stage3_date": int(stage3_count),
                "stage4_nearest": int(stage4_count),
                "total_matches": int(total_matches),
                "unique_enriched": int(unique_enriched),
                "enrichment_rate": float(enrichment_rate),
            }
            
            self.check_performance("Phase 239", duration, PHASE_239_TARGET)
            self.execution_report["phases_executed"].append("Phase 239")

            # Run continuous validators after Phase 239
            try:
                self.log("info", "Running continuous validators after Phase 239...")
                merge_key_result = self.merge_key_validator.validate()
                self.execution_report["validation_results"]["phase239_merge_key"] = merge_key_result
                if not merge_key_result["passed"]:
                    self.log("warning", f"Merge key validation failed: {merge_key_result['message']}")
            except Exception as e:
                self.log("warning", f"Validator error after Phase 239: {e}")

            return True, str(output_path)
        
        except Exception as e:
            self.log("error", f"Phase 239 failed: {e}")
            import traceback
            self.log("error", traceback.format_exc())
            return False, ""
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """Run complete Phase 220 → 221 → 239 pipeline."""
        self.log("info", "=" * 70)
        self.log("info", "PRODUCTION PIPELINE ORCHESTRATOR - STARTING")
        self.log("info", "=" * 70)
        
        overall_start = time.time()
        
        # Phase 220
        phase220_success, phase220_output = self.run_phase_220()
        if not phase220_success:
            self.log("error", "Pipeline failed at Phase 220")
            return self.execution_report
        
        # Phase 221
        phase221_success, phase221_output = self.run_phase_221(phase220_output)
        if not phase221_success:
            self.log("error", "Pipeline failed at Phase 221")
            return self.execution_report
        
        # Phase 239
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
        # Convert numpy types to Python types for JSON serialization
        report_clean = json.loads(json.dumps(self.execution_report, default=str))
        with open(report_path, "w") as f:
            json.dump(report_clean, f, indent=2)
        
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
    """Convenience function to run complete pipeline."""
    orchestrator = ProductionPipelineOrchestrator(verbose=verbose)
    return orchestrator.run_full_pipeline()


if __name__ == "__main__":
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
