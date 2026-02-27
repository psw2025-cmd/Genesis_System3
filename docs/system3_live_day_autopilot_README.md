# System3 Live Day Autopilot

**Single-button full-day autopilot for System3 (AngelOne ONLY, DRY-RUN ONLY)**

---

## Overview

The `system3_live_day_autopilot.py` script orchestrates a complete trading day automatically:

- **OP1**: Pre-market checks and diagnostics
- **OP2**: Live DRY-RUN AngelOne signal loop
- **OP3**: Intraday monitors (periodic)
- **OP4**: End-of-day processing (PnL, learning, reports)

All operations are **DRY-RUN ONLY** - no real trading functions are ever triggered.

---

## Safety Rules

### Hard Safety Enforcement

The script enforces strict safety checks before starting:

1. **LIVE_TRADING_ENABLED** must be `False`
2. **USE_LIVE_EXECUTION_ENGINE** must be `False`
3. **AUTOMATION_CONFIG.auto_execute_trades** must be `False`
4. **Ultra safety AUTO_EXECUTE_TRADES** must be `False`

If any of these are `True`, the script will **ABORT** with an error message.

### No Real Orders

The script **never** calls any function that can send a real AngelOne order. All execution is DRY-RUN only.

---

## How to Run

### Option 1: Batch File (Recommended)

Double-click or run:
```bash
run_live_day_autopilot.bat
```

### Option 2: Python Direct

```bash
# Activate venv first
venv\Scripts\activate

# Run script
python system3_live_day_autopilot.py
```

---

## Operational Phases

### OP1: Pre-Market Checks

Runs before market opens:

1. **Market Warmup Scanner** (`angel_market_warmup_scanner`)
   - Validates directory structure
   - Checks model presence (5 models)
   - Validates key files
   - Checks configuration safety

2. **Pre-Market Diagnostic** (`angel_monday_diagnostic`)
   - Comprehensive pre-market diagnostics
   - Model validation
   - Configuration checks
   - Ultra-Mode status

3. **Environment Guard** (`system3_phase43_env_guard`)
   - Environment consistency checks
   - Broker connectivity validation

**Expected Output**: All checks should show `PASS` or `OK` status.

---

### OP2: Live Session (DRY-RUN Loop)

Runs continuously during market hours:

- **Live AI Signal Generation**: Every 30 seconds
  - Builds full snapshot from AngelOne broker
  - Generates AI signals using trained models
  - Creates trade plans (DRY-RUN only)
  - Logs signals to CSV

- **Periodic PnL Simulation**: If enabled in automation config
  - Runs every N snapshots (configurable)
  - Simulates PnL for trade plans

- **Intraday Monitors**: Every 10 snapshots
  - Decision Auditor (Phase 35)
  - Policy & Risk Monitor (Phase 37)
  - Governance Summary (Phase 38)

**To Stop**: Press `Ctrl+C` to stop the live session and proceed to EOD processing.

---

### OP3: Intraday Monitors

Runs automatically every 10 snapshots during live session:

1. **Decision Auditor (Phase 35)**
   - Audits recent trading decisions
   - Validates decision quality
   - Output: `storage/ultra/phase35_audit_*.md`

2. **Policy & Risk Monitor (Phase 37)**
   - Monitors policy compliance
   - Risk assessment
   - Output: `storage/ultra/phase37_policy_risk_*.md`

3. **Governance Summary (Phase 38)**
   - Governance snapshot
   - Quick "all green" status
   - Output: `storage/ultra/phase38_governance_summary.md`

---

### OP4: End-of-Day Processing

Runs after live session ends (Ctrl+C or market close):

1. **PnL Simulation** (`angel_pnl_simulator`)
   - Simulates PnL for all trade plans
   - Output: `storage/live/angel_index_ai_pnl_log.csv`

2. **Daily PnL Summary** (`angel_daily_pnl_summary`)
   - Summarizes daily PnL by underlying
   - Trade count, win rate, exit reasons
   - Console output + CSV

3. **Daily Learning Report** (`angel_daily_learning_report`)
   - End-of-day learning summary
   - Outcome analysis
   - Output: `storage/reports/angel_daily_learning_report_YYYYMMDD.txt`

4. **Daily Auto Reports** (`angel_daily_auto_reports`)
   - Daily learning report
   - Rolling 7-day dashboard
   - Quick summary
   - Output: `storage/reports/`

---

## Logging

All operations are logged to:
```
logs/live_day_autopilot_YYYYMMDD.log
```

The log file includes:
- Safety check results
- Pre-market check results
- Live session snapshots
- Intraday monitor results
- End-of-day processing results
- Errors and warnings

---

## Example Expected Log Snippet

```
2025-11-30 09:00:00 [INFO] ======================================================================
2025-11-30 09:00:00 [INFO] SYSTEM3 LIVE DAY AUTOPILOT
2025-11-30 09:00:00 [INFO] ======================================================================
2025-11-30 09:00:00 [INFO] Started at: 2025-11-30 09:00:00
2025-11-30 09:00:00 [INFO] Log file: C:\Genesis_System3\logs\live_day_autopilot_20251130.log
2025-11-30 09:00:00 [INFO] 
2025-11-30 09:00:00 [INFO] ======================================================================
2025-11-30 09:00:00 [INFO] SAFETY ENFORCEMENT CHECK
2025-11-30 09:00:00 [INFO] ======================================================================
2025-11-30 09:00:00 [INFO] LIVE_TRADING_ENABLED: False
2025-11-30 09:00:00 [INFO] USE_LIVE_EXECUTION_ENGINE: False
2025-11-30 09:00:00 [INFO] auto_execute_trades: False
2025-11-30 09:00:00 [INFO] ======================================================================
2025-11-30 09:00:00 [INFO] ✓ All safety checks passed - DRY-RUN mode confirmed
2025-11-30 09:00:00 [INFO] ======================================================================
2025-11-30 09:00:01 [INFO] 
2025-11-30 09:00:01 [INFO] ======================================================================
2025-11-30 09:00:01 [INFO] OP1: PRE-MARKET CHECKS
2025-11-30 09:00:01 [INFO] ======================================================================
2025-11-30 09:00:01 [INFO] [OP1.1] Running Market Warmup Scanner...
2025-11-30 09:00:05 [INFO] [OK] Market warmup scanner: PASS
...
2025-11-30 09:15:00 [INFO] ======================================================================
2025-11-30 09:15:00 [INFO] Starting OP2: Live Session
2025-11-30 09:15:00 [INFO] ======================================================================
2025-11-30 09:15:00 [INFO] [INFO] Press Ctrl+C to stop the live session and proceed to EOD processing
2025-11-30 09:15:01 [INFO] Broker initialized.
2025-11-30 09:15:01 [INFO] 
2025-11-30 09:15:31 [INFO] [09:15:31] Snapshot #1...
2025-11-30 09:15:31 [INFO]   -> Signals generated
2025-11-30 09:15:31 [INFO] Sleeping for 30 seconds...
...
```

---

## Internal Functions/Modules Used

### Pre-Market (OP1)
- `core.engine.angel_market_warmup_scanner.scan_market_warmup()`
- `core.engine.angel_monday_diagnostic.run_pre_market_diagnostic()`
- `core.engine.system3_phase43_env_guard.run_phase43()`

### Live Session (OP2)
- `core.brokers.angel_one.broker.AngelOneBroker()`
- `core.engine.angel_options_watch_loop._build_full_snapshot()`
- `core.engine.angel_live_ai_signals.run_once_with_snapshot()`
- `core.engine.angel_pnl_simulator.run_pnl_simulation()` (periodic)

### Intraday Monitors (OP3)
- `core.engine.system3_phase35_ultra_auditor.run_phase35_audit()`
- `core.engine.system3_phase37_policy_risk_monitor.run_phase37_policy_risk_dashboard()`
- `core.engine.system3_phase38_governance_summary.run_phase38_governance_summary()`

### End-of-Day (OP4)
- `core.engine.angel_pnl_simulator.run_pnl_simulation()`
- `core.engine.angel_daily_pnl_summary.main()`
- `core.engine.angel_daily_learning_report.generate_daily_learning_report()`
- `core.engine.angel_daily_auto_reports.generate_daily_auto_report()`

### Safety Checks
- `config.live_trade_config.LIVE_TRADING_ENABLED`
- `config.live_trade_config.USE_LIVE_EXECUTION_ENGINE`
- `core.engine.angel_automation_config.AUTOMATION_CONFIG`
- `core.engine.ultra_safety.load_ultra_safety()`

---

## Configuration

The script uses existing System3 configuration files:

- `config/live_trade_config.py` - Live trading flags
- `core/engine/angel_automation_config.py` - Automation settings
- `core/engine/ultra_safety.py` - Ultra mode safety

**No new configuration files are created or modified.**

---

## Troubleshooting

### Safety Check Fails

If safety checks fail, check:
1. `config/live_trade_config.py` - Ensure `LIVE_TRADING_ENABLED = False`
2. `core/engine/angel_automation_config.py` - Ensure `auto_execute_trades = False`
3. Ultra safety config - Ensure `AUTO_EXECUTE_TRADES = False`

### Broker Connection Fails

- Check AngelOne API credentials
- Verify network connectivity
- Check broker initialization in logs

### No Signals Generated

- Check if market is open
- Verify models are loaded (5 models expected)
- Check snapshot data availability

---

## Notes

- **AngelOne ONLY**: Binance/multi-broker modules are ignored
- **DRY-RUN ONLY**: No real orders are ever sent
- **Automatic**: All phases run automatically in sequence
- **Interruptible**: Press Ctrl+C to stop live session and proceed to EOD
- **Logged**: All operations logged to daily log file

---

**End of Documentation**

