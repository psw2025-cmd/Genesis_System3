# 🚀 How to Run Full System with Live Paper Trading

## Quick Start Command

### Run with Live Angel Data (Paper Trading Enabled by Default)

```bash
cd C:\Genesis_System3
python option_chain_automation_master.py --refresh 5
```

**This will:**
- ✅ Connect to Angel One API
- ✅ Fetch real live market data
- ✅ Generate trading signals
- ✅ Execute paper trades automatically (when signals are generated)
- ✅ Track PnL in real-time
- ✅ Update every 5 seconds

---

## 📊 Monitor Paper Trading Results

### **Option 1: Watch Output Files (Real-time)**

Open these files in a text editor and refresh periodically:

#### **1. Paper Trading PnL Summary**
```bash
outputs/pnl_live.json
```
**Shows:**
- Total PnL (realized + unrealized)
- Win rate
- Total trades
- Open positions count

#### **2. Open Positions**
```bash
outputs/positions_live.json
```
**Shows:**
- All currently open positions
- Entry price vs current price
- Unrealized PnL per position

#### **3. Trade History**
```bash
outputs/paper_trades_live.csv
```
**Shows:**
- All executed trades (open and closed)
- Entry/exit prices
- PnL per trade
- Trade status (OPEN/CLOSED)

#### **4. Top Trade Signal**
```bash
outputs/top_trade_signal.json
```
**Shows:**
- Current best trading signal
- Action (TRADE or NO_TRADE)
- Confidence level
- Strategy used

#### **5. System Health**
```bash
outputs/health.json
```
**Shows:**
- System status
- Total cycles completed
- Data fetch success rate
- Current positions count

---

### **Option 2: Use Monitoring Script**

Run this in a separate terminal to see live updates:

```bash
python scripts/check_paper_trading_status.py
```

Or use the live monitor:

```bash
python scripts/live_paper_trading_monitor.py
```

---

## 🎯 Understanding Paper Trading Output

### **When Trades Execute:**

Trades will execute automatically when:
1. ✅ Signal has `action: "TRADE"` (not "NO_TRADE")
2. ✅ Signal confidence >= 0.75 (default minimum)
3. ✅ QC validation passed
4. ✅ Max positions limit not reached (default: 5)

### **What You'll See:**

#### **If Trades Are Executing:**
```json
// outputs/pnl_live.json
{
  "total_pnl": 5000.50,
  "realized_pnl": 3000.00,
  "unrealized_pnl": 2000.50,
  "total_trades": 5,
  "win_rate": 60.0,
  "open_positions": 2
}
```

#### **If No Trades (Normal):**
```json
// outputs/top_trade_signal.json
{
  "action": "NO_TRADE",
  "reason": "NO_STRATEGY_SIGNALS",
  "confidence": 0.0
}
```

**This is normal** - the system only trades when conditions are met for safety.

---

## ⚙️ Advanced Options

### **Run for Specific Duration**
```bash
python option_chain_automation_master.py --refresh 5 --duration 60
```
Runs for 60 minutes

### **Run Specific Number of Cycles**
```bash
python option_chain_automation_master.py --refresh 5 --cycles 10
```
Runs 10 cycles then stops

### **Enable Live Trade Execution (⚠️ DANGER - Real Money)**
```bash
python option_chain_automation_master.py --refresh 5 --live-trade-enable
```
**WARNING:** This enables REAL trading with real money. Only use if you understand the risks!

---

## 📈 What to Expect

### **First Few Cycles:**
- System fetches data (takes ~15-20 seconds per cycle)
- QC validation runs
- Signals generated
- Most signals will be "NO_TRADE" (normal - system is conservative)

### **When Market Conditions Are Right:**
- Signals with `action: "TRADE"` will appear
- Paper trades will execute automatically
- Positions will appear in `outputs/positions_live.json`
- PnL will update in real-time

### **Typical Output Files:**
```
outputs/
├── pnl_live.json              ← Total PnL, win rate, trade stats
├── positions_live.json        ← Current open positions
├── paper_trades_live.csv      ← All trade history
├── top_trade_signal.json      ← Best current signal
├── qc_report_live.json        ← Data quality report
├── chain_raw_live.csv         ← Raw option chain data
├── underlying_rank_live.csv   ← Index rankings
└── health.json                ← System health metrics
```

---

## 🔍 Troubleshooting

### **No Trades Executing?**
**This is normal!** The system is conservative:
- ✅ Check `outputs/top_trade_signal.json` - if `action: "NO_TRADE"`, system is working correctly
- ✅ System only trades when confidence >= 0.75
- ✅ System requires QC validation to pass
- ✅ This is a safety feature, not a bug

### **Want to See More Trades?**
You can lower the confidence threshold (edit code) or wait for better market conditions.

### **System Not Fetching Data?**
- Check `outputs/health.json` - look for `is_connected: true`
- Check logs in `logs/option_chain_automation_YYYYMMDD.log`
- Verify Angel One credentials in `config/.env`

---

## ✅ Verification Checklist

After starting the system, verify:

1. ✅ **System Running:**
   ```bash
   # Check health.json
   cat outputs/health.json
   # Should show: "is_running": true
   ```

2. ✅ **Data Fetching:**
   ```bash
   # Check chain_raw_live.csv has data
   # Should have rows with option chain data
   ```

3. ✅ **Signals Generating:**
   ```bash
   # Check top_trade_signal.json
   # Should update every 5 seconds
   ```

4. ✅ **Paper Trading Ready:**
   ```bash
   # Check pnl_live.json exists
   # Will show trades when they execute
   ```

---

## 🎉 Success Indicators

You'll know it's working when:
- ✅ `outputs/health.json` shows `is_running: true`
- ✅ `outputs/top_trade_signal.json` updates every 5 seconds
- ✅ `outputs/chain_raw_live.csv` has fresh data
- ✅ Console shows "CYCLE #X (LIVE)" messages
- ✅ When trades execute, `outputs/positions_live.json` shows positions

---

## 📝 Notes

- **Paper trading is enabled by default** - no real money at risk
- **Trades execute automatically** when conditions are met
- **System is conservative** - expects mostly NO_TRADE signals
- **All data is saved automatically** - no manual steps needed
- **System runs continuously** until you stop it (Ctrl+C)

---

**Ready to start? Run:**
```bash
python option_chain_automation_master.py --refresh 5
```
