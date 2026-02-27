# System3 Paper Trading & Mode Activation Guide

## Overview
System3 uses **DRY-RUN mode (paper trading) by default**. The system is engineered with **explicit safety mechanisms** to prevent accidental live trading. Mode activation is controlled through centralized configuration flags.

---

## Control Mechanism

### Primary Configuration File
**Location**: `config/live_trade_config.py`

This is the **single source of truth** for trading mode. The file contains three critical flags:

```python
# Flag 1: Master Kill-Switch (MUST REMAIN FALSE)
LIVE_TRADING_ENABLED = False  

# Flag 2: Execution Engine Mode (MUST REMAIN FALSE)
USE_LIVE_EXECUTION_ENGINE = False  

# Flag 3: Automation Override (In core/engine/angel_automation_config.py)
auto_execute_trades = False
```

### Default State
✅ **System starts in DRY-RUN (paper trading) mode**
- All signals are generated but NOT executed
- All trades are simulated only
- No real capital is at risk

---

## Activation Timeline When Running BAT File

### Step 1: Pre-Market Validation (First 3 checks)
When you run `START_AUTORUN_AND_WATCHDOG.bat`:

```batch
REM Check 1: Validate Live Thresholds (30 sec)
python core\validation\validate_live_thresholds.py

REM Check 2: Pre-Market Signal Dry-Run (60 sec)
python core\validation\pre_market_signal_dryrun.py

REM Check 3: Signal Engine Self-Test (45 sec)
python core\engine\system3_signal_engine_self_test.py
```

**What happens**: These scripts test the entire signal pipeline WITHOUT executing any trades.

### Step 2: Safety Enforcement (Startup Verification)
After pre-market checks pass, `system3_startup_verification.py` verifies:

```
✅ LIVE_TRADING_ENABLED: False (DRY-RUN mode)
✅ USE_LIVE_EXECUTION_ENGINE: False (DRY-RUN mode)
```

**If either flag is True**: ❌ System ABORTS with critical error (won't start)

### Step 3: Autorun Master Startup
When master starts (`system3_autorun_master.py` lines 155-195):

```python
def enforce_safety_checks() -> bool:
    """Hard safety enforcement - verify DRY-RUN mode."""
    
    # Check LIVE_TRADING_ENABLED (line 158)
    if LIVE_TRADING_ENABLED:
        errors.append("LIVE_TRADING_ENABLED is True (must be False)")
        return False  # ABORT
    
    # Check USE_LIVE_EXECUTION_ENGINE (line 160)
    if USE_LIVE_EXECUTION_ENGINE:
        errors.append("USE_LIVE_EXECUTION_ENGINE is True (must be False)")
        return False  # ABORT
    
    # Check auto_execute_trades (line 170)
    if AUTOMATION_CONFIG.auto_execute_trades:
        errors.append("auto_execute_trades is True (must be False)")
        return False  # ABORT
    
    # If all checks pass:
    logger.info("✓ All safety checks passed - DRY-RUN mode confirmed")
    return True
```

**Result**: Master only continues if **all three flags are False**

### Step 4: Phase Execution (201-310)
Phases execute in DRY-RUN mode:
- Phases 201-206: Infrastructure & connectivity checks
- Phases 209-230: Signal generation & analysis (simulation only)
- Phases 301-310: Reporting & logging

**No real trades execute during phases**

### Step 5: Ready-to-Trade Check (Phase 196)
`system3_phase196_dry_run_readiness.py` explicitly verifies:

```python
checks["dry_run_only"] = master_config.get("dry_run", True) is True
```

If DRY-RUN is False, this phase returns "NO" for readiness.

---

## How to Enable Live Trading

### ⚠️ CRITICAL: Live Trading Activation

To enable live trading, you must:

1. **Edit** `config/live_trade_config.py`
2. **Change** `LIVE_TRADING_ENABLED = False` to `LIVE_TRADING_ENABLED = True`
3. **Verify** both flags are set:
   ```python
   LIVE_TRADING_ENABLED = True          # Enable live trading
   USE_LIVE_EXECUTION_ENGINE = True     # Use Phase 107 (LIVE) instead of Phase 106 (DRY)
   ```

### Additional Safety Checks Before Enabling

The system will still verify:
- `core/engine/angel_automation_config.py`: Set `auto_execute_trades = True`
- `core/config/system3_ultra_safety.json`: Set `AUTO_EXECUTE_TRADES = True`
- Phase 196 confirms `"dry_run": False`

### What Happens When Live Trading is Enabled

When both flags are True:
- **Phase 106** (DRY-RUN simulation) is SKIPPED
- **Phase 107** (LIVE EXECUTION) RUNS and executes real trades
- Real capital is at risk
- Watchdog monitoring is ACTIVE for risk management

---

## Default Mode Verification

To verify current mode without starting the system:

```powershell
# From Genesis_System3 directory
cd C:\Genesis_System3
python -c "from config.live_trade_config import LIVE_TRADING_ENABLED, USE_LIVE_EXECUTION_ENGINE; print(f'LIVE: {LIVE_TRADING_ENABLED}, EXEC: {USE_LIVE_EXECUTION_ENGINE}')"
```

Expected output for paper trading mode:
```
LIVE: False, EXEC: False
```

---

## DRY-RUN vs LIVE Comparison

| Aspect | DRY-RUN (Paper) | LIVE (Real) |
|--------|---|---|
| **Config Flag** | `LIVE_TRADING_ENABLED = False` | `LIVE_TRADING_ENABLED = True` |
| **Phase 106/107** | 106 (Simulation) | 107 (Execution) |
| **Real Capital** | NOT at risk | AT RISK ⚠️ |
| **Trade Execution** | Logged only, not executed | Actually executed |
| **Default State** | ✅ Yes | ❌ No |
| **Activation** | Automatic | Manual config change |
| **Startup Check** | PASS (signals "continue") | FAIL (signals "safe mode verified") |

---

## Safety Architecture

### Multi-Layer Safety System

1. **Layer 1: Configuration File** (`config/live_trade_config.py`)
   - Central control point
   - Comments explain risks
   - Default is safe

2. **Layer 2: Startup Verification** (`system3_startup_verification.py`)
   - Checks flags before pre-market runs
   - Reports DRY-RUN status to user
   - Refuses to start if unsafe

3. **Layer 3: Master Enforcement** (`system3_autorun_master.py` lines 155-195)
   - Hard check before phase 200
   - Aborts if any flag is unsafe
   - Logs proof of safety check

4. **Layer 4: Phase-Level Guards** (Individual phase files)
   - Phase 106 (DRY) only when `USE_LIVE_EXECUTION_ENGINE = False`
   - Phase 107 (LIVE) only when `USE_LIVE_EXECUTION_ENGINE = True`
   - Mutual exclusion (never both execute)

5. **Layer 5: Watchdog Monitoring** (`system3_watchdog.py`)
   - Monitors master in separate process
   - Can restart if needed
   - Active in both modes

---

## Timeline: BAT Execution

```
START_AUTORUN_AND_WATCHDOG.bat runs
    ↓
[PRE-MARKET CHECKS] (2-3 minutes)
    ├─ validate_live_thresholds.py       [~30 sec]
    ├─ pre_market_signal_dryrun.py        [~60 sec]
    └─ system3_signal_engine_self_test.py [~45 sec]
    ↓ (All checks PASS)
[STARTUP VERIFICATION] (5 seconds)
    ├─ ✅ LIVE_TRADING_ENABLED: False ← DRY-RUN mode confirmed
    ├─ ✅ USE_LIVE_EXECUTION_ENGINE: False ← Paper trading
    └─ ✅ "READY TO START"
    ↓
[WATCHDOG SPAWNED] (in new window)
    └─ monitors system3_autorun_master.py
    ↓
[AUTORUN MASTER STARTED] (in current window)
    ├─ enforce_safety_checks() [CHECKS FLAGS AGAIN]
    │  ├─ LIVE_TRADING_ENABLED must be False ← VERIFIED
    │  ├─ USE_LIVE_EXECUTION_ENGINE must be False ← VERIFIED
    │  └─ auto_execute_trades must be False ← VERIFIED
    │  → "✓ All safety checks passed - DRY-RUN mode confirmed"
    │
    ├─ Phase 201-206: Infrastructure (2 min)
    ├─ Phase 209-230: Signal generation (5 min) [SIMULATION ONLY]
    ├─ Phase 106: DRY-RUN executor (3 min) [EXECUTES IN MEMORY, NOT REAL]
    ├─ Phase 301-310: Reporting (2 min)
    │
    └─ Waits for next market open (if pre-market run)
```

---

## Key Files Controlling Mode

| File | Purpose | Key Setting |
|------|---------|-------------|
| `config/live_trade_config.py` | Master config | `LIVE_TRADING_ENABLED` |
| `system3_autorun_master.py` | Startup enforcer | `enforce_safety_checks()` |
| `system3_startup_verification.py` | Pre-run verifier | Flag validation before start |
| `system3_phase196_dry_run_readiness.py` | Readiness reporter | `"dry_run": True/False` |
| `core/engine/system3_phase106_dryrun_executor.py` | Paper trading | Executes when EXEC_ENGINE = False |
| `core/engine/system3_phase107_live_executor.py` | Live trading | Executes when EXEC_ENGINE = True |
| `core/engine/angel_automation_config.py` | Automation controls | `auto_execute_trades` |

---

## Important Notes

### ⚠️ Never Modify These at Runtime
- Do NOT change config flags while master is running
- Do NOT manually toggle `LIVE_TRADING_ENABLED` during market hours
- Do NOT edit configs without understanding implications

### ✅ Safe Operations
- Run pre-market checks anytime (they are always safe)
- View logs: `storage/logs/system3_master_*.log`
- Monitor: Logs update every 30 seconds from watchdog
- Check mode: `START_AUTORUN_AND_WATCHDOG.bat` will print mode in first few lines

### 🔍 Verification Before Going Live
1. Ensure `config/live_trade_config.py` is in your favorite editor
2. Read through all comments in the file
3. Understand each trade limit setting
4. Only then change flags
5. Run `system3_startup_verification.py` manually to confirm

---

## Summary

**Current State**: System3 is set to **DRY-RUN (paper trading) mode**

**When you run the BAT file**:
1. Pre-market validation tests entire system (safely)
2. Master checks `LIVE_TRADING_ENABLED` flag (currently False)
3. System confirms DRY-RUN mode
4. Phases 201-310 execute with simulation only
5. No real trades happen
6. System waits for market open

**To switch to live trading**:
- Edit `config/live_trade_config.py`
- Set `LIVE_TRADING_ENABLED = True` and `USE_LIVE_EXECUTION_ENGINE = True`
- Master will enforce this before execution
- Real trades will execute in Phase 107

**Safety is guaranteed** by multi-layer enforcement at startup, phase-level, and watchdog levels.
