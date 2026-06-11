# Quick Start - Live Paper Trading

## 🚀 See Paper Trading Live on Screen (2 Steps)

### **Step 1: Start Simulation**
```bash
cd C:\Genesis_System3
venv\Scripts\activate
python -m scripts.replay_test --scenario TREND_UP --duration 10 --refresh 5
```

### **Step 2: Start Monitor (New Terminal Window)**
```bash
cd C:\Genesis_System3
venv\Scripts\activate
python scripts/monitor_live_simulation.py
```

**That's it!** You'll see:
- ✅ Trade signals generated
- ✅ Paper trades executed automatically
- ✅ Open positions with live PnL
- ✅ Total PnL (realized + unrealized)
- ✅ Win rate and trade count
- ✅ Everything updates every 2 seconds

---

## 📊 What You'll See

### **On Monitor Screen:**

```
💰 PAPER TRADING:
--------------------------------------------------------------------------------
  🟢 Total PnL: ₹125.50 (Unrealized: ₹75.00, Realized: ₹50.50)
  📊 Total Trades: 5 | Win Rate: 60.0%
  📈 Open Positions: 2

  📋 OPEN POSITIONS (2):
    1. NIFTY 24500 CE | Entry: ₹150.00 | Current: ₹165.00 | 🟢 PnL: ₹15.00 (10.00%)
    2. BANKNIFTY 49000 PE | Entry: ₹200.00 | Current: ₹185.00 | 🔴 PnL: -₹15.00 (-7.50%)
```

---

## ✅ Everything is Automatic

- ✅ **Trades execute automatically** when signals are generated
- ✅ **Positions update** every 5 seconds with current prices
- ✅ **PnL calculated** in real-time
- ✅ **Auto-close** on Stop Loss / Target
- ✅ **All data saved** automatically
- ✅ **Live display** on monitor

---

## 📁 Output Files

All saved automatically:
- `outputs/paper_trades_live.csv` - All trades
- `outputs/positions_live.json` - Current positions
- `outputs/pnl_live.json` - PnL summary

---

## 🎯 That's It!

Just run the two commands above and watch paper trading happen live on your screen!

**No manual steps needed - everything is automatic!**
