import os
import sys
import time

# Ensure project root in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from SmartApi import SmartConnect  # smartapi-python library
import pyotp

from core.utils.env_loader import get_angelone_credentials
from core.utils.logger import logger


def _env_live_guard():
    """Hard env guard to block live trading unless explicitly allowed."""
    flag = os.getenv("SYSTEM3_LIVE_TRADING_ALLOWED", "").strip().lower()
    allowed = flag in {"1", "true", "yes", "y"}
    if not allowed:
        msg = "LIVE TRADING BLOCKED BY ENV GUARD (SYSTEM3_LIVE_TRADING_ALLOWED not enabled)"
        logger.error(msg)
        raise RuntimeError(msg)


class AngelOneBroker:
    def __init__(self, allow_data_only: bool = False):
        """
        Initialize Angel One broker connection.

        Args:
            allow_data_only: If True, allows data fetching without live trading guard.
                            If False, requires SYSTEM3_LIVE_TRADING_ALLOWED for any operation.
                            Default: False (backward compatible)
        """
        # Only enforce live trading guard if not in data-only mode
        # Data-only mode allows fetching market data, option chains, etc. without live trading permission
        if not allow_data_only:
            _env_live_guard()

        creds = get_angelone_credentials()

        self.api_key = creds["api_key"]
        self.client_id = creds["client_id"]
        # SmartAPI docs: generateSession(client_id, password/pin, totp)
        self.pin_or_password = creds["pin"] or creds["password"]
        self.totp_secret = creds["totp_secret"]

        self.smart = None
        self.auth_token = None
        self.refresh_token = None
        self.feed_token = None

        self._validate_creds()
        self._login()

    def _validate_creds(self):
        missing = []
        if not self.api_key:
            missing.append("ANGELONE_API_KEY")
        if not self.client_id:
            missing.append("ANGELONE_CLIENT_ID")
        if not self.pin_or_password:
            missing.append("ANGELONE_PIN or ANGELONE_PASSWORD")
        if not self.totp_secret:
            missing.append("ANGELONE_TOTP")

        if missing:
            msg = f"Missing AngelOne env values: {', '.join(missing)}"
            logger.error(msg)
            raise RuntimeError(msg)

    def _safe_generateSession(self, max_retries=3, base_delay=2):
        """
        Safe generateSession with exponential backoff for rate limiting.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff

        Returns:
            Session data dict
        """
        import time
        import random

        totp = pyotp.TOTP(self.totp_secret).now()

        for attempt in range(max_retries):
            try:
                # Add small delay before each attempt (except first)
                if attempt > 0:
                    delay = base_delay**attempt + random.uniform(0, 1)
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries} after {delay:.1f}s delay...")
                    time.sleep(delay)
                else:
                    # Small delay even on first attempt to avoid rate limits
                    time.sleep(1)

                data = self.smart.generateSession(self.client_id, self.pin_or_password, totp)

                if data and data.get("status"):
                    return data
                else:
                    logger.warning(f"Login returned non-success status: {data}")
                    if attempt < max_retries - 1:
                        continue
                    raise RuntimeError(f"AngelOne login failed: {data}")

            except Exception as e:
                error_str = str(e)

                # Check for rate limiting errors
                if "Access denied" in error_str or "exceeding access rate" in error_str or "10054" in error_str:
                    if attempt < max_retries - 1:
                        delay = base_delay ** (attempt + 1) + random.uniform(0, 2)
                        logger.warning(
                            f"Rate limited. Waiting {delay:.1f}s before retry {attempt + 2}/{max_retries}..."
                        )
                        time.sleep(delay)
                        # Regenerate TOTP for next attempt (it's time-based)
                        totp = pyotp.TOTP(self.totp_secret).now()
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {max_retries} attempts. Please wait before retrying.")
                        raise RuntimeError(f"AngelOne rate limit exceeded: {e}")
                else:
                    # Non-rate-limit error - log and raise immediately
                    logger.error(f"generateSession failed (non-rate-limit): {e}")
                    raise

        raise RuntimeError("Failed to generate session after all retries")

    def _login(self):
        logger.info("Connecting to Angel One SmartAPI...")

        self.smart = SmartConnect(api_key=self.api_key)

        try:
            totp = pyotp.TOTP(self.totp_secret).now()
        except Exception as e:
            logger.error(f"Invalid TOTP secret: {e}")
            raise

        # Use safe generateSession with retry logic
        try:
            data = self._safe_generateSession(max_retries=3, base_delay=2)
        except Exception as e:
            logger.error(f"Login failed after retries: {e}")
            raise

        self.auth_token = data["data"]["jwtToken"]
        self.refresh_token = data["data"]["refreshToken"]

        # Add delay before getting feed token
        import time

        time.sleep(1)

        try:
            self.feed_token = self.smart.getfeedToken()
        except Exception as e:
            logger.warning(f"getfeedToken failed: {e}. Continuing without feed token.")
            self.feed_token = None

        logger.info("AngelOne login successful.")
        # SECURITY: Do not log feed token - it's a secret
        from core.utils.log_sanitizer import sanitize_log_message

        if self.feed_token:
            logger.info(sanitize_log_message(f"Feed token obtained: {self.feed_token}"))

    def _safe_get_profile(self, max_retries=3):
        """
        Safe getProfile with exponential backoff for rate limiting.

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            Profile dict or None if all retries fail
        """
        import time
        import random

        for attempt in range(max_retries):
            try:
                # Add delay before each attempt (except first)
                if attempt > 0:
                    delay = (2**attempt) + random.uniform(0, 1)
                    logger.warning(f"getProfile retry {attempt + 1}/{max_retries} after {delay:.1f}s delay...")
                    time.sleep(delay)
                else:
                    # Small delay even on first attempt
                    time.sleep(1)

                profile = self.smart.getProfile(self.refresh_token)
                if profile:
                    return profile
                else:
                    logger.warning(f"getProfile returned None (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        continue
                    return None

            except Exception as e:
                error_str = str(e).lower()

                # Check for rate limiting errors
                if (
                    "access rate" in error_str
                    or "access denied" in error_str
                    or "exceeding" in error_str
                    or "10054" in str(e)
                ):
                    if attempt < max_retries - 1:
                        delay = (2**attempt) + random.uniform(0, 1)
                        logger.warning(
                            f"getProfile rate limited. Waiting {delay:.1f}s before retry {attempt + 2}/{max_retries}..."
                        )
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"getProfile rate limit exceeded after {max_retries} attempts. Returning None.")
                        return None
                else:
                    # Non-rate-limit error - log and return None gracefully
                    logger.error(f"getProfile failed (non-rate-limit): {e}")
                    return None

        return None

    def get_profile(self):
        """
        Return user profile (basic sanity check).
        Uses safe wrapper with retry logic to avoid rate limits.
        """
        return self._safe_get_profile(max_retries=3)

    def get_positions(self):
        """
        Fetch open/closed positions from broker.
        Returns list of position dicts or empty list on error.
        """
        try:
            if hasattr(self.smart, "position"):
                resp = self.smart.position()
            elif hasattr(self.smart, "getPosition"):
                resp = self.smart.getPosition()
            else:
                logger.warning("Broker has no position() or getPosition() method")
                return []
            if not resp or not resp.get("status"):
                return []
            data = resp.get("data", [])
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return data.get("net", data.get("position", []))
            return []
        except Exception as e:
            logger.warning(f"get_positions failed: {e}")
            return []

    def get_ltp(self, exchange: str, tradingsymbol: str, symboltoken: str):
        """
        Fetch LTP for a given symbol.
        Example: exchange='NSE', tradingsymbol='SBIN-EQ', symboltoken='3045'
        """
        try:
            data = self.smart.ltpData(exchange, tradingsymbol, symboltoken)
            return data
        except Exception as e:
            logger.error(f"ltpData failed: {e}")
            return None

    def get_market_data_batch(self, exchange: str, tokens: list):
        """
        Fetch market data for multiple tokens in a single API call.

        Args:
            exchange: Exchange code (e.g., 'NFO')
            tokens: List of token strings

        Returns:
            dict mapping token -> quote data, or empty dict on error
        """
        if not tokens:
            return {}

        import time

        time.sleep(1)  # Rate limit buffer before API call

        try:
            if hasattr(self.smart, "getMarketData"):
                # Convert tokens to strings
                token_list = [str(t) for t in tokens]
                response = self.smart.getMarketData("FULL", {exchange: token_list})

                if response and response.get("status"):
                    result_map = {}
                    response_data = response.get("data", {})

                    # Parse response structure
                    fetched_data = None
                    if isinstance(response_data, dict):
                        if "fetched" in response_data:
                            fetched_data = response_data["fetched"]
                        elif exchange in response_data:
                            fetched_data = response_data[exchange]
                        else:
                            fetched_data = response_data
                    elif isinstance(response_data, list):
                        fetched_data = response_data

                    if isinstance(fetched_data, list):
                        for item in fetched_data:
                            token = str(item.get("token", ""))
                            if token:
                                result_map[token] = item
                    elif isinstance(fetched_data, dict):
                        # If it's a dict, try to extract by token
                        for token in token_list:
                            if token in fetched_data:
                                result_map[token] = fetched_data[token]

                    return result_map
                else:
                    logger.warning(
                        f"Batch market data fetch failed: {response.get('message') if response else 'No response'}"
                    )
                    return {}
            else:
                logger.warning("getMarketData method not available for batch fetch")
                return {}
        except Exception as e:
            logger.error(f"get_market_data_batch failed: {e}", exc_info=True)
            return {}

    def get_quote(self, exchange: str, tradingsymbol: str, symboltoken: str):
        """
        Fetch full quote data (OHLC, volume, OI, bid/ask) for a symbol.

        Returns:
            dict with quote data in format: {'status': True, 'data': {...}} or None on error
        """
        try:
            # Use getMarketData method (correct SmartAPI method)
            if hasattr(self.smart, "getMarketData"):
                params = {"mode": "FULL", "exchangeTokens": {exchange: [str(symboltoken)]}}
                response = self.smart.getMarketData("FULL", {exchange: [str(symboltoken)]})

                # Parse response structure
                if response and response.get("status"):
                    # getMarketData returns data in 'data' field with 'fetched' and 'unfetched' keys
                    response_data = response.get("data", {})

                    # Handle different response structures
                    quote_data = None

                    if isinstance(response_data, dict):
                        # Check for 'fetched' key (successful fetches)
                        if "fetched" in response_data:
                            fetched_data = response_data["fetched"]
                            # fetched_data can be a list (direct quotes) or dict (by exchange)
                            if isinstance(fetched_data, list) and len(fetched_data) > 0:
                                # Find our token in the list
                                for item in fetched_data:
                                    if str(item.get("token", "")) == str(symboltoken):
                                        quote_data = item
                                        break
                                # If not found by token, use first item
                                if not quote_data and len(fetched_data) > 0:
                                    quote_data = fetched_data[0]
                            elif isinstance(fetched_data, dict) and exchange in fetched_data:
                                exchange_data = fetched_data[exchange]
                                # Exchange data is a list of quote objects
                                if isinstance(exchange_data, list) and len(exchange_data) > 0:
                                    # Find our token in the list
                                    for item in exchange_data:
                                        if str(item.get("token", "")) == str(symboltoken):
                                            quote_data = item
                                            break
                                    # If not found by token, use first item
                                    if not quote_data and len(exchange_data) > 0:
                                        quote_data = exchange_data[0]
                                elif isinstance(exchange_data, dict):
                                    quote_data = exchange_data
                        # Check if data is nested by exchange directly
                        elif exchange in response_data:
                            exchange_data = response_data[exchange]
                            # Exchange data may be a list or dict
                            if isinstance(exchange_data, list) and len(exchange_data) > 0:
                                quote_data = exchange_data[0]
                            elif isinstance(exchange_data, dict):
                                quote_data = exchange_data
                        else:
                            # Direct data structure
                            quote_data = response_data
                    elif isinstance(response_data, list) and len(response_data) > 0:
                        quote_data = response_data[0]

                    if quote_data:
                        # Extract bid/ask from depth
                        bid_price = None
                        bid_qty = None
                        offer_price = None
                        offer_qty = None

                        depth = quote_data.get("depth", {})
                        if isinstance(depth, dict):
                            buy_depth = depth.get("buy", [])
                            sell_depth = depth.get("sell", [])
                            if buy_depth and len(buy_depth) > 0 and buy_depth[0].get("price", 0) > 0:
                                bid_price = buy_depth[0].get("price")
                                bid_qty = buy_depth[0].get("quantity")
                            if sell_depth and len(sell_depth) > 0 and sell_depth[0].get("price", 0) > 0:
                                offer_price = sell_depth[0].get("price")
                                offer_qty = sell_depth[0].get("quantity")

                        # Return in expected format
                        return {
                            "status": True,
                            "data": {
                                "ltp": quote_data.get("ltp"),
                                "open": quote_data.get("open"),
                                "high": quote_data.get("high"),
                                "low": quote_data.get("low"),
                                "close": quote_data.get("close"),
                                "volume": quote_data.get("tradeVolume") or quote_data.get("volume"),
                                "oi": quote_data.get("opnInterest")
                                or quote_data.get("oi")
                                or quote_data.get("openInterest"),
                                "change": quote_data.get("netChange") or quote_data.get("change"),
                                "pChange": quote_data.get("percentChange") or quote_data.get("pChange"),
                                "bidPrice": bid_price or quote_data.get("best5BidPrice") or quote_data.get("bidPrice"),
                                "bidQty": bid_qty or quote_data.get("best5BidQty") or quote_data.get("bidQty"),
                                "offerPrice": offer_price
                                or quote_data.get("best5AskPrice")
                                or quote_data.get("offerPrice"),
                                "offerQty": offer_qty or quote_data.get("best5AskQty") or quote_data.get("offerQty"),
                                "exchangeTimestamp": quote_data.get("exchFeedTime")
                                or quote_data.get("exchTradeTime")
                                or quote_data.get("exchangeTimestamp")
                                or quote_data.get("pTime"),
                            },
                        }
                    else:
                        logger.warning(
                            f"getMarketData returned empty/invalid data structure for {tradingsymbol}: {type(response_data)}"
                        )
                        return {"status": False, "data": {}}
                else:
                    logger.warning(
                        f"getMarketData failed for {tradingsymbol}: status={response.get('status') if response else None}, message={response.get('message') if response else 'No response'}"
                    )
                    return response if response else {"status": False, "data": {}}

            # Fallback to LTP if marketData not available
            else:
                logger.warning("getMarketData method not available, falling back to LTP")
                ltp_data = self.get_ltp(exchange, tradingsymbol, symboltoken)
                if ltp_data and ltp_data.get("status"):
                    return {
                        "status": True,
                        "data": {
                            "ltp": ltp_data.get("data", {}).get("ltp"),
                            "open": None,
                            "high": None,
                            "low": None,
                            "close": None,
                            "volume": None,
                            "oi": None,
                            "change": None,
                            "pChange": None,
                            "bidPrice": None,
                            "bidQty": None,
                            "offerPrice": None,
                            "offerQty": None,
                        },
                    }
                return {"status": False, "data": {}}

        except Exception as e:
            logger.error(f"getQuote failed for {tradingsymbol}: {e}", exc_info=True)
            return None

    def get_option_greeks(
        self,
        exchange: str,
        tradingsymbol: str,
        symboltoken: str,
        strike_price: float,
        expiry_date: str,
        option_type: str,
    ):
        """
        Fetch option Greeks (delta, gamma, theta, vega, rho, IV) for an option.
        Includes rate-limit awareness to prevent flooding logs on 'Access denied'.
        """
        try:
            # Use optionGreek method (correct SmartAPI method)
            if hasattr(self.smart, "optionGreek"):
                # Extract underlying name from tradingsymbol
                underlying_name = None
                for name in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]:
                    if name in tradingsymbol.upper():
                        underlying_name = name
                        break

                if not underlying_name:
                    underlying_name = tradingsymbol.split("2")[0] if "2" in tradingsymbol else tradingsymbol[:5]

                # Normalize expiry date format
                expiry_normalized = expiry_date.replace("-", "").upper()
                if len(expiry_normalized) == 8 and expiry_normalized.isdigit():
                    day = expiry_normalized[:2]
                    month = expiry_normalized[2:4]
                    year = expiry_normalized[4:8]
                    month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
                    try:
                        month_name = month_names[int(month) - 1]
                        expiry_normalized = f"{day}{month_name}{year}"
                    except:
                        pass

                # Call optionGreek API
                params = {"name": underlying_name, "expirydate": expiry_normalized}
                
                try:
                    response = self.smart.optionGreek(params)
                except Exception as api_err:
                    err_msg = str(api_err).lower()
                    if "access denied" in err_msg or "exceeding access rate" in err_msg:
                        # Graceful handling of rate limits
                        logger.warning(f"Rate limit hit in optionGreek for {underlying_name}. Pausing 1s...")
                        time.sleep(1)
                        # Optional: single retry
                        try:
                            response = self.smart.optionGreek(params)
                        except:
                            return {"status": False, "message": "Rate limited", "data": {}}
                    else:
                        raise api_err

                if response and response.get("status"):
                    greeks_data = response.get("data", {})
                    option_data = None

                    # Case 1: Response is a list of option objects
                    if isinstance(greeks_data, list):
                        strike_key = int(strike_price)
                        for item in greeks_data:
                            if isinstance(item, dict):
                                item_strike = item.get("strikePrice") or item.get("strike")
                                item_type = item.get("optionType") or item.get("option_type")
                                if item_strike == strike_key or (
                                    isinstance(item_strike, (int, float)) and abs(item_strike - strike_key) < 1
                                ):
                                    if item_type == option_type or item_type == option_type.upper():
                                        option_data = item
                                        break

                    # Case 2: Response is a dict organized by strike
                    elif isinstance(greeks_data, dict):
                        strike_key = str(int(strike_price))
                        strike_data = greeks_data.get(strike_key, {})
                        if option_type == "CE":
                            option_data = strike_data.get("CE", {}) or strike_data.get("ce", {}) or strike_data
                        else:
                            option_data = strike_data.get("PE", {}) or strike_data.get("pe", {}) or strike_data

                    if option_data:
                        return {
                            "status": True,
                            "data": {
                                "delta": option_data.get("delta"),
                                "gamma": option_data.get("gamma"),
                                "theta": option_data.get("theta"),
                                "vega": option_data.get("vega"),
                                "rho": option_data.get("rho"),
                                "iv": option_data.get("iv") or option_data.get("impliedVolatility"),
                                "pTime": option_data.get("pTime") or response.get("timestamp"),
                                "pChange": option_data.get("pChange"),
                                "pOI": option_data.get("pOI"),
                                "pVolume": option_data.get("pVolume"),
                            },
                        }
                    return {"status": False, "data": {}}
                return {"status": False, "data": {}}

            return None

        except Exception as e:
            err_str = str(e)
            if "Access denied" in err_str or "exceeding access rate" in err_str:
                logger.debug(f"Rate limited in getOptionGreek for {tradingsymbol}")
            else:
                logger.error(f"getOptionGreek failed for {tradingsymbol}: {e}")
            return None

    def getOptionGreeks(self, name: str, expirydate: str):
        """
        Wrapper for optionGreek API - fetches Greeks for all strikes of an underlying/expiry.

        Args:
            name: Underlying name (e.g., 'NIFTY')
            expirydate: Expiry date (e.g., '24FEB2026')

        Returns:
            dict with Greeks data for all strikes
        """
        try:
            if hasattr(self.smart, "optionGreek"):
                params = {"name": name, "expirydate": expirydate}
                response = self.smart.optionGreek(params)
                return response
            else:
                logger.warning("optionGreek method not available")
                return None
        except Exception as e:
            logger.error(f"getOptionGreeks failed: {e}", exc_info=True)
            return None

    def get_snap_quote(self, exchange: str, tradingsymbol: str, symboltoken: str):
        """
        Fetch snap quote with depth data (bid/ask levels).

        Returns:
            dict with snap quote data including bid/ask depth or None on error
        """
        try:
            # Try snapQuote method
            if hasattr(self.smart, "snapQuote"):
                params = {"exchange": exchange, "tradingsymbol": tradingsymbol, "symboltoken": symboltoken}
                data = self.smart.snapQuote(params)
                return data

            # Alternative method name
            elif hasattr(self.smart, "getSnapQuote"):
                data = self.smart.getSnapQuote(exchange, tradingsymbol, symboltoken)
                return data

            else:
                logger.warning("snapQuote method not available in SmartAPI")
                return None

        except Exception as e:
            logger.error(f"snapQuote failed: {e}")
            return None

    def get_option_chain(
        self,
        exchange: str,
        tradingsymbol: str,
        symboltoken: str,
        strike_price: int = None,
        expiry_date: str = None,
    ):
        """
        Fetch option chain data for a given underlying.

        Args:
            exchange: Exchange code (e.g., 'NFO', 'BFO')
            tradingsymbol: Trading symbol of the underlying (e.g., 'NIFTY', 'BANKNIFTY')
            symboltoken: Token of the underlying
            strike_price: Optional strike price filter
            expiry_date: Optional expiry date filter (format: DDMMMYYYY, e.g., '30DEC2024')

        Returns:
            dict with option chain data or None on error
        """
        try:
            # SmartAPI option chain method
            # Note: Check SmartAPI docs for exact method name and parameters
            # Common method names: getOptionChain, optionChain, etc.

            # Try the most common SmartAPI option chain method
            if hasattr(self.smart, "optionChain"):
                params = {
                    "exchange": exchange,
                    "tradingsymbol": tradingsymbol,
                    "symboltoken": symboltoken,
                }
                if strike_price:
                    params["strikeprice"] = strike_price
                if expiry_date:
                    params["expirydate"] = expiry_date

                data = self.smart.optionChain(params)
                return data

            # Alternative: Try getOptionChain
            elif hasattr(self.smart, "getOptionChain"):
                data = self.smart.getOptionChain(exchange, tradingsymbol, symboltoken, strike_price, expiry_date)
                return data

            # Fallback: Use market data API if available
            elif hasattr(self.smart, "marketData"):
                # Some SmartAPI versions use marketData with option chain type
                params = {"mode": "FULL", "exchangeTokens": {exchange: [symboltoken]}}  # or "LTP" for last traded price
                data = self.smart.marketData(params)
                return data

            else:
                logger.warning(
                    "Option chain method not found in SmartAPI. Available methods: "
                    + str([m for m in dir(self.smart) if not m.startswith("_")])
                )
                return None

        except Exception as e:
            logger.error(f"get_option_chain failed: {e}")
            return None

    def _check_live_trading_allowed(self, operation: str = "order placement"):
        """
        Check if live trading is allowed for operations that modify positions.
        This guard is separate from initialization guard to allow data fetching.
        """
        flag = os.getenv("SYSTEM3_LIVE_TRADING_ALLOWED", "").strip().lower()
        allowed = flag in {"1", "true", "yes", "y"}
        if not allowed:
            msg = f"LIVE TRADING BLOCKED: {operation} requires SYSTEM3_LIVE_TRADING_ALLOWED to be enabled"
            logger.error(msg)
            raise RuntimeError(msg)
        return True

    def get_option_chain_by_underlying(
        self,
        underlying_name: str,
        exchange: str = "NFO",
        include_all_strikes: bool = True,
        strike_band_mode: str = "NEAR_ATM",
        near_atm_strikes: int = 10,
        near_atm_percent: float = 0.02,
    ):
        """
        Fetch option chain for an underlying (e.g., NIFTY, BANKNIFTY).
        This method uses the instruments master to find all options and fetches their LTPs.

        This is a DATA-ONLY operation and does not require live trading permission.

        Args:
            underlying_name: Name of underlying (e.g., 'NIFTY', 'BANKNIFTY')
            exchange: Exchange code (default: 'NFO' for NSE, 'BFO' for BSE)
            include_all_strikes: If True, fetch all strikes; if False, fetch only ATM strikes

        Returns:
            list of dicts with option chain data, or None on error
        """
        try:
            from core.brokers.angel_one.instruments import (
                find_options_for_underlying,
                find_index_by_name,
            )
            import pandas as pd
            from datetime import date

            # Get index spot price
            index_exchange = "NSE" if exchange == "NFO" else "BSE"
            idx_row = find_index_by_name(underlying_name, index_exchange)
            if not idx_row:
                logger.error(f"Index {underlying_name} not found in {index_exchange}")
                return None

            spot = self.get_ltp(index_exchange, idx_row["symbol"], idx_row["token"])
            if not spot or not spot.get("status"):
                logger.error(f"Could not fetch spot price for {underlying_name}")
                return None

            try:
                spot_price = float(spot["data"]["ltp"])
            except (KeyError, ValueError, TypeError):
                logger.error(f"Invalid spot price data: {spot}")
                return None

            # Get all options for underlying
            df_opts = find_options_for_underlying(underlying_name, exchange)
            if df_opts is None or df_opts.empty:
                logger.error(f"No options found for {underlying_name} on {exchange}")
                return None

            # Parse expiry dates
            def _parse_expiry(x):
                x = str(x).strip()
                if not x:
                    return None
                from datetime import datetime

                for fmt in ("%d%b%Y", "%d%b%y", "%d-%b-%Y"):
                    try:
                        return datetime.strptime(x, fmt).date()
                    except:
                        continue
                return None

            df_opts = df_opts.copy()
            df_opts["expiry_dt"] = df_opts["expiry"].apply(_parse_expiry)

            # Filter to current/upcoming expiries
            today = date.today()
            future_expiries = df_opts[df_opts["expiry_dt"] >= today] if "expiry_dt" in df_opts.columns else df_opts

            if future_expiries.empty:
                future_expiries = df_opts

            # Get nearest expiry
            if "expiry_dt" in future_expiries.columns and not future_expiries["expiry_dt"].isna().all():
                nearest_expiry = future_expiries["expiry_dt"].min()
                df_opts = future_expiries[future_expiries["expiry_dt"] == nearest_expiry]
            else:
                # Use first expiry if parsing failed
                df_opts = future_expiries.head(100)  # Limit to avoid too many calls

            # Normalize strikes
            def _normalize_strike(raw):
                try:
                    v = float(raw)
                    if v > 100000:
                        v = v / 100.0
                    return v
                except:
                    return None

            # Use .copy() to avoid SettingWithCopyWarning
            df_opts = df_opts.copy()
            df_opts["strike_val"] = df_opts["strike"].apply(_normalize_strike)
            df_opts = df_opts.dropna(subset=["strike_val"])

            # TWO-TIER FETCH: Filter strikes based on mode
            # Tier 1: Near-ATM strikes (fast, for immediate strategy decisions)
            # Tier 2: Full chain (background, for deep analysis)
            original_df_opts = df_opts.copy()

            if strike_band_mode == "NEAR_ATM" or not include_all_strikes:
                # Filter to near-ATM strikes
                df_opts = df_opts.copy()
                df_opts["dist_from_spot"] = (df_opts["strike_val"] - spot_price).abs()

                # Use either strike count or percentage band (whichever is more restrictive)
                if near_atm_strikes > 0:
                    # Sort by distance and take nearest N strikes
                    df_opts = df_opts.sort_values("dist_from_spot").head(near_atm_strikes * 2)  # *2 for CE+PE

                if near_atm_percent > 0:
                    # Also filter by percentage band
                    percent_filter = df_opts["dist_from_spot"] <= (spot_price * near_atm_percent)
                    df_opts = df_opts[percent_filter]

                logger.info(f"[TIER-1] Filtered to {len(df_opts)} near-ATM strikes (mode: {strike_band_mode})")
            else:
                logger.info(f"[FULL] Fetching all {len(df_opts)} strikes (mode: FULL)")

            # Separate CE and PE
            sym_series = df_opts["symbol"].astype(str)
            ce_df = df_opts[sym_series.str.endswith("CE")].copy()
            pe_df = df_opts[sym_series.str.endswith("PE")].copy()

            option_chain = []

            # Fetch comprehensive data for each option (with progress indication for large datasets)
            all_options = pd.concat([ce_df, pe_df])
            total_options = len(all_options)

            if total_options > 20:
                logger.info(f"Fetching comprehensive data for {total_options} options (this may take a moment)...")

            # Get current timestamp once for all options
            from datetime import datetime
            import pytz

            ist = pytz.timezone("Asia/Kolkata")
            now_ist = datetime.now(ist)
            timestamp_ist = now_ist.strftime("%Y-%m-%d %H:%M:%S IST")
            timestamp_epoch = now_ist.timestamp()

            # OPTIMIZATION 1: Fetch Greeks in batch once per underlying/expiry instead of per option
            # This reduces API calls from N (one per option) to 1 (one per expiry)
            expiry_str = str(df_opts["expiry"].iloc[0] if not df_opts.empty else "").replace("-", "").upper()
            batch_greeks = None
            try:
                # Add delay before batch Greeks call to avoid rate limits
                time.sleep(0.2)  # 200ms delay
                # Try to get all Greeks for this underlying/expiry in one call
                batch_greeks = self.getOptionGreeks(underlying_name, expiry_str)
                if batch_greeks and batch_greeks.get("status") and batch_greeks.get("data"):
                    logger.info(f"[OK] Batch Greeks fetched for {underlying_name} {expiry_str}")
                else:
                    batch_greeks = None
                    # If batch fails for SENSEX, skip per-option calls (known issue)
                    if underlying_name == "SENSEX":
                        logger.warning(f"SENSEX batch Greeks failed - will use Black-Scholes fallback for all options")
            except Exception as e:
                error_str = str(e).lower()
                if "rate" in error_str or "access denied" in error_str:
                    logger.warning(
                        f"Rate limit on batch Greeks for {underlying_name} - will use Black-Scholes fallback"
                    )
                    batch_greeks = None
                    # For SENSEX, skip per-option calls entirely if rate limited
                    if underlying_name == "SENSEX":
                        logger.warning(f"SENSEX rate limited - using Black-Scholes for all options")
                else:
                    logger.debug(f"Batch Greeks fetch failed (will use per-option): {e}")
                    batch_greeks = None

            # OPTIMIZATION 2: Fetch ALL market data in batches with parallel processing
            # This reduces API calls from N (one per option) to ~N/50 (batches of 50)
            # And parallelizes batch fetches using ThreadPool
            import time
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import json as json_module

            # Load config for parallel workers
            try:
                from pathlib import Path as PathLib

                config_path = PathLib(ROOT_DIR) / "config" / "runtime_config.json"
                if config_path.exists():
                    with open(config_path, "r") as f:
                        runtime_config = json_module.load(f)
                    max_workers = runtime_config.get("fetch_parallel_workers", 8)
                    batch_size = runtime_config.get("fetch_batch_size", 50)
                    fetch_timeout = runtime_config.get("fetch_timeout_sec", 5)
                else:
                    max_workers = 8
                    batch_size = 50
                    fetch_timeout = 5
            except:
                max_workers = 8
                batch_size = 50
                fetch_timeout = 5

            all_tokens = [str(row["token"]) for _, row in all_options.iterrows()]
            market_data_map = {}  # token -> quote_data dict

            logger.info(
                f"[BATCH+PARALLEL] Fetching market data for {total_options} options in batches of {batch_size} with {max_workers} workers..."
            )
            print(
                f"[BATCH+PARALLEL] Fetching market data for {total_options} options in batches of {batch_size} with {max_workers} workers..."
            )

            start_fetch = time.time()

            # Create batches
            batches = []
            for i in range(0, len(all_tokens), batch_size):
                batches.append((i // batch_size + 1, all_tokens[i : i + batch_size]))

            total_batches = len(batches)

            # Fetch batches in parallel
            def fetch_batch(batch_info):
                batch_num, batch_tokens = batch_info
                try:
                    batch_data = self.get_market_data_batch(exchange, batch_tokens)
                    return batch_num, batch_data
                except Exception as e:
                    logger.debug(f"Batch {batch_num} failed: {e}")
                    return batch_num, {}

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_batch = {executor.submit(fetch_batch, batch): batch[0] for batch in batches}

                for future in as_completed(future_to_batch):
                    batch_num = future_to_batch[future]
                    try:
                        _, batch_data = future.result(timeout=fetch_timeout)
                        market_data_map.update(batch_data)
                        logger.debug(f"  Batch {batch_num}/{total_batches}: Got {len(batch_data)} responses")
                    except Exception as e:
                        logger.warning(f"  Batch {batch_num}/{total_batches} failed: {e}")

            fetch_duration = time.time() - start_fetch
            logger.info(
                f"[OK] Fetched market data for {len(market_data_map)}/{total_options} options in {fetch_duration:.2f}s"
            )
            print(
                f"[OK] Fetched market data for {len(market_data_map)}/{total_options} options in {fetch_duration:.2f}s"
            )

            # Now process each option using the pre-fetched market data
            for idx, (_, row) in enumerate(all_options.iterrows(), 1):
                opt_type = "CE" if str(row["symbol"]).endswith("CE") else "PE"

                # Show progress for large datasets (more frequent updates)
                if total_options > 20 and idx % 10 == 0:
                    logger.info(f"  Processing: {idx}/{total_options} options...")
                    print(f"  Processing: {idx}/{total_options} options...", flush=True)

                # Initialize option data dict with instrument master data
                # All market data fields default to None to prevent KeyErrors downstream
                opt_data = {
                    "underlying": underlying_name,
                    "exchange": exchange,
                    "tradingSymbol": str(row.get("symbol", "")),
                    "symbol": str(row.get("symbol", "")),
                    "name": str(row.get("name", underlying_name)),
                    "token": str(row.get("token", "")),
                    "expiry": str(row.get("expiry", "")),
                    "expiry_date": str(row.get("expiry_dt", "")),
                    "strike": float(row["strike_val"]),
                    "option_type": opt_type,
                    "instrumentType": str(row.get("instrumenttype", "")),
                    "lotSize": float(row.get("lotsize", 0)) if pd.notna(row.get("lotsize")) else None,
                    "tickSize": float(row.get("tick_size", 0.05)) if pd.notna(row.get("tick_size")) else 0.05,
                    "spot_price": spot_price,
                    "timestamp_ist": timestamp_ist,
                    "timestamp_epoch": timestamp_epoch,
                    "ltp": None, "open": None, "high": None, "low": None, "close": None,
                    "volume": None, "oi": None, "change": None, "pChange": None,
                    "bidPrice": None, "bidQty": None, "offerPrice": None, "offerQty": None,
                    "pTime": None, "delta": None, "gamma": None, "theta": None, "vega": None,
                    "rho": None, "iv": None, "pOI": None, "pVolume": None
                }

                # Use pre-fetched market data instead of individual API call
                token_str = str(row["token"])
                quote_raw = market_data_map.get(token_str)

                if quote_raw:
                    # Parse quote data from batch response
                    try:
                        # Extract bid/ask from depth
                        bid_price = None
                        bid_qty = None
                        offer_price = None
                        offer_qty = None

                        depth = quote_raw.get("depth", {})
                        if isinstance(depth, dict):
                            buy_depth = depth.get("buy", [])
                            sell_depth = depth.get("sell", [])
                            if buy_depth and len(buy_depth) > 0 and buy_depth[0].get("price", 0) > 0:
                                bid_price = buy_depth[0].get("price")
                                bid_qty = buy_depth[0].get("quantity")
                            if sell_depth and len(sell_depth) > 0 and sell_depth[0].get("price", 0) > 0:
                                offer_price = sell_depth[0].get("price")
                                offer_qty = sell_depth[0].get("quantity")

                        # Parse quote data
                        opt_data["ltp"] = float(quote_raw.get("ltp", 0)) if quote_raw.get("ltp") is not None else None
                        opt_data["open"] = (
                            float(quote_raw.get("open", 0)) if quote_raw.get("open") is not None else None
                        )
                        opt_data["high"] = (
                            float(quote_raw.get("high", 0)) if quote_raw.get("high") is not None else None
                        )
                        opt_data["low"] = float(quote_raw.get("low", 0)) if quote_raw.get("low") is not None else None
                        opt_data["close"] = (
                            float(quote_raw.get("close", 0)) if quote_raw.get("close") is not None else None
                        )
                        opt_data["volume"] = (
                            int(quote_raw.get("tradeVolume") or quote_raw.get("volume", 0))
                            if quote_raw.get("tradeVolume") or quote_raw.get("volume")
                            else None
                        )
                        opt_data["oi"] = (
                            int(quote_raw.get("opnInterest") or quote_raw.get("oi") or quote_raw.get("openInterest", 0))
                            if (quote_raw.get("opnInterest") or quote_raw.get("oi") or quote_raw.get("openInterest"))
                            else None
                        )
                        opt_data["change"] = (
                            float(quote_raw.get("netChange") or quote_raw.get("change", 0))
                            if (quote_raw.get("netChange") or quote_raw.get("change")) is not None
                            else None
                        )
                        opt_data["pChange"] = (
                            float(quote_raw.get("percentChange") or quote_raw.get("pChange", 0))
                            if (quote_raw.get("percentChange") or quote_raw.get("pChange")) is not None
                            else None
                        )
                        opt_data["bidPrice"] = (
                            float(bid_price or quote_raw.get("best5BidPrice") or quote_raw.get("bidPrice", 0))
                            if (bid_price or quote_raw.get("best5BidPrice") or quote_raw.get("bidPrice")) is not None
                            else None
                        )
                        opt_data["bidQty"] = (
                            int(bid_qty or quote_raw.get("best5BidQty") or quote_raw.get("bidQty", 0))
                            if (bid_qty or quote_raw.get("best5BidQty") or quote_raw.get("bidQty")) is not None
                            else None
                        )
                        opt_data["offerPrice"] = (
                            float(offer_price or quote_raw.get("best5AskPrice") or quote_raw.get("offerPrice", 0))
                            if (offer_price or quote_raw.get("best5AskPrice") or quote_raw.get("offerPrice"))
                            is not None
                            else None
                        )
                        opt_data["offerQty"] = (
                            int(offer_qty or quote_raw.get("best5AskQty") or quote_raw.get("offerQty", 0))
                            if (offer_qty or quote_raw.get("best5AskQty") or quote_raw.get("offerQty")) is not None
                            else None
                        )
                        opt_data["pTime"] = (
                            quote_raw.get("exchFeedTime")
                            or quote_raw.get("exchTradeTime")
                            or quote_raw.get("exchangeTimestamp")
                            or quote_raw.get("pTime")
                        )
                    except (KeyError, ValueError, TypeError) as e:
                        logger.debug(f"Error parsing batch quote data for {row['symbol']}: {e}")
                        # Fall through to LTP fallback
                        quote_raw = None
                else:
                    # Fallback: Try LTP if batch data not available
                    quote_raw = None

                if not quote_raw:
                    # Fallback: Try individual LTP call if batch failed
                    if not opt_data.get("ltp"):
                        try:
                            ltp_data = self.get_ltp(exchange, row["symbol"], token_str)
                            if ltp_data and ltp_data.get("status"):
                                opt_data["ltp"] = float(ltp_data["data"]["ltp"])
                        except Exception as e:
                            logger.debug(f"LTP fallback failed for {row['symbol']}: {e}")
                            opt_data["ltp"] = None

                    # Set defaults for other fields if quote not available
                    if opt_data.get("ltp") is None:
                        opt_data.update(
                            {
                                "ltp": None,
                                "open": None,
                                "high": None,
                                "low": None,
                                "close": None,
                                "volume": None,
                                "oi": None,
                                "change": None,
                                "pChange": None,
                                "bidPrice": None,
                                "bidQty": None,
                                "offerPrice": None,
                                "offerQty": None,
                            }
                        )

                # Fetch option Greeks (delta, gamma, theta, vega, rho, IV)
                # OPTIMIZATION: Use batch Greeks if available, otherwise try per-option API
                greeks_data = None
                strike_val = float(row["strike_val"])

                # First try: Use batch Greeks data if we fetched it earlier
                if batch_greeks and batch_greeks.get("status") and batch_greeks.get("data"):
                    try:
                        greeks_list = batch_greeks.get("data", [])
                        if isinstance(greeks_list, list):
                            # Find matching strike and option type
                            for item in greeks_list:
                                if isinstance(item, dict):
                                    item_strike = item.get("strikePrice") or item.get("strike")
                                    item_type = item.get("optionType") or item.get("option_type", "")
                                    if (
                                        item_strike
                                        and abs(float(item_strike) - strike_val) < 1
                                        and item_type.upper() == opt_type.upper()
                                    ):
                                        greeks_data = {"status": True, "data": item}
                                        break
                    except Exception as e:
                        logger.debug(f"Error parsing batch Greeks: {e}")

                # Second try: Per-option API call (only if batch failed and not SENSEX)
                if not greeks_data:
                    # Skip per-option calls for SENSEX if batch failed (known rate limit issues)
                    if underlying_name == "SENSEX" and (not batch_greeks or not batch_greeks.get("status")):
                        logger.debug(
                            f"Skipping per-option Greeks API for SENSEX {row['symbol']} (batch failed, using Black-Scholes)"
                        )
                        greeks_data = None
                    else:
                        expiry_str = str(row.get("expiry", "")).replace("-", "").upper()
                        # Add delay before Greeks API call to avoid rate limits
                        time.sleep(0.2)  # Increased to 200ms delay for Greeks API
                        try:
                            greeks_data = self.get_option_greeks(
                                exchange, row["symbol"], str(row["token"]), strike_val, expiry_str, opt_type
                            )
                        except Exception as e:
                            error_str = str(e).lower()
                            if "rate" in error_str or "access denied" in error_str:
                                logger.debug(
                                    f"Rate limit on Greeks API for {row['symbol']}, using Black-Scholes fallback"
                                )
                                greeks_data = None
                            else:
                                raise

                if greeks_data and greeks_data.get("status"):
                    try:
                        greeks = greeks_data.get("data", {})
                        opt_data["delta"] = float(greeks.get("delta", 0)) if greeks.get("delta") is not None else None
                        opt_data["gamma"] = float(greeks.get("gamma", 0)) if greeks.get("gamma") is not None else None
                        opt_data["theta"] = float(greeks.get("theta", 0)) if greeks.get("theta") is not None else None
                        opt_data["vega"] = float(greeks.get("vega", 0)) if greeks.get("vega") is not None else None
                        opt_data["rho"] = float(greeks.get("rho", 0)) if greeks.get("rho") is not None else None
                        opt_data["iv"] = float(greeks.get("iv", 0)) if greeks.get("iv") is not None else None
                        opt_data["pTime"] = greeks.get("pTime")
                        opt_data["pChange"] = (
                            float(greeks.get("pChange", 0))
                            if greeks.get("pChange") is not None
                            else opt_data.get("pChange")
                        )
                        opt_data["pOI"] = int(greeks.get("pOI", 0)) if greeks.get("pOI") else None
                        opt_data["pVolume"] = int(greeks.get("pVolume", 0)) if greeks.get("pVolume") else None
                    except (KeyError, ValueError, TypeError) as e:
                        logger.debug(f"Error parsing Greeks data for {row['symbol']}: {e}")
                        # Fall through to Black-Scholes calculation
                        greeks_data = None
                else:
                    greeks_data = None

                # Fallback: Calculate Greeks using Black-Scholes if API failed
                if not greeks_data or not greeks_data.get("status"):
                    try:
                        from src.metrics.greeks import calculate_greeks_from_market_price
                        from datetime import datetime
                        import pytz

                        # Calculate time to expiry
                        # Use expiry_date from opt_data (already set earlier in the code)
                        expiry_date_str = (
                            opt_data.get("expiry_date", "") or row.get("expiry_dt", "") or row.get("expiry", "")
                        )
                        if expiry_date_str:
                            try:
                                if isinstance(expiry_date_str, str):
                                    # Try parsing different date formats
                                    expiry_date = None
                                    for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y%m%d", "%d%b%Y", "%d%B%Y"]:
                                        try:
                                            expiry_date = datetime.strptime(expiry_date_str.split()[0], fmt)
                                            break
                                        except:
                                            continue

                                    if expiry_date:
                                        ist = pytz.timezone("Asia/Kolkata")
                                        now = datetime.now(ist)
                                        time_to_expiry = (expiry_date.replace(tzinfo=ist) - now).total_seconds() / (
                                            365.25 * 24 * 3600
                                        )

                                        if time_to_expiry > 0 and opt_data.get("ltp") and opt_data.get("ltp") > 0:
                                            # Calculate Greeks from market price
                                            mid_price = opt_data.get("ltp")
                                            if opt_data.get("bidPrice") and opt_data.get("offerPrice"):
                                                mid_price = (
                                                    opt_data.get("bidPrice") + opt_data.get("offerPrice")
                                                ) / 2.0

                                            greeks_calculated = calculate_greeks_from_market_price(
                                                spot=spot_price,
                                                strike=float(row["strike_val"]),
                                                time_to_expiry=time_to_expiry,
                                                option_type=opt_type,
                                                market_price=mid_price,
                                                risk_free_rate=0.06,  # 6% risk-free rate
                                            )

                                            if greeks_calculated:
                                                opt_data["delta"] = greeks_calculated.get("delta")
                                                opt_data["gamma"] = greeks_calculated.get("gamma")
                                                opt_data["theta"] = greeks_calculated.get("theta")
                                                opt_data["vega"] = greeks_calculated.get("vega")
                                                opt_data["rho"] = greeks_calculated.get("rho")
                                                opt_data["iv"] = greeks_calculated.get("iv")
                            except Exception as e:
                                logger.debug(f"Date parsing failed for {row['symbol']}: {e}")
                    except Exception as e:
                        logger.debug(f"Black-Scholes calculation failed for {row['symbol']}: {e}")

                    # Set defaults if calculation also fails
                    if opt_data.get("delta") is None:
                        opt_data.update(
                            {
                                "delta": None,
                                "gamma": None,
                                "theta": None,
                                "vega": None,
                                "rho": None,
                                "iv": None,
                                "pTime": None,
                                "pOI": None,
                                "pVolume": None,
                            }
                        )
                    else:
                        # If Greeks were calculated via Black-Scholes, estimate pOI and pVolume
                        # pOI = Premium-weighted OI (OI * premium per contract)
                        # pVolume = Premium-weighted Volume (Volume * premium per contract)
                        if opt_data.get("oi") is not None and opt_data.get("ltp") is not None:
                            try:
                                # Premium OI = OI * LTP (total premium value in OI)
                                opt_data["pOI"] = int(opt_data["oi"] * opt_data["ltp"]) if opt_data["ltp"] > 0 else None
                            except:
                                opt_data["pOI"] = None

                        if opt_data.get("volume") is not None and opt_data.get("ltp") is not None:
                            try:
                                # Premium Volume = Volume * LTP (total premium value in volume)
                                opt_data["pVolume"] = (
                                    int(opt_data["volume"] * opt_data["ltp"]) if opt_data["ltp"] > 0 else None
                                )
                            except:
                                opt_data["pVolume"] = None

                # Calculate moneyness
                opt_data["moneyness"] = (
                    "ATM"
                    if abs(row["strike_val"] - spot_price) < (spot_price * 0.01)
                    else (
                        "ITM"
                        if (opt_type == "CE" and row["strike_val"] < spot_price)
                        or (opt_type == "PE" and row["strike_val"] > spot_price)
                        else "OTM"
                    )
                )

                # Calculate change percentage if we have LTP and close
                if opt_data.get("ltp") and opt_data.get("close"):
                    try:
                        opt_data["change"] = opt_data["ltp"] - opt_data["close"]
                        opt_data["pChange"] = (
                            ((opt_data["ltp"] - opt_data["close"]) / opt_data["close"] * 100)
                            if opt_data["close"] > 0
                            else None
                        )
                    except:
                        pass

                option_chain.append(opt_data)

            # Sort by strike
            option_chain.sort(key=lambda x: x["strike"])

            logger.info(f"Fetched option chain for {underlying_name}: {len(option_chain)} options")
            return option_chain

        except Exception as e:
            logger.error(f"get_option_chain_by_underlying failed: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None
