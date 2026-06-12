"""
Dhan Index Options - Real Master Dataset Builder

Consolidates live signals, trade plans, PnL outcomes, and real outcome logs
into a single, canonical master dataset for training and analysis.

Mode: READ/WRITE, but only into /storage/learning/ (no changes to baseline training CSV).

Inputs:
- storage/live/dhan_index_ai_signals.csv
- storage/live/dhan_index_ai_trades_plan.csv
- storage/live/dhan_index_ai_pnl_log.csv
- storage/learning/real_outcomes.csv (if exists)

Outputs:
- storage/learning/dhan_index_real_master_dataset.parquet
- storage/learning/dhan_index_real_master_dataset.csv

Environment/Config: None required. Handles missing files gracefully.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
TRAINING_DIR = PROJECT_ROOT / "storage" / "training"

# Input files
SIGNALS_CSV = LIVE_DIR / "dhan_index_ai_signals.csv"
TRADES_PLAN_CSV = LIVE_DIR / "dhan_index_ai_trades_plan.csv"
PNL_LOG_CSV = LIVE_DIR / "dhan_index_ai_pnl_log.csv"
REAL_OUTCOMES_CSV = LEARNING_DIR / "real_outcomes.csv"

# Output files
MASTER_PARQUET = LEARNING_DIR / "dhan_index_real_master_dataset.parquet"
MASTER_CSV = LEARNING_DIR / "dhan_index_real_master_dataset.csv"

LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def build_master_dataset() -> Dict[str, Any]:
    """
    Build master dataset from available sources.

    Handles missing files gracefully.

    Returns:
        Dict with build results and statistics
    """
    print("=== ANGEL ONE INDEX OPTIONS - REAL MASTER DATASET BUILDER ===")
    print("[INFO] Building master dataset from available sources\n")

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

    # Load real outcomes
    df_outcomes = None
    if REAL_OUTCOMES_CSV.exists():
        try:
            df_outcomes = pd.read_csv(REAL_OUTCOMES_CSV)
            sources_found.append("real_outcomes")
            print(f"[LOAD] Real outcomes: {len(df_outcomes)} rows")
        except Exception as e:
            print(f"[WARN] Failed to load real outcomes: {e}")
            sources_missing.append("real_outcomes")
    else:
        sources_missing.append("real_outcomes")

    if not sources_found:
        return {
            "status": "NO_DATA",
            "message": "No source files found. Cannot build master dataset.",
            "sources_found": [],
            "sources_missing": sources_missing,
        }

    print(f"\n[INFO] Sources found: {', '.join(sources_found)}")
    if sources_missing:
        print(f"[INFO] Sources missing: {', '.join(sources_missing)}")

    # Build master dataset
    master_rows = []

    # Strategy: Start with trade plans as base (if available)
    # Then enrich with signals, PnL, and outcomes
    if df_trades is not None and not df_trades.empty:
        # Use trades as base
        for _, trade_row in df_trades.iterrows():
            master_row = _build_row_from_trade(trade_row, df_signals, df_pnl, df_outcomes)
            if master_row:
                master_rows.append(master_row)
    elif df_signals is not None and not df_signals.empty:
        # Fallback: use signals as base
        for _, signal_row in df_signals.iterrows():
            master_row = _build_row_from_signal(signal_row, df_trades, df_pnl, df_outcomes)
            if master_row:
                master_rows.append(master_row)
    elif df_pnl is not None and not df_pnl.empty:
        # Fallback: use PnL log as base
        for _, pnl_row in df_pnl.iterrows():
            master_row = _build_row_from_pnl(pnl_row, df_signals, df_trades, df_outcomes)
            if master_row:
                master_rows.append(master_row)
    elif df_outcomes is not None and not df_outcomes.empty:
        # Fallback: use outcomes as base
        for _, outcome_row in df_outcomes.iterrows():
            master_row = _build_row_from_outcome(outcome_row, df_signals, df_trades, df_pnl)
            if master_row:
                master_rows.append(master_row)

    if not master_rows:
        return {
            "status": "EMPTY",
            "message": "No rows could be built from available sources",
            "sources_found": sources_found,
            "sources_missing": sources_missing,
        }

    # Create DataFrame
    df_master = pd.DataFrame(master_rows)

    # Ensure standard columns exist
    standard_cols = [
        "ts_entry",
        "ts_exit",
        "underlying",
        "expiry",
        "strike",
        "side",
        "signal_label",
        "pred_label",
        "true_label",
        "confidence",
        "score",
        "entry_ltp",
        "exit_ltp",
        "pnl_pct",
        "exit_reason",
        "market_regime",
        "vol_regime",
    ]

    # Add missing columns with NaN
    for col in standard_cols:
        if col not in df_master.columns:
            df_master[col] = np.nan

    # Reorder columns (standard first, then others)
    other_cols = [c for c in df_master.columns if c not in standard_cols]
    df_master = df_master[standard_cols + other_cols]

    # Save
    try:
        # Save as CSV (always works)
        df_master.to_csv(MASTER_CSV, index=False)
        print(f"[SAVE] Master dataset (CSV): {MASTER_CSV} ({len(df_master)} rows)")

        # Save as Parquet (optional, requires pyarrow)
        try:
            df_master.to_parquet(MASTER_PARQUET, index=False, engine="pyarrow")
            print(f"[SAVE] Master dataset (Parquet): {MASTER_PARQUET} ({len(df_master)} rows)")
        except ImportError:
            print(f"[WARN] Parquet save skipped: pyarrow not installed. CSV saved successfully.")
        except Exception as e:
            print(f"[WARN] Parquet save failed: {e}. CSV saved successfully.")

        return {
            "status": "SUCCESS",
            "sources_found": sources_found,
            "sources_missing": sources_missing,
            "total_rows": len(df_master),
            "parquet_path": str(MASTER_PARQUET),
            "csv_path": str(MASTER_CSV),
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Failed to save master dataset: {e}",
            "sources_found": sources_found,
        }


def _build_row_from_trade(
    trade_row: pd.Series,
    df_signals: Optional[pd.DataFrame],
    df_pnl: Optional[pd.DataFrame],
    df_outcomes: Optional[pd.DataFrame],
) -> Optional[Dict[str, Any]]:
    """Build master row from trade plan."""
    row = {
        "ts_entry": trade_row.get("timestamp", trade_row.get("ts", np.nan)),
        "underlying": trade_row.get("underlying", np.nan),
        "expiry": trade_row.get("expiry", np.nan),
        "strike": trade_row.get("strike", np.nan),
        "side": trade_row.get("side", trade_row.get("action", np.nan)),
        "entry_ltp": trade_row.get("entry_price", trade_row.get("suggested_entry", np.nan)),
        "confidence": trade_row.get("confidence", np.nan),
        "score": trade_row.get("score", np.nan),
        "pred_label": trade_row.get("pred_label", trade_row.get("signal", np.nan)),
    }

    # Enrich with signals if available
    if df_signals is not None and not df_signals.empty:
        # Try to match by underlying, strike, timestamp
        match = _find_matching_signal(trade_row, df_signals)
        if match is not None:
            row["signal_label"] = match.get("pred_label", match.get("signal", np.nan))
            if pd.isna(row["confidence"]):
                row["confidence"] = match.get("pred_confidence", np.nan)
            if pd.isna(row["score"]):
                row["score"] = match.get("expected_move_score", np.nan)

    # Enrich with PnL if available
    if df_pnl is not None and not df_pnl.empty:
        match = _find_matching_pnl(trade_row, df_pnl)
        if match is not None:
            row["ts_exit"] = match.get("exit_timestamp", match.get("timestamp", np.nan))
            row["exit_ltp"] = match.get("exit_price", match.get("exit_ltp", np.nan))
            row["pnl_pct"] = match.get("pnl_pct", np.nan)
            row["exit_reason"] = match.get("exit_reason", match.get("reason", np.nan))

    # Enrich with outcomes if available
    if df_outcomes is not None and not df_outcomes.empty:
        match = _find_matching_outcome(trade_row, df_outcomes)
        if match is not None:
            row["true_label"] = match.get("true_label", match.get("outcome_label", np.nan))
            if pd.isna(row["pnl_pct"]):
                row["pnl_pct"] = match.get("pnl_pct", np.nan)
            if pd.isna(row["exit_reason"]):
                row["exit_reason"] = match.get("exit_reason", match.get("reason_exit", np.nan))
            row["market_regime"] = match.get("market_regime", match.get("regime", np.nan))
            row["vol_regime"] = match.get("vol_regime", np.nan)

    return row


def _build_row_from_signal(
    signal_row: pd.Series,
    df_trades: Optional[pd.DataFrame],
    df_pnl: Optional[pd.DataFrame],
    df_outcomes: Optional[pd.DataFrame],
) -> Optional[Dict[str, Any]]:
    """Build master row from signal."""
    row = {
        "ts_entry": signal_row.get("timestamp", signal_row.get("ts", np.nan)),
        "underlying": signal_row.get("underlying", np.nan),
        "expiry": signal_row.get("expiry", np.nan),
        "strike": signal_row.get("strike", np.nan),
        "side": signal_row.get("side", np.nan),
        "signal_label": signal_row.get("pred_label", signal_row.get("signal", np.nan)),
        "pred_label": signal_row.get("pred_label", signal_row.get("signal", np.nan)),
        "confidence": signal_row.get("pred_confidence", signal_row.get("confidence", np.nan)),
        "score": signal_row.get("expected_move_score", signal_row.get("score", np.nan)),
    }

    # Enrich with trades, PnL, outcomes (similar logic)
    if df_trades is not None:
        match = _find_matching_trade(signal_row, df_trades)
        if match is not None:
            row["entry_ltp"] = match.get("entry_price", match.get("suggested_entry", np.nan))

    if df_pnl is not None:
        match = _find_matching_pnl(signal_row, df_pnl)
        if match is not None:
            row["ts_exit"] = match.get("exit_timestamp", match.get("timestamp", np.nan))
            row["exit_ltp"] = match.get("exit_price", np.nan)
            row["pnl_pct"] = match.get("pnl_pct", np.nan)
            row["exit_reason"] = match.get("exit_reason", np.nan)

    if df_outcomes is not None:
        match = _find_matching_outcome(signal_row, df_outcomes)
        if match is not None:
            row["true_label"] = match.get("true_label", np.nan)
            row["market_regime"] = match.get("market_regime", np.nan)

    return row


def _build_row_from_pnl(
    pnl_row: pd.Series,
    df_signals: Optional[pd.DataFrame],
    df_trades: Optional[pd.DataFrame],
    df_outcomes: Optional[pd.DataFrame],
) -> Optional[Dict[str, Any]]:
    """Build master row from PnL log."""
    row = {
        "ts_entry": pnl_row.get("entry_timestamp", pnl_row.get("timestamp", np.nan)),
        "ts_exit": pnl_row.get("exit_timestamp", pnl_row.get("timestamp", np.nan)),
        "underlying": pnl_row.get("underlying", np.nan),
        "expiry": pnl_row.get("expiry", np.nan),
        "strike": pnl_row.get("strike", np.nan),
        "side": pnl_row.get("side", np.nan),
        "entry_ltp": pnl_row.get("entry_price", np.nan),
        "exit_ltp": pnl_row.get("exit_price", np.nan),
        "pnl_pct": pnl_row.get("pnl_pct", np.nan),
        "exit_reason": pnl_row.get("exit_reason", np.nan),
    }

    # Enrich with signals, trades, outcomes
    if df_signals is not None:
        match = _find_matching_signal(pnl_row, df_signals)
        if match is not None:
            row["signal_label"] = match.get("pred_label", np.nan)
            row["confidence"] = match.get("pred_confidence", np.nan)
            row["score"] = match.get("expected_move_score", np.nan)

    if df_trades is not None:
        match = _find_matching_trade(pnl_row, df_trades)
        if match is not None:
            row["pred_label"] = match.get("pred_label", np.nan)

    if df_outcomes is not None:
        match = _find_matching_outcome(pnl_row, df_outcomes)
        if match is not None:
            row["true_label"] = match.get("true_label", np.nan)
            row["market_regime"] = match.get("market_regime", np.nan)

    return row


def _build_row_from_outcome(
    outcome_row: pd.Series,
    df_signals: Optional[pd.DataFrame],
    df_trades: Optional[pd.DataFrame],
    df_pnl: Optional[pd.DataFrame],
) -> Optional[Dict[str, Any]]:
    """Build master row from outcome log."""
    row = {
        "ts_entry": outcome_row.get("entry_timestamp", outcome_row.get("timestamp", np.nan)),
        "ts_exit": outcome_row.get("exit_timestamp", outcome_row.get("timestamp", np.nan)),
        "underlying": outcome_row.get("underlying", np.nan),
        "expiry": outcome_row.get("expiry", np.nan),
        "strike": outcome_row.get("strike", np.nan),
        "side": outcome_row.get("side", np.nan),
        "true_label": outcome_row.get("true_label", outcome_row.get("outcome_label", np.nan)),
        "entry_ltp": outcome_row.get("entry_price", np.nan),
        "exit_ltp": outcome_row.get("exit_price", np.nan),
        "pnl_pct": outcome_row.get("pnl_pct", np.nan),
        "exit_reason": outcome_row.get("exit_reason", outcome_row.get("reason_exit", np.nan)),
        "market_regime": outcome_row.get("market_regime", outcome_row.get("regime", np.nan)),
        "vol_regime": outcome_row.get("vol_regime", np.nan),
    }

    # Enrich with signals, trades, PnL
    if df_signals is not None:
        match = _find_matching_signal(outcome_row, df_signals)
        if match is not None:
            row["signal_label"] = match.get("pred_label", np.nan)
            row["confidence"] = match.get("pred_confidence", np.nan)
            row["score"] = match.get("expected_move_score", np.nan)

    if df_trades is not None:
        match = _find_matching_trade(outcome_row, df_trades)
        if match is not None:
            row["pred_label"] = match.get("pred_label", np.nan)

    if df_pnl is not None:
        match = _find_matching_pnl(outcome_row, df_pnl)
        if match is not None:
            if pd.isna(row["pnl_pct"]):
                row["pnl_pct"] = match.get("pnl_pct", np.nan)

    return row


def _find_matching_signal(row: pd.Series, df_signals: pd.DataFrame) -> Optional[pd.Series]:
    """Find matching signal row."""
    # Try to match by underlying, strike, and timestamp proximity
    if "underlying" not in df_signals.columns or "underlying" not in row.index:
        return None

    matches = df_signals[df_signals["underlying"] == row.get("underlying", None)]
    if matches.empty:
        return None

    if "strike" in df_signals.columns and "strike" in row.index:
        matches = matches[matches["strike"] == row.get("strike", None)]
        if matches.empty:
            return None

    # Return first match (or closest by timestamp if available)
    return matches.iloc[0] if not matches.empty else None


def _find_matching_trade(row: pd.Series, df_trades: pd.DataFrame) -> Optional[pd.Series]:
    """Find matching trade plan row."""
    if "underlying" not in df_trades.columns or "underlying" not in row.index:
        return None

    matches = df_trades[df_trades["underlying"] == row.get("underlying", None)]
    if matches.empty:
        return None

    if "strike" in df_trades.columns and "strike" in row.index:
        matches = matches[matches["strike"] == row.get("strike", None)]

    return matches.iloc[0] if not matches.empty else None


def _find_matching_pnl(row: pd.Series, df_pnl: pd.DataFrame) -> Optional[pd.Series]:
    """Find matching PnL log row."""
    if "underlying" not in df_pnl.columns or "underlying" not in row.index:
        return None

    matches = df_pnl[df_pnl["underlying"] == row.get("underlying", None)]
    if matches.empty:
        return None

    if "strike" in df_pnl.columns and "strike" in row.index:
        matches = matches[matches["strike"] == row.get("strike", None)]

    return matches.iloc[0] if not matches.empty else None


def _find_matching_outcome(row: pd.Series, df_outcomes: pd.DataFrame) -> Optional[pd.Series]:
    """Find matching outcome row."""
    if "underlying" not in df_outcomes.columns or "underlying" not in row.index:
        return None

    matches = df_outcomes[df_outcomes["underlying"] == row.get("underlying", None)]
    if matches.empty:
        return None

    if "strike" in df_outcomes.columns and "strike" in row.index:
        matches = matches[matches["strike"] == row.get("strike", None)]

    return matches.iloc[0] if not matches.empty else None


def main() -> None:
    """Main entry point."""
    result = build_master_dataset()

    if result["status"] == "SUCCESS":
        print(f"\n=== BUILD SUMMARY ===")
        print(f"Sources Found: {', '.join(result['sources_found'])}")
        if result.get("sources_missing"):
            print(f"Sources Missing: {', '.join(result['sources_missing'])}")
        print(f"Total Rows: {result['total_rows']}")
        print(f"Parquet: {result['parquet_path']}")
        print(f"CSV: {result['csv_path']}")
        print("\n✅ Master dataset built successfully")
    else:
        print(f"\n[INFO] {result.get('message', 'Build not completed')}")


if __name__ == "__main__":
    main()
