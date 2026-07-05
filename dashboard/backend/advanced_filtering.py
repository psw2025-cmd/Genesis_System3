"""
Advanced Filtering & Search System
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class AdvancedFiltering:
    """
    Advanced filtering and search system
    """

    def __init__(self):
        self.saved_filters = {}

    def filter_option_chain(self, contracts: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter option chain contracts

        Args:
            contracts: List of contracts
            filters: Filter criteria

        Returns:
            Filtered contracts
        """
        filtered = contracts

        # Strike range filter
        if "strike_range" in filters:
            min_strike = filters["strike_range"].get("min", 0)
            max_strike = filters["strike_range"].get("max", 999999)
            filtered = [c for c in filtered if min_strike <= c.get("strike", 0) <= max_strike]

        # Expiry filter
        if "expiries" in filters and filters["expiries"]:
            filtered = [c for c in filtered if c.get("expiry") in filters["expiries"]]

        # Near ATM filter
        if filters.get("near_atm", False) and contracts:
            spot = next((c.get("spot_price", 0) for c in contracts if c.get("spot_price")), 0)
            if spot > 0:
                atm_range = spot * 0.05  # 5% range
                filtered = [c for c in filtered if abs(c.get("strike", 0) - spot) <= atm_range]

        # OI threshold
        if "oi_min" in filters:
            filtered = [c for c in filtered if c.get("oi", 0) >= filters["oi_min"]]

        # Volume threshold
        if "volume_min" in filters:
            filtered = [c for c in filtered if c.get("volume", 0) >= filters["volume_min"]]

        # IV range
        if "iv_range" in filters:
            min_iv = filters["iv_range"].get("min", 0)
            max_iv = filters["iv_range"].get("max", 10)
            filtered = [c for c in filtered if min_iv <= c.get("iv", 0) <= max_iv]

        # Delta range
        if "delta_range" in filters:
            min_delta = filters["delta_range"].get("min", -1)
            max_delta = filters["delta_range"].get("max", 1)
            filtered = [c for c in filtered if min_delta <= c.get("delta", 0) <= max_delta]

        # Gamma range
        if "gamma_range" in filters:
            min_gamma = filters["gamma_range"].get("min", 0)
            max_gamma = filters["gamma_range"].get("max", 1)
            filtered = [c for c in filtered if min_gamma <= c.get("gamma", 0) <= max_gamma]

        # Option type filter
        if "option_types" in filters and filters["option_types"]:
            filtered = [c for c in filtered if c.get("option_type") in filters["option_types"]]

        # Liquidity threshold
        if "liquidity_min" in filters:
            filtered = [c for c in filtered if (c.get("oi", 0) + c.get("volume", 0)) >= filters["liquidity_min"]]

        return filtered

    def filter_positions(self, positions: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter positions

        Args:
            positions: List of positions
            filters: Filter criteria

        Returns:
            Filtered positions
        """
        filtered = positions

        # Underlying filter
        if "underlyings" in filters and filters["underlyings"]:
            filtered = [p for p in filtered if p.get("underlying") in filters["underlyings"]]

        # PnL range
        if "pnl_range" in filters:
            min_pnl = filters["pnl_range"].get("min", -999999)
            max_pnl = filters["pnl_range"].get("max", 999999)
            filtered = [p for p in filtered if min_pnl <= p.get("unrealized_pnl", 0) <= max_pnl]

        # Entry date range
        if "entry_date_range" in filters:
            min_date = filters["entry_date_range"].get("min")
            max_date = filters["entry_date_range"].get("max")
            if min_date or max_date:
                filtered = [p for p in filtered if self._date_in_range(p.get("entry_time"), min_date, max_date)]

        # Strategy filter
        if "strategies" in filters and filters["strategies"]:
            filtered = [p for p in filtered if p.get("strategy") in filters["strategies"]]

        # Profit/Loss filter
        if "pnl_type" in filters:
            if filters["pnl_type"] == "profit":
                filtered = [p for p in filtered if p.get("unrealized_pnl", 0) > 0]
            elif filters["pnl_type"] == "loss":
                filtered = [p for p in filtered if p.get("unrealized_pnl", 0) < 0]

        return filtered

    def filter_signals(self, signals: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter trade signals

        Args:
            signals: List of signals
            filters: Filter criteria

        Returns:
            Filtered signals
        """
        filtered = signals

        # Confidence threshold
        if "confidence_min" in filters:
            filtered = [s for s in filtered if s.get("confidence", 0) >= filters["confidence_min"]]

        # Underlying filter
        if "underlyings" in filters and filters["underlyings"]:
            filtered = [s for s in filtered if s.get("underlying") in filters["underlyings"]]

        # Strategy type
        if "strategy_types" in filters and filters["strategy_types"]:
            filtered = [s for s in filtered if s.get("strategy") in filters["strategy_types"]]

        # Action filter
        if "actions" in filters and filters["actions"]:
            filtered = [s for s in filtered if s.get("action") in filters["actions"]]

        return filtered

    def save_filter_preset(self, name: str, filter_config: Dict[str, Any], filter_type: str = "option_chain") -> bool:
        """Save a filter preset"""
        key = f"{filter_type}_{name}"
        self.saved_filters[key] = {
            "name": name,
            "type": filter_type,
            "config": filter_config,
            "created": datetime.now().isoformat(),
        }
        return True

    def get_filter_presets(self, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get saved filter presets"""
        if filter_type:
            return [v for k, v in self.saved_filters.items() if v.get("type") == filter_type]
        return list(self.saved_filters.values())

    def delete_filter_preset(self, name: str, filter_type: str) -> bool:
        """Delete a filter preset"""
        key = f"{filter_type}_{name}"
        if key in self.saved_filters:
            del self.saved_filters[key]
            return True
        return False

    def _date_in_range(self, date_str: Optional[str], min_date: Optional[str], max_date: Optional[str]) -> bool:
        """Check if date is in range"""
        if not date_str:
            return False

        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if min_date:
                min_dt = datetime.fromisoformat(min_date.replace("Z", "+00:00"))
                if date < min_dt:
                    return False
            if max_date:
                max_dt = datetime.fromisoformat(max_date.replace("Z", "+00:00"))
                if date > max_dt:
                    return False
            return True
        except:
            return True  # If parsing fails, include it


# Global instance
_advanced_filtering = AdvancedFiltering()


def get_advanced_filtering() -> AdvancedFiltering:
    """Get global advanced filtering instance"""
    return _advanced_filtering
