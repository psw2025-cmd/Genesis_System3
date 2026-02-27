"""
Test script for phases 261-300
Verifies that all phases can be imported and run without errors.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Test phases
test_results = {}
errors = []

for phase_num in range(261, 301):
    try:
        # Find phase file
        phase_files = list((PROJECT_ROOT / "core" / "engine").glob(f"system3_phase{phase_num}_*.py"))
        if phase_files:
            file_stem = phase_files[0].stem
            module_name = f"core.engine.{file_stem}"
            func_name = f"run_phase{phase_num}"
            
            # Import and test
            module = __import__(module_name, fromlist=[func_name])
            func = getattr(module, func_name)
            
            # Run phase
            result = func()
            
            test_results[phase_num] = {
                "status": result.get("status", "UNKNOWN"),
                "details": result.get("details", ""),
                "has_outputs": "outputs" in result,
                "has_errors": len(result.get("errors", [])) > 0,
            }
        else:
            test_results[phase_num] = {
                "status": "NOT FOUND",
                "details": "Phase file not found",
                "has_outputs": False,
                "has_errors": True,
            }
            errors.append(f"Phase {phase_num}: File not found")
    except Exception as e:
        test_results[phase_num] = {
            "status": "ERROR",
            "details": str(e),
            "has_outputs": False,
            "has_errors": True,
        }
        errors.append(f"Phase {phase_num}: {e}")

# Print results
print("=" * 70)
print("PHASES 261-300 TEST RESULTS")
print("=" * 70)

ok_count = sum(1 for r in test_results.values() if r["status"] == "OK")
warn_count = sum(1 for r in test_results.values() if r["status"] == "WARN")
error_count = sum(1 for r in test_results.values() if r["status"] == "ERROR")
not_found = sum(1 for r in test_results.values() if r["status"] == "NOT FOUND")

print(f"\nOK: {ok_count}")
print(f"WARN: {warn_count}")
print(f"ERROR: {error_count}")
print(f"NOT FOUND: {not_found}")

if errors:
    print(f"\nErrors: {len(errors)}")
    for error in errors[:10]:
        print(f"  - {error}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

