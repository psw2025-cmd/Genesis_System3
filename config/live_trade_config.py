"""
System3 Live Trading Configuration (Mode 1 - Dhan Only)

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
# DHAN ORDER SETTINGS
# ============================================================================
DHAN_PRODUCT_TYPE = "INTRADAY"
DHAN_ORDER_VARIETY = "NORMAL"
DHAN_ALLOWED_ORDER_TYPES = ["MARKET"]

# Backward-compat aliases (phases 101/107 still use old names — updated below)
ANGEL_PRODUCT_TYPE = DHAN_PRODUCT_TYPE
ANGEL_ORDER_VARIETY = DHAN_ORDER_VARIETY
ANGEL_ALLOWED_ORDER_TYPES = DHAN_ALLOWED_ORDER_TYPES

# ============================================================================
# ADDITIONAL RISK CONTROLS — SINGLE SOURCE OF TRUTH (units explicit)
# ============================================================================
# C3 FIX: all risk ceilings centralized here with EXPLICIT units to avoid the
# prior ambiguity (optimizer's max_daily_loss=10.0 is a PERCENT suggestion,
# NOT an absolute rupee cap — they are different things and must not be confused).
MAX_DAILY_DRAWDOWN_RUPEES = 5000      # HARD STOP: absolute ₹ daily loss → halt trading
MAX_RISK_PER_TRADE_RUPEES = 2000      # HARD CAP: absolute ₹ risk per single trade
MAX_DAILY_LOSS_PCT = 10.0             # SOFT: % of capital/day (optimizer suggestion only)
MAX_PORTFOLIO_HEAT_PCT = 6.0          # SOFT: max % of capital deployed at once

# Enforcement note: the HARD ₹ caps (DRAWDOWN_RUPEES, RISK_PER_TRADE_RUPEES) are
# the authoritative live-trading guards. The _PCT values are advisory only and
# come from the risk optimizer's Kelly analysis — never used as live stop logic.

USE_LIVE_EXECUTION_ENGINE = False  # Use Phase 107 (LIVE) vs Phase 106 (DRY_RUN)

# ============================================================================
# MARKET TIMINGS (IST)
# ============================================================================
MARKET_OPEN_TIME = "09:15"
MARKET_CLOSE_TIME = "15:30"

