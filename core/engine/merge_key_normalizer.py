"""
Merge Key Normalizer - Auto-standardize Phase 239 merge keys

This module enforces strict normalization across:
- underlying (standardize format)
- strike (integer, no floats)
- side (CE/PE → BUY/SELL translation)
- expiry (DDMMMYYYY → YYYY-MM-DD)
- ts (ISO8601 with UTC offset normalization)

After normalization, Phase 239 join should succeed with >30% enrichment.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Any
import json

PROJECT_ROOT = Path(__file__).parent
METRICS_DIR = PROJECT_ROOT / "storage" / "metrics"
METRICS_DIR.mkdir(parents=True, exist_ok=True)


def _log(msg: str) -> None:
    """Log message."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def normalize_underlying(series: pd.Series) -> Tuple[pd.Series, dict]:
    """Standardize underlying values."""
    original = series.copy()

    # Standard mappings
    mappings = {
        "BANKNIFTY": "BANKNIFTY",
        "NIFTY": "NIFTY",
        "SENSEX": "SENSEX",
        "FINNIFTY": "FINNIFTY",
        "MIDCPNIFTY": "MIDCPNIFTY",
    }

    # Normalize to uppercase and strip
    series = series.astype(str).str.upper().str.strip()

    # Apply mappings
    normalized = series.map(lambda x: mappings.get(x, x))

    changes = (original != normalized).sum()
    return normalized, {"metric": "underlying_normalized", "changes": int(changes)}


def normalize_strike(series: pd.Series) -> Tuple[pd.Series, dict]:
    """Convert strike to integer."""
    original = series.copy()

    # Convert to numeric, then to int
    numeric = pd.to_numeric(series, errors="coerce")
    normalized = numeric.fillna(0).astype(int)

    # Track changes
    changes = (original.fillna(0).astype(float).astype(int) != normalized).sum()

    return normalized, {"metric": "strike_int", "changes": int(changes)}


def normalize_side(series: pd.Series) -> Tuple[pd.Series, dict]:
    """Map CE/PE → BUY/SELL or keep BUY/SELL as-is."""
    original = series.copy()

    # Mapping: CE (call) → BUY (bullish), PE (put) → SELL (bearish)
    side_map = {
        "CE": "BUY",
        "PE": "SELL",
        "BUY": "BUY",
        "SELL": "SELL",
        "HOLD": "HOLD",
        "0": "HOLD",
    }

    series = series.astype(str).str.upper().str.strip()
    normalized = series.map(lambda x: side_map.get(x, "HOLD"))

    changes = (original != normalized).sum()
    invalid = normalized[~normalized.isin(["BUY", "SELL", "HOLD"])].unique()

    return normalized, {
        "metric": "side_normalized",
        "changes": int(changes),
        "invalid_values": invalid.tolist() if len(invalid) > 0 else [],
    }


def normalize_expiry(series: pd.Series) -> Tuple[pd.Series, dict]:
    """
    Convert expiry to YYYY-MM-DD format.

    Supports:
    - DDMMMYYYY (e.g., 30DEC2025)
    - YYYY-MM-DD (e.g., 2025-12-30)
    - ISO date formats
    """
    original = series.copy()

    # Try multiple formats
    for fmt in ["%d%b%Y", "%Y-%m-%d", "mixed"]:
        if fmt == "mixed":
            parsed = pd.to_datetime(series, format="mixed", errors="coerce")
        else:
            parsed = pd.to_datetime(series, format=fmt, errors="coerce")

        if not parsed.isna().all():
            break

    # Convert to YYYY-MM-DD string format
    normalized = parsed.dt.strftime("%Y-%m-%d")

    # Handle any remaining NaT
    null_count = normalized.isna().sum()
    if null_count > 0:
        _log(f"WARN: {null_count} null expiry values remain after normalization")

    return normalized, {
        "metric": "expiry_normalized",
        "nulls_after": int(null_count),
    }


def normalize_timestamp(series: pd.Series) -> Tuple[pd.Series, dict]:
    """
    Normalize timestamps to ISO8601 UTC naive string format.

    Handles:
    - ISO8601 with offset (2025-11-28 23:44:02+00:00)
    - Naive local timestamps (2025-11-30 01:19:00)
    """
    original = series.copy()

    # Parse with mixed format (handles both types)
    parsed = pd.to_datetime(series, format="mixed", errors="coerce", utc=True)

    # Convert to naive UTC (remove timezone info for consistent comparison)
    normalized = parsed.dt.tz_localize(None)

    # Convert to ISO string
    normalized_str = normalized.astype(str)

    null_count = normalized.isna().sum()

    return normalized_str, {
        "metric": "ts_normalized",
        "nulls_after": int(null_count),
    }


def normalize_signals(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Normalize signals (Phase 221) merge keys."""
    df = df.copy()
    metrics = {"name": "signals_normalized", "before": len(df), "operations": []}

    _log("Normalizing SIGNALS merge keys...")

    # 1. Normalize side (CE/PE → BUY/SELL)
    if "side" in df.columns:
        df["side"], op_metrics = normalize_side(df["side"])
        metrics["operations"].append(op_metrics)
        _log(f"  ✓ side: {op_metrics['changes']} changes")

    # 2. Normalize expiry (DDMMMYYYY → YYYY-MM-DD)
    if "expiry" in df.columns:
        df["expiry"], op_metrics = normalize_expiry(df["expiry"])
        metrics["operations"].append(op_metrics)
        _log(f"  ✓ expiry: normalized")

    # 3. Normalize ts (handle offset)
    if "ts" in df.columns:
        df["ts"], op_metrics = normalize_timestamp(df["ts"])
        metrics["operations"].append(op_metrics)
        _log(f"  ✓ ts: {op_metrics['nulls_after']} nulls")

    # 4. Normalize strike (float → int)
    if "strike" in df.columns:
        df["strike"], op_metrics = normalize_strike(df["strike"])
        metrics["operations"].append(op_metrics)
        _log(f"  ✓ strike: {op_metrics['changes']} changes to int")

    # 5. Normalize underlying
    if "underlying" in df.columns:
        df["underlying"], op_metrics = normalize_underlying(df["underlying"])
        metrics["operations"].append(op_metrics)
        _log(f"  ✓ underlying: {op_metrics['changes']} changes")

    metrics["after"] = len(df)
    return df, metrics


def normalize_orders(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    """Normalize orders (healed) merge keys."""
    df = df.copy()
    metrics = {"name": "orders_normalized", "before": len(df), "operations": []}

    _log("Normalizing ORDERS merge keys...")

    # 1. Side is already BUY/SELL — just uppercase/strip
    if "side" in df.columns:
        df["side"] = df["side"].astype(str).str.upper().str.strip()
        metrics["operations"].append({"metric": "side_clean", "action": "uppercase"})
        _log(f"  ✓ side: cleaned")

    # 2. Normalize expiry (already YYYY-MM-DD, just ensure format)
    if "expiry" in df.columns:
        df["expiry"], op_metrics = normalize_expiry(df["expiry"])
        metrics["operations"].append(op_metrics)
        _log(f"  ✓ expiry: normalized")

    # 3. Normalize ts (ensure naive UTC)
    if "ts" in df.columns:
        df["ts"], op_metrics = normalize_timestamp(df["ts"])
        metrics["operations"].append(op_metrics)
        _log(f"  ✓ ts: {op_metrics['nulls_after']} nulls")

    # 4. Normalize strike (float → int)
    if "strike" in df.columns:
        df["strike"], op_metrics = normalize_strike(df["strike"])
        metrics["operations"].append(op_metrics)
        _log(f"  ✓ strike: {op_metrics['changes']} changes to int")

    # 5. Normalize underlying
    if "underlying" in df.columns:
        df["underlying"], op_metrics = normalize_underlying(df["underlying"])
        metrics["operations"].append(op_metrics)
        _log(f"  ✓ underlying: {op_metrics['changes']} changes")

    metrics["after"] = len(df)
    return df, metrics


def validate_keys_alignment(signals: pd.DataFrame, orders: pd.DataFrame) -> Dict[str, Any]:
    """Validate that merge keys are aligned after normalization."""
    validation = {"status": "OK", "issues": []}

    merge_keys = ["ts", "underlying", "strike", "side", "expiry"]

    for key in merge_keys:
        if key not in signals.columns:
            validation["issues"].append(f"Signals missing {key}")
            validation["status"] = "ERROR"
            continue

        if key not in orders.columns:
            validation["issues"].append(f"Orders missing {key}")
            validation["status"] = "ERROR"
            continue

        sig_dtype = signals[key].dtype
        ord_dtype = orders[key].dtype

        if sig_dtype != ord_dtype:
            validation["issues"].append(f"{key}: type mismatch (signals={sig_dtype}, orders={ord_dtype})")
            validation["status"] = "WARN"

    return validation


def main():
    """Main entry point."""
    print(f"\n{'='*70}")
    print("MERGE KEY NORMALIZER - PHASE 239 PREPARATION")
    print(f"{'='*70}")

    # Load datasets
    signals_path = Path(__file__).parent.parent.parent / "storage" / "live" / "forward" / "phase221_forward_returns.csv"
    orders_path = (
        Path(__file__).parent.parent.parent / "storage" / "live" / "healed" / "dhan_virtual_orders_healed.csv"
    )

    if not signals_path.exists():
        print(f"❌ Signals not found: {signals_path}")
        return

    if not orders_path.exists():
        print(f"❌ Orders not found: {orders_path}")
        return

    df_signals = pd.read_csv(signals_path)
    df_orders = pd.read_csv(orders_path)

    # Normalize
    df_signals_norm, sig_metrics = normalize_signals(df_signals)
    df_orders_norm, ord_metrics = normalize_orders(df_orders)

    # Validate alignment
    validation = validate_keys_alignment(df_signals_norm, df_orders_norm)

    print(f"\n{'='*70}")
    print("VALIDATION RESULTS")
    print(f"{'='*70}")
    print(f"Status: {validation['status']}")
    if validation["issues"]:
        for issue in validation["issues"]:
            print(f"  ⚠️  {issue}")

    # Save normalized datasets
    print(f"\n{'='*70}")
    print("SAVING NORMALIZED DATASETS")
    print(f"{'='*70}")

    signals_norm_path = (
        Path(__file__).parent.parent.parent / "storage" / "live" / "forward" / "phase221_forward_returns_normalized.csv"
    )
    orders_norm_path = (
        Path(__file__).parent.parent.parent
        / "storage"
        / "live"
        / "healed"
        / "dhan_virtual_orders_healed_normalized.csv"
    )

    signals_norm_path.parent.mkdir(parents=True, exist_ok=True)
    orders_norm_path.parent.mkdir(parents=True, exist_ok=True)

    df_signals_norm.to_csv(signals_norm_path, index=False)
    df_orders_norm.to_csv(orders_norm_path, index=False)

    print(f"✓ Signals saved: {signals_norm_path}")
    print(f"✓ Orders saved: {orders_norm_path}")

    # Save metrics
    all_metrics = {
        "timestamp": datetime.now().isoformat(),
        "signals": sig_metrics,
        "orders": ord_metrics,
        "validation": validation,
    }

    metrics_path = Path(__file__).parent.parent.parent / "storage" / "metrics" / "merge_key_normalizer_metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2, default=str)

    print(f"✓ Metrics saved: {metrics_path}")

    print(f"\n{'='*70}")
    print("NORMALIZATION COMPLETE")
    print(f"{'='*70}")
    print(f"Signals: {sig_metrics['before']} → {sig_metrics['after']} rows")
    print(f"Orders: {ord_metrics['before']} → {ord_metrics['after']} rows")
    print(f"Ready for Phase 239 join")


if __name__ == "__main__":
    main()
