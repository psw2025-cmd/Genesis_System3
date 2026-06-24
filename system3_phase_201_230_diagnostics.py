"""
System3 Phases 201-230 Diagnostics Script

Runs all phases 201-230 in test mode and prints summary.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import all phase functions
PHASE_MODULES = {}
PHASE_IMPORTS = {
    201: ("system3_phase201_filesystem_integrity", "run_phase201"),
    202: ("system3_phase202_permissions_self_repair", "run_phase202"),
    203: ("system3_phase203_config_consistency", "run_phase203"),
    204: ("system3_phase204_python_env_validator", "run_phase204"),
    205: ("system3_phase205_broker_selftest", "run_phase205"),
    206: ("system3_phase206_model_compatibility", "run_phase206"),
    207: ("system3_phase207_hotfix_registry", "run_phase207"),
    208: ("system3_phase208_signal_consistency", "run_phase208"),
    209: ("system3_phase209_duplicate_purger", "run_phase209"),
    210: ("system3_phase210_timegap_analyzer", "run_phase210"),
    211: ("system3_phase211_feature_drift", "run_phase211"),
    212: ("system3_phase212_label_quality", "run_phase212"),
    213: ("system3_phase213_training_window", "run_phase213"),
    214: ("system3_phase214_hyperparam_snapshot", "run_phase214"),
    215: ("system3_phase215_overfit_sentinel", "run_phase215"),
    216: ("system3_phase216_greeks_audit", "run_phase216"),
    217: ("system3_phase217_vol_regime", "run_phase217"),
    218: ("system3_phase218_momentum_scanner", "run_phase218"),
    219: ("system3_phase219_breakout_analyzer", "run_phase219"),
    220: ("system3_phase220_correlation_map", "run_phase220"),
    221: ("system3_phase221_forward_returns", "run_phase221"),
    222: ("system3_phase222_signal_edge", "run_phase222"),
    223: ("system3_phase223_threshold_optimizer", "run_phase223"),
    224: ("system3_phase224_score_attribution", "run_phase224"),
    225: ("system3_phase225_label_reconciliation", "run_phase225"),
    226: ("system3_phase226_feature_importance", "run_phase226"),
    227: ("system3_phase227_latency_profiler", "run_phase227"),
    228: ("system3_phase228_snapshot_coverage", "run_phase228"),
    229: ("system3_phase229_schema_guard", "run_phase229"),
    230: ("system3_phase230_ai_fallback_audit", "run_phase230"),
}

for phase_num in range(201, 231):
    try:
        module_name, func_name = PHASE_IMPORTS[phase_num]
        module = __import__(f"core.engine.{module_name}", fromlist=[func_name])
        PHASE_MODULES[phase_num] = getattr(module, func_name)
    except (ImportError, AttributeError) as e:
        print(f"Warning: Phase {phase_num} import failed: {e}")


def main():
    """Run diagnostics for phases 201-230."""
    print("=" * 70)
    print("SYSTEM3 PHASES 201-230 DIAGNOSTICS")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = []
    for phase_num in range(201, 231):
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
                    elif "files_checked" in outputs:
                        key_info = f" ({outputs['files_checked']} files)"
                    elif "patterns_detected" in outputs:
                        key_info = f" ({outputs['patterns_detected']} patterns)"
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

    print(f"✅ OK: {ok_count}")
    print(f"⚠️ WARN: {warn_count}")
    print(f"❌ ERROR: {error_count}")
    print(f"⏸️ NOT IMPLEMENTED: {not_impl_count}")
    print(f"\nTotal: {len(results)} phases")

    # List main output files
    print("\n" + "=" * 70)
    print("MAIN OUTPUT FILES")
    print("=" * 70)

    output_files = []
    for phase_num, result in results:
        if "outputs" in result:
            outputs = result["outputs"]
            for key in [
                "report_path",
                "log_path",
                "output_file",
                "flags_file",
                "regimes_file",
                "patterns_file",
                "breakout_file",
                "coverage_file",
                "importance_file",
                "hparams_path",
                "candidates_file",
                "reconciled_file",
                "selected_window_path",
                "correlation_matrix_path",
            ]:
                if key in outputs and outputs[key]:
                    output_files.append((phase_num, key, outputs[key]))

    for phase_num, key, path in sorted(set(output_files)):
        print(f"Phase {phase_num:3d}: {Path(path).name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
