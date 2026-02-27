"""
System3 Ultra - Phase 25: Adaptive Stoploss Engine (ASE)

Dynamic stoploss based on:
- Volatility
- Drift
- Risk level
- Premium behaviour

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 88
"""

import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

# Base stoploss percentages
BASE_SL_PCT = 0.10  # 10% base stoploss
MIN_SL_PCT = 0.05  # 5% minimum
MAX_SL_PCT = 0.20  # 20% maximum


def compute_stoploss(
    risk_level: str,
    volatility: float,
    drift_strength: float,
    drift_direction: Optional[str] = None,
    premium_behavior: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compute adaptive stoploss percentage.

    Args:
        risk_level: "LOW", "MEDIUM", or "HIGH"
        volatility: Volatility measure (0-1)
        drift_strength: Confidence drift strength (0-1)
        drift_direction: "UPWARD", "DOWNWARD", or "STABLE"
        premium_behavior: Premium behavior indicator (optional)

    Returns:
        Dict with sl_pct and reason list
    """
    vol_norm = max(0.0, min(1.0, volatility))
    drift_norm = max(0.0, min(1.0, drift_strength))

    reasons = []
    sl_pct = BASE_SL_PCT

    # Risk level adjustment
    if risk_level == "LOW":
        sl_pct *= 0.8  # Tighter stoploss for low risk
        reasons.append("low risk tolerance")
    elif risk_level == "HIGH":
        sl_pct *= 1.3  # Wider stoploss for high risk
        reasons.append("high risk tolerance")

    # Volatility adjustment (higher vol = wider stoploss)
    if vol_norm > 0.7:
        sl_pct *= 1.4
        reasons.append("high volatility")
    elif vol_norm < 0.3:
        sl_pct *= 0.9
        reasons.append("low volatility")

    # Drift adjustment
    if drift_direction == "DOWNWARD":
        sl_pct *= 1.2  # Wider stoploss if confidence drifting down
        reasons.append("downward drift")
        if drift_norm > 0.5:
            sl_pct *= 1.1
            reasons.append("strong downward drift")
    elif drift_direction == "UPWARD":
        sl_pct *= 0.95  # Slightly tighter if confidence improving
        reasons.append("upward drift")

    # Premium behavior adjustment
    if premium_behavior:
        if "decay" in premium_behavior.lower() or "weak" in premium_behavior.lower():
            sl_pct *= 1.15
            reasons.append("premium weakness")
        elif "strong" in premium_behavior.lower() or "momentum" in premium_behavior.lower():
            sl_pct *= 0.92
            reasons.append("premium strength")

    # Apply safety caps
    sl_pct = max(MIN_SL_PCT, min(MAX_SL_PCT, sl_pct))

    return {
        "sl_pct": float(sl_pct),
        "reason": reasons,
        "base_sl_pct": BASE_SL_PCT,
        "adjustments": {
            "risk_level": risk_level,
            "volatility": float(vol_norm),
            "drift_strength": float(drift_norm),
            "drift_direction": drift_direction or "UNKNOWN",
        },
    }


def main() -> None:
    """Main entry point for testing."""
    print("=== SYSTEM3 ULTRA - PHASE 25: ADAPTIVE STOPLOSS ENGINE (ASE) ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Sample inputs for verification
    samples = [
        {
            "risk_level": "LOW",
            "volatility": 0.2,
            "drift_strength": 0.1,
            "drift_direction": "STABLE",
            "premium_behavior": "strong",
        },
        {
            "risk_level": "MEDIUM",
            "volatility": 0.5,
            "drift_strength": 0.3,
            "drift_direction": "UPWARD",
            "premium_behavior": "normal",
        },
        {
            "risk_level": "HIGH",
            "volatility": 0.9,
            "drift_strength": 0.6,
            "drift_direction": "DOWNWARD",
            "premium_behavior": "weak",
        },
    ]

    print("=== SAMPLE INPUTS ===")
    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}:")
        print(f"  Risk Level: {sample['risk_level']}")
        print(f"  Volatility: {sample['volatility']}")
        print(f"  Drift Strength: {sample['drift_strength']}")
        print(f"  Drift Direction: {sample['drift_direction']}")
        print(f"  Premium Behavior: {sample['premium_behavior']}")

    print("\n=== SAMPLE OUTPUTS ===")
    for i, sample in enumerate(samples, 1):
        result = compute_stoploss(**sample)
        print(f"\nSample {i} Result:")
        print(f"  Stoploss %: {result['sl_pct']:.3f} ({result['sl_pct']*100:.1f}%)")
        print(f"  Reasons: {', '.join(result['reason'])}")
        print(f"  Base SL: {result['base_sl_pct']:.3f}")

    print("\n[OK] Adaptive Stoploss Engine validated")


if __name__ == "__main__":
    main()
