# System3 GENI Ultra Master Agent - Overview

**Date**: 2025-11-30  
**Version**: 1.0.0

---

## What is GENI Master?

GENI (Genesis Intelligence) Master is a high-level orchestration and validation layer for System3 Ultra operations. It provides:

- **Centralized validation** - Run full or quick validation suites
- **Task orchestration** - Coordinate existing System3 scripts
- **State management** - Track system health and validation status
- **Safe operation** - All operations are DRY-RUN / shadow-only

---

## Safety Guarantees

✅ **No Real Trades** - GENI Master never places real broker orders  
✅ **No Auto-Promotion** - Models are never automatically promoted  
✅ **No Config Changes** - Configuration files are read-only  
✅ **Read-Only Orchestration** - Only coordinates existing scripts  
✅ **Safe Mode Default** - All safety flags default to False  

---

## CLI Commands

### Status Check

```bash
python system3_geni_master.py status
```

**What it does**:
- Checks environment (paths, files)
- Runs quick validation if environment is OK
- Updates state file
- Prints current system status

**Output**: Status summary to console + state file update

---

### Full Validation

```bash
python system3_geni_master.py full-validation
```

**What it does**:
- Runs complete System3 validation suite
- Parses validation results
- Updates state with validation status
- Generates summary JSON and MD files

**Output**: Validation results + summary files

---

### Daily Ultra

```bash
python system3_geni_master.py daily-ultra
```

**What it does**:
- Runs daily Ultra automation cycle (DRY-RUN)
- Runs quick validation after
- Updates state
- Generates summary

**Output**: Daily cycle results + validation summary

---

### Panel Test

```bash
python system3_geni_master.py panel-test
```

**What it does**:
- Runs Ultra control panel test suite
- Records test results
- Updates state

**Output**: Test results + summary

---

### All Operations

```bash
python system3_geni_master.py all
```

**What it does**:
- Runs full validation
- Runs panel test
- Runs daily ultra
- Combines all results

**Output**: Combined results summary

---

## File Locations

### GENI State

**Location**: `storage/geni/system3_geni_state.json`

**Contains**:
- Environment status
- Validation status
- Last validation summary
- Pending issues

---

### Last Run Summary

**JSON**: `storage/geni/system3_geni_last_run.json`  
**MD**: `storage/geni/system3_geni_last_run.md`

**Contains**:
- Timestamp
- Mode executed
- Success status
- Validation results
- Warnings
- Recommended next actions

---

### Logs

GENI Master uses existing System3 logging:
- Console output for immediate feedback
- Existing validation scripts write their own logs
- No separate GENI log file (uses existing infrastructure)

---

## Interaction with System3

### system3_ultra.py

- **GENI does NOT modify** `system3_ultra.py`
- GENI can call `system3_ultra.py` as a task
- Both can run independently
- GENI provides orchestration layer above `system3_ultra.py`

### Daily Runners

- **GENI uses** `system3_ultra_daily_runner.py` (does not modify)
- GENI orchestrates daily runners, doesn't replace them
- Existing daily scripts continue to work independently

### Validation Scripts

- **GENI uses** `system3_ultra_validation.py` and `run_full_verification_checklist.py`
- GENI parses their output and summarizes results
- Existing validation scripts continue to work independently

---

## Architecture

### Core Modules

```
core/geni/
├── __init__.py          # Package init
├── geni_config.py       # Paths and safety flags
├── geni_state.py        # State management
├── geni_tasks.py        # Task registry
├── geni_validator.py    # Validation helpers
└── geni_orchestrator.py # Main orchestrator
```

### Entry Point

```
system3_geni_master.py  # CLI entry point
```

### Storage

```
storage/geni/
├── system3_geni_state.json      # Current state
├── system3_geni_last_run.json  # Last run summary (JSON)
└── system3_geni_last_run.md     # Last run summary (MD)
```

---

## Usage Examples

### Check System Status

```bash
python system3_geni_master.py status
```

**Expected Output**:
```
System3 GENI Master – SAFE MODE (no real orders, no auto-promotion)
======================================================================
[GENI] Mode: STATUS CHECK
[GENI] Environment OK: True
[GENI] Last validation: Quick validation: 45/45 passed
[GENI] Pending issues: 0
```

### Run Full Validation

```bash
python system3_geni_master.py full-validation
```

**Expected Output**:
```
System3 GENI Master – SAFE MODE (no real orders, no auto-promotion)
======================================================================
[GENI] Mode: FULL VALIDATION
[GENI] Running full validation...
...
======================================================================
GENI Master Summary
======================================================================
Mode: full_validation
Success: True
Validation: 45/45 passed
Summary JSON: C:\Genesis_System3\storage\geni\system3_geni_last_run.json
Summary MD: C:\Genesis_System3\storage\geni\system3_geni_last_run.md
======================================================================
```

---

## Important Notes

1. **GENI Master does NOT place real trades** - All operations are safe
2. **GENI Master does NOT auto-promote models** - Manual promotion only
3. **GENI Master does NOT modify configs** - Read-only access
4. **GENI Master orchestrates existing scripts** - Does not replace them
5. **All modes are SAFE** - No live trading or auto-execution

---

## Troubleshooting

### "Task not found" Error

- Check that task name matches registry in `geni_tasks.py`
- Verify script paths in `geni_config.py`

### Validation Timeout

- Increase timeout in `geni_validator.py`
- Check that validation scripts are working independently

### State File Issues

- State file is auto-created if missing
- Corrupt state files are replaced with defaults
- Check `storage/geni/` directory permissions

---

## Next Steps

1. **Run status check** to verify installation
2. **Run full validation** to test validation integration
3. **Review summary files** in `storage/geni/`
4. **Integrate into daily workflow** if needed

---

**Last Updated**: 2025-11-30  
**Status**: ✅ Implementation Complete

