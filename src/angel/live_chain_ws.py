"""
WebSocket Live Option Chain - Primary method for real-time data
"""
import json
import time
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime
import pytz
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from core.brokers.angel_one.broker import AngelOneBroker
from core.utils.logger import logger


class LiveChainWebSocket:
    """
    WebSocket manager for live option chain data.
    """
    
    # Exchange type mapping
    EXCHANGE_MAP = {
        "NFO": 2,  # NSE_FO
        "BFO": 4,  # BSE_FO
        "NSE": 1,  # NSE_CM
        "BSE": 3,  # BSE_CM
    }
    
    # Subscription mode
    MODE_SNAP_QUOTE = 3  # Full data: LTP, OHLC, volume, OI, bid/ask
    
    def __init__(self, broker: AngelOneBroker):
        """
        Initialize WebSocket connection.
        
        Args:
            broker: AngelOneBroker instance (must be logged in)
        """
        self.broker = broker
        self.ws = None
        self.is_connected = False
        self.is_subscribed = False
        self.subscribed_tokens = {}  # {exchange: [tokens]}
        self.data_callback: Optional[Callable] = None
        self.reconnect_count = 0
        self.last_data_time = None
        self.connection_lock = threading.Lock()
        
    def connect(self) -> bool:
        """
        Connect to WebSocket.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            if not self.broker.auth_token or not self.broker.feed_token:
                logger.error("Broker not logged in - missing auth_token or feed_token")
                return False
            
            self.ws = SmartWebSocketV2(
                auth_token=self.broker.auth_token,
                api_key=self.broker.api_key,
                client_code=self.broker.client_id,
                feed_token=self.broker.feed_token,
                max_retry_attempt=3,
                retry_strategy=1,
                retry_delay=5
            )
            
            # Set callbacks
            self.ws.on_open = self._on_open
            self.ws.on_data = self._on_data
            self.ws.on_error = self._on_error
            self.ws.on_close = self._on_close
            
            # Start connection
            self.ws.connect()
            self.is_connected = True
            logger.info("WebSocket connected")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}", exc_info=True)
            self.is_connected = False
            return False
    
    def subscribe(self, tokens_by_exchange: Dict[str, List[str]], callback: Callable = None):
        """
        Subscribe to option tokens.
        
        Args:
            tokens_by_exchange: Dict mapping exchange -> list of tokens
                Example: {"NFO": ["12345", "12346"], "BFO": ["78901"]}
            callback: Optional callback function(data) called on each update
        """
        if not self.is_connected or not self.ws:
            logger.error("WebSocket not connected")
            return False
        
        self.data_callback = callback
        
        # Convert to WebSocket format
        token_list = []
        for exchange, tokens in tokens_by_exchange.items():
            exch_type = self.EXCHANGE_MAP.get(exchange)
            if exch_type and tokens:
                token_list.append({
                    "exchangeType": exch_type,
                    "tokens": [str(t) for t in tokens]
                })
                self.subscribed_tokens[exchange] = tokens
        
        if not token_list:
            logger.warning("No tokens to subscribe")
            return False
        
        try:
            correlation_id = f"LIVE_{int(time.time())}"
            self.ws.subscribe(
                correlation_id=correlation_id,
                mode=self.MODE_SNAP_QUOTE,
                token_list=token_list
            )
            self.is_subscribed = True
            logger.info(f"Subscribed to {sum(len(t) for t in tokens_by_exchange.values())} tokens")
            return True
        except Exception as e:
            logger.error(f"Subscription failed: {e}", exc_info=True)
            return False
    
    def _on_open(self, wsapp):
        """WebSocket opened callback."""
        logger.info("WebSocket connection opened")
        self.is_connected = True
        
        # Resubscribe if we had previous subscriptions
        if self.subscribed_tokens and not self.is_subscribed:
            logger.info("Resubscribing to tokens...")
            self.subscribe(self.subscribed_tokens, self.data_callback)
    
    def _on_data(self, wsapp, data):
        """WebSocket data callback - receives parsed dict from SmartWebSocketV2."""
        try:
            self.last_data_time = time.time()
            
            # SmartWebSocketV2._parse_binary_data() already parsed the binary data
            # Data is a dict with fields from SNAP_QUOTE mode:
            # - token, last_traded_price, volume_trade_for_the_day, open_interest
            # - best_5_buy_data, best_5_sell_data (for bid/ask)
            # - open_price_of_the_day, high_price_of_the_day, low_price_of_the_day, closed_price
            
            if isinstance(data, dict):
                # Extract key fields
                parsed = {
                    "token": data.get("token", ""),
                    "ltp": data.get("last_traded_price", 0) / 100.0 if data.get("last_traded_price") else None,  # Convert from paise
                    "volume": data.get("volume_trade_for_the_day", 0),
                    "oi": data.get("open_interest", 0),
                    "open": data.get("open_price_of_the_day", 0) / 100.0 if data.get("open_price_of_the_day") else None,
                    "high": data.get("high_price_of_the_day", 0) / 100.0 if data.get("high_price_of_the_day") else None,
                    "low": data.get("low_price_of_the_day", 0) / 100.0 if data.get("low_price_of_the_day") else None,
                    "close": data.get("closed_price", 0) / 100.0 if data.get("closed_price") else None,
                }
                
                # Extract bid/ask from best_5_sell_data (ask) and best_5_buy_data (bid)
                best_5_buy = data.get("best_5_buy_data", [])
                best_5_sell = data.get("best_5_sell_data", [])
                
                if best_5_buy:
                    parsed["bidPrice"] = best_5_buy[0].get("price", 0) / 100.0 if best_5_buy[0].get("price") else None
                    parsed["bidQty"] = best_5_buy[0].get("quantity", 0)
                else:
                    parsed["bidPrice"] = None
                    parsed["bidQty"] = 0
                
                if best_5_sell:
                    parsed["offerPrice"] = best_5_sell[0].get("price", 0) / 100.0 if best_5_sell[0].get("price") else None
                    parsed["offerQty"] = best_5_sell[0].get("quantity", 0)
                else:
                    parsed["offerPrice"] = None
                    parsed["offerQty"] = 0
                
                # Process the parsed data
                if self.data_callback:
                    self.data_callback(parsed)
            else:
                logger.warning(f"Unexpected data format: {type(data)}")
                
        except Exception as e:
            logger.error(f"Error processing WebSocket data: {e}", exc_info=True)
    
    def _on_error(self, wsapp, error):
        """WebSocket error callback."""
        logger.error(f"WebSocket error: {error}")
        self.is_connected = False
    
    def _on_close(self, wsapp, close_status_code, close_msg):
        """WebSocket close callback."""
        logger.warning(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.is_connected = False
        self.is_subscribed = False
    
    def disconnect(self):
        """Disconnect WebSocket."""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
        self.is_connected = False
        self.is_subscribed = False
        logger.info("WebSocket disconnected")
    
    def is_alive(self, timeout_seconds: int = 30) -> bool:
        """
        Check if WebSocket is alive (received data recently).
        
        Args:
            timeout_seconds: Maximum seconds since last data
        
        Returns:
            True if alive, False otherwise
        """
        if not self.is_connected:
            return False
        
        if self.last_data_time is None:
            return True  # Just connected, give it time
        
        elapsed = time.time() - self.last_data_time
        return elapsed < timeout_seconds
    
    def reconnect(self) -> bool:
        """
        Reconnect WebSocket.
        
        Returns:
            True if reconnected, False otherwise
        """
        logger.info("Attempting WebSocket reconnect...")
        self.disconnect()
        time.sleep(2)
        self.reconnect_count += 1
        return self.connect()
