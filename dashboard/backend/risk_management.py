"""
Risk Management Dashboard
VaR, Expected Shortfall, Risk Metrics
"""

import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone("Asia/Kolkata")


class RiskManagement:
    """
    Risk management and metrics calculation
    """

    def calculate_var(self, returns: List[float], confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR)

        Args:
            returns: List of returns
            confidence_level: Confidence level (0.95 = 95%)

        Returns:
            VaR metrics
        """
        if not returns or len(returns) < 2:
            return {"var": 0.0, "confidence": confidence_level}

        returns_array = np.array(returns)

        # Historical VaR
        var_historical = np.percentile(returns_array, (1 - confidence_level) * 100)

        # Parametric VaR (assuming normal distribution)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        var_parametric = mean_return - std_return * np.abs(
            np.percentile(np.random.normal(0, 1, 10000), (1 - confidence_level) * 100)
        )

        return {
            "var_historical": float(var_historical),
            "var_parametric": float(var_parametric),
            "var": float(var_historical),  # Use historical as default
            "confidence": confidence_level,
            "mean": float(mean_return),
            "std": float(std_return),
        }

    def calculate_expected_shortfall(self, returns: List[float], confidence_level: float = 0.95) -> Dict[str, float]:
        """
        Calculate Expected Shortfall (Conditional VaR)

        Args:
            returns: List of returns
            confidence_level: Confidence level

        Returns:
            Expected Shortfall metrics
        """
        if not returns or len(returns) < 2:
            return {"es": 0.0, "confidence": confidence_level}

        returns_array = np.array(returns)
        var = np.percentile(returns_array, (1 - confidence_level) * 100)

        # Expected Shortfall = mean of returns below VaR
        tail_returns = returns_array[returns_array <= var]
        es = np.mean(tail_returns) if len(tail_returns) > 0 else var

        return {
            "es": float(es),
            "var": float(var),
            "confidence": confidence_level,
            "tail_observations": len(tail_returns),
        }

    def calculate_portfolio_risk(
        self, positions: List[Dict[str, Any]], market_data: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate portfolio risk metrics

        Args:
            positions: List of positions
            market_data: Current market prices

        Returns:
            Portfolio risk metrics
        """
        if not positions:
            return {
                "total_exposure": 0.0,
                "total_pnl": 0.0,
                "var": 0.0,
                "expected_shortfall": 0.0,
                "max_drawdown": 0.0,
                "concentration_risk": 0.0,
            }

        # Calculate exposures
        total_exposure = 0.0
        total_pnl = 0.0
        underlying_exposures = {}

        for pos in positions:
            entry_price = pos.get("entry_price", 0)
            qty = pos.get("qty", 0)
            underlying = pos.get("underlying", "UNKNOWN")
            exposure = abs(entry_price * qty)
            pnl = pos.get("unrealized_pnl", 0)

            total_exposure += exposure
            total_pnl += pnl

            if underlying not in underlying_exposures:
                underlying_exposures[underlying] = 0.0
            underlying_exposures[underlying] += exposure

        # Concentration risk (max exposure to single underlying)
        max_underlying_exposure = max(underlying_exposures.values()) if underlying_exposures else 0
        concentration_risk = (max_underlying_exposure / total_exposure * 100) if total_exposure > 0 else 0

        # Calculate returns for VaR/ES
        returns = []
        for pos in positions:
            entry_price = pos.get("entry_price", 0)
            current_price = pos.get("current_price", entry_price)
            if entry_price > 0:
                ret = (current_price - entry_price) / entry_price
                returns.append(ret)

        # VaR and Expected Shortfall
        var_metrics = self.calculate_var(returns) if returns else {"var": 0.0}
        es_metrics = self.calculate_expected_shortfall(returns) if returns else {"es": 0.0}

        # Greeks exposure
        total_delta = sum(pos.get("delta", 0) * pos.get("qty", 0) for pos in positions)
        total_gamma = sum(pos.get("gamma", 0) * pos.get("qty", 0) for pos in positions)
        total_theta = sum(pos.get("theta", 0) * pos.get("qty", 0) for pos in positions)
        total_vega = sum(pos.get("vega", 0) * pos.get("qty", 0) for pos in positions)

        return {
            "total_exposure": round(total_exposure, 2),
            "total_pnl": round(total_pnl, 2),
            "var_95": round(var_metrics.get("var", 0) * total_exposure, 2) if total_exposure > 0 else 0.0,
            "expected_shortfall_95": round(es_metrics.get("es", 0) * total_exposure, 2) if total_exposure > 0 else 0.0,
            "concentration_risk": round(concentration_risk, 2),
            "position_count": len(positions),
            "underlying_exposures": {k: round(v, 2) for k, v in underlying_exposures.items()},
            "greeks_exposure": {
                "delta": round(total_delta, 4),
                "gamma": round(total_gamma, 4),
                "theta": round(total_theta, 4),
                "vega": round(total_vega, 4),
            },
            "max_underlying_exposure": round(max_underlying_exposure, 2),
        }

    def check_risk_limits(self, positions: List[Dict[str, Any]], risk_limits: Dict[str, float]) -> Dict[str, Any]:
        """
        Check if risk limits are breached

        Args:
            positions: List of positions
            risk_limits: Risk limit configuration

        Returns:
            Risk limit status
        """
        portfolio_risk = self.calculate_portfolio_risk(positions)

        breaches = []
        warnings = []

        # Max positions
        max_positions = risk_limits.get("max_positions", 5)
        if len(positions) > max_positions:  # Breach only when EXCEEDING limit, not when equal
            breaches.append(
                {"limit": "max_positions", "value": len(positions), "limit_value": max_positions, "severity": "error"}
            )
        elif len(positions) == max_positions:
            # At limit - add warning but not breach
            warnings.append(
                {
                    "limit": "max_positions",
                    "value": len(positions),
                    "limit_value": max_positions,
                    "severity": "warning",
                    "message": "At limit",
                }
            )

        # Max exposure
        max_exposure = risk_limits.get("max_exposure", 100000)
        if portfolio_risk["total_exposure"] > max_exposure:
            breaches.append(
                {
                    "limit": "max_exposure",
                    "value": portfolio_risk["total_exposure"],
                    "limit_value": max_exposure,
                    "severity": "error",
                }
            )
        elif portfolio_risk["total_exposure"] > max_exposure * 0.8:
            warnings.append(
                {
                    "limit": "max_exposure",
                    "value": portfolio_risk["total_exposure"],
                    "limit_value": max_exposure,
                    "severity": "warning",
                }
            )

        # Max loss
        max_loss = risk_limits.get("max_loss", -5000)
        if portfolio_risk["total_pnl"] < max_loss:
            breaches.append(
                {
                    "limit": "max_loss",
                    "value": portfolio_risk["total_pnl"],
                    "limit_value": max_loss,
                    "severity": "error",
                }
            )

        # Concentration risk
        max_concentration = risk_limits.get("max_concentration_pct", 50)
        if portfolio_risk["concentration_risk"] > max_concentration:
            breaches.append(
                {
                    "limit": "max_concentration",
                    "value": portfolio_risk["concentration_risk"],
                    "limit_value": max_concentration,
                    "severity": "error",
                }
            )
        elif portfolio_risk["concentration_risk"] > max_concentration * 0.8:
            warnings.append(
                {
                    "limit": "max_concentration",
                    "value": portfolio_risk["concentration_risk"],
                    "limit_value": max_concentration,
                    "severity": "warning",
                }
            )

        return {
            "status": "PASS" if not breaches else "FAIL",
            "breaches": breaches,
            "warnings": warnings,
            "portfolio_risk": portfolio_risk,
            "timestamp": datetime.now(IST).isoformat(),
        }


# Global instance
_risk_management = RiskManagement()


def get_risk_management() -> RiskManagement:
    """Get global risk management instance"""
    return _risk_management
