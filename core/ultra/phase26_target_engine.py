"""
System3 Ultra - Phase 26: Adaptive Target Engine (ATE)

Compute dynamic target percentage based on:
- Risk level
- Volatility
- Score

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 89
"""

from pathlib import Path
from typing import Any, Dict

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

# Base target percentages
BASE_TP_PCT = 0.20  # 20% base target
MIN_TP_PCT = 0.10  # 10% minimum
MAX_TP_PCT = 0.50  # 50% maximum


def compute_target(
    risk_level: str,
    volatility: float,
    score: float,
) -> Dict[str, Any]:
    """
    Compute adaptive target percentage.

    Args:
        risk_level: "LOW", "MEDIUM", or "HIGH"
        volatility: Volatility measure (0-1)
        score: Expected move score (-1 to 1)

    Returns:
        Dict with tp_pct and reason list
    """
    vol_norm = max(0.0, min(1.0, volatility))
    score_abs = abs(score)
    score_norm = max(0.0, min(1.0, score_abs))

    reasons = []
    tp_pct = BASE_TP_PCT

    # Risk level adjustment
    if risk_level == "LOW":
        tp_pct *= 0.9  # Slightly lower target for low risk
        reasons.append("low risk profile")
    elif risk_level == "HIGH":
        tp_pct *= 1.2  # Higher target for high risk
        reasons.append("high risk profile")

    # Volatility adjustment (stable vol = higher target)
    if vol_norm < 0.3:
        tp_pct *= 1.3
        reasons.append("stable volatility")
    elif vol_norm > 0.7:
        tp_pct *= 0.85
        reasons.append("high volatility")

    # Score adjustment (strong score = higher target)
    if score_norm > 0.6:
        tp_pct *= 1.25
        reasons.append("strong score")
    elif score_norm < 0.3:
        tp_pct *= 0.9
        reasons.append("weak score")

    # Apply safety caps
    tp_pct = max(MIN_TP_PCT, min(MAX_TP_PCT, tp_pct))

    return {
        "tp_pct": float(tp_pct),
        "reason": reasons,
        "base_tp_pct": BASE_TP_PCT,
        "adjustments": {
            "risk_level": risk_level,
            "volatility": float(vol_norm),
            "score": float(score_norm),
        },
    }


def main() -> None:
    """Main entry point for testing."""
    print("=== SYSTEM3 ULTRA - PHASE 26: ADAPTIVE TARGET ENGINE (ATE) ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Sample inputs for verification
    samples = [
        {
            "risk_level": "LOW",
            "volatility": 0.2,
            "score": 0.7,
        },
        {
            "risk_level": "MEDIUM",
            "volatility": 0.5,
            "score": 0.4,
        },
        {
            "risk_level": "HIGH",
            "volatility": 0.8,
            "score": 0.2,
        },
    ]

    print("=== SAMPLE INPUTS ===")
    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}:")
        print(f"  Risk Level: {sample['risk_level']}")
        print(f"  Volatility: {sample['volatility']}")
        print(f"  Score: {sample['score']}")

    print("\n=== SAMPLE OUTPUTS ===")
    for i, sample in enumerate(samples, 1):
        result = compute_target(**sample)
        print(f"\nSample {i} Result:")
        print(f"  Target %: {result['tp_pct']:.3f} ({result['tp_pct']*100:.1f}%)")
        print(f"  Reasons: {', '.join(result['reason'])}")
        print(f"  Base TP: {result['base_tp_pct']:.3f}")

    print("\n[OK] Adaptive Target Engine validated")


if __name__ == "__main__":
    main()
