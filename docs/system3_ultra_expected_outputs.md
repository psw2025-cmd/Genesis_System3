# System3 Ultra Control Panel - Expected Outputs Guide

**Purpose**: This document defines the expected outputs for all System3 Ultra operations to help with validation, troubleshooting, and understanding successful execution.

**Last Updated**: 2025-11-30

---

## Table of Contents

1. [Safety Status Checks](#safety-status-checks)
2. [Validation Outputs](#validation-outputs)
3. [Core Operations](#core-operations)
4. [Ultra Phases 21-30](#ultra-phases-21-30)
5. [Ultra Phases 31-38](#ultra-phases-31-38)
6. [Ultra Phases 39-45](#ultra-phases-39-45)
7. [System Tools](#system-tools)
8. [Error Handling](#error-handling)
9. [File Outputs](#file-outputs)

---

## Safety Status Checks

### Option S: Safety Status Check

**Expected Output**:
```
=== SYSTEM3 ULTRA SAFETY SWITCHES ===

Current Safety Settings:
  AUTO_EXECUTE_TRADES: False (❌ DISABLED)
  AUTO_UPDATE_THRESHOLDS: False (❌ DISABLED)
  AUTO_RETRAIN_MODELS: False (❌ DISABLED)
  AUTO_PROMOTE_MODELS: False (❌ DISABLED)
  AUTO_WRITE_CONFIG: False (❌ DISABLED)

[NOTE] All features default to DISABLED for safety.
```

**Expected Status**: All switches should be `False` (DISABLED) for safe operation.

---

## Validation Outputs

### Option V: Full Validation

**Expected Output**:
```
======================================================================
SYSTEM3 ULTRA - FULL VALIDATION
======================================================================
Date: YYYY-MM-DD HH:MM:SS

======================================================================
FILE-LEVEL VALIDATION
======================================================================
  ✓ Main control panel (system3_ultra.py)
  ✓ Runtime loops (system3_ultra_runtime_loops.py)
  ✓ Daily runner (system3_ultra_daily_runner.py)
  ✓ Weekly runner (system3_ultra_weekly_runner.py)
  ✓ Validation engine (system3_ultra_validation.py)
  ... (25 total file checks)

======================================================================
IMPORT VALIDATION
======================================================================
  ✓ Ultra safety module
  ✓ Automation config
  ✓ Phase 21
  ✓ Phase 31
  ... (7 total import checks)

======================================================================
SAFETY VALIDATION
======================================================================
  ✓ Auto-execute trades
  ✓ Auto-simulate PnL
  ✓ Ultra auto-execute
  ✓ Ultra auto-update
  ✓ Ultra auto-retrain
  ✓ Ultra auto-promote
  ✓ Baseline models directory exists
  ✓ Ultra models isolated

======================================================================
MENU VALIDATION
======================================================================
  ✓ Menu structure documentation
  ✓ Main control panel importable

======================================================================
RUNTIME VALIDATION (DRY-RUN)
======================================================================
[Testing Phase 31]...
  ✓ Phase 31 importable
[Testing Phase 35]...
  ✓ Phase 35 importable
... (9 total runtime checks)

======================================================================
VALIDATION SUMMARY
======================================================================
Total tests: 51
Passed: 51
Failed: 0

[INFO] Validation log saved to: C:\Genesis_System3\storage\ultra\system3_ultra_validation_log.md

[OK] All validations passed!
```

**Expected Status**: 
- Total tests: 51
- Passed: 51
- Failed: 0
- Success rate: 100%

---

## Core Operations

### Option 2: Health Check

**Expected Output**:
```
[ENV] Mode: TEST, Market: NSE
[STORAGE] Test snapshot stored at: storage/history\HEALTHCHECK_YYYYMMDD_HHMMSS.json
```

**Expected Status**: Should complete without errors.

---

### Option 10: Train Angel One Index Options Models

**Expected Output**:
```
=== TRAINING ANGEL ONE INDEX OPTIONS MODELS ===

[LOAD] Loading training data...
[INFO] Training data loaded: X rows

[INFO] Training models for: NIFTY, BANKNIFTY

[NIFTY]
  Training samples: X
  Features: X
  [TRAIN] Training model...
  [SAVE] Model saved to: core/models/angel_one/NIFTY_model.pkl
  [SAVE] Metadata saved to: core/models/angel_one/NIFTY_model_meta.json
  [OK] NIFTY model trained successfully

[BANKNIFTY]
  ... (similar output)

[OK] All models trained successfully
```

**Expected Status**: Should complete with "OK" messages for each underlying.

---

## Ultra Phases 21-30

### Option 84: Phase 21 - Adaptive Risk Engine (ARE)

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 21: ADAPTIVE RISK ENGINE (ARE) ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[INPUT] Sample inputs:
  Volatility: 0.15
  Confidence: 0.75
  Score: 0.30
  Market Regime: NORMAL
  Historical Win Rate: 0.60

[OUTPUT] Risk Evaluation:
  Risk Level: MEDIUM
  Risk Score: 0.45
  Reason: Moderate volatility with good confidence

[OK] Adaptive Risk Engine validated
```

**Expected Status**: Should output risk level (LOW/MEDIUM/HIGH), risk score, and reason.

---

### Option 87: Phase 24 - Confidence Drift Analyzer

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 24: CONFIDENCE DRIFT ANALYZER ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[LOAD] Analyzing X confidence values

=== CONFIDENCE DRIFT ANALYSIS ===
Drift Direction: STABLE | UPWARD | DOWNWARD | INSUFFICIENT_DATA
Drift Strength: 0.XXX
Standard Deviation: 0.XXX
Mean Confidence: 0.XXX
Early Mean: 0.XXX
Late Mean: 0.XXX
Drift Difference: 0.XXX
Sample Size: X

[SAVE] Drift report saved to: storage/reports_ultra/phase24_confidence_drift_report.json

[OK] Confidence Drift Analyzer validated
```

**Expected Status**: 
- Should complete without KeyError
- All fields (early_mean, late_mean, drift_diff, sample_size) should be present
- Should save report to JSON file

---

### Option 93: Phase 30 - Real-Time Calibration Engine (RTCE)

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 30: REAL-TIME CALIBRATION ENGINE (RTCE) ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[INPUT] Sample calibration inputs:
  Risk Level: MEDIUM
  Volatility Impact: STABLE
  Confidence Drift: STABLE
  Sensitivity: 0.25

[OUTPUT] Calibrated Parameters:
  Updated Risk Level: MEDIUM
  Updated SL: 2.5%
  Updated TP: 5.0%
  Updated Quantity: 50

[OK] Real-Time Calibration Engine validated
```

**Expected Status**: Should output calibrated risk level, SL, TP, and quantity.

---

## Ultra Phases 31-38

### Option 94: Phase 31 - Decision Fusion

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 31: ULTRA DECISION FUSION ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[LOAD] Loading live signals...
[LOAD] Loading Ultra artifacts...
[FUSION] Computing fused decisions...

[SAVE] Fused decisions saved to: storage/ultra/phase31_ultra_fused_decisions.csv
[SAVE] Summary saved to: storage/ultra/phase31_ultra_fused_decisions_summary.json

[OK] Phase 31 Ultra Decision Fusion completed
```

**Expected Status**: Should create CSV and JSON output files.

---

### Option 98: Phase 35 - Decision Auditor

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 35: ULTRA DECISION AUDITOR ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[LOAD] Loaded X Ultra decisions
[LOAD] Loaded X shadow trades
[LOAD] Safety limits: max_size=1.0, max_trades/day=50

[SAVE] Audit CSV saved to: storage/ultra/phase35_decision_audit.csv

=== AUDIT SUMMARY ===
Total decisions audited: X
OK: X
WARN: X
BLOCK: X

[SAVE] Audit report MD saved to: storage/ultra/phase35_decision_audit_report.md

[OK] Phase 35 Ultra Decision Auditor completed
```

**Expected Status**: 
- Should audit all decisions
- Should categorize as OK/WARN/BLOCK
- Should create CSV and MD report files

---

### Option 100: Phase 37 - Policy & Risk Monitor

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 37: POLICY & RISK MONITOR ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[LOAD] Loaded thresholds (read-only)
[LOAD] Loaded audit results: X decisions
[LOAD] Loaded shadow trades: X trades

[SAVE] Dashboard saved to: storage/ultra/phase37_policy_risk_dashboard.md

[OK] Phase 37 Policy & Risk Monitor completed
```

**Expected Status**: Should create MD dashboard file.

---

### Option 101: Phase 38 - Governance Summary

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 38: ULTRA GOVERNANCE SUMMARY ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[LOAD] Loading governance inputs...
  - Comparison summary: ✓
  - Promotion plan: ✓
  - Audit results: ✓
  - Policy dashboard: ✓

[SAVE] Governance summary saved to: storage/ultra/phase38_governance_summary.md

[OK] Phase 38 Ultra Governance Summary completed
```

**Expected Status**: Should create MD governance summary file.

---

## Ultra Phases 39-45

### Option 102: Phase 39 - Shadow Campaign

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 39: SHADOW CAMPAIGN ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[CONFIG] Loops: 3, Sleep: 5 seconds

Loop 1/3 started
[OK] Phase 31 Ultra Decision Fusion completed
[OK] Phase 34 Ultra Shadow Execution completed
Sleeping for 5 seconds...

Loop 2/3 started
... (similar output)

[OK] Phase 39 Shadow Campaign completed
[SAVE] Daily summary saved to: storage/ultra/phase39_daily_summary_YYYYMMDD.md
```

**Expected Status**: Should complete all loops and create daily summary.

---

### Option 104: Phase 41 - Promotion Executor

**Expected Output (Without Flag)**:
```
=== SYSTEM3 ULTRA - PHASE 41: PROMOTION EXECUTOR (STAGING ONLY) ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only
[SAFETY] Staging only - no baseline models will be modified

[Phase41] Promotion flag file not found

[ERROR] Promotion flag not found or invalid
[INFO] Create C:\Genesis_System3\storage\config\ultra_promotion_flag.txt with keyword: ALLOW_ULTRA_PROMOTION_STAGING
```

**Expected Status**: Should show error message (expected - safety mechanism).

**Expected Output (With Flag)**:
```
[Phase41] Promotion flag found and valid
[LOAD] Loading promotion plan...
[STAGE] Staging Ultra models to: core/models/angel_one_ultra_staging/
[OK] Phase 41 Promotion Executor completed
```

---

### Option 105: Phase 42 - Take Baseline Snapshot

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 42: SNAPSHOT MANAGER ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[CREATE] Creating baseline snapshot...
[SAVE] Snapshot created: storage/snapshots/snapshot_YYYYMMDD_HHMMSS/
  - Models: X files
  - Configs: X files

[OK] Phase 42 Snapshot created
```

**Expected Status**: Should create timestamped snapshot directory.

---

### Option 106: Phase 42 - List Snapshots

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 42: SNAPSHOT MANAGER ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

=== AVAILABLE SNAPSHOTS ===

1. snapshot_20251130_014500
   Date: 2025-11-30 01:45:00
   Models: 2
   Configs: 3

2. snapshot_20251130_012600
   Date: 2025-11-30 01:26:00
   Models: 2
   Configs: 3

[OK] Phase 42 Snapshot list completed
```

**Expected Status**: Should list all available snapshots with details.

---

### Option 107: Phase 43 - Environment & Broker Guard

**Expected Output**:
```
=== SYSTEM3 ULTRA - PHASE 43: ENVIRONMENT & BROKER GUARD ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[Phase43] Env guard started
[Phase43] Angel System3: ENABLED
[Phase43] Binance System3: DISABLED
[Phase43] Report written to storage/ultra/phase43_env_guard_report.md

[OK] Phase 43 Environment Guard completed
[SAVE] Report: storage/ultra/phase43_env_guard_report.md

[STATUS] Overall: OK | WARN
[WARN] Review warnings in report (if any)
```

**Expected Status**: Should check environment and create report.

---

## System Tools

### Option L: View Latest Logs

**Expected Output**:
```
=== LATEST SYSTEM3 ULTRA LOGS ===

[2025-11-30 01:45:35] [INFO] Completed: core.engine.system3_phase34_ultra_shadow_exec.run_phase34_shadow_once
[2025-11-30 01:45:36] [INFO] Completed: core.engine.system3_phase35_ultra_auditor.run_phase35_audit
[2025-11-30 01:45:38] [INFO] Completed: core.engine.system3_phase36_cull_orchestrator.run_phase36_cull_full_cycle
... (more log entries)
```

**Expected Status**: Should display recent log entries.

---

## Error Handling

### Expected Error Format

**For Recoverable Errors**:
```
[WARN] Error message here
[INFO] Continuing execution...
```

**For Non-Recoverable Errors**:
```
[ERROR] Error message here
Traceback (most recent call last):
  ... (traceback details)
[ERROR] Module execution failed
```

**For Expected Errors (Safety Mechanisms)**:
```
[ERROR] Promotion flag not found or invalid
[INFO] This is expected - safety mechanism working correctly
```

---

## File Outputs

### Expected File Locations

**Ultra Storage**:
- `storage/ultra/phase31_ultra_fused_decisions.csv`
- `storage/ultra/phase35_decision_audit.csv`
- `storage/ultra/phase37_policy_risk_dashboard.md`
- `storage/ultra/phase38_governance_summary.md`
- `storage/ultra/phase39_daily_summary_YYYYMMDD.md`
- `storage/ultra/phase43_env_guard_report.md`

**Ultra Reports**:
- `storage/reports_ultra/phase24_confidence_drift_report.json`
- `storage/reports_ultra/phase29_sensitivity_summary.json`
- `storage/reports_ultra/phase30_calibration_results.csv`

**Snapshots**:
- `storage/snapshots/snapshot_YYYYMMDD_HHMMSS/`

**Validation**:
- `storage/ultra/system3_ultra_validation_log.md`

---

## Success Indicators

### ✅ Successful Execution Indicators

1. **"[OK] ... completed"** - Operation completed successfully
2. **"[SAVE] ... saved to: ..."** - Output file created
3. **"✓" checkmarks** - Validation checks passed
4. **No ERROR messages** (except expected safety errors)
5. **Exit code 0** - Process completed without errors

### ⚠️ Warning Indicators

1. **"[WARN] ..."** - Non-critical warning
2. **"[STATUS] Overall: WARN"** - Review warnings
3. **CSV parsing warnings** - Data format issues (non-blocking)

### ❌ Error Indicators

1. **"[ERROR] ..."** - Critical error (except expected safety errors)
2. **"Traceback"** - Python exception occurred
3. **"Failed: X"** - Validation failures
4. **Exit code != 0** - Process failed

---

## Common Patterns

### Phase Execution Pattern

```
=== SYSTEM3 ULTRA - PHASE X: MODULE NAME ===

[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only

[LOAD] Loading data...
[PROCESS] Processing...
[SAVE] Output saved to: path/to/file

[OK] Phase X completed
```

### Validation Pattern

```
[Testing Phase X]...
  ✓ Phase X importable
```

### Safety Check Pattern

```
[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only
[SAFETY] Staging only - no baseline models will be modified
```

---

## Expected Timings

### Quick Operations (< 1 second)
- Safety status check
- Health check
- Most phase validations
- Menu navigation

### Medium Operations (1-5 seconds)
- Phase 31-38 executions
- Phase 39-43 executions
- Validation suite
- Log viewing

### Long Operations (5+ seconds)
- Model training (Option 10): ~20 seconds
- Shadow campaign (Option 102): Depends on loops
- Full validation: ~1-2 seconds

---

## Validation Checklist

### Before Running Tests

- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] Safety switches confirmed disabled
- [ ] Baseline models exist
- [ ] Storage directories exist

### After Running Tests

- [ ] No critical errors in logs
- [ ] Expected output files created
- [ ] Validation: 51/51 passed
- [ ] All phases show "[OK] ... completed"
- [ ] Safety mechanisms confirmed working

---

## Troubleshooting Guide

### If Output Doesn't Match Expected

1. **Check Safety Status** (Option S)
   - All switches should be DISABLED
   - If enabled, disable them

2. **Run Validation** (Option V)
   - Should show 51/51 passed
   - If failures, check file paths and imports

3. **Check Logs** (Option L)
   - Review recent log entries
   - Look for ERROR messages

4. **Check File Outputs**
   - Verify expected files exist
   - Check file permissions
   - Verify storage directories exist

5. **Check Phase-Specific Issues**
   - Review phase documentation
   - Check required input files
   - Verify data availability

---

**Last Updated**: 2025-11-30  
**Status**: ✅ **COMPLETE**

