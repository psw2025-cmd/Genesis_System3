"""
System3 Phase 239 - Virtual PnL Joiner

Join virtual trades with forward returns to measure edge with multi-stage matching and validation.
"""

import sys
import json
import math
import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.utils.timestamp_parser import (
    normalize_timestamp_column_strict,
    parse_system3_timestamp,
)

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
METRICS_DIR = PROJECT_ROOT / "storage" / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)
VIRTUAL_ORDERS_CSV = STORAGE_LIVE / "angel_virtual_orders.csv"
FORWARD_SIGNALS_CSV = STORAGE_LIVE / "angel_index_ai_signals_with_forward.csv"
OUTPUT_CSV = STORAGE_LIVE / "angel_virtual_orders_with_pnl.csv"
VALIDATION_JSON = STORAGE_LIVE / "meta" / "PHASE239_POST_FIX_VALIDATION.json"
VALIDATION_JSON.parent.mkdir(parents=True, exist_ok=True)

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_virtual_trades_enrichment.log"


def _log(message: str) -> None:
    """Log message."""
    log_msg = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(log_msg)
    except Exception:
        pass


def _write_json(path: Path, payload: dict) -> None:
    """Write JSON with safe casting."""
    serializable = json.loads(json.dumps(payload, default=lambda o: o if isinstance(o, (int, float, str, bool)) else str(o)))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)


SIDE_MAP = {
    "BUY": "BUY",
    "SELL": "SELL",
    "HOLD": "HOLD",
    "CE": "BUY",
    "PE": "SELL",
    "CALL": "BUY",
    "PUT": "SELL",
    "C": "BUY",
    "P": "SELL",
    "1": "BUY",
    "-1": "SELL",
    "0": "HOLD",
}


def _normalize_side(series: pd.Series) -> pd.Series:
    """Map raw side strings to BUY/SELL/HOLD."""
    def mapper(val):
        raw = str(val).upper().strip()
        return SIDE_MAP.get(raw, "HOLD")
    return series.astype(str).apply(mapper)


def _prepare_forward_df(forward_df: pd.DataFrame, errors: list) -> pd.DataFrame:
    """Heal forward dataframe for join: ts, side, expiry using centralized parser."""
    df = forward_df.copy()

    # Use canonical timestamp parser (strict, metrics-aware)
    df, _ = normalize_timestamp_column_strict(
        df,
        col_name="ts",
        fallback_col="timestamp",
        metrics_path=METRICS_DIR / "phase239_forward_ts_metrics.json",
        name="phase239_forward_ts",
    )

    df = df.copy()
    df["side"] = _normalize_side(df.get("side", pd.Series(["HOLD"] * len(df))))
    
    # Normalize strike to float64 for merge compatibility
    if "strike" in df.columns:
        df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
    
    # Normalize underlying to string for merge compatibility
    if "underlying" in df.columns:
        df["underlying"] = df["underlying"].astype(str).str.upper().str.strip()

    df["expiry"] = parse_system3_timestamp(df.get("expiry"), name="forward_expiry")
    df["expiry"] = df["expiry"].dt.normalize()
    if "time_to_expiry" in df.columns:
        tte = pd.to_numeric(df["time_to_expiry"], errors="coerce")
        mask = df["expiry"].isna() & df["ts"].notna() & tte.notna()
        if mask.any():
            df.loc[mask, "expiry"] = df.loc[mask, "ts"] + pd.to_timedelta(tte[mask].apply(lambda x: math.ceil(x)), unit="D")
            _log(f"Filled expiry from time_to_expiry for {mask.sum()} rows")

    return df


def _stage_merge_exact(base: pd.DataFrame, fwd: pd.DataFrame, forward_cols: list, keys: list, label: str):
    """Exact merge on keys; fills forward cols where missing."""
    subset_keys = [k for k in keys if k in base.columns and k in fwd.columns]
    if not subset_keys:
        return base, 0
    
    # Initialize forward columns if missing in base
    for col in forward_cols:
        if col not in base.columns:
            base[col] = pd.NA
    
    before = base[forward_cols[0]].notna().sum() if forward_cols else 0
    # Filter forward_cols to only those present in fwd
    valid_forward_cols = [c for c in forward_cols if c in fwd.columns]
    if not valid_forward_cols:
        return base, 0
    # Keep all base rows; fill using merge where keys match
    merged = base.merge(
        fwd[subset_keys + valid_forward_cols],
        on=subset_keys,
        how="left",
        suffixes=("", "_fwd"),
    )
    # Copy forward cols - merged has them, update base where merged is notna
    for col in valid_forward_cols:
        if col in merged.columns:
            # Fill base[col] where merged[col] is not NaN
            base[col] = merged[col]
    matched = base[valid_forward_cols[0]].notna().sum() - before
    _log(f"Stage {label}: matched {matched} rows on keys {subset_keys}")
    return base, matched


def _stage_merge_asof(base: pd.DataFrame, fwd: pd.DataFrame, forward_cols: list, by_cols: list, tolerance: timedelta, label: str):
    """Nearest-time merge with tolerance on ts and grouping keys."""
    if "ts" not in base.columns or "ts" not in fwd.columns:
        return base, 0
    
    # Initialize forward columns if missing
    for col in forward_cols:
        if col not in base.columns:
            base[col] = pd.NA

    unmatched = base[base[forward_cols[0]].isna()].copy()
    if unmatched.empty:
        return base, 0

    base_work = unmatched.reset_index().sort_values("ts")
    fwd_work = fwd.reset_index().sort_values("ts")

    # Filter forward_cols to only those present in fwd_work
    valid_forward_cols = [c for c in forward_cols if c in fwd_work.columns]
    if not valid_forward_cols:
        return base, 0

    by_cols = [c for c in by_cols if c in base_work.columns and c in fwd_work.columns]
    
    # Build the columns for merge - only include columns that exist in fwd_work
    cols_for_merge = (by_cols if by_cols else []) + ["ts"] + valid_forward_cols
    
    if by_cols:
        merged = pd.merge_asof(
            base_work,
            fwd_work[cols_for_merge].sort_values("ts"),
            on="ts",
            by=by_cols,
            direction="nearest",
            tolerance=tolerance,
            suffixes=("", "_fwd"),
        )
    else:
        merged = pd.merge_asof(
            base_work,
            fwd_work[cols_for_merge].sort_values("ts"),
            on="ts",
            direction="nearest",
            tolerance=tolerance,
            suffixes=("", "_fwd"),
        )

    # Check which suffix was used for forward columns (merge_asof adds _fwd if column exists in both)
    _log(f"DEBUG {label}: merged columns = {merged.columns.tolist()}")
    _log(f"DEBUG {label}: valid_forward_cols = {valid_forward_cols}")
    
    cols_to_use = []
    for col in valid_forward_cols:
        if col + "_fwd" in merged.columns:
            cols_to_use.append(col + "_fwd")
            _log(f"DEBUG {label}: {col} found as {col}_fwd")
        elif col in merged.columns:
            cols_to_use.append(col)
            _log(f"DEBUG {label}: {col} found unsuffixed")
        else:
            # Column missing entirely - skip
            _log(f"DEBUG {label}: {col} NOT FOUND in merged")
            continue
    
    if not cols_to_use:
        _log(f"DEBUG {label}: NO cols_to_use - returning")
        return base, 0
    
    _log(f"DEBUG {label}: cols_to_use = {cols_to_use}")
    new_mask = merged[cols_to_use[0]].notna()
    matched_indices = merged.loc[new_mask, "index"]
    for i, col in enumerate(valid_forward_cols):
        if i < len(cols_to_use):
            base.loc[matched_indices, col] = merged.loc[new_mask, cols_to_use[i]].values
    matched = int(new_mask.sum())
    _log(f"Stage {label}: matched {matched} rows via asof (tolerance {tolerance})")
    return base, matched


def _stage_merge_date(base: pd.DataFrame, fwd: pd.DataFrame, forward_cols: list, keys: list, label: str):
    """Date-only join (ts.date + keys)."""
    if "ts" not in base.columns or "ts" not in fwd.columns:
        return base, 0
    
    # Initialize forward columns if missing
    for col in forward_cols:
        if col not in base.columns:
            base[col] = pd.NA

    base_work = base.reset_index()
    fwd_work = fwd.reset_index()
    base_work["join_date"] = pd.to_datetime(base_work["ts"], errors="coerce").dt.date
    fwd_work["join_date"] = pd.to_datetime(fwd_work["ts"], errors="coerce").dt.date
    join_keys = ["join_date"] + [k for k in keys if k in base_work.columns and k in fwd_work.columns]

    # Filter forward_cols to only those present in fwd_work
    valid_forward_cols = [c for c in forward_cols if c in fwd_work.columns]
    if not valid_forward_cols:
        return base, 0

    merged = base_work.merge(fwd_work[join_keys + valid_forward_cols], on=join_keys, how="left", suffixes=("", "_fwd"))
    new_mask = merged[valid_forward_cols[0]].notna() & base_work[valid_forward_cols[0]].isna()
    matched_indices = merged.loc[new_mask, "index"]
    for col in valid_forward_cols:
        base.loc[matched_indices, col] = merged.loc[new_mask, col].values
    matched = int(new_mask.sum())
    _log(f"Stage {label}: matched {matched} rows on date-only keys {join_keys}")
    return base, matched


def run_phase239() -> dict:
    """Run Phase 239: Virtual PnL Joiner (multi-stage)."""
    errors = []
    warnings = []
    start_time = time.time()

    if not VIRTUAL_ORDERS_CSV.exists():
        _log("WARN: Virtual orders CSV not found")
        return {
            "phase": 239,
            "status": "WARN",
            "details": "Virtual orders CSV not found",
            "outputs": {},
            "errors": []
        }

    if not FORWARD_SIGNALS_CSV.exists():
        _log("WARN: Forward signals CSV not found")
        return {
            "phase": 239,
            "status": "WARN",
            "details": "Forward signals CSV not found",
            "outputs": {},
            "errors": []
        }

    try:
        orders_df = pd.read_csv(VIRTUAL_ORDERS_CSV, engine="python", on_bad_lines="skip")
        forward_df = pd.read_csv(FORWARD_SIGNALS_CSV, engine="python", on_bad_lines="skip")
        _log(f"Loaded {len(orders_df)} virtual orders and {len(forward_df)} forward rows")

        forward_df = _prepare_forward_df(forward_df, errors)
        
        # Use centralized timestamp parser for orders
        orders_df, _ = normalize_timestamp_column_strict(
            orders_df,
            col_name="ts",
            fallback_col="timestamp",
            metrics_path=METRICS_DIR / "phase239_orders_ts_metrics.json",
            name="phase239_orders_ts",
        )
        orders_df["expiry"] = parse_system3_timestamp(orders_df.get("expiry"), name="orders_expiry")
        orders_df["expiry"] = orders_df["expiry"].dt.normalize()
        orders_df["side"] = _normalize_side(orders_df.get("side", pd.Series(["HOLD"] * len(orders_df))))
        
        # Ensure required merge key columns exist (avoid KeyError in Phase 238/239)
        for col in ["underlying", "strike"]:
            if col not in orders_df.columns:
                orders_df[col] = pd.NA
                _log(f"Added missing column '{col}' as NA for merge compatibility")
        # Normalize merge key types for compatibility
        if "strike" in orders_df.columns:
            orders_df["strike"] = pd.to_numeric(orders_df["strike"], errors="coerce")
        if "underlying" in orders_df.columns:
            orders_df["underlying"] = orders_df["underlying"].astype(str).str.upper().str.strip()
        
        # PRE-MERGE GUARD: Count and drop orders with null merge keys (explicit metrics)
        merge_keys = [k for k in ["ts", "underlying", "strike", "side", "expiry"] if k in orders_df.columns]
        if not merge_keys:
            return {
                "phase": 239,
                "status": "ERROR",
                "details": "No merge keys available in orders (need at least ts)",
                "outputs": {},
                "errors": ["Missing merge key columns in orders DataFrame"],
            }
        null_mask = orders_df[merge_keys].isna().any(axis=1)
        null_count = int(null_mask.sum())
        if null_count > 0:
            null_rate = null_count / len(orders_df)
            msg = f"PRE-MERGE GUARD: Dropping {null_count} orders with null merge keys ({null_rate:.2%})"
            _log(msg)
            warnings.append(msg)
            orders_df = orders_df[~null_mask].copy()

        forward_cols = [c for c in forward_df.columns if c.lower().startswith("fwd_ret") or c.lower().startswith("forward_ret")]
        if not forward_cols:
            _log("WARNING: No forward return columns found - checking for alt names")
            forward_cols = [c for c in forward_df.columns if "forward" in c.lower() or "ret" in c.lower()]
        
        if not forward_cols:
            return {
                "phase": 239,
                "status": "ERROR",
                "details": "No forward return columns present",
                "outputs": {},
                "errors": ["Missing forward return columns"],
            }
        
        _log(f"Forward return columns detected: {forward_cols}")

        for col in forward_cols:
            if col not in orders_df.columns:
                orders_df[col] = pd.NA

        stage_stats = []

        orders_df, m1 = _stage_merge_exact(
            orders_df,
            forward_df,
            forward_cols,
            ["ts", "underlying", "strike", "side", "expiry"],
            label="exact_full",
        )
        stage_stats.append({"stage": "exact_full", "matched": int(m1)})

        orders_df, m2 = _stage_merge_asof(
            orders_df,
            forward_df,
            forward_cols,
            by_cols=["underlying", "strike", "side"],
            tolerance=timedelta(seconds=2),
            label="asof_2s",
        )
        stage_stats.append({"stage": "asof_2s", "matched": int(m2)})

        orders_df, m3 = _stage_merge_date(
            orders_df,
            forward_df,
            forward_cols,
            keys=["underlying", "side"],
            label="date_only",
        )
        stage_stats.append({"stage": "date_only", "matched": int(m3)})

        orders_df, m4 = _stage_merge_asof(
            orders_df,
            forward_df,
            forward_cols,
            by_cols=["underlying", "side"],
            tolerance=timedelta(seconds=5),
            label="nearest_symbol",
        )
        stage_stats.append({"stage": "nearest_symbol", "matched": int(m4)})

        matched_count = int(orders_df[forward_cols[0]].notna().sum()) if forward_cols and forward_cols[0] in orders_df.columns else 0
        unmatched_count = int(len(orders_df) - matched_count)
        match_rate = (matched_count / len(orders_df) * 100) if len(orders_df) > 0 else 0.0

        _log(f"Final join result: matched {matched_count} ({match_rate:.1f}%), unmatched {unmatched_count}")

        for col in forward_cols:
            if col in orders_df.columns:
                pnl_col = col.replace("forward_ret", "pnl").replace("fwd_ret", "pnl")
                orders_df[pnl_col] = orders_df[col] * orders_df.get("lots", 1)

        orders_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

        orders_with_valid_ts = int(orders_df["ts"].notna().sum()) if "ts" in orders_df.columns else 0
        overall_enrichment_rate = (matched_count / len(orders_df)) if len(orders_df) else 0.0
        valid_ts_enrichment_rate = (matched_count / orders_with_valid_ts) if orders_with_valid_ts else 0.0

        validation = {
            "timestamp": datetime.now().isoformat(),
            "phase": 239,
            "total_orders": int(len(orders_df)),
            "orders_with_valid_ts": orders_with_valid_ts,
            "matched": matched_count,
            "unmatched": unmatched_count,
            "overall_enrichment_rate": round(overall_enrichment_rate, 6),
            "valid_ts_enrichment_rate": round(valid_ts_enrichment_rate, 6),
            "forward_quality": {
                "ts_missing": int(forward_df["ts"].isna().sum()) if "ts" in forward_df.columns else None,
                "expiry_missing": int(forward_df["expiry"].isna().sum()) if "expiry" in forward_df.columns else None,
                "side_counts": forward_df.get("side", pd.Series(dtype=str)).value_counts(dropna=False).to_dict(),
            },
            "stage_stats": stage_stats,
            "outputs": {"output_file": str(OUTPUT_CSV)},
        }
        _write_json(VALIDATION_JSON, validation)

        # Enrichment thresholds
        enrichment_warn = False
        if overall_enrichment_rate < 0.30:
            warnings.append(f"Overall enrichment rate below 30%: {overall_enrichment_rate:.2%}")
            enrichment_warn = True
        if valid_ts_enrichment_rate < 0.80:
            warnings.append(f"Valid-ts enrichment rate below 80%: {valid_ts_enrichment_rate:.2%}")
            enrichment_warn = True

        metrics_payload = {
            "timestamp": datetime.now().isoformat(),
            "phase": 239,
            "total_orders": int(len(orders_df)),
            "orders_with_valid_ts": orders_with_valid_ts,
            "enriched_orders": matched_count,
            "overall_enrichment_rate": round(overall_enrichment_rate, 6),
            "valid_ts_enrichment_rate": round(valid_ts_enrichment_rate, 6),
            "thresholds": {
                "overall_min": 0.30,
                "valid_ts_min": 0.80,
            },
            "status": "WARN" if enrichment_warn else "OK",
            "production_blocker": enrichment_warn,
            "stage_stats": stage_stats,
            "warnings": warnings,
            "errors": errors,
            "duration_seconds": round(time.time() - start_time, 4),
        }
        _write_json(METRICS_DIR / "phase_239_enrichment_metrics.json", metrics_payload)

        status = "OK" if not enrichment_warn and match_rate >= 85 else "WARN"
        if match_rate < 85:
            warnings.append(f"Join match rate below target: {match_rate:.1f}%")
        if forward_cols and forward_cols[0] in orders_df.columns and orders_df[forward_cols[0]].isna().all():
            status = "WARN"
            warnings.append("fwd_ret_1 remains 100% NaN after all join stages")

        duration = time.time() - start_time

        return {
            "phase": 239,
            "status": status,
            "details": f"Enriched {len(orders_df)} orders: {matched_count} matched ({match_rate:.1f}%), {unmatched_count} unmatched",
            "outputs": {
                "total_orders": len(orders_df),
                "matched": matched_count,
                "unmatched": unmatched_count,
                "match_rate_pct": match_rate,
                "output_file": str(OUTPUT_CSV),
                "validation_file": str(VALIDATION_JSON),
                "metrics_file": str(METRICS_DIR / "phase_239_enrichment_metrics.json"),
                "duration_seconds": duration,
            },
            "warnings": warnings,
            "errors": errors,
        }

    except Exception as e:
        import traceback
        error_msg = f"Error enriching trades: {e}"
        trace = traceback.format_exc()
        _log(f"ERROR: {error_msg}\n{trace}")
        print(f"FULL ERROR:\n{trace}")
        return {
            "phase": 239,
            "status": "ERROR",
            "details": error_msg,
            "outputs": {},
            "errors": [error_msg],
        }


if __name__ == "__main__":
    result = run_phase239()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")

