# Option Chain - Comprehensive Column Headers

## ✅ Implementation Complete

The option chain fetching has been enhanced to fetch **ALL possible columns** from Angel One SmartAPI.

---

## 📊 Complete Column List

### Contract Information (from Instrument Master)
| Column | Description | Source | Example |
|--------|-------------|--------|---------|
| `underlying` | Underlying name | Instrument Master | "NIFTY" |
| `exchange` | Exchange code | Instrument Master | "NFO" |
| `tradingSymbol` | Trading symbol | Instrument Master | "NIFTY25DEC2423000CE" |
| `symbol` | Symbol (alias) | Instrument Master | "NIFTY25DEC2423000CE" |
| `name` | Underlying name | Instrument Master | "NIFTY" |
| `token` | Symbol token | Instrument Master | "12345" |
| `expiry` | Expiry date string | Instrument Master | "30DEC2024" |
| `expiry_date` | Parsed expiry date | Instrument Master | "2024-12-30" |
| `strikePrice` | Strike price | Instrument Master | 23000.0 |
| `strike` | Strike (alias) | Instrument Master | 23000.0 |
| `optionType` | CE or PE | Instrument Master | "CE" |
| `option_type` | Option type (alias) | Instrument Master | "CE" |
| `instrumentType` | Instrument type | Instrument Master | "OPTIDX" |
| `lotSize` | Lot size | Instrument Master | 50 |
| `tickSize` | Tick size | Instrument Master | 0.05 |

### Price Data (from Quote API)
| Column | Description | Source | Example |
|--------|-------------|--------|---------|
| `ltp` | Last traded price | Quote API | 125.50 |
| `open` | Open price | Quote API | 120.00 |
| `high` | High price | Quote API | 130.00 |
| `low` | Low price | Quote API | 118.00 |
| `close` | Previous close | Quote API | 122.00 |
| `change` | Price change | Quote API | 3.50 |
| `pChange` | Percentage change | Quote API | 2.87 |

### Volume & Open Interest (from Quote API)
| Column | Description | Source | Example |
|--------|-------------|--------|---------|
| `volume` | Trading volume | Quote API | 125000 |
| `oi` | Open interest | Quote API | 5000000 |

### Bid/Ask Data (from Quote/SnapQuote API)
| Column | Description | Source | Example |
|--------|-------------|--------|---------|
| `bidPrice` | Best bid price | Quote API | 125.00 |
| `bidQty` | Best bid quantity | Quote API | 100 |
| `offerPrice` | Best ask/offer price | Quote API | 126.00 |
| `offerQty` | Best ask quantity | Quote API | 150 |

### Option Greeks (from Greeks API)
| Column | Description | Source | Example |
|--------|-------------|--------|---------|
| `delta` | Price sensitivity to underlying | Greeks API | 0.5234 |
| `gamma` | Delta sensitivity | Greeks API | 0.0123 |
| `theta` | Time decay (per day) | Greeks API | -15.50 |
| `vega` | Volatility sensitivity | Greeks API | 25.30 |
| `rho` | Interest rate sensitivity | Greeks API | 2.10 |
| `iv` | Implied volatility | Greeks API | 0.18 |
| `impliedVolatility` | IV (alias) | Greeks API | 0.18 |
| `pTime` | Premium time | Greeks API | - |
| `pChange` | Premium change | Greeks API | 2.5 |
| `pOI` | Premium OI | Greeks API | - |
| `pVolume` | Premium volume | Greeks API | - |

### Calculated Fields
| Column | Description | Source | Example |
|--------|-------------|--------|---------|
| `spot_price` | Current spot price | Calculated | 23150.25 |
| `moneyness` | ATM/ITM/OTM | Calculated | "ATM" |

---

## 🔄 Data Fetching Flow

```
1. Load Instrument Master
   ↓
   Get all option contracts for underlying
   ↓
2. For each option contract:
   ├─ Fetch LTP (get_ltp)
   ├─ Fetch Full Quote (get_quote) → OHLC, Volume, OI, Bid/Ask
   ├─ Fetch Greeks (get_option_greeks) → Delta, Gamma, Theta, Vega, Rho, IV
   └─ Merge all data
   ↓
3. Return comprehensive option chain
```

---

## 📋 Column Categories Summary

### ✅ Contract Info (13 columns)
- underlying, exchange, tradingSymbol, symbol, name, token
- expiry, expiry_date, strikePrice, strike
- optionType, option_type, instrumentType
- lotSize, tickSize

### ✅ Price Data (7 columns)
- ltp, open, high, low, close, change, pChange

### ✅ Volume & OI (2 columns)
- volume, oi

### ✅ Bid/Ask (4 columns)
- bidPrice, bidQty, offerPrice, offerQty

### ✅ Greeks (10 columns)
- delta, gamma, theta, vega, rho
- iv, impliedVolatility
- pTime, pChange, pOI, pVolume

### ✅ Calculated (2 columns)
- spot_price, moneyness

**Total: 38 columns** (when all APIs are available)

---

## 🎯 API Methods Used

### 1. Instrument Master
- **Source**: `storage/instruments/OpenAPIScripMaster.json`
- **Fields**: All contract details (token, symbol, expiry, strike, lotSize, etc.)

### 2. LTP API
- **Method**: `smart.ltpData(exchange, tradingsymbol, symboltoken)`
- **Fields**: `ltp`

### 3. Quote API
- **Method**: `smart.getQuote()` or `smart.marketData()`
- **Fields**: `open`, `high`, `low`, `close`, `volume`, `oi`, `change`, `pChange`, `bidPrice`, `bidQty`, `offerPrice`, `offerQty`

### 4. Greeks API
- **Method**: `smart.getOptionGreek()` or `smart.optionGreek()`
- **Fields**: `delta`, `gamma`, `theta`, `vega`, `rho`, `iv`, `pTime`, `pChange`, `pOI`, `pVolume`

### 5. Snap Quote API (Optional)
- **Method**: `smart.snapQuote()` or `smart.getSnapQuote()`
- **Fields**: Depth data (if available)

---

## ⚠️ Data Availability Notes

### Market Hours
- **Live data** (LTP, quotes, Greeks): Available during market hours (9:15 AM - 3:30 PM IST)
- **After hours**: May return None or previous day's data

### API Limitations
- Some fields may be `None` if:
  - Market is closed
  - Option has no trading activity
  - API method not available in your SmartAPI version
  - Rate limiting (too many requests)

### Fallback Behavior
- If `getQuote()` fails → Falls back to `get_ltp()`
- If `getOptionGreek()` fails → Greeks set to `None`
- If `snapQuote()` fails → Bid/ask from quote API used

---

## 📝 CSV Output

When saved to CSV, all columns are included:

```csv
underlying,exchange,tradingSymbol,symbol,name,token,expiry,expiry_date,strikePrice,strike,optionType,option_type,instrumentType,lotSize,tickSize,ltp,open,high,low,close,volume,oi,change,pChange,bidPrice,bidQty,offerPrice,offerQty,delta,gamma,theta,vega,rho,iv,impliedVolatility,pTime,pOI,pVolume,spot_price,moneyness
NIFTY,NFO,NIFTY25DEC2423000CE,NIFTY25DEC2423000CE,NIFTY,12345,30DEC2024,2024-12-30,23000,23000,CE,CE,OPTIDX,50,0.05,125.50,120.00,130.00,118.00,122.00,125000,5000000,3.50,2.87,125.00,100,126.00,150,0.5234,0.0123,-15.50,25.30,2.10,0.18,0.18,,,23150.25,ATM
```

---

## 🚀 Usage

```python
from core.brokers.angel_one.broker import AngelOneBroker

broker = AngelOneBroker(allow_data_only=True)

# Fetch comprehensive option chain
option_chain = broker.get_option_chain_by_underlying(
    underlying_name="NIFTY",
    exchange="NFO",
    include_all_strikes=True
)

# Each option contains all 38+ columns
for opt in option_chain:
    print(f"Strike: {opt['strike']}")
    print(f"LTP: {opt['ltp']}")
    print(f"Volume: {opt['volume']}")
    print(f"OI: {opt['oi']}")
    print(f"Delta: {opt['delta']}")
    print(f"IV: {opt['iv']}")
    print(f"Bid: {opt['bidPrice']}, Ask: {opt['offerPrice']}")
    # ... all other columns available
```

---

## ✅ Verification

Run the test script to see all columns:

```bash
python -m core.engine.test_angelone_option_chain NIFTY
```

The output will show:
1. **Basic Option Data** - Strike, Type, LTP, Volume, OI, Moneyness
2. **Option Greeks** - Delta, Gamma, Theta, Vega, IV (if available)
3. **Bid/Ask Data** - Bid/Ask prices and quantities (if available)
4. **Summary Statistics** - Totals and ranges
5. **Data Availability** - Which columns have data

---

## 📊 Column Mapping Reference

### Angel One API Response → Our Column Names

| Angel One Field | Our Column | Notes |
|----------------|------------|-------|
| `ltp` | `ltp` | Last traded price |
| `open` | `open` | Open price |
| `high` | `high` | High price |
| `low` | `low` | Low price |
| `close` | `close` | Previous close |
| `volume` | `volume` | Trading volume |
| `oi` | `oi` | Open interest |
| `change` | `change` | Price change |
| `pChange` | `pChange` | Percentage change |
| `bidPrice` | `bidPrice` | Best bid |
| `bidQty` | `bidQty` | Bid quantity |
| `offerPrice` | `offerPrice` | Best ask |
| `offerQty` | `offerQty` | Ask quantity |
| `delta` | `delta` | Option delta |
| `gamma` | `gamma` | Option gamma |
| `theta` | `theta` | Option theta |
| `vega` | `vega` | Option vega |
| `rho` | `rho` | Option rho |
| `iv` | `iv` | Implied volatility |

---

**Status**: ✅ **COMPLETE** - All possible columns are now fetched and available in the option chain data.
