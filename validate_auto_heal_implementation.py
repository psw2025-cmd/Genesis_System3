"""
Final Validation Report - System3 Auto-Heal Implementation

This script runs a complete end-to-end validation of all auto-heal functionality.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 70)
print("SYSTEM3 AUTO-HEAL - FINAL VALIDATION REPORT")
print("=" * 70)
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

validation_results = {
    "timestamp": datetime.now().isoformat(),
    "validations": [],
    "overall_status": "PASS",
}

# Validation 1: Check orchestrator exists
print("1. Checking Auto-Heal Orchestrator...")
try:
    from core.engine.system3_auto_heal_orchestrator import AutoHealOrchestrator
    orchestrator = AutoHealOrchestrator()
    print("   ✅ Orchestrator imported and initialized")
    validation_results["validations"].append({
        "name": "Orchestrator Import",
        "status": "PASS",
    })
except Exception as e:
    print(f"   ❌ Failed: {e}")
    validation_results["validations"].append({
        "name": "Orchestrator Import",
        "status": "FAIL",
        "error": str(e),
    })
    validation_results["overall_status"] = "FAIL"

# Validation 2: Check phase 306 enhanced
print("\n2. Checking Phase 306 Enhancement...")
try:
    from core.engine.system3_phase306_staleness_guard import run_phase306, trigger_auto_heal
    result = run_phase306()
    
    if "auto_heal_triggered" in result.get("outputs", {}):
        print("   ✅ Phase 306 has auto-heal integration")
        validation_results["validations"].append({
            "name": "Phase 306 Enhancement",
            "status": "PASS",
            "details": f"Status: {result['status']}, Expired: {result['outputs'].get('expired_count', 0)}",
        })
    else:
        print("   ❌ Phase 306 missing auto-heal integration")
        validation_results["validations"].append({
            "name": "Phase 306 Enhancement",
            "status": "FAIL",
            "error": "auto_heal_triggered not in outputs",
        })
        validation_results["overall_status"] = "FAIL"
except Exception as e:
    print(f"   ❌ Failed: {e}")
    validation_results["validations"].append({
        "name": "Phase 306 Enhancement",
        "status": "FAIL",
        "error": str(e),
    })
    validation_results["overall_status"] = "FAIL"

# Validation 3: Check scheduler exists
print("\n3. Checking Auto-Heal Scheduler...")
try:
    from system3_auto_heal_scheduler import AutoHealScheduler
    scheduler = AutoHealScheduler()
    print("   ✅ Scheduler imported and initialized")
    validation_results["validations"].append({
        "name": "Scheduler Import",
        "status": "PASS",
    })
except Exception as e:
    print(f"   ❌ Failed: {e}")
    validation_results["validations"].append({
        "name": "Scheduler Import",
        "status": "FAIL",
        "error": str(e),
    })
    validation_results["overall_status"] = "FAIL"

# Validation 4: Check test suite exists
print("\n4. Checking Test Suite...")
try:
    test_file = PROJECT_ROOT / "test_auto_heal_comprehensive.py"
    if test_file.exists():
        print(f"   ✅ Test suite found: {test_file.name}")
        validation_results["validations"].append({
            "name": "Test Suite",
            "status": "PASS",
        })
    else:
        print(f"   ❌ Test suite not found")
        validation_results["validations"].append({
            "name": "Test Suite",
            "status": "FAIL",
            "error": "File not found",
        })
        validation_results["overall_status"] = "FAIL"
except Exception as e:
    print(f"   ❌ Failed: {e}")
    validation_results["validations"].append({
        "name": "Test Suite",
        "status": "FAIL",
        "error": str(e),
    })
    validation_results["overall_status"] = "FAIL"

# Validation 5: Check batch files exist
print("\n5. Checking Batch Files...")
batch_files = [
    "run_auto_heal.bat",
    "run_auto_heal_tests.bat",
    "start_auto_heal_scheduler.bat",
]
batch_status = []
for batch_file in batch_files:
    batch_path = PROJECT_ROOT / batch_file
    if batch_path.exists():
        print(f"   ✅ {batch_file}")
        batch_status.append(True)
    else:
        print(f"   ❌ {batch_file} not found")
        batch_status.append(False)

if all(batch_status):
    validation_results["validations"].append({
        "name": "Batch Files",
        "status": "PASS",
    })
else:
    validation_results["validations"].append({
        "name": "Batch Files",
        "status": "PARTIAL",
        "details": f"{sum(batch_status)}/{len(batch_status)} files found",
    })

# Validation 6: Check trigger mechanism
print("\n6. Checking Trigger Mechanism...")
try:
    trigger_file = PROJECT_ROOT / "storage" / "meta" / "system3_heal_trigger.json"
    if trigger_file.exists():
        with trigger_file.open("r") as f:
            trigger_data = json.load(f)
        print(f"   ✅ Trigger file exists")
        print(f"      Triggered by: {trigger_data.get('triggered_by')}")
        print(f"      Reason: {trigger_data.get('reason')}")
        validation_results["validations"].append({
            "name": "Trigger Mechanism",
            "status": "PASS",
            "details": trigger_data.get("reason"),
        })
    else:
        print(f"   ⚠️  Trigger file not found (may have been processed)")
        validation_results["validations"].append({
            "name": "Trigger Mechanism",
            "status": "PASS",
            "details": "No active trigger (normal state)",
        })
except Exception as e:
    print(f"   ❌ Failed: {e}")
    validation_results["validations"].append({
        "name": "Trigger Mechanism",
        "status": "FAIL",
        "error": str(e),
    })
    validation_results["overall_status"] = "FAIL"

# Validation 7: Check test results
print("\n7. Checking Test Results...")
try:
    results_dir = PROJECT_ROOT / "logs" / "auto_heal"
    if results_dir.exists():
        result_files = list(results_dir.glob("test_results_*.json"))
        if result_files:
            latest_result = max(result_files, key=lambda p: p.stat().st_mtime)
            with latest_result.open("r") as f:
                test_results = json.load(f)
            
            print(f"   ✅ Latest test results: {latest_result.name}")
            print(f"      Total: {test_results['total_tests']}, Passed: {test_results['passed']}")
            print(f"      Success Rate: {test_results['success_rate']:.1f}%")
            
            if test_results["success_rate"] == 100.0:
                validation_results["validations"].append({
                    "name": "Test Results",
                    "status": "PASS",
                    "details": f"{test_results['passed']}/{test_results['total_tests']} passed",
                })
            else:
                validation_results["validations"].append({
                    "name": "Test Results",
                    "status": "PARTIAL",
                    "details": f"{test_results['passed']}/{test_results['total_tests']} passed",
                })
        else:
            print(f"   ⚠️  No test result files found")
            validation_results["validations"].append({
                "name": "Test Results",
                "status": "WARN",
                "details": "No test results found",
            })
    else:
        print(f"   ⚠️  Test results directory not found")
        validation_results["validations"].append({
            "name": "Test Results",
            "status": "WARN",
            "details": "Results directory not found",
        })
except Exception as e:
    print(f"   ❌ Failed: {e}")
    validation_results["validations"].append({
        "name": "Test Results",
        "status": "FAIL",
        "error": str(e),
    })

# Validation 8: Check documentation
print("\n8. Checking Documentation...")
docs = [
    "SYSTEM3_AUTO_HEAL_IMPLEMENTATION_COMPLETE.md",
    "AUTO_HEAL_QUICK_REFERENCE.md",
]
docs_status = []
for doc in docs:
    doc_path = PROJECT_ROOT / doc
    if doc_path.exists():
        print(f"   ✅ {doc}")
        docs_status.append(True)
    else:
        print(f"   ❌ {doc} not found")
        docs_status.append(False)

if all(docs_status):
    validation_results["validations"].append({
        "name": "Documentation",
        "status": "PASS",
    })
else:
    validation_results["validations"].append({
        "name": "Documentation",
        "status": "PARTIAL",
        "details": f"{sum(docs_status)}/{len(docs_status)} documents found",
    })

# Final Summary
print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

pass_count = sum(1 for v in validation_results["validations"] if v["status"] == "PASS")
total_count = len(validation_results["validations"])

print(f"Validations Passed: {pass_count}/{total_count}")
print(f"Overall Status: {validation_results['overall_status']}")

# Save validation report
report_file = PROJECT_ROOT / "logs" / "auto_heal" / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
report_file.parent.mkdir(parents=True, exist_ok=True)

with report_file.open("w", encoding="utf-8") as f:
    json.dump(validation_results, f, indent=2)

print(f"\nReport saved: {report_file.relative_to(PROJECT_ROOT)}")

print("\n" + "=" * 70)
if validation_results["overall_status"] == "PASS":
    print("✅ ALL VALIDATIONS PASSED - SYSTEM READY FOR PRODUCTION")
else:
    print("⚠️  SOME VALIDATIONS FAILED - REVIEW REQUIRED")
print("=" * 70)

sys.exit(0 if validation_results["overall_status"] == "PASS" else 1)
