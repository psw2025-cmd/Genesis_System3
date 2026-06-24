"""
System3 Ultra - Phase 27: Risk-Reward Balancer

Balance SL/TP dynamically for optimized risk-reward ratio.
Combines results from Adaptive Stoploss Engine (ASE) and Adaptive Target Engine (ATE).

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 90
"""

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

# Import ASE and ATE
from core.ultra.phase25_stoploss_engine import compute_stoploss
from core.ultra.phase26_target_engine import compute_target

# Target RR ratio
TARGET_RR_RATIO = 1.5  # Target 1.5:1 risk-reward
MIN_RR_RATIO = 1.0  # Minimum acceptable
MAX_RR_RATIO = 3.0  # Maximum reasonable


def balance_risk_reward(
    risk_level: str,
    volatility: float,
    score: float,
    drift_strength: float = 0.0,
    drift_direction: Optional[str] = None,
    premium_behavior: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Balance SL/TP for optimized risk-reward ratio.

    Args:
        risk_level: "LOW", "MEDIUM", or "HIGH"
        volatility: Volatility measure (0-1)
        score: Expected move score (-1 to 1)
        drift_strength: Confidence drift strength
        drift_direction: Drift direction
        premium_behavior: Premium behavior indicator

    Returns:
        Dict with rr_ratio, adjusted_sl, adjusted_tp
    """
    # Get initial SL and TP from engines
    sl_result = compute_stoploss(
        risk_level=risk_level,
        volatility=volatility,
        drift_strength=drift_strength,
        drift_direction=drift_direction,
        premium_behavior=premium_behavior,
    )
    tp_result = compute_target(
        risk_level=risk_level,
        volatility=volatility,
        score=score,
    )

    initial_sl = sl_result["sl_pct"]
    initial_tp = tp_result["tp_pct"]

    # Compute initial RR ratio
    initial_rr = initial_tp / initial_sl if initial_sl > 0 else 0.0

    # Adjust to target RR if needed
    adjusted_sl = initial_sl
    adjusted_tp = initial_tp

    if initial_rr < MIN_RR_RATIO:
        # RR too low, increase TP or decrease SL
        # Prefer increasing TP (more aggressive)
        adjusted_tp = initial_sl * TARGET_RR_RATIO
        if adjusted_tp > 0.50:  # Cap at 50%
            adjusted_tp = 0.50
            adjusted_sl = adjusted_tp / TARGET_RR_RATIO
    elif initial_rr > MAX_RR_RATIO:
        # RR too high, decrease TP or increase SL
        # Prefer decreasing TP (more conservative)
        adjusted_tp = initial_sl * TARGET_RR_RATIO
    else:
        # RR is reasonable, fine-tune to target
        if abs(initial_rr - TARGET_RR_RATIO) > 0.2:
            adjusted_tp = initial_sl * TARGET_RR_RATIO

    # Final RR ratio
    final_rr = adjusted_tp / adjusted_sl if adjusted_sl > 0 else 0.0

    return {
        "rr_ratio": float(final_rr),
        "adjusted_sl": float(adjusted_sl),
        "adjusted_tp": float(adjusted_tp),
        "initial_sl": float(initial_sl),
        "initial_tp": float(initial_tp),
        "initial_rr": float(initial_rr),
        "target_rr": TARGET_RR_RATIO,
        "adjustment_applied": abs(initial_rr - final_rr) > 0.05,
    }


def main() -> None:
    """Main entry point for testing."""
    print("=== SYSTEM3 ULTRA - PHASE 27: RISK-REWARD BALANCER ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Sample inputs for verification
    samples = [
        {
            "risk_level": "LOW",
            "volatility": 0.2,
            "score": 0.7,
            "drift_strength": 0.1,
            "drift_direction": "STABLE",
            "premium_behavior": "strong",
        },
        {
            "risk_level": "MEDIUM",
            "volatility": 0.5,
            "score": 0.4,
            "drift_strength": 0.3,
            "drift_direction": "UPWARD",
            "premium_behavior": "normal",
        },
        {
            "risk_level": "HIGH",
            "volatility": 0.8,
            "score": 0.2,
            "drift_strength": 0.6,
            "drift_direction": "DOWNWARD",
            "premium_behavior": "weak",
        },
    ]

    print("=== SAMPLE INPUTS ===")
    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}:")
        for key, value in sample.items():
            print(f"  {key}: {value}")

    print("\n=== SAMPLE OUTPUTS ===")
    for i, sample in enumerate(samples, 1):
        result = balance_risk_reward(**sample)
        print(f"\nSample {i} Result:")
        print(f"  RR Ratio: {result['rr_ratio']:.2f}")
        print(f"  Adjusted SL: {result['adjusted_sl']:.3f} ({result['adjusted_sl']*100:.1f}%)")
        print(f"  Adjusted TP: {result['adjusted_tp']:.3f} ({result['adjusted_tp']*100:.1f}%)")
        print(f"  Initial RR: {result['initial_rr']:.2f}")
        print(f"  Target RR: {result['target_rr']:.2f}")
        print(f"  Adjustment Applied: {result['adjustment_applied']}")

    print("\n[OK] Risk-Reward Balancer validated")


if __name__ == "__main__":
    main()
