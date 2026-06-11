"""
Test Phases 311-330 Implementation
Quick validation of all new phases
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_phase(phase_num):
    """Test a single phase."""
    try:
        module_name = f"core.engine.system3_phase{phase_num}_*"
        
        # Import dynamically
        if phase_num == 311:
            from core.engine.system3_phase311_baseline_fs_snapshot import run_phase311
            result = run_phase311()
        elif phase_num == 312:
            from core.engine.system3_phase312_phase_registry_self_check import run_phase312
            result = run_phase312()
        elif phase_num == 313:
            from core.engine.system3_phase313_config_consistency_auditor import run_phase313
            result = run_phase313()
        elif phase_num == 314:
            from core.engine.system3_phase314_data_lineage_tracker import run_phase314
            result = run_phase314()
        elif phase_num == 315:
            from core.engine.system3_phase315_transactional_write_guard import run_phase315
            result = run_phase315()
        else:
            # For phases 316-330 (generic implementation)
            import importlib
            phase_files = list((PROJECT_ROOT / "core" / "engine").glob(f"system3_phase{phase_num}_*.py"))
            if not phase_files:
                return {"phase": phase_num, "status": "ERROR", "details": "Module not found"}
            
            module_path = phase_files[0]
            module_name = module_path.stem
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            func = getattr(module, f"run_phase{phase_num}")
            result = func()
        
        return result
        
    except Exception as e:
        return {"phase": phase_num, "status": "ERROR", "details": str(e)}


def main():
    """Test all phases 311-330."""
    print("=" * 80)
    print("TESTING PHASES 311-330")
    print("=" * 80)
    print()
    
    results = []
    
    for phase_num in range(311, 331):
        print(f"Testing Phase {phase_num}...", end=" ")
        result = test_phase(phase_num)
        results.append(result)
        
        status_icon = "[OK]" if result["status"] == "OK" else ("[WARN]" if result["status"] == "WARN" else "[ERROR]")
        print(f"{status_icon} {result['status']}: {result['details']}")
    
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    ok_count = sum(1 for r in results if r["status"] == "OK")
    warn_count = sum(1 for r in results if r["status"] == "WARN")
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    
    print(f"Total: {len(results)} phases")
    print(f"[OK] OK: {ok_count}")
    print(f"[WARN] WARN: {warn_count}")
    print(f"[ERROR] ERROR: {error_count}")
    print()
    
    if error_count == 0:
        print("[OK] ALL PHASES PASSED!")
    else:
        print("[WARN] Some phases had errors - review above")
    
    return error_count == 0


if __name__ == "__main__":
    import importlib.util
    success = main()
    sys.exit(0 if success else 1)
