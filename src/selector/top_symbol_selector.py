"""
Top Symbol Selector - Ranks underlyings and selects best for trading
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger


class TopSymbolSelector:
    """
    Selects top underlying for trading based on liquidity, signals, and execution quality.
    """
    
    def __init__(
        self,
        spread_threshold_pct: float = 6.0,
        min_volume_near_atm: int = 1000,
        min_strikes_band: int = 10
    ):
        """
        Initialize selector.
        
        Args:
            spread_threshold_pct: Maximum median spread % (default: 6%)
            min_volume_near_atm: Minimum volume near ATM (default: 1000)
            min_strikes_band: Minimum strikes within expected move band (default: 10)
        """
        self.spread_threshold_pct = spread_threshold_pct
        self.min_volume_near_atm = min_volume_near_atm
        self.min_strikes_band = min_strikes_band
    
    def calculate_expected_move(
        self,
        spot: float,
        iv: float,
        time_to_expiry: float
    ) -> float:
        """
        Calculate expected move using IV.
        
        Expected Move = Spot * IV * sqrt(T)
        
        Args:
            spot: Current spot price
            iv: Implied volatility (e.g., 0.20 for 20%)
            time_to_expiry: Time to expiry in years
        
        Returns:
            Expected move in points
        """
        if time_to_expiry <= 0 or iv <= 0:
            return spot * 0.02  # Default 2% if can't calculate
        
        return spot * iv * np.sqrt(time_to_expiry)
    
    def liquidity_gate(
        self,
        df: pd.DataFrame,
        spot: float,
        expected_move: float
    ) -> Tuple[bool, List[str]]:
        """
        Check if underlying passes liquidity gate.
        
        Args:
            df: DataFrame with option chain data
            spot: Current spot price
            expected_move: Expected move in points
        
        Returns:
            Tuple of (passed, reasons)
        """
        reasons = []
        
        # Check 1: Median spread %
        if 'bid_ask_spread_pct' in df.columns:
            median_spread = df['bid_ask_spread_pct'].median()
            if median_spread > self.spread_threshold_pct:
                reasons.append(f"Median spread {median_spread:.2f}% > {self.spread_threshold_pct}%")
                return False, reasons
        
        # Check 2: Volume near ATM
        atm_band = spot * 0.02  # 2% band
        near_atm = df[
            (df['strike'].notna()) &
            (abs(df['strike'] - spot) <= atm_band) &
            (df['volume'].notna())
        ]
        
        if near_atm.empty:
            reasons.append("No options near ATM")
            return False, reasons
        
        total_volume = near_atm['volume'].sum()
        if total_volume < self.min_volume_near_atm:
            reasons.append(f"Volume near ATM {total_volume} < {self.min_volume_near_atm}")
            return False, reasons
        
        # Check 3: Strikes within expected move
        strike_band = expected_move
        in_band = df[
            (df['strike'].notna()) &
            (abs(df['strike'] - spot) <= strike_band)
        ]
        
        if len(in_band) < self.min_strikes_band:
            reasons.append(f"Only {len(in_band)} strikes in band < {self.min_strikes_band}")
            return False, reasons
        
        return True, []
    
    def calculate_pcr(
        self,
        df: pd.DataFrame,
        spot: float,
        band_pct: float = 0.02
    ) -> Tuple[float, float]:
        """
        Calculate PCR (Put-Call Ratio) and delta-weighted PCR.
        
        Args:
            df: DataFrame with option chain
            spot: Current spot price
            band_pct: Band around ATM (default: 2%)
        
        Returns:
            Tuple of (simple_pcr, delta_weighted_pcr)
        """
        band = spot * band_pct
        
        # Filter near ATM
        near_atm = df[
            (df['strike'].notna()) &
            (abs(df['strike'] - spot) <= band)
        ]
        
        if near_atm.empty:
            return 0.0, 0.0
        
        # Separate CE and PE
        ce = near_atm[near_atm['option_type'] == 'CE']
        pe = near_atm[near_atm['option_type'] == 'PE']
        
        # Simple PCR (OI-based)
        ce_oi = ce['oi'].sum() if 'oi' in ce.columns and ce['oi'].notna().any() else 0
        pe_oi = pe['oi'].sum() if 'oi' in pe.columns and pe['oi'].notna().any() else 0
        
        simple_pcr = pe_oi / ce_oi if ce_oi > 0 else 0.0
        
        # Delta-weighted PCR
        if 'delta' in ce.columns and 'delta' in pe.columns:
            ce_delta_oi = (ce['delta'].abs() * ce['oi']).sum() if ce['oi'].notna().any() else 0
            pe_delta_oi = (pe['delta'].abs() * pe['oi']).sum() if pe['oi'].notna().any() else 0
            delta_pcr = pe_delta_oi / ce_delta_oi if ce_delta_oi > 0 else 0.0
        else:
            delta_pcr = simple_pcr
        
        return float(simple_pcr), float(delta_pcr)
    
    def calculate_signal_strength(
        self,
        df: pd.DataFrame,
        spot: float
    ) -> float:
        """
        Calculate signal strength (0-100).
        
        Args:
            df: DataFrame with option chain
            spot: Current spot price
        
        Returns:
            Signal strength score (0-100)
        """
        score = 0.0
        
        # Component 1: PCR (30 points)
        pcr, delta_pcr = self.calculate_pcr(df, spot)
        if 0.8 <= pcr <= 1.2:  # Neutral zone
            score += 15
        elif pcr > 1.2:  # Bearish
            score += 30
        elif pcr < 0.8:  # Bullish
            score += 30
        
        # Component 2: OI buildup concentration (25 points)
        if 'oi_buildup' in df.columns:
            buildup_counts = df['oi_buildup'].value_counts()
            long_buildup = buildup_counts.get('Long Buildup', 0)
            short_buildup = buildup_counts.get('Short Buildup', 0)
            total = len(df)
            if total > 0:
                concentration = max(long_buildup, short_buildup) / total
                score += concentration * 25
        
        # Component 3: Volume activity (25 points)
        if 'volume' in df.columns and df['volume'].notna().any():
            total_volume = df['volume'].sum()
            # Normalize (assume 100k+ is good)
            volume_score = min(25, (total_volume / 100000) * 25)
            score += volume_score
        
        # Component 4: OI change momentum (20 points)
        if 'dOI' in df.columns and df['dOI'].notna().any():
            total_doi = df['dOI'].abs().sum()
            # Normalize
            doi_score = min(20, (total_doi / 1000000) * 20)
            score += doi_score
        
        return min(100.0, score)
    
    def calculate_execution_quality(
        self,
        df: pd.DataFrame
    ) -> float:
        """
        Calculate execution quality score (0-100).
        
        Args:
            df: DataFrame with option chain
        
        Returns:
            Execution quality score
        """
        score = 100.0
        
        # Penalize high spreads
        if 'bid_ask_spread_pct' in df.columns:
            median_spread = df['bid_ask_spread_pct'].median()
            if median_spread > 5:
                score -= (median_spread - 5) * 10
            score = max(0, score)
        
        # Penalize low volume
        if 'volume' in df.columns:
            total_volume = df['volume'].sum()
            if total_volume < 10000:
                score -= 20
            score = max(0, score)
        
        return max(0.0, min(100.0, score))
    
    def score_underlying(
        self,
        df: pd.DataFrame,
        underlying: str,
        spot: float,
        time_to_expiry: float
    ) -> Dict:
        """
        Score an underlying.
        
        Args:
            df: DataFrame with option chain data
            underlying: Underlying name
            spot: Current spot price
            time_to_expiry: Time to expiry in years
        
        Returns:
            Dict with scoring results
        """
        # Calculate expected move
        if 'iv' in df.columns and df['iv'].notna().any():
            median_iv = df['iv'].median()
        else:
            median_iv = 0.20  # Default 20%
        
        expected_move = self.calculate_expected_move(spot, median_iv, time_to_expiry)
        
        # Liquidity gate
        passed, gate_reasons = self.liquidity_gate(df, spot, expected_move)
        
        if not passed:
            return {
                "underlying": underlying,
                "underlying_score": 0.0,
                "liquidity_gate_passed": False,
                "liquidity_gate_reasons": gate_reasons,
                "signal_strength": 0.0,
                "execution_quality": 0.0,
                "pcr": 0.0,
                "pcr_delta_weighted": 0.0,
                "expected_move": expected_move,
                "recommendation": "NO TRADE"
            }
        
        # Calculate metrics
        pcr, delta_pcr = self.calculate_pcr(df, spot)
        signal_strength = self.calculate_signal_strength(df, spot)
        execution_quality = self.calculate_execution_quality(df)
        
        # Overall score (weighted)
        underlying_score = (
            signal_strength * 0.5 +
            execution_quality * 0.3 +
            (100 if passed else 0) * 0.2
        )
        
        return {
            "underlying": underlying,
            "underlying_score": float(underlying_score),
            "liquidity_gate_passed": True,
            "liquidity_gate_reasons": [],
            "signal_strength": float(signal_strength),
            "execution_quality": float(execution_quality),
            "pcr": float(pcr),
            "pcr_delta_weighted": float(delta_pcr),
            "expected_move": float(expected_move),
            "spot": float(spot),
            "time_to_expiry": float(time_to_expiry),
            "recommendation": "TRADE" if underlying_score >= 50 else "NO TRADE"
        }
    
    def select_top_underlying(
        self,
        all_data: Dict[str, pd.DataFrame],
        spots: Dict[str, float],
        time_to_expiry_map: Dict[str, float]
    ) -> Tuple[Optional[str], pd.DataFrame]:
        """
        Select top underlying from all indices.
        
        Args:
            all_data: Dict mapping underlying -> DataFrame
            spots: Dict mapping underlying -> spot price
            time_to_expiry_map: Dict mapping underlying -> time_to_expiry
        
        Returns:
            Tuple of (top_underlying, rankings_df)
        """
        rankings = []
        
        for underlying, df in all_data.items():
            if df.empty:
                continue
            
            spot = spots.get(underlying, df.get('spot_price', 0).iloc[0] if 'spot_price' in df.columns else 0)
            time_to_expiry = time_to_expiry_map.get(underlying, 0.065)  # Default ~24 days
            
            score_result = self.score_underlying(df, underlying, spot, time_to_expiry)
            rankings.append(score_result)
        
        if not rankings:
            return None, pd.DataFrame()
        
        rankings_df = pd.DataFrame(rankings)
        rankings_df = rankings_df.sort_values('underlying_score', ascending=False)
        
        top = rankings_df.iloc[0] if not rankings_df.empty else None
        top_underlying = top['underlying'] if top is not None and top['recommendation'] == 'TRADE' else None
        
        return top_underlying, rankings_df
