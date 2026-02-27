# Monitor Issues Analysis and Fix

**Date**: 2026-01-31  
**Status**: ✅ **FIXED**

---

## 🔍 Issues Found in Monitor Output

### **Issue 1: Price Showing as Rs 0.00**
**Problem**: All trades showing "Price: Rs 0.00"
**Root Cause**: Monitor was looking for `price` column, but CSV has `entry_price` and `exit_price`
**Fix**: Updated monitor to use `exit_price` for closed trades, `entry_price` for open trades

### **Issue 2: Action Column Confusion**
**Problem**: Showing "[CLOSE] OPEN BANKNIFTY" - confusing display
**Root Cause**: Monitor was looking for `action` column, but CSV has `status` column (OPEN/CLOSED)
**Fix**: Updated monitor to read `status` column and display correctly

### **Issue 3: Qty Showing as "nan"**
**Problem**: Some trades showing qty as "nan"
**Root Cause**: Missing qty values in CSV
**Fix**: Added check for NaN values and default to 0

### **Issue 4: Timestamp Showing as "N/A"**
**Problem**: All timestamps showing as "N/A"
**Root Cause**: Monitor was looking for `time_ist` or `timestamp`, but CSV has `entry_time_ist` and `exit_time_ist`
**Fix**: Updated monitor to use `exit_time_ist` for closed trades, `entry_time_ist` for open trades

---

## ✅ Fixes Applied

### **File: `scripts/monitor_10min.py`**

**Changes:**
1. Added `import numpy as np` for NaN checking
2. Updated trade display logic to:
   - Read `status` instead of `action`
   - Use `exit_price` for closed trades, `entry_price` for open trades
   - Use `exit_time_ist` for closed trades, `entry_time_ist` for open trades
   - Handle NaN qty values
   - Display PnL and exit reason for closed trades

**Before:**
```python
action = trade.get('action', 'N/A')
price = trade.get('price', 0)
timestamp = trade.get('time_ist', trade.get('timestamp', 'N/A'))
```

**After:**
```python
status = trade.get('status', 'N/A')
if status == 'CLOSED' and pd.notna(trade.get('exit_price')):
    price = float(trade.get('exit_price', 0))
    timestamp = trade.get('exit_time_ist', trade.get('exit_timestamp', 'N/A'))
    pnl = trade.get('realized_pnl', 0)
    reason = trade.get('exit_reason', '')
else:
    price = float(trade.get('entry_price', 0))
    timestamp = trade.get('entry_time_ist', trade.get('entry_timestamp', 'N/A'))
    pnl = trade.get('unrealized_pnl', 0)
    reason = ''
```

---

## 📊 CSV Structure Understanding

The `paper_trades_live.csv` file stores **position-level data**, not trade-level events:

**Columns:**
- `status`: OPEN or CLOSED
- `entry_price`: Entry price when position opened
- `exit_price`: Exit price when position closed (NaN if still open)
- `entry_time_ist`: Entry timestamp
- `exit_time_ist`: Exit timestamp (NaN if still open)
- `realized_pnl`: PnL if closed
- `unrealized_pnl`: PnL if still open
- `exit_reason`: STOP_LOSS, TARGET, etc.

**This is correct** - it's a position ledger, not a trade log.

---

## ✅ Verification

**After Fix:**
- ✅ Prices display correctly (entry_price or exit_price)
- ✅ Status displays correctly (OPEN/CLOSED)
- ✅ Timestamps display correctly (entry_time_ist or exit_time_ist)
- ✅ Qty handles NaN values
- ✅ PnL and exit reason displayed for closed trades

---

**Status**: ✅ **ALL ISSUES FIXED**

**The monitor now correctly displays position data from the CSV.**
