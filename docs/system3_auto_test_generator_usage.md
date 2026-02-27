# System3 Auto-Test Generator - Usage Guide

**Location**: `core/tools/system3_auto_test_generator.py`  
**Convenience Script**: `system3_generate_tests.py` (root directory)

---

## 🚀 QUICK START

### Option 1: Use Convenience Script (Recommended)

```bash
python system3_generate_tests.py
```

### Option 2: Run Directly

```bash
python core/tools/system3_auto_test_generator.py
```

### Option 3: Integrated (Automatic)

The test generator runs automatically when you execute:

```bash
python system3_universal_autophase_engine.py
```

It runs as **Step 7** in the full cycle.

---

## 📊 WHAT IT DOES

1. **Loads Phase Registry**: Reads `storage/meta/system3_phase_registry.json`
2. **Generates Individual Tests**: Creates `test_phase_XXX.py` for each implemented phase
3. **Generates Range Tests**: Creates `test_phases_XXX_YYY.py` for phase ranges
4. **Saves Tests**: All tests saved to `tests/auto/system3_generated_tests/`

---

## 📁 OUTPUT LOCATION

All generated tests are saved to:
```
tests/auto/system3_generated_tests/
```

### Example Files Generated

- `test_phase_201.py`
- `test_phase_202.py`
- ...
- `test_phase_300.py`
- `test_phases_201_230.py`
- `test_phases_231_260.py`
- `test_phases_261_300.py`

---

## 🧪 RUNNING GENERATED TESTS

### Run Individual Test

```bash
python tests/auto/system3_generated_tests/test_phase_201.py
```

### Run Range Test

```bash
python tests/auto/system3_generated_tests/test_phases_201_230.py
```

### Run All Tests with unittest

```bash
python -m unittest discover tests/auto/system3_generated_tests/ -v
```

---

## 📈 EXPECTED OUTPUT

### Generator Output

```
======================================================================
SYSTEM3 AUTO-TEST GENERATOR
======================================================================
Start Time: 2025-12-03T00:00:00

Generating tests for all implemented phases...
Generated test for phase 201: tests/auto/system3_generated_tests/test_phase_201.py
Generated test for phase 202: tests/auto/system3_generated_tests/test_phase_202.py
...

======================================================================
GENERATION SUMMARY
======================================================================
Individual Tests Generated: 233
Range Tests Generated: 3
Test Directory: tests/auto/system3_generated_tests/

======================================================================
GENERATION COMPLETE
======================================================================
```

---

## ✅ VERIFICATION

After generation, verify tests were created:

```bash
dir tests\auto\system3_generated_tests\test_phase_*.py
```

You should see test files for all implemented phases.

---

## 🔧 TROUBLESHOOTING

### Issue: "No such file or directory"

**Solution**: Make sure you're in the project root (`C:\Genesis_System3`)

### Issue: "Module not found"

**Solution**: Ensure virtual environment is activated:
```bash
venv\Scripts\activate
```

### Issue: "Registry not found"

**Solution**: Run the phase registry builder first:
```bash
python system3_phase_registry_builder.py
```

---

## 📋 STATUS

- ✅ **Implementation**: Complete
- ✅ **Convenience Script**: Created (`system3_generate_tests.py`)
- ✅ **Documentation**: Complete
- ✅ **Ready**: For immediate use

---

**Last Updated**: 2025-12-03

