"""
QC Validator for Option Chain Data
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger


class QCValidator:
    """
    Quality Control validator for option chain data.
    """

    def __init__(
        self,
        min_data_completeness: float = 0.7,
        max_spread_pct: float = 10.0,
        min_contracts: int = 50,
        sim_mode: bool = False,
        paper_sanity_mode: bool = False,
    ):
        """
        Initialize QC validator.

        Args:
            min_data_completeness: Minimum data completeness (default: 70%)
            max_spread_pct: Maximum acceptable spread % (default: 10%)
            min_contracts: Minimum contracts required (default: 50)
            sim_mode: Simulation mode - more lenient checks (default: False)
        """
        self.min_data_completeness = min_data_completeness
        self.max_spread_pct = max_spread_pct
        self.min_contracts = 10 if sim_mode else min_contracts  # Lower threshold for sim mode
        self.sim_mode = sim_mode
        self.paper_sanity_mode = paper_sanity_mode

        # Per-underlying contract thresholds (some indices have fewer contracts)
        self.underlying_min_contracts = {
            "SENSEX": 30,  # SENSEX typically has fewer contracts
            "MIDCPNIFTY": 40,  # MIDCPNIFTY has fewer than NIFTY
            "FINNIFTY": 45,  # FINNIFTY has fewer than NIFTY
            "NIFTY": 50,  # Standard threshold
            "BANKNIFTY": 50,  # Standard threshold
        }

        # PAPER_SANITY: Lower thresholds by 20-30%
        if paper_sanity_mode:
            self.min_data_completeness = max(0.6, min_data_completeness * 0.8)  # Lower to 60% or 80% of original
            # Reduce min_contracts by 20%
            for key in self.underlying_min_contracts:
                self.underlying_min_contracts[key] = max(10, int(self.underlying_min_contracts[key] * 0.8))

    @staticmethod
    def _first_present_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        for col in candidates:
            if col in df.columns:
                return col
        return None

    @classmethod
    def _bid_ask_columns(cls, df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
        alias_pairs = [
            ("bidPrice", "offerPrice"),
            ("top_bid_price", "top_ask_price"),
            ("bid", "ask"),
        ]
        for bid_col, ask_col in alias_pairs:
            if bid_col in df.columns and ask_col in df.columns:
                return bid_col, ask_col
        bid_col = cls._first_present_column(df, ["bidPrice", "top_bid_price", "bid"])
        ask_col = cls._first_present_column(df, ["offerPrice", "top_ask_price", "ask"])
        return bid_col, ask_col

    @classmethod
    def normalize_oi_change_alias(cls, df: pd.DataFrame) -> pd.Series:
        """
        Return OI-change values using the first supported alias.

        Supported aliases are dOI, oi_change, and change_in_oi. The input
        DataFrame is not mutated.
        """
        oi_col = cls._first_present_column(df, ["dOI", "oi_change", "change_in_oi"])
        if oi_col is None:
            return pd.Series([pd.NA] * len(df), index=df.index, dtype="object")
        return df[oi_col]

    def validate_snapshot(self, df: pd.DataFrame, underlying: str) -> Tuple[bool, List[str]]:
        """
        Validate a snapshot.

        Args:
            df: DataFrame with option chain data
            underlying: Underlying name

        Returns:
            Tuple of (passed, reasons)
        """
        failures = []
        if df is None or df.empty:
            return False, ["No contracts to validate"]

        # Check 1: Minimum contracts (per-underlying threshold)
        min_contracts_for_underlying = self.underlying_min_contracts.get(underlying, self.min_contracts)
        if len(df) < min_contracts_for_underlying:
            failures.append(f"Insufficient contracts: {len(df)} < {min_contracts_for_underlying}")

        # Check 2: Data completeness
        critical_cols = ["ltp", "strike", "option_type", "spot_price"]
        for col in critical_cols:
            if col in df.columns:
                completeness = df[col].notna().sum() / len(df)
                if completeness < self.min_data_completeness:
                    failures.append(f"{col} completeness {completeness:.1%} < {self.min_data_completeness:.1%}")

        # Check 3: Bid/Ask validity (ask >= bid)
        bid_col, ask_col = self._bid_ask_columns(df)
        if bid_col and ask_col:
            invalid_spreads = df[
                (df[bid_col].notna()) & (df[ask_col].notna()) & (df[ask_col] < df[bid_col])
            ]
            if len(invalid_spreads) > 0:
                failures.append(f"{len(invalid_spreads)} contracts have ask < bid (invalid)")

        # Check 4: IV sanity (0-3 range, i.e., 0-300%)
        if "iv" in df.columns:
            invalid_iv = df[(df["iv"].notna()) & ((df["iv"] < 0) | (df["iv"] > 3.0))]
            if len(invalid_iv) > 0:
                failures.append(f"{len(invalid_iv)} contracts have IV outside 0-3 range")

        # Check 5: Spread quality
        if "bid_ask_spread_pct" in df.columns:
            high_spread = (df["bid_ask_spread_pct"] > self.max_spread_pct).sum()
            if high_spread > len(df) * 0.3:  # More than 30% with high spread
                failures.append(f"{high_spread} contracts have spread > {self.max_spread_pct}%")

        # Check 6: Price validity
        if "ltp" in df.columns:
            negative_ltp = (df["ltp"] < 0).sum()
            if negative_ltp > 0:
                failures.append(f"{negative_ltp} contracts have negative LTP")

            zero_ltp = (df["ltp"] == 0).sum()
            if zero_ltp > len(df) * 0.2:  # More than 20% with zero LTP
                failures.append(f"{zero_ltp} contracts have zero LTP")

        # Check 7: Strike validity
        if "strike" in df.columns:
            invalid_strikes = df["strike"].isna().sum()
            if invalid_strikes > len(df) * 0.1:
                failures.append(f"{invalid_strikes} contracts have invalid strikes")

        # Check 8: Option type validity
        if "option_type" in df.columns:
            valid_types = set(["CE", "PE"])
            invalid_types = set(df["option_type"].dropna().unique()) - valid_types
            if invalid_types:
                failures.append(f"Invalid option types: {invalid_types}")

        # Check 9: Enough strikes around ATM
        if "strike" in df.columns and "spot_price" in df.columns:
            spot = df["spot_price"].iloc[0] if df["spot_price"].notna().any() else None
            if spot:
                # In sim mode, use wider band (10% instead of 5%) and lower requirement
                if self.sim_mode:
                    atm_band = spot * 0.10  # 10% band for simulation
                    min_strikes = 5
                else:
                    atm_band = spot * 0.05  # 5% band for live
                    min_strikes = 10

                strikes_near_atm = df[(df["strike"].notna()) & (abs(df["strike"] - spot) <= atm_band)]

                if len(strikes_near_atm) < min_strikes:
                    failures.append(
                        f"Only {len(strikes_near_atm)} strikes near ATM (need >= {min_strikes}, band={atm_band/spot*100:.1f}%)"
                    )

        # Check 10: Stable timestamps (not stale)
        if "fetch_timestamp" in df.columns:
            # Check if all timestamps are recent (within last 60 seconds)
            from datetime import datetime

            import pytz

            ist = pytz.timezone("Asia/Kolkata")
            now = datetime.now(ist)
            try:
                df["ts_parsed"] = pd.to_datetime(
                    df["fetch_timestamp"].str.replace(" IST", ""), format="%Y-%m-%d %H:%M:%S", errors="coerce"
                )
                stale = (now - df["ts_parsed"]).dt.total_seconds() > 60
                if stale.sum() > len(df) * 0.1:  # More than 10% stale
                    failures.append(f"{stale.sum()} contracts have stale timestamps (>60s old)")
            except:
                pass

        passed = len(failures) == 0
        return passed, failures

    def validate_all(self, all_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """
        Validate all underlyings.

        Args:
            all_data: Dict mapping underlying -> DataFrame

        Returns:
            Dict with validation results
        """
        results = {}
        all_passed = True

        for underlying, df in all_data.items():
            if df.empty:
                results[underlying] = {"passed": False, "reasons": ["Empty DataFrame"]}
                all_passed = False
                continue

            passed, reasons = self.validate_snapshot(df, underlying)
            results[underlying] = {"passed": passed, "reasons": reasons, "contract_count": len(df)}

            if not passed:
                all_passed = False
                logger.warning(f"QC FAIL for {underlying}: {reasons}")
            else:
                logger.info(f"QC PASS for {underlying}")

        return {
            "overall_passed": all_passed,
            "underlying_results": results,
            "timestamp": pd.Timestamp.now().isoformat(),
        }


