# System3 CSV Cleaning Pipeline - Implementation Summary

## Overview

A comprehensive automated cleaning and validation pipeline has been implemented for `dhan_index_ai_signals_with_forward.csv`. The pipeline produces clean, validated CSV files ready for EV analysis, threshold optimization, and model training.

## Files Created

### Core Modules

1. **`core/tools/schema_audit.py`**
   - Performs schema audit and generates documentation
   - Detects duplicate header rows and invalid rows
   - Categorizes columns into logical groups
   - Generates `docs/SYSTEM3_CSV_SCHEMA_AUTOMATED.md`

2. **`core/tools/clean_dhan_signals_csv.py`**
   - Main cleaning pipeline
   - Removes bad rows (duplicate headers, invalid rows)
   - Converts numeric columns
   - Fixes moneyness calculation (CRITICAL)
   - Removes extreme outliers
   - Detects SELL signal anomalies
   - Creates EV-ready subset
   - Generates clean files in `storage/clean/`

3. **`core/tools/validate_clean_csv.py`**
   - Validates cleaned CSV files
   - Checks Greeks, IV, probabilities, moneyness, forward returns
   - Generates `docs/SYSTEM3_CSV_CLEAN_VALIDATION_SUMMARY.md`

### Runner Scripts

4. **`run_clean_signals_and_validate.bat`**
   - Batch file to run the complete pipeline
   - Executes: schema audit → cleaning → validation
   - Prints summary of generated files

## Output Files

### Clean CSV Files

- **`storage/clean/dhan_index_ai_signals_with_forward_clean.csv`**
  - Fully cleaned version of the original CSV
  - Bad rows removed, types converted, moneyness fixed, outliers removed

- **`storage/clean/dhan_index_ai_signals_with_forward_ev_ready.csv`**
  - Subset ready for EV analysis and training
  - All forward returns present, valid signals, no outliers
  - Typically 200-400 rows

- **`storage/clean/dhan_index_ai_signals_sell_anomalies.csv`**
  - SELL signals with extreme positive forward returns
  - Requires manual review
  - May be empty if no anomalies detected

### Documentation Files

- **`docs/SYSTEM3_CSV_SCHEMA_AUTOMATED.md`**
  - Schema overview and column categorization
  - Bad row detection results

- **`docs/SYSTEM3_CSV_CLEAN_VALIDATION_SUMMARY.md`**
  - Validation results for cleaned files
  - Confirmation that critical issues are resolved

## Pipeline Steps

### Step 1: Schema Audit
- Loads CSV and generates statistics
- Detects duplicate header rows
- Categorizes columns
- Generates schema documentation

### Step 2: Cleaning Pipeline
1. **Load raw CSV**
2. **Remove bad rows**:
   - Duplicate headers (signal='signal' or pred_label='pred_label')
   - Completely empty rows
3. **Convert numeric columns** (47 columns)
4. **Fix moneyness** (CRITICAL):
   - Recalculate as `spot / strike` for all rows
5. **Detect SELL anomalies** (before outlier removal)
6. **Remove outliers**:
   - Rows with |forward_return| > 1.0
7. **Create EV-ready subset**:
   - All forward returns present
   - Valid signals
   - Required columns present
8. **Save clean files**

### Step 3: Validation
- Validates Greeks ranges
- Validates IV ranges
- Validates probabilities
- Validates moneyness consistency
- Validates forward returns
- Generates validation report

## Usage

### Run Complete Pipeline

```batch
run_clean_signals_and_validate.bat
```

### Run Individual Steps

```bash
# Schema audit
python -m core.tools.schema_audit

# Cleaning pipeline
python -m core.tools.clean_dhan_signals_csv

# Validation
python -m core.tools.validate_clean_csv
```

## Key Features

### Critical Fixes Implemented

1. **Moneyness Fix** ✅
   - Recalculated as `spot / strike` for all rows
   - No longer trusts original moneyness values

2. **Outlier Removal** ✅
   - Removes rows with |forward_return| > 1.0
   - Prevents skewing of EV analysis

3. **SELL Anomaly Detection** ✅
   - Detects SELL signals with extreme positive forward returns
   - Saves to separate file for manual review

### Data Quality Improvements

- **Type Conversion**: 47 columns converted to proper numeric types
- **Bad Row Removal**: Duplicate headers and invalid rows removed
- **EV-Ready Subset**: Filtered to rows suitable for EV analysis

## Constants and Configuration

All constants are defined at the top of `clean_dhan_signals_csv.py`:

- `OUTLIER_THRESHOLD = 1.0` - Threshold for extreme forward returns
- `NUMERIC_COLUMNS` - List of columns to convert to numeric
- File paths for input/output

## Error Handling

- All modules include try/except blocks
- Errors are logged with traceback
- Pipeline stops on fatal errors
- Non-fatal issues are logged as warnings

## Next Steps

After running the pipeline:

1. **Review SELL anomalies** (if any detected)
2. **Use clean CSV** for general analysis
3. **Use EV-ready CSV** for:
   - Phase 222 (EV analysis)
   - Phase 223 (threshold optimization)
   - Model training

## Status

✅ **Implementation Complete**
- All modules created
- Pipeline tested
- Documentation generated

⚠️ **Known Issue Fixed**
- Index alignment issue in `remove_outliers` function fixed
- All boolean masks now properly aligned with DataFrame index

---

**Last Updated**: 2025-12-04

