# Batch File Instructions - Complete Guide

## 🚀 Single Command to Run Everything

### **Main File: START_PAPER_TRADING.bat**

**Just double-click this file and everything runs automatically!**

---

## ✅ What the Batch File Does

1. **Checks virtual environment** - Verifies venv exists
2. **Activates venv** - Automatically activates Python environment
3. **Creates directories** - Creates outputs/ and logs/ if needed
4. **Starts simulation** - Runs in background (minimized window)
5. **Shows live status** - Displays paper trading status every 5 seconds
6. **Auto-refreshes** - Updates continuously

---

## 📋 How to Use

### **Step 1: Double-Click**
```
START_PAPER_TRADING.bat
```

### **Step 2: Wait 8 Seconds**
The system will:
- Activate virtual environment
- Start simulation in background
- Initialize data

### **Step 3: Watch Live Status**
You'll see:
- Total PnL
- Open positions
- Trade history
- Win rate
- All updates every 5 seconds

### **Step 4: Stop (Optional)**
- Press **Ctrl+C** to stop monitoring
- Simulation continues in background
- To stop simulation: Close minimized window or Task Manager

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

## ✅ Verification

**Tested and verified:**
- ✅ Batch file executes correctly
- ✅ Virtual environment activates
- ✅ Simulation starts in background
- ✅ Status monitor runs
- ✅ Output files generated
- ✅ No errors

---

## 🔧 Alternative Batch Files

| File | Use Case |
|------|----------|
| `START_PAPER_TRADING.bat` | **Main file** - Complete automation |
| `run_paper_trading_simple.bat` | Simple single-window mode |
| `run_paper_trading_with_status.bat` | Auto-refresh every 10 seconds |

---

## 📝 Requirements

- Virtual environment (`venv` folder) must exist
- Python packages installed
- `option_chain_ALL_INDICES.csv` (optional)

---

## ✅ Status

**All batch files tested and verified!**

**Ready to use - Just double-click `START_PAPER_TRADING.bat`**
