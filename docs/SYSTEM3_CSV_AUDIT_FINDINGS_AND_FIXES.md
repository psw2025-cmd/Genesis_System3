# System3 CSV Audit - Findings and Fixes
**File**: `storage/live/dhan_index_ai_signals_with_forward.csv`  
**Analysis Date**: December 4, 2025, 7:30 PM IST  
**Status**: ⚠️ **CRITICAL ISSUES FOUND - FIXES REQUIRED**

---

## 🔍 ULTRA ANALYSIS FINDINGS

### Issue #1: DUPLICATE HEADER ROWS ⚠️ **CRITICAL**

**Evidence**:
- Line 1: Correct header with 80 columns
- Lines 32-33: Duplicate headers (different schema, missing columns)
- Lines 64-66: Duplicate headers
- Lines 277-279: Duplicate headers

**Impact**:
- CSV parsing treats headers as data
- Column misalignment
- `final_score` read from wrong column
- Phase 223 errors (partially fixed with numeric conversion)
- Data corruption

**Root Cause**: Phase 221 or signal generation writing headers multiple times

**Fix**: Remove duplicate headers + fix Phase 221

---

### Issue #2: SCHEMA INCONSISTENCY ⚠️ **CRITICAL**

**Problem**: Two different schemas in same file

**Schema 1** (Line 1 - Correct):
```
underlying,index_exch,opt_exch,spot,expiry,strike,side,symbol,token,ltp,...
```
- Has `strike` at position 6
- Has `ltp` at position 9
- Has `token` at position 8
- 80 columns

**Schema 2** (Lines 32-33 - Incorrect):
```
underlying,index_exch,opt_exch,spot,expiry,,side,symbol,token,,time_to_expiry,...
```
- Missing `strike` (empty position 6)
- Missing `ltp` (empty position 9)
- Missing `token` (empty position 8)
- Different column count

**Impact**:
- Column misalignment
- Data read incorrectly
- Forward returns misaligned

---

### Issue #3: INCOMPLETE DATA ROWS ⚠️ **HIGH**

**Location**: Rows 560-610 (end of file)

**Problem**: Rows with only basic columns, missing all features

**Example Row**:
```
FINNIFTY,NSE,NFO,27890.25,30DEC2025,27950.0,CE,FINNIFTY30DEC2527950CE,61453,437.15,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,HOLD,6.899473710417506e-08,0.9999995467729064,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,2.611109153509009e-07,1.9211617824672583e-07,0.9999995467729064,0.0,,
```

**Missing**:
- All technical indicators (rsi, macd, etc.)
- All trend scores
- All volatility metrics
- **Forward returns** (fwd_ret_1, fwd_ret_3, fwd_ret_5) - **CRITICAL**

**Impact**:
- Phase 222 EV analysis incomplete
- Phase 223 threshold optimization incomplete
- Only ~25-30% of rows usable for analysis

---

### Issue #4: FORWARD RETURNS COVERAGE ⚠️ **HIGH**

**Coverage**: ~25-30% of rows have forward returns

**Distribution**:
- Rows 1-31: ~50% have forward returns
- Rows 34-276: ~50% have forward returns  
- Rows 560+: 0% have forward returns

**Impact**:
- Phase 222 EV analysis based on partial data
- Phase 223 threshold optimization based on partial data
- This explains why only 2 SELL signals found

---

### Issue #5: FINAL_SCORE DATA TYPE ⚠️ **MEDIUM** (FIXED)

**Problem**: `final_score` contains strings
**Status**: ✅ **FIXED** (Phase 223 now converts to numeric)

---

## 🛠️ FIXES CREATED

### Fix Script: `system3_csv_cleanup_fix.py`

**Actions**:
1. ✅ Creates backup of original file
2. ✅ Removes duplicate header rows
3. ✅ Filters incomplete rows
4. ✅ Converts `final_score` to numeric
5. ✅ Analyzes forward returns coverage
6. ✅ Saves cleaned file

**Usage**:
```bash
python system3_csv_cleanup_fix.py
```

**Output**:
- Backup: `dhan_index_ai_signals_with_forward.csv.backup`
- Cleaned: `dhan_index_ai_signals_with_forward.csv.cleaned`

---

### Fix Phase 221: Prevent Header Duplication

**File**: `core/engine/system3_phase221_forward_returns.py`

**Current Code** (Line 165):
```python
df.to_csv(OUTPUT_CSV, index=False)
```

**Issue**: Always writes header, even if appending

**Fix Required**: Check if file exists before writing header

```python
# Check if file exists
if OUTPUT_CSV.exists():
    # Append mode - no header
    df.to_csv(OUTPUT_CSV, mode="a", header=False, index=False)
else:
    # New file - write header
    df.to_csv(OUTPUT_CSV, mode="w", header=True, index=False)
```

**OR**: Always overwrite (current behavior is correct if overwriting)

---

## 📊 IMPACT ANALYSIS

### On Phase 223 (Threshold Optimizer)

**Current**:
- ✅ Runs successfully (after numeric conversion fix)
- ⚠️ Only 2 SELL signals found
- ⚠️ 0 BUY signals found

**Root Cause**: 
- Incomplete data (only ~25-30% usable)
- Duplicate headers causing column misalignment
- Missing forward returns

**After Fixes**:
- Should find more signals
- Better threshold optimization
- More accurate candidates

---

### On Phase 222 (Signal Edge)

**Current**:
- ⚠️ EV analysis based on incomplete data
- ⚠️ Only rows with forward returns analyzed

**After Fixes**:
- Complete EV analysis
- More accurate edge estimation

---

### On Signal Engine

**Current**:
- ⚠️ May read wrong columns (schema mismatch)
- ⚠️ Processes duplicate headers as data

**After Fixes**:
- Correct column reading
- No duplicate header issues

---

## 🎯 RECOMMENDATIONS

### Immediate (Before Next Market Day)

1. **Run Cleanup Script**:
   ```bash
   python system3_csv_cleanup_fix.py
   ```

2. **Review Cleaned File**:
   - Check row count
   - Verify forward returns coverage
   - Confirm no duplicate headers

3. **Replace Original** (if cleaned file is good):
   ```bash
   copy dhan_index_ai_signals_with_forward.csv.cleaned dhan_index_ai_signals_with_forward.csv
   ```

4. **Fix Phase 221**:
   - Prevent header duplication
   - Ensure forward returns for ALL rows

5. **Re-run Phases**:
   - Phase 221 (regenerate with fixes)
   - Phase 222 (verify EV tables)
   - Phase 223 (verify threshold candidates)

### Long-Term

1. **CSV Validation Module**:
   - Pre-write validation
   - Post-write verification
   - Automatic cleanup

2. **Data Quality Monitoring**:
   - Alert on duplicate headers
   - Alert on schema changes
   - Alert on incomplete data

3. **Robust CSV Writer**:
   - Centralized writing logic
   - Header management
   - Schema enforcement

---

## 📋 VALIDATION CHECKLIST

- [ ] Backup created
- [ ] Duplicate headers removed
- [ ] Incomplete rows filtered
- [ ] Forward returns coverage analyzed
- [ ] Cleaned file reviewed
- [ ] Original file replaced (if cleaned is good)
- [ ] Phase 221 fixed (prevent header duplication)
- [ ] Phase 221 re-run (regenerate with fixes)
- [ ] Phase 222 re-run (verify EV tables)
- [ ] Phase 223 re-run (verify threshold candidates)

---

**Report Generated**: December 4, 2025, 7:30 PM IST  
**Status**: ⚠️ **CRITICAL ISSUES FOUND - CLEANUP SCRIPT READY**

