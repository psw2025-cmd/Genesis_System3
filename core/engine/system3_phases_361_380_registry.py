"""
System3 Phases 361-380 Registry & Integration Module

Registers all 20 phases in the final implementation block.
Provides callable functions and phase metadata for autorun orchestration.

Phase Categories:
  - signal_pipeline: Phases 361-365 (snapshot, calibration, monitoring, health, accuracy)
  - data_quality: Phases 370-375 (schema, deduplication, conflict, curation, freshness, quality)
  - strategy_analysis: Phases 366-369 (ensemble, safety, latency, profiling)
  - self_test: Phases 376-380 (testing suite, validation, optimization, edge cases, sign-off)
"""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Phase registry mapping phase_number -> (module_name, function_name, category, mode)
PHASES_361_380_REGISTRY = {
    # Signal Pipeline Block (361-365)
    361: ("system3_phase361_signal_pipeline_snapshot", "run_phase361", "signal_pipeline", "pre-market"),
    362: ("system3_phase362_forward_calibrator", "run_phase362", "signal_pipeline", "pre-market"),
    363: ("system3_phase363_model_drift_checker", "run_phase363", "signal_pipeline", "post-market"),
    364: ("system3_phase364_health_dashboard_feed", "run_phase364", "signal_pipeline", "live"),
    365: ("system3_phase365_accuracy_tracker", "run_phase365", "signal_pipeline", "post-market"),
    # Strategy Analysis Block (366-369)
    366: ("system3_phase366_strategy_ensemble_evaluator", "run_phase366", "strategy_analysis", "post-market"),
    367: ("system3_phase367_safety_guardrail_recommender", "run_phase367", "strategy_analysis", "live"),
    368: ("system3_phase368_broker_latency_monitor", "run_phase368", "strategy_analysis", "live"),
    369: ("system3_phase369_pipeline_profiler", "run_phase369", "strategy_analysis", "post-market"),
    # Data Quality Block (370-375)
    370: ("system3_phase370_signal_schema_normalizer", "run_phase370", "data_quality", "pre-market"),
    371: ("system3_phase371_signal_duplicate_scanner", "run_phase371", "data_quality", "post-market"),
    372: ("system3_phase372_signal_conflict_resolver", "run_phase372", "data_quality", "post-market"),
    373: ("system3_phase373_signal_clean_curated_builder", "run_phase373", "data_quality", "post-market"),
    374: ("system3_phase374_signal_history_freshness_checker", "run_phase374", "data_quality", "live"),
    375: ("system3_phase375_signal_data_quality_summary", "run_phase375", "data_quality", "post-market"),
    # Self-Test & Validation Block (376-380) - PLACEHOLDER FOR NOW
    376: ("system3_phase376_self_test_suite", "run_phase376", "self_test", "post-market"),
    377: ("system3_phase377_validation_report_generator", "run_phase377", "self_test", "post-market"),
    378: ("system3_phase378_performance_optimizer", "run_phase378", "self_test", "post-market"),
    379: ("system3_phase379_edge_case_handler", "run_phase379", "self_test", "post-market"),
    380: ("system3_phase380_final_sign_off", "run_phase380", "self_test", "post-market"),
}

# Imported phase callables
PHASE_CALLABLES = {}


def load_phase_callables():
    """Dynamically load all phase callables."""
    global PHASE_CALLABLES

    for phase_num, (module_name, func_name, category, mode) in PHASES_361_380_REGISTRY.items():
        try:
            module = __import__(f"core.engine.{module_name}", fromlist=[func_name])
            func = getattr(module, func_name)
            PHASE_CALLABLES[phase_num] = func
            logger.info(f"Loaded Phase {phase_num}: {func_name}")
        except Exception as e:
            logger.warning(f"Failed to load Phase {phase_num} ({module_name}.{func_name}): {e}")


def get_phase_callable(phase_num: int):
    """Get the callable for a specific phase."""
    if not PHASE_CALLABLES:
        load_phase_callables()
    return PHASE_CALLABLES.get(phase_num)


def get_phases_by_mode(mode: str):
    """Get all phase numbers for a given mode (pre-market, live, post-market, eod)."""
    return [p for p, (m_name, f_name, cat, m) in PHASES_361_380_REGISTRY.items() if m == mode]


def get_phases_by_category(category: str):
    """Get all phase numbers for a given category."""
    return [p for p, (m_name, f_name, cat, m) in PHASES_361_380_REGISTRY.items() if cat == category]


def get_phase_info(phase_num: int):
    """Get metadata for a specific phase."""
    if phase_num not in PHASES_361_380_REGISTRY:
        return None
    module_name, func_name, category, mode = PHASES_361_380_REGISTRY[phase_num]
    return {
        "phase": phase_num,
        "module": module_name,
        "function": func_name,
        "category": category,
        "mode": mode,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Phases 361-380 Registry ===")
    print(f"Total phases: {len(PHASES_361_380_REGISTRY)}")

    print("\nPhases by category:")
    for category in ["signal_pipeline", "strategy_analysis", "data_quality", "self_test"]:
        phases = get_phases_by_category(category)
        print(f"  {category}: {phases}")

    print("\nPhases by mode:")
    for mode in ["pre-market", "live", "post-market"]:
        phases = get_phases_by_mode(mode)
        print(f"  {mode}: {phases}")

    print("\nLoading callables...")
    load_phase_callables()
    print(f"Successfully loaded: {len(PHASE_CALLABLES)} phases")
    print(f"Failed to load: {len(PHASES_361_380_REGISTRY) - len(PHASE_CALLABLES)} phases")
