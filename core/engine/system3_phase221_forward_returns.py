"""
System3 Phase 221 - Forward Return Calculator

Computes forward returns for historical signals.
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json
import time

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.utils.timestamp_parser import normalize_timestamp_column_strict, write_iso_timestamps

OUTPUT_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_with_forward.csv"
METRICS_DIR = PROJECT_ROOT / "storage" / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)
# Use aggregated full dataset (from Phase 220) if available, else fall back to current curated
CURATED_FULL_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_curated_full.csv"
CURATED_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals_curated.csv"
SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"
LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _log(msg: str) -> None:
    """Log message to phase log file."""
    log_file = LOG_DIR / "phase221_forward_returns.log"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with log_file.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def run_phase221(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 221: Forward Return Calculator.

    Returns:
        dict: {
            "phase": 221,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "rows_processed": int,
                "forward_returns_added": bool,
                "output_file": str,
            },
            "errors": [],
        }
    """
    errors = []
    warnings = []
    start_time = time.time()

    try:
        # Priority: aggregated full dataset (Phase 220) > curated > regular signals
        if CURATED_FULL_CSV.exists():
            signals_file = CURATED_FULL_CSV
            _log(f"Using aggregated full dataset: {CURATED_FULL_CSV}")
        elif CURATED_CSV.exists():
            signals_file = CURATED_CSV
            _log(f"Using current curated signals: {CURATED_CSV}")
        elif SIGNALS_CSV.exists():
            signals_file = SIGNALS_CSV
            _log(f"Using regular signals: {SIGNALS_CSV}")
        else:
            return {
                "phase": 221,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"rows_processed": 0, "forward_returns_added": False, "output_file": str(OUTPUT_CSV)},
                "errors": [],
            }

        # Load data with safe CSV loader
        try:
            df = pd.read_csv(signals_file, engine="python", on_bad_lines="skip")

            # Remove any rows that are duplicate headers (rows matching column names exactly)
            if len(df) > 0:
                header_cols = df.columns.tolist()
                # Check for rows that match header exactly (duplicate headers)
                mask = df.astype(str).apply(lambda x: x.tolist() == header_cols, axis=1)
                duplicate_headers = mask.sum()
                if duplicate_headers > 0:
                    df = df[~mask].copy()
                    errors.append(f"Removed {duplicate_headers} duplicate header rows from source file")
        except Exception as e:
            errors.append(f"Failed to load CSV: {e}")
            return {
                "phase": 221,
                "status": "ERROR",
                "details": f"Failed to load CSV: {e}",
                "outputs": {"rows_processed": 0, "forward_returns_added": False, "output_file": str(OUTPUT_CSV)},
                "errors": errors,
            }

        if len(df) == 0:
            return {
                "phase": 221,
                "status": "WARN",
                "details": "No data to process",
                "outputs": {"rows_processed": 0, "forward_returns_added": False, "output_file": str(OUTPUT_CSV)},
                "errors": [],
            }

        # FIX: Use centralized timestamp parser (handles all formats, fills gaps)
        try:
            df, ts_metrics = normalize_timestamp_column_strict(
                df,
                col_name="ts",
                fallback_col="timestamp",
                metrics_path=METRICS_DIR / "phase221_ts_metrics.json",
                name="phase221_ts",
            )
            errors.append(
                f"Timestamp parsing: used canonical parser; NaT {ts_metrics.get('nat_count', 0)} / {ts_metrics.get('total', 0)}"
            )
        except ValueError as e:
            return {
                "phase": 221,
                "status": "ERROR",
                "details": f"Timestamp parsing failed: {e}",
                "outputs": {"rows_processed": 0, "forward_returns_added": False, "output_file": str(OUTPUT_CSV)},
                "errors": [str(e)],
            }

        # FIX: Normalize side column (CE/PE → BUY/SELL) before grouping
        if "side" in df.columns:
            # Map option types to trading directions
            side_map = {
                "BUY": "BUY",
                "SELL": "SELL",
                "CE": "BUY",  # Call option = bullish = BUY direction
                "PE": "SELL",  # Put option = bearish = SELL direction
                "0": "HOLD",
                "HOLD": "HOLD",
            }
            df["side"] = df["side"].astype(str).str.upper().map(side_map).fillna("HOLD")
            invalid_sides = df[~df["side"].isin(["BUY", "SELL", "HOLD"])]["side"].unique()
            if len(invalid_sides) > 0:
                errors.append(f"Warning: Invalid side values found: {invalid_sides}")

        # PRODUCTION-GRADE FORWARD RETURN COMPUTATION
        # Required horizons: 1, 2, 5, 10, 15 periods
        FORWARD_HORIZONS = [1, 2, 5, 10, 15]

        # Determine price column: prefer ltp (option premium), fallback to close/spot
        price_col = None
        if "ltp" in df.columns:
            price_col = "ltp"
        elif "close" in df.columns:
            price_col = "close"
        elif "spot" in df.columns:
            price_col = "spot"
        else:
            return {
                "phase": 221,
                "status": "ERROR",
                "details": "No price column (ltp/close/spot) available for forward returns",
                "outputs": {"rows_processed": len(df), "forward_returns_added": False, "output_file": str(OUTPUT_CSV)},
                "errors": ["CRITICAL: Missing price column"],
            }

        # Convert price column to numeric
        df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
        _log(f"Using price column: {price_col}")

        # Initialize ALL required forward return columns
        for horizon in FORWARD_HORIZONS:
            df[f"fwd_ret_{horizon}"] = np.nan

        # STRATEGY: Compute forward returns at dataframe level (time-sorted)
        # This works even when contracts have few rows - we look ahead in time
        # Sort by timestamp to ensure forward lookups are chronological
        df = df.sort_values("ts").reset_index(drop=True)

        # Vectorized forward return computation for ALL rows
        for horizon in FORWARD_HORIZONS:
            col_name = f"fwd_ret_{horizon}"
            # Shift price backward (negative shift = forward in time)
            future_prices = df[price_col].shift(-horizon)
            current_prices = df[price_col]

            # Calculate percentage returns where both current and future are valid and >0
            valid_mask = current_prices.notna() & future_prices.notna() & (current_prices > 0)
            returns = (future_prices - current_prices) / current_prices

            # Assign returns where valid
            df.loc[valid_mask, col_name] = returns[valid_mask]

        computed_count = df["fwd_ret_1"].notna().sum()
        errors.append(f"Computed forward returns for {computed_count} rows across {len(FORWARD_HORIZONS)} horizons")

        # Per-horizon validation stats
        for horizon in FORWARD_HORIZONS:
            col_name = f"fwd_ret_{horizon}"
            non_null = df[col_name].notna().sum()
            _log(f"{col_name}: {non_null} rows")

        # VALIDATION: Ensure output integrity before saving
        ts_null_count = df["ts"].isna().sum()
        if ts_null_count == len(df):
            return {
                "phase": 221,
                "status": "ERROR",
                "details": "Output ts column is 100% NaN - rejecting write",
                "outputs": {"rows_processed": len(df), "forward_returns_added": False, "output_file": str(OUTPUT_CSV)},
                "errors": ["CRITICAL: ts column validation failed"],
            }

        invalid_sides = df[~df["side"].isin(["BUY", "SELL", "HOLD"])]["side"].unique()
        if len(invalid_sides) > 0:
            errors.append(f"WARNING: Output contains invalid side values: {invalid_sides}")

        # Write back with clean ISO timestamps
        df["ts"] = write_iso_timestamps(df["ts"])

        # Save enriched data with a fallback in case the file is temporarily locked
        try:
            df.to_csv(OUTPUT_CSV, index=False)
        except PermissionError:
            tmp_path = OUTPUT_CSV.with_suffix(".tmp")
            df.to_csv(tmp_path, index=False)
            tmp_path.replace(OUTPUT_CSV)

        # PRODUCTION-GRADE VALIDATION
        if ts_null_count > 0:
            errors.append(f"Output has {ts_null_count}/{len(df)} rows with NaN timestamps")

        # Count how many rows got forward returns for EACH horizon
        FORWARD_HORIZONS = [1, 2, 5, 10, 15]
        fwd_ret_cols = [f"fwd_ret_{h}" for h in FORWARD_HORIZONS]
        rows_with_returns = df[fwd_ret_cols].notna().any(axis=1).sum()

        # Per-horizon stats
        horizon_stats = {}
        horizon_warnings = False
        for h in FORWARD_HORIZONS:
            col = f"fwd_ret_{h}"
            non_null = int(df[col].notna().sum())
            coverage = non_null / len(df) if len(df) else 0.0
            horizon_stats[f"fwd_ret_{h}"] = {
                "non_null": non_null,
                "coverage": round(coverage, 6),
            }
            if coverage < 0.90:
                warnings.append(f"Coverage below 90% for horizon {h}: {coverage:.2%}")
                horizon_warnings = True

        errors.append(f"Forward return coverage: {horizon_stats}")

        status = "OK" if rows_with_returns > 0 and not horizon_warnings else "WARN"
        details = f"Computed forward returns for {rows_with_returns} of {len(df)} rows across {len(FORWARD_HORIZONS)} horizons"

        metrics = {
            "timestamp": datetime.now().isoformat(),
            "phase": 221,
            "rows_processed": int(len(df)),
            "rows_with_forward_returns": int(rows_with_returns),
            "horizons": FORWARD_HORIZONS,
            "horizon_coverage": horizon_stats,
            "coverage_threshold": 0.90,
            "status": "WARN" if horizon_warnings else "OK",
            "production_blocker": horizon_warnings,
            "warnings": warnings,
            "errors": errors,
            "duration_seconds": round(time.time() - start_time, 4),
        }
        metrics_path = METRICS_DIR / "phase_221_forward_coverage.json"
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        with metrics_path.open("w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        return {
            "phase": 221,
            "status": status,
            "details": details,
            "outputs": {
                "rows_processed": len(df),
                "rows_with_forward_returns": rows_with_returns,
                "forward_returns_added": rows_with_returns > 0,
                "forward_horizons": FORWARD_HORIZONS,
                "horizon_stats": horizon_stats,
                "output_file": str(OUTPUT_CSV),
                "metrics_file": str(metrics_path),
                "duration_seconds": round(time.time() - start_time, 4),
            },
            "warnings": warnings,
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 221,
            "status": "ERROR",
            "details": f"Phase 221 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 221 - FORWARD RETURN CALCULATOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase221()

    print(f"Phase 221: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nOutput CSV: {result['outputs']['output_file']}")
        print(f"Total Rows: {result['outputs']['rows_processed']}")
        if "rows_with_forward_returns" in result["outputs"]:
            print(f"Rows with Forward Returns: {result['outputs']['rows_with_forward_returns']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
