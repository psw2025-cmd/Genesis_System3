# Complete Paper Trading System Guide

## Overview

This guide covers the complete paper trading system with multi-day support, pre-trading validation, and post-trading cleanup.

---

## System Architecture

### **Components:**

1. **Pre-Trading Validation** (`scripts/pre_trading_validation.py`)
   - Checks Python environment
   - Verifies directories
   - Validates configuration
   - Checks base data
   - Verifies components
   - Checks output files
   - Handles previous session data

2. **Multi-Session Handler** (`scripts/multi_session_handler.py`)
   - Tracks sessions across multiple days
   - Archives daily sessions
   - Maintains cumulative statistics
   - Handles session continuity

3. **Post-Trading Cleanup** (`scripts/post_trading_cleanup.py`)
   - Archives session data
   - Clears current session (optional)
   - Prepares for next session
   - Generates session reports

4. **End-to-End Verification** (`scripts/end_to_end_verification.py`)
   - Verifies pre-trading setup
   - Monitors during trading
   - Validates post-trading

5. **Main Batch File** (`START_PAPER_TRADING_COMPLETE.bat`)
   - Orchestrates all phases
   - Handles errors
   - Provides monitoring

---

## Usage

### **Single Session:**

```batch
START_PAPER_TRADING_COMPLETE.bat
```

### **With Custom Parameters:**

```batch
START_PAPER_TRADING_COMPLETE.bat TREND_UP 10 5
```

Parameters:
- Scenario (default: TREND_UP)
- Duration in minutes (default: 10)
- Refresh interval in seconds (default: 5)

---

## Process Flow

### **Phase 1: Pre-Trading Validation**

1. Check Python environment
2. Verify directories exist
3. Validate configuration flags
4. Check base data
5. Verify components importable
6. Check output files writable
7. Handle previous session data

**If any check fails → System stops**

### **Phase 2: Multi-Session Setup**

1. Initialize multi-session handler
2. Check if new day (reset if needed)
3. Load previous session state
4. Update session tracking

### **Phase 3: Paper Trading**

1. Start simulation in background
2. Run end-to-end verification
3. Monitor status every 5 seconds
4. Update multi-session state periodically

### **Phase 4: Post-Trading Cleanup**

1. Archive session data
2. Update multi-session state
3. Clear current session (optional)
4. Prepare for next session
5. Generate session report

---

## Multi-Day Support

### **How It Works:**

1. **Session ID**: Based on date (YYYYMMDD)
2. **State File**: `storage/multi_session_state.json`
3. **Archive**: `storage/archive/session_YYYYMMDD_HHMMSS/`

### **Session Continuity:**

- Each day gets a new session ID
- Previous day's data is archived
- Cumulative statistics maintained
- Daily PnL tracked separately

### **Data Persistence:**

- **Per Session**: PnL, positions, trades
- **Cumulative**: Total days, total trades, total PnL
- **Archive**: All session data preserved

---

## Verification

### **Pre-Trading:**

```batch
python scripts\pre_trading_validation.py
```

### **During Trading:**

```batch
python scripts\end_to_end_verification.py
```

### **Post-Trading:**

```batch
python scripts\post_trading_cleanup.py
```

### **Multi-Session:**

```batch
python scripts\verify_multiple_sessions.py
```

---

## Output Files

### **Current Session:**
- `outputs/pnl_live.json` - Current PnL
- `outputs/positions_live.json` - Open positions
- `outputs/paper_trades_live.csv` - Trade history
- `outputs/top_trade_signal.json` - Latest signal
- `outputs/qc_report_live.json` - QC status

### **Archived Sessions:**
- `storage/archive/session_YYYYMMDD_HHMMSS/`
  - `pnl.json`
  - `positions.json`
  - `trades.csv`
  - `session_summary.json`
  - `session_report.json`

### **Multi-Session State:**
- `storage/multi_session_state.json`
  - All sessions tracked
  - Cumulative statistics
  - Last session date

---

## Troubleshooting

### **Pre-Trading Validation Fails:**

1. Check Python version (need 3.8+)
2. Verify venv exists
3. Check directories exist
4. Verify configuration flags (both False)
5. Check base CSV exists

### **During Trading Issues:**

1. Check logs: `logs/`
2. Verify outputs being generated
3. Check simulation is running
4. Verify components working

### **Post-Trading Issues:**

1. Check archive directory exists
2. Verify files being archived
3. Check multi-session state updating

---

## Best Practices

1. **Always run pre-trading validation** before starting
2. **Let cleanup run** at end of session
3. **Check archives** periodically
4. **Monitor multi-session state** for trends
5. **Review session reports** for analysis

---

## Status

✅ **All components implemented and tested**
✅ **Multi-day support working**
✅ **End-to-end verification complete**
✅ **Ready for production use**

---

**Last Updated**: 2026-01-31
