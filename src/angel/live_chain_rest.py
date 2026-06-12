"""
REST Fallback for Option Chain - Secondary method when WebSocket fails.

NOTE: Angel One broker path is disabled (System3 is Dhan-only).
LiveChainREST will raise RuntimeError at runtime when the broker
tries to execute any Angel One API call via the disabled shim.
"""
import time
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.brokers.angel_one.broker import AngelOneBroker
from core.utils.logger import logger


class LiveChainREST:
    """
    REST API fallback for option chain data.
    Implements rate limiting and batching.
    """
    
    def __init__(self, broker: AngelOneBroker, max_requests_per_minute: int = 60):
        """
        Initialize REST fallback.
        
        Args:
            broker: AngelOneBroker instance
            max_requests_per_minute: Rate limit (default: 60)
        """
        self.broker = broker
        self.max_requests_per_minute = max_requests_per_minute
        self.request_times = []
        self.last_request_time = 0
        self.min_interval = 60.0 / max_requests_per_minute
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        now = time.time()
        
        # Remove old requests (older than 1 minute)
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # Check if we need to wait
        if len(self.request_times) >= self.max_requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0]) + 0.1
            if sleep_time > 0:
                logger.debug(f"Rate limit: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        # Record this request
        self.request_times.append(time.time())
        self.last_request_time = now
    
    def fetch_option_chain_batch(
        self,
        underlying_name: str,
        exchange: str,
        expiry_date: Optional[str] = None,
        strikes: Optional[List[float]] = None,
        expected_move: Optional[float] = None,
        max_strikes: int = 50
    ) -> Optional[List[Dict]]:
        """
        Fetch option chain using REST API with rate limiting.
        
        Args:
            underlying_name: Underlying name (e.g., 'NIFTY')
            exchange: Exchange code ('NFO' or 'BFO')
            expiry_date: Optional expiry date filter
            strikes: Optional list of strikes to fetch
            expected_move: Expected move for strike filtering (ATM ± expected_move)
            max_strikes: Maximum strikes to fetch (default: 50)
        
        Returns:
            List of option dicts or None on error
        """
        self._rate_limit()
        
        try:
            # Use existing broker method
            option_chain = self.broker.get_option_chain_by_underlying(
                underlying_name=underlying_name,
                exchange=exchange,
                include_all_strikes=(strikes is None and expected_move is None)
            )
            
            if not option_chain:
                return None
            
            # Filter by expiry if provided
            if expiry_date:
                option_chain = [
                    opt for opt in option_chain
                    if str(opt.get('expiry', '')).upper() == expiry_date.upper()
                ]
            
            # Filter by expected_move band if provided (ATM ± expected_move)
            if expected_move and option_chain:
                spot = option_chain[0].get('spot_price', 0)
                if spot > 0:
                    strike_band = expected_move
                    option_chain = [
                        opt for opt in option_chain
                        if abs(opt.get('strike', 0) - spot) <= strike_band
                    ]
                    # Limit to max_strikes
                    if len(option_chain) > max_strikes:
                        # Sort by distance from ATM and take closest
                        option_chain.sort(key=lambda x: abs(x.get('strike', 0) - spot))
                        option_chain = option_chain[:max_strikes]
            
            # Filter by strikes if provided
            if strikes:
                option_chain = [
                    opt for opt in option_chain
                    if opt.get('strike') in strikes
                ]
            
            return option_chain
            
        except Exception as e:
            logger.error(f"REST fetch failed for {underlying_name}: {e}", exc_info=True)
            return None
    
    def fetch_all_indices(
        self,
        indices: List[Dict],
        expiry_map: Dict[str, str]
    ) -> Dict[str, List[Dict]]:
        """
        Fetch option chain for all indices using REST.
        
        Args:
            indices: List of dicts with 'name' and 'exchange'
            expiry_map: Dict mapping underlying_name -> expiry_string
        
        Returns:
            Dict mapping underlying_name -> list of option dicts
        """
        results = {}
        
        for idx in indices:
            name = idx.get("name")
            exchange = idx.get("exchange", "NFO")
            expiry = expiry_map.get(name)
            
            logger.info(f"REST fetching {name} ({exchange})...")
            option_chain = self.fetch_option_chain_batch(name, exchange, expiry)
            
            if option_chain:
                results[name] = option_chain
                logger.info(f"REST fetched {len(option_chain)} options for {name}")
            else:
                logger.warning(f"REST fetch returned no data for {name}")
                results[name] = []
        
        return results
