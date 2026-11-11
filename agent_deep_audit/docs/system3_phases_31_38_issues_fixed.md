# System3 Phases 31-38 Blueprint: Issues Fixed

**Date**: 2025-11-29  
**Status**: ✅ **All Issues Identified and Corrected**

---

## Issues Found and Fixed

### 1. ✅ Menu Option Numbers - FIXED
**Issue**: Blueprint specified menu options 48-55, but these are already taken (48-93 are used).

**Fix**: Updated all menu options to 94-101:
- Phase 31: Menu option 94 (was 48)
- Phase 32: Menu option 95 (was 49)
- Phase 33: Menu option 96 (was 50)
- Phase 34: Menu option 97 (was 51)
- Phase 35: Menu option 98 (was 52)
- Phase 36: Menu option 99 (was 53)
- Phase 37: Menu option 100 (was 54)
- Phase 38: Menu option 101 (was 55)

---

### 2. ✅ Input File Paths - FIXED
**Issue**: Blueprint referenced incorrect file paths for Phase 21-30 outputs:
- `storage/ultra/phase21_risk_scores.csv` (doesn't exist)
- `storage/ultra/phase22_sl_tp_grid.csv` (doesn't exist)
- `storage/ultra/phase23_position_size_table.csv` (doesn't exist)
- `storage/ultra/phase26_regime_tags.csv` (doesn't exist)

**Fix**: Updated to correct paths:
- `storage/reports_ultra/phase21_risk_evaluations.csv` ✅
- `storage/reports_ultra/phase24_confidence_drift_report.json` ✅
- `storage/reports_ultra/phase29_sensitivity_summary.json` ✅
- `storage/reports_ultra/phase30_calibration_results.csv` ✅
- Added note that Phases 22, 23, 25, 26, 27 provide runtime calculations, not stored files

---

### 3. ✅ Missing Implementation Conventions Section - ADDED
**Issue**: Blueprint mentioned adding section 0.4 but it wasn't in the document.

**Fix**: Added complete section 0.4 with:
- Main entrypoint requirements
- Logging conventions
- Safety rules (what not to modify)
- Error handling requirements

---

### 4. ✅ File Naming Convention Clarification - ADDED
**Issue**: Unclear whether phases 31-38 should be in `core/ultra/` or `core/engine/`.

**Fix**: Added note that Phases 31-38 are integration phases, so they go in `core/engine/` (not `core/ultra/` like phases 21-30).

---

### 5. ✅ Reserved Phases Note - ADDED
**Issue**: Document title says "31-38" but there was a reference to "31-40" in the text.

**Fix**: 
- Added note at top: "Phases 39–40 are intentionally reserved for future global consolidation"
- Fixed reference in "How to Use This MD" section

---

## Summary of Changes

| Issue | Status | Location |
|-------|--------|----------|
| Menu options 48-55 → 94-101 | ✅ Fixed | All phase sections |
| Input file paths | ✅ Fixed | Phase 31.2 |
| Section 0.4 conventions | ✅ Added | After section 0.3 |
| File location clarification | ✅ Added | Phase 31.4 |
| Reserved phases note | ✅ Added | Document header |

---

## Blueprint Status

✅ **READY FOR IMPLEMENTATION**

All issues have been corrected. The blueprint is now:
- Consistent with existing menu numbering
- Using correct file paths
- Including all required conventions
- Clear about file locations
- Properly documenting reserved phases

---

**Next Steps**: Proceed with implementation of Phases 31-38 according to the corrected blueprint.

