# System3 GENI Master - Quick Start Guide

**Date**: 2025-11-30  
**Purpose**: Quick reference for using GENI Master

---

## Installation Status

✅ **GENI Master is installed and ready to use**

All files created:
- `core/geni/` package (6 modules)
- `system3_geni_master.py` entry script
- `tests/test_geni_master.py` test suite
- Documentation files

---

## Quick Commands

### Check System Status

```bash
python system3_geni_master.py status
```

**What it does**:
- Checks environment (paths, files)
- Runs quick validation
- Updates state file
- Prints status summary

**Expected Output**:
```
System3 GENI Master – SAFE MODE (no real orders, no auto-promotion)
======================================================================
[GENI] Mode: STATUS CHECK
[GENI] Environment OK: True
[GENI] Last validation: Quick validation: X/Y passed
[GENI] Pending issues: 0
```

---

### Run Full Validation

```bash
python system3_geni_master.py full-validation
```

**What it does**:
- Runs complete System3 validation suite
- Parses results
- Updates state
- Generates summary

---

### Run Daily Ultra Cycle

```bash
python system3_geni_master.py daily-ultra
```

**What it does**:
- Runs daily Ultra automation (DRY-RUN)
- Runs validation
- Updates state

---

### Run All Operations

```bash
python system3_geni_master.py all
```

**What it does**:
- Full validation
- Panel test
- Daily ultra
- Combined summary

---

## Output Files

After running GENI master, check:

- **State**: `storage/geni/system3_geni_state.json`
- **Summary JSON**: `storage/geni/system3_geni_last_run.json`
- **Summary MD**: `storage/geni/system3_geni_last_run.md`

---

## Safety Reminder

**Every run displays**:
```
System3 GENI Master – SAFE MODE (no real orders, no auto-promotion)
```

This confirms all operations are safe.

---

## Troubleshooting

### "Validation: 0/0 passed"

This means the parser couldn't extract numbers from validation output. The validation script still ran successfully - check the raw output in the summary files.

**Fix Applied**: Parser improved to handle multiple output formats.

### "pytest not found"

Use unittest instead:
```bash
python -m unittest tests.test_geni_master
```

---

## Next Steps

1. ✅ **Installation**: Complete
2. ✅ **Status Check**: Working
3. ⏳ **Full Validation**: Run and verify parsing
4. ⏳ **Daily Integration**: Use in daily workflow if needed

---

**Last Updated**: 2025-11-30  
**Status**: ✅ **READY FOR USE**

