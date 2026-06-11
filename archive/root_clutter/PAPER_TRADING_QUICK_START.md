# System3 Paper Trading - Quick Reference

## Current Status
✅ **Paper Trading is ENABLED** - You can run this during real market hours

## What This Means
- Signals are generated from **real live market data**
- Trades are **simulated** (not real)
- **No capital at risk** whatsoever
- Runs every hour during **9:15 AM - 3:30 PM** market hours

## How to Run

### Start Paper Trading Session
```powershell
cd C:\Genesis_System3
.\START_AUTORUN_AND_WATCHDOG.bat
```

**What it does:**
1. Validates system readiness (3 pre-market checks)
2. Confirms paper trading mode is active
3. Launches watchdog monitoring
4. Waits for market open or starts if market is open
5. Every hour: Generates signals → Simulates trades → Logs results

### Stop Anytime
- Press `Ctrl+C` in the main window
- System gracefully shuts down at 4:00 PM anyway

## Monitoring While Running

### Watch Execution Log (Real-Time)
```powershell
Get-Content logs\phase106_dryrun_execution.log -Tail 50 -Wait
```

### Check Simulated Orders
```powershell
Import-Csv storage/live/live_orders_ledger.csv | Format-Table
```

### View Master Log
```powershell
Get-Content logs\system3_master_*.log -Tail 100
```

## When It Runs

| Time | Action |
|------|--------|
| **9:15 AM** | Market opens → System becomes active |
| **Every hour** | Signal generation + Paper trade simulation |
| **3:30 PM** | Signal archival |
| **3:35 PM** | EOD Learning (learns from paper trades) |
| **3:40 PM** | Post-Close Audit |
| **4:00 PM** | Automatic shutdown |

## Safety Guarantees

✅ No real orders sent to broker  
✅ No real capital at risk  
✅ System aborts if safety flags are wrong  
✅ Watchdog monitors for issues  
✅ All activities logged  

## Checking Current Mode

```powershell
python -c "from config.live_trade_config import LIVE_TRADING_ENABLED, USE_LIVE_EXECUTION_ENGINE; print(f'LIVE={LIVE_TRADING_ENABLED}, EXEC_ENGINE={USE_LIVE_EXECUTION_ENGINE}')"
```

Expected output:
```
LIVE=False, EXEC_ENGINE=False
```

If either shows `True` → System will NOT START (safety protection)

## Understanding Paper Trading Behavior

| Aspect | What Happens |
|--------|---|
| **Signal Generation** | Uses real market data |
| **Order Placement** | Simulated only |
| **Fill Price** | Simulated ±0.1% slippage |
| **Position Tracking** | Tracked in live_orders_ledger.csv |
| **P&L Calculation** | Calculated (simulated gains/losses) |
| **Broker Integration** | NOT connected (safe) |
| **Risk** | ZERO - it's all simulated |

## Common Questions

### Q: Can this lose real money?
**A:** No. Everything is simulated. Zero capital at risk.

### Q: Does it connect to my Angel One account?
**A:** No. It operates in complete isolation.

### Q: Can I run this during work hours?
**A:** Yes! It's designed for 9:15 AM - 3:30 PM market hours.

### Q: What if there's an error?
**A:** Check logs in `logs/` folder or run pre-market check manually:
```powershell
python core/validation/pre_market_signal_dryrun.py
```

### Q: How long until I can switch to real trading?
**A:** After 5-10 trading days of paper trading validation.

### Q: What happens if I forget to stop it?
**A:** System automatically shuts down at 4:00 PM.

## Files to Monitor

| File | Purpose | Location |
|------|---------|----------|
| Phase 106 Log | Simulated trade details | `logs/phase106_dryrun_execution.log` |
| Order Ledger | Simulated orders | `storage/live/live_orders_ledger.csv` |
| Master Log | Overall system status | `logs/system3_master_*.log` |
| Daily Summary | Paper trading P&L | `storage/ultra/DAILY_PAPER_TRADING_SUMMARY.md` |

## Configuration Files

- **Main**: `config/live_trade_config.py`
  - `LIVE_TRADING_ENABLED = False` ✓
  - `USE_LIVE_EXECUTION_ENGINE = False` ✓

## Important: DO NOT CHANGE
- ❌ Do NOT set `LIVE_TRADING_ENABLED = True` unless ready for real trading
- ❌ Do NOT set `USE_LIVE_EXECUTION_ENGINE = True` unless ready for real trading
- ❌ Do NOT modify flags while system is running

## Next Steps

1. **Run paper trading** during market hours
2. **Monitor** `logs/phase106_dryrun_execution.log`
3. **Track** simulated P&L for 5-10 days
4. **Validate** signal quality and position management
5. **When confident** → Then enable real trading (only if desired)

---

**Your system is ready for paper trading on live market hours!**
