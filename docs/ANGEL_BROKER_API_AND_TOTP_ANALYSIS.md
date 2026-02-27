# Angel Broker API and TOTP - Comprehensive Analysis Report

**Generated**: 2025-12-05  
**Project**: Genesis System3  
**Analysis Scope**: Complete project folder analysis for Angel Broker API integration and TOTP implementation

---

## Executive Summary

This document provides a comprehensive analysis of all Angel Broker API integration and TOTP (Time-based One-Time Password) implementation found in the Genesis System3 project. The system uses **Angel One SmartAPI** for broker integration with **TOTP-based two-factor authentication** for secure login.

---

## 1. Angel Broker API Integration

### 1.1 Core Broker Implementation

**Location**: `core/brokers/angel_one/broker.py`

**Key Components**:
- **Class**: `AngelOneBroker`
- **Library**: `SmartApi` (from `smartapi-python` package)
- **Main Methods**:
  - `__init__()`: Initializes broker connection with credentials
  - `_login()`: Authenticates with Angel One using TOTP
  - `get_profile()`: Retrieves user profile information
  - `get_ltp()`: Fetches Last Traded Price for symbols

**Authentication Flow**:
```python
1. Load credentials from environment variables
2. Initialize SmartConnect with API key
3. Generate TOTP code using pyotp
4. Call generateSession(client_id, pin/password, totp)
5. Extract auth_token, refresh_token, and feed_token
```

**API Methods Used**:
- `SmartConnect(api_key)` - Initialize connection
- `generateSession(client_id, pin, totp)` - Authenticate and get tokens
- `getfeedToken()` - Get feed token for market data
- `getProfile(refresh_token)` - Get user profile
- `ltpData(exchange, tradingsymbol, symboltoken)` - Get last traded price

**New Methods Added**:
- `get_option_chain()` - Fetch option chain data (direct API method)
- `get_option_chain_by_underlying()` - Fetch complete option chain for an underlying (uses instruments master + LTP)

### 1.2 Order Wrapper (Skeleton)

**Location**: `core/broker/angel_live_order_wrapper.py`

**Status**: Currently a skeleton implementation (DRY_RUN mode)

**Class**: `AngelLiveOrderWrapper`

**Methods**:
- `place_market_order()` - Place market orders (currently DRY_RUN)
- `cancel_order()` - Cancel orders (currently DRY_RUN)
- `get_order_status()` - Get order status (currently DRY_RUN)

**Note**: Real SmartAPI integration is pending. Currently returns DRY_RUN responses.

### 1.3 Instruments Management

**Location**: `core/brokers/angel_one/instruments.py`

**Functions**:
- `load_instruments()` - Loads instrument master from JSON
- `find_by_tradingsymbol()` - Find instrument by exchange and symbol
- `find_options_for_underlying()` - Get all options for an underlying
- `find_index_by_name()` - Find index instrument by name

**Data Source**: `storage/instruments/OpenAPIScripMaster.json`

**Supported Exchanges**:
- NSE (National Stock Exchange)
- NFO (NSE Futures & Options)
- BSE (Bombay Stock Exchange)
- BFO (BSE Futures & Options)

**Supported Underlyings**:
- NIFTY
- BANKNIFTY
- FINNIFTY
- MIDCPNIFTY
- SENSEX

### 1.4 Test Files

**Location**: `core/engine/test_angelone_api.py`

**Purpose**: Tests broker connection, authentication, profile fetch, and LTP retrieval

**Test Flow**:
1. Initialize `AngelOneBroker`
2. Fetch user profile
3. Test LTP retrieval for sample symbol (SBIN-EQ)

**Location**: `core/engine/test_angelone_instruments.py`

**Purpose**: Tests instrument loading and lookup functionality

---

## 2. TOTP (Time-based One-Time Password) Implementation

### 2.1 TOTP Library

**Package**: `pyotp` (listed in `requirements.txt`)

**Usage**: Used in `core/brokers/angel_one/broker.py`

### 2.2 TOTP Implementation Details

**Code Location**: `core/brokers/angel_one/broker.py` (lines 68-71)

**Implementation**:
```python
import pyotp

# Generate TOTP code from secret
totp = pyotp.TOTP(self.totp_secret).now()
```

**How It Works**:
1. TOTP secret is stored in environment variable `ANGELONE_TOTP`
2. `pyotp.TOTP()` creates a TOTP object from the secret
3. `.now()` generates the current 6-digit code (valid for 30 seconds)
4. This code is used along with client_id and pin/password for authentication

### 2.3 TOTP Secret Storage

**Location**: Environment variables (loaded from `config/.env`)

**Variable Name**: `ANGELONE_TOTP`

**Format**: Base32 encoded secret key (typically 16-32 characters)

**Security**: 
- Stored in `.env` file (should be in `.gitignore`)
- Loaded via `python-dotenv` package
- Never hardcoded in source code

### 2.4 TOTP Setup Process

**To Set Up TOTP for Angel One**:

1. **Get TOTP Secret from Angel One**:
   - Log in to Angel One web portal
   - Navigate to API settings
   - Enable API access
   - Generate TOTP secret (QR code or manual entry)
   - Scan QR code with authenticator app (Google Authenticator, Authy, etc.) OR
   - Manually enter the secret key

2. **Store in Environment**:
   - Add to `config/.env` file:
     ```
     ANGELONE_TOTP=YOUR_TOTP_SECRET_HERE
     ```

3. **Verify Setup**:
   - Run test: `python -m core.engine.test_angelone_api`
   - Should successfully authenticate and fetch profile

---

## 3. Credentials Management

### 3.1 Environment Variables

**Location**: `config/.env` (not in repository, should be created locally)

**Required Variables**:
```bash
ANGELONE_API_KEY=<your_api_key>
ANGELONE_CLIENT_ID=<your_client_id>
ANGELONE_PIN=<your_pin>          # OR ANGELONE_PASSWORD
ANGELONE_TOTP=<your_totp_secret>
```

### 3.2 Credential Loader

**Location**: `core/utils/env_loader.py`

**Function**: `get_angelone_credentials()`

**Returns**:
```python
{
    "api_key": str,
    "client_id": str,
    "pin": str,              # or password
    "password": str,         # alternative to pin
    "totp_secret": str
}
```

**Validation**: 
- Checks for missing credentials
- Raises `RuntimeError` if any required field is missing
- Logs errors for debugging

### 3.3 Security Guards

**Location**: `core/brokers/angel_one/broker.py` (lines 16-23)

**Function**: `_env_live_guard()`

**Purpose**: Prevents accidental live trading

**Check**: 
- Reads `SYSTEM3_LIVE_TRADING_ALLOWED` environment variable
- Blocks live trading unless explicitly enabled
- Must be set to `"1"`, `"true"`, `"yes"`, or `"y"` to allow

---

## 4. Configuration Files

### 4.1 Live Trading Config

**Location**: `config/live_trade_config.py`

**Key Settings**:
- `LIVE_TRADING_ENABLED = False` (default: disabled)
- `USE_LIVE_EXECUTION_ENGINE = False` (default: paper trading)
- `MAX_LIVE_TRADES_PER_DAY = 10`
- `MAX_LIVE_TRADES_PER_UNDERLYING = 3`
- `DEFAULT_LOTS_PER_TRADE = 1`
- `LIVE_ALLOWED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]`

**Angel-Specific Settings**:
- `ANGEL_PRODUCT_TYPE = "INTRADAY"`
- `ANGEL_ORDER_VARIETY = "NORMAL"`
- `ANGEL_ALLOWED_ORDER_TYPES = ["MARKET"]`

### 4.2 Live Trade Config JSON

**Location**: `config/live_trade_config.json`

**Settings**:
```json
{
  "LIVE_TRADING_ENABLED": false,
  "USE_ANGELONE_LIVE_EXECUTION": false,
  "MAX_DAILY_LOSS": 5000,
  "MAX_OPEN_POSITIONS": 3,
  "MAX_LOTS_PER_TRADE": 1,
  "AUTO_SQUARE_OFF_TIME": "15:20",
  "SYMBOL_WHITELIST": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"],
  "MIN_SCORE_FOR_TRADE": 0.12
}
```

---

## 5. Dependencies

### 5.1 Required Packages

**File**: `requirements.txt`

**Angel Broker Related**:
- `smartapi-python` - Official Angel One SmartAPI Python SDK
- `pyotp` - TOTP implementation library
- `python-dotenv` - Environment variable management
- `requests` - HTTP requests (used by SmartAPI)

**Other Dependencies**:
- `pandas` - Data manipulation
- `scikit-learn` - Machine learning models
- `torch` - Deep learning (for Phase 249+)
- `psutil` - System monitoring

### 5.2 Installation

```bash
pip install -r requirements.txt
```

---

## 6. Authentication Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Angel One Authentication                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  1. Load Credentials from .env     │
         │     - API Key                      │
         │     - Client ID                    │
         │     - PIN/Password                 │
         │     - TOTP Secret                  │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  2. Initialize SmartConnect        │
         │     SmartConnect(api_key)          │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  3. Generate TOTP Code             │
         │     pyotp.TOTP(secret).now()       │
         │     → 6-digit code (30s valid)    │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  4. Authenticate                   │
         │     generateSession(              │
         │       client_id,                   │
         │       pin/password,               │
         │       totp_code                    │
         │     )                             │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  5. Extract Tokens                │
         │     - auth_token (JWT)             │
         │     - refresh_token               │
         │     - feed_token                  │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │  6. Ready for API Calls           │
         │     - getProfile()                │
         │     - ltpData()                  │
         │     - placeOrder() (future)      │
         └────────────────────────────────────┘
```

---

## 7. File Structure Summary

### 7.1 Core Broker Files

```
core/
├── brokers/
│   └── angel_one/
│       ├── __init__.py
│       ├── broker.py              ← Main broker class with TOTP auth
│       └── instruments.py         ← Instrument lookup utilities
├── broker/
│   └── angel_live_order_wrapper.py  ← Order placement wrapper (skeleton)
└── utils/
    └── env_loader.py              ← Credential loading utility
```

### 7.2 Configuration Files

```
config/
├── .env                           ← Credentials (not in repo)
├── live_trade_config.py          ← Python config
├── live_trade_config.json        ← JSON config
└── system3_broker_config.yml     ← YAML config (if exists)
```

### 7.3 Test Files

```
core/engine/
├── test_angelone_api.py          ← API connection test
└── test_angelone_instruments.py  ← Instrument lookup test
```

### 7.4 Data Files

```
storage/
└── instruments/
    └── OpenAPIScripMaster.json   ← Instrument master data
```

---

## 8. Usage Examples

### 8.1 Basic Broker Connection

```python
from core.brokers.angel_one.broker import AngelOneBroker

# Initialize (automatically authenticates)
broker = AngelOneBroker()

# Get profile
profile = broker.get_profile()

# Get LTP
ltp = broker.get_ltp("NSE", "SBIN-EQ", "3045")
```

### 8.2 Fetch Option Chain

```python
from core.brokers.angel_one.broker import AngelOneBroker

# Initialize broker
broker = AngelOneBroker()

# Fetch option chain for NIFTY (all strikes)
option_chain = broker.get_option_chain_by_underlying(
    underlying_name="NIFTY",
    exchange="NFO",
    include_all_strikes=True
)

# Option chain is a list of dicts with:
# - underlying, exchange, expiry, strike, option_type (CE/PE)
# - symbol, token, ltp, spot_price, moneyness (ATM/ITM/OTM)

# Filter for ATM options
atm_options = [opt for opt in option_chain if opt.get("moneyness") == "ATM"]

# Get CE options only
ce_options = [opt for opt in option_chain if opt.get("option_type") == "CE"]

# Get specific strike
strike_23000 = [opt for opt in option_chain if opt.get("strike") == 23000]
```

### 8.2 TOTP Code Generation (Standalone)

```python
import pyotp

# Your TOTP secret from environment
totp_secret = "YOUR_SECRET_HERE"

# Generate current code
totp = pyotp.TOTP(totp_secret)
current_code = totp.now()  # 6-digit code, valid for 30 seconds

print(f"Current TOTP: {current_code}")
```

### 8.3 Testing Connection

```bash
# Activate virtual environment
venv\Scripts\activate

# Test API connection
python -m core.engine.test_angelone_api

# Test instruments
python -m core.engine.test_angelone_instruments

# Test option chain fetching
python -m core.engine.test_angelone_option_chain NIFTY
python -m core.engine.test_angelone_option_chain BANKNIFTY --all-strikes
python -m core.engine.test_angelone_option_chain FINNIFTY
```

---

## 9. Security Considerations

### 9.1 Credential Security

✅ **Good Practices**:
- Credentials stored in `.env` file (not in source code)
- `.env` file should be in `.gitignore`
- Environment variables loaded via `python-dotenv`
- No hardcoded secrets in code

⚠️ **Recommendations**:
- Use environment-specific `.env` files
- Rotate API keys periodically
- Use secure storage for production (e.g., Azure Key Vault, AWS Secrets Manager)
- Enable 2FA on Angel One account
- Restrict API key permissions to minimum required

### 9.2 TOTP Security

✅ **Current Implementation**:
- TOTP secret stored securely in environment
- Code generated on-demand (not cached)
- 30-second validity window
- No TOTP codes logged or stored

⚠️ **Best Practices**:
- Never share TOTP secret
- Use authenticator app (not SMS)
- Backup TOTP secret securely
- Rotate if compromised

### 9.3 Live Trading Guards

✅ **Safety Mechanisms**:
- `SYSTEM3_LIVE_TRADING_ALLOWED` environment check
- `LIVE_TRADING_ENABLED` config flag (default: False)
- Paper trading mode by default
- Multiple validation layers before execution

---

## 10. API Documentation References

### 10.1 Angel One SmartAPI

**Official Documentation**: 
- SmartAPI Portal: https://smartapi.angelone.in/
- API Documentation: https://smartapi.angelone.in/docs/

**Key Endpoints Used**:
- `generateSession()` - Authentication
- `getProfile()` - User profile
- `ltpData()` - Last traded price
- `getfeedToken()` - Market data feed token

**Future Endpoints** (for order placement):
- `placeOrder()` - Place orders
- `modifyOrder()` - Modify orders
- `cancelOrder()` - Cancel orders
- `getOrderBook()` - Get order book
- `getTradeBook()` - Get trade book

### 10.2 pyotp Library

**Documentation**: https://github.com/pyotp/pyotp

**Key Methods**:
- `pyotp.TOTP(secret)` - Create TOTP object
- `.now()` - Get current code
- `.verify(code)` - Verify code
- `.provisioning_uri()` - Generate QR code URI

---

## 11. Troubleshooting

### 11.1 Common Issues

**Issue**: `Missing AngelOne env values`
- **Solution**: Check `config/.env` file exists and contains all required variables

**Issue**: `Invalid TOTP secret`
- **Solution**: Verify TOTP secret is correct Base32 format, check for typos

**Issue**: `generateSession failed`
- **Solution**: 
  - Verify client_id, pin/password are correct
  - Ensure TOTP code is current (generated within 30 seconds)
  - Check API key is valid and active

**Issue**: `LIVE TRADING BLOCKED BY ENV GUARD`
- **Solution**: Set `SYSTEM3_LIVE_TRADING_ALLOWED=1` in environment (only if you want live trading)

### 11.2 Debug Steps

1. **Verify Credentials**:
   ```python
   from core.utils.env_loader import get_angelone_credentials
   creds = get_angelone_credentials()
   print(creds)  # Check all fields are populated
   ```

2. **Test TOTP Generation**:
   ```python
   import pyotp
   totp = pyotp.TOTP("YOUR_SECRET")
   print(totp.now())  # Should print 6-digit code
   ```

3. **Test Connection**:
   ```bash
   python -m core.engine.test_angelone_api
   ```

---

## 12. Future Enhancements

### 12.1 Planned Features

- [ ] Real order placement implementation (currently skeleton)
- [ ] Order status polling and updates
- [ ] Position management
- [ ] Real-time market data streaming
- [ ] WebSocket integration for live quotes
- [ ] Order modification and cancellation
- [ ] Trade book and order book management
- [ ] Historical data fetching
- [ ] Portfolio management

### 12.2 Integration Points

**Phase 101-130**: Live trading automation phases
- Phase 103: Order wrapper skeleton (done)
- Phase 107: Live execution engine (pending real API)
- Phase 108: Order status refresher (pending)

**Current Status**: Paper trading mode active, live execution infrastructure ready but disabled

---

## 13. Related Documentation

### 13.1 Project Documentation

- `docs/system3_phases_101_130_angelone_full_auto_plan.md` - Full automation plan
- `SYSTEM3_ANGEL_ONE_ROADMAP.md` - Roadmap and status
- `docs/system3_angel_index_options_overview.md` - Index options overview

### 13.2 Configuration Files

- `config/live_trade_config.py` - Live trading configuration
- `config/live_trade_config.json` - JSON configuration
- `config/.env` - Environment variables (create locally)

---

## 14. Summary

### 14.1 Angel Broker API

✅ **Implemented**:
- Broker connection and authentication
- TOTP-based 2FA login
- Profile retrieval
- LTP data fetching
- Instrument lookup and management
- **Option chain data fetching** (NEW)
- Test utilities

⏳ **Pending**:
- Real order placement (skeleton exists)
- Order status management
- Position tracking
- Market data streaming

### 14.2 TOTP Implementation

✅ **Fully Functional**:
- TOTP code generation using `pyotp`
- Secure secret storage in environment
- Integration with Angel One authentication
- 30-second validity window
- On-demand code generation

### 14.3 Security

✅ **In Place**:
- Environment-based credential storage
- Multiple live trading guards
- Paper trading mode by default
- No hardcoded secrets

---

## 15. Quick Reference

### 15.1 Environment Variables

```bash
ANGELONE_API_KEY=<your_api_key>
ANGELONE_CLIENT_ID=<your_client_id>
ANGELONE_PIN=<your_pin>
ANGELONE_TOTP=<your_totp_secret>
SYSTEM3_LIVE_TRADING_ALLOWED=0  # Set to 1 to enable live trading
```

### 15.2 Key Files

- `core/brokers/angel_one/broker.py` - Main broker class
- `core/utils/env_loader.py` - Credential loader
- `config/.env` - Credentials (create locally)
- `requirements.txt` - Dependencies

### 15.3 Test Commands

```bash
# Test API connection
python -m core.engine.test_angelone_api

# Test instruments
python -m core.engine.test_angelone_instruments

# Test option chain fetching
python -m core.engine.test_angelone_option_chain NIFTY
python -m core.engine.test_angelone_option_chain BANKNIFTY --all-strikes
```

---

**End of Analysis Report**

*This report was generated by analyzing the complete Genesis System3 project folder structure and all relevant files related to Angel Broker API and TOTP implementation.*
