# Quick Start - Live Trading (Single Click)

## For Tomorrow's Live Market

### Step 1: Pre-Market Check (Run Now)
```bash
PRE_MARKET_CHECK.bat
```
**What it does:**
- Checks virtual environment
- Verifies all required files
- Validates system components
- Confirms market hours detection

**Expected Result:** "ALL CHECKS PASSED - SYSTEM READY"

---

### Step 2: Start Live Trading (Single Click)
```bash
START_LIVE_TRADING_AUTO.bat
```
**What it does automatically:**
1. ✅ Activates virtual environment
2. ✅ Runs pre-trading validation
3. ✅ Sets up multi-session handling
4. ✅ Auto-detects market hours
5. ✅ Starts paper trading automatically
6. ✅ Auto-updates Excel every 5 minutes
7. ✅ Shows live monitor with real-time updates

**No manual intervention needed!**

---

## What You'll See

### Live Monitor Display:
- Real-time PnL updates
- Open positions
- Recent trades
- System status
- Market hours status

### Excel Auto-Updates:
- Every 5 minutes during market hours
- Includes latest predictions
- Updates accuracy metrics
- Shows live trade data

---

## Important Notes

### Market Hours:
- **Opens:** 09:15 IST
- **Closes:** 15:30 IST
- System auto-detects and starts/stops accordingly

### To Stop:
- Press `Ctrl+C` in the monitor window
- System will clean up automatically

### Files Created:
- `outputs/paper_trades_live.csv` - All trades
- `outputs/pnl_live.json` - PnL summary
- `outputs/positions_live.json` - Open positions
- `outputs/OptionChain_Master_v3_AI_FINAL.xlsx` - Updated Excel

---

## Troubleshooting

### If market hours detection fails:
- System will still run (uses simulation mode as fallback)

### If Excel update fails:
- Check `outputs/` folder permissions
- Verify `chain_raw_live.csv` exists

### If paper trading doesn't start:
- Check `config/.env` file exists
- Verify virtual environment is activated

---

## Summary

**Before Market Opens:**
1. Run `PRE_MARKET_CHECK.bat` ✅

**When Market Opens:**
1. Run `START_LIVE_TRADING_AUTO.bat` ✅
2. Watch the monitor ✅
3. Excel auto-updates every 5 minutes ✅

**That's it! Everything is automated!**
