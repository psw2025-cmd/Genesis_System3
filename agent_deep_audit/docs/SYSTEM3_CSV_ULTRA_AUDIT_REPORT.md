# System3 CSV Ultra Audit Report - Comprehensive Quality Control
**File Analyzed**: `storage/live/dhan_index_ai_signals_with_forward.csv`  
**Analysis Date**: December 4, 2025, 7:30 PM IST  
**Status**: ⚠️ **CRITICAL ISSUES FOUND**

---

## Executive Summary

**Total Rows**: ~610 rows (estimated)  
**Total Columns**: 80 columns  
**Critical Issues**: 5  
**Data Quality**: ⚠️ **POOR** (duplicate headers, missing data, schema inconsistencies)

---

## 🚨 CRITICAL ISSUES FOUND

### Issue #1: DUPLICATE HEADER ROWS ⚠️ **CRITICAL**

**Location**: Lines 32-33, 64-66, 277-279  
**Problem**: Header row appears multiple times in the middle of data  
**Impact**: 
- CSV parsing will treat headers as data rows
- Column misalignment
- Data corruption
- Phase 223 and other phases will fail or produce incorrect results

**Evidence**:
```
Line 1:  underlying,index_exch,opt_exch,spot,expiry,strike,side,symbol,token,ltp,...
Line 32: underlying,index_exch,opt_exch,spot,expiry,,side,symbol,token,,time_to_expiry,...
Line 33: underlying,index_exch,opt_exch,spot,expiry,,side,symbol,token,,time_to_expiry,...
```

**Root Cause**: Likely Phase 221 or signal generation appending data incorrectly

**Fix Required**: 
- Remove duplicate header rows
- Fix Phase 221 to prevent header duplication
- Add header detection logic to skip duplicate headers

---

### Issue #2: SCHEMA INCONSISTENCY ⚠️ **CRITICAL**

**Problem**: Different header schemas in the same file

**Schema 1** (Line 1 - Correct):
- Has `strike` column (position 6)
- Has `ltp` column (position 9)
- Has `token` column (position 8)
- 80 columns total

**Schema 2** (Lines 32-33 - Incorrect):
- Missing `strike` column (empty position 6)
- Missing `ltp` column (empty position 9)
- Missing `token` column (empty position 8)
- Different column count

**Impact**:
- Column misalignment
- Data read incorrectly
- `final_score` may be read from wrong column
- Forward returns may be misaligned

**Fix Required**:
- Standardize schema
- Remove rows with incorrect schema
- Fix data generation to use consistent schema

---

### Issue #3: INCOMPLETE DATA ROWS ⚠️ **HIGH**

**Location**: Rows 560+  
**Problem**: Rows with only basic columns populated, missing all feature columns

**Example** (Line 560):
```
FINNIFTY,NSE,NFO,27890.25,30DEC2025,27950.0,CE,FINNIFTY30DEC2527950CE,61453,437.15,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,HOLD,6.899473710417506e-08,0.9999995467729064,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,2.611109153509009e-07,1.9211617824672583e-07,0.9999995467729064,0.0,,
```

**Missing Columns**:
- All technical indicators (rsi, macd, etc.)
- All trend scores
- All volatility metrics
- All momentum scores
- Most ML predictions
- **Forward returns** (fwd_ret_1, fwd_ret_3, fwd_ret_5) - **CRITICAL**

**Impact**:
- Phase 222 (Signal Edge) will have incomplete data
- Phase 223 (Threshold Optimizer) will have incomplete data
- EV analysis will be incorrect
- Threshold optimization will be based on incomplete data

**Fix Required**:
- Filter out incomplete rows
- Fix data generation to ensure all columns populated
- Add data completeness validation

---

### Issue #4: FORWARD RETURNS INCONSISTENCY ⚠️ **HIGH**

**Problem**: Forward returns (`fwd_ret_1`, `fwd_ret_3`, `fwd_ret_5`) are not consistently populated

**Analysis**:
- **Rows 1-31**: Forward returns populated (some rows)
- **Rows 32-33**: Duplicate headers (no data)
- **Rows 34-276**: Forward returns populated (some rows)
- **Rows 277-279**: Duplicate headers (no data)
- **Rows 560+**: Forward returns **MISSING** (all empty)

**Coverage Estimate**:
- ~50% of rows have forward returns
- ~50% missing forward returns

**Impact**:
- Phase 222 (Signal Edge) will have incomplete EV analysis
- Phase 223 (Threshold Optimizer) will have incomplete data
- Threshold optimization will be based on partial data
- This explains why Phase 223 found only 2 SELL signals

**Fix Required**:
- Ensure Phase 221 populates forward returns for ALL rows
- Add validation to check forward return coverage
- Filter out rows without forward returns before analysis

---

### Issue #5: FINAL_SCORE DATA TYPE ISSUE ⚠️ **MEDIUM**

**Problem**: `final_score` column contains string values (already fixed in Phase 223)

**Status**: ✅ **FIXED** (Phase 223 now converts to numeric)

**Impact**: 
- Was causing Phase 223 errors
- Now handled with `pd.to_numeric()`

---

## 📊 DETAILED ANALYSIS

### Column Structure Analysis

**Expected Columns** (from Phase 221):
1. Base columns from curated CSV (72 columns)
2. Forward return columns (3 columns): `fwd_ret_1`, `fwd_ret_3`, `fwd_ret_5`
3. **Total**: 75 columns

**Actual Columns** (Line 1):
- 80 columns (includes additional columns)

**Column Mismatch**: 5 extra columns (may be from different source)

---

### Data Completeness Analysis

**Rows with Complete Data** (Rows 1-31, 34-276):
- ✅ All feature columns populated
- ✅ Forward returns populated (some rows)
- ✅ `final_score` present
- ✅ Signals present

**Rows with Incomplete Data** (Rows 560+):
- ⚠️ Only basic columns populated
- ❌ Feature columns empty
- ❌ Forward returns **MISSING**
- ⚠️ `final_score` may be present but other features missing

**Duplicate Headers** (Rows 32-33, 64-66, 277-279):
- ❌ No data, just headers
- ❌ Will cause parsing errors

---

### Forward Returns Coverage

**Rows with Forward Returns**:
- Rows 1-31: ~50% have forward returns
- Rows 34-276: ~50% have forward returns
- Rows 560+: 0% have forward returns

**Total Coverage**: ~25-30% of all rows

**Impact on Phase 223**:
- Only rows with forward returns are useful for threshold optimization
- This explains why only 2 SELL signals found (very small dataset)

---

### final_score Distribution

**From Sample Data**:
- Most scores are negative (bearish bias)
- Range: approximately -0.35 to +0.15
- Mean: ~0.0 (slightly negative)
- No scores >= 0.4 (explains 0 BUY signals)

**Data Quality**:
- ✅ Scores are numeric (after conversion)
- ✅ Scores are reasonable range
- ⚠️ Strong bearish bias (may be market condition or data issue)

---

## 🔍 ROOT CAUSE ANALYSIS

### Why Duplicate Headers?

**Possible Causes**:
1. **Phase 221 Appending Mode**: If Phase 221 appends to file, it may write header each time
2. **Multiple Writers**: Multiple processes writing to same file
3. **File Corruption**: File was corrupted during write
4. **Append Logic Error**: Code appends header instead of data

**Most Likely**: Phase 221 writes header on each run instead of checking if file exists

---

### Why Incomplete Rows?

**Possible Causes**:
1. **Different Data Source**: Rows 560+ from different snapshot (less complete)
2. **Feature Generation Failed**: Feature generation failed for these rows
3. **Forward Returns Not Calculated**: Phase 221 didn't calculate forward returns for these rows
4. **Data Merge Issue**: Data merged from multiple sources incorrectly

**Most Likely**: Different snapshot with incomplete feature generation

---

## 🛠️ FIXES REQUIRED

### Fix #1: Remove Duplicate Headers

**Action**: Clean CSV file to remove duplicate header rows

**Code**:
```python
# Read CSV
df = pd.read_csv(CSV_FILE, engine="python", on_bad_lines="skip")

# Remove rows that are duplicate headers
header_row = df.columns.tolist()
df = df[~df.astype(str).apply(lambda x: x.tolist() == header_row, axis=1)]

# Save cleaned CSV
df.to_csv(CSV_FILE, index=False)
```

---

### Fix #2: Fix Phase 221 Header Logic

**File**: `core/engine/system3_phase221_forward_returns.py`

**Current Issue**: May be writing header on each append

**Fix**: Check if file exists before writing header

```python
# Before writing
if OUTPUT_CSV.exists():
    # Append mode - no header
    df.to_csv(OUTPUT_CSV, mode="a", header=False, index=False)
else:
    # New file - write header
    df.to_csv(OUTPUT_CSV, mode="w", header=True, index=False)
```

---

### Fix #3: Filter Incomplete Rows

**Action**: Add validation to filter out incomplete rows

**Code**:
```python
# Filter rows with missing critical columns
critical_cols = ["final_score", "fwd_ret_1", "fwd_ret_3", "fwd_ret_5"]
df_complete = df.dropna(subset=critical_cols)

# Use only complete rows for analysis
```

---

### Fix #4: Ensure Forward Returns for All Rows

**File**: `core/engine/system3_phase221_forward_returns.py`

**Issue**: Forward returns not calculated for all rows

**Fix**: Ensure forward returns calculated for ALL rows, not just some

---

## 📈 IMPACT ASSESSMENT

### Impact on Phase 223 (Threshold Optimizer)

**Current State**:
- ✅ Phase 223 runs successfully (after fixes)
- ⚠️ Only 2 SELL signals found (due to incomplete data)
- ⚠️ 0 BUY signals (due to incomplete data + bearish bias)

**After Fixes**:
- Should find more signals (with complete data)
- Better threshold optimization
- More accurate candidate selection

---

### Impact on Phase 222 (Signal Edge)

**Current State**:
- ⚠️ EV analysis based on incomplete data
- ⚠️ Only ~25-30% of rows have forward returns
- ⚠️ EV tables may be inaccurate

**After Fixes**:
- Complete EV analysis
- More accurate edge estimation
- Better threshold proposals

---

### Impact on Signal Engine

**Current State**:
- ⚠️ May read incorrect columns (due to schema mismatch)
- ⚠️ May process duplicate header rows as data
- ⚠️ May miss signals due to incomplete data

**After Fixes**:
- Correct column reading
- No duplicate header issues
- Complete signal generation

---

## 🎯 RECOMMENDATIONS

### Immediate Actions (Before Next Market Day)

1. **Clean CSV File**:
   - Remove duplicate header rows
   - Filter incomplete rows
   - Standardize schema

2. **Fix Phase 221**:
   - Prevent header duplication
   - Ensure forward returns for ALL rows
   - Add data completeness validation

3. **Add CSV Validation**:
   - Check for duplicate headers
   - Validate schema consistency
   - Check data completeness

4. **Test Phases**:
   - Re-run Phase 221
   - Re-run Phase 222
   - Re-run Phase 223
   - Verify results

### Long-Term Improvements

1. **CSV Writer Module**:
   - Centralized CSV writing logic
   - Header management
   - Schema validation

2. **Data Quality Checks**:
   - Pre-write validation
   - Post-write verification
   - Automatic cleanup

3. **Monitoring**:
   - Alert on duplicate headers
   - Alert on schema changes
   - Alert on incomplete data

---

## 📋 VALIDATION CHECKLIST

- [ ] Duplicate headers removed
- [ ] Schema standardized
- [ ] Incomplete rows filtered
- [ ] Forward returns populated for all rows
- [ ] Phase 221 fixed (no header duplication)
- [ ] Phase 222 re-run (verify EV tables)
- [ ] Phase 223 re-run (verify threshold candidates)
- [ ] Signal engine tested (verify signal generation)

---

## 📊 STATISTICS

**File Size**: ~200 KB (estimated)  
**Total Rows**: ~610  
**Duplicate Headers**: 6-9 rows  
**Incomplete Rows**: ~50 rows (rows 560+)  
**Rows with Forward Returns**: ~150-180 rows (25-30%)  
**Complete Data Rows**: ~400-450 rows (65-75%)

---

**Report Generated**: December 4, 2025, 7:30 PM IST  
**Status**: ⚠️ **CRITICAL ISSUES FOUND - FIXES REQUIRED**

