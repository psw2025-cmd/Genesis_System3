"""
System3 Live Trading Configuration (Mode 1 - Angel One Only)

This is the CENTRAL configuration file for all live trading operations.
All phases 101-130 MUST check these flags before any real trading operations.

PAPER TRADING MODE:
  - LIVE_TRADING_ENABLED = False (always) → No real capital at risk
  - USE_LIVE_EXECUTION_ENGINE = False (always) → Phase 106 executes, not Phase 107
  - Paper trades run during market hours (9:15-15:30) on market data
  - All signals are simulated with realistic fill prices and slippage
  - Position tracking and P&L calculation work identically to live trading
"""

# ============================================================================
# CRITICAL SAFETY FLAGS
# ============================================================================
# PAPER TRADING MODE (Safe for live market hours)
LIVE_TRADING_ENABLED = False           # MUST remain False - no real capital used
USE_LIVE_EXECUTION_ENGINE = False      # MUST remain False - use Phase 106 (paper) not Phase 107 (live)

# To switch to REAL LIVE TRADING (ONLY after extensive testing):
# Set BOTH flags to True AND update automation config AND ensure safety checks pass

# ============================================================================
# TRADE LIMITS (Paper Trading)
# ============================================================================
# These limits apply to SIMULATED trades during paper trading
# Helps validate if strategy would respect position limits
MAX_LIVE_TRADES_PER_DAY = 10           # Max simulated trades per day
MAX_LIVE_TRADES_PER_UNDERLYING = 3     # Max simulated trades per underlying per day
MAX_RISK_PER_TRADE_RUPEES = 2000       # Max simulated risk per trade (for testing)
DEFAULT_LOTS_PER_TRADE = 1

# ============================================================================
# ALLOWED UNDERLYINGS
# ============================================================================
# Allowed underlyings for live auto trading
LIVE_ALLOWED_UNDERLYINGS = [
    "NIFTY",
    "BANKNIFTY",
    "FINNIFTY",
    "MIDCPNIFTY",
    "SENSEX"
]

# ============================================================================
# ANGEL ONE SPECIFIC SETTINGS
# ============================================================================
ANGEL_PRODUCT_TYPE = "INTRADAY"  # or as per current SmartAPI usage
ANGEL_ORDER_VARIETY = "NORMAL"
ANGEL_ALLOWED_ORDER_TYPES = ["MARKET"]  # For phase 1 live trading

# ============================================================================
# ADDITIONAL RISK CONTROLS
# ============================================================================
MAX_DAILY_DRAWDOWN_RUPEES = 5000  # Maximum daily drawdown limit
USE_LIVE_EXECUTION_ENGINE = False  # Use Phase 107 (LIVE) vs Phase 106 (DRY_RUN)

# ============================================================================
# MARKET TIMINGS (IST)
# ============================================================================
MARKET_OPEN_TIME = "09:15"
MARKET_CLOSE_TIME = "15:30"

