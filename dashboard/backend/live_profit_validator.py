"""
Live Profit Validation System
Multi-source validation for real-time profit calculations
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import pytz

IST = pytz.timezone("Asia/Kolkata")


class LiveProfitValidator:
    """
    Multi-source profit validation for live trading conditions
    """

    def __init__(self):
        self.validation_cache = {}
        self.validation_history = []

    def validate_against_broker(self, position: Dict[str, Any], broker_api: Optional[Any] = None) -> Dict[str, Any]:
        """
        Validate profit against broker API

        Args:
            position: Position dictionary
            broker_api: Broker API instance (optional)

        Returns:
            Validation result
        """
        try:
            # If broker API is available, get real-time PnL
            if broker_api:
                symbol = position.get("symbol", "")
                broker_pnl = broker_api.get_position_pnl(symbol)
                return {
                    "source": "broker",
                    "pnl": broker_pnl,
                    "timestamp": datetime.now(IST).isoformat(),
                    "status": "SUCCESS",
                }
            else:
                # Fallback: calculate from position data
                entry_price = position.get("entry_price", 0)
                current_price = position.get("current_price", entry_price)
                qty = position.get("qty", 0)
                broker_pnl = (current_price - entry_price) * qty

                return {
                    "source": "broker_calculated",
                    "pnl": broker_pnl,
                    "timestamp": datetime.now(IST).isoformat(),
                    "status": "CALCULATED",
                }
        except Exception as e:
            return {
                "source": "broker",
                "pnl": 0.0,
                "error": str(e),
                "timestamp": datetime.now(IST).isoformat(),
                "status": "ERROR",
            }

    def validate_against_market_data(
        self, position: Dict[str, Any], market_data_source: str = "yahoo"
    ) -> Dict[str, Any]:
        """
        Validate profit against live market data

        Args:
            position: Position dictionary
            market_data_source: Market data source ('yahoo', 'nse', etc.)

        Returns:
            Validation result
        """
        try:
            underlying = position.get("underlying", "NIFTY")
            strike = position.get("strike", 0)
            option_type = position.get("option_type", "CE")
            expiry = position.get("expiry", "")

            # Get current spot price
            spot_price = self._get_live_spot_price(underlying, market_data_source)

            # Calculate option price from spot (simplified Black-Scholes approximation)
            option_price = self._calculate_option_price(spot_price, strike, option_type, expiry)

            entry_price = position.get("entry_price", 0)
            qty = position.get("qty", 0)
            market_pnl = (option_price - entry_price) * qty

            return {
                "source": f"market_{market_data_source}",
                "pnl": market_pnl,
                "spot_price": spot_price,
                "option_price": option_price,
                "timestamp": datetime.now(IST).isoformat(),
                "status": "SUCCESS",
            }
        except Exception as e:
            return {
                "source": f"market_{market_data_source}",
                "pnl": 0.0,
                "error": str(e),
                "timestamp": datetime.now(IST).isoformat(),
                "status": "ERROR",
            }

    def validate_against_historical(
        self, position: Dict[str, Any], historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate profit against historical patterns

        Args:
            position: Position dictionary
            historical_data: Historical position data

        Returns:
            Validation result
        """
        try:
            # Find similar historical positions
            similar_positions = self._find_similar_positions(position, historical_data)

            if not similar_positions:
                return {
                    "source": "historical",
                    "pnl": 0.0,
                    "timestamp": datetime.now(IST).isoformat(),
                    "status": "NO_DATA",
                }

            # Calculate average PnL from similar positions
            avg_pnl = sum(p.get("realized_pnl", 0) for p in similar_positions) / len(similar_positions)

            return {
                "source": "historical",
                "pnl": avg_pnl,
                "sample_size": len(similar_positions),
                "timestamp": datetime.now(IST).isoformat(),
                "status": "SUCCESS",
            }
        except Exception as e:
            return {
                "source": "historical",
                "pnl": 0.0,
                "error": str(e),
                "timestamp": datetime.now(IST).isoformat(),
                "status": "ERROR",
            }

    def multi_validate_profit(
        self, position: Dict[str, Any], reported_pnl: float, validation_sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Multi-validate profit from multiple sources

        Args:
            position: Position dictionary
            reported_pnl: Reported PnL to validate
            validation_sources: List of sources to use (default: all)

        Returns:
            Comprehensive validation result
        """
        if validation_sources is None:
            validation_sources = ["broker", "market", "historical", "internal"]

        validations = []

        # Internal calculation
        if "internal" in validation_sources:
            entry_price = position.get("entry_price", 0)
            current_price = position.get("current_price", entry_price)
            qty = position.get("qty", 0)
            internal_pnl = (current_price - entry_price) * qty
            validations.append({"source": "internal", "pnl": internal_pnl, "status": "SUCCESS"})

        # Broker validation
        if "broker" in validation_sources:
            broker_validation = self.validate_against_broker(position)
            validations.append(broker_validation)

        # Market data validation (skip if timeout risk)
        if "market" in validation_sources:
            try:
                market_validation = self.validate_against_market_data(position)
                validations.append(market_validation)
            except:
                # Skip market validation if it times out
                pass

        # Historical validation
        if "historical" in validation_sources:
            historical_data = self._load_historical_data()
            historical_validation = self.validate_against_historical(position, historical_data)
            validations.append(historical_validation)

        # Calculate consensus
        successful_validations = [v for v in validations if v.get("status") == "SUCCESS"]
        if successful_validations:
            pnl_values = [v["pnl"] for v in successful_validations]
            consensus_pnl = sum(pnl_values) / len(pnl_values)

            # Calculate differences
            differences = [abs(reported_pnl - pnl) for pnl in pnl_values]
            max_difference = max(differences) if differences else 0
            avg_difference = sum(differences) / len(differences) if differences else 0

            # Determine validation status
            if max_difference < 0.01:
                status = "PASS"
            elif max_difference < abs(consensus_pnl) * 0.05:  # Within 5%
                status = "WARN"
            else:
                status = "FAIL"

            # Calculate confidence
            confidence = max(0.0, 1.0 - (avg_difference / (abs(consensus_pnl) + 1)))
        else:
            consensus_pnl = reported_pnl
            max_difference = 0
            avg_difference = 0
            status = "NO_DATA"
            confidence = 0.0

        result = {
            "reported_pnl": round(reported_pnl, 2),
            "consensus_pnl": round(consensus_pnl, 2),
            "validations": validations,
            "max_difference": round(max_difference, 2),
            "average_difference": round(avg_difference, 2),
            "validation_status": status,
            "confidence": round(confidence, 3),
            "sources_used": len(successful_validations),
            "timestamp": datetime.now(IST).isoformat(),
        }

        # Store in history
        self.validation_history.append(result)
        if len(self.validation_history) > 1000:
            self.validation_history = self.validation_history[-1000:]

        return result

    def _get_live_spot_price(self, underlying: str, source: str = "yahoo") -> float:
        """Get live spot price from market data source"""
        try:
            if source == "yahoo":
                symbols = {
                    "NIFTY": "^NSEI",
                    "BANKNIFTY": "^NSEBANK",
                    "FINNIFTY": "^NSEFINNIFTY",
                    "MIDCPNIFTY": "^NSEMIDCP",
                    "SENSEX": "^BSESN",
                }

                yahoo_symbol = symbols.get(underlying.upper())
                if yahoo_symbol:
                    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
                    response = requests.get(url, timeout=2)  # Reduced timeout
                    if response.status_code == 200:
                        data = response.json()
                        if "chart" in data and "result" in data["chart"]:
                            result = data["chart"]["result"][0]
                            meta = result.get("meta", {})
                            return meta.get("regularMarketPrice", 0.0)

            return 0.0
        except:
            return 0.0

    def _calculate_option_price(self, spot: float, strike: float, option_type: str, expiry: str) -> float:
        """Calculate option price (simplified)"""
        if spot <= 0 or strike <= 0:
            return 0.0

        # Simplified intrinsic value calculation
        if option_type == "CE":
            intrinsic = max(0, spot - strike)
        else:  # PE
            intrinsic = max(0, strike - spot)

        # Add time value (simplified)
        time_value = spot * 0.02  # 2% of spot as time value

        return intrinsic + time_value

    def _find_similar_positions(
        self, position: Dict[str, Any], historical_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find similar historical positions"""
        similar = []

        underlying = position.get("underlying", "")
        option_type = position.get("option_type", "")
        strike_range = position.get("strike", 0) * 0.1  # Within 10% of strike

        for hist_pos in historical_data:
            if (
                hist_pos.get("underlying", "") == underlying
                and hist_pos.get("option_type", "") == option_type
                and abs(hist_pos.get("strike", 0) - position.get("strike", 0)) <= strike_range
            ):
                similar.append(hist_pos)

        return similar[:10]  # Return top 10 similar

    def _load_historical_data(self) -> List[Dict[str, Any]]:
        """Load historical position data"""
        try:
            from pathlib import Path

            ROOT_DIR = Path(__file__).parent.parent.parent
            pnl_file = ROOT_DIR / "outputs" / "paper_pnl.csv"

            if pnl_file.exists():
                import pandas as pd

                df = pd.read_csv(pnl_file)
                return df.to_dict("records")
        except:
            pass

        return []


# Global instance
_live_validator = LiveProfitValidator()


def get_live_validator() -> LiveProfitValidator:
    """Get global live validator instance"""
    return _live_validator
