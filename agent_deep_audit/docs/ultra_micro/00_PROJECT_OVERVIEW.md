# System3 - Ultra Micro Project Overview
**Generated**: 2025-12-04  
**Purpose**: Complete project structure and architecture at ultra-micro detail level

---

## Project Information

**Name**: System3  
**Full Name**: Genesis System3 - Autonomous Trading System  
**Description**: Fully autonomous, AI-driven index options trading system for Dhan (NSE/BSE)  
**Language**: Python 3.8+  
**Architecture**: Modular Phase-Based System  
**Trading Mode**: DRY-RUN ONLY (No live trading)  
**Broker**: Dhan (DhanHQ)

---

## Core Architecture

### System Design Philosophy
- **Modular**: Each phase is an independent module
- **Phase-Based**: Sequential execution with dependencies
- **Autonomous**: Fully automated from market open to close
- **Safe**: Multiple layers of DRY-RUN protection
- **Self-Healing**: Retry logic, error recovery, watchdog monitoring

### Main Components

1. **Autorun Master** (`system3_autorun_master.py`)
   - Orchestrates entire trading day
   - Manages phase execution
   - Handles scheduling and timing
   - Updates heartbeat

2. **Watchdog** (`system3_watchdog.py`)
   - Monitors autorun master
   - Restarts master if crashed (during market hours only)
   - Checks heartbeat staleness
   - Respects shutdown flags

3. **Autopilot** (`system3_live_day_autopilot.py`)
   - Generates live signals
   - Creates trade plans (DRY-RUN)
   - Manages OP cycles
   - Handles signal processing

---

## Directory Structure (Ultra Micro)

### Root Directory
```
C:\Genesis_System3\
├── core/                    # Core engine modules
│   ├── engine/              # Phase implementations (219 files)
│   ├── phases/              # Additional phase modules
│   ├── brokers/             # Broker integration (Dhan)
│   ├── models/              # ML models (5 underlyings)
│   ├── config/              # Configuration files
│   └── utils/               # Utility functions
├── storage/                 # Data storage
│   ├── live/                # Live trading data
│   ├── meta/                # Metadata and configs
│   ├── training/            # Training datasets
│   └── snapshots/           # Model snapshots
├── logs/                    # Log files
│   ├── system3_autorun_master_*.log
│   ├── system3_watchdog_*.log
│   └── live_day_autopilot_*.log
├── docs/                    # Documentation
│   └── ultra_micro/         # This documentation
├── config/                  # Configuration
│   └── live_trade_config.py # Safety flags
├── venv/                    # Virtual environment
└── [Main Scripts]           # Entry points
```

---

## Key Files (Ultra Micro Detail)

### 1. `system3_autorun_master.py`
**Purpose**: Main orchestration script  
**Size**: ~600 lines  
**Key Functions**:
- `main()`: Entry point, orchestrates entire day
- `enforce_safety_checks()`: DRY-RUN verification
- `update_heartbeat()`: Heartbeat thread
- `check_shutdown_flag()`: Prevents restart loops
- `is_market_time()`: Market hours check (09:15-15:30 IST)
- `run_phases_range()`: Executes phase ranges
- `run_op1()`, `run_op2()`, `run_op3()`: OP cycles

**Phase Loading**:
- Lines 71-83: Loads phases 201-230 from `system3_phase_201_230_diagnostics`
- Lines 85-92: Loads phases 231-260 from `system3_phase_231_260_diagnostics`
- Lines 94-101: Loads phases 261-300 from `system3_phase_261_300_diagnostics`
- Lines 103-110: Loads phases 301-310 from `system3_phases_301_310_diagnostics`

**Execution Schedule**:
- Pre-market: Phases 201-310 (runs once at startup)
- 9:15 AM: Autopilot starts (OP2)
- Every 30 min: Phases 220-260 (during market hours)
- Every 2 hours: Curated file refresh
- Every hour: OP cycles
- 3:30 PM: Archive signals
- 3:35 PM: EOD Learning
- 4:00 PM: Clean shutdown

### 2. `system3_watchdog.py`
**Purpose**: Monitor and restart autorun master  
**Size**: ~260 lines  
**Key Functions**:
- `is_market_hours()`: Market hours check (09:15-16:00 IST)
- `check_shutdown_flag()`: Prevents restart after shutdown
- `check_heartbeat_staleness()`: Detects frozen master
- `is_master_running()`: Process check using psutil
- `start_master()`: Restart master with retry logic

**Behavior**:
- Checks every 60 seconds
- Only restarts during market hours (9:15 AM - 4:00 PM)
- Respects shutdown flag (won't restart after clean shutdown)
- Detects heartbeat staleness (> 3 minutes = frozen)

### 3. `system3_live_day_autopilot.py`
**Purpose**: Live signal generation and trade planning  
**Size**: ~570 lines  
**Key Functions**:
- `run_op1_pre_market_checks()`: Pre-market validation
- `run_op2_live_session()`: Main signal generation loop
- `run_op3_eod_processing()`: End-of-day tasks

**Safety Checks** (Lines 59-86):
- `LIVE_TRADING_ENABLED = False`
- `USE_LIVE_EXECUTION_ENGINE = False`
- `auto_execute_trades = False`
- `AUTO_EXECUTE_TRADES = False`

**Error Handling**:
- Lines 138-141: UnicodeEncodeError handling (non-critical)
- Lines 189-195: DhanHQ ImportError handling (graceful)

### 4. `START_AUTORUN_AND_WATCHDOG.bat`
**Purpose**: Launch script for autorun system  
**Lines**: 30  
**Structure**:
- Line 5: Sets working directory
- Line 8: Activates virtual environment
- Line 11: Starts watchdog in new window
- Line 26: Starts autorun master in current window

---

## Phase System (Ultra Micro)

### Phase Ranges

| Range | Count | Diagnostic Script | Loading Method |
|-------|-------|-------------------|----------------|
| 201-230 | 30 | `system3_phase_201_230_diagnostics.py` | PHASE_IMPORTS dict |
| 231-260 | 30 | `system3_phase_231_260_diagnostics.py` | PHASE_MODULES dict |
| 261-300 | 40 | `system3_phase_261_300_diagnostics.py` | PHASE_MODULES dict |
| 301-310 | 10 | `system3_phases_301_310_diagnostics.py` | PHASE_MODULES dict |

**Total Phases in Autorun**: 110 phases (201-310)

### Phase Loading Mechanism

**For 201-230** (Uses PHASE_IMPORTS):
```python
PHASE_IMPORTS = {
    201: ("system3_phase201_filesystem_integrity", "run_phase201"),
    202: ("system3_phase202_permissions_self_repair", "run_phase202"),
    # ... etc
}
```

**For 231-310** (Uses PHASE_MODULES):
```python
PHASE_MODULES = {
    231: <function run_phase231>,
    232: <function run_phase232>,
    # ... etc
}
```

### Phase Execution Flow

1. **Import Phase Function**: Dynamic import from diagnostic script
2. **Store in PHASE_IMPORTS**: Dictionary mapping phase number → function
3. **Execute via `run_phases_range()`**: Calls function, captures result
4. **Result Format**: `{"phase": N, "status": "OK/WARN/ERROR", "details": "...", "outputs": {...}}`
5. **Logging**: All results logged to autorun master log

---

## Data Flow (Ultra Micro)

### Signal Generation Flow

```
Market Data (Dhan API)
    ↓
Options Chain Retrieval (dhan_options_watch.py)
    ↓
Feature Engineering
    ↓
AI Model Prediction (5 models: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX)
    ↓
Signal Generation (dhan_live_ai_signals.py)
    ↓
dhan_index_ai_signals.csv (Raw signals)
    ↓
Phase 144: PnL vs Execution Scenario
    ↓
dhan_index_ai_signals_curated.csv (Curated signals)
    ↓
Phase 221: Forward Returns Calculation
    ↓
dhan_index_ai_signals_with_forward.csv (Enriched signals)
    ↓
Phase 222: Signal Edge Estimation
    ↓
EV Tables (logs/research/system3_signal_edge_report.md)
    ↓
Phase 304: Threshold Tuner
    ↓
storage/meta/system3_live_thresholds.json
    ↓
Trade Decision Engine (dhan_trade_decision.py)
    ↓
Trade Plans (DRY-RUN only)
```

### File Dependencies

**Input Files**:
- `storage/live/dhan_index_ai_signals.csv` (Raw signals)
- `storage/live/dhan_index_ai_signals_curated.csv` (Curated signals)
- `storage/meta/system3_live_thresholds.json` (Thresholds)

**Output Files**:
- `storage/live/dhan_index_ai_signals_with_forward.csv` (Phase 221)
- `logs/research/system3_signal_edge_report.md` (Phase 222)
- `storage/meta/system3_threshold_proposals_*.json` (Phase 304)

---

## Configuration System (Ultra Micro)

### Safety Flags

**File**: `config/live_trade_config.py`
- `LIVE_TRADING_ENABLED`: Must be `False`
- `USE_LIVE_EXECUTION_ENGINE`: Must be `False`

**File**: `core/engine/dhan_automation_config.py`
- `AUTOMATION_CONFIG.auto_execute_trades`: Must be `False`

**File**: `core/config/system3_ultra_safety.json`
- `AUTO_EXECUTE_TRADES`: Must be `False`

**Verification**: `system3_autorun_master.py` lines 147-200 (`enforce_safety_checks()`)

### Market Hours Configuration

**Autorun Master** (`system3_autorun_master.py` lines 440-446):
- Market Open: 09:15 IST
- Market Close: 15:30 IST
- Function: `is_market_time()`

**Watchdog** (`system3_watchdog.py` lines 54-62):
- Market Open: 09:15 IST
- Market Close: 16:00 IST (includes shutdown time)
- Function: `is_market_hours()`

---

## Heartbeat System (Ultra Micro)

### Heartbeat File
**Location**: `system3_daily_heartbeat.json`  
**Update Frequency**: Every 60 seconds  
**Thread**: Daemon thread started in autorun master (line 477-478)

### Heartbeat Structure
```json
{
  "timestamp": "ISO format timestamp",
  "status": "running",
  "autopilot_running": true/false,
  "last_phase_run": "ISO timestamp",
  "last_curated_refresh": "ISO timestamp",
  "last_op_cycle": "ISO timestamp"
}
```

### Staleness Detection
**Watchdog** checks heartbeat age:
- If > 3 minutes old → Considered stale
- If stale during market hours → Master may be frozen
- Watchdog can restart master if stale

---

## Shutdown System (Ultra Micro)

### Shutdown Flag
**Location**: `system3_shutdown_flag.json`  
**Purpose**: Prevents restart loops after clean shutdown

### Shutdown Flag Structure
```json
{
  "shutdown_date": "YYYY-MM-DD",
  "shutdown_time": "ISO timestamp",
  "reason": "scheduled_shutdown_4pm"
}
```

### Shutdown Logic
1. **At 4:00 PM**: Autorun master writes shutdown flag
2. **Master Exits**: Clean exit with shutdown flag written
3. **Watchdog Detects**: Checks shutdown flag
4. **No Restart**: Watchdog won't restart if shutdown flag exists for today
5. **Next Day**: Shutdown flag from previous day doesn't block new start

**Code**: `system3_autorun_master.py` lines 118-129, 132-145, 556-562

---

## Phase Execution Details (Ultra Micro)

### Phase Result Format
```python
{
    "phase": 221,
    "status": "OK" | "WARN" | "ERROR",
    "details": "Human-readable description",
    "outputs": {
        "rows_processed": 608,
        "output_file": "path/to/file.csv",
        # ... phase-specific outputs
    },
    "errors": ["error1", "error2"]  # Only if status == "ERROR"
}
```

### Phase Status Meanings

**OK**: Phase executed successfully, all outputs generated

**WARN**: Phase executed but with warnings:
- No data available (expected for some phases)
- Missing optional inputs
- Insufficient data for analysis
- Conservative behavior (better to warn than fail)

**ERROR**: Phase failed critically:
- Missing required inputs
- Code errors
- File I/O failures
- Import errors

**SKIPPED**: Phase not executed:
- Not in autorun range
- Not implemented yet
- Conditional execution (conditions not met)

---

## Statistics

- **Total Phase Files**: 219 files in `core/engine/`
- **Phases in Autorun**: 110 phases (201-310)
- **Total Lines of Code**: ~50,000+ lines (estimated)
- **Main Scripts**: 4 (autorun master, watchdog, autopilot, batch file)
- **Diagnostic Scripts**: 4 (one per phase range)
- **Configuration Files**: 3+ (safety flags, automation config, ultra safety)

---

**Documentation Generated**: 2025-12-04  
**Status**: ✅ **ULTRA MICRO OVERVIEW COMPLETE**

