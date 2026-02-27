# Quick Start - Batch Files for Paper Trading

## 🚀 Single Command to Run Everything

### **Option 1: Complete Automation (Recommended)**
```batch
START_PAPER_TRADING.bat
```

**What it does:**
- ✅ Activates virtual environment automatically
- ✅ Starts simulation in background
- ✅ Shows live status updates every 5 seconds
- ✅ Everything in one window
- ✅ Press Ctrl+C to stop monitoring (simulation continues)

---

### **Option 2: Simple Mode**
```batch
run_paper_trading_simple.bat
```

**What it does:**
- ✅ Runs simulation with output
- ✅ Single window
- ✅ Press Ctrl+C to stop

---

### **Option 3: With Status Updates**
```batch
run_paper_trading_with_status.bat
```

**What it does:**
- ✅ Runs simulation in background
- ✅ Shows status every 10 seconds
- ✅ Auto-refreshes

---

## 📋 Files Created

| File | Purpose |
|------|---------|
| `START_PAPER_TRADING.bat` | **Main file** - Complete automation |
| `run_paper_trading_complete.bat` | Simulation + Monitor in separate windows |
| `run_paper_trading_simple.bat` | Simple single-window mode |
| `run_paper_trading_with_status.bat` | Auto-refreshing status |

---

## ✅ How to Use

1. **Double-click** `START_PAPER_TRADING.bat`
2. **Wait** for simulation to start (8 seconds)
3. **Watch** live paper trading status
4. **Press Ctrl+C** to stop monitoring (simulation continues in background)

---

## 🎯 What You'll See

```
================================================================================
  PAPER TRADING STATUS - 2026-01-31 14:00:00
================================================================================

PnL SUMMARY:
--------------------------------------------------------------------------------
  Total PnL: Rs 165209.78
  Unrealized: Rs -34031.40
  Realized: Rs 199241.18
  Open Positions: 3
  Total Trades: 28
  Winning: 19 | Losing: 9
  Win Rate: 67.9%
  Avg PnL per Trade: Rs 7115.76

OPEN POSITIONS (3):
--------------------------------------------------------------------------------
  1. BANKNIFTY 61200.0 CE
     Entry: Rs 890.94 | Current: Rs 4081.28
     [PROFIT] PnL: Rs 207350.10 (358.09%)
  ...
```

---

## 🔧 Requirements

- Virtual environment must exist (`venv` folder)
- Python packages installed
- `option_chain_ALL_INDICES.csv` (optional - system will use simulation data if missing)

---

## ✅ Tested & Verified

All batch files have been tested and verified to work correctly.

**Status**: ✅ **READY TO USE**
