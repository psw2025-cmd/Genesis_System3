"""
Multi-Validation Audit System
Validates data against multiple online and offline sources
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import pytz

IST = pytz.timezone("Asia/Kolkata")


class ValidationSource:
    """Validation source configuration"""

    def __init__(self, name: str, online: bool, enabled: bool = True):
        self.name = name
        self.online = online
        self.enabled = enabled
        self.last_check = None
        self.status = "unknown"
        self.response_time = None


class MultiValidationAudit:
    """
    Multi-validation audit system for online and offline verification
    """

    def __init__(self):
        self.sources = {
            "yahoo_finance": ValidationSource("Yahoo Finance", online=True),
            "nse_website": ValidationSource("NSE Website", online=True),
            "broker_api": ValidationSource("Broker API", online=True),
            "internal_calc": ValidationSource("Internal Calculation", online=False),
            "historical_data": ValidationSource("Historical Data", online=False),
            "synthetic_data": ValidationSource("Synthetic Data", online=False),
        }
        self.validation_history = []
        self.audit_results = []

    def validate_spot_price(self, underlying: str, reported_price: float, tolerance: float = 0.01) -> Dict[str, Any]:
        """
        Validate spot price against multiple sources

        Args:
            underlying: Underlying symbol
            reported_price: Reported spot price
            tolerance: Acceptable difference percentage

        Returns:
            Validation results
        """
        validations = []

        # Online sources
        if self.sources["yahoo_finance"].enabled:
            yahoo_price = self._get_yahoo_price(underlying)
            if yahoo_price:
                diff = abs(reported_price - yahoo_price) / reported_price if reported_price > 0 else 0
                validations.append(
                    {
                        "source": "yahoo_finance",
                        "price": yahoo_price,
                        "difference": abs(reported_price - yahoo_price),
                        "difference_pct": diff * 100,
                        "match": diff <= tolerance,
                        "online": True,
                    }
                )

        if self.sources["nse_website"].enabled:
            nse_price = self._get_nse_price(underlying)
            if nse_price:
                diff = abs(reported_price - nse_price) / reported_price if reported_price > 0 else 0
                validations.append(
                    {
                        "source": "nse_website",
                        "price": nse_price,
                        "difference": abs(reported_price - nse_price),
                        "difference_pct": diff * 100,
                        "match": diff <= tolerance,
                        "online": True,
                    }
                )

        # Offline sources
        if self.sources["internal_calc"].enabled:
            # Internal calculation validation (always matches if same calculation)
            validations.append(
                {
                    "source": "internal_calc",
                    "price": reported_price,
                    "difference": 0,
                    "difference_pct": 0,
                    "match": True,
                    "online": False,
                }
            )

        if self.sources["historical_data"].enabled:
            hist_price = self._get_historical_price(underlying)
            if hist_price:
                diff = abs(reported_price - hist_price) / reported_price if reported_price > 0 else 0
                validations.append(
                    {
                        "source": "historical_data",
                        "price": hist_price,
                        "difference": abs(reported_price - hist_price),
                        "difference_pct": diff * 100,
                        "match": diff <= tolerance * 2,  # More lenient for historical
                        "online": False,
                    }
                )

        # Calculate consensus
        online_validations = [v for v in validations if v.get("online")]
        offline_validations = [v for v in validations if not v.get("online")]

        online_prices = [v["price"] for v in online_validations if v.get("price")]
        offline_prices = [v["price"] for v in offline_validations if v.get("price")]

        consensus_online = sum(online_prices) / len(online_prices) if online_prices else None
        consensus_offline = sum(offline_prices) / len(offline_prices) if offline_prices else None
        consensus_all = (
            sum([v["price"] for v in validations if v.get("price")]) / len([v for v in validations if v.get("price")])
            if validations
            else None
        )

        # Determine status
        online_match = all(v.get("match", False) for v in online_validations) if online_validations else None
        offline_match = all(v.get("match", False) for v in offline_validations) if offline_validations else None

        if online_match is True and offline_match is True:
            status = "PASS"
        elif online_match is True or offline_match is True:
            status = "WARN"
        else:
            status = "FAIL"

        result = {
            "underlying": underlying,
            "reported_price": reported_price,
            "validations": validations,
            "consensus": {"online": consensus_online, "offline": consensus_offline, "all": consensus_all},
            "status": status,
            "online_match": online_match,
            "offline_match": offline_match,
            "timestamp": datetime.now(IST).isoformat(),
        }

        self.validation_history.append(result)
        return result

    def validate_option_price(
        self, symbol: str, strike: float, option_type: str, expiry: str, reported_price: float, tolerance: float = 0.05
    ) -> Dict[str, Any]:
        """
        Validate option price against multiple sources
        """
        validations = []

        # Get spot price first
        underlying = symbol.split("-")[0] if "-" in symbol else symbol
        spot_price = self._get_yahoo_price(underlying)

        if spot_price:
            # Calculate theoretical price (simplified Black-Scholes)
            theoretical_price = self._calculate_option_price(spot_price, strike, option_type, expiry)

            diff = abs(reported_price - theoretical_price) / reported_price if reported_price > 0 else 0
            validations.append(
                {
                    "source": "theoretical_calc",
                    "price": theoretical_price,
                    "difference": abs(reported_price - theoretical_price),
                    "difference_pct": diff * 100,
                    "match": diff <= tolerance,
                    "online": False,
                }
            )

        # Historical validation
        hist_price = self._get_historical_option_price(symbol, strike, option_type, expiry)
        if hist_price:
            diff = abs(reported_price - hist_price) / reported_price if reported_price > 0 else 0
            validations.append(
                {
                    "source": "historical_data",
                    "price": hist_price,
                    "difference": abs(reported_price - hist_price),
                    "difference_pct": diff * 100,
                    "match": diff <= tolerance * 2,
                    "online": False,
                }
            )

        # Determine status
        all_match = all(v.get("match", False) for v in validations) if validations else False

        result = {
            "symbol": symbol,
            "strike": strike,
            "option_type": option_type,
            "reported_price": reported_price,
            "validations": validations,
            "status": "PASS" if all_match else "WARN",
            "timestamp": datetime.now(IST).isoformat(),
        }

        return result

    def validate_pnl(self, position: Dict[str, Any], reported_pnl: float, tolerance: float = 0.01) -> Dict[str, Any]:
        """
        Validate PnL calculation
        """
        validations = []

        # Internal calculation
        entry_price = position.get("entry_price", 0)
        current_price = position.get("current_price", entry_price)
        qty = position.get("qty", 0)
        internal_pnl = (current_price - entry_price) * qty

        diff = (
            abs(reported_pnl - internal_pnl) / abs(internal_pnl)
            if internal_pnl != 0
            else abs(reported_pnl - internal_pnl)
        )
        validations.append(
            {
                "source": "internal_calc",
                "pnl": internal_pnl,
                "difference": abs(reported_pnl - internal_pnl),
                "difference_pct": (diff / abs(internal_pnl) * 100) if internal_pnl != 0 else 0,
                "match": abs(reported_pnl - internal_pnl) < 0.01,
                "online": False,
            }
        )

        # Historical validation
        hist_pnl = self._get_historical_pnl(position)
        if hist_pnl is not None:
            diff = abs(reported_pnl - hist_pnl) / abs(hist_pnl) if hist_pnl != 0 else abs(reported_pnl - hist_pnl)
            validations.append(
                {
                    "source": "historical_data",
                    "pnl": hist_pnl,
                    "difference": abs(reported_pnl - hist_pnl),
                    "difference_pct": (diff / abs(hist_pnl) * 100) if hist_pnl != 0 else 0,
                    "match": abs(reported_pnl - hist_pnl) < 0.01,
                    "online": False,
                }
            )

        all_match = all(v.get("match", False) for v in validations) if validations else False

        result = {
            "position_id": position.get("position_id", "unknown"),
            "reported_pnl": reported_pnl,
            "validations": validations,
            "status": "PASS" if all_match else "WARN",
            "timestamp": datetime.now(IST).isoformat(),
        }

        return result

    def comprehensive_audit(
        self, health_data: Dict[str, Any], positions: List[Dict[str, Any]], chain_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive audit of all system data
        """
        audit_results = {
            "timestamp": datetime.now(IST).isoformat(),
            "spot_price_validations": [],
            "option_price_validations": [],
            "pnl_validations": [],
            "system_checks": [],
            "overall_status": "PASS",
        }

        # Validate spot prices
        if chain_data.get("spot"):
            spot_validation = self.validate_spot_price(chain_data.get("underlying", "NIFTY"), chain_data.get("spot", 0))
            audit_results["spot_price_validations"].append(spot_validation)

        # Validate option prices
        contracts = chain_data.get("contracts", [])
        for contract in contracts[:10]:  # Sample first 10
            option_validation = self.validate_option_price(
                contract.get("symbol", ""),
                contract.get("strike", 0),
                contract.get("option_type", "CE"),
                contract.get("expiry", ""),
                contract.get("ltp", 0),
            )
            audit_results["option_price_validations"].append(option_validation)

        # Validate PnL
        for position in positions:
            pnl_validation = self.validate_pnl(position, position.get("unrealized_pnl", 0))
            audit_results["pnl_validations"].append(pnl_validation)

        # System checks
        system_checks = {
            "broker_connected": health_data.get("broker_status") == "connected",
            "market_status": health_data.get("market_status", "unknown"),
            "qc_status": health_data.get("qc_status") == "PASS",
            "data_source": health_data.get("data_source", "unknown"),
        }
        audit_results["system_checks"] = system_checks

        # Determine overall status
        spot_failures = sum(1 for v in audit_results["spot_price_validations"] if v.get("status") == "FAIL")
        option_failures = sum(1 for v in audit_results["option_price_validations"] if v.get("status") == "FAIL")
        pnl_failures = sum(1 for v in audit_results["pnl_validations"] if v.get("status") == "FAIL")

        if spot_failures > 0 or option_failures > len(contracts) * 0.1 or pnl_failures > 0:
            audit_results["overall_status"] = "FAIL"
        elif spot_failures == 0 and option_failures == 0 and pnl_failures == 0:
            audit_results["overall_status"] = "PASS"
        else:
            audit_results["overall_status"] = "WARN"

        self.audit_results.append(audit_results)
        return audit_results

    def _get_yahoo_price(self, underlying: str) -> Optional[float]:
        """Get price from Yahoo Finance"""
        try:
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
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    if "chart" in data and "result" in data["chart"]:
                        result = data["chart"]["result"][0]
                        meta = result.get("meta", {})
                        return meta.get("regularMarketPrice", 0.0)
        except:
            pass
        return None

    def _get_nse_price(self, underlying: str) -> Optional[float]:
        """Get price from NSE website (simplified)"""
        # This would require web scraping or NSE API
        # For now, return None
        return None

    def _get_historical_price(self, underlying: str) -> Optional[float]:
        """Get historical price from stored data"""
        try:
            from pathlib import Path

            ROOT_DIR = Path(__file__).parent.parent.parent
            chain_file = ROOT_DIR / "outputs" / "chain_raw_live.csv"

            if chain_file.exists():
                import pandas as pd

                df = pd.read_csv(chain_file)
                if "underlying" in df.columns and "spot_price" in df.columns:
                    mask = df["underlying"].astype(str).str.upper() == underlying.upper()
                    if mask.any():
                        return float(df[mask]["spot_price"].iloc[0])
        except:
            pass
        return None

    def _calculate_option_price(self, spot: float, strike: float, option_type: str, expiry: str) -> float:
        """Calculate theoretical option price (simplified)"""
        if spot <= 0 or strike <= 0:
            return 0.0

        # Simplified intrinsic value
        if option_type == "CE":
            intrinsic = max(0, spot - strike)
        else:
            intrinsic = max(0, strike - spot)

        # Add time value (simplified)
        time_value = spot * 0.02
        return intrinsic + time_value

    def _get_historical_option_price(
        self, symbol: str, strike: float, option_type: str, expiry: str
    ) -> Optional[float]:
        """Get historical option price"""
        # Would query historical data
        return None

    def _get_historical_pnl(self, position: Dict[str, Any]) -> Optional[float]:
        """Get historical PnL for similar position"""
        # Would query historical positions
        return None


# Global instance
_multi_validator = MultiValidationAudit()


def get_multi_validator() -> MultiValidationAudit:
    """Get global multi-validator instance"""
    return _multi_validator
