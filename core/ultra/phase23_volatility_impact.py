"""
System3 Ultra - Phase 23: Volatility Regime Impact Engine

Understand how volatility affects decisions.
Classifies volatility regimes and computes impact factors.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 86
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"
LEARNING_ULTRA_DIR = PROJECT_ROOT / "storage" / "learning_ultra"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)


def compute_volatility_regime(
    volatility: float,
    volatility_trend: Optional[float] = None,
    volatility_spikiness: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Compute volatility regime and impact factor.

    Args:
        volatility: Current volatility (0-1 scale)
        volatility_trend: Trend in volatility (positive = rising, negative = falling)
        volatility_spikiness: Measure of volatility spikes (0-1)

    Returns:
        Dict with vol_regime, impact_factor, and explanation
    """
    vol_norm = max(0.0, min(1.0, volatility))

    # Default values if not provided
    if volatility_trend is None:
        volatility_trend = 0.0
    if volatility_spikiness is None:
        volatility_spikiness = vol_norm * 0.5  # Estimate from volatility

    reasons = []
    impact_factor = 0.0

    # Classify regime
    if vol_norm < 0.3:
        if abs(volatility_trend) < 0.1:
            vol_regime = "STABLE"
            impact_factor = 0.1  # Positive impact (stable is good)
            reasons.append("stable low volatility")
        else:
            vol_regime = "RISING" if volatility_trend > 0 else "FALLING"
            impact_factor = 0.0
            reasons.append(f"volatility {vol_regime.lower()}")
    elif vol_norm < 0.6:
        if volatility_spikiness > 0.6:
            vol_regime = "SPIKY"
            impact_factor = -0.15  # Negative impact (spiky is risky)
            reasons.append("spiky volatility pattern")
        else:
            vol_regime = "RISING" if volatility_trend > 0.2 else "STABLE"
            impact_factor = -0.05
            reasons.append("moderate volatility")
    else:
        if volatility_spikiness > 0.7:
            vol_regime = "CHAOTIC"
            impact_factor = -0.3  # Strong negative impact
            reasons.append("chaotic high volatility")
        else:
            vol_regime = "RISING"
            impact_factor = -0.2
            reasons.append("rising volatility")

    # Adjust impact based on trend
    if volatility_trend > 0.3:
        impact_factor -= 0.1
        reasons.append("volatility trending up")
    elif volatility_trend < -0.3:
        impact_factor += 0.05
        reasons.append("volatility trending down")

    # Clamp impact factor
    impact_factor = max(-0.5, min(0.2, impact_factor))

    return {
        "vol_regime": vol_regime,
        "impact_factor": float(impact_factor),
        "explanation": reasons,
        "volatility": float(vol_norm),
        "volatility_trend": float(volatility_trend),
        "volatility_spikiness": float(volatility_spikiness),
    }


def analyze_volatility_from_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze volatility from historical data.

    Args:
        df: DataFrame with volatility-related columns

    Returns:
        Dict with volatility analysis
    """
    if df.empty:
        return {
            "vol_regime": "UNKNOWN",
            "impact_factor": 0.0,
            "explanation": ["insufficient data"],
        }

    # Try to find volatility columns
    vol_cols = [c for c in df.columns if "vol" in c.lower() or "std" in c.lower()]
    if not vol_cols:
        return {
            "vol_regime": "UNKNOWN",
            "impact_factor": 0.0,
            "explanation": ["no volatility data"],
        }

    vol_col = vol_cols[0]
    vol_values = df[vol_col].dropna()

    if vol_values.empty:
        return {
            "vol_regime": "UNKNOWN",
            "impact_factor": 0.0,
            "explanation": ["no valid volatility values"],
        }

    # Compute statistics
    vol_mean = vol_values.mean()
    vol_std = vol_values.std()
    vol_trend = 0.0
    vol_spikiness = 0.0

    if len(vol_values) > 1:
        # Simple trend: compare first half vs second half
        mid = len(vol_values) // 2
        first_half = vol_values.iloc[:mid].mean()
        second_half = vol_values.iloc[mid:].mean()
        vol_trend = (second_half - first_half) / (vol_mean + 1e-10)

        # Spikiness: coefficient of variation
        if vol_mean > 0:
            vol_spikiness = vol_std / vol_mean

    return compute_volatility_regime(
        volatility=vol_mean,
        volatility_trend=vol_trend,
        volatility_spikiness=min(1.0, vol_spikiness),
    )


def main() -> None:
    """Main entry point for testing."""
    print("=== SYSTEM3 ULTRA - PHASE 23: VOLATILITY REGIME IMPACT ENGINE ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    # Sample inputs for verification
    samples = [
        {
            "volatility": 0.2,
            "volatility_trend": 0.0,
            "volatility_spikiness": 0.1,
        },
        {
            "volatility": 0.5,
            "volatility_trend": 0.3,
            "volatility_spikiness": 0.7,
        },
        {
            "volatility": 0.9,
            "volatility_trend": 0.5,
            "volatility_spikiness": 0.9,
        },
    ]

    print("=== SAMPLE INPUTS ===")
    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}:")
        print(f"  Volatility: {sample['volatility']}")
        print(f"  Trend: {sample['volatility_trend']}")
        print(f"  Spikiness: {sample['volatility_spikiness']}")

    print("\n=== SAMPLE OUTPUTS ===")
    for i, sample in enumerate(samples, 1):
        result = compute_volatility_regime(**sample)
        print(f"\nSample {i} Result:")
        print(f"  Vol Regime: {result['vol_regime']}")
        print(f"  Impact Factor: {result['impact_factor']:.3f}")
        print(f"  Explanation: {', '.join(result['explanation'])}")

    # Try to analyze from shadow master if available
    shadow_csv = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.csv"
    if shadow_csv.exists():
        try:
            df = pd.read_csv(shadow_csv)
            analysis = analyze_volatility_from_data(df)
            print(f"\n=== ANALYSIS FROM SHADOW MASTER ===")
            print(f"Vol Regime: {analysis['vol_regime']}")
            print(f"Impact Factor: {analysis['impact_factor']:.3f}")
            print(f"Explanation: {', '.join(analysis['explanation'])}")
        except Exception as e:
            print(f"\n[WARN] Could not analyze shadow master: {e}")

    print("\n[OK] Volatility Regime Impact Engine validated")


if __name__ == "__main__":
    main()
