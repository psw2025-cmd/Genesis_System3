# Live Paper Trading Guide - REAL Market Data

## ✅ CONFIRMED: Real Live Market Data Only

**NO virtual/simulation data will be used.**

The system is configured to use **REAL live market data** from Angel One API.

---

## 🚀 Quick Start

### Single Command to Start:
```batch
START_REAL_LIVE_PAPER_TRADING.bat
```

This will:
1. ✅ Check market hours (09:15 - 15:30 IST)
2. ✅ Initialize Angel One broker connection
3. ✅ Fetch REAL live market data
4. ✅ Start paper trading with real data
5. ✅ Update every 5 seconds

---

## 📋 What You Need to Do

### Prerequisites:
1. ✅ **Angel One Credentials**: Already configured in `.env` file
2. ✅ **Market Hours**: Run during 09:15 - 15:30 IST (Mon-Fri)
3. ✅ **Internet Connection**: Required for API calls
4. ✅ **Virtual Environment**: Already set up

### Steps to Start:

#### Step 1: Verify Credentials
```bash
# Check if .env file exists and has credentials
type .env | findstr ANGEL
```

#### Step 2: Start Paper Trading
```batch
# Double-click or run:
START_REAL_LIVE_PAPER_TRADING.bat
```

#### Step 3: Monitor
- Watch the console for real-time updates
- Check `outputs/chain_raw_live.csv` for latest data
- Check `outputs/top_trade_signal.json` for trade signals
- Check `logs/run.log` for detailed logs

---

## 🔍 Verification: Real Data vs Simulation

### How to Confirm It's Using Real Data:

#### 1. Check Logs
Look for these messages in `logs/run.log`:
```
[INFO] Initializing broker...
[INFO] Initializing components...
[INFO] Starting LIVE chain system (refresh: 5s)
```

**NOT these (which indicate simulation):**
```
[INFO] SIMULATION MODE: Skipping broker initialization
[INFO] Starting SIMULATION chain system
```

#### 2. Check Data Source
The system fetches from:
- ✅ **Real API**: `https://apiconnect.angelone.in/rest/secure/angelbroking/`
- ❌ **NOT from**: `src/sim/replay_engine.py` (simulation)

#### 3. Check Command Line
The batch file runs:
```bash
python scripts\run_live_chain.py --refresh 5
```

**Note**: NO `--sim-mode` flag = Real data

---

## ⚙️ Configuration

### Real Data Mode (Current):
```python
# scripts/run_live_chain.py
sim_mode = False  # ← REAL DATA
```

### Simulation Mode (NOT used):
```python
# Only used if you explicitly add --sim-mode flag
sim_mode = True  # ← Only for testing
```

---

## 📊 What Happens During Live Trading

### Every 5 Seconds:
1. ✅ **Fetch Real Data**: Calls Angel One API for live option chain
2. ✅ **Process Data**: Calculate Greeks, IV, deltas
3. ✅ **QC Validation**: Check data quality
4. ✅ **Generate Signals**: Top symbol selection + strategy
5. ✅ **Paper Trade**: Simulate trade execution (NO real orders)
6. ✅ **Update PnL**: Track paper trading P&L
7. ✅ **Save Outputs**: CSV, JSON, logs

### Data Flow:
```
Angel One API (REAL)
    ↓
Broker Connection (REAL)
    ↓
Option Chain Data (REAL)
    ↓
Processing & Calculations
    ↓
Paper Trading Signals
    ↓
Simulated Execution (PAPER)
    ↓
PnL Tracking
```

---

## 🛡️ Safety Confirmation

### Paper Trading Mode:
- ✅ **LIVE_TRADING_ENABLED = False** (in `config/live_trade_config.py`)
- ✅ **USE_LIVE_EXECUTION_ENGINE = False**
- ✅ **All trades are simulated** (no real orders sent)
- ✅ **No real capital at risk**

### Real Data Mode:
- ✅ **sim_mode = False** (default)
- ✅ **Broker initialized** (real API connection)
- ✅ **Real market data fetched** (live prices, OI, volume)
- ✅ **Real-time updates** (every 5 seconds)

---

## 📁 Output Files

### Real Data Outputs:
- `outputs/chain_raw_live.csv` - Real option chain data
- `outputs/underlying_rank_live.csv` - Real-time rankings
- `outputs/top_trade_signal.json` - Real trade signals
- `outputs/qc_report_live.json` - Real QC results
- `logs/run.log` - Real execution logs

### Paper Trading Outputs:
- `outputs/paper_trades.csv` - Simulated trades
- `outputs/pnl_summary.json` - Paper trading P&L
- `storage/live/option_chain.db` - Real data snapshots

---

## ⚠️ Important Notes

### Market Hours:
- **Open**: 09:15 IST (Mon-Fri)
- **Close**: 15:30 IST (Mon-Fri)
- **Outside hours**: System will warn but can continue with `--ignore-market-hours`

### Rate Limiting:
- Angel One API has rate limits
- If you see "Access denied because of exceeding access rate":
  - Wait a few minutes
  - System will retry automatically
  - Consider reducing refresh interval

### Data Completeness:
- Some contracts may not have all data (normal)
- Greeks calculated via Black-Scholes if API fails
- System handles missing data gracefully

---

## 🔧 Troubleshooting

### Issue: "Market is closed"
**Solution**: Run during market hours (09:15-15:30 IST) or use `--ignore-market-hours`

### Issue: "Access denied - rate limit"
**Solution**: Wait a few minutes, system will retry

### Issue: "No data returned"
**Solution**: 
- Check internet connection
- Verify Angel One credentials in `.env`
- Check if market is open

### Issue: "Broker initialization failed"
**Solution**:
- Check `.env` file has correct credentials
- Verify TOTP secret is correct
- Check internet connection

---

## ✅ Final Confirmation

**To verify you're using REAL data:**

1. **Check the batch file**: `START_REAL_LIVE_PAPER_TRADING.bat`
   - Should NOT have `--sim-mode` flag
   - Should have `--refresh 5` (or your preferred interval)

2. **Check the logs**: `logs/run.log`
   - Should say "LIVE chain system"
   - Should NOT say "SIMULATION MODE"

3. **Check the data**: `outputs/chain_raw_live.csv`
   - Should have current timestamps
   - Should match current market prices

4. **Check broker connection**:
   - Should see "Initializing broker..." in logs
   - Should see API calls in logs

---

## 🎯 Summary

✅ **Real Market Data**: YES (Angel One API)  
✅ **Simulation Mode**: NO (disabled)  
✅ **Paper Trading**: YES (simulated execution)  
✅ **Real Orders**: NO (safety enabled)  
✅ **Live Updates**: YES (every 5 seconds)  

**You're ready to start live paper trading with real market data!**

---

## 📞 Quick Commands

```batch
# Start real live paper trading
START_REAL_LIVE_PAPER_TRADING.bat

# Check status
python scripts\check_paper_trading_status.py

# View latest data
type outputs\chain_raw_live.csv | more

# View logs
type logs\run.log | more
```

---

**Status**: ✅ **READY FOR REAL LIVE PAPER TRADING**
