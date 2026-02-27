"""
Enhanced Performance Prediction & Profit Validation System
Multi-validation for live trading conditions
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import pytz

IST = pytz.timezone("Asia/Kolkata")


class PerformancePredictor:
    """
    Enhanced performance prediction with multi-validation
    """

    def __init__(self):
        self.prediction_history = []
        self.actual_history = []
        self.validation_sources = []

    def predict_profit(self, position: Dict[str, Any], current_price: float, time_held: float = 0.0) -> Dict[str, Any]:
        """
        Predict profit for a position with multi-validation

        Args:
            position: Position dictionary
            current_price: Current market price
            time_held: Time position has been held (hours)

        Returns:
            Dict with predictions and validations
        """
        entry_price = position.get("entry_price", 0)
        qty = position.get("qty", position.get("quantity", 0))
        strike = position.get("strike", 0)
        option_type = position.get("option_type", "CE")
        expiry = position.get("expiry", "")
        underlying = position.get("underlying", "NIFTY")

        # Method 1: Simple P&L calculation
        simple_pnl = (current_price - entry_price) * qty

        # Method 2: Greeks-based prediction
        delta = position.get("delta", 0.5)
        gamma = position.get("gamma", 0)
        theta = position.get("theta", -0.1)
        vega = position.get("vega", 0)

        # Estimate price movement impact
        spot_change = current_price - entry_price if "spot_price" in position else 0
        delta_pnl = spot_change * delta * qty * 100  # For options

        # Theta decay (time value loss)
        hours_to_expiry = self._calculate_hours_to_expiry(expiry)
        theta_decay = abs(theta) * time_held * qty * 100

        # Gamma effect (convexity)
        gamma_effect = 0.5 * gamma * (spot_change**2) * qty * 100 if gamma else 0

        greeks_pnl = delta_pnl - theta_decay + gamma_effect

        # Method 3: Historical pattern prediction
        historical_prediction = self._predict_from_history(position, current_price)

        # Method 4: Volatility-based prediction
        iv = position.get("iv", 0.2)
        volatility_pnl = self._predict_from_volatility(entry_price, current_price, iv, time_held, qty)

        # Ensemble prediction (weighted average)
        predictions = {
            "simple": simple_pnl,
            "greeks": greeks_pnl,
            "historical": historical_prediction,
            "volatility": volatility_pnl,
        }

        # Weighted ensemble (adjust weights based on data availability)
        weights = {
            "simple": 0.3,
            "greeks": 0.4 if delta else 0.1,
            "historical": 0.2 if historical_prediction else 0.1,
            "volatility": 0.2 if iv else 0.1,
        }

        # Normalize weights
        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}

        ensemble_pnl = sum(predictions[k] * weights[k] for k in predictions)

        # Calculate confidence
        confidence = self._calculate_confidence(position, predictions, weights)

        # Risk metrics
        risk_metrics = self._calculate_risk_metrics(position, current_price, ensemble_pnl)

        return {
            "predicted_pnl": round(ensemble_pnl, 2),
            "predictions": {k: round(v, 2) for k, v in predictions.items()},
            "weights": {k: round(v, 3) for k, v in weights.items()},
            "confidence": round(confidence, 3),
            "risk_metrics": risk_metrics,
            "current_pnl": round(simple_pnl, 2),
            "method_breakdown": {
                "delta_contribution": round(delta_pnl, 2),
                "theta_decay": round(-theta_decay, 2),
                "gamma_effect": round(gamma_effect, 2),
            },
            "timestamp": datetime.now(IST).isoformat(),
        }

    def _calculate_hours_to_expiry(self, expiry: str) -> float:
        """Calculate hours until expiry"""
        try:
            if not expiry:
                return 24.0  # Default

            # Parse expiry date (format: DDMMMYYYY or DD-MMM-YYYY)
            expiry_date = datetime.strptime(expiry, "%d%b%Y")
            expiry_date = IST.localize(expiry_date.replace(hour=15, minute=30))
            now = datetime.now(IST)

            if expiry_date > now:
                return (expiry_date - now).total_seconds() / 3600.0
            return 0.0
        except:
            return 24.0  # Default fallback

    def _predict_from_history(self, position: Dict[str, Any], current_price: float) -> float:
        """Predict based on historical patterns"""
        # Use prediction history if available
        if len(self.prediction_history) > 10:
            # Calculate average prediction accuracy
            recent = self.prediction_history[-10:]
            avg_accuracy = sum(r.get("accuracy", 0.5) for r in recent) / len(recent)

            # Apply to current prediction
            entry_price = position.get("entry_price", 0)
            simple_pnl = (current_price - entry_price) * position.get("qty", 0)
            return simple_pnl * avg_accuracy

        return 0.0

    def _predict_from_volatility(
        self, entry_price: float, current_price: float, iv: float, time_held: float, qty: int
    ) -> float:
        """Predict based on implied volatility"""
        if iv <= 0 or entry_price <= 0:
            return 0.0

        # Expected move based on IV
        expected_move_pct = iv * math.sqrt(time_held / 24.0 / 365.0)  # Annualized IV

        # Price change
        price_change = current_price - entry_price
        price_change_pct = price_change / entry_price if entry_price > 0 else 0

        # Volatility-adjusted prediction
        if abs(price_change_pct) < expected_move_pct:
            # Within expected range
            volatility_pnl = price_change * qty
        else:
            # Beyond expected range - apply volatility scaling
            volatility_pnl = price_change * qty * (expected_move_pct / abs(price_change_pct))

        return volatility_pnl

    def _calculate_confidence(
        self, position: Dict[str, Any], predictions: Dict[str, float], weights: Dict[str, float]
    ) -> float:
        """Calculate prediction confidence"""
        confidence = 0.5  # Base confidence

        # Increase confidence if we have Greeks
        if position.get("delta") is not None:
            confidence += 0.2
        if position.get("gamma") is not None:
            confidence += 0.1
        if position.get("theta") is not None:
            confidence += 0.1
        if position.get("iv") is not None:
            confidence += 0.1

        # Check prediction consistency
        pnl_values = [v for v in predictions.values() if v != 0]
        if len(pnl_values) > 1:
            std_dev = math.sqrt(sum((v - sum(pnl_values) / len(pnl_values)) ** 2 for v in pnl_values) / len(pnl_values))
            avg = abs(sum(pnl_values) / len(pnl_values))
            if avg > 0:
                consistency = 1.0 - min(1.0, std_dev / avg)
                confidence *= 0.5 + consistency * 0.5

        return min(0.95, max(0.3, confidence))

    def _calculate_risk_metrics(
        self, position: Dict[str, Any], current_price: float, predicted_pnl: float
    ) -> Dict[str, float]:
        """Calculate risk metrics"""
        entry_price = position.get("entry_price", 0)
        stop_loss = position.get("stop_loss", 0)
        target = position.get("target", 0)
        qty = position.get("qty", 0)

        # Risk-reward ratio
        risk = abs(entry_price - stop_loss) * qty if stop_loss > 0 else abs(predicted_pnl) * 0.3
        reward = abs(target - entry_price) * qty if target > 0 else abs(predicted_pnl) * 0.5
        risk_reward = reward / risk if risk > 0 else 0.0

        # Maximum loss
        max_loss = (stop_loss - entry_price) * qty if stop_loss > 0 else predicted_pnl * -0.5

        # Probability of profit (simplified)
        prob_profit = 0.5
        if predicted_pnl > 0:
            prob_profit = min(0.9, 0.5 + (predicted_pnl / (abs(entry_price * qty) + 1)) * 0.4)
        elif predicted_pnl < 0:
            prob_profit = max(0.1, 0.5 - (abs(predicted_pnl) / (abs(entry_price * qty) + 1)) * 0.4)

        return {
            "risk_reward_ratio": round(risk_reward, 2),
            "max_loss": round(max_loss, 2),
            "probability_of_profit": round(prob_profit, 3),
            "current_drawdown": round(min(0, predicted_pnl), 2),
        }

    def validate_profit(
        self, position: Dict[str, Any], reported_pnl: float, validation_sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Multi-validate profit calculation against multiple sources

        Args:
            position: Position dictionary
            reported_pnl: PnL reported by system
            validation_sources: List of validation sources (broker, market data, etc.)

        Returns:
            Validation results
        """
        validations = []

        # Source 1: Internal calculation
        entry_price = position.get("entry_price", 0)
        current_price = position.get("current_price", entry_price)
        qty = position.get("qty", 0)
        internal_pnl = (current_price - entry_price) * qty
        validations.append(
            {
                "source": "internal",
                "pnl": internal_pnl,
                "difference": abs(reported_pnl - internal_pnl),
                "match": abs(reported_pnl - internal_pnl) < 0.01,
            }
        )

        # Source 2: Validation sources (broker, market data, etc.)
        for source in validation_sources:
            source_pnl = source.get("pnl", 0)
            source_name = source.get("name", "unknown")
            validations.append(
                {
                    "source": source_name,
                    "pnl": source_pnl,
                    "difference": abs(reported_pnl - source_pnl),
                    "match": abs(reported_pnl - source_pnl) < 0.01,
                }
            )

        # Calculate consensus
        all_pnls = [v["pnl"] for v in validations]
        consensus_pnl = sum(all_pnls) / len(all_pnls) if all_pnls else reported_pnl

        # Check if all sources agree
        all_match = all(v["match"] for v in validations)

        # Calculate confidence
        differences = [v["difference"] for v in validations]
        avg_difference = sum(differences) / len(differences) if differences else 0
        confidence = max(0.0, 1.0 - (avg_difference / (abs(consensus_pnl) + 1)))

        return {
            "reported_pnl": round(reported_pnl, 2),
            "consensus_pnl": round(consensus_pnl, 2),
            "validations": validations,
            "all_match": all_match,
            "confidence": round(confidence, 3),
            "average_difference": round(avg_difference, 2),
            "validation_status": "PASS" if all_match else "WARN" if confidence > 0.7 else "FAIL",
            "timestamp": datetime.now(IST).isoformat(),
        }

    def predict_portfolio_performance(
        self, positions: List[Dict[str, Any]], market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict overall portfolio performance

        Args:
            positions: List of positions
            market_data: Current market data

        Returns:
            Portfolio prediction
        """
        total_predicted_pnl = 0.0
        total_confidence = 0.0
        position_predictions = []

        for position in positions:
            current_price = market_data.get(
                position.get("symbol", ""), position.get("current_price", position.get("entry_price", 0))
            )

            prediction = self.predict_profit(position, current_price)
            total_predicted_pnl += prediction["predicted_pnl"]
            total_confidence += prediction["confidence"]
            position_predictions.append(prediction)

        avg_confidence = total_confidence / len(positions) if positions else 0.0

        # Portfolio risk metrics
        total_exposure = sum(abs(pos.get("entry_price", 0) * pos.get("qty", 0)) for pos in positions)

        portfolio_risk = {
            "total_exposure": round(total_exposure, 2),
            "predicted_pnl": round(total_predicted_pnl, 2),
            "pnl_percentage": round((total_predicted_pnl / total_exposure * 100) if total_exposure > 0 else 0, 2),
            "average_confidence": round(avg_confidence, 3),
            "position_count": len(positions),
        }

        return {
            "portfolio_prediction": portfolio_risk,
            "position_predictions": position_predictions,
            "timestamp": datetime.now(IST).isoformat(),
        }

    def update_prediction_history(self, prediction: Dict[str, Any], actual_pnl: float):
        """Update prediction history for learning"""
        accuracy = 1.0 - abs(prediction["predicted_pnl"] - actual_pnl) / (abs(actual_pnl) + 1)

        self.prediction_history.append(
            {
                "prediction": prediction,
                "actual_pnl": actual_pnl,
                "accuracy": accuracy,
                "timestamp": datetime.now(IST).isoformat(),
            }
        )

        # Keep only last 100 predictions
        if len(self.prediction_history) > 100:
            self.prediction_history = self.prediction_history[-100:]


# Global instance
_performance_predictor = PerformancePredictor()


def get_performance_predictor() -> PerformancePredictor:
    """Get global performance predictor instance"""
    return _performance_predictor
