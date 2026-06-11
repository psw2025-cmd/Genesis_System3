# MONDAY PRE-MARKET EXECUTION SUMMARY

**Date:** 2025-12-07
**Time:** 19:24:54
**Verdict:** RED

---

## Sequence Results

### ✅ Step 0: Safety Flag Check

**Status:** PASS

- All flags verified False

### ✅ Step 1: Verify Instruments (Option 5)

**Status:** PASS

- Exit code: 0
- Patterns found: True
- Output lines: stdout=12, stderr=1

### ✅ Step 2: Train/Verify Models (Option 10)

**Status:** PASS

- Exit code: 0
- Patterns found: True
- Output lines: stdout=90, stderr=1

### ✅ Step 3: Core Boot / Generate Signals (Option 1)

**Status:** PASS

- Exit code: 0
- Patterns found: True
- Output lines: stdout=4, stderr=1

### ✅ Step 4: Data Pipeline Test (Option 3)

**Status:** PASS

- Exit code: 0
- Patterns found: True
- Output lines: stdout=6, stderr=1

### ✅ Step 5: Real Data Extractor (Option 33)

**Status:** PASS

- Exit code: 0
- Patterns found: True
- Output lines: stdout=5, stderr=1

### ❌ Step 6: Block Test 331-360

**Status:** FAIL

- Exit code: 0
- Patterns found: True
- Blocking errors: ['ERROR: ', 'FAIL']
- Output lines: stdout=1, stderr=280

### ℹ️ Step 7: File Validation

**Status:** INFO


**Details:**
```json
{
  "storage/live/angel_index_ai_signals.csv": {
    "exists": true,
    "size_bytes": 129063,
    "age_minutes": 468.2
  },
  "storage/live/angel_index_ai_signals_curated.csv": {
    "exists": true,
    "size_bytes": 7369,
    "age_minutes": 468.2
  },
  "storage/live/angel_index_ai_signals_with_forward.csv": {
    "exists": true,
    "size_bytes": 7668,
    "age_minutes": 468.2
  },
  "core/models/angel_one/NIFTY_model.pkl": {
    "exists": true,
    "size_bytes": 279081
  },
  "core/models/angel_one/BANKNIFTY_model.pkl": {
    "exists": true,
    "size_bytes": 274329
  },
  "core/models/angel_one/FINNIFTY_model.pkl": {
    "exists": true,
    "size_bytes": 216569
  },
  "core/models/angel_one/MIDCPNIFTY_model.pkl": {
    "exists": true,
    "size_bytes": 285705
  },
  "core/models/angel_one/SENSEX_model.pkl": {
    "exists": true,
    "size_bytes": 213977
  }
}
```

---

## Verdict Explanation

**RED**

Critical failures detected. DO NOT proceed to market open.
Review failed steps above and resolve issues before retrying.

---

## Next Steps

1. ❌ DO NOT start Option 11
2. Review FAIL steps above
3. Fix blocking issues
4. Rerun this script: `python system3_monday_premarket_sequence.py`
5. Only proceed when verdict is GREEN or YELLOW

---

**Report generated:** 2025-12-07 19:24:54
**Script:** system3_monday_premarket_sequence.py