"""
World-Class Option Chain Automation System - Master Orchestrator
==================================================================

This is a production-ready, fully integrated option chain automation system
that combines:
- Real-time data fetching (WebSocket + REST fallback)
- Advanced option chain analysis (Greeks, IV, OI)
- ML-powered signal generation
- Multi-layer risk management
- Paper trading execution
- Comprehensive monitoring and alerting

Features:
- Automatic market hours detection
- Self-healing data pipeline
- Multi-model ensemble predictions
- Dynamic position sizing
- Real-time PnL tracking
- Comprehensive logging and monitoring

Author: AI System Builder
Date: 2026-02-02
Version: 1.0.0
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import time
import json
import logging
import threading
import traceback
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
import pytz

# Ensure project root in path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import core components (with optional broker support)
try:
    from core.brokers.angel_one.broker import AngelOneBroker
    BROKER_AVAILABLE = True
except ImportError:
    BROKER_AVAILABLE = False

try:
    from src.angel.live_chain_ws import LiveChainWebSocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

try:
    from src.angel.live_chain_rest import LiveChainREST
    REST_AVAILABLE = True
except ImportError:
    REST_AVAILABLE = False
from src.ml.ensemble_predictor import EnsemblePredictor
from src.selector.strategy_engine import StrategyEngine
from src.trading.paper_executor import PaperExecutor
from src.trading.pnl_tracker import PnLTracker
from src.trading.dynamic_risk_management import DynamicRiskManager
from src.trading.advanced_position_sizing import AdvancedPositionSizing
from src.utils.market_hours import is_market_open
from src.validation.qc_validator import QCValidator
from core.utils.logger import logger

# Configure logging
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"option_chain_automation_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@dataclass
class SystemConfig:
    """System configuration parameters."""
    # Data fetching
    refresh_interval_seconds: int = 5
    use_websocket: bool = True
    websocket_timeout: int = 30
    rest_fallback_enabled: bool = True
    
    # Trading parameters
    max_positions: int = 5
    min_confidence: float = 0.5  # Optimized: Lowered from 0.75 to 0.5 for more trading opportunities
    slippage_pct: float = 0.1
    
    # Risk management
    max_daily_loss_pct: float = 2.0
    max_position_size_pct: float = 20.0
    stop_loss_pct: float = 3.0
    take_profit_pct: float = 5.0
    
    # Market hours
    market_open_time: str = "09:15"
    market_close_time: str = "15:30"
    timezone: str = "Asia/Kolkata"
    market_check_interval: int = 30  # Seconds between market checks when closed
    
    # Simulation mode
    enable_simulation: bool = False
    sim_scenario: Optional[str] = None  # TREND_UP, TREND_DOWN, RANGE, HIGH_VOL, LOW_LIQUIDITY, DATA_ERRORS
    
    # PAPER_SANITY mode - Force trades for system verification
    paper_sanity_mode: bool = False  # If True, force at least 1 trade per cycle if QC >= 70% and confidence >= 0.60
    
    # Monitoring
    heartbeat_interval: int = 60
    health_check_interval: int = 300
    
    # Output paths
    output_dir: Path = ROOT_DIR / "outputs"
    storage_dir: Path = ROOT_DIR / "storage" / "live"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'SystemConfig':
        """Load from JSON file."""
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
                return cls(**data)
        return cls()
    
    def save(self, config_path: Path):
        """Save to JSON file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)


@dataclass
class SystemStatus:
    """System status tracking."""
    is_running: bool = False
    is_connected: bool = False
    last_data_fetch: Optional[datetime] = None
    last_signal_generated: Optional[datetime] = None
    last_trade_executed: Optional[datetime] = None
    total_cycles: int = 0
    successful_fetches: int = 0
    failed_fetches: int = 0
    signals_generated: int = 0
    trades_executed: int = 0
    current_positions: int = 0
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert datetime to string
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat() if value else None
        return data


class OptionChainAutomationMaster:
    """
    Master orchestrator for option chain automation system.
    
    This class coordinates all components:
    - Data fetching (WebSocket + REST)
    - Option chain analysis
    - Signal generation (ML + strategy)
    - Risk management
    - Trade execution (paper trading)
    - Monitoring and alerting
    """
    
    # Available indices for trading
    AVAILABLE_INDICES = [
        {"name": "NIFTY", "exchange": "NFO"},
        {"name": "BANKNIFTY", "exchange": "NFO"},
        {"name": "FINNIFTY", "exchange": "NFO"},
        {"name": "MIDCPNIFTY", "exchange": "NFO"},
        {"name": "SENSEX", "exchange": "BFO"},
    ]
    
    def __init__(self, config: Optional[SystemConfig] = None):
        """
        Initialize the master orchestrator.
        
        Args:
            config: System configuration (uses default if None)
        """
        self.config = config or SystemConfig()
        self.status = SystemStatus()
        
        # Core components
        self.broker: Optional[AngelOneBroker] = None
        self.websocket: Optional[LiveChainWebSocket] = None
        self.rest_fallback: Optional[LiveChainREST] = None
        self.ensemble_predictor: Optional[EnsemblePredictor] = None
        self.strategy_engine: Optional[StrategyEngine] = None
        self.paper_executor: Optional[PaperExecutor] = None
        self.pnl_tracker: Optional[PnLTracker] = None
        self.risk_manager: Optional[DynamicRiskManager] = None
        self.position_sizer: Optional[AdvancedPositionSizing] = None
        self.qc_validator: Optional[QCValidator] = None
        
        # Data storage
        self.current_chain_data: Dict[str, pd.DataFrame] = {}
        self.expiry_map: Dict[str, str] = {}
        
        # WebSocket data storage
        self._ws_data_cache: Dict[str, Dict[str, Dict]] = {}  # {underlying: {token: data}}
        self._ws_data_lock = threading.Lock()
        
        # Threading
        self._stop_event = threading.Event()
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._health_check_thread: Optional[threading.Thread] = None
        
        # Timezone
        self.tz = pytz.timezone(self.config.timezone)
        
        # Simulation mode
        self.sim_mode = False
        self.sim_scenario = None
        self.sim_engine = None
        self.sim_seed = None  # Random seed for deterministic simulation
        
        # LIVE safety lock - trades disabled by default in LIVE mode
        self.live_trade_enabled = False
        
        # PAPER_SANITY mode - Force trades for system verification
        self.paper_sanity_mode = self.config.paper_sanity_mode
        
        # Ensure output directories exist
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self.config.storage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("OptionChainAutomationMaster initialized")
    
    def initialize(self) -> bool:
        """
        Initialize all system components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("=" * 80)
            logger.info("INITIALIZING OPTION CHAIN AUTOMATION SYSTEM")
            logger.info("=" * 80)
            
            # 1. Initialize broker
            logger.info("Step 1/8: Initializing broker...")
            if not BROKER_AVAILABLE:
                logger.warning("[WARN] Broker not available (SmartApi not installed) - system will run in test mode")
                self.broker = None
            else:
                try:
                    self.broker = AngelOneBroker(allow_data_only=True)
                    logger.info("[OK] Broker initialized successfully")
                except Exception as e:
                    logger.warning(f"[WARN] Broker initialization failed: {e} - system will run in test mode")
                    self.broker = None
            
            # 2. Initialize data fetchers
            logger.info("Step 2/8: Initializing data fetchers...")
            if self.config.use_websocket and WEBSOCKET_AVAILABLE and self.broker:
                try:
                    self.websocket = LiveChainWebSocket(self.broker)
                    logger.info("[OK] WebSocket initialized")
                except Exception as e:
                    logger.warning(f"[WARN] WebSocket initialization failed: {e}, using REST only")
                    self.config.use_websocket = False
            else:
                logger.warning("[WARN] WebSocket not available, using REST only")
                self.config.use_websocket = False
            
            if self.config.rest_fallback_enabled:
                if REST_AVAILABLE and self.broker:
                    try:
                        self.rest_fallback = LiveChainREST(self.broker)
                        logger.info("[OK] REST fallback initialized")
                    except Exception as e:
                        logger.warning(f"[WARN] REST fallback initialization failed: {e}")
                        self.rest_fallback = None
                else:
                    logger.warning("[WARN] REST fallback not available (broker not initialized)")
                    self.rest_fallback = None
            
            # 3. Initialize ML predictor
            logger.info("Step 3/8: Initializing ML ensemble predictor...")
            try:
                self.ensemble_predictor = EnsemblePredictor()
                logger.info("[OK] ML ensemble predictor initialized")
            except Exception as e:
                logger.warning(f"[WARN] ML predictor initialization failed: {e}, continuing without ML")
            
            # 4. Initialize strategy engine
            logger.info("Step 4/8: Initializing strategy engine...")
            try:
                self.strategy_engine = StrategyEngine(paper_sanity_mode=self.paper_sanity_mode)
                logger.info("[OK] Strategy engine initialized")
            except Exception as e:
                logger.error(f"[FAIL] Strategy engine initialization failed: {e}")
                return False
            
            # 5. Initialize paper executor
            logger.info("Step 5/8: Initializing paper executor...")
            try:
                self.paper_executor = PaperExecutor(
                    slippage_pct=self.config.slippage_pct,
                    max_positions=self.config.max_positions
                )
                logger.info("[OK] Paper executor initialized")
            except Exception as e:
                logger.error(f"[FAIL] Paper executor initialization failed: {e}")
                return False
            
            # 6. Initialize PnL tracker
            logger.info("Step 6/8: Initializing PnL tracker...")
            try:
                self.pnl_tracker = PnLTracker()
                logger.info("[OK] PnL tracker initialized")
            except Exception as e:
                logger.error(f"[FAIL] PnL tracker initialization failed: {e}")
                return False
            
            # 7. Initialize risk manager
            logger.info("Step 7/8: Initializing risk manager...")
            try:
                self.risk_manager = DynamicRiskManager()
                logger.info("[OK] Risk manager initialized")
            except Exception as e:
                logger.warning(f"[WARN] Risk manager initialization failed: {e}, using defaults")
                self.risk_manager = DynamicRiskManager()
            
            # 8. Initialize position sizer
            logger.info("Step 8/8: Initializing position sizer...")
            try:
                self.position_sizer = AdvancedPositionSizing()
                logger.info("[OK] Position sizer initialized")
            except Exception as e:
                logger.warning(f"[WARN] Position sizer initialization failed: {e}, using defaults")
            
            # 9. Initialize QC validator
            try:
                self.qc_validator = QCValidator(sim_mode=self.sim_mode, paper_sanity_mode=self.paper_sanity_mode)
                logger.info("[OK] QC validator initialized")
            except Exception as e:
                logger.warning(f"[WARN] QC validator initialization failed: {e}")
                self.qc_validator = None
            
            # 10. Get expiry dates
            logger.info("Getting expiry dates for indices...")
            if self.sim_mode:
                # SIM MODE: Use simulated expiries (no API calls)
                logger.info("[SIM] Using simulated expiry dates (no API calls)")
                for idx in self.AVAILABLE_INDICES:
                    # Use a standard simulated expiry date
                    self.expiry_map[idx["name"]] = "24FEB2026"  # Simulated expiry
                    logger.info(f"[SIM] Expiry for {idx['name']}: 24FEB2026 (simulated)")
            else:
                # LIVE MODE: Get real expiry dates (may use cached JSON, no API if broker not available)
                self._update_expiry_map()
            
            logger.info("=" * 80)
            logger.info("[OK] INITIALIZATION COMPLETE")
            logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            logger.error(f"[FAIL] Initialization failed: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def _update_expiry_map(self):
        """Update expiry map for all indices."""
        for idx in self.AVAILABLE_INDICES:
            try:
                # Get nearest expiry (weekly preferred) - works without broker
                from src.angel.expiry_selector import ExpirySelector
                selector = ExpirySelector(self.broker)  # Broker optional
                expiry = selector.get_nearest_weekly_expiry(idx["name"], idx["exchange"])
                if expiry:
                    self.expiry_map[idx["name"]] = expiry
                    logger.info(f"Expiry for {idx['name']}: {expiry}")
                else:
                    logger.warning(f"No expiry found for {idx['name']}")
            except Exception as e:
                logger.warning(f"Failed to get expiry for {idx['name']}: {e}")
                # Set a placeholder so system can continue
                self.expiry_map[idx["name"]] = None
    
    def fetch_option_chain_data(self) -> Dict[str, pd.DataFrame]:
        """
        Fetch option chain data for all indices.
        
        Returns:
            Dictionary mapping underlying name to DataFrame
        """
        all_data = {}
        total_indices = len(self.AVAILABLE_INDICES)
        
        print(f"[FETCH] Starting data fetch for {total_indices} indices...", flush=True)
        logger.info(f"Starting data fetch for {total_indices} indices...")
        
        for idx_num, idx in enumerate(self.AVAILABLE_INDICES, 1):
            name = idx["name"]
            exchange = idx["exchange"]
            expiry = self.expiry_map.get(name)
            
            print(f"[{idx_num}/{total_indices}] Fetching {name} ({exchange})...", flush=True)
            logger.info(f"[{idx_num}/{total_indices}] Fetching {name} ({exchange})...")
            
            if not expiry:
                logger.warning(f"No expiry for {name}, skipping")
                print(f"  [SKIP] No expiry for {name}", flush=True)
                continue
            
            try:
                # Try WebSocket first if available and connected
                ws_data_available = False
                if self.config.use_websocket and self.websocket:
                    if not self.websocket.is_connected:
                        # Try to connect WebSocket
                        logger.info(f"Attempting WebSocket connection for {name}...")
                        print(f"  [WS] Connecting WebSocket...", flush=True)
                        if self.websocket.connect():
                            logger.info(f"WebSocket connected for {name}")
                            print(f"  [WS] Connected", flush=True)
                        else:
                            logger.warning(f"WebSocket connection failed for {name}, using REST")
                            print(f"  [WS] Connection failed, using REST", flush=True)
                    
                    # If WebSocket is connected, try to use it
                    if self.websocket.is_connected:
                        ws_data = self._fetch_via_websocket(name, exchange, expiry)
                        if ws_data is not None:
                            df = pd.DataFrame(ws_data)
                            # Add calculated columns
                            print(f"  [ENRICH] Adding calculated columns for {name}...", flush=True)
                            df = self._enrich_option_chain(df, name)
                            all_data[name] = df
                            logger.info(f"[OK] Fetched {len(df)} options for {name} via WebSocket")
                            print(f"  [OK] Fetched {len(df)} options for {name} via WebSocket", flush=True)
                            ws_data_available = True
                        else:
                            logger.warning(f"WebSocket data fetch failed for {name}, falling back to REST")
                            print(f"  [WS] Data fetch failed, using REST", flush=True)
                
                # Use REST fallback if WebSocket didn't work
                if not ws_data_available and self.rest_fallback:
                    # Reduce max_strikes to avoid too many API calls and rate limits
                    # 30 strikes = 60 contracts (CE+PE) = reasonable amount
                    option_chain = self.rest_fallback.fetch_option_chain_batch(
                        underlying_name=name,
                        exchange=exchange,
                        expiry_date=expiry,
                        max_strikes=30  # Reduced from 50 to avoid rate limits
                    )
                    
                    if option_chain and len(option_chain) > 0:
                        df = pd.DataFrame(option_chain)
                        
                        # Add calculated columns
                        print(f"  [ENRICH] Adding calculated columns for {name}...", flush=True)
                        df = self._enrich_option_chain(df, name)
                        
                        all_data[name] = df
                        logger.info(f"[OK] Fetched {len(df)} options for {name}")
                        print(f"  [OK] Fetched {len(df)} options for {name}", flush=True)
                    else:
                        logger.warning(f"No data returned for {name}")
                        print(f"  [WARN] No data returned for {name}", flush=True)
                        all_data[name] = pd.DataFrame()
                else:
                    logger.error("No data fetcher available")
                    all_data[name] = pd.DataFrame()
                    
            except Exception as e:
                logger.error(f"Failed to fetch data for {name}: {e}")
                logger.error(traceback.format_exc())
                all_data[name] = pd.DataFrame()
        
        return all_data
    
    def _fetch_via_websocket(self, underlying_name: str, exchange: str, expiry: str) -> Optional[List[Dict]]:
        """
        Fetch option chain data via WebSocket.
        
        Strategy:
        1. Get initial option chain structure from REST (to know tokens)
        2. Subscribe to those tokens via WebSocket
        3. Wait for WebSocket updates (with timeout)
        4. Merge WebSocket updates into chain data
        5. Return enriched option chain
        
        Args:
            underlying_name: Underlying name (e.g., 'NIFTY')
            exchange: Exchange code ('NFO' or 'BFO')
            expiry: Expiry date string
            
        Returns:
            List of option dicts or None on error
        """
        try:
            # Step 1: Get initial option chain structure from REST
            if not self.rest_fallback:
                logger.warning("REST fallback not available for WebSocket initial structure")
                return None
            
            print(f"  [WS] Getting initial structure from REST...", flush=True)
            initial_chain = self.rest_fallback.fetch_option_chain_batch(
                underlying_name=underlying_name,
                exchange=exchange,
                expiry_date=expiry,
                max_strikes=30
            )
            
            if not initial_chain or len(initial_chain) == 0:
                logger.warning(f"No initial chain data for {underlying_name}")
                return None
            
            # Step 2: Extract tokens and organize by exchange
            tokens_by_exchange = {}
            token_to_option_map = {}  # token -> option dict
            
            for opt in initial_chain:
                token = str(opt.get('token', ''))
                if token and token not in token_to_option_map:
                    token_to_option_map[token] = opt
                    if exchange not in tokens_by_exchange:
                        tokens_by_exchange[exchange] = []
                    tokens_by_exchange[exchange].append(token)
            
            if not tokens_by_exchange:
                logger.warning(f"No tokens found for {underlying_name}")
                return None
            
            total_tokens = sum(len(tokens) for tokens in tokens_by_exchange.values())
            print(f"  [WS] Subscribing to {total_tokens} tokens...", flush=True)
            
            # Step 3: Set up WebSocket data callback
            ws_updates = {}  # token -> latest data
            
            def ws_data_callback(data: Dict):
                """Callback for WebSocket data updates."""
                token = str(data.get('token', ''))
                if token:
                    ws_updates[token] = data
            
            # Step 4: Subscribe to tokens
            if not self.websocket.subscribe(tokens_by_exchange, callback=ws_data_callback):
                logger.warning(f"WebSocket subscription failed for {underlying_name}")
                return None
            
            # Step 5: Wait for WebSocket updates (with timeout)
            print(f"  [WS] Waiting for updates (max 3 seconds)...", flush=True)
            wait_time = 0
            max_wait = 3.0  # Maximum wait time in seconds
            check_interval = 0.1  # Check every 100ms
            
            while wait_time < max_wait:
                time.sleep(check_interval)
                wait_time += check_interval
                
                # Check if we have updates for all tokens (or enough updates)
                if len(ws_updates) >= min(total_tokens, len(ws_updates) + 10):
                    # Got enough updates, proceed
                    break
            
            updates_received = len(ws_updates)
            print(f"  [WS] Received {updates_received}/{total_tokens} updates", flush=True)
            
            # Step 6: Merge WebSocket updates into initial chain
            enriched_chain = []
            for opt in initial_chain:
                token = str(opt.get('token', ''))
                enriched_opt = opt.copy()
                
                # Merge WebSocket updates if available
                if token in ws_updates:
                    ws_data = ws_updates[token]
                    
                    # Update price fields from WebSocket
                    if ws_data.get('ltp') is not None:
                        enriched_opt['ltp'] = ws_data['ltp']
                    if ws_data.get('open') is not None:
                        enriched_opt['open'] = ws_data['open']
                    if ws_data.get('high') is not None:
                        enriched_opt['high'] = ws_data['high']
                    if ws_data.get('low') is not None:
                        enriched_opt['low'] = ws_data['low']
                    if ws_data.get('close') is not None:
                        enriched_opt['close'] = ws_data['close']
                    if ws_data.get('volume') is not None:
                        enriched_opt['volume'] = ws_data['volume']
                    if ws_data.get('oi') is not None:
                        enriched_opt['oi'] = ws_data['oi']
                    if ws_data.get('bidPrice') is not None:
                        enriched_opt['bidPrice'] = ws_data['bidPrice']
                    if ws_data.get('bidQty') is not None:
                        enriched_opt['bidQty'] = ws_data['bidQty']
                    if ws_data.get('offerPrice') is not None:
                        enriched_opt['offerPrice'] = ws_data['offerPrice']
                    if ws_data.get('offerQty') is not None:
                        enriched_opt['offerQty'] = ws_data['offerQty']
                
                enriched_chain.append(enriched_opt)
            
            logger.info(f"WebSocket fetch complete for {underlying_name}: {updates_received}/{total_tokens} tokens updated")
            return enriched_chain
            
        except Exception as e:
            logger.error(f"WebSocket fetch failed for {underlying_name}: {e}", exc_info=True)
            return None
    
    def _enrich_option_chain(self, df: pd.DataFrame, underlying: str) -> pd.DataFrame:
        """
        Enrich option chain with calculated metrics.
        
        Args:
            df: Raw option chain DataFrame
            underlying: Underlying name
            
        Returns:
            Enriched DataFrame
        """
        if df.empty:
            return df
        
        try:
            # Add Greeks if not present
            if 'delta' not in df.columns:
                from core.engine.greeks_engine.greeks_calculator import compute_greeks_for_df
                df = compute_greeks_for_df(df)
            
            # Add calculated metrics
            if 'spot_price' in df.columns and 'strike' in df.columns:
                df['atm_distance'] = abs(df['spot_price'] - df['strike'])
                df['atm_distance_pct'] = (df['atm_distance'] / df['spot_price']) * 100
                df['moneyness'] = df['strike'] / df['spot_price']
            
            # Add bid-ask spread
            if 'bidPrice' in df.columns and 'offerPrice' in df.columns:
                df['bid_ask_spread'] = df['offerPrice'] - df['bidPrice']
                if 'ltp' in df.columns:
                    df['bid_ask_spread_pct'] = (df['bid_ask_spread'] / df['ltp']) * 100
            
            # Add liquidity score
            if 'volume' in df.columns and 'oi' in df.columns:
                # Convert to numeric first to avoid FutureWarning
                volume_numeric = pd.to_numeric(df['volume'], errors='coerce').fillna(0)
                oi_numeric = pd.to_numeric(df['oi'], errors='coerce').fillna(0)
                df['liquidity_score'] = (volume_numeric * 0.4 + oi_numeric * 0.6)
            
            # Add timestamp
            df['fetch_timestamp'] = datetime.now(self.tz).isoformat()
            df['underlying'] = underlying
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to enrich option chain: {e}")
            logger.error(traceback.format_exc())
            return df
    
    def generate_signals(self, chain_data: Dict[str, pd.DataFrame], qc_results: Dict[str, Tuple[bool, List[str]]] = None) -> Tuple[List[Dict], List[str]]:
        """
        Generate trading signals from option chain data.
        
        Args:
            chain_data: Dictionary of option chain DataFrames
            
        Returns:
            Tuple of (signals list, errors list)
        """
        signals = []
        errors = []
        
        if qc_results is None:
            qc_results = {}
        
        for underlying, df in chain_data.items():
            if df.empty:
                errors.append(f"{underlying}: Empty dataframe")
                # Still generate NO_TRADE signal
                no_trade_signal = {
                    'action': 'NO_TRADE',
                    'underlying': underlying,
                    'reason': 'EMPTY_DATA',
                    'reasons': ['EMPTY_DATA'],
                    'confidence': 0.0,
                    'timestamp': datetime.now(self.tz).isoformat()
                }
                signals.append(no_trade_signal)
                continue
            
            # Check QC first - if failed, skip strategy and generate NO_TRADE
            qc_passed = True
            qc_failure_reasons = []
            if underlying in qc_results:
                qc_passed, qc_failure_reasons = qc_results[underlying]
            
            if not qc_passed:
                # QC failed - generate NO_TRADE immediately, skip predictions and strategy
                no_trade_signal = {
                    'action': 'NO_TRADE',
                    'underlying': underlying,
                    'strategy': 'NONE',
                    'reason': 'QC_FAILED',
                    'reasons': ['QC_FAILED'] + qc_failure_reasons[:3],  # Only NO_TRADE reasons
                    'confidence': 0.0,
                    'timestamp': datetime.now(self.tz).isoformat()
                }
                signals.append(no_trade_signal)
                errors.append(f"{underlying}: QC_FAILED - {', '.join(qc_failure_reasons[:3])}")
                continue
            
            try:
                predictions_available = False
                
                # Use ML ensemble for predictions (only if QC passed)
                if self.ensemble_predictor:
                    try:
                        predictions = self.ensemble_predictor.predict_batch(
                            df, underlying, self.sim_scenario
                        )
                        if predictions and predictions.get('predictions'):
                            df['ml_prediction'] = predictions.get('predictions', [])
                            df['ml_confidence'] = predictions.get('confidences', [])
                            predictions_available = True
                            logger.info(f"{underlying}: Predictions generated (model: {predictions.get('model_name', 'unknown')})")
                        else:
                            errors.append(f"{underlying}: Predictions returned empty")
                    except Exception as e:
                        error_msg = f"{underlying}: Prediction failed - {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                
                # If predictions not available, generate NO_TRADE signal
                if not predictions_available:
                    no_trade_signal = {
                        'action': 'NO_TRADE',
                        'underlying': underlying,
                        'strategy': 'NONE',
                        'reason': 'PREDICTION_UNAVAILABLE',
                        'reasons': ['PREDICTION_UNAVAILABLE'],
                        'confidence': 0.0,
                        'timestamp': datetime.now(self.tz).isoformat()
                    }
                    signals.append(no_trade_signal)
                    continue
                
                # Use strategy engine (only if predictions available)
                if self.strategy_engine and predictions_available:
                    try:
                        # StrategyEngine uses decide() method (wrapper)
                        spot = float(df['spot_price'].iloc[0]) if 'spot_price' in df.columns and not df.empty else 0
                        expected_move = float(df['ml_prediction'].abs().mean()) if 'ml_prediction' in df.columns and df['ml_prediction'].notna().any() else spot * 0.02
                        
                        # Calculate sentiment
                        pcr = 1.0  # Default PCR
                        delta_pcr = 1.0  # Default delta PCR
                        if 'oi' in df.columns and 'option_type' in df.columns:
                            pe_oi = df[df['option_type'] == 'PE']['oi'].sum() if len(df[df['option_type'] == 'PE']) > 0 else 1
                            ce_oi = df[df['option_type'] == 'CE']['oi'].sum() if len(df[df['option_type'] == 'CE']) > 0 else 1
                            if ce_oi > 0:
                                pcr = pe_oi / ce_oi
                        
                        sentiment = self.strategy_engine.analyze_sentiment(df, spot, pcr, delta_pcr)
                        
                        # Calculate liquidity score
                        liquidity_score = 50.0  # Default
                        if 'volume' in df.columns and 'oi' in df.columns:
                            avg_volume = df['volume'].mean() if df['volume'].notna().any() else 0
                            avg_oi = df['oi'].mean() if df['oi'].notna().any() else 0
                            liquidity_score = min(100.0, (avg_volume * 0.4 + avg_oi * 0.6) / 100)
                        
                        # Calculate signal strength from predictions
                        signal_strength = 50.0  # Default
                        if 'ml_confidence' in df.columns:
                            signal_strength = float(df['ml_confidence'].mean() * 100) if df['ml_confidence'].notna().any() else 50.0
                        
                        # Get strategy decision using unified decide() method
                        strategy_result = self.strategy_engine.decide(
                            df=df,
                            spot=spot,
                            expected_move=expected_move,
                            sentiment=sentiment,
                            liquidity_score=liquidity_score,
                            signal_strength=signal_strength
                        )
                        
                        # Convert strategy result to signal format
                        if strategy_result.get('action') == 'TRADE':
                            signal = {
                                'action': 'TRADE',
                                'underlying': underlying,
                                'strategy': strategy_result.get('strategy'),
                                'confidence': strategy_result.get('confidence', 0.0),
                                'strikes': strategy_result.get('strikes', []),
                                'tokens': strategy_result.get('tokens', []),
                                'entry_mid': strategy_result.get('entry_mid', 0.0),
                                'stop_loss': strategy_result.get('stop_loss', 0.0),
                                'target': strategy_result.get('target', 0.0),
                                'reason': strategy_result.get('reason', 'Strategy recommendation'),
                                'reasons': strategy_result.get('reasons', []),
                                'timestamp': datetime.now(self.tz).isoformat()
                            }
                            signals.append(signal)
                        else:
                            # NO_TRADE from strategy - normalize to NO_TRADE format
                            strategy_name = strategy_result.get('strategy', 'NONE')
                            no_trade_signal = {
                                'action': 'NO_TRADE',
                                'underlying': underlying,
                                'strategy': 'NONE',
                                'candidate_strategy': strategy_name if strategy_name != 'NONE' else None,
                                'reason': 'NO_STRATEGY_SIGNALS',
                                'reasons': ['NO_STRATEGY_SIGNALS'],  # Only NO_TRADE reasons, not trade rationale
                                'confidence': strategy_result.get('confidence', 0.0),
                                'timestamp': datetime.now(self.tz).isoformat()
                            }
                            signals.append(no_trade_signal)
                            
                    except Exception as e:
                        error_msg = f"{underlying}: Strategy engine failed - {e}"
                        logger.error(error_msg)
                        logger.error(traceback.format_exc())
                        errors.append(error_msg)
                        # Add NO_TRADE on strategy failure
                        no_trade_signal = {
                            'action': 'NO_TRADE',
                            'underlying': underlying,
                            'strategy': 'NONE',
                            'reason': 'STRATEGY_ERROR',
                            'reasons': ['STRATEGY_ERROR'],
                            'confidence': 0.0,
                            'timestamp': datetime.now(self.tz).isoformat()
                        }
                        signals.append(no_trade_signal)
                else:
                    # No strategy engine - create basic signal from predictions
                    if predictions_available and 'ml_prediction' in df.columns:
                        # Create simple signal from predictions
                        avg_pred = df['ml_prediction'].mean() if 'ml_prediction' in df.columns else 0
                        avg_conf = df['ml_confidence'].mean() if 'ml_confidence' in df.columns else 0
                        
                        if avg_conf >= self.config.min_confidence and abs(avg_pred) > 0.01:
                            basic_signal = {
                                'action': 'TRADE',
                                'underlying': underlying,
                                'confidence': float(avg_conf),
                                'predicted_move': float(avg_pred),
                                'timestamp': datetime.now(self.tz).isoformat()
                            }
                            signals.append(basic_signal)
                        else:
                            reason = 'LOW_CONFIDENCE' if avg_conf < self.config.min_confidence else 'NO_PREDICTION'
                            no_trade_signal = {
                                'action': 'NO_TRADE',
                                'underlying': underlying,
                                'strategy': 'NONE',
                                'reason': reason,
                                'reasons': [reason],
                                'confidence': float(avg_conf),
                                'timestamp': datetime.now(self.tz).isoformat()
                            }
                            signals.append(no_trade_signal)
                    else:
                        errors.append(f"{underlying}: Strategy engine not available and no predictions")
                
            except Exception as e:
                error_msg = f"{underlying}: Signal generation failed - {e}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                errors.append(error_msg)
                # Add NO_TRADE on exception
                no_trade_signal = {
                    'action': 'NO_TRADE',
                    'underlying': underlying,
                    'strategy': 'NONE',
                    'reason': 'EXCEPTION',
                    'reasons': ['EXCEPTION'],
                    'confidence': 0.0,
                    'timestamp': datetime.now(self.tz).isoformat()
                }
                signals.append(no_trade_signal)
        
        # Filter by confidence and normalize NO_TRADE signals
        filtered_signals = []
        for s in signals:
            if s.get('action') == 'NO_TRADE':
                # Ensure NO_TRADE signals have correct format
                if 'strategy' not in s or s.get('strategy') != 'NONE':
                    if 'strategy' in s and s.get('strategy'):
                        s['candidate_strategy'] = s.get('strategy')
                    s['strategy'] = 'NONE'
                # Ensure reasons only contain NO_TRADE reasons
                if 'reasons' not in s or not s.get('reasons'):
                    s['reasons'] = [s.get('reason', 'NO_TRADE')]
                filtered_signals.append(s)
            elif s.get('confidence', 0) >= self.config.min_confidence:
                filtered_signals.append(s)
            else:
                # Low confidence - convert to NO_TRADE
                no_trade = s.copy()
                no_trade['action'] = 'NO_TRADE'
                # Move strategy to candidate_strategy, set strategy to NONE
                if 'strategy' in no_trade and no_trade.get('strategy') and no_trade.get('strategy') != 'NONE':
                    no_trade['candidate_strategy'] = no_trade['strategy']
                no_trade['strategy'] = 'NONE'
                no_trade['reason'] = 'LOW_CONFIDENCE'
                # Replace reasons list with only NO_TRADE reasons
                no_trade['reasons'] = ['LOW_CONFIDENCE']
                no_trade['original_confidence'] = s.get('confidence', 0)
                filtered_signals.append(no_trade)
        
        # Sort by confidence (highest first), but NO_TRADE at end
        filtered_signals.sort(key=lambda x: (
            0 if x.get('action') == 'NO_TRADE' else 1,
            -x.get('confidence', 0)
        ))
        
        return filtered_signals, errors
    
    def execute_trades(self, signals: List[Dict]) -> List[Dict]:
        """
        Execute trades based on signals.
        
        Args:
            signals: List of trading signals (should only contain TRADE signals)
            
        Returns:
            List of executed trades
        """
        executed_trades = []
        
        # Filter to only TRADE signals
        trade_signals = [s for s in signals if s.get('action') == 'TRADE']
        
        if not trade_signals:
            logger.info("No TRADE signals to execute")
            return executed_trades
        
        for signal in trade_signals:
            # Check max positions BEFORE attempting execution
            if self.status.current_positions >= self.config.max_positions:
                logger.warning(f"Max positions ({self.config.max_positions}) reached, skipping remaining {len(trade_signals) - len(executed_trades)} signals")
                break
            
            # Get underlying data
            underlying = signal.get('underlying')
            if underlying not in self.current_chain_data:
                logger.warning(f"Underlying {underlying} not in current chain data")
                continue
            
            df = self.current_chain_data[underlying]
            
            try:
                # Execute paper trade
                if self.paper_executor:
                    position = self.paper_executor.execute_trade(
                        trade_signal=signal,
                        current_data=df,
                        cycle_timestamp=datetime.now(self.tz).isoformat()
                    )
                    
                    if position:
                        executed_trades.append(position)
                        self.status.trades_executed += 1
                        self.status.current_positions = len(self.paper_executor.positions)
                        logger.info(f"[OK] Trade executed: {position.get('position_id')}")
            
            except Exception as e:
                logger.error(f"Failed to execute trade: {e}")
                logger.error(traceback.format_exc())
        
        return executed_trades
    
    def update_pnl(self):
        """Update PnL tracking."""
        if self.pnl_tracker and self.paper_executor:
            try:
                # Update positions with current prices
                all_data = self.current_chain_data
                closed_positions = self.paper_executor.update_positions(all_data, datetime.now(self.tz).isoformat())
                
                # Get positions summary from paper executor
                positions_summary = self.paper_executor.get_positions_summary()
                
                # Update PnL tracker
                pnl_data = self.pnl_tracker.update(positions_summary, datetime.now(self.tz).isoformat())
                if pnl_data:
                    # Sync total_pnl from PnL tracker (includes unrealized)
                    self.status.total_pnl = pnl_data.get('total_pnl', 0.0)
                    # Daily PnL is only realized PnL
                    self.status.daily_pnl = pnl_data.get('total_realized_pnl', 0.0)
                    # Also update from PnL summary file if available
                    pnl_summary_file = self.config.output_dir / "paper_pnl_summary.json"
                    if pnl_summary_file.exists():
                        try:
                            pnl_summary = json.loads(pnl_summary_file.read_text())
                            self.status.total_pnl = pnl_summary.get('total_pnl', self.status.total_pnl)
                        except:
                            pass
                
                # Save positions to JSON for dashboard
                try:
                    positions_file = self.config.output_dir / "positions_live.json"
                    positions = list(self.paper_executor.positions.values())
                    positions_data = {
                        "positions": positions,
                        "open_count": len(positions),
                        "closed_count": len(closed_positions),
                        "timestamp": datetime.now(self.tz).isoformat()
                    }
                    with open(positions_file, 'w') as f:
                        json.dump(positions_data, f, indent=2, default=str)
                except Exception as e:
                    logger.debug(f"Failed to save positions: {e}")
            except Exception as e:
                logger.error(f"Failed to update PnL: {e}")
    
    def generate_market_closed_outputs(self, reason: str):
        """
        Generate output files when market is closed (heartbeat mode).
        
        Args:
            reason: Reason why market is closed
        """
        now = datetime.now(self.tz)
        timestamp = now.isoformat()
        
        try:
            # 1. qc_report_live.json
            qc_report = {
                "status": "MARKET_CLOSED",
                "mode": "MARKET_CLOSED",
                "timestamp": timestamp,
                "reason": reason,
                "cycle_count": self.status.total_cycles,
                "last_data_fetch": self.status.last_data_fetch.isoformat() if self.status.last_data_fetch else None
            }
            qc_file = self.config.output_dir / "qc_report_live.json"
            with open(qc_file, 'w') as f:
                json.dump(qc_report, f, indent=2, default=str)
            
            # 2. top_trade_signal.json
            signal = {
                "action": "NO_TRADE",
                "mode": "MARKET_CLOSED",
                "reason": "MARKET_CLOSED",
                "timestamp": timestamp,
                "confidence": 0.0
            }
            signal_file = self.config.output_dir / "top_trade_signal.json"
            with open(signal_file, 'w') as f:
                json.dump(signal, f, indent=2, default=str)
            
            # 3. underlying_rank_live.csv
            rank_data = []
            for idx in self.AVAILABLE_INDICES:
                rank_data.append({
                    "underlying": idx["name"],
                    "exchange": idx["exchange"],
                    "status": "MARKET_CLOSED",
                    "rank": 0,
                    "timestamp": timestamp
                })
            rank_df = pd.DataFrame(rank_data)
            rank_file = self.config.output_dir / "underlying_rank_live.csv"
            rank_df.to_csv(rank_file, index=False)
            
            # 4. Preserve chain_raw_live.csv - do NOT overwrite with status row.
            # Dashboard uses it as cached data when market closed (data_source=cached).

            # Update status (for health.json)
            self.status.last_data_fetch = now
            
            logger.debug(f"Market-closed outputs generated: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to generate market-closed outputs: {e}")
    
    def generate_simulation_data(self, scenario: str, seed: Optional[int] = None) -> Dict[str, pd.DataFrame]:
        """
        Generate simulated option chain data for testing.
        
        Args:
            scenario: Simulation scenario (TREND_UP, TREND_DOWN, RANGE, HIGH_VOL, LOW_LIQUIDITY, DATA_ERRORS)
            seed: Random seed for deterministic generation (default: None for non-deterministic)
        
        Returns:
            Dictionary of simulated option chain DataFrames
        """
        import random
        import numpy as np
        
        # Set seed for deterministic simulation
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        all_data = {}
        base_prices = {
            "NIFTY": 19500,
            "BANKNIFTY": 45000,
            "FINNIFTY": 21000,
            "MIDCPNIFTY": 12000,
            "SENSEX": 72000
        }
        
        for idx in self.AVAILABLE_INDICES:
            name = idx["name"]
            base_price = base_prices.get(name, 20000)
            
            # DATA_ERRORS: Generate fewer contracts for some underlyings to trigger QC failure
            if scenario == "DATA_ERRORS":
                # Make at least 2 underlyings have too few contracts (< min_contracts=10)
                if name in ["NIFTY", "BANKNIFTY"]:
                    num_strikes = random.randint(3, 8)  # Too few contracts
                else:
                    num_strikes = random.randint(15, 25)  # Normal amount
            elif scenario == "TREND_UP":
                # TREND_UP: Generate QC-compliant data with safe margins
                # >= 80 contracts (safe above min_contracts=50, or 10 in sim_mode)
                # >= 12 strikes near ATM within 5% band (safe above >=10)
                num_strikes = 85  # Will generate 85*2 = 170 contracts (CE + PE for each strike)
            else:
                # Generate strikes around base price (more contracts for QC)
                num_strikes = 51
            
            strikes = []
            # Determine strike step based on underlying
            strike_steps = {
                "NIFTY": 50,
                "BANKNIFTY": 100,
                "FINNIFTY": 50,
                "MIDCPNIFTY": 25,
                "SENSEX": 100
            }
            strike_step = strike_steps.get(name, 50)
            
            # For TREND_UP, ensure we have enough strikes near ATM (within 5% band)
            if scenario == "TREND_UP":
                # Generate strikes symmetrically around base_price
                # Ensure at least 12 strikes within 5% band
                atm_band = base_price * 0.05
                min_strikes_in_band = 12
                # Calculate how many strikes we need on each side
                strikes_per_side = max(min_strikes_in_band // 2, 6)
                # Generate strikes from -strikes_per_side to +strikes_per_side, then extend
                for i in range(-num_strikes//2, num_strikes//2 + 1):
                    strike = base_price + (i * strike_step)
                    strikes.append(strike)
            else:
                # Normal generation
                for i in range(-num_strikes//2, num_strikes//2 + 1):
                    strike = base_price + (i * strike_step)
                    strikes.append(strike)
            
            rows = []
            used_tokens = set()  # Track tokens to detect duplicates
            
            for strike in strikes:
                # Apply scenario-based price movement
                if scenario == "TREND_UP":
                    price_mult = 1.0 + (random.random() * 0.02)  # +0-2%
                elif scenario == "TREND_DOWN":
                    price_mult = 1.0 - (random.random() * 0.02)  # -0-2%
                elif scenario == "RANGE":
                    price_mult = 1.0 + (random.random() - 0.5) * 0.01  # ±0.5%
                else:
                    price_mult = 1.0
                
                ltp = abs(base_price - strike) * 0.1 * price_mult
                ltp = max(1.0, ltp)
                
                # Scenario-specific adjustments
                if scenario == "HIGH_VOL":
                    ltp *= (1.0 + random.random() * 0.5)
                elif scenario == "LOW_LIQUIDITY":
                    ltp *= (1.0 - random.random() * 0.3)
                
                # Generate token (simulated)
                token_base = f"{name}{strike}"
                symbol_base = f"{name}{strike}"
                
                # Initialize default values
                oi_val = random.randint(1000, 100000)
                iv_val = random.uniform(0.15, 0.30)
                
                # For TREND_UP: Generate BOTH CE and PE for each strike (ensures completeness)
                # For other scenarios: Generate one option type per strike
                if scenario == "TREND_UP":
                    # Generate both CE and PE for this strike
                    option_types_for_strike = ["CE", "PE"]
                else:
                    # Normal: one option type per strike
                    option_types_for_strike = ["CE" if strike >= base_price else "PE"]
                
                # Generate rows for each option type
                for opt_type in option_types_for_strike:
                    token = f"{token_base}{opt_type}{int(time.time() * 1000) % 1000000 + random.randint(0, 999)}"
                    symbol = f"{symbol_base}{opt_type}"
                
                    # DATA_ERRORS: Inject various errors
                    if scenario == "DATA_ERRORS":
                        error_type = random.random()
                        if error_type < 0.15:  # 15% chance: NaN in ltp
                            ltp = float('nan')
                        elif error_type < 0.25:  # 10% chance: NaN in strike
                            strike = float('nan')
                        elif error_type < 0.35:  # 10% chance: NaN in oi
                            oi_val = float('nan')
                        elif error_type < 0.45:  # 10% chance: NaN in iv
                            iv_val = float('nan')
                        elif error_type < 0.50:  # 5% chance: Duplicate token
                            if used_tokens:
                                token = random.choice(list(used_tokens))
                            else:
                                used_tokens.add(token)
                        elif error_type < 0.55:  # 5% chance: Invalid option_type
                            opt_type = random.choice(["XX", "INVALID", ""])
                        else:
                            # Normal row (keep defaults)
                            used_tokens.add(token)
                    elif scenario == "TREND_UP":
                        # TREND_UP: Ensure high quality data (no NaNs, valid option types)
                        # Ensure completeness >= 0.95
                        # Only allow valid option types
                        if opt_type not in ["CE", "PE"]:
                            opt_type = "CE"  # Fallback to valid type
                        # Ensure all numeric fields are valid
                        if pd.isna(ltp) or ltp <= 0:
                            ltp = abs(base_price - strike) * 0.1 * price_mult
                            ltp = max(1.0, ltp)
                        if pd.isna(oi_val) or oi_val <= 0:
                            oi_val = random.randint(1000, 100000)
                        if pd.isna(iv_val) or iv_val <= 0:
                            iv_val = random.uniform(0.15, 0.30)
                        used_tokens.add(token)
                    else:
                        # Normal scenario (keep defaults)
                        used_tokens.add(token)
                    
                    row = {
                        "underlying": name,
                        "strike": strike if not pd.isna(strike) else None,
                        "spot_price": base_price,
                        "ltp": ltp if not pd.isna(ltp) else None,
                        "bidPrice": ltp * 0.99 if ltp and not pd.isna(ltp) else None,
                        "offerPrice": ltp * 1.01 if ltp and not pd.isna(ltp) else None,
                        "mid_price": ltp if ltp and not pd.isna(ltp) else None,
                        "volume": random.randint(100, 10000) if scenario != "LOW_LIQUIDITY" else random.randint(1, 100),
                        "oi": oi_val if not pd.isna(oi_val) else None,
                        "option_type": opt_type,
                        "expiry": self.expiry_map.get(name, "08FEB2026"),
                        "delta": random.uniform(0.1, 0.9),
                        "gamma": random.uniform(0.01, 0.05),
                        "iv": iv_val if not pd.isna(iv_val) else None,
                        "token": token,
                        "symbol": symbol,
                        "fetch_timestamp": datetime.now(self.tz).isoformat()
                    }
                    
                    # DATA_ERRORS: Some rows missing required columns (drop some columns randomly)
                    if scenario == "DATA_ERRORS" and random.random() < 0.1:  # 10% chance
                        # Remove a critical column randomly
                        col_to_remove = random.choice(["strike", "ltp", "oi", "iv"])
                        if col_to_remove in row:
                            del row[col_to_remove]
                    
                    rows.append(row)
            
            df = pd.DataFrame(rows)
            
            # DATA_ERRORS: Ensure some DataFrames have issues
            if scenario == "DATA_ERRORS" and name in ["NIFTY", "BANKNIFTY"]:
                # These should fail QC due to insufficient contracts
                pass  # Already handled above with num_strikes
            
            all_data[name] = df
        
        return all_data
    
    def run_cycle(self, market_closed: bool = False, market_reason: str = "") -> Dict[str, Any]:
        """
        Run one complete cycle: fetch -> analyze -> signal -> execute.
        
        Args:
            market_closed: If True, market is closed (heartbeat mode)
            market_reason: Reason why market is closed
        
        Returns:
            Cycle results dictionary
        """
        cycle_start = datetime.now(self.tz)
        cycle_results = {
            'cycle_start': cycle_start.isoformat(),
            'success': False,
            'data_fetched': False,
            'signals_generated': 0,
            'trades_executed': 0,
            'mode': 'SIMULATION' if self.sim_mode else ('MARKET_CLOSED' if market_closed else 'LIVE'),
            'errors': [],
            'performance_metrics': {}
        }
        
        try:
            # Handle market-closed mode
            if market_closed and not self.sim_mode:
                logger.info(f"Market closed cycle: {market_reason}")
                self.generate_market_closed_outputs(market_reason)
                cycle_results['data_fetched'] = True  # Heartbeat counts as data fetch
                cycle_results['success'] = True
                self.status.successful_fetches += 1
                self.status.last_data_fetch = cycle_start
                cycle_results['cycle_end'] = datetime.now(self.tz).isoformat()
                self.status.total_cycles += 1
                return cycle_results
            
            # 1. Fetch data (simulation or live)
            if self.sim_mode:
                logger.info(f"SIM MODE: Generating simulation data (scenario: {self.sim_scenario}, seed={self.sim_seed})...")
                chain_data = self.generate_simulation_data(self.sim_scenario or "RANGE", seed=self.sim_seed)
            else:
                logger.info("Fetching option chain data...")
                chain_data = self.fetch_option_chain_data()
            
            self.current_chain_data = chain_data
            
            if not chain_data or all(df.empty for df in chain_data.values()):
                cycle_results['errors'].append("No data fetched")
                # Still generate outputs even if no data
                if market_closed:
                    self.generate_market_closed_outputs(market_reason)
                else:
                    # Generate NO_TRADE outputs when no data fetched (broker not available, etc.)
                    no_trade_signal = {
                        "action": "NO_TRADE",
                        "mode": "LIVE",
                        "reason": "NO_DATA_FETCHED",
                        "reasons": ["NO_DATA_FETCHED"],
                        "confidence": 0.0,
                        "timestamp": cycle_start.isoformat(),
                        "symbol": "N/A"
                    }
                    self._save_top_signal(no_trade_signal)
                    
                    # Generate QC report
                    qc_report = {
                        "status": "NO_DATA",
                        "mode": "LIVE",
                        "timestamp": cycle_start.isoformat(),
                        "qc_passed": False,
                        "reason": "No data fetched - broker not available or connection failed",
                        "cycle": self.status.total_cycles + 1
                    }
                    qc_file = self.config.output_dir / "qc_report_live.json"
                    with open(qc_file, 'w') as f:
                        json.dump(qc_report, f, indent=2, default=str)
                    
                    # Generate empty chain CSV with status
                    chain_data = {
                        "status": "NO_DATA",
                        "mode": "LIVE",
                        "timestamp": cycle_start.isoformat(),
                        "reason": "No data fetched - broker not available or connection failed",
                        "cycle": self.status.total_cycles + 1
                    }
                    chain_df = pd.DataFrame([chain_data])
                    chain_file = self.config.output_dir / "chain_raw_live.csv"
                    chain_df.to_csv(chain_file, index=False)
                    
                    # Generate underlying ranking CSV
                    rank_data = []
                    for idx in self.AVAILABLE_INDICES:
                        rank_data.append({
                            "underlying": idx["name"],
                            "exchange": idx["exchange"],
                            "status": "NO_DATA",
                            "rank": 0,
                            "timestamp": cycle_start.isoformat()
                        })
                    rank_df = pd.DataFrame(rank_data)
                    rank_file = self.config.output_dir / "underlying_rank_live.csv"
                    rank_df.to_csv(rank_file, index=False)
                    
                    # Update health metrics
                    self._update_health_metrics(cycle_start, False)
                
                cycle_results['cycle_end'] = datetime.now(self.tz).isoformat()
                self.status.total_cycles += 1
                return cycle_results
            
            cycle_results['data_fetched'] = True
            self.status.successful_fetches += 1
            self.status.last_data_fetch = cycle_start
            
            # Performance: Track fetch duration
            fetch_end = datetime.now(self.tz)
            fetch_duration = (fetch_end - cycle_start).total_seconds()
            cycle_results['performance_metrics']['fetch_duration_sec'] = fetch_duration
            
            # Save chain data to CSV
            self._save_chain_data(chain_data)
            
            # 2. QC Validation (BEFORE signal generation)
            qc_results = {}  # {underlying: (passed, failures)}
            qc_passed_all = True
            qc_failures = []
            qc_passed_count = 0
            qc_total_count = 0
            qc_pass_rate = 0.0
            
            if self.qc_validator:
                logger.info("Running QC validation...")
                for underlying, df in chain_data.items():
                    if not df.empty:
                        qc_total_count += 1
                        try:
                            passed, reasons = self.qc_validator.validate_snapshot(df, underlying)
                            qc_results[underlying] = (passed, reasons)
                            if not passed:
                                qc_passed_all = False
                                qc_failures.extend([f"{underlying}: {r}" for r in reasons])
                                logger.warning(f"QC FAILED for {underlying}: {reasons}")
                            else:
                                qc_passed_count += 1
                                logger.info(f"QC PASSED for {underlying}")
                        except Exception as e:
                            logger.error(f"QC validation error for {underlying}: {e}")
                            qc_passed_all = False
                            qc_failures.append(f"{underlying}: QC_ERROR - {e}")
                            qc_results[underlying] = (False, [f"QC_ERROR: {e}"])
            
            # PAPER_SANITY: Calculate QC pass rate
            qc_pass_rate = (qc_passed_count / qc_total_count * 100) if qc_total_count > 0 else 0.0
            
            # 3. Generate signals (QC gating: skip strategy for QC-failed underlyings)
            logger.info("Generating trading signals...")
            signal_start = datetime.now(self.tz)
            signals, signal_errors = self.generate_signals(chain_data, qc_results)
            signal_end = datetime.now(self.tz)
            signal_duration = (signal_end - signal_start).total_seconds()
            cycle_results['performance_metrics']['strategy_duration_sec'] = signal_duration
            cycle_results['errors'].extend(signal_errors)
            
            # Track QC failures separately
            cycle_results['qc_failures'] = qc_failures
            
            cycle_results['signals_generated'] = len(signals)
            self.status.signals_generated += len(signals)
            self.status.last_signal_generated = cycle_start
            
            # Save top signal (always ensure valid JSON)
            if signals:
                top_signal = signals[0].copy()
            else:
                top_signal = {
                    "action": "NO_TRADE",
                    "mode": "SIMULATION" if self.sim_mode else "LIVE",
                    "reason": "No signals generated",
                    "reasons": ["No signals generated"],
                    "confidence": 0.0,
                    "timestamp": cycle_start.isoformat()
                }
            
            # Ensure required fields
            if 'mode' not in top_signal:
                top_signal['mode'] = "SIMULATION" if self.sim_mode else "LIVE"
            if 'reasons' not in top_signal:
                reason = top_signal.get('reason', 'Unknown')
                top_signal['reasons'] = [reason] if reason else []
            if 'symbol' not in top_signal and 'tokens' in top_signal and top_signal['tokens']:
                top_signal['symbol'] = top_signal['tokens'][0]
            elif 'symbol' not in top_signal:
                top_signal['symbol'] = top_signal.get('underlying', 'UNKNOWN')
            
            self._save_top_signal(top_signal)
            
            # 4. Execute trades (only TRADE signals, not NO_TRADE)
            # LIVE SAFETY LOCK: In LIVE mode, trades are disabled unless explicitly enabled
            if not self.sim_mode and not self.live_trade_enabled:
                # LIVE mode without trade enable flag - force NO_TRADE
                logger.warning("[SAFETY] LIVE mode trade execution disabled (--live-trade-enable not set)")
                trade_signals = []
            else:
                trade_signals = [s for s in signals if s.get('action') == 'TRADE']
            
            # PAPER_SANITY: Force at least 1 trade if QC >= 70% and confidence >= 0.60
            if self.paper_sanity_mode and len(trade_signals) == 0:
                if qc_pass_rate >= 70.0:
                    # Find highest confidence NO_TRADE signal
                    no_trade_signals = [s for s in signals if s.get('action') == 'NO_TRADE']
                    if no_trade_signals:
                        # Sort by confidence descending
                        no_trade_signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
                        best_no_trade = no_trade_signals[0]
                        confidence = best_no_trade.get('confidence', 0)
                        
                        if confidence >= 0.60:
                            # Force convert to TRADE
                            logger.warning(f"[PAPER_SANITY] Forcing trade: QC={qc_pass_rate:.1f}%, confidence={confidence:.2f}")
                            forced_signal = best_no_trade.copy()
                            forced_signal['action'] = 'TRADE'
                            forced_signal['reason'] = 'PAPER_SANITY_FORCED'
                            forced_signal['reasons'] = ['PAPER_SANITY_FORCED']
                            # Ensure required fields for execution
                            if 'tokens' not in forced_signal or not forced_signal.get('tokens'):
                                # Try to get tokens from underlying data
                                underlying = forced_signal.get('underlying')
                                if underlying in chain_data and not chain_data[underlying].empty:
                                    df = chain_data[underlying]
                                    # Get ATM strike
                                    spot = float(df['spot_price'].iloc[0]) if 'spot_price' in df.columns else 0
                                    if spot > 0:
                                        # Find closest strike to ATM
                                        df['strike_dist'] = abs(df['strike'] - spot)
                                        closest = df.nsmallest(1, 'strike_dist')
                                        if not closest.empty:
                                            forced_signal['tokens'] = [str(closest.iloc[0].get('token', ''))]
                                            forced_signal['strikes'] = [float(closest.iloc[0].get('strike', 0))]
                                            forced_signal['entry_mid'] = float(closest.iloc[0].get('mid_price', closest.iloc[0].get('ltp', 0)))
                                            forced_signal['stop_loss'] = forced_signal['entry_mid'] * 0.7
                                            forced_signal['target'] = forced_signal['entry_mid'] * 1.5
                                            forced_signal['strategy'] = forced_signal.get('candidate_strategy', 'BUY_CE')
                                            trade_signals = [forced_signal]
                                            logger.info(f"[PAPER_SANITY] Forced trade created: {underlying} {forced_signal.get('strategy')}")
            
            if trade_signals:
                # Check how many can actually execute (considering max positions)
                eligible_count = len([s for s in trade_signals if self.status.current_positions < self.config.max_positions])
                if eligible_count > 0:
                    logger.info(f"Executing {eligible_count} trades...")
                    executed = self.execute_trades(trade_signals)
                    cycle_results['trades_executed'] = len(executed)
                else:
                    logger.info(f"0 trades eligible (max positions {self.config.max_positions} reached, {len(trade_signals)} signals skipped)")
                    cycle_results['trades_executed'] = 0
            else:
                logger.info("No trade signals to execute (all NO_TRADE)")
                cycle_results['trades_executed'] = 0
            
            # 5. Update PnL (this also updates positions with current prices)
            self.update_pnl()
            
            # Ensure positions are saved even if no trades executed
            if self.paper_executor and len(self.paper_executor.positions) > 0:
                try:
                    positions_file = self.config.output_dir / "positions_live.json"
                    positions = list(self.paper_executor.positions.values())
                    positions_summary = self.paper_executor.get_positions_summary()
                    positions_data = {
                        "positions": positions,
                        "open_count": len(positions),
                        "closed_count": positions_summary.get('closed_count', 0),
                        "timestamp": datetime.now(self.tz).isoformat()
                    }
                    with open(positions_file, 'w') as f:
                        json.dump(positions_data, f, indent=2, default=str)
                except Exception as e:
                    logger.debug(f"Failed to save positions in cycle: {e}")
            
            # 6. Generate QC report
            self._generate_qc_report(chain_data, signals, qc_passed_all, qc_failures)
            
            # 7. Generate underlying ranking
            self._generate_underlying_ranking(chain_data)
            
            # 8. Update health metrics
            self._update_health_metrics(cycle_start, qc_passed_all)
            
            cycle_results['success'] = True
            cycle_results['qc_passed'] = qc_passed_all
            if qc_failures:
                cycle_results['qc_failures'] = qc_failures
            
        except Exception as e:
            error_msg = f"Cycle error: {e}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            cycle_results['errors'].append(error_msg)
            self.status.errors.append(error_msg)
            self.status.failed_fetches += 1
            
            # Still generate outputs on error
            try:
                no_trade_signal = {
                    "action": "NO_TRADE",
                    "mode": "SIMULATION" if self.sim_mode else "LIVE",
                    "reason": f"CYCLE_ERROR: {str(e)[:100]}",
                    "confidence": 0.0,
                    "timestamp": datetime.now(self.tz).isoformat()
                }
                self._save_top_signal(no_trade_signal)
                
                qc_report = {
                    "status": "ERROR",
                    "mode": "SIMULATION" if self.sim_mode else "LIVE",
                    "timestamp": datetime.now(self.tz).isoformat(),
                    "error": error_msg,
                    "cycle": self.status.total_cycles
                }
                qc_file = self.config.output_dir / "qc_report_live.json"
                with open(qc_file, 'w') as f:
                    json.dump(qc_report, f, indent=2, default=str)
            except:
                pass
        
        finally:
            cycle_end = datetime.now(self.tz)
            cycle_results['cycle_end'] = cycle_end.isoformat()
            cycle_duration = (cycle_end - cycle_start).total_seconds()
            cycle_results['performance_metrics']['cycle_duration_sec'] = cycle_duration
            
            # Save performance metrics
            try:
                perf_file = self.config.output_dir / "perf_metrics.json"
                perf_data = {
                    'timestamp': cycle_end.isoformat(),
                    'cycle': self.status.total_cycles + 1,
                    **cycle_results['performance_metrics']
                }
                with open(perf_file, 'w') as f:
                    json.dump(perf_data, f, indent=2, default=str)
                
                # Ingest into SQLite for dashboard
                try:
                    from dashboard.backend.app import ingest_cycle_metrics, log_event
                    ingest_cycle_metrics()
                    log_event("CYCLE_COMPLETED", {
                        "cycle": self.status.total_cycles + 1,
                        "trades_executed": cycle_results.get('trades_executed', 0),
                        "qc_passed": cycle_results.get('qc_passed', False)
                    })
                except ImportError:
                    pass  # Dashboard not installed
                except Exception as e:
                    logger.debug(f"Dashboard ingestion failed: {e}")
            except:
                pass
            
            self.status.total_cycles += 1
            # Always update health metrics
            try:
                self._update_health_metrics(cycle_start, cycle_results.get('qc_passed', False))
            except:
                pass
        
        return cycle_results
    
    def _save_chain_data(self, chain_data: Dict[str, pd.DataFrame]):
        """Save chain data to CSV."""
        try:
            all_rows = []
            for underlying, df in chain_data.items():
                if not df.empty:
                    all_rows.append(df)
            
            if all_rows:
                # Filter out empty DataFrames to avoid FutureWarning
                non_empty_rows = [df for df in all_rows if not df.empty]
                if non_empty_rows:
                    combined_df = pd.concat(non_empty_rows, ignore_index=True)
                else:
                    combined_df = pd.DataFrame()
            else:
                # Create empty DataFrame with timestamp
                combined_df = pd.DataFrame({
                    'timestamp': [datetime.now(self.tz).isoformat()],
                    'status': ['NO_DATA'],
                    'mode': ['SIMULATION' if self.sim_mode else 'LIVE']
                })
            
            chain_file = self.config.output_dir / "chain_raw_live.csv"
            combined_df.to_csv(chain_file, index=False, encoding='utf-8')
            # Update last_known cache for dashboard data_source state machine
            try:
                from dashboard.backend.data_source_state import write_last_known
                write_last_known(self.config.output_dir, datetime.now(self.tz))
            except ImportError:
                try:
                    from data_source_state import write_last_known
                    write_last_known(self.config.output_dir, datetime.now(self.tz))
                except ImportError:
                    pass
        except Exception as e:
            logger.error(f"Failed to save chain data: {e}")
            # Create minimal fallback
            try:
                fallback_df = pd.DataFrame({
                    'timestamp': [datetime.now(self.tz).isoformat()],
                    'status': ['SAVE_ERROR'],
                    'mode': ['SIMULATION' if self.sim_mode else 'LIVE'],
                    'error': [str(e)[:100]]
                })
                chain_file = self.config.output_dir / "chain_raw_live.csv"
                fallback_df.to_csv(chain_file, index=False, encoding='utf-8')
            except:
                pass
    
    def _save_top_signal(self, signal: Dict):
        """Save top trade signal to JSON."""
        try:
            # Ensure timestamp
            if 'timestamp' not in signal:
                signal['timestamp'] = datetime.now(self.tz).isoformat()
            
            # Ensure all required fields
            required_fields = {
                'action': signal.get('action', 'NO_TRADE'),
                'mode': signal.get('mode', 'SIMULATION' if self.sim_mode else 'LIVE'),
                'timestamp': signal.get('timestamp', datetime.now(self.tz).isoformat()),
                'reasons': signal.get('reasons', [signal.get('reason', 'Unknown')]),
                'confidence': signal.get('confidence', 0.0),
                'symbol': signal.get('symbol', signal.get('underlying', 'UNKNOWN'))
            }
            
            # Merge required fields
            for key, value in required_fields.items():
                if key not in signal:
                    signal[key] = value
            
            signal_file = self.config.output_dir / "top_trade_signal.json"
            with open(signal_file, 'w', encoding='utf-8') as f:
                json.dump(signal, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save top signal: {e}")
            # Create minimal fallback
            try:
                fallback = {
                    "action": "NO_TRADE",
                    "mode": "SIMULATION" if self.sim_mode else "LIVE",
                    "reason": "OUTPUT_ERROR",
                    "reasons": [f"OUTPUT_ERROR: {str(e)[:50]}"],
                    "confidence": 0.0,
                    "timestamp": datetime.now(self.tz).isoformat(),
                    "symbol": "UNKNOWN"
                }
                signal_file = self.config.output_dir / "top_trade_signal.json"
                with open(signal_file, 'w', encoding='utf-8') as f:
                    json.dump(fallback, f, indent=2, default=str, ensure_ascii=False)
            except:
                pass
    
    def _generate_qc_report(
        self, 
        chain_data: Dict[str, pd.DataFrame], 
        signals: List[Dict],
        qc_passed: bool = True,
        qc_failures: List[str] = None
    ):
        """Generate QC report."""
        try:
            trade_signals = [s for s in signals if s.get('action') == 'TRADE']
            no_trade_signals = [s for s in signals if s.get('action') == 'NO_TRADE']
            
            qc_report = {
                "status": "PASS" if qc_passed else "FAIL",
                "qc_passed": qc_passed,
                "mode": "SIMULATION" if self.sim_mode else "LIVE",
                "timestamp": datetime.now(self.tz).isoformat(),
                "underlying_count": len(chain_data),
                "total_contracts": sum(len(df) for df in chain_data.values()),
                "signals_generated": len(signals),
                "trade_signals": len(trade_signals),
                "no_trade_signals": len(no_trade_signals),
                "cycle": self.status.total_cycles,
                "last_data_fetch": self.status.last_data_fetch.isoformat() if self.status.last_data_fetch else None
            }
            
            if qc_failures:
                qc_report["qc_failures"] = qc_failures[:10]  # Limit to first 10
            
            if no_trade_signals:
                reasons = {}
                for s in no_trade_signals:
                    reason = s.get('reason', 'UNKNOWN')
                    reasons[reason] = reasons.get(reason, 0) + 1
                qc_report["no_trade_reasons"] = reasons
            
            qc_file = self.config.output_dir / "qc_report_live.json"
            with open(qc_file, 'w', encoding='utf-8') as f:
                json.dump(qc_report, f, indent=2, default=str, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to generate QC report: {e}")
            # Create minimal fallback
            try:
                fallback = {
                    "status": "ERROR",
                    "mode": "SIMULATION" if self.sim_mode else "LIVE",
                    "timestamp": datetime.now(self.tz).isoformat(),
                    "error": str(e)[:100]
                }
                qc_file = self.config.output_dir / "qc_report_live.json"
                with open(qc_file, 'w', encoding='utf-8') as f:
                    json.dump(fallback, f, indent=2, default=str, ensure_ascii=False)
            except:
                pass
    
    def _update_health_metrics(self, cycle_start: datetime, qc_passed: bool):
        """Update health metrics and write health.json."""
        try:
            # Calculate success rate
            total_cycles = max(1, self.status.total_cycles)
            data_success_rate = (self.status.successful_fetches / total_cycles) * 100
            
            # signal_success_rate: percentage of cycles that generated at least one signal
            # Formula: cycles_with_signals / total_cycles * 100
            # We track this via signals_generated > 0 per cycle, but since we don't track per-cycle,
            # we use: min(100.0, (signals_generated / (total_cycles * avg_underlyings)) * 100)
            # For safety, cap at 100.0
            avg_underlyings = len(self.AVAILABLE_INDICES)  # ~5 underlyings
            expected_signals_per_cycle = avg_underlyings
            signal_success_rate = min(100.0, (self.status.signals_generated / max(1, total_cycles * expected_signals_per_cycle)) * 100)
            
            # Sync current_positions from paper_executor if available
            actual_positions = self.status.current_positions
            if self.paper_executor:
                actual_positions = len(self.paper_executor.positions)
                self.status.current_positions = actual_positions
            
            # Also try to read from positions file if executor not available
            if actual_positions == 0:
                positions_file = self.config.output_dir / "positions_live.json"
                if positions_file.exists():
                    try:
                        with open(positions_file, 'r') as f:
                            pos_data = json.load(f)
                            if isinstance(pos_data, dict):
                                actual_positions = pos_data.get('open_count', len(pos_data.get('positions', [])))
                            elif isinstance(pos_data, list):
                                actual_positions = len(pos_data)
                            self.status.current_positions = actual_positions
                    except:
                        pass
            
            # data_source: real when connected and data fetched; not_ready otherwise
            data_source_val = "real" if (self.status.is_connected and self.status.last_data_fetch) else "not_ready"
            health = {
                'timestamp': cycle_start.isoformat(),
                'is_running': self.status.is_running,
                'is_connected': self.status.is_connected,
                'data_source': data_source_val,
                'last_data_fetch': self.status.last_data_fetch.isoformat() if self.status.last_data_fetch else None,
                'total_cycles': self.status.total_cycles,
                'successful_fetches': self.status.successful_fetches,
                'failed_fetches': self.status.failed_fetches,
                'data_success_rate': round(data_success_rate, 2),
                'signal_success_rate': round(signal_success_rate, 2),
                'signals_generated': self.status.signals_generated,
                'trades_executed': self.status.trades_executed,
                'current_positions': actual_positions,  # Use synced value
                'total_pnl': self.status.total_pnl,
                'daily_pnl': self.status.daily_pnl,
                'qc_passed': qc_passed,
                'mode': 'SIMULATION' if self.sim_mode else 'LIVE'
            }
            
            health_file = self.config.output_dir / "health.json"
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(health, f, indent=2, default=str, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Failed to update health metrics: {e}")
            # Create minimal fallback
            try:
                fallback = {
                    "timestamp": datetime.now(self.tz).isoformat(),
                    "total_cycles": self.status.total_cycles,
                    "last_data_fetch": self.status.last_data_fetch.isoformat() if self.status.last_data_fetch else None,
                    "error": str(e)[:100]
                }
                health_file = self.config.output_dir / "health.json"
                with open(health_file, 'w', encoding='utf-8') as f:
                    json.dump(fallback, f, indent=2, default=str, ensure_ascii=False)
            except:
                pass
    
    def _generate_underlying_ranking(self, chain_data: Dict[str, pd.DataFrame]):
        """Generate underlying ranking CSV."""
        try:
            rankings = []
            for idx, (underlying, df) in enumerate(chain_data.items(), 1):
                if not df.empty:
                    avg_volume = df['volume'].mean() if 'volume' in df.columns else 0
                    avg_oi = df['oi'].mean() if 'oi' in df.columns else 0
                    liquidity_score = avg_volume * 0.4 + avg_oi * 0.6
                    
                    rankings.append({
                        "underlying": underlying,
                        "rank": idx,
                        "liquidity_score": liquidity_score,
                        "contracts": len(df),
                        "timestamp": datetime.now(self.tz).isoformat()
                    })
            
            if rankings:
                rank_df = pd.DataFrame(rankings)
                rank_df = rank_df.sort_values('liquidity_score', ascending=False)
                rank_df['rank'] = range(1, len(rank_df) + 1)
                
                rank_file = self.config.output_dir / "underlying_rank_live.csv"
                rank_df.to_csv(rank_file, index=False)
        except Exception as e:
            logger.error(f"Failed to generate underlying ranking: {e}")
    
    def run(self, duration_minutes: Optional[int] = None, max_cycles: Optional[int] = None, 
            sim_mode: bool = False, sim_scenario: Optional[str] = None):
        """
        Run the automation system.
        
        Args:
            duration_minutes: Run for N minutes (None = until stopped)
            max_cycles: Maximum number of cycles (None = unlimited)
            sim_mode: Enable simulation mode
            sim_scenario: Simulation scenario (TREND_UP, TREND_DOWN, RANGE, HIGH_VOL, LOW_LIQUIDITY, DATA_ERRORS)
        """
        if not self.initialize():
            logger.error("Initialization failed, cannot run")
            return
        
        # Set simulation mode
        self.sim_mode = sim_mode or self.config.enable_simulation
        self.sim_scenario = sim_scenario or self.config.sim_scenario or "RANGE"
        
        # SIM MODE RESET: Clear runtime state for fresh simulation
        if self.sim_mode:
            logger.info("SIM MODE: Resetting runtime state for fresh simulation...")
            # Reset counters
            self.status.trades_executed = 0
            self.status.current_positions = 0
            self.status.total_pnl = 0.0
            self.status.daily_pnl = 0.0
            self.status.total_cycles = 0
            self.status.successful_fetches = 0
            self.status.failed_fetches = 0
            self.status.signals_generated = 0
            self.status.errors = []
            
            # Clear in-memory positions
            if self.paper_executor:
                self.paper_executor.positions.clear()
            
            logger.info("[OK] SIM state reset complete")
        
        logger.info("=" * 80)
        logger.info("STARTING OPTION CHAIN AUTOMATION SYSTEM")
        logger.info("=" * 80)
        logger.info(f"Mode: {'SIMULATION' if self.sim_mode else 'LIVE'}")
        if self.sim_mode:
            logger.info(f"Simulation scenario: {self.sim_scenario}")
        logger.info(f"Refresh interval: {self.config.refresh_interval_seconds}s")
        logger.info(f"Max positions: {self.config.max_positions}")
        logger.info(f"Min confidence: {self.config.min_confidence}")
        
        self.status.is_running = True
        self.status.is_connected = True
        
        # Start background threads
        self._start_background_threads()
        
        start_time = datetime.now(self.tz)
        cycle_count = 0
        
        try:
            while not self._stop_event.is_set():
                # Check market hours (skip if simulation mode)
                market_open, reason = is_market_open()
                
                if not market_open and not self.sim_mode:
                    # Market closed - run heartbeat cycle
                    logger.info(f"Market closed: {reason} - Running heartbeat cycle...")
                    cycle_results = self.run_cycle(market_closed=True, market_reason=reason)
                    logger.info(f"Heartbeat cycle complete: {json.dumps(cycle_results, indent=2, default=str)}")
                    cycle_count += 1
                    
                    # Wait for next market check
                    if not self._stop_event.is_set():
                        time.sleep(self.config.market_check_interval)
                    continue
                
                # Check duration limit
                if duration_minutes:
                    elapsed = (datetime.now(self.tz) - start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        logger.info(f"Duration limit ({duration_minutes} min) reached")
                        break
                
                # Check cycle limit
                if max_cycles and cycle_count >= max_cycles:
                    logger.info(f"Cycle limit ({max_cycles}) reached")
                    break
                
                # Run cycle
                logger.info(f"\n{'='*80}")
                logger.info(f"CYCLE #{cycle_count + 1} ({'SIM' if self.sim_mode else 'LIVE'})")
                logger.info(f"{'='*80}\n")
                
                cycle_results = self.run_cycle(market_closed=False)
                
                # Log cycle results
                logger.info(f"Cycle results: {json.dumps(cycle_results, indent=2, default=str)}")
                
                cycle_count += 1
                
                # Wait for next cycle
                if not self._stop_event.is_set():
                    time.sleep(self.config.refresh_interval_seconds)
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}")
            logger.error(traceback.format_exc())
        finally:
            self.shutdown()
    
    def _start_background_threads(self):
        """Start background monitoring threads."""
        # Heartbeat thread
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True
        )
        self._heartbeat_thread.start()
        
        # Health check thread
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self._health_check_thread.start()
    
    def _heartbeat_loop(self):
        """Background heartbeat loop."""
        while not self._stop_event.is_set():
            try:
                self._save_status()
                time.sleep(self.config.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                time.sleep(self.config.heartbeat_interval)
    
    def _health_check_loop(self):
        """Background health check loop."""
        while not self._stop_event.is_set():
            try:
                self._perform_health_check()
                time.sleep(self.config.health_check_interval)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(self.config.health_check_interval)
    
    def _save_status(self):
        """Save system status to file."""
        try:
            status_file = self.config.output_dir / "system_status.json"
            with open(status_file, 'w') as f:
                json.dump(self.status.to_dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save status: {e}")
    
    def _perform_health_check(self):
        """Perform system health check (background thread)."""
        try:
            # Use the same method as cycle health update
            total_cycles = max(1, self.status.total_cycles)
            data_success_rate = (self.status.successful_fetches / total_cycles) * 100
            
            # Use same formula as _update_health_metrics (capped at 100)
            avg_underlyings = len(self.AVAILABLE_INDICES)
            expected_signals_per_cycle = avg_underlyings
            signal_success_rate = min(100.0, (self.status.signals_generated / max(1, total_cycles * expected_signals_per_cycle)) * 100)
            
            health = {
                'timestamp': datetime.now(self.tz).isoformat(),
                'is_running': self.status.is_running,
                'is_connected': self.status.is_connected,
                'last_data_fetch': self.status.last_data_fetch.isoformat() if self.status.last_data_fetch else None,
                'total_cycles': self.status.total_cycles,
                'successful_fetches': self.status.successful_fetches,
                'failed_fetches': self.status.failed_fetches,
                'data_success_rate': round(data_success_rate, 2),
                'signal_success_rate': round(signal_success_rate, 2),
                'signals_generated': self.status.signals_generated,
                'trades_executed': self.status.trades_executed,
                'current_positions': self.status.current_positions,
                'total_pnl': self.status.total_pnl,
                'daily_pnl': self.status.daily_pnl,
                'mode': 'SIMULATION' if self.sim_mode else 'LIVE'
            }
            
            health_file = self.config.output_dir / "health_check.json"
            with open(health_file, 'w') as f:
                json.dump(health, f, indent=2, default=str)
            
            logger.debug(f"Health check updated: cycles={self.status.total_cycles}, last_fetch={health['last_data_fetch']}")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    def shutdown(self):
        """Shutdown the system gracefully."""
        logger.info("=" * 80)
        logger.info("SHUTTING DOWN OPTION CHAIN AUTOMATION SYSTEM")
        logger.info("=" * 80)
        
        self._stop_event.set()
        self.status.is_running = False
        self.status.is_connected = False  # Mark as disconnected on shutdown
        
        # Write final health.json with shutdown state
        try:
            total_cycles = max(1, self.status.total_cycles)
            data_success_rate = (self.status.successful_fetches / total_cycles) * 100
            
            # Use same formula as _update_health_metrics
            avg_underlyings = len(self.AVAILABLE_INDICES)
            expected_signals_per_cycle = avg_underlyings
            signal_success_rate = min(100.0, (self.status.signals_generated / max(1, total_cycles * expected_signals_per_cycle)) * 100)
            
            final_health = {
                'timestamp': datetime.now(self.tz).isoformat(),
                'is_running': False,  # System is shutting down
                'is_connected': False,  # Connections closed
                'last_data_fetch': self.status.last_data_fetch.isoformat() if self.status.last_data_fetch else None,
                'total_cycles': self.status.total_cycles,
                'successful_fetches': self.status.successful_fetches,
                'failed_fetches': self.status.failed_fetches,
                'data_success_rate': round(data_success_rate, 2),
                'signal_success_rate': round(signal_success_rate, 2),
                'signals_generated': self.status.signals_generated,
                'trades_executed': self.status.trades_executed,
                'current_positions': self.status.current_positions,
                'total_pnl': self.status.total_pnl,
                'daily_pnl': self.status.daily_pnl,
                'mode': 'SIMULATION' if self.sim_mode else 'LIVE',
                'shutdown_time': datetime.now(self.tz).isoformat()
            }
            
            health_file = self.config.output_dir / "health.json"
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(final_health, f, indent=2, default=str, ensure_ascii=False)
            
            logger.info(f"Final health.json written: is_running=False, trades_executed={self.status.trades_executed}, current_positions={self.status.current_positions}")
        except Exception as e:
            logger.error(f"Failed to write final health.json: {e}")
        
        # Save final status
        self._save_status()
        
        # Close connections
        if self.websocket:
            try:
                self.websocket.disconnect()
            except:
                pass
        
        logger.info("[OK] Shutdown complete")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Option Chain Automation System")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--duration", type=int, help="Run duration in minutes")
    parser.add_argument("--cycles", type=int, help="Maximum number of cycles")
    parser.add_argument("--refresh", type=int, default=5, help="Refresh interval in seconds")
    parser.add_argument("--sim", action="store_true", help="Enable simulation mode")
    parser.add_argument("--scenario", type=str, help="Simulation scenario (TREND_UP, TREND_DOWN, RANGE, HIGH_VOL, LOW_LIQUIDITY, DATA_ERRORS)")
    parser.add_argument("--market-check", type=int, help="Market check interval in seconds when closed (default: 30)")
    parser.add_argument("--live-trade-enable", action="store_true", help="Enable trade execution in LIVE mode (default: False, trades disabled for safety)")
    parser.add_argument("--seed", type=int, help="Random seed for deterministic simulation (default: None)")
    parser.add_argument("--paper-sanity", action="store_true", help="Enable PAPER_SANITY mode - force trades for system verification (default: False)")
    
    args = parser.parse_args()
    
    # Load config
    if args.config:
        config = SystemConfig.from_file(Path(args.config))
    else:
        config = SystemConfig()
    
    if args.refresh:
        config.refresh_interval_seconds = args.refresh
    
    if args.market_check:
        config.market_check_interval = args.market_check
    
    if args.sim:
        config.enable_simulation = True
    
    if args.scenario:
        config.sim_scenario = args.scenario
    
    if args.paper_sanity:
        config.paper_sanity_mode = True
        logger.info("[PAPER_SANITY] Mode enabled - will force trades if QC >= 70% and confidence >= 0.60")
    
    # Create and run system
    system = OptionChainAutomationMaster(config)
    
    # Set LIVE trade enable flag
    if args.live_trade_enable:
        system.live_trade_enabled = True
        logger.warning("[WARNING] LIVE trade execution ENABLED - trades will be executed in LIVE mode")
    else:
        system.live_trade_enabled = False
        if not args.sim:
            logger.info("[SAFETY] LIVE mode: Trade execution disabled (use --live-trade-enable to enable)")
    
    # Set simulation seed for deterministic runs
    sim_seed = getattr(args, 'seed', None)
    if sim_seed is not None and args.sim:
        logger.info(f"[DETERMINISTIC] Using random seed: {sim_seed}")
        system.sim_seed = sim_seed
    
    system.run(
        duration_minutes=args.duration, 
        max_cycles=args.cycles,
        sim_mode=args.sim,
        sim_scenario=args.scenario
    )


if __name__ == "__main__":
    main()
