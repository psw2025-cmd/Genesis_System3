# MONDAY PRE-MARKET EXECUTION SUMMARY

**Date:** 2025-12-07
**Time:** 19:16:23
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

### ⚠️ Step 2: Train/Verify Models (Option 10)

**Status:** WARN

- Exit code: 1
- Patterns found: False
- Missing patterns: ['MODEL ACCURACY', 'saved']
- Output lines: stdout=1, stderr=6

### ✅ Step 3: Core Boot / Generate Signals (Option 1)

**Status:** PASS

- Exit code: 0
- Patterns found: True
- Output lines: stdout=4, stderr=1

### ❌ Step 4: Data Pipeline Test (Option 3)

**Status:** FAIL

- Exit code: 1
- Patterns found: False
- Missing patterns: ['Test completed', 'saved at']
- Blocking errors: ['error']
- Output lines: stdout=1, stderr=12

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

**Report generated:** 2025-12-07 19:16:23
**Script:** system3_monday_premarket_sequence.py