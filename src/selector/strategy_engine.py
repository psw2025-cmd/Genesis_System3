"""
Strategy Recommendation Engine
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger


class StrategyEngine:
    """
    Recommends trading strategies based on market conditions.
    """
    
    def __init__(
        self,
        min_liquidity_score: float = 40.0,  # Lowered from 60.0 (optimized - more opportunities)
        min_confidence: float = 0.5,  # Lowered from 0.6 (optimized - more signals)
        paper_sanity_mode: bool = False
    ):
        """
        Initialize strategy engine.
        
        Args:
            min_liquidity_score: Minimum liquidity score to trade (default: 60)
            min_confidence: Minimum confidence to recommend trade (default: 0.6)
        """
        self.min_liquidity_score = min_liquidity_score
        self.min_confidence = min_confidence
        self.paper_sanity_mode = paper_sanity_mode
        
        # PAPER_SANITY: Lower thresholds
        if paper_sanity_mode:
            self.min_liquidity_score = 30.0  # Lower from 40
            self.min_confidence = 0.45  # Lower from 0.5
    
    def analyze_sentiment(
        self,
        df: pd.DataFrame,
        spot: float,
        pcr: float,
        delta_pcr: float
    ) -> Dict[str, float]:
        """
        Analyze market sentiment.
        
        Args:
            df: Option chain DataFrame
            spot: Current spot price
            pcr: Put-Call Ratio
            delta_pcr: Delta-weighted PCR
        
        Returns:
            Dict with sentiment scores
        """
        # Bullish indicators
        bullish_score = 0.0
        bearish_score = 0.0
        
        # PCR analysis
        if pcr < 0.8:
            bullish_score += 30  # Low PCR = bullish
        elif pcr > 1.2:
            bearish_score += 30  # High PCR = bearish
        
        # OI buildup analysis
        if 'oi_buildup' in df.columns:
            buildup_counts = df['oi_buildup'].value_counts()
            long_buildup = buildup_counts.get('Long Buildup', 0)
            short_buildup = buildup_counts.get('Short Buildup', 0)
            total = len(df)
            
            if total > 0:
                long_pct = long_buildup / total
                short_pct = short_buildup / total
                
                if long_pct > 0.3:
                    bullish_score += 25
                if short_pct > 0.3:
                    bearish_score += 25
        
        # Price momentum
        if 'dLTP' in df.columns and df['dLTP'].notna().any():
            avg_price_change = df['dLTP'].mean()
            if avg_price_change > 0:
                bullish_score += 20
            elif avg_price_change < 0:
                bearish_score += 20
        
        # Volume analysis
        if 'dVolume' in df.columns and df['dVolume'].notna().any():
            ce_volume = df[(df['option_type'] == 'CE') & (df['dVolume'].notna())]['dVolume'].sum()
            pe_volume = df[(df['option_type'] == 'PE') & (df['dVolume'].notna())]['dVolume'].sum()
            
            if ce_volume > pe_volume * 1.2:
                bullish_score += 15
            elif pe_volume > ce_volume * 1.2:
                bearish_score += 15
        
        # Normalize to 0-100
        total = bullish_score + bearish_score
        if total > 0:
            bullish_score = (bullish_score / total) * 100
            bearish_score = (bearish_score / total) * 100
        
        return {
            "bullish_score": float(bullish_score),
            "bearish_score": float(bearish_score),
            "sentiment": "BULLISH" if bullish_score > bearish_score + 10 else "BEARISH" if bearish_score > bullish_score + 10 else "NEUTRAL"
        }
    
    def select_strikes(
        self,
        df: pd.DataFrame,
        spot: float,
        expected_move: float,
        option_type: str,
        strategy_type: str,
        max_strikes: int = 25
    ) -> List[float]:
        """
        Select strikes for strategy.
        
        Args:
            df: Option chain DataFrame
            spot: Current spot price
            expected_move: Expected move in points
            option_type: 'CE' or 'PE'
            strategy_type: 'debit', 'credit', 'spread', etc.
            max_strikes: Maximum strikes to consider
        
        Returns:
            List of selected strikes
        """
        # Filter by option type
        df_filtered = df[df['option_type'] == option_type].copy()
        
        if df_filtered.empty:
            return []
        
        # Filter by liquidity
        if 'bid_ask_spread_pct' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['bid_ask_spread_pct'] < 10]  # Max 10% spread
        
        if 'volume' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['volume'] > 0]
        
        # Select strikes based on strategy
        if strategy_type in ['debit', 'buy']:
            # For buying: ATM and 1-2 steps OTM
            band = expected_move * 0.5
            strikes = df_filtered[
                (df_filtered['strike'] >= spot - band) &
                (df_filtered['strike'] <= spot + expected_move)
            ]['strike'].unique().tolist()
            
        elif strategy_type in ['credit', 'sell']:
            # For selling: OTM
            strikes = df_filtered[
                df_filtered['strike'] > spot + expected_move * 0.3
            ]['strike'].unique().tolist()
            
        elif strategy_type == 'spread':
            # For spreads: ATM ± expected_move
            strikes = df_filtered[
                (df_filtered['strike'] >= spot - expected_move) &
                (df_filtered['strike'] <= spot + expected_move)
            ]['strike'].unique().tolist()
            
        else:
            # Default: ATM band
            band = expected_move
            strikes = df_filtered[
                (df_filtered['strike'] >= spot - band) &
                (df_filtered['strike'] <= spot + band)
            ]['strike'].unique().tolist()
        
        # Sort and limit
        strikes = sorted(strikes)[:max_strikes]
        
        return strikes
    
    def recommend_strategy(
        self,
        df: pd.DataFrame,
        underlying: str,
        spot: float,
        expected_move: float,
        sentiment: Dict,
        liquidity_score: float,
        signal_strength: float
    ) -> Dict:
        """
        Recommend trading strategy.
        
        Args:
            df: Option chain DataFrame
            underlying: Underlying name
            spot: Current spot price
            expected_move: Expected move in points
            sentiment: Sentiment dict from analyze_sentiment
            liquidity_score: Liquidity score (0-100)
            signal_strength: Signal strength (0-100)
        
        Returns:
            Strategy recommendation dict
        """
        # Check if we should trade (optimized thresholds)
        confidence = (signal_strength + liquidity_score) / 200.0
        
        # Lower thresholds for more opportunities (optimized)
        if confidence < self.min_confidence or liquidity_score < self.min_liquidity_score:
            return {
                "action": "NO TRADE",
                "strategy": None,
                "reason": f"Low confidence ({confidence:.2f}) or liquidity ({liquidity_score:.1f})",
                "confidence": float(confidence),
                "strikes": [],
                "tokens": []
            }
        
        sentiment_type = sentiment.get("sentiment", "NEUTRAL")
        bullish_score = sentiment.get("bullish_score", 0)
        bearish_score = sentiment.get("bearish_score", 0)
        
        # PAPER_SANITY: Lower sentiment thresholds
        sentiment_threshold = 50.0 if self.paper_sanity_mode else 60.0
        neutral_liquidity_threshold = 50.0 if self.paper_sanity_mode else 70.0
        
        # Strategy selection
        if sentiment_type == "BULLISH" and bullish_score > sentiment_threshold:
            # Bullish: Buy CE or bull call spread
            strategy = "BUY_CE"
            option_type = "CE"
            strikes = self.select_strikes(df, spot, expected_move, option_type, "debit")
            
        elif sentiment_type == "BEARISH" and bearish_score > sentiment_threshold:
            # Bearish: Buy PE or bear put spread
            strategy = "BUY_PE"
            option_type = "PE"
            strikes = self.select_strikes(df, spot, expected_move, option_type, "debit")
            
        elif sentiment_type == "NEUTRAL" and liquidity_score > neutral_liquidity_threshold:
            # Neutral: Iron condor/fly (if high liquidity)
            strategy = "IRON_CONDOR"
            option_type = "BOTH"
            # Select strikes for both CE and PE
            ce_strikes = self.select_strikes(df, spot, expected_move, "CE", "credit")
            pe_strikes = self.select_strikes(df, spot, expected_move, "PE", "credit")
            strikes = sorted(list(set(ce_strikes + pe_strikes)))[:4]  # Max 4 strikes
            
        else:
            # Low confidence - no trade
            return {
                "action": "NO TRADE",
                "strategy": None,
                "reason": f"Unclear sentiment or low liquidity",
                "confidence": float(confidence),
                "strikes": [],
                "tokens": []
            }
        
        # Select best contracts
        selected_contracts = []
        for strike in strikes[:2]:  # Max 2 strikes for simplicity
            contract = df[
                (df['strike'] == strike) &
                (df['option_type'] == option_type if option_type != "BOTH" else True)
            ]
            
            if not contract.empty:
                # Select most liquid
                contract = contract.sort_values('volume', ascending=False).iloc[0]
                selected_contracts.append({
                    "token": str(contract.get('token', '')),
                    "symbol": str(contract.get('symbol', '')),
                    "strike": float(contract.get('strike', 0)),
                    "option_type": str(contract.get('option_type', '')),
                    "entry_mid": float(contract.get('mid_price', contract.get('ltp', 0))),
                    "spread": float(contract.get('bid_ask_spread', 0)),
                    "volume": float(contract.get('volume', 0))
                })
        
        if not selected_contracts:
            return {
                "action": "NO TRADE",
                "strategy": None,
                "reason": "No suitable contracts found",
                "confidence": float(confidence),
                "strikes": [],
                "tokens": []
            }
        
        # Calculate SL and target
        entry_mid = selected_contracts[0]['entry_mid']
        stop_loss = entry_mid * 0.7  # 30% stop loss
        target = entry_mid * 1.5  # 50% target
        
        return {
            "action": "TRADE",
            "strategy": strategy,
            "confidence": float(confidence),
            "strikes": [c['strike'] for c in selected_contracts],
            "tokens": [c['token'] for c in selected_contracts],
            "contracts": selected_contracts,
            "entry_mid": float(entry_mid),
            "stop_loss": float(stop_loss),
            "target": float(target),
            "qty_lots": 1,  # Default 1 lot
            "reason": f"{sentiment_type} sentiment, {strategy} strategy"
        }
    
    def decide(
        self,
        df: pd.DataFrame,
        spot: float,
        expected_move: float,
        sentiment: Dict,
        liquidity_score: float,
        signal_strength: float
    ) -> Dict:
        """
        Unified decision method - wrapper for recommend_strategy.
        NEVER throws exceptions - always returns valid dict.
        
        Args:
            df: Option chain DataFrame
            spot: Current spot price
            expected_move: Expected move in points
            sentiment: Sentiment dict from analyze_sentiment
            liquidity_score: Liquidity score (0-100)
            signal_strength: Signal strength (0-100)
        
        Returns:
            Dict with action (TRADE or NO_TRADE) and reasons
        """
        try:
            # Get underlying from dataframe if available
            underlying = str(df['underlying'].iloc[0]) if 'underlying' in df.columns and not df.empty else "UNKNOWN"
            
            # Call recommend_strategy with all required parameters
            result = self.recommend_strategy(
                df=df,
                underlying=underlying,
                spot=spot,
                expected_move=expected_move,
                sentiment=sentiment,
                liquidity_score=liquidity_score,
                signal_strength=signal_strength
            )
            
            # Normalize action field
            if result.get('action') == 'NO TRADE':
                result['action'] = 'NO_TRADE'
            elif result.get('action') == 'TRADE':
                result['action'] = 'TRADE'
            
            # Ensure reasons list exists
            if 'reasons' not in result:
                reason = result.get('reason', 'Unknown')
                result['reasons'] = [reason] if reason else []
            
            return result
            
        except Exception as e:
            logger.error(f"StrategyEngine.decide() error: {e}")
            return {
                "action": "NO_TRADE",
                "strategy": None,
                "confidence": 0.0,
                "strikes": [],
                "tokens": [],
                "reasons": [f"STRATEGY_ERROR: {str(e)[:100]}"],
                "reason": f"STRATEGY_ERROR: {str(e)[:100]}"
            }