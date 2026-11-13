# System3 Phases 101-130: Comprehensive Analysis & Review
**Document**: `system3_phases_101_130_angelone_full_auto_plan.md`  
**Analysis Date**: 2025-11-30  
**Status**: 📋 **ANALYSIS COMPLETE - READY FOR IMPLEMENTATION**

---

## Executive Summary

### Purpose
This plan defines **30 new phases (101-130)** that add **Dhan LIVE trading automation** to System3, specifically for **Mode 1 (Indian Market Only)**. The implementation is designed to be:

- ✅ **Safe & Layered**: Multiple safety checks and guards
- ✅ **Fully Configurable**: All real trading controlled by config flags
- ✅ **Additive Only**: No changes to existing Baseline/Ultra behavior
- ✅ **Conservative**: Initial real tests limited to 1 lot per trade

### Key Principles
1. **Baseline & Ultra MUST NOT change by default**
2. **All new modules are additive**
3. **Real trading only activates when explicit flags are ON**
4. **Initial real tests: 1 lot per trade only**

---

## Phase Group Overview

### Group 1: Live Trading Config & Local Order Ledger (101-105)
**Purpose**: Foundation layer for live trading infrastructure

| Phase | Name | Purpose | Key Outputs |
|-------|------|---------|-------------|
| **101** | Live Trading Config + Sanity Check | Central config layer + pre-market check script | `config/live_trade_config.py`, `storage/live/phase101_live_trade_config_snapshot.json` |
| **102** | Local Order Ledger Schema | Define canonical CSV ledger for all live trades | `storage/live/live_orders_ledger.csv` (with header) |
| **103** | Dhan Low-Level Order Wrapper | Abstract Dhan DhanHQ order placement (skeleton) | `core/broker/dhan_live_order_wrapper.py` (class skeleton) |
| **104** | Trade Plan → Local Order Construction | Convert trade plan CSV rows to ledger orders | Appended rows to `live_orders_ledger.csv` |
| **105** | Ledger Integrity Checker | Validate ledger sanity before execution | Validation dict, `logs/phase105_ledger_integrity_issues.log` |

**Dependencies**: None (foundation layer)

---

### Group 2: Dhan Execution Wrapper & Dry-Run Mirroring (106-110)
**Purpose**: Execution layer with dry-run capability

| Phase | Name | Purpose | Key Outputs |
|-------|------|---------|-------------|
| **106** | Live Execution DRY-RUN Bridge | Wire ledger to existing DRY RUN executor | Updated ledger (DRY_RUN_FILLED), `logs/phase106_dryrun_execution.log` |
| **107** | Dhan LIVE Execution | Actual real-order placement (guarded, OFF by default) | Updated ledger (SENT/FILLED), `logs/phase107_live_execution_engine.log` |
| **108** | Order Status Refresher | Pull order statuses from Angel and update ledger | Updated ledger statuses |
| **109** | Intraday Risk Guard | Enforce capital and drawdown limits | Risk check dict (OK/BLOCK) |
| **110** | Stop-Loss & Exit Rule Builder | Build conservative SL/TP rules per trade | `storage/live/phase110_exit_rules_pending.json` |

**Dependencies**: 
- Phase 103 (AngelLiveOrderWrapper)
- Phase 102 (Ledger schema)
- Existing DRY RUN executor

---

### Group 3: Live Signal → Trade → Order Flow (111-115)
**Purpose**: Session orchestration and control

| Phase | Name | Purpose | Key Outputs |
|-------|------|---------|-------------|
| **111** | Live Signal Session Orchestrator | Orchestrate phases 101, 102, 104, 105, 109 | Combined status dict |
| **112** | Session Loop Controller | One-shot loop controller (iterations=1 default) | `logs/phase112_session_loop.log` |
| **113** | Kill Switch Monitor | Monitor kill switch file | Status dict (OK/KILL) |
| **114** | Live Session Health Snapshot | Summarize session health | `storage/live/phase114_live_session_health.md` |
| **115** | Intraday Alert Summary | Generate text summary for alerts | `storage/live/phase115_intraday_alert_summary.txt` |

**Dependencies**: 
- Phases 101, 102, 104, 105, 109 (for Phase 111)
- Phase 106 or 107 (for Phase 112)
- Phase 109, 113 (for Phase 114)

---

### Group 4: Intraday Session Brain & Kill-Switch (116-120)
**Purpose**: Session management and safety

| Phase | Name | Purpose | Key Outputs |
|-------|------|---------|-------------|
| **116** | End-of-Session Auto Stop | Auto-stop at market close | `storage/live/kill_switch.json` |
| **117** | Live → Learning Bridge | Connect ledger to Real Outcome files | `storage/learning/live_trade_outcomes.csv` |
| **118** | Daily Live PnL Snapshot | Summarize daily PnL from ledger | `storage/live/phase118_daily_pnl_snapshot.md` |
| **119** | Safety Audit for Live Trading | Comprehensive safety check | `storage/live/phase119_live_safety_audit.md` |
| **120** | End-of-Day Live Summary Pack | Combine outputs from 114, 118, 119 | `storage/live/phase120_eod_live_summary_pack.md` |

**Dependencies**:
- Phase 114, 118, 119 (for Phase 120)
- Existing Real Outcome logging (for Phase 117)

---

### Group 5: Post-Trade Logging, PnL & Outcome Bridges (121-125)
**Status**: ⚠️ **RESERVED FOR FUTURE ENHANCEMENTS**

**Implementation**: Empty stubs with `status: "NOT_IMPLEMENTED"`

| Phase | Name | Status |
|-------|------|--------|
| **121-125** | Reserved | Stub modules only |

---

### Group 6: Control Panel Integration & Safety Reports (126-130)
**Status**: ⚠️ **STUBS FOR FUTURE MENU INTEGRATION**

**Implementation**: Stub modules with `status: "STUB"` for future `system3_ultra.py` menu integration

| Phase | Name | Status |
|-------|------|--------|
| **126-130** | Control Panel Stubs | Stub modules only |

---

## Critical Configuration File

### `config/live_trade_config.py`

**Purpose**: Central configuration for all live trading risk controls

**Key Settings**:
```python
LIVE_TRADING_ENABLED = False        # MUST remain False by default
MAX_LIVE_TRADES_PER_DAY = 10
MAX_LIVE_TRADES_PER_UNDERLYING = 3
MAX_RISK_PER_TRADE_RUPEES = 2000   # Adjustable later
DEFAULT_LOTS_PER_TRADE = 1

# Allowed underlyings for live auto
LIVE_ALLOWED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

# Angel-specific
ANGEL_PRODUCT_TYPE = "INTRADAY"
ANGEL_ORDER_VARIETY = "NORMAL"
ANGEL_ALLOWED_ORDER_TYPES = ["MARKET"]  # For phase 1 live trading
```

**Safety**: This is the **ONLY** place where real trading can be enabled. All phases check this flag.

---

## Order Ledger Schema

### `storage/live/live_orders_ledger.csv`

**Purpose**: Canonical ledger for all live trades

**Columns**:
```
local_order_id, timestamp, underlying, symbol, expiry, strike, option_type, side,
lots, qty, entry_price, target_price, stop_loss_price, status, broker_order_id,
broker_status, last_update_ts, pnl_absolute, pnl_percent, exit_price, exit_reason, notes
```

**Status Values**:
- `PLANNED` - Order created from trade plan, not sent
- `SENT` - Order sent to broker
- `PARTIAL` - Partially filled
- `FILLED` - Fully filled
- `CANCELLED` - Cancelled
- `REJECTED` - Rejected by broker
- `EXPIRED` - Expired
- `ERROR` - Error state

**Safety Rules**:
- Never truncate or overwrite existing rows
- Always append new rows
- Header verification before operations

---

## Dhan Order Wrapper

### `core/broker/dhan_live_order_wrapper.py`

**Purpose**: Abstract Dhan DhanHQ order placement

**Class Structure**:
```python
class AngelLiveOrderWrapper:
    def __init__(self, smart_connect=None, logger=None)
    def place_market_order(self, *, symbol, qty, side, product_type, variety) -> dict
    def cancel_order(self, broker_order_id: str) -> dict
    def get_order_status(self, broker_order_id: str) -> dict
```

**Current Implementation**: 
- **Skeleton only** - No real API calls
- Returns `"status": "ERROR", "error": "NOT_IMPLEMENTED"` or `"DRY_RUN"`
- Real DhanHQ integration to be added later by Pritam

**Safety**: This is the **ONLY** place where real broker API calls will be made. All other phases use this wrapper.

---

## Safety Mechanisms

### 1. Config-Based Safety
- `LIVE_TRADING_ENABLED = False` by default
- All phases check this flag before any real operations
- Phase 107 explicitly aborts if flag is False

### 2. Risk Guards
- **Phase 109**: Intraday Risk Guard
  - Enforces `MAX_LIVE_TRADES_PER_DAY`
  - Enforces `MAX_LIVE_TRADES_PER_UNDERLYING`
  - Enforces `MAX_DAILY_DRAWDOWN_RUPEES`
  - Returns `status: "BLOCK"` if limits exceeded

### 3. Kill Switch
- **Phase 113**: Kill Switch Monitor
  - Reads `storage/live/kill_switch.json`
  - If `"kill": true`, returns `status: "KILL"`
  - Used by Phase 112 to abort execution

### 4. End-of-Session Auto Stop
- **Phase 116**: End-of-Session Auto Stop
  - Automatically sets kill switch at market close (15:30)
  - Prevents trading after market hours

### 5. Ledger Integrity
- **Phase 105**: Ledger Integrity Checker
  - Validates all ledger rows before execution
  - Checks for negative qty, missing fields, invalid statuses
  - Logs issues to `logs/phase105_ledger_integrity_issues.log`

### 6. Dry-Run First
- **Phase 106**: DRY-RUN Bridge
  - All orders go through DRY-RUN first
  - No real broker calls until Phase 107 is explicitly enabled
  - Phase 107 wrapper is DRY_RUN by default

---

## Implementation Patterns

### 1. Phase Module Structure

**Standard Pattern**:
```python
"""
System3 Phase NNN - <Description>
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def run_phaseNNN(**kwargs) -> dict:
    """
    Main function for Phase NNN.
    
    Returns:
        dict: {
            "phase": NNN,
            "status": "OK" or "ERROR",
            "details": "short human-readable summary",
            "outputs": { ... },      # phase-specific
            "errors": [],            # list of error strings
        }
    """
    try:
        # Phase logic here
        return {
            "phase": NNN,
            "status": "OK",
            "details": "Phase NNN completed successfully",
            "outputs": {},
            "errors": []
        }
    except Exception as e:
        return {
            "phase": NNN,
            "status": "ERROR",
            "details": f"Phase NNN failed: {str(e)}",
            "outputs": {},
            "errors": [str(e)]
        }

def main():
    """CLI entry point."""
    result = run_phaseNNN()
    print(f"Phase{result['phase']}: {result['details']}")
    return 0 if result['status'] == "OK" else 1

if __name__ == "__main__":
    sys.exit(main())
```

### 2. Config Import Pattern

```python
from config.live_trade_config import (
    LIVE_TRADING_ENABLED,
    MAX_LIVE_TRADES_PER_DAY,
    MAX_LIVE_TRADES_PER_UNDERLYING,
    DEFAULT_LOTS_PER_TRADE,
    LIVE_ALLOWED_UNDERLYINGS,
    ANGEL_PRODUCT_TYPE,
    ANGEL_ORDER_VARIETY,
)
```

### 3. Ledger Read/Write Pattern

```python
import pandas as pd

LEDGER_PATH = PROJECT_ROOT / "storage" / "live" / "live_orders_ledger.csv"

# Read ledger
if LEDGER_PATH.exists():
    df = pd.read_csv(LEDGER_PATH)
else:
    # Create with header (Phase 102 logic)
    df = pd.DataFrame(columns=[...])

# Modify ledger
# ... logic ...

# Write ledger (append mode for new rows, or full write for updates)
df.to_csv(LEDGER_PATH, index=False)
```

### 4. Safety Check Pattern

```python
# Check LIVE_TRADING_ENABLED
if not LIVE_TRADING_ENABLED:
    return {
        "phase": NNN,
        "status": "ERROR",
        "details": "LIVE_TRADING_ENABLED=False; aborting",
        "outputs": {},
        "errors": ["LIVE_TRADING_ENABLED=False"]
    }

# Check kill switch (Phase 113)
kill_switch_path = PROJECT_ROOT / "storage" / "live" / "kill_switch.json"
if kill_switch_path.exists():
    with kill_switch_path.open("r") as f:
        kill_data = json.load(f)
        if kill_data.get("kill", False):
            return {
                "phase": NNN,
                "status": "KILL",
                "details": "Kill switch activated",
                "outputs": {},
                "errors": []
            }
```

---

## Dependencies & Integration Points

### Existing System3 Components to Reuse

1. **DRY RUN Executor**
   - Location: Existing System3 codebase
   - Used by: Phase 106
   - Action: Cursor agent must inspect existing code and reuse

2. **Trade Plan CSV**
   - Location: `storage/live/dhan_index_ai_trades_plan.csv`
   - Used by: Phase 104
   - Format: Existing System3 trade planning output

3. **Real Outcome Logging**
   - Location: `storage/learning/` (phases 28-37)
   - Used by: Phase 117
   - Action: Connect ledger to existing Real Outcome files

4. **SmartConnect Session**
   - Location: Existing Dhan integration
   - Used by: Phase 103 (AngelLiveOrderWrapper)
   - Action: Pass existing SmartConnect session to wrapper

### New Components to Create

1. **Config File**: `config/live_trade_config.py`
2. **Broker Wrapper**: `core/broker/dhan_live_order_wrapper.py`
3. **Order Ledger**: `storage/live/live_orders_ledger.csv`
4. **Phase Modules**: `core/engine/system3_phaseNNN_*.py` (101-120)
5. **Stub Modules**: `core/engine/system3_phaseNNN_*.py` (121-130)

---

## File Structure

### New Directories
- `core/broker/` - Broker-specific wrappers (if doesn't exist)

### New Files by Category

**Config**:
- `config/live_trade_config.py`

**Broker**:
- `core/broker/dhan_live_order_wrapper.py`

**Phase Modules (101-120)**:
- `core/engine/system3_phase101_live_trade_config_check.py`
- `core/engine/system3_phase102_order_ledger_schema.py`
- `core/engine/system3_phase103_*.py` (wrapper, no CLI)
- `core/engine/system3_phase104_tradeplan_to_orders.py`
- `core/engine/system3_phase105_ledger_integrity_check.py`
- `core/engine/system3_phase106_dryrun_execution_bridge.py`
- `core/engine/system3_phase107_live_execution_engine.py`
- `core/engine/system3_phase108_order_status_refresher.py`
- `core/engine/system3_phase109_intraday_risk_guard.py`
- `core/engine/system3_phase110_exit_rule_builder.py`
- `core/engine/system3_phase111_live_session_brain.py`
- `core/engine/system3_phase112_session_loop_controller.py`
- `core/engine/system3_phase113_kill_switch_monitor.py`
- `core/engine/system3_phase114_live_session_health.py`
- `core/engine/system3_phase115_intraday_alert_summary.py`
- `core/engine/system3_phase116_end_session_auto_stop.py`
- `core/engine/system3_phase117_live_to_learning_bridge.py`
- `core/engine/system3_phase118_daily_live_pnl_snapshot.py`
- `core/engine/system3_phase119_live_safety_audit.py`
- `core/engine/system3_phase120_eod_live_summary_pack.py`

**Stub Modules (121-130)**:
- `core/engine/system3_phase121_*.py` through `system3_phase130_*.py`

**Storage/Live Outputs**:
- `storage/live/phase101_live_trade_config_snapshot.json`
- `storage/live/live_orders_ledger.csv`
- `storage/live/phase110_exit_rules_pending.json`
- `storage/live/kill_switch.json`
- `storage/live/phase114_live_session_health.md`
- `storage/live/phase115_intraday_alert_summary.txt`
- `storage/live/phase118_daily_pnl_snapshot.md`
- `storage/live/phase119_live_safety_audit.md`
- `storage/live/phase120_eod_live_summary_pack.md`

**Logs**:
- `logs/phase102_order_ledger_schema.log`
- `logs/phase105_ledger_integrity_issues.log`
- `logs/phase106_dryrun_execution.log`
- `logs/phase107_live_execution_engine.log`
- `logs/phase112_session_loop.log`

---

## Verification Workflow

### Step 1: Config & Ledger Setup
```bash
python -m core.engine.system3_phase101_live_trade_config_check
python -m core.engine.system3_phase102_order_ledger_schema
python -m core.engine.system3_phase105_ledger_integrity_check
```

**Expected**:
- Config snapshot JSON created
- Ledger CSV with header created
- Integrity check passes

### Step 2: Trade Plan → Ledger → DRY RUN
```bash
python -m core.engine.system3_phase104_tradeplan_to_orders
python -m core.engine.system3_phase106_dryrun_execution_bridge
python -m core.engine.system3_phase108_order_status_refresher
```

**Expected**:
- Trade plan rows converted to ledger orders
- DRY_RUN execution updates ledger
- Status refresher updates (or logs NOT_IMPLEMENTED)

### Step 3: Session Brain One-Shot
```bash
python -m core.engine.system3_phase111_live_session_brain
python -m core.engine.system3_phase112_session_loop_controller
python -m core.engine.system3_phase114_live_session_health
```

**Expected**:
- Session brain orchestrates phases
- Loop controller runs one iteration
- Health snapshot generated

---

## Key Safety Guarantees

1. ✅ **No Real Trading by Default**: `LIVE_TRADING_ENABLED = False`
2. ✅ **Config-Controlled**: All risk limits in one config file
3. ✅ **Dry-Run First**: Phase 106 always runs before Phase 107
4. ✅ **Kill Switch**: Can be activated at any time
5. ✅ **Risk Guards**: Multiple layers of risk checking
6. ✅ **Ledger Integrity**: Validation before any execution
7. ✅ **End-of-Session Auto-Stop**: Prevents after-hours trading
8. ✅ **1 Lot Limit**: Initial real tests limited to 1 lot
9. ✅ **Additive Only**: No changes to existing Baseline/Ultra
10. ✅ **Wrapper Abstraction**: All broker calls go through one wrapper

---

## Implementation Priority

### Phase 1: Foundation (101-105) - **HIGH PRIORITY**
- Essential infrastructure
- No dependencies on other new phases
- Can be implemented and tested independently

### Phase 2: Execution Layer (106-110) - **HIGH PRIORITY**
- Depends on Phase 103 (wrapper)
- Enables dry-run testing
- Phase 107 must remain DRY_RUN until explicitly enabled

### Phase 3: Session Orchestration (111-115) - **MEDIUM PRIORITY**
- Depends on Phases 101-110
- Orchestrates the full flow
- Can be tested once foundation is ready

### Phase 4: Session Management (116-120) - **MEDIUM PRIORITY**
- Depends on earlier phases
- End-of-day operations
- Safety and reporting

### Phase 5: Stubs (121-130) - **LOW PRIORITY**
- Future enhancements
- Menu integration stubs
- Minimal implementation required

---

## Critical Implementation Notes

1. **Phase 103 (Wrapper)**: Must remain DRY_RUN/STUB until Pritam explicitly enables real DhanHQ integration
2. **Phase 107 (Live Execution)**: Must check `LIVE_TRADING_ENABLED` and abort if False
3. **Phase 106 (Dry-Run)**: Must reuse existing DRY RUN executor from System3
4. **Phase 104 (Trade Plan)**: Must check for duplicates before appending to ledger
5. **Phase 105 (Integrity)**: Must validate ledger before any execution phase
6. **Phase 109 (Risk Guard)**: Must be called before Phase 107
7. **Phase 113 (Kill Switch)**: Must be checked in Phase 112 loop
8. **All Phases**: Must follow standard return dict format
9. **All Phases**: Must not modify existing Baseline/Ultra files
10. **All Phases**: Must log to appropriate locations

---

## Questions & Clarifications Needed

1. **DRY RUN Executor**: Need to locate existing DRY RUN executor module name/path
2. **SmartConnect Session**: Need to understand how existing SmartConnect session is managed
3. **Lot Size**: Need to determine lot size calculation (assume 1 for now, log warning)
4. **Trade Plan CSV Format**: Need to verify exact column names in `dhan_index_ai_trades_plan.csv`
5. **Real Outcome Files**: Need to verify format of existing Real Outcome files for Phase 117

---

## Summary

This plan defines a **comprehensive, safe, layered approach** to adding live trading automation to System3. The implementation is:

- ✅ **Well-Structured**: Clear phase groups with specific purposes
- ✅ **Safety-First**: Multiple layers of safety checks and guards
- ✅ **Config-Driven**: All risk controls in one central config
- ✅ **Additive**: No changes to existing Baseline/Ultra code
- ✅ **Testable**: Clear verification workflow
- ✅ **Extensible**: Reserved phases for future enhancements

**Status**: ✅ **ANALYSIS COMPLETE - READY FOR IMPLEMENTATION**

---

**Next Steps**: 
1. Review this analysis
2. Clarify any questions
3. Proceed with implementation in priority order (101-105 first)

