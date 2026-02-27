# SYSTEM3 PHASES 1-200: WARN/ERROR SUMMARY

**Report Generated:** 2025-12-07T02:24:20.767319

---

## Error Summary

### Total Errors: 3

**Critical Phase Failures:**


#### Phase 165
- **Issue:** Syntax Error: invalid syntax (<unknown>, line 24)
- **File:** system3_phase165_risk-reward_analysis.py
- **Severity:** HIGH
- **Action:** MUST FIX BEFORE PRODUCTION

#### Phase 167
- **Issue:** Syntax Error: invalid syntax (<unknown>, line 24)
- **File:** system3_phase167_time-of-day_analysis.py
- **Severity:** HIGH
- **Action:** MUST FIX BEFORE PRODUCTION

#### Phase 103
- **Issue:** Phase file not found
- **File:** Unknown
- **Severity:** CRITICAL
- **Action:** MUST FIX BEFORE PRODUCTION


---

## Warning Summary

### Total Warnings: 26

**Phases with Warnings:**


### Safety Check Warnings

- Phase 101: Incomplete safety checks: found 1/3
- Phase 102: Incomplete safety checks: found 0/3
- Phase 104: Incomplete safety checks: found 0/3
- Phase 105: Incomplete safety checks: found 0/3
- Phase 106: Incomplete safety checks: found 0/3
- Phase 107: Incomplete safety checks: found 1/3
- Phase 108: Incomplete safety checks: found 0/3
- Phase 109: Incomplete safety checks: found 0/3
- Phase 110: Incomplete safety checks: found 0/3
- Phase 111: Incomplete safety checks: found 0/3


---

## Action Items

### CRITICAL (Do Immediately)
1. **Phase 103 Missing** - Reconstruct or locate order ledger phase
2. **Phase 165 Syntax Error** - Fix line 24 syntax
3. **Phase 167 Syntax Error** - Fix line 24 syntax

### HIGH (Before Next Release)
1. Update deprecated API calls in 26 phases
2. Complete safety checks in phases 101-130
3. Consolidate duplicate phase files

### MEDIUM (Before Production)
1. Test Phase 107 (live execution) with broker API
2. Validate all import chains
3. Add missing docstrings

### LOW (Polish)
1. Standardize all function names
2. Add type hints
3. Improve test coverage

---

**Summary Date:** 2025-12-07T02:24:20.767319