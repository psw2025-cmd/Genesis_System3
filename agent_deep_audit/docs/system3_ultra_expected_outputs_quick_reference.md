# System3 Ultra - Expected Outputs Quick Reference

**Quick Reference Guide** for validating System3 Ultra operations.

---

## ✅ Success Indicators

### Standard Success Pattern
```
[OK] Phase X completed
[SAVE] Output saved to: path/to/file
```

### Validation Success
```
Total tests: 51
Passed: 51
Failed: 0
[OK] All validations passed!
```

---

## Key Operations

### Option S: Safety Status
**Expected**: All switches `False (❌ DISABLED)`

### Option V: Validation
**Expected**: `51/51 passed, 0 failed`

### Option 87: Phase 24
**Expected**: No KeyError, all fields present
```
Early Mean: 0.XXX
Late Mean: 0.XXX
Drift Difference: 0.XXX
Sample Size: X
[OK] Confidence Drift Analyzer validated
```

### Option 98: Phase 35
**Expected**: Audit summary with counts
```
Total decisions audited: X
OK: X
WARN: X
BLOCK: X
[OK] Phase 35 Ultra Decision Auditor completed
```

### Option 100: Phase 37
**Expected**: Dashboard file created
```
[SAVE] Dashboard saved to: storage/ultra/phase37_policy_risk_dashboard.md
[OK] Phase 37 Policy & Risk Monitor completed
```

### Option 101: Phase 38
**Expected**: Governance summary created
```
[SAVE] Governance summary saved to: storage/ultra/phase38_governance_summary.md
[OK] Phase 38 Ultra Governance Summary completed
```

---

## ⚠️ Expected Warnings

### Option 71: CSV Parsing
**Expected**: `[WARN] Failed to load synthetic: Error tokenizing data...`
**Status**: Non-blocking, module continues

### Option 104: Promotion Flag
**Expected**: `[ERROR] Promotion flag not found or invalid`
**Status**: Expected - safety mechanism working

### Option 107: Environment Guard
**Expected**: `[STATUS] Overall: WARN`
**Status**: Review warnings, but execution completed

---

## ❌ Error Indicators

### Critical Errors (Should NOT occur)
- `KeyError: ...` (except fixed Phase 24)
- `Traceback` with exceptions
- `Failed: X` in validation
- Missing required output files

### Expected Errors (Safety)
- Promotion flag not found (Option 104)
- Interactive input EOFError (Option 83 in automated tests)

---

## File Output Checklist

### After Running Phases 31-38
- [ ] `storage/ultra/phase31_ultra_fused_decisions.csv`
- [ ] `storage/ultra/phase35_decision_audit.csv`
- [ ] `storage/ultra/phase37_policy_risk_dashboard.md`
- [ ] `storage/ultra/phase38_governance_summary.md`

### After Running Validation
- [ ] `storage/ultra/system3_ultra_validation_log.md`

### After Running Phase 42
- [ ] `storage/snapshots/snapshot_YYYYMMDD_HHMMSS/`

---

## Quick Validation

### Run These to Verify System
1. **Option S** → All switches DISABLED ✅
2. **Option V** → 51/51 passed ✅
3. **Option 98** → Phase 35 completes ✅
4. **Option 100** → Phase 37 completes ✅
5. **Option 101** → Phase 38 completes ✅

**If all pass**: System is operational ✅

---

**Full Guide**: `docs/system3_ultra_expected_outputs.md`

