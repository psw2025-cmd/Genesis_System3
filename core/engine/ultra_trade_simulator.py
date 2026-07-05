"""
System3 Ultra - Trade Simulator (Shadow, Offline)

Simulates Ultra-only trades on historical snapshots, offline.
Shadow mode only - no real trades.

Inputs:
- Historical signals / snapshots
- Ultra models

Outputs:
- storage/ultra/dhan_ultra_trade_plan_sim.csv
- storage/ultra/dhan_ultra_pnl_sim.csv
- storage/reports_ultra/ultra_trade_sim_summary.csv

Menu Option: 81
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"
LEARNING_ULTRA_DIR = PROJECT_ROOT / "storage" / "learning_ultra"

SHADOW_SIGNALS_CSV = ULTRA_DIR / "dhan_ultra_live_shadow_signals.csv"
SHADOW_MASTER_PARQUET = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.parquet"
SHADOW_MASTER_CSV = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.csv"

TRADE_PLAN_SIM_CSV = ULTRA_DIR / "dhan_ultra_trade_plan_sim.csv"
PNL_SIM_CSV = ULTRA_DIR / "dhan_ultra_pnl_sim.csv"
SUMMARY_CSV = REPORTS_ULTRA_DIR / "ultra_trade_sim_summary.csv"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def simulate_ultra_trades() -> Dict[str, Any]:
    """
    Simulate Ultra-only trades on historical data.

    Returns:
        Dict with simulation results
    """
    print("=== SYSTEM3 ULTRA - TRADE SIMULATOR (SHADOW) ===")
    print("[INFO] Simulating Ultra trades on historical snapshots\n")
    print("[SAFETY] Shadow mode only - offline simulation\n")

    # Load shadow signals or master dataset
    df_signals = None
    if SHADOW_SIGNALS_CSV.exists():
        try:
            df_signals = pd.read_csv(SHADOW_SIGNALS_CSV)
            print(f"[LOAD] Shadow signals: {len(df_signals)} rows")
        except Exception as e:
            print(f"[WARN] Failed to load shadow signals: {e}")
    elif SHADOW_MASTER_PARQUET.exists():
        try:
            df_signals = pd.read_parquet(SHADOW_MASTER_PARQUET)
            print(f"[LOAD] Shadow master (Parquet): {len(df_signals)} rows")
        except Exception:
            if SHADOW_MASTER_CSV.exists():
                df_signals = pd.read_csv(SHADOW_MASTER_CSV)
                print(f"[LOAD] Shadow master (CSV): {len(df_signals)} rows")

    if df_signals is None or df_signals.empty:
        return {
            "status": "NO_DATA",
            "message": "No shadow signals or master dataset found",
        }

    # Filter for Ultra predictions (use ultra_pred if available, else use signal)
    if "ultra_pred" in df_signals.columns:
        df_trades = df_signals[
            (df_signals["ultra_pred"].isin(["BUY_CE", "BUY_PE"])) & (df_signals["ultra_conf"] >= 0.70)  # Threshold
        ].copy()
    else:
        df_trades = df_signals[
            (df_signals["signal"].isin(["BUY_CE", "BUY_PE"])) & (df_signals.get("confidence", 0) >= 0.70)
        ].copy()

    if df_trades.empty:
        return {
            "status": "NO_TRADES",
            "message": "No eligible trades found",
        }

    print(f"[FILTER] Eligible trades: {len(df_trades)}")

    # Generate trade plans
    trade_plans = []
    for _, row in df_trades.iterrows():
        entry_price = row.get("ltp", row.get("entry_price", np.nan))
        if pd.isna(entry_price) or entry_price <= 0:
            continue

        # Calculate SL/TP (simplified)
        sl_pct = 0.10  # 10% stop loss
        tp_pct = 0.20  # 20% target

        if row.get("ultra_pred") == "BUY_CE" or row.get("signal") == "BUY_CE":
            sl_price = entry_price * (1 - sl_pct)
            tp_price = entry_price * (1 + tp_pct)
            action = "BUY_CE"
        else:
            sl_price = entry_price * (1 - sl_pct)
            tp_price = entry_price * (1 + tp_pct)
            action = "BUY_PE"

        trade_plans.append(
            {
                "timestamp": row.get("timestamp", datetime.utcnow().isoformat()),
                "underlying": row.get("underlying", np.nan),
                "strike": row.get("strike", np.nan),
                "side": row.get("side", np.nan),
                "action": action,
                "entry_price": entry_price,
                "sl_price": sl_price,
                "tp_price": tp_price,
                "confidence": row.get("ultra_conf", row.get("confidence", np.nan)),
                "score": row.get("score", np.nan),
            }
        )

    if not trade_plans:
        return {
            "status": "EMPTY",
            "message": "No trade plans generated",
        }

    # Save trade plans
    df_plans = pd.DataFrame(trade_plans)
    df_plans.to_csv(TRADE_PLAN_SIM_CSV, index=False)
    print(f"[SAVE] Trade plans: {TRADE_PLAN_SIM_CSV} ({len(trade_plans)} trades)")

    # Simulate PnL (use future ltp from logs if available, else simulate)
    pnl_rows = []
    for plan in trade_plans:
        # Try to find exit price from shadow master
        exit_price = None
        exit_reason = "TIMEOUT"

        # Simplified: use entry price * random factor for simulation
        # In real implementation, would use future ltp from logs
        if "pnl_pct" in df_signals.columns:
            # Use actual PnL if available
            match = df_signals[
                (df_signals["underlying"] == plan["underlying"]) & (df_signals["strike"] == plan["strike"])
            ]
            if not match.empty:
                pnl_pct = match.iloc[0].get("pnl_pct", 0.0)
                exit_reason = match.iloc[0].get("exit_reason", "TIMEOUT")
            else:
                pnl_pct = 0.0
        else:
            # Simulate
            pnl_pct = np.random.uniform(-0.15, 0.25)  # Random PnL for demo

        pnl_rows.append(
            {
                "entry_timestamp": plan["timestamp"],
                "underlying": plan["underlying"],
                "strike": plan["strike"],
                "side": plan["side"],
                "action": plan["action"],
                "entry_price": plan["entry_price"],
                "exit_price": exit_price if exit_price else plan["entry_price"] * (1 + pnl_pct),
                "exit_reason": exit_reason,
                "pnl_pct": pnl_pct,
            }
        )

    # Save PnL log
    df_pnl = pd.DataFrame(pnl_rows)
    df_pnl.to_csv(PNL_SIM_CSV, index=False)
    print(f"[SAVE] PnL log: {PNL_SIM_CSV} ({len(pnl_rows)} trades)")

    # Generate summary
    summary_rows = []
    for underlying in UNDERLYINGS:
        df_u = df_pnl[df_pnl["underlying"] == underlying]
        if df_u.empty:
            continue

        wins = (df_u["pnl_pct"] > 0).sum()
        losses = (df_u["pnl_pct"] < 0).sum()
        win_rate = wins / len(df_u) * 100 if len(df_u) > 0 else 0.0
        avg_pnl = df_u["pnl_pct"].mean()
        total_pnl = df_u["pnl_pct"].sum()

        summary_rows.append(
            {
                "underlying": underlying,
                "trades": len(df_u),
                "wins": wins,
                "losses": losses,
                "win_rate": float(win_rate),
                "avg_pnl": float(avg_pnl),
                "total_pnl": float(total_pnl),
            }
        )

    # Save summary
    if summary_rows:
        df_summary = pd.DataFrame(summary_rows)
        df_summary.to_csv(SUMMARY_CSV, index=False)
        print(f"[SAVE] Summary: {SUMMARY_CSV}")

    return {
        "status": "SUCCESS",
        "total_trades": len(trade_plans),
        "summary": summary_rows,
    }


def main() -> None:
    """Main entry point."""
    result = simulate_ultra_trades()

    if result["status"] == "SUCCESS":
        print("\n=== TRADE SIMULATION SUMMARY ===")
        print(f"Total Trades: {result['total_trades']}")
        if result.get("summary"):
            print("\nPer Underlying:")
            for row in result["summary"]:
                print(f"{row['underlying']}:")
                print(f"  Trades: {row['trades']}, Win Rate: {row['win_rate']:.1f}%")
                print(f"  Avg PnL: {row['avg_pnl']:.2f}%, Total: {row['total_pnl']:.2f}%")
        print("\n[SAVE] All simulation results saved")
        print("[NOTE] Shadow simulation only - no real trades")
    else:
        print(f"\n[INFO] {result.get('message', 'Simulation not completed')}")


if __name__ == "__main__":
    main()
