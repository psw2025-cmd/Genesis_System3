from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd


class TradeRuleEngine:
    """
    Meta-rule engine that decides whether a signal row is tradable.

    It encapsulates:
    - basic eligibility checks (label, confidence, score, ATM distance)
    - sign alignment between score and action (CE up / PE down)
    - a composite trade_score for ranking

    For now this mirrors the previous logic in dhan_trade_decision.build_trade_plan
    so behaviour stays the same, but it is centralized here for future upgrades.
    """

    def __init__(self, thresholds: Any):
        self.t = thresholds

    def _compute_trade_score(self, row: pd.Series) -> float:
        label = row.get("pred_label", "HOLD")
        conf = float(row.get("pred_confidence", 0.0) or 0.0)
        score = float(row.get("expected_move_score", 0.0) or 0.0)
        moneyness = float(row.get("moneyness", 0.0) or 0.0)

        # Basic alignment: CE trades should have positive score, PE trades negative
        if label == "BUY_CE" and score <= 0:
            return 0.0
        if label == "BUY_PE" and score >= 0:
            return 0.0
        if label == "HOLD":
            return 0.0

        # Penalize far OTM/ITM (|moneyness| too large)
        m_penalty = 1.0 + max(0.0, abs(moneyness) - 1.0) * 0.5

        base = abs(score) * conf
        final_score = base / m_penalty
        return float(final_score)

    def evaluate(self, row: pd.Series) -> Dict[str, Any]:
        """
        Evaluate one signal row and decide if it's a trade candidate.

        Returns:
            {
              "eligible": bool,
              "reason": str,
              "action": "BUY_CE" | "BUY_PE" | "HOLD" | "AVOID",
              "action_confidence": float,
              "trade_score": float,
            }
        """
        label = str(row.get("pred_label", "HOLD") or "HOLD")
        conf = float(row.get("pred_confidence", 0.0) or 0.0)
        score = float(row.get("expected_move_score", 0.0) or 0.0)
        moneyness = float(row.get("moneyness", 0.0) or 0.0)

        # Default response
        decision: Dict[str, Any] = {
            "eligible": False,
            "reason": "",
            "action": "HOLD",
            "action_confidence": conf,
            "trade_score": 0.0,
        }

        if label not in ("BUY_CE", "BUY_PE"):
            decision["reason"] = "label_not_buy"
            decision["action"] = "HOLD"
            return decision

        if conf < float(self.t.min_confidence):
            decision["reason"] = f"low_confidence({conf:.3f}<{self.t.min_confidence:.3f})"
            decision["action"] = label
            return decision

        if abs(score) < float(self.t.min_abs_score):
            decision["reason"] = f"low_score({abs(score):.3f}<{self.t.min_abs_score:.3f})"
            decision["action"] = label
            return decision

        if abs(moneyness) > float(self.t.max_atm_dist_pct):
            decision["reason"] = f"too_far_from_atm(|{moneyness:.3f}|>{self.t.max_atm_dist_pct:.3f})"
            decision["action"] = label
            return decision

        trade_score = self._compute_trade_score(row)
        if trade_score <= 0:
            decision["reason"] = "non_positive_trade_score"
            decision["action"] = label
            return decision

        # Passed all checks
        decision.update(
            {
                "eligible": True,
                "reason": "ok",
                "action": label,
                "action_confidence": conf,
                "trade_score": trade_score,
            }
        )
        return decision
