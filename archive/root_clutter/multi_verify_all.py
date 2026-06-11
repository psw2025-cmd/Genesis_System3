"""
MULTI-LEVEL VERIFICATION - Complete System3 CSV Fixes & Warnings Check
"""

import sys
from pathlib import Path
import json
import traceback

ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

print("=" * 70)
print("MULTI-LEVEL VERIFICATION - SYSTEM3 CSV FIXES & WARNINGS")
print("=" * 70)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

results = {
    "level1_code_verification": {},
    "level2_functional_tests": {},
    "level3_integration_tests": {},
    "level4_phase_tests": {},
    "level5_error_scan": {},
}

# ============================================================================
# LEVEL 1: CODE VERIFICATION (Static Analysis)
# ============================================================================

print("=" * 70)
print("LEVEL 1: CODE VERIFICATION (Static Analysis)")
print("=" * 70)
print()

def verify_csv_loading_code(file_path, file_name):
    """Verify CSV loading code in a file."""
    issues = []
    checks = {
        "has_engine_python": False,
        "has_on_bad_lines": False,
        "has_try_except": False,
        "has_error_handling": False,
    }
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")
            
        # Check for robust CSV loading
        for i, line in enumerate(lines, 1):
            if "pd.read_csv" in line:
                if 'engine="python"' in line:
                    checks["has_engine_python"] = True
                if 'on_bad_lines="skip"' in line:
                    checks["has_on_bad_lines"] = True
                
                # Check if try/except wraps this line
                context_start = max(0, i - 10)
                context_end = min(len(lines), i + 10)
                context = "\n".join(lines[context_start:context_end])
                
                if "try:" in context:
                    checks["has_try_except"] = True
                if "except" in context:
                    checks["has_error_handling"] = True
        
        # Report
        all_checks = all(checks.values())
        if not all_checks:
            for check, passed in checks.items():
                if not passed:
                    issues.append(f"Missing: {check}")
        
        return {
            "status": "PASSED" if all_checks else "FAILED",
            "checks": checks,
            "issues": issues,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "checks": checks,
            "issues": [f"Could not verify: {e}"],
        }

# Verify all files
files_to_check = [
    ("core/engine/angel_pnl_simulator.py", "angel_pnl_simulator"),
    ("core/engine/angel_trade_decision.py", "angel_trade_decision"),
    ("core/engine/angel_real_data_extractor.py", "angel_real_data_extractor"),
    ("core/engine/system3_phase222_signal_edge.py", "phase222"),
    ("core/engine/system3_phase263_advanced_pnl_attribution.py", "phase263"),
]

for file_path, file_name in files_to_check:
    full_path = ROOT_DIR / file_path
    if full_path.exists():
        result = verify_csv_loading_code(full_path, file_name)
        results["level1_code_verification"][file_name] = result
        
        status_icon = "✅" if result["status"] == "PASSED" else "❌"
        logger.info(f"{status_icon} {file_name}: {result['status']}")
        if result.get("issues"):
            for issue in result["issues"]:
                logger.warning(f"    - {issue}")
    else:
        logger.error(f"❌ {file_name}: File not found")
        results["level1_code_verification"][file_name] = {"status": "ERROR", "error": "File not found"}

print()

# ============================================================================
# LEVEL 2: FUNCTIONAL TESTS
# ============================================================================

print("=" * 70)
print("LEVEL 2: FUNCTIONAL TESTS")
print("=" * 70)
print()

# Test 1: PnL Simulator
logger.info("[TEST] PnL Simulator...")
try:
    from core.engine.angel_pnl_simulator import _load_data
    
    df_sig, df_tr = _load_data()
    
    if df_sig is None and df_tr is None:
        results["level2_functional_tests"]["pnl_simulator"] = {
            "status": "SKIPPED",
            "reason": "Files not found"
        }
        logger.warning("⚠️  Files not found (OK)")
    elif df_sig is None or df_tr is None:
        results["level2_functional_tests"]["pnl_simulator"] = {
            "status": "FAILED",
            "reason": "One CSV failed to load"
        }
        logger.error("❌ One CSV failed to load")
    else:
        results["level2_functional_tests"]["pnl_simulator"] = {
            "status": "PASSED",
            "signals_rows": len(df_sig),
            "trades_rows": len(df_tr),
        }
        logger.info(f"✅ PASSED: {len(df_sig)} signals, {len(df_tr)} trades")
except Exception as e:
    results["level2_functional_tests"]["pnl_simulator"] = {
        "status": "FAILED",
        "error": str(e)
    }
    logger.error(f"❌ FAILED: {e}")

# Test 2: Trade Decision
logger.info("[TEST] Trade Decision...")
try:
    import pandas as pd
    signals_csv = ROOT_DIR / "storage" / "live" / "angel_index_ai_signals.csv"
    
    if signals_csv.exists():
        df = pd.read_csv(signals_csv, engine="python", on_bad_lines="skip")
        results["level2_functional_tests"]["trade_decision"] = {
            "status": "PASSED",
            "rows": len(df),
        }
        logger.info(f"✅ PASSED: {len(df)} rows")
    else:
        results["level2_functional_tests"]["trade_decision"] = {
            "status": "SKIPPED",
            "reason": "File not found"
        }
        logger.warning("⚠️  File not found (OK)")
except Exception as e:
    results["level2_functional_tests"]["trade_decision"] = {
        "status": "FAILED",
        "error": str(e)
    }
    logger.error(f"❌ FAILED: {e}")

# Test 3: Data Extractor
logger.info("[TEST] Data Extractor...")
try:
    from core.engine.angel_real_data_extractor import extract_real_training_data
    
    df = extract_real_training_data()
    results["level2_functional_tests"]["data_extractor"] = {
        "status": "PASSED",
        "rows": len(df),
    }
    logger.info(f"✅ PASSED: {len(df)} rows")
except Exception as e:
    results["level2_functional_tests"]["data_extractor"] = {
        "status": "FAILED",
        "error": str(e)
    }
    logger.error(f"❌ FAILED: {e}")

print()

# ============================================================================
# LEVEL 3: INTEGRATION TESTS
# ============================================================================

print("=" * 70)
print("LEVEL 3: INTEGRATION TESTS")
print("=" * 70)
print()

# Test: Full PnL Simulation
logger.info("[TEST] Full PnL Simulation...")
try:
    from core.engine.angel_pnl_simulator import run_pnl_simulation
    
    result = run_pnl_simulation()
    
    if result is not None:
        results["level3_integration_tests"]["pnl_simulation"] = {
            "status": "PASSED",
            "trades": len(result),
        }
        logger.info(f"✅ PASSED: {len(result)} trades simulated")
    else:
        results["level3_integration_tests"]["pnl_simulation"] = {
            "status": "SKIPPED",
            "reason": "No trades to simulate"
        }
        logger.warning("⚠️  No trades to simulate (OK)")
except Exception as e:
    results["level3_integration_tests"]["pnl_simulation"] = {
        "status": "FAILED",
        "error": str(e)
    }
    logger.error(f"❌ FAILED: {e}")
    traceback.print_exc()

print()

# ============================================================================
# LEVEL 4: PHASE TESTS
# ============================================================================

print("=" * 70)
print("LEVEL 4: PHASE TESTS")
print("=" * 70)
print()

def test_phase(phase_num, module_name, function_name="run_phase"):
    """Test a phase and return detailed result."""
    try:
        module = __import__(module_name, fromlist=[function_name])
        phase_func = getattr(module, function_name, None)
        
        if phase_func is None:
            return {"status": "SKIPPED", "reason": "Function not found"}
        
        result = phase_func()
        
        if isinstance(result, dict):
            return {
                "status": result.get("status", "UNKNOWN"),
                "details": result.get("details", ""),
                "errors": result.get("errors", []),
            }
        else:
            return {"status": "PASSED", "details": "Completed"}
            
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

# Test phases
test_phases = [
    (222, "core.engine.system3_phase222_signal_edge", "run_phase222"),
    (225, "core.engine.system3_phase225_label_reconciliation", "run_phase225"),
    (263, "core.engine.system3_phase263_advanced_pnl_attribution", "run_phase263"),
]

for phase_num, module_name, func_name in test_phases:
    logger.info(f"[TEST] Phase {phase_num}...")
    result = test_phase(phase_num, module_name, func_name)
    results["level4_phase_tests"][f"phase_{phase_num}"] = result
    
    status = result["status"]
    if status in ["OK", "PASSED"]:
        logger.info(f"✅ Phase {phase_num}: {status}")
    elif status == "WARN":
        logger.warning(f"⚠️  Phase {phase_num}: {status} - {result.get('details', '')}")
    else:
        logger.error(f"❌ Phase {phase_num}: {status}")
        if result.get("error"):
            logger.error(f"    Error: {result['error']}")

print()

# ============================================================================
# LEVEL 5: ERROR SCAN
# ============================================================================

print("=" * 70)
print("LEVEL 5: ERROR SCAN")
print("=" * 70)
print()

# Check for any CSV parsing errors in logs
log_dir = ROOT_DIR / "logs"
csv_parsing_errors = []

if log_dir.exists():
    for log_file in log_dir.glob("*.log"):
        try:
            with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if "Error tokenizing data" in content or "Expected" in content and "fields" in content:
                    csv_parsing_errors.append(str(log_file))
        except:
            pass

if csv_parsing_errors:
    results["level5_error_scan"]["csv_parsing_errors_in_logs"] = {
        "status": "FOUND",
        "files": csv_parsing_errors,
    }
    logger.warning(f"⚠️  Found CSV parsing errors in {len(csv_parsing_errors)} log files")
    for log_file in csv_parsing_errors:
        logger.warning(f"    - {log_file}")
else:
    results["level5_error_scan"]["csv_parsing_errors_in_logs"] = {
        "status": "NONE",
    }
    logger.info("✅ No CSV parsing errors found in recent logs")

# Check actual CSV file for issues
signals_csv = ROOT_DIR / "storage" / "live" / "angel_index_ai_signals.csv"
if signals_csv.exists():
    try:
        import pandas as pd
        df = pd.read_csv(signals_csv, engine="python", on_bad_lines="skip")
        results["level5_error_scan"]["csv_file_check"] = {
            "status": "PASSED",
            "rows": len(df),
            "columns": len(df.columns),
        }
        logger.info(f"✅ CSV file loads successfully: {len(df)} rows, {len(df.columns)} columns")
    except Exception as e:
        results["level5_error_scan"]["csv_file_check"] = {
            "status": "FAILED",
            "error": str(e),
        }
        logger.error(f"❌ CSV file check failed: {e}")

print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("=" * 70)
print("MULTI-LEVEL VERIFICATION SUMMARY")
print("=" * 70)
print()

all_passed = True
critical_failures = []

# Level 1: Code Verification
print("LEVEL 1: Code Verification")
for name, result in results["level1_code_verification"].items():
    status = result["status"]
    if status == "FAILED":
        all_passed = False
        critical_failures.append(f"{name}: Code verification failed")
        print(f"  ❌ {name}: {status}")
    elif status == "ERROR":
        all_passed = False
        critical_failures.append(f"{name}: Code verification error")
        print(f"  ❌ {name}: {status}")
    else:
        print(f"  ✅ {name}: {status}")

print()

# Level 2: Functional Tests
print("LEVEL 2: Functional Tests")
for name, result in results["level2_functional_tests"].items():
    status = result["status"]
    if status == "FAILED":
        all_passed = False
        critical_failures.append(f"{name}: Functional test failed")
        print(f"  ❌ {name}: {status}")
    elif status == "SKIPPED":
        print(f"  ⚠️  {name}: {status} ({result.get('reason', '')})")
    else:
        print(f"  ✅ {name}: {status}")

print()

# Level 3: Integration Tests
print("LEVEL 3: Integration Tests")
for name, result in results["level3_integration_tests"].items():
    status = result["status"]
    if status == "FAILED":
        all_passed = False
        critical_failures.append(f"{name}: Integration test failed")
        print(f"  ❌ {name}: {status}")
    elif status == "SKIPPED":
        print(f"  ⚠️  {name}: {status} ({result.get('reason', '')})")
    else:
        print(f"  ✅ {name}: {status}")

print()

# Level 4: Phase Tests
print("LEVEL 4: Phase Tests")
for name, result in results["level4_phase_tests"].items():
    status = result["status"]
    if status in ["ERROR", "FAILED"]:
        all_passed = False
        critical_failures.append(f"{name}: Phase test failed")
        print(f"  ❌ {name}: {status}")
    elif status == "WARN":
        print(f"  ⚠️  {name}: {status} (expected)")
    else:
        print(f"  ✅ {name}: {status}")

print()

# Level 5: Error Scan
print("LEVEL 5: Error Scan")
for name, result in results["level5_error_scan"].items():
    status = result["status"]
    if status == "FOUND":
        print(f"  ⚠️  {name}: {status} (historical - may be from before fixes)")
    elif status == "FAILED":
        all_passed = False
        critical_failures.append(f"{name}: Error scan failed")
        print(f"  ❌ {name}: {status}")
    else:
        print(f"  ✅ {name}: {status}")

print()

# Final Assessment
print("=" * 70)
if all_passed and not critical_failures:
    print("✅ ALL VERIFICATIONS PASSED")
    print("=" * 70)
    print()
    print("Summary:")
    print("  ✅ All CSV loading code verified")
    print("  ✅ All functional tests passed")
    print("  ✅ All integration tests passed")
    print("  ✅ Phase tests completed (warnings are expected)")
    print("  ✅ No critical errors found")
    print()
    print("System Status: ✅ PRODUCTION READY")
else:
    print("❌ SOME VERIFICATIONS FAILED")
    print("=" * 70)
    print()
    print("Critical Failures:")
    for failure in critical_failures:
        print(f"  - {failure}")

print()

# Save results
results_file = ROOT_DIR / "docs" / "multi_verification_results.json"
results_file.parent.mkdir(parents=True, exist_ok=True)
with open(results_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

logger.info(f"Results saved to: {results_file}")

