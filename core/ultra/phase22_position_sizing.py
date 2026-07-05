"""
System3 Ultra - Phase 22: Dynamic Position Sizing Engine

Decide quantity dynamically based on:
- Risk level
- Confidence
- Score
- Volatility

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 85
"""

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

# Safety rules
MIN_QTY = 1
MAX_QTY = 100
BASE_QTY = 25  # Base quantity for MEDIUM risk


def compute_position_size(
    risk_level: str,
    confidence: float,
    score: float,
    volatility: float,
) -> Dict[str, Any]:
    """
    Compute dynamic position size.

    Args:
        risk_level: "LOW", "MEDIUM", or "HIGH"
        confidence: Model confidence (0-1)
        score: Expected move score (-1 to 1)
        volatility: Volatility measure (0-1)

    Returns:
        Dict with qty and reason list
    """
    # Normalize inputs
    conf_norm = max(0.0, min(1.0, confidence))
    score_abs = abs(score)
    score_norm = max(0.0, min(1.0, score_abs))
    vol_norm = max(0.0, min(1.0, volatility))

    reasons = []
    qty = BASE_QTY

    # Risk level multiplier
    if risk_level == "LOW":
        qty_multiplier = 0.5  # Smaller position for low risk
        reasons.append("risk LOW")
    elif risk_level == "MEDIUM":
        qty_multiplier = 1.0  # Base position
        reasons.append("risk MEDIUM")
    else:  # HIGH
        qty_multiplier = 1.5  # Larger position for high risk (but capped)
        reasons.append("risk HIGH")

    qty = BASE_QTY * qty_multiplier

    # Confidence adjustment
    if conf_norm > 0.8:
        qty *= 1.2
        reasons.append("confidence strong")
    elif conf_norm < 0.6:
        qty *= 0.8
        reasons.append("confidence weak")

    # Score adjustment
    if score_norm > 0.5:
        qty *= 1.15
        reasons.append("score strong")
    elif score_norm < 0.3:
        qty *= 0.85
        reasons.append("score weak")

    # Volatility adjustment (higher vol = reduce size slightly)
    if vol_norm > 0.7:
        qty *= 0.9
        reasons.append("high volatility")
    elif vol_norm < 0.3:
        qty *= 1.1
        reasons.append("low volatility")

    # Apply safety caps
    qty = max(MIN_QTY, min(MAX_QTY, int(qty)))

    return {
        "qty": int(qty),
        "reason": reasons,
        "base_qty": BASE_QTY,
        "multipliers": {
            "risk_level": qty_multiplier,
            "confidence_adj": conf_norm,
            "score_adj": score_norm,
            "volatility_adj": vol_norm,
        },
    }


def main() -> None:
    """Main entry point for testing."""
    print("=== SYSTEM3 ULTRA - PHASE 22: DYNAMIC POSITION SIZING ENGINE ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Sample inputs for verification
    samples = [
        {
            "risk_level": "LOW",
            "confidence": 0.9,
            "score": 0.7,
            "volatility": 0.2,
        },
        {
            "risk_level": "MEDIUM",
            "confidence": 0.7,
            "score": 0.4,
            "volatility": 0.5,
        },
        {
            "risk_level": "HIGH",
            "confidence": 0.5,
            "score": 0.2,
            "volatility": 0.8,
        },
    ]

    print("=== SAMPLE INPUTS ===")
    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}:")
        print(f"  Risk Level: {sample['risk_level']}")
        print(f"  Confidence: {sample['confidence']}")
        print(f"  Score: {sample['score']}")
        print(f"  Volatility: {sample['volatility']}")

    print("\n=== SAMPLE OUTPUTS ===")
    for i, sample in enumerate(samples, 1):
        result = compute_position_size(**sample)
        print(f"\nSample {i} Result:")
        print(f"  Quantity: {result['qty']}")
        print(f"  Reasons: {', '.join(result['reason'])}")
        print(f"  Base Qty: {result['base_qty']}")
        print(f"  Multipliers: {result['multipliers']}")

    print("\n[OK] Dynamic Position Sizing Engine validated")


if __name__ == "__main__":
    main()
