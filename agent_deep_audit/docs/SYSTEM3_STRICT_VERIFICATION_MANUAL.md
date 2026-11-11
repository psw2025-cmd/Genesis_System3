# System3 Strict Verification - Manual Execution Guide
**Date**: 2025-12-04  
**Purpose**: Complete verification of all System3 commands with strict error detection

---

## Execution Instructions

Due to terminal configuration issues, all commands must be executed manually using the **exact full Python path**:

```
C:\Genesis_System3\venv\Scripts\python.exe
```

**NEVER use**: `python`, `py`, `py.exe`, or any aliases.

---

## Commands to Execute

### 1. Python Version Check
```batch
C:\Genesis_System3\venv\Scripts\python.exe --version
```

**Expected Output**:
- STDOUT: `Python 3.10.11` (or similar)
- STDERR: (empty)
- EXIT CODE: 0
- **SUCCESS**: If exit code is 0 and no errors in stderr

---

### 2. Phase 221 - Forward Returns
```batch
C:\Genesis_System3\venv\Scripts\python.exe core\engine\system3_phase221_forward_returns.py
```

**Expected Output**:
- STDOUT: Contains "Phase 221: Computed forward returns"
- STDERR: (empty or warnings only)
- EXIT CODE: 0
- **SUCCESS**: If exit code is 0, no error keywords in stderr, and output file created

**Output File**: `storage\live\dhan_index_ai_signals_with_forward.csv`

**Error Keywords to Check**:
- error
- exception
- traceback
- failed
- FileNotFound
- ModuleNotFound
- KeyError
- ValueError

---

### 3. Phase 222 - Signal Edge
```batch
C:\Genesis_System3\venv\Scripts\python.exe core\engine\system3_phase222_signal_edge.py
```

**Expected Output**:
- STDOUT: Contains "Phase 222: Created X EV tables"
- STDERR: (empty or warnings only)
- EXIT CODE: 0
- **SUCCESS**: If exit code is 0, no error keywords in stderr, and output file created

**Output File**: `logs\research\system3_signal_edge_report.md`

**Error Keywords to Check**: Same as above

---

### 4. PnL Simulator
```batch
C:\Genesis_System3\venv\Scripts\python.exe core\engine\dhan_pnl_simulator.py
```

**Expected Output**:
- STDOUT: Contains "[PNL] Detailed trade PnL log written"
- STDERR: (empty or warnings only)
- EXIT CODE: 0
- **SUCCESS**: If exit code is 0, no error keywords in stderr, and output file created

**Output File**: `storage\live\dhan_index_ai_pnl_log.csv`

**Error Keywords to Check**: Same as above

---

## Execution Report Format

After each command, record:

```
=== COMMAND EXECUTION REPORT ===
COMMAND: <full command>
STDOUT: <full stdout>
STDERR: <full stderr>
EXIT CODE: <exit code>
SUCCESS/FAILURE: <SUCCESS or FAILURE>
REASON: <explanation>
```

---

## Error Detection Rules

### FAILURE Conditions

A command is considered **FAILED** if ANY of the following are true:

1. **Exit Code ≠ 0**
2. **STDERR contains any of these keywords**:
   - error
   - exception
   - traceback
   - not recognized
   - failed
   - FileNotFound
   - ModuleNotFound
   - KeyError
   - ValueError
   - UnicodeDecodeError
   - ImportError
   - AttributeError
   - TypeError
   - NameError
   - SyntaxError
   - IndentationError

### SUCCESS Conditions

A command is considered **SUCCESS** only if:

1. Exit code = 0
2. No error keywords in STDERR
3. Expected output file exists (if applicable)
4. Expected output appears in STDOUT

---

## Automatic Fixes

If a command fails, check for these common issues:

### Import Errors
- **Symptom**: `ModuleNotFoundError: No module named 'core'`
- **Fix**: Ensure script has:
  ```python
  import sys
  from pathlib import Path
  PROJECT_ROOT = Path(__file__).parent.parent.parent
  if str(PROJECT_ROOT) not in sys.path:
      sys.path.insert(0, str(PROJECT_ROOT))
  ```

### File Not Found Errors
- **Symptom**: `FileNotFoundError` or `[ERROR] Signals CSV not found`
- **Fix**: Verify input files exist in expected locations

### CSV Parsing Errors
- **Symptom**: `Error tokenizing data` or `Expected X fields, saw Y`
- **Fix**: Scripts should use `engine="python", on_bad_lines="skip"`

---

## Batch File Execution

Alternatively, use the batch files (they use the correct Python path):

```batch
run_phase221.bat
run_phase222.bat
run_pnl_simulator.bat
```

---

## Verification Script

Run the comprehensive verification script:

```batch
C:\Genesis_System3\venv\Scripts\python.exe comprehensive_system3_verification.py
```

This will test:
- Python path existence
- Directory structure
- Script file existence
- Import capabilities
- Output file existence

---

## Current Status

Based on previous runs:

- ✅ **Phase 221**: Working correctly
- ✅ **Phase 222**: Working correctly
- ✅ **PnL Simulator**: Fixed and working correctly

All scripts have proper sys.path setup and should execute without errors.

---

## Next Steps

1. Execute all commands manually using the full Python path
2. Record execution reports for each command
3. Verify all output files are created
4. Check for any warnings (non-fatal)
5. Document any issues found

---

**Last Updated**: 2025-12-04

