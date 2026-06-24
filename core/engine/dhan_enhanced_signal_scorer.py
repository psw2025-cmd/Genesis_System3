"""
Dhan Index Options - Enhanced Signal Scoring Engine

Provides advanced signal scoring beyond basic confidence and expected_move_score.
Includes:
- Multi-factor scoring
- Risk-adjusted scores
- Market condition adjustments
- Historical performance weighting
"""

from typing import Any, Dict

import numpy as np
import pandas as pd

from core.engine.dhan_trade_config import DEFAULT_THRESHOLDS


class EnhancedSignalScorer:
    """Enhanced signal scoring with multiple factors."""

    def __init__(self):
        self.weights = {
            "confidence": 0.30,
            "expected_move": 0.25,
            "moneyness": 0.15,
            "volatility": 0.10,
            "momentum": 0.10,
            "risk_reward": 0.10,
        }

    def compute_enhanced_score(self, signal_row: pd.Series) -> Dict[str, Any]:
        """
        Compute enhanced score for a signal.

        Returns dict with:
        - base_score: original expected_move_score
        - enhanced_score: multi-factor score
        - components: breakdown of score components
        - risk_adjusted_score: risk-adjusted version
        """
        # Base components
        confidence = float(signal_row.get("pred_confidence", 0.0))
        base_score = float(signal_row.get("expected_move_score", 0.0))
        moneyness = abs(float(signal_row.get("moneyness", 0.0)))

        # Compute component scores
        conf_score = confidence * self.weights["confidence"]
        move_score = abs(base_score) * self.weights["expected_move"] * np.sign(base_score)

        # Moneyness score (prefer near ATM)
        moneyness_score = max(0, 1.0 - moneyness / 5.0) * self.weights["moneyness"]

        # Volatility proxy (using rolling std if available)
        vol_score = 0.0
        if "ltp_roll_std_5" in signal_row:
            vol = float(signal_row.get("ltp_roll_std_5", 0.0))
            vol_score = min(1.0, vol / 100.0) * self.weights["volatility"]

        # Momentum proxy (using change % if available)
        momentum_score = 0.0
        if "ltp_chg_1_pct" in signal_row:
            momentum = abs(float(signal_row.get("ltp_chg_1_pct", 0.0)))
            momentum_score = min(1.0, momentum / 5.0) * self.weights["momentum"]

        # Risk-reward (simplified)
        rr_score = 0.0
        if base_score != 0:
            # Assume 2:1 RR for positive scores, adjust for negative
            rr_ratio = 2.0 if base_score > 0 else 1.5
            rr_score = min(1.0, rr_ratio / 3.0) * self.weights["risk_reward"]

        # Combine scores
        enhanced_score = conf_score + move_score + moneyness_score + vol_score + momentum_score + rr_score

        # Risk adjustment (penalize far OTM, low confidence)
        risk_factor = 1.0
        if moneyness > 2.0:
            risk_factor *= 0.8  # Penalize far OTM
        if confidence < 0.75:
            risk_factor *= 0.9  # Penalize low confidence

        risk_adjusted_score = enhanced_score * risk_factor

        return {
            "base_score": base_score,
            "enhanced_score": enhanced_score,
            "risk_adjusted_score": risk_adjusted_score,
            "components": {
                "confidence": conf_score,
                "expected_move": move_score,
                "moneyness": moneyness_score,
                "volatility": vol_score,
                "momentum": momentum_score,
                "risk_reward": rr_score,
            },
            "risk_factor": risk_factor,
        }

    def rank_signals(self, df_signals: pd.DataFrame) -> pd.DataFrame:
        """Rank signals by enhanced score."""
        if df_signals.empty:
            return df_signals

        df = df_signals.copy()
        scores = []
        for _, row in df.iterrows():
            score_data = self.compute_enhanced_score(row)
            scores.append(score_data["risk_adjusted_score"])

        df["enhanced_score"] = scores
        df = df.sort_values("enhanced_score", ascending=False)

        return df


# Global scorer instance
_enhanced_scorer = None


def get_enhanced_scorer() -> EnhancedSignalScorer:
    """Get global enhanced scorer instance."""
    global _enhanced_scorer
    if _enhanced_scorer is None:
        _enhanced_scorer = EnhancedSignalScorer()
    return _enhanced_scorer
