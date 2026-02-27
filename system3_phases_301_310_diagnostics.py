"""
System3 Phases 301-310 Diagnostics Script

Runs all phases 301-310 in test mode and prints summary.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import all phase functions
PHASE_MODULES = {}
PHASE_IMPORTS = {
    301: ("system3_phase301_daily_live_vs_forward", "run_phase301"),
    302: ("system3_phase302_regime_performance", "run_phase302"),
    303: ("system3_phase303_edge_decay", "run_phase303"),
    304: ("system3_phase304_threshold_tuner", "run_phase304"),
    305: ("system3_phase305_confidence_tier", "run_phase305"),
    306: ("system3_phase306_staleness_guard", "run_phase306"),
    307: ("system3_phase307_live_vs_test_consistency", "run_phase307"),
    308: ("system3_phase308_daily_dashboard", "run_phase308"),
    309: ("system3_phase309_schedule_hints", "run_phase309"),
    310: ("system3_phase310_ultra_health", "run_phase310"),
}

for phase_num in range(301, 311):
    try:
        module_name, func_name = PHASE_IMPORTS[phase_num]
        module = __import__(f"core.engine.{module_name}", fromlist=[func_name])
        PHASE_MODULES[phase_num] = getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        print(f"Warning: Phase {phase_num} import failed: {e}")


def main():
    """Run diagnostics for phases 301-310."""
    print("=" * 70)
    print("SYSTEM3 PHASES 301-310 DIAGNOSTICS")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    for phase_num in range(301, 311):
        if phase_num in PHASE_MODULES:
            print(f"Phase {phase_num:3d}... ", end="", flush=True)
            try:
                result = PHASE_MODULES[phase_num]()
                results.append((phase_num, result))
                status_icon = "✅" if result["status"] == "OK" else "⚠️" if result["status"] == "WARN" else "❌"
                key_info = ""
                if "outputs" in result:
                    outputs = result["outputs"]
                    if "rows_processed" in outputs:
                        key_info = f" ({outputs['rows_processed']} rows)"
                    elif "underlyings_analyzed" in outputs:
                        key_info = f" ({outputs['underlyings_analyzed']} underlyings)"
                    elif "phases_checked" in outputs:
                        key_info = f" (score: {outputs.get('overall_health_score', 0):.1f})"
                print(f"{status_icon} {result['status']}{key_info}")
            except Exception as e:
                print(f"❌ ERROR: {e}")
                results.append((phase_num, {"status": "ERROR", "details": str(e), "errors": [str(e)]}))
        else:
            print(f"Phase {phase_num:3d}... ⚠️ NOT IMPLEMENTED")
            results.append((phase_num, {"status": "NOT_IMPLEMENTED", "details": "Module not found"}))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    ok_count = sum(1 for _, r in results if r.get("status") == "OK")
    warn_count = sum(1 for _, r in results if r.get("status") == "WARN")
    error_count = sum(1 for _, r in results if r.get("status") == "ERROR")
    not_impl_count = sum(1 for _, r in results if r.get("status") == "NOT_IMPLEMENTED")
    
    print(f"✅ OK:     {ok_count:2d}")
    print(f"⚠️  WARN:   {warn_count:2d}")
    print(f"❌ ERROR:  {error_count:2d}")
    print(f"⚠️  NOT IMPLEMENTED: {not_impl_count:2d}")
    print()
    
    # WARN phases details
    warn_phases = [(p, r) for p, r in results if r.get("status") == "WARN"]
    if warn_phases:
        print("WARN Phases:")
        for phase_num, result in warn_phases:
            print(f"  Phase {phase_num}: {result.get('details', 'N/A')}")
        print()
    
    # ERROR phases details
    error_phases = [(p, r) for p, r in results if r.get("status") == "ERROR"]
    if error_phases:
        print("ERROR Phases:")
        for phase_num, result in error_phases:
            print(f"  Phase {phase_num}: {result.get('details', 'N/A')}")
            if "errors" in result:
                for error in result["errors"]:
                    print(f"    - {error}")
        print()
    
    print("=" * 70)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 70)
    
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

