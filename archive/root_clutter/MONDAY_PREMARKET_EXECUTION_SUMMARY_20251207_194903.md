# MONDAY PRE-MARKET EXECUTION SUMMARY

**Date:** 2025-12-07
**Time:** 19:49:23
**Verdict:** GREEN

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

### ✅ Step 6: Block Test 331-360

**Status:** PASS

- Exit code: 0
- Patterns found: True
- Output lines: stdout=1, stderr=280

### ℹ️ Step 7: File Validation

**Status:** INFO


**Details:**
```json
{
  "storage/live/angel_index_ai_signals.csv": {
    "exists": true,
    "size_bytes": 129063,
    "age_minutes": 492.7
  },
  "storage/live/angel_index_ai_signals_curated.csv": {
    "exists": true,
    "size_bytes": 7369,
    "age_minutes": 492.7
  },
  "storage/live/angel_index_ai_signals_with_forward.csv": {
    "exists": true,
    "size_bytes": 7668,
    "age_minutes": 492.7
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

**GREEN**

All steps passed successfully. System ready for market open.

---

## Next Steps

1. ✅ Safety confirmed - all flags remain False
2. ✅ Models loaded/trained successfully
3. ✅ Signals pipeline operational
4. ✅ Block test 331-360 passed
5. 🚀 Ready to start Option 11 (Live AI Signals Loop) at 09:10 AM

---

**Report generated:** 2025-12-07 19:49:23
**Script:** system3_monday_premarket_sequence.py