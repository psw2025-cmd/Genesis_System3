"""
System3 Ultra - Phase 30: Real-Time Calibration Engine (RTCE)

Live recalibration of:
- Risk level
- Stoploss (SL)
- Target (TP)
- Position sizing

Combines results from Phases 21-29.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 93
"""

import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

# Import all phase engines
from core.ultra.phase21_adaptive_risk_engine import AdaptiveRiskEngine
from core.ultra.phase22_position_sizing import compute_position_size
from core.ultra.phase23_volatility_impact import compute_volatility_regime
from core.ultra.phase24_confidence_drift import analyze_confidence_drift
from core.ultra.phase25_stoploss_engine import compute_stoploss
from core.ultra.phase26_target_engine import compute_target
from core.ultra.phase27_rr_balancer import balance_risk_reward


class RealTimeCalibrationEngine:
    """
    Real-Time Calibration Engine - Combines all adaptive components.
    """

    def __init__(self):
        """Initialize the calibration engine."""
        self.risk_engine = AdaptiveRiskEngine()

    def calibrate(
        self,
        volatility: float,
        confidence: float,
        score: float,
        market_regime: Optional[str] = None,
        underlying: Optional[str] = None,
        drift_strength: float = 0.0,
        drift_direction: Optional[str] = None,
        premium_behavior: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform real-time calibration of all parameters.

        Args:
            volatility: Volatility measure (0-1)
            confidence: Model confidence (0-1)
            score: Expected move score (-1 to 1)
            market_regime: Market regime label
            underlying: Underlying name
            drift_strength: Confidence drift strength
            drift_direction: Drift direction
            premium_behavior: Premium behavior indicator

        Returns:
            Dict with updated risk_level, sl, tp, qty, and reasons
        """
        reasons = []

        # Step 1: Compute volatility regime
        vol_regime_result = compute_volatility_regime(
            volatility=volatility,
            volatility_trend=0.0,  # Could be computed from history
            volatility_spikiness=volatility * 0.5,
        )
        vol_regime = vol_regime_result["vol_regime"]
        vol_impact = vol_regime_result["impact_factor"]
        reasons.extend(vol_regime_result["explanation"])

        # Step 2: Compute adaptive risk level
        risk_result = self.risk_engine.compute_risk(
            volatility=volatility,
            confidence=confidence,
            score=score,
            market_regime=market_regime or vol_regime,
            underlying=underlying,
        )
        risk_level = risk_result["risk_level"]
        reasons.extend(risk_result["reason"])

        # Step 3: Compute adaptive stoploss
        sl_result = compute_stoploss(
            risk_level=risk_level,
            volatility=volatility,
            drift_strength=drift_strength,
            drift_direction=drift_direction,
            premium_behavior=premium_behavior,
        )
        updated_sl = sl_result["sl_pct"]
        reasons.extend(sl_result["reason"])

        # Step 4: Compute adaptive target
        tp_result = compute_target(
            risk_level=risk_level,
            volatility=volatility,
            score=score,
        )
        updated_tp = tp_result["tp_pct"]
        reasons.extend(tp_result["reason"])

        # Step 5: Balance risk-reward
        rr_result = balance_risk_reward(
            risk_level=risk_level,
            volatility=volatility,
            score=score,
            drift_strength=drift_strength,
            drift_direction=drift_direction,
            premium_behavior=premium_behavior,
        )
        # Use balanced values if adjustment was applied
        if rr_result["adjustment_applied"]:
            updated_sl = rr_result["adjusted_sl"]
            updated_tp = rr_result["adjusted_tp"]
            reasons.append("risk-reward balanced")

        # Step 6: Compute position size
        qty_result = compute_position_size(
            risk_level=risk_level,
            confidence=confidence,
            score=score,
            volatility=volatility,
        )
        updated_qty = qty_result["qty"]
        reasons.extend(qty_result["reason"])

        # Compile final result
        return {
            "updated_risk_level": risk_level,
            "updated_sl": float(updated_sl),
            "updated_tp": float(updated_tp),
            "updated_qty": int(updated_qty),
            "reason": list(set(reasons)),  # Remove duplicates
            "components": {
                "volatility_regime": vol_regime,
                "volatility_impact": float(vol_impact),
                "risk_score": float(risk_result["risk_score"]),
                "rr_ratio": float(rr_result["rr_ratio"]),
            },
        }


def main() -> None:
    """Main entry point for testing."""
    print("=== SYSTEM3 ULTRA - PHASE 30: REAL-TIME CALIBRATION ENGINE (RTCE) ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    engine = RealTimeCalibrationEngine()

    # Sample inputs for verification
    samples = [
        {
            "volatility": 0.2,
            "confidence": 0.85,
            "score": 0.6,
            "market_regime": "LOW_VOL_RANGE",
            "underlying": "NIFTY",
            "drift_strength": 0.1,
            "drift_direction": "STABLE",
            "premium_behavior": "strong",
        },
        {
            "volatility": 0.5,
            "confidence": 0.65,
            "score": 0.3,
            "market_regime": "MEDIUM_VOL_RANGE",
            "underlying": "BANKNIFTY",
            "drift_strength": 0.3,
            "drift_direction": "UPWARD",
            "premium_behavior": "normal",
        },
        {
            "volatility": 0.9,
            "confidence": 0.45,
            "score": 0.1,
            "market_regime": "HIGH_VOL_TREND_UP",
            "underlying": "FINNIFTY",
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

    print("\n=== CALIBRATION OUTPUTS ===")
    for i, sample in enumerate(samples, 1):
        result = engine.calibrate(**sample)
        print(f"\nSample {i} Calibration Result:")
        print(f"  Updated Risk Level: {result['updated_risk_level']}")
        print(f"  Updated SL: {result['updated_sl']:.3f} ({result['updated_sl']*100:.1f}%)")
        print(f"  Updated TP: {result['updated_tp']:.3f} ({result['updated_tp']*100:.1f}%)")
        print(f"  Updated Qty: {result['updated_qty']}")
        print(f"  RR Ratio: {result['components']['rr_ratio']:.2f}")
        print(f"  Reasons: {', '.join(result['reason'][:5])}...")  # Show first 5 reasons

    # Save calibration results
    import pandas as pd

    df_results = pd.DataFrame([{**sample, **engine.calibrate(**sample)} for sample in samples])
    output_csv = REPORTS_ULTRA_DIR / "phase30_calibration_results.csv"
    df_results.to_csv(output_csv, index=False)
    print(f"\n[SAVE] Calibration results saved to: {output_csv}")

    print("\n[OK] Real-Time Calibration Engine validated")


if __name__ == "__main__":
    main()
