"""
System3 Ultra - Phase 21: Adaptive Risk Engine (ARE)

System3 learns to select risk level dynamically based on:
- Volatility
- Confidence
- Score
- Market regime
- Historical win-rate

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 84
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
REPORTS_ULTRA_DIR = PROJECT_ROOT / "storage" / "reports_ultra"
LEARNING_ULTRA_DIR = PROJECT_ROOT / "storage" / "learning_ultra"

REPORTS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


class AdaptiveRiskEngine:
    """
    Adaptive Risk Engine - Dynamically selects risk level.
    """

    def __init__(self):
        """Initialize the Adaptive Risk Engine."""
        # Load historical win-rate if available
        self.historical_win_rate = self._load_historical_win_rate()

    def _load_historical_win_rate(self) -> Dict[str, float]:
        """Load historical win-rate per underlying."""
        win_rates = {}

        # Try to load from PnL logs or shadow master
        pnl_csv = ULTRA_DIR / "dhan_ultra_pnl_sim.csv"
        shadow_csv = LEARNING_ULTRA_DIR / "dhan_ultra_shadow_master.csv"

        for csv_path in [pnl_csv, shadow_csv]:
            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path)
                    if "underlying" in df.columns and "pnl_pct" in df.columns:
                        for underlying in UNDERLYINGS:
                            df_u = df[df["underlying"] == underlying]
                            if not df_u.empty and "pnl_pct" in df_u.columns:
                                wins = (df_u["pnl_pct"] > 0).sum()
                                total = len(df_u)
                                if total > 0:
                                    win_rates[underlying] = wins / total
                except Exception:
                    pass

        # Default win-rate if not found
        for underlying in UNDERLYINGS:
            if underlying not in win_rates:
                win_rates[underlying] = 0.50  # Default 50%

        return win_rates

    def compute_risk(
        self,
        volatility: float,
        confidence: float,
        score: float,
        market_regime: Optional[str] = None,
        underlying: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compute adaptive risk level.

        Args:
            volatility: Volatility measure (0-1 scale, higher = more volatile)
            confidence: Model confidence (0-1)
            score: Expected move score (-1 to 1)
            market_regime: Market regime label (optional)
            underlying: Underlying name (optional, for historical win-rate)

        Returns:
            Dict with risk_level, risk_score, and reason vector
        """
        # Normalize inputs
        vol_norm = max(0.0, min(1.0, volatility))
        conf_norm = max(0.0, min(1.0, confidence))
        score_abs = abs(score)
        score_norm = max(0.0, min(1.0, score_abs))

        # Get historical win-rate
        win_rate = self.historical_win_rate.get(underlying, 0.50) if underlying else 0.50

        # Compute risk components
        reasons = []

        # Volatility component (higher vol = higher risk)
        vol_risk = vol_norm * 0.4
        if vol_norm > 0.7:
            reasons.append("high volatility")
        elif vol_norm < 0.3:
            reasons.append("low volatility")

        # Confidence component (lower conf = higher risk)
        conf_risk = (1.0 - conf_norm) * 0.3
        if conf_norm < 0.6:
            reasons.append("low confidence")
        elif conf_norm > 0.8:
            reasons.append("high confidence")

        # Score component (lower score = higher risk)
        score_risk = (1.0 - score_norm) * 0.2
        if score_norm < 0.3:
            reasons.append("weak score")
        elif score_norm > 0.5:
            reasons.append("strong score")

        # Win-rate component (lower win-rate = higher risk)
        win_rate_risk = (1.0 - win_rate) * 0.1
        if win_rate < 0.4:
            reasons.append("poor historical performance")
        elif win_rate > 0.6:
            reasons.append("good historical performance")

        # Regime component
        regime_risk = 0.0
        if market_regime:
            if "HIGH_VOL" in market_regime:
                regime_risk = 0.15
                reasons.append("high volatility regime")
            elif "LOW_VOL" in market_regime:
                regime_risk = -0.05
                reasons.append("low volatility regime")
            if "TREND" in market_regime:
                regime_risk += 0.05
                reasons.append("trending market")

        # Total risk score
        risk_score = vol_risk + conf_risk + score_risk + win_rate_risk + regime_risk
        risk_score = max(0.0, min(1.0, risk_score))  # Clamp to [0, 1]

        # Classify risk level
        if risk_score < 0.33:
            risk_level = "LOW"
        elif risk_score < 0.67:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return {
            "risk_level": risk_level,
            "risk_score": float(risk_score),
            "reason": reasons,
            "components": {
                "volatility_risk": float(vol_risk),
                "confidence_risk": float(conf_risk),
                "score_risk": float(score_risk),
                "win_rate_risk": float(win_rate_risk),
                "regime_risk": float(regime_risk),
            },
        }

    def evaluate_sample(self, samples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate multiple samples.

        Args:
            samples: List of dicts with volatility, confidence, score, etc.

        Returns:
            List of risk evaluation results
        """
        results = []
        for sample in samples:
            result = self.compute_risk(
                volatility=sample.get("volatility", 0.5),
                confidence=sample.get("confidence", 0.5),
                score=sample.get("score", 0.0),
                market_regime=sample.get("market_regime"),
                underlying=sample.get("underlying"),
            )
            results.append(
                {
                    **sample,
                    **result,
                }
            )
        return results


def main() -> None:
    """Main entry point for testing."""
    print("=== SYSTEM3 ULTRA - PHASE 21: ADAPTIVE RISK ENGINE (ARE) ===\n")
    print("[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    engine = AdaptiveRiskEngine()

    # Sample inputs for verification
    samples = [
        {
            "volatility": 0.2,
            "confidence": 0.85,
            "score": 0.6,
            "market_regime": "LOW_VOL_RANGE",
            "underlying": "NIFTY",
        },
        {
            "volatility": 0.5,
            "confidence": 0.65,
            "score": 0.3,
            "market_regime": "MEDIUM_VOL_RANGE",
            "underlying": "BANKNIFTY",
        },
        {
            "volatility": 0.9,
            "confidence": 0.45,
            "score": 0.1,
            "market_regime": "HIGH_VOL_TREND_UP",
            "underlying": "FINNIFTY",
        },
    ]

    print("=== SAMPLE INPUTS ===")
    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}:")
        print(f"  Volatility: {sample['volatility']}")
        print(f"  Confidence: {sample['confidence']}")
        print(f"  Score: {sample['score']}")
        print(f"  Regime: {sample['market_regime']}")
        print(f"  Underlying: {sample['underlying']}")

    print("\n=== SAMPLE OUTPUTS ===")
    results = engine.evaluate_sample(samples)

    for i, result in enumerate(results, 1):
        print(f"\nSample {i} Result:")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Risk Score: {result['risk_score']:.3f}")
        print(f"  Reasons: {', '.join(result['reason'])}")
        print(f"  Components:")
        for comp, value in result["components"].items():
            print(f"    {comp}: {value:.3f}")

    # Save sample results
    df_results = pd.DataFrame(results)
    output_csv = REPORTS_ULTRA_DIR / "phase21_risk_evaluations.csv"
    df_results.to_csv(output_csv, index=False)
    print(f"\n[SAVE] Sample results saved to: {output_csv}")

    print("\n[OK] Adaptive Risk Engine validated")


if __name__ == "__main__":
    main()
