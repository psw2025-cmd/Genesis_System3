"""
System3 Ultra - Threshold Lab V2 (Shadow Only)

Experiments thresholds on shadow PnL without changing real configs.
Grid search analysis only.

Inputs:
- storage/learning_ultra/dhan_ultra_shadow_master.parquet

Outputs:
- storage/reports_ultra/ultra_threshold_grid_search.csv

Menu Option: 79
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_ULTRA_DIR = PROJECT_ROOT / "storage" / "learning_ultra"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

SHADOW_PARQUET = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.parquet"
SHADOW_CSV = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.csv"
GRID_SEARCH_CSV = REPORTS_ULTRA_DIR / "ultra_threshold_grid_search.csv"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def grid_search_thresholds() -> Dict[str, Any]:
    """
    Grid search threshold combinations on shadow dataset.

    Returns:
        Dict with grid search results
    """
    print("=== SYSTEM3 ULTRA - THRESHOLD LAB V2 (SHADOW) ===")
    print("[INFO] Grid search threshold experiments\n")
    print("[SAFETY] Shadow analysis only - no config changes\n")

    # Load shadow master dataset
    df_shadow = None
    if SHADOW_PARQUET.exists():
        try:
            df_shadow = pd.read_parquet(SHADOW_PARQUET)
        except Exception:
            if SHADOW_CSV.exists():
                df_shadow = pd.read_csv(SHADOW_CSV)
    elif SHADOW_CSV.exists():
        df_shadow = pd.read_csv(SHADOW_CSV)

    if df_shadow is None or df_shadow.empty:
        return {
            "status": "NO_DATA",
            "message": "Shadow master dataset not found. Run Phase 10 first.",
        }

    print(f"[LOAD] Shadow dataset: {len(df_shadow)} rows")

    # Threshold grids
    conf_thresholds = np.arange(0.60, 0.96, 0.05)
    score_thresholds = np.arange(0.10, 0.61, 0.05)

    all_results = []

    for underlying in UNDERLYINGS:
        df_u = df_shadow[df_shadow["underlying"] == underlying] if "underlying" in df_shadow.columns else pd.DataFrame()
        if df_u.empty:
            continue

        print(f"\n[GRID SEARCH] {underlying}...")

        # Need confidence, score, and is_win columns
        if "confidence" not in df_u.columns or "score" not in df_u.columns or "is_win" not in df_u.columns:
            print(f"[SKIP] {underlying}: Missing required columns")
            continue

        for conf_thresh in conf_thresholds:
            for score_thresh in score_thresholds:
                # Filter trades that would pass these thresholds
                filtered = df_u[(df_u["confidence"] >= conf_thresh) & (df_u["score"].abs() >= score_thresh)]

                if len(filtered) < 1:
                    continue

                # Compute metrics
                trades = len(filtered)
                wins = filtered["is_win"].sum() if "is_win" in filtered.columns else 0
                win_rate = wins / trades if trades > 0 else 0.0

                avg_pnl = filtered["pnl_pct"].mean() if "pnl_pct" in filtered.columns else 0.0
                max_dd = filtered["pnl_pct"].min() if "pnl_pct" in filtered.columns else 0.0

                # Sharpe-like metric (simplified)
                sharpe_like = (
                    avg_pnl / (filtered["pnl_pct"].std() + 1e-10)
                    if "pnl_pct" in filtered.columns and filtered["pnl_pct"].std() > 0
                    else 0.0
                )

                all_results.append(
                    {
                        "underlying": underlying,
                        "conf_thresh": float(conf_thresh),
                        "score_thresh": float(score_thresh),
                        "trades": trades,
                        "win_rate": float(win_rate * 100),
                        "avg_pnl": float(avg_pnl),
                        "max_drawdown": float(max_dd),
                        "sharpe_like": float(sharpe_like),
                        "comment": f"Trades: {trades}, Win%: {win_rate*100:.1f}%, Avg PnL: {avg_pnl:.2f}%",
                    }
                )

    if not all_results:
        return {
            "status": "EMPTY",
            "message": "No threshold combinations found",
        }

    # Save results
    df_results = pd.DataFrame(all_results)
    df_results = df_results.sort_values(["underlying", "avg_pnl"], ascending=[True, False])
    df_results.to_csv(GRID_SEARCH_CSV, index=False)
    print(f"\n[SAVE] Grid search results: {GRID_SEARCH_CSV}")

    # Summary
    summary = {}
    for underlying in UNDERLYINGS:
        df_u_results = df_results[df_results["underlying"] == underlying]
        if not df_u_results.empty:
            best = df_u_results.iloc[0]
            summary[underlying] = {
                "best_conf": best["conf_thresh"],
                "best_score": best["score_thresh"],
                "best_avg_pnl": best["avg_pnl"],
                "best_win_rate": best["win_rate"],
            }

    return {
        "status": "SUCCESS",
        "total_combinations": len(all_results),
        "summary": summary,
    }


def main() -> None:
    """Main entry point."""
    result = grid_search_thresholds()

    if result["status"] == "SUCCESS":
        print("\n=== THRESHOLD GRID SEARCH SUMMARY ===")
        print(f"Total Combinations Tested: {result['total_combinations']}")
        print("\nBest Thresholds Per Underlying:")
        for underlying, best in result["summary"].items():
            print(f"{underlying}:")
            print(f"  Confidence: {best['best_conf']:.2f}")
            print(f"  Score: {best['best_score']:.2f}")
            print(f"  Avg PnL: {best['best_avg_pnl']:.2f}%")
            print(f"  Win Rate: {best['best_win_rate']:.1f}%")
        print(f"\n[SAVE] Full results: {GRID_SEARCH_CSV}")
        print("[NOTE] No config changes - analysis only")
    else:
        print(f"\n[INFO] {result.get('message', 'Grid search not completed')}")


if __name__ == "__main__":
    main()
