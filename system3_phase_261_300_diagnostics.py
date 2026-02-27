"""
System3 Phases 261-300 Diagnostics Script

Runs all phases 261-300 in test mode and prints summary.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import phase functions
PHASE_MODULES = {}

# Load phase functions dynamically
for phase_num in range(261, 301):
    try:
        # Try to find the module file
        phase_files = list((PROJECT_ROOT / "core" / "engine").glob(f"system3_phase{phase_num}_*.py"))
        if phase_files:
            # Extract module name from file
            file_stem = phase_files[0].stem
            module_name = f"core.engine.{file_stem}"
            func_name = f"run_phase{phase_num}"
            
            # Import module
            module = __import__(module_name, fromlist=[func_name])
            if hasattr(module, func_name):
                PHASE_MODULES[phase_num] = getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        pass  # Phase not found or function missing


def run_diagnostics() -> None:
    """Run diagnostics for all phases 261-300."""
    print("=" * 70)
    print("SYSTEM3 PHASES 261-300 DIAGNOSTICS")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    status_counts = {"OK": 0, "WARN": 0, "ERROR": 0, "NOT IMPLEMENTED": 0}
    
    # Run each phase
    for phase_num in range(261, 301):
        if phase_num in PHASE_MODULES:
            try:
                result = PHASE_MODULES[phase_num]()
                results[phase_num] = result
                status = result.get("status", "ERROR")
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Print status
                status_icon = "✅" if status == "OK" else "⚠️" if status == "WARN" else "❌"
                print(f"Phase {phase_num}... {status_icon} {status}")
            except Exception as e:
                results[phase_num] = {
                    "phase": phase_num,
                    "status": "ERROR",
                    "details": f"Exception: {e}",
                    "outputs": {},
                    "errors": [str(e)],
                }
                status_counts["ERROR"] += 1
                print(f"Phase {phase_num}... ❌ ERROR: {e}")
        else:
            results[phase_num] = {
                "phase": phase_num,
                "status": "NOT IMPLEMENTED",
                "details": "Phase module not found",
                "outputs": {},
                "errors": [],
            }
            status_counts["NOT IMPLEMENTED"] += 1
            print(f"Phase {phase_num}... ⏳ NOT IMPLEMENTED")
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"OK: {status_counts.get('OK', 0)}")
    print(f"WARN: {status_counts.get('WARN', 0)}")
    print(f"ERROR: {status_counts.get('ERROR', 0)}")
    print(f"NOT IMPLEMENTED: {status_counts.get('NOT IMPLEMENTED', 0)}")
    print("=" * 70)
    
    # List main output files
    print("\n## Main Output Files\n")
    for phase_num in sorted(results.keys()):
        result = results[phase_num]
        if result.get("status") == "OK" and "outputs" in result:
            outputs = result["outputs"]
            report_file = outputs.get("report_file") or outputs.get("report_path")
            if report_file:
                print(f"Phase {phase_num}: {report_file}")


if __name__ == "__main__":
    run_diagnostics()

