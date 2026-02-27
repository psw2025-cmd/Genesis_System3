"""
System3 Ultra - Shadow Real-Data Engine V1

Builds shadow learning datasets for Ultra profile using real signals, trade plans, PnL logs, outcomes.
All operations are shadow/experimental only - no changes to baseline.

Inputs:
- storage/live/angel_index_ai_signals.csv
- storage/live/angel_index_ai_trades_plan.csv
- storage/live/angel_index_ai_pnl_log.csv
- storage/learning/angel_index_real_master_dataset.parquet (optional)

Outputs:
- storage/learning_ultra/angel_ultra_shadow_master.parquet
- storage/learning_ultra/angel_ultra_shadow_master.csv

Menu Option: 73
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
LEARNING_ULTRA_DIR = PROJECT_ROOT / "storage" / "learning_ultra"

# Input files (from baseline)
SIGNALS_CSV = LIVE_DIR / "angel_index_ai_signals.csv"
TRADES_PLAN_CSV = LIVE_DIR / "angel_index_ai_trades_plan.csv"
PNL_LOG_CSV = LIVE_DIR / "angel_index_ai_pnl_log.csv"
REAL_MASTER_PARQUET = LEARNING_DIR / "angel_index_real_master_dataset.parquet"

# Output files (Ultra shadow)
SHADOW_PARQUET = LEARNING_ULTRA_DIR / "angel_ultra_shadow_master.parquet"
SHADOW_CSV = LEARNING_ULTRA_DIR / "angel_ultra_shadow_master.csv"

LEARNING_ULTRA_DIR.mkdir(parents=True, exist_ok=True)


def build_shadow_master() -> Dict[str, Any]:
    """
    Build shadow master dataset from available sources.

    Returns:
        Dict with build results and statistics
    """
    print("=== SYSTEM3 ULTRA - SHADOW REAL-DATA ENGINE V1 ===")
    print("[INFO] Building shadow master dataset for Ultra profile\n")
    print("[SAFETY] Shadow mode only - no changes to baseline\n")

    sources_found = []
    sources_missing = []

    # Load signals
    df_signals = None
    if SIGNALS_CSV.exists():
        try:
            df_signals = pd.read_csv(SIGNALS_CSV)
            sources_found.append("signals")
            print(f"[LOAD] Signals: {len(df_signals)} rows")
        except Exception as e:
            print(f"[WARN] Failed to load signals: {e}")
            sources_missing.append("signals")
    else:
        sources_missing.append("signals")

    # Load trade plans
    df_trades = None
    if TRADES_PLAN_CSV.exists():
        try:
            df_trades = pd.read_csv(TRADES_PLAN_CSV)
            sources_found.append("trades_plan")
            print(f"[LOAD] Trade plans: {len(df_trades)} rows")
        except Exception as e:
            print(f"[WARN] Failed to load trade plans: {e}")
            sources_missing.append("trades_plan")
    else:
        sources_missing.append("trades_plan")

    # Load PnL log
    df_pnl = None
    if PNL_LOG_CSV.exists():
        try:
            df_pnl = pd.read_csv(PNL_LOG_CSV)
            sources_found.append("pnl_log")
            print(f"[LOAD] PnL log: {len(df_pnl)} rows")
        except Exception as e:
            print(f"[WARN] Failed to load PnL log: {e}")
            sources_missing.append("pnl_log")
    else:
        sources_missing.append("pnl_log")

    # Load real master dataset (optional)
    df_master = None
    if REAL_MASTER_PARQUET.exists():
        try:
            df_master = pd.read_parquet(REAL_MASTER_PARQUET)
            sources_found.append("real_master")
            print(f"[LOAD] Real master dataset: {len(df_master)} rows")
        except Exception:
            # Try CSV fallback
            master_csv = LEARNING_DIR / "angel_index_real_master_dataset.csv"
            if master_csv.exists():
                try:
                    df_master = pd.read_csv(master_csv)
                    sources_found.append("real_master")
                    print(f"[LOAD] Real master dataset (CSV): {len(df_master)} rows")
                except Exception as e:
                    print(f"[WARN] Failed to load real master: {e}")

    if not sources_found:
        return {
            "status": "NO_DATA",
            "message": "No source files found. Cannot build shadow master dataset.",
            "sources_found": [],
            "sources_missing": sources_missing,
        }

    print(f"\n[INFO] Sources found: {', '.join(sources_found)}")
    if sources_missing:
        print(f"[INFO] Sources missing: {', '.join(sources_missing)}")

    # Build shadow master dataset
    shadow_rows = []

    # Strategy: Use trade plans as base (if available), then enrich
    if df_trades is not None and not df_trades.empty:
        for _, trade_row in df_trades.iterrows():
            shadow_row = _build_shadow_row_from_trade(trade_row, df_signals, df_pnl, df_master)
            if shadow_row:
                shadow_rows.append(shadow_row)
    elif df_signals is not None and not df_signals.empty:
        for _, signal_row in df_signals.iterrows():
            shadow_row = _build_shadow_row_from_signal(signal_row, df_trades, df_pnl, df_master)
            if shadow_row:
                shadow_rows.append(shadow_row)
    elif df_pnl is not None and not df_pnl.empty:
        for _, pnl_row in df_pnl.iterrows():
            shadow_row = _build_shadow_row_from_pnl(pnl_row, df_signals, df_trades, df_master)
            if shadow_row:
                shadow_rows.append(shadow_row)
    elif df_master is not None and not df_master.empty:
        for _, master_row in df_master.iterrows():
            shadow_row = _build_shadow_row_from_master(master_row)
            if shadow_row:
                shadow_rows.append(shadow_row)

    if not shadow_rows:
        return {
            "status": "EMPTY",
            "message": "No rows could be built from available sources",
            "sources_found": sources_found,
            "sources_missing": sources_missing,
        }

    # Create DataFrame
    df_shadow = pd.DataFrame(shadow_rows)

    # Ensure standard columns exist
    standard_cols = [
        "underlying",
        "strike",
        "side",
        "ts",
        "ltp",
        "spot",
        "signal",
        "pred_label",
        "score",
        "confidence",
        "sl_price",
        "tp_price",
        "exit_reason",
        "pnl_pct",
        "is_win",
        "is_loss",
        "is_misfire",
        "profile_source",
    ]

    # Add missing columns with NaN
    for col in standard_cols:
        if col not in df_shadow.columns:
            df_shadow[col] = np.nan

    # Compute is_win, is_loss, is_misfire if pnl_pct available
    if "pnl_pct" in df_shadow.columns:
        df_shadow["is_win"] = (df_shadow["pnl_pct"] > 0).astype(int)
        df_shadow["is_loss"] = (df_shadow["pnl_pct"] < 0).astype(int)
        df_shadow["is_misfire"] = 0  # Will be computed if signal vs outcome mismatch

    # Compute is_misfire (signal vs outcome mismatch)
    if "signal" in df_shadow.columns and "pred_label" in df_shadow.columns:
        # Misfire: signal was BUY_CE but outcome was loss, or signal was HOLD but there was a big move
        # Simplified: if signal != pred_label and pnl < 0, it's a misfire
        if "pnl_pct" in df_shadow.columns:
            signal_mismatch = df_shadow["signal"] != df_shadow["pred_label"]
            negative_pnl = df_shadow["pnl_pct"] < 0
            df_shadow["is_misfire"] = (signal_mismatch & negative_pnl).astype(int)

    # Set profile_source
    df_shadow["profile_source"] = "BASELINE"

    # Reorder columns (standard first, then others)
    other_cols = [c for c in df_shadow.columns if c not in standard_cols]
    df_shadow = df_shadow[standard_cols + other_cols]

    # Save
    try:
        # Save as CSV (always works)
        df_shadow.to_csv(SHADOW_CSV, index=False)
        print(f"[SAVE] Shadow master CSV: {SHADOW_CSV} ({len(df_shadow)} rows)")

        # Save as Parquet (optional)
        try:
            df_shadow.to_parquet(SHADOW_PARQUET, index=False, engine="pyarrow")
            print(f"[SAVE] Shadow master Parquet: {SHADOW_PARQUET} ({len(df_shadow)} rows)")
        except ImportError:
            print(f"[WARN] Parquet save skipped: pyarrow not installed. CSV saved successfully.")
        except Exception as e:
            print(f"[WARN] Parquet save failed: {e}. CSV saved successfully.")

        return {
            "status": "SUCCESS",
            "sources_found": sources_found,
            "sources_missing": sources_missing,
            "total_rows": len(df_shadow),
            "parquet_path": str(SHADOW_PARQUET),
            "csv_path": str(SHADOW_CSV),
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Failed to save shadow master dataset: {e}",
            "sources_found": sources_found,
        }


def _build_shadow_row_from_trade(
    trade_row: pd.Series,
    df_signals: Optional[pd.DataFrame],
    df_pnl: Optional[pd.DataFrame],
    df_master: Optional[pd.DataFrame],
) -> Optional[Dict[str, Any]]:
    """Build shadow row from trade plan."""
    row = {
        "underlying": trade_row.get("underlying", np.nan),
        "strike": trade_row.get("strike", np.nan),
        "side": trade_row.get("side", trade_row.get("action", np.nan)),
        "ts": trade_row.get("timestamp", trade_row.get("ts", np.nan)),
        "ltp": trade_row.get("entry_price", trade_row.get("suggested_entry", np.nan)),
        "spot": trade_row.get("spot", np.nan),
        "signal": trade_row.get("pred_label", trade_row.get("signal", np.nan)),
        "pred_label": trade_row.get("pred_label", trade_row.get("signal", np.nan)),
        "confidence": trade_row.get("confidence", np.nan),
        "score": trade_row.get("score", np.nan),
        "sl_price": trade_row.get("suggested_stoploss", np.nan),
        "tp_price": trade_row.get("suggested_target", np.nan),
    }

    # Enrich with signals
    if df_signals is not None:
        match = _find_matching_row(trade_row, df_signals, ["underlying", "strike"])
        if match is not None:
            row["signal"] = match.get("pred_label", match.get("signal", row["signal"]))
            if pd.isna(row["confidence"]):
                row["confidence"] = match.get("pred_confidence", np.nan)
            if pd.isna(row["score"]):
                row["score"] = match.get("expected_move_score", np.nan)

    # Enrich with PnL
    if df_pnl is not None:
        match = _find_matching_row(trade_row, df_pnl, ["underlying", "strike"])
        if match is not None:
            row["exit_reason"] = match.get("exit_reason", match.get("reason", np.nan))
            row["pnl_pct"] = match.get("pnl_pct", np.nan)

    # Enrich with master dataset
    if df_master is not None:
        match = _find_matching_row(trade_row, df_master, ["underlying", "strike"])
        if match is not None:
            if pd.isna(row["pnl_pct"]):
                row["pnl_pct"] = match.get("pnl_pct", np.nan)
            if pd.isna(row["exit_reason"]):
                row["exit_reason"] = match.get("exit_reason", np.nan)

    return row


def _build_shadow_row_from_signal(
    signal_row: pd.Series,
    df_trades: Optional[pd.DataFrame],
    df_pnl: Optional[pd.DataFrame],
    df_master: Optional[pd.DataFrame],
) -> Optional[Dict[str, Any]]:
    """Build shadow row from signal."""
    row = {
        "underlying": signal_row.get("underlying", np.nan),
        "strike": signal_row.get("strike", np.nan),
        "side": signal_row.get("side", np.nan),
        "ts": signal_row.get("timestamp", signal_row.get("ts", np.nan)),
        "ltp": signal_row.get("ltp", np.nan),
        "spot": signal_row.get("spot", np.nan),
        "signal": signal_row.get("pred_label", signal_row.get("signal", np.nan)),
        "pred_label": signal_row.get("pred_label", signal_row.get("signal", np.nan)),
        "confidence": signal_row.get("pred_confidence", signal_row.get("confidence", np.nan)),
        "score": signal_row.get("expected_move_score", signal_row.get("score", np.nan)),
    }

    # Enrich with trades, PnL, master
    if df_trades is not None:
        match = _find_matching_row(signal_row, df_trades, ["underlying", "strike"])
        if match is not None:
            row["sl_price"] = match.get("suggested_stoploss", np.nan)
            row["tp_price"] = match.get("suggested_target", np.nan)

    if df_pnl is not None:
        match = _find_matching_row(signal_row, df_pnl, ["underlying", "strike"])
        if match is not None:
            row["exit_reason"] = match.get("exit_reason", np.nan)
            row["pnl_pct"] = match.get("pnl_pct", np.nan)

    if df_master is not None:
        match = _find_matching_row(signal_row, df_master, ["underlying", "strike"])
        if match is not None:
            if pd.isna(row["pnl_pct"]):
                row["pnl_pct"] = match.get("pnl_pct", np.nan)

    return row


def _build_shadow_row_from_pnl(
    pnl_row: pd.Series,
    df_signals: Optional[pd.DataFrame],
    df_trades: Optional[pd.DataFrame],
    df_master: Optional[pd.DataFrame],
) -> Optional[Dict[str, Any]]:
    """Build shadow row from PnL log."""
    row = {
        "underlying": pnl_row.get("underlying", np.nan),
        "strike": pnl_row.get("strike", np.nan),
        "side": pnl_row.get("side", np.nan),
        "ts": pnl_row.get("entry_timestamp", pnl_row.get("timestamp", np.nan)),
        "ltp": pnl_row.get("entry_price", np.nan),
        "spot": pnl_row.get("spot", np.nan),
        "exit_reason": pnl_row.get("exit_reason", np.nan),
        "pnl_pct": pnl_row.get("pnl_pct", np.nan),
    }

    # Enrich with signals, trades, master
    if df_signals is not None:
        match = _find_matching_row(pnl_row, df_signals, ["underlying", "strike"])
        if match is not None:
            row["signal"] = match.get("pred_label", np.nan)
            row["pred_label"] = match.get("pred_label", np.nan)
            row["confidence"] = match.get("pred_confidence", np.nan)
            row["score"] = match.get("expected_move_score", np.nan)

    if df_trades is not None:
        match = _find_matching_row(pnl_row, df_trades, ["underlying", "strike"])
        if match is not None:
            row["sl_price"] = match.get("suggested_stoploss", np.nan)
            row["tp_price"] = match.get("suggested_target", np.nan)

    if df_master is not None:
        match = _find_matching_row(pnl_row, df_master, ["underlying", "strike"])
        if match is not None:
            if pd.isna(row["signal"]):
                row["signal"] = match.get("signal_label", np.nan)

    return row


def _build_shadow_row_from_master(master_row: pd.Series) -> Optional[Dict[str, Any]]:
    """Build shadow row from master dataset."""
    return {
        "underlying": master_row.get("underlying", np.nan),
        "strike": master_row.get("strike", np.nan),
        "side": master_row.get("side", np.nan),
        "ts": master_row.get("ts_entry", master_row.get("ts", np.nan)),
        "ltp": master_row.get("entry_ltp", master_row.get("entry_price", np.nan)),
        "spot": master_row.get("spot", np.nan),
        "signal": master_row.get("signal_label", master_row.get("pred_label", np.nan)),
        "pred_label": master_row.get("pred_label", np.nan),
        "confidence": master_row.get("confidence", np.nan),
        "score": master_row.get("score", np.nan),
        "exit_reason": master_row.get("exit_reason", np.nan),
        "pnl_pct": master_row.get("pnl_pct", np.nan),
    }


def _find_matching_row(
    row: pd.Series,
    df: pd.DataFrame,
    match_cols: list[str],
) -> Optional[pd.Series]:
    """Find matching row in DataFrame."""
    if df.empty or not match_cols:
        return None

    matches = df.copy()
    for col in match_cols:
        if col in df.columns and col in row.index:
            val = row.get(col)
            if pd.notna(val):
                matches = matches[matches[col] == val]
            else:
                return None

    return matches.iloc[0] if not matches.empty else None


def main() -> None:
    """Main entry point."""
    result = build_shadow_master()

    if result["status"] == "SUCCESS":
        print(f"\n=== BUILD SUMMARY ===")
        print(f"Sources Found: {', '.join(result['sources_found'])}")
        if result.get("sources_missing"):
            print(f"Sources Missing: {', '.join(result['sources_missing'])}")
        print(f"Total Rows: {result['total_rows']}")
        print(f"CSV: {result['csv_path']}")
        if "parquet_path" in result:
            print(f"Parquet: {result['parquet_path']}")
        print("\n✅ Shadow master dataset built successfully")
    else:
        print(f"\n[INFO] {result.get('message', 'Build not completed')}")


if __name__ == "__main__":
    main()
