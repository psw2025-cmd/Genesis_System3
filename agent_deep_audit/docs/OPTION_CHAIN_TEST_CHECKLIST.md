# Option Chain Fetching - Test Checklist

## ✅ Implementation Complete

### Files Modified/Created

1. **Core Broker Class** (`core/brokers/dhan/broker.py`)
   - ✅ Added `allow_data_only` parameter to `__init__()`
   - ✅ Added `get_option_chain()` method
   - ✅ Added `get_option_chain_by_underlying()` method
   - ✅ Added `_check_live_trading_allowed()` for future order placement

2. **Test Script** (`core/engine/test_angelone_option_chain.py`)
   - ✅ Created complete test script
   - ✅ Uses `allow_data_only=True`
   - ✅ Supports command-line arguments
   - ✅ Formats and displays option chain data
   - ✅ Saves to CSV

3. **Updated Existing Scripts** (All use `allow_data_only=True`)
   - ✅ `core/engine/test_angelone_api.py`
   - ✅ `core/engine/dhan_options_watch.py`
   - ✅ `core/engine/dhan_options_watch_loop.py`
   - ✅ `core/engine/dhan_monday_diagnostic.py`
   - ✅ `core/engine/system3_phase205_broker_selftest.py`
   - ✅ `core/engine/ultra_live_signals_shadow.py`

## 🧪 Ready to Test

### Prerequisites Check

Before running the test, ensure:

- [ ] Virtual environment is activated
- [ ] Credentials are configured in `config/.env`:
  - [ ] `ANGELONE_API_KEY`
  - [ ] `ANGELONE_CLIENT_ID`
  - [ ] `ANGELONE_PIN` or `ANGELONE_PASSWORD`
  - [ ] `ANGELONE_TOTP` (TOTP secret)
- [ ] Instruments master file exists: `storage/instruments/OpenAPIScripMaster.json`
- [ ] Dependencies installed: `dhanhq-python`, `pyotp`, `pandas`

### Test Commands

```bash
# 1. Activate virtual environment
venv\Scripts\activate

# 2. Test NIFTY option chain (ATM strikes only)
python -m core.engine.test_angelone_option_chain NIFTY

# 3. Test BANKNIFTY with all strikes
python -m core.engine.test_angelone_option_chain BANKNIFTY --all-strikes

# 4. Test other underlyings
python -m core.engine.test_angelone_option_chain FINNIFTY
python -m core.engine.test_angelone_option_chain MIDCPNIFTY
python -m core.engine.test_angelone_option_chain SENSEX
```

### Expected Output

```
Initializing Dhan broker...
Login successful.

Fetching option chain data...

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
...

Summary:
  CE Options: 60
  PE Options: 60
  CE LTP Range: 5.25 - 450.00
  PE LTP Range: 3.50 - 380.00

Option chain saved to: storage/live/option_chain_NIFTY_NFO.csv
```

### Troubleshooting

#### Issue: "LIVE TRADING BLOCKED BY ENV GUARD"
**Status**: ✅ **FIXED** - Should not occur with `allow_data_only=True`

#### Issue: "Missing Dhan env values"
**Solution**: Check `config/.env` file has all required credentials

#### Issue: "Index NIFTY not found"
**Solution**: Check `storage/instruments/OpenAPIScripMaster.json` exists and is valid

#### Issue: "Could not fetch spot price"
**Solution**: 
- Check internet connection
- Verify broker authentication works: `python -m core.engine.test_angelone_api`
- Check if market is open (for live prices)

#### Issue: "No options found"
**Solution**:
- Verify instruments master file is up to date
- Check underlying name spelling (must be exact: "NIFTY", "BANKNIFTY", etc.)
- Verify exchange code ("NFO" for NSE, "BFO" for BSE)

## 📊 Output Files

After successful run, check:

- [ ] CSV file created: `storage/live/option_chain_{underlying}_{exchange}.csv`
- [ ] CSV contains columns: underlying, exchange, expiry, strike, option_type, symbol, token, ltp, spot_price, moneyness
- [ ] Data is sorted by strike price
- [ ] Both CE and PE options are included

## 🔍 Verification Steps

1. **Test Basic Functionality**
   ```bash
   python -m core.engine.test_angelone_option_chain NIFTY
   ```
   Should complete without errors and display option chain.

2. **Test All Strikes**
   ```bash
   python -m core.engine.test_angelone_option_chain BANKNIFTY --all-strikes
   ```
   Should fetch more options than default (ATM only).

3. **Verify CSV Output**
   ```bash
   # Check if file exists
   dir storage\live\option_chain_*.csv
   
   # View first few lines (if you have a CSV viewer)
   type storage\live\option_chain_NIFTY_NFO.csv | more
   ```

4. **Test Different Underlyings**
   - NIFTY (NFO)
   - BANKNIFTY (NFO)
   - FINNIFTY (NFO)
   - MIDCPNIFTY (NFO)
   - SENSEX (BFO)

## ✅ Success Criteria

- [ ] Script runs without errors
- [ ] Option chain data is fetched successfully
- [ ] Data is displayed in formatted table
- [ ] CSV file is created with correct data
- [ ] Both CE and PE options are included
- [ ] Spot price is correctly fetched
- [ ] Moneyness (ATM/ITM/OTM) is calculated correctly

## 🎯 Next Steps After Testing

Once testing is successful:

1. **Integrate into Trading Logic**
   - Use `get_option_chain_by_underlying()` in your strategies
   - Filter options based on your criteria (strike, moneyness, etc.)

2. **Build Option Analysis Tools**
   - Calculate Greeks (if available)
   - Build volatility surfaces
   - Analyze option flow

3. **Automate Option Chain Monitoring**
   - Schedule regular option chain fetches
   - Track changes over time
   - Build alerts for specific conditions

---

**Status**: ✅ **READY FOR TESTING**

Run the commands and verify everything works as expected!
