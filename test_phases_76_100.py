"""
System3 Phases 76-100 - Complete Test Suite

Runs all 25 phases (76-100) and validates outputs.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Phase modules
PHASES = [
    ("76", "system3_phase76_geni_self_critique"),
    ("77", "system3_phase77_geni_self_correction"),
    ("78", "system3_phase78_geni_consensus"),
    ("79", "system3_phase79_adaptive_thresholds"),
    ("80", "system3_phase80_geni_evolution_status"),
    ("81", "system3_phase81_latency_profiler"),
    ("82", "system3_phase82_job_scheduler"),
    ("83", "system3_phase83_tick_to_trade_latency"),
    ("84", "system3_phase84_resource_optimizer"),
    ("85", "system3_phase85_heartbeat"),
    ("86", "system3_phase86_position_sizing"),
    ("87", "system3_phase87_expected_value"),
    ("88", "system3_phase88_portfolio_risk"),
    ("89", "system3_phase89_optimal_entry"),
    ("90", "system3_phase90_optimal_exit"),
    ("91", "system3_phase91_live_dashboard"),
    ("92", "system3_phase92_session_replay"),
    ("93", "system3_phase93_operator_override"),
    ("94", "system3_phase94_notification_engine"),
    ("95", "system3_phase95_operator_activity_log"),
    ("96", "system3_phase96_chaos_test"),
    ("97", "system3_phase97_backup_recovery"),
    ("98", "system3_phase98_rollback"),
    ("99", "system3_phase99_version_freeze"),
    ("100", "system3_phase100_final_certification"),
]


def run_phase(phase_num: str, module_name: str) -> Dict[str, Any]:
    """Run a single phase module."""
    print("\n" + "="*70)
    print(f"PHASE {phase_num}: {module_name}")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", f"core.engine.{module_name}"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per phase
        )
        
        return {
            "phase": phase_num,
            "module": module_name,
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "phase": phase_num,
            "module": module_name,
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "Timeout after 5 minutes",
        }
    except Exception as e:
        return {
            "phase": phase_num,
            "module": module_name,
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e),
        }


def check_output_files(phase_num: str) -> List[str]:
    """Check which expected output files exist for a phase."""
    storage_dir = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"
    existing = []
    
    # Common patterns
    patterns = [
        f"phase{phase_num}_*.json",
        f"phase{phase_num}_*.md",
        f"phase{phase_num}_*.parquet",
        f"phase{phase_num}_*.log",
    ]
    
    for pattern in patterns:
        for file in storage_dir.glob(pattern):
            existing.append(file.name)
    
    return sorted(existing)


def main():
    """Run all phases and generate report."""
    print("\n" + "="*70)
    print("SYSTEM3 PHASES 76-100 - COMPLETE TEST SUITE")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    # Run all phases
    for phase_num, module_name in PHASES:
        result = run_phase(phase_num, module_name)
        results.append(result)
        
        # Check output files
        output_files = check_output_files(phase_num)
        result["output_files"] = output_files
        
        # Print summary
        status = "[OK]" if result["success"] else "[FAIL]"
        print(f"{status} Phase {phase_num}: {len(output_files)} output files")
        if result["stderr"]:
            print(f"  Error: {result['stderr'][:200]}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    print(f"Total phases: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print("\nFailed phases:")
        for r in results:
            if not r["success"]:
                print(f"  Phase {r['phase']}: {r['module']}")
                if r["stderr"]:
                    print(f"    {r['stderr'][:100]}")
    
    # Output files summary
    print("\nOutput files created:")
    for r in results:
        if r["output_files"]:
            print(f"  Phase {r['phase']}: {', '.join(r['output_files'])}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

