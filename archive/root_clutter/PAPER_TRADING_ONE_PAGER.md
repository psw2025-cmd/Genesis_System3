# Paper Trading - One-Pager Quick Reference

## Your System Status

✅ **Paper trading is ACTIVE and ready to run during live market hours**

---

## What This Means

| Aspect | Status |
|--------|--------|
| **Signals** | Generated from REAL market data (9:15 AM - 3:30 PM) |
| **Trade Execution** | SIMULATED (not real) via Phase 106 |
| **Capital at Risk** | ZERO |
| **Broker Connection** | NOT connected (completely safe) |
| **Monitoring** | All trades logged for analysis |
| **Auto-Shutdown** | 4:00 PM every trading day |

---

## How to Start

```powershell
# 1. Verify configuration (anytime)
python system3_startup_verification.py

# 2. Start trading (9:15 AM - 3:30 PM only)
.\START_AUTORUN_AND_WATCHDOG.bat

# 3. Monitor (in another PowerShell window)
Get-Content logs\phase106_dryrun_execution.log -Tail 50 -Wait
```

---

## What Happens

| Time | Action |
|------|--------|
| 9:15 AM | Market opens → System becomes active |
| Every 60 min | Generate signals → Simulate trades → Log results |
| 3:30 PM | Archive signals |
| 3:35 PM | EOD Learning |
| 4:00 PM | Auto shutdown |

---

## Key Configuration

```python
# config/live_trade_config.py

LIVE_TRADING_ENABLED = False           # ✓ No real capital
USE_LIVE_EXECUTION_ENGINE = False      # ✓ Phase 106 (paper)
```

**DO NOT CHANGE** unless switching to real trading (not recommended yet)

---

## Files to Monitor

```
logs/phase106_dryrun_execution.log      ← Paper trade details
storage/live/live_orders_ledger.csv     ← Simulated orders
logs/system3_master_*.log               ← System health
```

---

## Safety Checks

✅ Config flags verified at startup  
✅ Master enforces safety before each cycle  
✅ Phase 106 cannot send real orders  
✅ Phase 107 (live) is completely skipped  
✅ Watchdog monitors system health  

---

## Quick Validation

```powershell
# This should show LIVE=False, EXEC=False
python -c "from config.live_trade_config import LIVE_TRADING_ENABLED, USE_LIVE_EXECUTION_ENGINE; print(f'{LIVE_TRADING_ENABLED},{USE_LIVE_EXECUTION_ENGINE}')"
```

Expected: `False,False` ✓

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| Won't start | `python system3_startup_verification.py` |
| No trades | Are we in market hours? (9:15-15:30) |
| Check config | Review `config/live_trade_config.py` |
| View logs | `Get-Content logs\system3_master_*.log -Tail 100` |

---

## Documentation Files

- **5-min read**: `PAPER_TRADING_QUICK_START.md`
- **10-min read**: `PAPER_TRADING_COMPLETE_SUMMARY.md`
- **30-min read**: `PAPER_TRADING_LIVE_MARKET_HOURS_GUIDE.md`
- **Pre-check**: `PAPER_TRADING_SETUP_VALIDATION.md`
- **Mode details**: `PAPER_TRADING_ACTIVATION_GUIDE.md`

---

## Remember

✅ Run during market hours (9:15 AM - 3:30 PM)  
✅ Monitor logs while running  
✅ Let it auto-shutdown at 4:00 PM  
❌ Don't change config while running  
❌ Don't enable real trading until thoroughly tested  

---

## Current Status

```
Config:  LIVE=False (no real capital)
Exec:    Phase 106 (paper trading)
Safety:  ✓ Confirmed
Ready:   ✓ Yes
```

**You're ready to trade! Use the BAT file during market hours.**
