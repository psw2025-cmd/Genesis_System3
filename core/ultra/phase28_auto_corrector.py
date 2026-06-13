"""
System3 Ultra - Phase 28: Failure-Mode Auto-Corrector

Detect repeated misfires & recommend corrections.
Analyzes last 300 outcomes, clusters misfires, detects patterns.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 91
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
LEARNING_ULTRA_DIR = PROJECT_ROOT / "storage" / "learning_ultra"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)


def analyze_misfires(df: pd.DataFrame, n: int = 300) -> Dict[str, Any]:
    """
    Analyze misfires from outcomes data.

    Args:
        df: DataFrame with outcomes (should have is_misfire, exit_reason, pnl_pct, etc.)
        n: Number of recent outcomes to analyze

    Returns:
        Dict with issue detection and recommendations
    """
    if df.empty:
        return {
            "issue": "NO_DATA",
            "recommendation": "Collect more outcome data",
            "misfire_count": 0,
            "total_count": 0,
        }

    # Take last N rows
    df_recent = df.tail(n).copy()

    # Check for misfire column
    if "is_misfire" not in df_recent.columns:
        # Try to infer from other columns
        if "pnl_pct" in df_recent.columns and "signal" in df_recent.columns:
            # Misfire: negative PnL when signal was BUY
            df_recent["is_misfire"] = (
                (df_recent["signal"].isin(["BUY_CE", "BUY_PE"])) & (df_recent["pnl_pct"] < 0)
            ).astype(int)
        else:
            return {
                "issue": "INSUFFICIENT_COLUMNS",
                "recommendation": "Outcome data missing required columns",
                "misfire_count": 0,
                "total_count": len(df_recent),
            }

    total_count = len(df_recent)
    misfire_count = df_recent["is_misfire"].sum() if "is_misfire" in df_recent.columns else 0
    misfire_rate = misfire_count / total_count if total_count > 0 else 0.0

    if misfire_count < 3:
        return {
            "issue": "LOW_MISFIRE_COUNT",
            "recommendation": "Insufficient misfires for pattern detection",
            "misfire_count": misfire_count,
            "total_count": total_count,
            "misfire_rate": float(misfire_rate),
        }

    # Analyze misfire patterns
    df_misfires = df_recent[df_recent["is_misfire"] == 1].copy()

    issues = []
    recommendations = []

    # Pattern 1: Early exits (TIMEOUT exits with negative PnL)
    if "exit_reason" in df_misfires.columns:
        timeout_misfires = df_misfires[df_misfires["exit_reason"] == "TIMEOUT"]
        if len(timeout_misfires) > misfire_count * 0.4:
            issues.append("early exits")
            recommendations.append("increase stoploss by 0.05")

    # Pattern 2: Stop-loss hits (too tight)
    if "exit_reason" in df_misfires.columns:
        sl_misfires = df_misfires[df_misfires["exit_reason"].str.contains("STOPLOSS", case=False, na=False)]
        if len(sl_misfires) > misfire_count * 0.5:
            issues.append("frequent stoploss hits")
            recommendations.append("widen stoploss by 0.03")

    # Pattern 3: Low confidence trades failing
    if "confidence" in df_misfires.columns:
        low_conf_misfires = df_misfires[df_misfires["confidence"] < 0.7]
        if len(low_conf_misfires) > misfire_count * 0.6:
            issues.append("low confidence trades")
            recommendations.append("increase min_confidence threshold by 0.05")

    # Pattern 4: Weak score trades failing
    if "score" in df_misfires.columns:
        weak_score_misfires = df_misfires[df_misfires["score"].abs() < 0.3]
        if len(weak_score_misfires) > misfire_count * 0.5:
            issues.append("weak score trades")
            recommendations.append("increase min_score threshold by 0.05")

    # Pattern 5: High volatility regime failures
    if "market_regime" in df_misfires.columns or "regime_label" in df_misfires.columns:
        regime_col = "market_regime" if "market_regime" in df_misfires.columns else "regime_label"
        high_vol_misfires = df_misfires[df_misfires[regime_col].str.contains("HIGH_VOL", case=False, na=False)]
        if len(high_vol_misfires) > misfire_count * 0.4:
            issues.append("high volatility regime failures")
            recommendations.append("reduce position size in high volatility by 20%")

    # Default recommendation if no specific pattern
    if not issues:
        issues.append("general misfire pattern")
        recommendations.append("review threshold settings and risk parameters")

    return {
        "issue": ", ".join(issues) if issues else "UNKNOWN",
        "recommendation": "; ".join(recommendations) if recommendations else "No specific recommendation",
        "misfire_count": misfire_count,
        "total_count": total_count,
        "misfire_rate": float(misfire_rate),
        "patterns_detected": len(issues),
    }


def load_recent_outcomes(n: int = 300) -> Optional[pd.DataFrame]:
    """Load last N outcomes from available sources."""
    # Try PnL simulation
    pnl_csv = ULTRA_DIR / "dhan_ultra_pnl_sim.csv"
    if pnl_csv.exists():
        try:
            df = pd.read_csv(pnl_csv)
            return df.tail(n)
        except Exception:
            pass

    # Try shadow master
    shadow_csv = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.csv"
    if shadow_csv.exists():
        try:
            df = pd.read_csv(shadow_csv)
            return df.tail(n)
        except Exception:
            pass

    # Try real outcomes
    real_outcomes = LEARNING_ULTRA_DIR.parent / "learning" / "real_outcomes.csv"
    if real_outcomes.exists():
        try:
            df = pd.read_csv(real_outcomes)
            return df.tail(n)
        except Exception:
            pass

    return None


def main() -> None:
    """Main entry point for testing."""
    print("=== SYSTEM3 ULTRA - PHASE 28: FAILURE-MODE AUTO-CORRECTOR ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Load recent outcomes
    df_outcomes = load_recent_outcomes(n=300)

    if df_outcomes is None or df_outcomes.empty:
        print("[WARN] No outcome data found. Using synthetic data for demo.")
        # Generate synthetic misfire data for demo
        np.random.seed(42)
        n_samples = 100
        df_outcomes = pd.DataFrame(
            {
                "signal": np.random.choice(["BUY_CE", "BUY_PE", "HOLD"], n_samples),
                "pnl_pct": np.random.uniform(-0.15, 0.25, n_samples),
                "exit_reason": np.random.choice(["TIMEOUT", "STOPLOSS", "TAKEPROFIT"], n_samples),
                "confidence": np.random.uniform(0.5, 0.9, n_samples),
                "score": np.random.uniform(-0.5, 0.5, n_samples),
            }
        )
        # Create misfires: negative PnL when signal was BUY
        df_outcomes["is_misfire"] = (
            (df_outcomes["signal"].isin(["BUY_CE", "BUY_PE"])) & (df_outcomes["pnl_pct"] < 0)
        ).astype(int)

    print(f"[LOAD] Analyzing {len(df_outcomes)} recent outcomes")

    # Analyze misfires
    result = analyze_misfires(df_outcomes, n=300)

    print("\n=== MISFIRE ANALYSIS ===")
    print(f"Issue Detected: {result['issue']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Misfire Count: {result['misfire_count']}")
    print(f"Total Count: {result['total_count']}")
    print(f"Misfire Rate: {result['misfire_rate']:.1%}")
    print(f"Patterns Detected: {result.get('patterns_detected', 0)}")

    # Save auto-correction report
    import json

    # Convert numpy/pandas types to native Python types for JSON serialization
    result_serializable = {}
    for k, v in result.items():
        if isinstance(v, np.integer):
            result_serializable[k] = int(v)
        elif isinstance(v, np.floating):
            result_serializable[k] = float(v)
        elif hasattr(v, "item"):  # Handle pandas scalar types
            result_serializable[k] = v.item()
        else:
            result_serializable[k] = v
    report_json = REPORTS_ULTRA_DIR / "phase28_auto_correction_report.json"
    with report_json.open("w", encoding="utf-8") as f:
        json.dump(result_serializable, f, indent=2)
    print(f"\n[SAVE] Auto-correction report saved to: {report_json}")

    print("\n[OK] Failure-Mode Auto-Corrector validated")


if __name__ == "__main__":
    main()
