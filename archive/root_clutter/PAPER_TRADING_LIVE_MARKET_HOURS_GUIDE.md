# System3 Paper Trading on Live Market Hours

## Overview

You now have **paper trading enabled for real live market hours** (9:15 AM - 3:30 PM IST). The system will:

1. ✅ Generate real signals from live market data
2. ✅ Simulate trade execution with realistic fill prices
3. ✅ Track positions and calculate P&L in real-time
4. ✅ Run during actual market hours without real capital at risk

---

## Current Configuration

```python
# config/live_trade_config.py

LIVE_TRADING_ENABLED = False           # ← No real capital used
USE_LIVE_EXECUTION_ENGINE = False      # ← Uses Phase 106 (paper trading)
```

**This combination means**:
- Phase 106 (DRY-RUN Executor) runs during market hours
- Phase 107 (LIVE Execution) is completely skipped
- All trades are simulated on real market data
- No actual orders are sent to Angel One broker

---

## How It Works During Market Hours

### Timeline (9:15 AM - 3:30 PM)

```
9:15 AM - Market opens
  ↓
System3 Master detects market hours (is_market_time() = True)
  ↓
Every hour during market hours:
  ├─ Run OP Cycle (signal generation from live data)
  ├─ Phase 106: Simulate trade execution
  │   ├─ Read live signals from angel_index_ai_signals.csv
  │   ├─ Simulate order placement
  │   ├─ Simulate realistic fill prices (with slippage)
  │   ├─ Update live_orders_ledger.csv
  │   └─ Write results to phase106_dryrun_execution.log
  │
  ├─ Track: Position updates
  ├─ Track: Simulated P&L
  └─ Track: Trade statistics
  
  (Repeat every hour until market close)
  
3:30 PM - Market closes
  ↓
Signal archival
  ↓
3:35 PM - EOD Learning (learn from today's paper trades)
  ↓
3:40 PM - Post-Close Audit
  ↓
4:00 PM - System shutdown
```

---

## What Gets Simulated (Phase 106)

### Order Placement (Simulated)
```
Order Type: MARKET (as per config)
Broker: Angel One (simulated)
Product: INTRADAY
Quantity: 1 lot per trade (configurable)
Time: Real market time
```

### Fill Price Simulation
```python
# From system3_phase106_dryrun_execution_bridge.py

fill_price = entry_price * (1 + slippage)

# Where slippage = random(-0.001, +0.001)
# = -0.1% to +0.1% (realistic market slippage)
```

### Position Tracking
- Buy/Sell orders tracked in `storage/live/live_orders_ledger.csv`
- Filled orders update position status
- P&L calculated: (fill_price - entry_price) * quantity

### Logging
- Execution log: `logs/phase106_dryrun_execution.log`
- Ledger updates: `storage/live/live_orders_ledger.csv`
- Daily summary: `DAILY_PAPER_TRADING_SUMMARY.md` (if enabled)

---

## File Structure for Paper Trading

```
storage/
├── live/
│   ├── angel_index_ai_signals.csv          ← Real signal generation
│   ├── live_orders_ledger.csv              ← Simulated order tracking
│   └── curated_signals_*.csv               ← Curated signal data
│
├── meta/
│   └── system3_live_thresholds.json        ← Threshold configuration
│
└── logs/
    └── phase106_dryrun_execution.log       ← Paper trading execution log

core/
├── engine/
│   ├── system3_phase106_dryrun_execution_bridge.py    ← Paper trading engine
│   └── system3_phase107_live_execution_engine.py      ← SKIPPED (never runs)
│
└── validation/
    └── pre_market_signal_dryrun.py         ← Pre-market paper trade test
```

---

## Safety Mechanisms

### 1. Hard Stop on Startup
```python
# system3_autorun_master.py lines 155-195

def enforce_safety_checks() -> bool:
    if LIVE_TRADING_ENABLED:  # Must be False
        logger.error("LIVE_TRADING_ENABLED is True - ABORTING")
        return False
    
    if USE_LIVE_EXECUTION_ENGINE:  # Must be False
        logger.error("USE_LIVE_EXECUTION_ENGINE is True - ABORTING")
        return False
    
    return True  # OK to continue with paper trading
```

### 2. Phase-Level Guards
- Phase 106 only runs if `USE_LIVE_EXECUTION_ENGINE = False` ✅
- Phase 107 only runs if `USE_LIVE_EXECUTION_ENGINE = True` (currently False)
- Mutual exclusion: Never both execute in same session

### 3. Watchdog Monitoring
- Separate monitoring process tracks main master
- Can restart if needed
- Logs all transitions

---

## Example: What Happens When You Start

### Command
```powershell
cd C:\Genesis_System3
.\START_AUTORUN_AND_WATCHDOG.bat
```

### Output (First 2 minutes)
```
[11:30:45] Starting System3 Autorun Master
[11:30:50] Pre-Market Check 1: Validate Live Thresholds ✓
[11:30:80] Pre-Market Check 2: Pre-Market Signal Dry-Run ✓
[11:31:20] Pre-Market Check 3: Signal Engine Self-Test ✓
[11:31:25] ============================================
[11:31:25] SAFETY ENFORCEMENT CHECK
[11:31:25] LIVE_TRADING_ENABLED: False ✓
[11:31:25] USE_LIVE_EXECUTION_ENGINE: False ✓
[11:31:25] ✓ All safety checks passed - DRY-RUN mode confirmed
[11:31:25] ============================================
[11:31:30] Waiting for market open (09:15)...
```

### If Current Time is 10:00 AM (Market Open)
```
[10:00:00] Market hours detected (09:15-15:30)
[10:00:05] Running OP Cycle (Signal Generation)
[10:00:35] Phase 106: DRY-RUN Execution
[10:00:40]   Reading signals from: storage/live/angel_index_ai_signals.csv
[10:00:42]   Orders to process: 5
[10:00:43]   Simulating fill prices (realistic slippage)
[10:00:50]   Updating ledger: live_orders_ledger.csv
[10:00:55]   ✓ DRY-RUN Execution Complete (5 orders filled)
[10:00:55]   LOG: logs/phase106_dryrun_execution.log
[10:01:00] Hourly OP cycle completed successfully
```

---

## How to Monitor Paper Trading

### 1. Watch Live Execution Log
```powershell
# In PowerShell
Get-Content logs\phase106_dryrun_execution.log -Tail 50 -Wait

# Or check file modification
ls logs\phase106_dryrun_execution.log -File | Select LastWriteTime, Length
```

### 2. Check Order Ledger
```powershell
# View simulated orders
Import-Csv storage/live/live_orders_ledger.csv | Format-Table
```

### 3. Monitor System3 Master Log
```powershell
Get-Content logs\system3_master_*.log -Tail 100
```

### 4. Inspect Daily Report
- File: `storage/ultra/DAILY_PAPER_TRADING_SUMMARY.md`
- Updated after market close
- Shows all simulated trades and P&L

---

## Key Differences: Paper vs Real Trading

| Feature | Paper Trading | Real Trading |
|---------|---|---|
| **Configuration** | `LIVE_TRADING_ENABLED = False` | `LIVE_TRADING_ENABLED = True` |
| **Phase Used** | Phase 106 (DRY-RUN) | Phase 107 (LIVE) |
| **Capital at Risk** | ❌ None | ⚠️ YES |
| **Broker Orders** | Simulated only | Actually placed |
| **Fill Prices** | Simulated (±0.1%) | Real market fills |
| **Execution Speed** | Instant (simulated) | Real broker latency |
| **P&L Tracking** | Simulated | Real account balance |
| **Order Status** | FILLED (simulated) | EXECUTED (broker confirmed) |
| **Market Hours** | Always runs during market | Always runs during market |

---

## Switching to Real Trading (When Ready)

### ⚠️ Prerequisites
1. Extensive testing with paper trading
2. Validate strategy in multiple market conditions
3. Confirm all safety checks understand
4. Ensure capital risk management in place

### Steps to Enable Live Trading
1. **Read the entire config file** carefully:
   ```powershell
   notepad config/live_trade_config.py
   ```

2. **Update two flags**:
   ```python
   LIVE_TRADING_ENABLED = True           # Enable real trading
   USE_LIVE_EXECUTION_ENGINE = True      # Run Phase 107 instead of Phase 106
   ```

3. **Update automation config**:
   ```python
   # core/engine/angel_automation_config.py
   auto_execute_trades = True
   ```

4. **Verify ultra safety**:
   ```python
   # core/config/system3_ultra_safety.json
   "AUTO_EXECUTE_TRADES": true
   ```

5. **Run startup verification**:
   ```powershell
   python system3_startup_verification.py
   ```

6. **Confirm the output**:
   ```
   ❌ CRITICAL: LIVE_TRADING_ENABLED is True
   ❌ CRITICAL: USE_LIVE_EXECUTION_ENGINE is True
   ⚠️  LIVE TRADING ENABLED - SYSTEM READY FOR REAL TRADING
   ```

7. **Run the BAT file**:
   ```powershell
   .\START_AUTORUN_AND_WATCHDOG.bat
   ```

---

## Important Notes

### ✅ Safe to Run During Market Hours
- Paper trading is designed for live market data
- No capital risk whatsoever
- All trades are simulated
- Realistic slippage and fill prices

### ⚠️ Understanding Paper Trading Differences
1. **Slippage**: Simulated ±0.1% (real trades may vary ±0.2-0.5%)
2. **Liquidity**: Assumes immediate fill (real orders may be partial)
3. **Speed**: Instant execution (real broker has latency)
4. **Costs**: No brokerage/taxes (real account has these)

### 🔍 Validation Before Real Trading
- Track P&L accuracy for 5-10 trading days
- Validate position limits are respected
- Confirm signal quality on real market data
- Test stop-loss and profit-taking behavior

---

## Configuration Reference

### Paper Trading (Current)
```python
LIVE_TRADING_ENABLED = False
USE_LIVE_EXECUTION_ENGINE = False
```
✅ Safe for any time  
✅ Safe during market hours  
✅ Safe for extended testing  

### Live Trading (Do NOT enable without testing)
```python
LIVE_TRADING_ENABLED = True
USE_LIVE_EXECUTION_ENGINE = True
```
⚠️ Real capital at risk  
⚠️ Requires thorough validation  
⚠️ Requires understanding of all limits  

---

## Support & Troubleshooting

### Issue: Phase 106 not executing
**Check**: Is `USE_LIVE_EXECUTION_ENGINE = False`? (Should be)
**Check**: Are we in market hours? (9:15 AM - 3:30 PM)
**Check**: `logs/phase106_dryrun_execution.log` for errors

### Issue: No signals being generated
**Check**: Is live signal source active? (`storage/live/angel_index_ai_signals.csv`)
**Check**: Are thresholds configured? (`storage/meta/system3_live_thresholds.json`)
**Check**: Run pre-market check manually to diagnose

### Issue: Orders not being simulated
**Check**: Is ledger file present? (`storage/live/live_orders_ledger.csv`)
**Check**: Are there PLANNED orders in ledger?
**Check**: Check Phase 106 execution log for specific errors

---

## Summary

Your System3 is now configured to:
- ✅ Generate signals from real live market data during 9:15 AM - 3:30 PM
- ✅ Simulate trade execution with realistic fill prices
- ✅ Track positions and calculate paper P&L
- ✅ Run safely without any real capital at risk
- ✅ Log all activities for analysis and validation

**You can run this during actual market hours to validate your strategy before enabling real trading.**
