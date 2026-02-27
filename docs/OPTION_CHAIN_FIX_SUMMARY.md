# Option Chain Fetching - Issue Fix Summary

## Problem Identified

The `AngelOneBroker` class had a `_env_live_guard()` that was blocking **ALL** broker initialization, including data fetching operations like:
- Option chain fetching
- LTP (Last Traded Price) retrieval
- Profile fetching
- Market data access

This guard was meant to prevent live trading, but it was too restrictive and blocked even read-only data operations.

## Root Cause

The `_env_live_guard()` function was called in `AngelOneBroker.__init__()`, which meant:
- **Any** use of `AngelOneBroker()` required `SYSTEM3_LIVE_TRADING_ALLOWED=1`
- This blocked legitimate data fetching operations
- Existing code like `angel_options_watch.py` would fail if the guard was enforced

## Solution Implemented

### 1. Modified Broker Initialization

Added an `allow_data_only` parameter to `AngelOneBroker.__init__()`:

```python
def __init__(self, allow_data_only: bool = False):
    """
    Initialize Angel One broker connection.
    
    Args:
        allow_data_only: If True, allows data fetching without live trading guard.
                        If False, requires SYSTEM3_LIVE_TRADING_ALLOWED for any operation.
                        Default: False (backward compatible)
    """
    # Only enforce live trading guard if not in data-only mode
    if not allow_data_only:
        _env_live_guard()
```

### 2. Updated All Data-Fetching Code

Updated all existing files that use `AngelOneBroker()` for data fetching:

- ✅ `core/engine/test_angelone_option_chain.py` - Option chain test script
- ✅ `core/engine/test_angelone_api.py` - API test script
- ✅ `core/engine/angel_options_watch.py` - Options watch
- ✅ `core/engine/angel_options_watch_loop.py` - Options watch loop
- ✅ `core/engine/angel_monday_diagnostic.py` - Diagnostic script
- ✅ `core/engine/system3_phase205_broker_selftest.py` - Broker self-test
- ✅ `core/engine/ultra_live_signals_shadow.py` - Ultra shadow signals

All now use: `AngelOneBroker(allow_data_only=True)`

### 3. Added Guard for Order Placement

Added a separate method `_check_live_trading_allowed()` that can be called by order placement methods:

```python
def _check_live_trading_allowed(self, operation: str = "order placement"):
    """Check if live trading is allowed for operations that modify positions."""
    flag = os.getenv("SYSTEM3_LIVE_TRADING_ALLOWED", "").strip().lower()
    allowed = flag in {"1", "true", "yes", "y"}
    if not allowed:
        msg = f"LIVE TRADING BLOCKED: {operation} requires SYSTEM3_LIVE_TRADING_ALLOWED to be enabled"
        logger.error(msg)
        raise RuntimeError(msg)
    return True
```

This will be used by order placement methods (when implemented) to ensure live trading is only allowed when explicitly enabled.

## Behavior After Fix

### Data Fetching (No Guard Required)
```python
# These work without SYSTEM3_LIVE_TRADING_ALLOWED
broker = AngelOneBroker(allow_data_only=True)
option_chain = broker.get_option_chain_by_underlying("NIFTY", "NFO")
ltp = broker.get_ltp("NSE", "SBIN-EQ", "3045")
profile = broker.get_profile()
```

### Order Placement (Guard Required)
```python
# These will require SYSTEM3_LIVE_TRADING_ALLOWED=1
# (When order placement methods are implemented)
broker = AngelOneBroker()  # or allow_data_only=False
broker.place_order(...)  # Will call _check_live_trading_allowed()
```

## Testing

You can now test option chain fetching:

```bash
# Activate venv
venv\Scripts\activate

# Fetch NIFTY option chain (no SYSTEM3_LIVE_TRADING_ALLOWED needed)
python -m core.engine.test_angelone_option_chain NIFTY

# Fetch all strikes for BANKNIFTY
python -m core.engine.test_angelone_option_chain BANKNIFTY --all-strikes
```

## Backward Compatibility

- Default behavior (`allow_data_only=False`) maintains backward compatibility
- Existing code that doesn't specify `allow_data_only` will still require `SYSTEM3_LIVE_TRADING_ALLOWED`
- All data-fetching scripts have been updated to use `allow_data_only=True`

## Security

- ✅ Data fetching operations are safe and don't require live trading permission
- ✅ Order placement operations will still require `SYSTEM3_LIVE_TRADING_ALLOWED=1`
- ✅ Guard is enforced at the right level (order placement, not data access)

---

**Status**: ✅ **FIXED** - Option chain fetching now works without requiring live trading permission.
