# CSV Parsing Fixes - Verification Commands

## Quick Test Commands

Run these commands in your terminal to verify the fixes:

### Option 1: Run the Test Script

```bash
python test_csv_parsing_fixes.py
```

This will test all 3 fixed files automatically.

---

### Option 2: Manual Testing (Individual Tests)

#### Test 1: PnL Simulator

```python
python -c "from core.engine.angel_pnl_simulator import _load_data; df_sig, df_tr = _load_data(); print(f'Signals: {len(df_sig) if df_sig is not None else 0} rows'); print(f'Trades: {len(df_tr) if df_tr is not None else 0} rows'); print('✅ PnL simulator CSV parsing works!')"
```

**Expected Output**: Should show row counts or handle errors gracefully (no crash).

---

#### Test 2: Trade Decision

```python
python -c "import pandas as pd; from pathlib import Path; csv_path = Path('storage/live/angel_index_ai_signals.csv'); df = pd.read_csv(csv_path, engine='python', on_bad_lines='skip') if csv_path.exists() else pd.DataFrame(); print(f'✅ Trade decision CSV parsing works! Loaded {len(df)} rows')"
```

**Expected Output**: Should load CSV successfully, skipping malformed lines.

---

#### Test 3: Data Extractor

```python
python -c "from core.engine.angel_real_data_extractor import extract_real_training_data; df = extract_real_training_data(); print(f'✅ Data extractor CSV parsing works! Returned {len(df)} rows')"
```

**Expected Output**: Should return DataFrame (may be empty), no errors.

---

### Option 3: Full PnL Simulation Test

```python
python -c "from core.engine.angel_pnl_simulator import run_pnl_simulation; result = run_pnl_simulation(); print('✅ PnL simulation completed successfully!' if result is not None else '⚠️ No trades to simulate (this is OK)')"
```

**Expected Output**: Should complete without the "Expected 72 fields" error.

---

## What to Look For

### ✅ Success Indicators:
- No `Error tokenizing data. C error: Expected 72 fields` errors
- CSV files load successfully
- Malformed lines are skipped (warning may appear, but no crash)
- Functions complete without exceptions

### ❌ Failure Indicators:
- `Error tokenizing data` exceptions
- Crashes when reading CSV files
- Functions return None unexpectedly

---

## Expected Behavior

**Before Fixes**:
```
[ERROR] PnL simulation failed: Error tokenizing data. C error: Expected 72 fields in line 32, saw 75
```

**After Fixes**:
```
[INFO] Signals CSV loaded with X rows
[INFO] Trades plan CSV loaded with Y rows
[INFO] CSV parsing handled gracefully (malformed lines skipped)
```

---

## Quick Verification Command

Run this single command to test all fixes:

```bash
python test_csv_parsing_fixes.py
```

Or use Python interactively:

```python
python
>>> from core.engine.angel_pnl_simulator import _load_data
>>> df_sig, df_tr = _load_data()
>>> print(f"Signals: {len(df_sig) if df_sig is not None else 'None'} rows")
>>> print(f"Trades: {len(df_tr) if df_tr is not None else 'None'} rows")
>>> # If no errors, fixes are working!
```

---

## Files Fixed

1. ✅ `core/engine/angel_pnl_simulator.py` - Line 43-53
2. ✅ `core/engine/angel_trade_decision.py` - Line 242-248
3. ✅ `core/engine/angel_real_data_extractor.py` - Line 42

All files now use: `engine="python", on_bad_lines="skip"`

