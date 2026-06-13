"""
System3 Ultra - Phase 34: Ultra Live Shadow Comparison

Run Ultra decisions in shadow, side-by-side with baseline.
Baseline still controls DRY RUN trades.
Ultra decisions are logged separately as shadow trades, never executed.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 97
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)
LIVE_DIR.mkdir(parents=True, exist_ok=True)


def _load_latest_signals() -> Optional[pd.DataFrame]:
    """Load latest signals CSV."""
    signals_csv = LIVE_DIR / "dhan_index_ai_signals.csv"
    if not signals_csv.exists():
        return None
    try:
        df = pd.read_csv(signals_csv)
        if df.empty:
            return None
        # Get last snapshot (group by timestamp and take most recent)
        if "timestamp" in df.columns:
            latest_ts = df["timestamp"].max()
            return df[df["timestamp"] == latest_ts].copy()
        return df.tail(30).copy()  # Fallback: last 30 rows
    except Exception:
        return None


def _load_ultra_decisions() -> Optional[pd.DataFrame]:
    """Load Ultra fused decisions."""
    ultra_csv = ULTRA_DIR / "phase31_ultra_fused_decisions.csv"
    if not ultra_csv.exists():
        return None
    try:
        df = pd.read_csv(ultra_csv)
        if df.empty:
            return None
        # Get latest decisions
        if "timestamp" in df.columns:
            latest_ts = df["timestamp"].max()
            return df[df["timestamp"] == latest_ts].copy()
        return df.tail(30).copy()
    except Exception:
        return None


def run_phase34_shadow_once() -> str:
    """
    Run Phase 34: Ultra Shadow Execution (one-shot).

    Returns:
        Path to shadow trades CSV
    """
    print("=== SYSTEM3 ULTRA - PHASE 34: ULTRA LIVE SHADOW COMPARISON ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only")
    print("[SAFETY] Shadow trades are logged but NEVER executed\n")

    # Load latest signals
    df_signals = _load_latest_signals()
    if df_signals is None or df_signals.empty:
        print("[PHASE 34][ERROR] No live signals found")
        error_path = ULTRA_DIR / "phase34_error_no_signals.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write("# Phase 34 Error\n\nNo live signals found\n")
        return str(error_path)

    print(f"[LOAD] Loaded {len(df_signals)} signals")

    # Load Ultra decisions
    df_ultra = _load_ultra_decisions()
    if df_ultra is None or df_ultra.empty:
        print("[PHASE 34][WARN] No Ultra decisions found. Run Phase 31 first.")
        error_path = ULTRA_DIR / "phase34_error_no_ultra.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write("# Phase 34 Error\n\nNo Ultra decisions found. Run Phase 31 first.\n")
        return str(error_path)

    print(f"[LOAD] Loaded {len(df_ultra)} Ultra decisions")

    # Create shadow trades
    shadow_trades = []
    timestamp = datetime.utcnow().isoformat()

    for _, ultra_row in df_ultra.iterrows():
        final_action = ultra_row.get("final_action", "HOLD")
        final_risk_flag = ultra_row.get("final_risk_flag", "RISKY")

        # Only create shadow trade if action is BUY and risk is SAFE
        if final_action in ["BUY_CE", "STRONG_BUY_CE", "BUY_PE", "STRONG_BUY_PE"] and final_risk_flag == "SAFE":
            shadow_trade = {
                "timestamp": timestamp,
                "underlying": ultra_row.get("underlying", ""),
                "strike": ultra_row.get("strike", np.nan),
                "side": ultra_row.get("side", ""),
                "action": final_action,
                "size": ultra_row.get("final_size", 0.0),
                "reason": "ULTRA_SHADOW",
                "ltp": ultra_row.get("ltp", np.nan),
                "spot": ultra_row.get("spot", np.nan),
                "confidence": ultra_row.get("confidence", np.nan),
                "score": ultra_row.get("score", np.nan),
                "sl_pct": ultra_row.get("sl_pct", np.nan),
                "tp_pct": ultra_row.get("tp_pct", np.nan),
            }
            shadow_trades.append(shadow_trade)

    if not shadow_trades:
        print("[INFO] No shadow trades generated (no BUY actions with SAFE risk flag)")
        # Still create empty file
        df_shadow = pd.DataFrame()
    else:
        df_shadow = pd.DataFrame(shadow_trades)
        print(f"[GENERATE] Generated {len(df_shadow)} shadow trades")

    # Append to shadow CSV
    shadow_csv = LIVE_DIR / "dhan_index_ai_ultra_trades_shadow.csv"
    write_header = not shadow_csv.exists()

    if not df_shadow.empty:
        df_shadow.to_csv(
            shadow_csv,
            mode="a",
            header=write_header,
            index=False,
        )
        print(f"[SAVE] Shadow trades appended to: {shadow_csv}")
    else:
        # Create empty file with header if it doesn't exist
        if not shadow_csv.exists():
            df_empty = pd.DataFrame(
                columns=[
                    "timestamp",
                    "underlying",
                    "strike",
                    "side",
                    "action",
                    "size",
                    "reason",
                    "ltp",
                    "spot",
                    "confidence",
                    "score",
                    "sl_pct",
                    "tp_pct",
                ]
            )
            df_empty.to_csv(shadow_csv, index=False)
            print(f"[SAVE] Created empty shadow trades file: {shadow_csv}")

    print("\n[OK] Phase 34 Ultra Shadow Execution completed")
    print("[SAFETY] Shadow trades logged but NOT executed")
    return str(shadow_csv)


def main() -> None:
    """Main entry point for CLI use."""
    try:
        path = run_phase34_shadow_once()
        print(f"\n[PHASE 34] Output written to: {path}")
    except Exception as e:
        print(f"[PHASE 34][ERROR] {e}")
        error_path = ULTRA_DIR / "phase34_error.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write(f"# Phase 34 Error\n\n{str(e)}\n")
        print(f"[PHASE 34] Error details saved to: {error_path}")


if __name__ == "__main__":
    main()
