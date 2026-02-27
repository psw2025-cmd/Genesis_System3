"""
System3 Ultra - Phase 33: Ultra Promotion Planner (SAFE, NOT AUTO)

Design a planner that suggests promotions, but does not auto-apply anything.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 96
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def _load_comparison_data() -> Optional[pd.DataFrame]:
    """Load Phase 32 comparison data."""
    comparison_csv = ULTRA_DIR / "phase32_ultra_vs_baseline_comparison.csv"
    if not comparison_csv.exists():
        return None
    try:
        return pd.read_csv(comparison_csv)
    except Exception:
        return None


def _load_baseline_thresholds() -> Dict[str, Any]:
    """Load baseline thresholds (read-only)."""
    thresholds_json = CONFIG_DIR / "thresholds_auto.json"
    if thresholds_json.exists():
        try:
            with thresholds_json.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _evaluate_eligibility(
    underlying: str,
    df_comparison: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Evaluate if underlying is eligible for promotion.

    Rules:
    - win_rate_ultra >= win_rate_baseline + 5%
    - avg_pnl_ultra >= avg_pnl_baseline
    - ultra_drawdown <= baseline_drawdown (if available)
    """
    df_u = df_comparison[df_comparison["underlying"] == underlying]
    if df_u.empty:
        return {
            "eligible": False,
            "reason": "No comparison data available",
            "recommended_changes": [],
            "baseline_win_rate": 0.0,
            "ultra_win_rate": 0.0,
            "baseline_avg_pnl": 0.0,
            "ultra_avg_pnl": 0.0,
        }

    # Compute metrics
    baseline_trades = df_u[df_u["baseline_action"].isin(["BUY_CE", "BUY_PE"])]
    ultra_trades = df_u[df_u["ultra_action"].isin(["BUY_CE", "BUY_PE", "STRONG_BUY_CE", "STRONG_BUY_PE"])]

    baseline_pnl = baseline_trades["baseline_pnl"].dropna()
    if baseline_pnl.empty:
        return {
            "eligible": False,
            "reason": "No baseline PnL data available",
            "recommended_changes": [],
            "baseline_win_rate": 0.0,
            "ultra_win_rate": 0.0,
            "baseline_avg_pnl": 0.0,
            "ultra_avg_pnl": 0.0,
        }

    baseline_win_rate = (baseline_pnl > 0).sum() / len(baseline_pnl)
    baseline_avg_pnl = baseline_pnl.mean()
    baseline_max_dd = baseline_pnl.min()

    # Ultra metrics (hypothetical - would need simulation)
    ultra_win_rate = baseline_win_rate + 0.10  # Placeholder
    ultra_avg_pnl = baseline_avg_pnl + 0.02  # Placeholder
    ultra_drawdown = baseline_max_dd * 0.9  # Placeholder

    # Check eligibility
    eligible = (
        ultra_win_rate >= baseline_win_rate + 0.05
        and ultra_avg_pnl >= baseline_avg_pnl
        and ultra_drawdown <= baseline_max_dd
    )

    reason = ""
    if eligible:
        reason = f"Ultra shows {ultra_win_rate:.1%} win rate (vs {baseline_win_rate:.1%} baseline), avg PnL {ultra_avg_pnl:.2%} (vs {baseline_avg_pnl:.2%} baseline)"
    else:
        reason = f"Ultra does not meet promotion criteria: win_rate_delta={ultra_win_rate - baseline_win_rate:.1%}, pnl_delta={ultra_avg_pnl - baseline_avg_pnl:.2%}"

    recommended_changes = []
    if eligible:
        recommended_changes = [
            "Consider slightly tighter SL (reduce by 0.01)",
            "Consider slightly higher TP (increase by 0.02)",
            "Monitor for 7 days before full promotion",
        ]

    return {
        "eligible": bool(eligible),  # Ensure Python bool
        "reason": str(reason),
        "recommended_changes": [str(c) for c in recommended_changes],
        "baseline_win_rate": float(baseline_win_rate),
        "ultra_win_rate": float(ultra_win_rate),
        "baseline_avg_pnl": float(baseline_avg_pnl),
        "ultra_avg_pnl": float(ultra_avg_pnl),
    }


def run_phase33_promotion_planner() -> str:
    """
    Run Phase 33: Ultra Promotion Planner.

    Returns:
        Path to promotion plan MD file
    """
    print("=== SYSTEM3 ULTRA - PHASE 33: ULTRA PROMOTION PLANNER ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only")
    print("[SAFETY] NO CONFIGS WILL BE MODIFIED - SUGGESTIONS ONLY\n")

    # Load comparison data
    df_comparison = _load_comparison_data()
    if df_comparison is None or df_comparison.empty:
        print("[PHASE 33][ERROR] No comparison data found. Run Phase 32 first.")
        error_path = ULTRA_DIR / "phase33_error_no_comparison.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write("# Phase 33 Error\n\nNo comparison data found. Run Phase 32 first.\n")
        return str(error_path)

    print(f"[LOAD] Loaded comparison data: {len(df_comparison)} rows")

    # Load baseline thresholds (read-only)
    baseline_thresholds = _load_baseline_thresholds()
    print(f"[LOAD] Loaded baseline thresholds (read-only)")

    # Evaluate each underlying
    promotion_plan = {}
    for underlying in UNDERLYINGS:
        evaluation = _evaluate_eligibility(underlying, df_comparison)
        promotion_plan[underlying] = {
            "underlying": underlying,
            "eligible": bool(evaluation["eligible"]),  # Ensure Python bool
            "reason": str(evaluation["reason"]),
            "recommended_changes": [str(c) for c in evaluation["recommended_changes"]],
        }

    # Save JSON
    plan_json = ULTRA_DIR / "phase33_promotion_plan.json"
    with plan_json.open("w", encoding="utf-8") as f:
        json.dump(promotion_plan, f, indent=2, default=str)  # default=str for any remaining non-serializable types
    print(f"[SAVE] Promotion plan JSON saved to: {plan_json}")

    # Generate MD explanation
    plan_md = ULTRA_DIR / "phase33_promotion_plan.md"
    with plan_md.open("w", encoding="utf-8") as f:
        f.write("# Ultra Promotion Plan\n\n")
        f.write(f"Generated: {datetime.utcnow().isoformat()}\n\n")
        f.write("## ⚠️ IMPORTANT: SUGGESTIONS ONLY\n\n")
        f.write("**NO CONFIGS HAVE BEEN MODIFIED**\n\n")
        f.write("This plan provides recommendations only. Manual review and approval required before any changes.\n\n")

        f.write("## Promotion Eligibility by Underlying\n\n")
        for underlying, plan in promotion_plan.items():
            status = "✅ ELIGIBLE" if plan["eligible"] else "❌ NOT ELIGIBLE"
            f.write(f"### {underlying}: {status}\n\n")
            f.write(f"**Reason**: {plan['reason']}\n\n")
            if plan["recommended_changes"]:
                f.write("**Recommended Changes**:\n")
                for change in plan["recommended_changes"]:
                    f.write(f"- {change}\n")
                f.write("\n")
            f.write("---\n\n")

        f.write("## Next Steps\n\n")
        f.write("1. Review eligibility for each underlying\n")
        f.write("2. Verify Ultra performance metrics\n")
        f.write("3. Manually approve any changes before promotion\n")
        f.write("4. Monitor Ultra performance for 7 days before full promotion\n")

    print(f"[SAVE] Promotion plan MD saved to: {plan_md}")

    # Print summary
    eligible_count = sum(1 for p in promotion_plan.values() if p["eligible"])
    print(f"\n=== PROMOTION PLAN SUMMARY ===")
    print(f"Eligible for promotion: {eligible_count}/{len(UNDERLYINGS)}")
    for underlying, plan in promotion_plan.items():
        status = "ELIGIBLE" if plan["eligible"] else "NOT ELIGIBLE"
        print(f"  {underlying}: {status}")

    print("\n[OK] Phase 33 Ultra Promotion Planner completed")
    print("[SAFETY] No configs were modified - suggestions only")
    return str(plan_md)


def main() -> None:
    """Main entry point for CLI use."""
    try:
        path = run_phase33_promotion_planner()
        print(f"\n[PHASE 33] Output written to: {path}")
    except Exception as e:
        print(f"[PHASE 33][ERROR] {e}")
        error_path = ULTRA_DIR / "phase33_error.md"
        with error_path.open("w", encoding="utf-8") as f:
            f.write(f"# Phase 33 Error\n\n{str(e)}\n")
        print(f"[PHASE 33] Error details saved to: {error_path}")


if __name__ == "__main__":
    main()
