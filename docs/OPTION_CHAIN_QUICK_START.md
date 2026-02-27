# Option Chain Fetching - Quick Start Guide

**Status**: ✅ **READY TO USE**

The option chain fetching functionality has been implemented and is ready to use.

---

## Quick Start

### 1. Test with Command Line

```bash
# Activate virtual environment
venv\Scripts\activate

# Fetch NIFTY option chain (ATM strikes only)
python -m core.engine.test_angelone_option_chain NIFTY

# Fetch all strikes for BANKNIFTY
python -m core.engine.test_angelone_option_chain BANKNIFTY --all-strikes

# Other underlyings
python -m core.engine.test_angelone_option_chain FINNIFTY
python -m core.engine.test_angelone_option_chain MIDCPNIFTY
python -m core.engine.test_angelone_option_chain SENSEX
```

### 2. Use in Python Code

```python
from core.brokers.angel_one.broker import AngelOneBroker

# Initialize broker (automatically authenticates with TOTP)
broker = AngelOneBroker()

# Fetch option chain for NIFTY
option_chain = broker.get_option_chain_by_underlying(
    underlying_name="NIFTY",
    exchange="NFO",
    include_all_strikes=True  # Set False for ATM strikes only
)

# Option chain is a list of dictionaries
print(f"Fetched {len(option_chain)} options")

# Each option contains:
for opt in option_chain[:3]:  # Show first 3
    print(f"""
    Underlying: {opt['underlying']}
    Strike: {opt['strike']}
    Type: {opt['option_type']}  # CE or PE
    LTP: {opt['ltp']}
    Moneyness: {opt['moneyness']}  # ATM, ITM, or OTM
    Symbol: {opt['symbol']}
    Expiry: {opt['expiry']}
    """)
```

### 3. Filter Options

```python
# Get only ATM options
atm_options = [opt for opt in option_chain if opt.get("moneyness") == "ATM"]

# Get only CE options
ce_options = [opt for opt in option_chain if opt.get("option_type") == "CE"]

# Get only PE options
pe_options = [opt for opt in option_chain if opt.get("option_type") == "PE"]

# Get specific strike
strike_23000 = [opt for opt in option_chain if opt.get("strike") == 23000]

# Get options with LTP available
options_with_ltp = [opt for opt in option_chain if opt.get("ltp") is not None]
```

---

## What Data is Returned?

Each option in the chain contains:

| Field | Description | Example |
|-------|-------------|---------|
| `underlying` | Underlying name | "NIFTY" |
| `exchange` | Exchange code | "NFO" |
| `expiry` | Expiry date string | "30DEC2024" |
| `expiry_date` | Parsed expiry date | "2024-12-30" |
| `strike` | Strike price | 23000.0 |
| `option_type` | CE or PE | "CE" |
| `symbol` | Trading symbol | "NIFTY25DEC2423000CE" |
| `token` | Symbol token | "12345" |
| `ltp` | Last traded price | 125.50 (or None if not available) |
| `spot_price` | Current spot price | 23150.25 |
| `moneyness` | ATM/ITM/OTM | "ATM" |

---

## Supported Underlyings

- **NIFTY** (NFO exchange)
- **BANKNIFTY** (NFO exchange)
- **FINNIFTY** (NFO exchange)
- **MIDCPNIFTY** (NFO exchange)
- **SENSEX** (BFO exchange)

---

## Output Files

When you run the test script, it saves the option chain data to:

```
storage/live/option_chain_{underlying}_{exchange}.csv
```

Example: `storage/live/option_chain_NIFTY_NFO.csv`

---

## Example Output

```
================================================================================
OPTION CHAIN: NIFTY
================================================================================
Spot Price: 23150.25
Expiry: 30DEC2024
Total Options: 120

Strike     Type  LTP        Moneyness  Symbol                         
--------------------------------------------------------------------------------
22800.00   CE    350.50     OTM        NIFTY25DEC2422800CE
22900.00   CE    280.25     OTM        NIFTY25DEC2422900CE
23000.00   CE    210.00     ATM        NIFTY25DEC2423000CE
23100.00   CE    150.75     ITM        NIFTY25DEC2423100CE
23200.00   CE    105.50     ITM        NIFTY25DEC2423200CE
...

Summary:
  CE Options: 60
  PE Options: 60
  CE LTP Range: 5.25 - 450.00
  PE LTP Range: 3.50 - 380.00
```

---

## Troubleshooting

### Issue: "LIVE TRADING BLOCKED BY ENV GUARD"

**Solution**: This is expected for data fetching. The guard only blocks actual order placement, not data retrieval. If you see this error, check your environment setup.

### Issue: "No options found"

**Possible causes**:
1. Instruments master file missing: Check `storage/instruments/OpenAPIScripMaster.json`
2. Underlying name mismatch: Use exact names: "NIFTY", "BANKNIFTY", etc.
3. Exchange code wrong: Use "NFO" for NSE underlyings, "BFO" for SENSEX

### Issue: "Could not fetch spot price"

**Solution**: 
- Check internet connection
- Verify broker authentication is working
- Run `python -m core.engine.test_angelone_api` to test connection

---

## Advanced Usage

### Fetch for Multiple Underlyings

```python
from core.brokers.angel_one.broker import AngelOneBroker

broker = AngelOneBroker()

underlyings = ["NIFTY", "BANKNIFTY", "FINNIFTY"]

all_chains = {}
for underlying in underlyings:
    exchange = "NFO" if underlying != "SENSEX" else "BFO"
    chain = broker.get_option_chain_by_underlying(
        underlying_name=underlying,
        exchange=exchange,
        include_all_strikes=False  # ATM only for speed
    )
    all_chains[underlying] = chain
    print(f"{underlying}: {len(chain)} options")
```

### Save to DataFrame

```python
import pandas as pd

option_chain = broker.get_option_chain_by_underlying("NIFTY", "NFO", True)

df = pd.DataFrame(option_chain)

# Save to CSV
df.to_csv("nifty_option_chain.csv", index=False)

# Filter and analyze
ce_df = df[df['option_type'] == 'CE']
atm_df = df[df['moneyness'] == 'ATM']

print(f"ATM CE options: {len(atm_df)}")
print(f"Average ATM CE LTP: {atm_df['ltp'].mean():.2f}")
```

---

## Next Steps

1. **Test the functionality**: Run the test script with your preferred underlying
2. **Integrate into your code**: Use `get_option_chain_by_underlying()` in your trading logic
3. **Customize filters**: Adjust `include_all_strikes` parameter based on your needs
4. **Build strategies**: Use the option chain data for strategy development

---

**Ready to use!** 🚀

Run: `python -m core.engine.test_angelone_option_chain NIFTY`
