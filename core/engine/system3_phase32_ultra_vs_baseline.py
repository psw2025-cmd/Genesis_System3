"""
System3 Ultra - Phase 32: Ultra vs Baseline Comparator

Compare ULTRA fused decisions vs baseline trade plans and PnL.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 95
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

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def _load_baseline_trades() -> Optional[pd.DataFrame]:
    """Load baseline trade plans."""
    trades_csv = LIVE_DIR / "angel_index_ai_trades_plan.csv"
    if not trades_csv.exists():
        return None
    try:
        return pd.read_csv(trades_csv)
    except Exception:
        return None


def _load_baseline_pnl() -> Optional[pd.DataFrame]:
    """Load baseline PnL log."""
    pnl_csv = LIVE_DIR / "angel_index_ai_pnl_log.csv"
    if not pnl_csv.exists():
        return None
    try:
        return pd.read_csv(pnl_csv)
    except Exception:
        return None


def _load_ultra_decisions() -> Optional[pd.DataFrame]:
    """Load Ultra fused decisions."""
    ultra_csv = ULTRA_DIR / "phase31_ultra_fused_decisions.csv"
    if not ultra_csv.exists():
        return None
    try:
        return pd.read_csv(ultra_csv)
    except Exception:
        return None


def _align_trades(
    df_baseline: pd.DataFrame,
    df_pnl: pd.DataFrame,
    df_ultra: pd.DataFrame,
) -> pd.DataFrame:
    """Align baseline trades with PnL and Ultra decisions."""
    aligned_rows = []

    # Join baseline trades with PnL
    if df_pnl is not None and not df_pnl.empty:
        # Try to match by underlying, strike, side, and timestamp
        for _, trade in df_baseline.iterrows():
            trade_underlying = trade.get("underlying", "")
            trade_strike = trade.get("strike", np.nan)
            trade_side = trade.get("side", "")
            trade_ts = trade.get("timestamp", trade.get("ts", ""))

            # Find matching PnL
            pnl_match = None
            if not df_pnl.empty:
                pnl_candidates = df_pnl[
                    (df_pnl.get("underlying", "") == trade_underlying)
                    & (df_pnl.get("strike", "") == trade_strike)
                    & (df_pnl.get("side", "") == trade_side)
                ]
                if not pnl_candidates.empty:
                    pnl_match = pnl_candidates.iloc[0]

            # Find matching Ultra decision
            ultra_match = None
            if df_ultra is not None and not df_ultra.empty:
                ultra_candidates = df_ultra[
                    (df_ultra.get("underlying", "") == trade_underlying)
                    & (df_ultra.get("strike", "") == trade_strike)
                    & (df_ultra.get("side", "") == trade_side)
                ]
                if not ultra_candidates.empty:
                    ultra_match = ultra_candidates.iloc[0]

            aligned_row = {
                "timestamp": trade_ts,
                "underlying": trade_underlying,
                "strike": trade_strike,
                "side": trade_side,
                "baseline_action": trade.get("action", trade.get("pred_label", "UNKNOWN")),
                "baseline_pnl": pnl_match.get("pnl_pct", np.nan) if pnl_match is not None else np.nan,
                "ultra_action": ultra_match.get("final_action", "HOLD") if ultra_match is not None else "HOLD",
                "ultra_pnl": np.nan,  # Hypothetical, would need to simulate
                "ultra_confidence": ultra_match.get("confidence", np.nan) if ultra_match is not None else np.nan,
                "ultra_score": ultra_match.get("score", np.nan) if ultra_match is not None else np.nan,
            }
            aligned_rows.append(aligned_row)
    else:
        # No PnL data, just compare actions
        for _, trade in df_baseline.iterrows():
            trade_underlying = trade.get("underlying", "")
            trade_strike = trade.get("strike", np.nan)
            trade_side = trade.get("side", "")

            ultra_match = None
            if df_ultra is not None and not df_ultra.empty:
                ultra_candidates = df_ultra[
                    (df_ultra.get("underlying", "") == trade_underlying)
                    & (df_ultra.get("strike", "") == trade_strike)
                    & (df_ultra.get("side", "") == trade_side)
                ]
                if not ultra_candidates.empty:
                    ultra_match = ultra_candidates.iloc[0]

            aligned_row = {
                "timestamp": trade.get("timestamp", trade.get("ts", "")),
                "underlying": trade_underlying,
                "strike": trade_strike,
                "side": trade_side,
                "baseline_action": trade.get("action", trade.get("pred_label", "UNKNOWN")),
                "baseline_pnl": np.nan,
                "ultra_action": ultra_match.get("final_action", "HOLD") if ultra_match is not None else "HOLD",
                "ultra_pnl": np.nan,
                "ultra_confidence": ultra_match.get("confidence", np.nan) if ultra_match is not None else np.nan,
                "ultra_score": ultra_match.get("score", np.nan) if ultra_match is not None else np.nan,
            }
            aligned_rows.append(aligned_row)

    return pd.DataFrame(aligned_rows)


def _compute_metrics(df_aligned: pd.DataFrame) -> Dict[str, Any]:
    """Compute comparison metrics."""
    if df_aligned.empty:
        return {}

    metrics = {}

    # Overall metrics
    baseline_trades = df_aligned[df_aligned["baseline_action"].isin(["BUY_CE", "BUY_PE"])]
    ultra_trades = df_aligned[df_aligned["ultra_action"].isin(["BUY_CE", "BUY_PE", "STRONG_BUY_CE", "STRONG_BUY_PE"])]

    # Baseline metrics
    baseline_pnl = baseline_trades["baseline_pnl"].dropna()
    if not baseline_pnl.empty:
        metrics["baseline_n_trades"] = len(baseline_trades)
        metrics["baseline_win_rate"] = (baseline_pnl > 0).sum() / len(baseline_pnl) if len(baseline_pnl) > 0 else 0.0
        metrics["baseline_avg_pnl"] = baseline_pnl.mean()
        metrics["baseline_max_dd"] = baseline_pnl.min() if len(baseline_pnl) > 0 else 0.0
    else:
        metrics["baseline_n_trades"] = len(baseline_trades)
        metrics["baseline_win_rate"] = 0.0
        metrics["baseline_avg_pnl"] = 0.0
        metrics["baseline_max_dd"] = 0.0

    # Ultra metrics (hypothetical)
    metrics["ultra_n_trades"] = len(ultra_trades)
    metrics["ultra_win_rate"] = 0.0  # Would need simulation
    metrics["ultra_avg_pnl"] = 0.0  # Would need simulation

    # Differences
    metrics["win_rate_delta"] = metrics["ultra_win_rate"] - metrics["baseline_win_rate"]
    metrics["avg_pnl_delta"] = metrics["ultra_avg_pnl"] - metrics["baseline_avg_pnl"]

    # Per-underlying metrics
    per_underlying = {}
    for underlying in UNDERLYINGS:
        df_u = df_aligned[df_aligned["underlying"] == underlying]
        if df_u.empty:
            continue

        baseline_u = df_u[df_u["baseline_action"].isin(["BUY_CE", "BUY_PE"])]
        ultra_u = df_u[df_u["ultra_action"].isin(["BUY_CE", "BUY_PE", "STRONG_BUY_CE", "STRONG_BUY_PE"])]

        baseline_pnl_u = baseline_u["baseline_pnl"].dropna()

        per_underlying[underlying] = {
            "baseline_n_trades": len(baseline_u),
            "baseline_win_rate": (baseline_pnl_u > 0).sum() / len(baseline_pnl_u) if len(baseline_pnl_u) > 0 else 0.0,
            "baseline_avg_pnl": baseline_pnl_u.mean() if len(baseline_pnl_u) > 0 else 0.0,
            "ultra_n_trades": len(ultra_u),
            "ultra_win_rate": 0.0,
            "ultra_avg_pnl": 0.0,
        }

    metrics["per_underlying"] = per_underlying

    return metrics


def run_phase32_comparison() -> str:
    """
    Run Phase 32: Ultra vs Baseline Comparison.

    Returns:
        Path to summary MD file
    """
    print("=== SYSTEM3 ULTRA - PHASE 32: ULTRA VS BASELINE COMPARATOR ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load data
    df_baseline_trades = _load_baseline_trades()
    df_baseline_pnl = _load_baseline_pnl()
    df_ultra = _load_ultra_decisions()

    if df_baseline_trades is None or df_baseline_trades.empty:
        print("[PHASE 32][ERROR] No baseline trades found")
        error_path = ULTRA_DIR / "phase32_error_no_baseline.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write("# Phase 32 Error\n\nNo baseline trades found\n")
        return str(error_path)

    if df_ultra is None or df_ultra.empty:
        print("[PHASE 32][WARN] No Ultra decisions found. Run Phase 31 first.")
        error_path = ULTRA_DIR / "phase32_error_no_ultra.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write("# Phase 32 Error\n\nNo Ultra decisions found. Run Phase 31 first.\n")
        return str(error_path)

    print(f"[LOAD] Baseline trades: {len(df_baseline_trades)}")
    if df_baseline_pnl is not None:
        print(f"[LOAD] Baseline PnL: {len(df_baseline_pnl)}")
    print(f"[LOAD] Ultra decisions: {len(df_ultra)}")

    # Align trades
    df_aligned = _align_trades(df_baseline_trades, df_baseline_pnl, df_ultra)
    print(f"[ALIGN] Aligned {len(df_aligned)} trades")

    # Save comparison CSV
    comparison_csv = ULTRA_DIR / "phase32_ultra_vs_baseline_comparison.csv"
    df_aligned.to_csv(comparison_csv, index=False)
    print(f"[SAVE] Comparison CSV saved to: {comparison_csv}")

    # Compute metrics
    metrics = _compute_metrics(df_aligned)

    # Generate summary MD
    summary_md = ULTRA_DIR / "phase32_ultra_vs_baseline_summary.md"
    with summary_md.open("w", encoding="utf-8") as f:
        f.write("# Ultra vs Baseline Comparison Summary\n\n")
        f.write(f"Generated: {datetime.utcnow().isoformat()}\n\n")
        f.write("## Overall Metrics\n\n")
        f.write("| Metric | Baseline | Ultra | Delta |\n")
        f.write("|--------|----------|-------|-------|\n")
        f.write(
            f"| Number of Trades | {metrics.get('baseline_n_trades', 0)} | {metrics.get('ultra_n_trades', 0)} | {metrics.get('ultra_n_trades', 0) - metrics.get('baseline_n_trades', 0)} |\n"
        )
        f.write(
            f"| Win Rate | {metrics.get('baseline_win_rate', 0.0):.1%} | {metrics.get('ultra_win_rate', 0.0):.1%} | {metrics.get('win_rate_delta', 0.0):.1%} |\n"
        )
        f.write(
            f"| Avg PnL | {metrics.get('baseline_avg_pnl', 0.0):.2%} | {metrics.get('ultra_avg_pnl', 0.0):.2%} | {metrics.get('avg_pnl_delta', 0.0):.2%} |\n"
        )
        f.write(f"| Max Drawdown | {metrics.get('baseline_max_dd', 0.0):.2%} | N/A | N/A |\n\n")

        f.write("## Per-Underlying Metrics\n\n")
        for underlying, u_metrics in metrics.get("per_underlying", {}).items():
            f.write(f"### {underlying}\n\n")
            f.write("| Metric | Baseline | Ultra |\n")
            f.write("|--------|----------|-------|\n")
            f.write(f"| Trades | {u_metrics.get('baseline_n_trades', 0)} | {u_metrics.get('ultra_n_trades', 0)} |\n")
            f.write(
                f"| Win Rate | {u_metrics.get('baseline_win_rate', 0.0):.1%} | {u_metrics.get('ultra_win_rate', 0.0):.1%} |\n"
            )
            f.write(
                f"| Avg PnL | {u_metrics.get('baseline_avg_pnl', 0.0):.2%} | {u_metrics.get('ultra_avg_pnl', 0.0):.2%} |\n\n"
            )

        f.write("## Notes\n\n")
        f.write("- Ultra PnL metrics are hypothetical and would require simulation\n")
        f.write("- This comparison is read-only and does not modify any baseline logic\n")
        f.write("- Ultra decisions are logged separately and never executed\n")

    print(f"[SAVE] Summary MD saved to: {summary_md}")
    print("\n[OK] Phase 32 Ultra vs Baseline Comparison completed")
    return str(summary_md)


def main() -> None:
    """Main entry point for CLI use."""
    try:
        path = run_phase32_comparison()
        print(f"\n[PHASE 32] Output written to: {path}")
    except Exception as e:
        print(f"[PHASE 32][ERROR] {e}")
        error_path = ULTRA_DIR / "phase32_error.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write(f"# Phase 32 Error\n\n{str(e)}\n")
        print(f"[PHASE 32] Error details saved to: {error_path}")


if __name__ == "__main__":
    main()
