"""
System3 Phases 331-360 Registry & Integration Module

Registers all new phases for the autorun master.
Provides callable functions and phase metadata.
"""

import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Phase registry mapping phase_number -> (module_name, function_name, category, mode)
# Existing phases 331-340 use run_phase_XXX format, new phases 341-360 use run_phase_XXX_name format
PHASES_331_360_REGISTRY = {
    331: ("system3_phase331_signal_integrity", "run_phase_331", "accuracy", "pre-market"),
    332: ("system3_phase332_signal_volume_coverage", "run_phase_332", "accuracy", "pre-market"),
    333: ("system3_phase333_signal_consistency", "run_phase_333", "accuracy", "pre-market"),
    334: ("system3_phase334_model_drift_snapshot", "run_phase_334", "accuracy", "post-market"),
    335: ("system3_phase335_model_drift_analyzer", "run_phase_335", "accuracy", "post-market"),
    336: ("system3_phase336_safe_mode_suggestor", "run_phase_336", "accuracy", "post-market"),
    337: ("system3_phase337_forward_return_quality_tracker", "run_phase_337", "accuracy", "post-market"),
    338: ("system3_phase338_signal_outcome_correlation", "run_phase_338", "accuracy", "post-market"),
    339: ("system3_phase339_daily_signal_pipeline_summary", "run_phase_339", "accuracy", "post-market"),
    340: ("system3_phase340_signal_pipeline_regression_guard", "run_phase_340", "accuracy", "post-market"),
    341: (
        "system3_phase341_model_drift_detector_v2",
        "run_phase_341_model_drift_detector_v2",
        "accuracy",
        "post-market",
    ),
    342: (
        "system3_phase342_live_performance_estimator",
        "run_phase_342_live_performance_estimator",
        "accuracy",
        "live",
    ),
    343: (
        "system3_phase343_signals_freshness_enforcer",
        "run_phase_343_signals_freshness_enforcer",
        "hardening",
        "pre-market",
    ),
    344: ("system3_phase344_pipeline_schema_guard", "run_phase_344_pipeline_schema_guard", "hardening", "pre-market"),
    345: (
        "system3_phase345_warn_root_cause_tracker",
        "run_phase_345_warn_root_cause_tracker",
        "hardening",
        "post-market",
    ),
    346: ("system3_phases_346_350_hardening_pack", "run_phase_346_live_data_integrity_checker", "hardening", "live"),
    347: ("system3_phases_346_350_hardening_pack", "run_phase_347_historical_cache_sanity", "hardening", "post-market"),
    348: ("system3_phases_346_350_hardening_pack", "run_phase_348_virtual_orders_guard", "hardening", "eod"),
    349: ("system3_phases_346_350_hardening_pack", "run_phase_349_phase_dependency_guard", "hardening", "pre-market"),
    350: ("system3_phases_346_350_hardening_pack", "run_phase_350_warn_task_converter", "hardening", "post-market"),
    351: ("system3_phases_351_360_safety_automation", "run_phase_351_trading_mode_audit", "safety", "pre-market"),
    352: ("system3_phases_351_360_safety_automation", "run_phase_352_risk_limits_snapshot", "safety", "live"),
    353: ("system3_phases_351_360_safety_automation", "run_phase_353_broker_connectivity_monitor", "safety", "live"),
    354: (
        "system3_phases_351_360_safety_automation",
        "run_phase_354_virtual_fill_realism_checker",
        "safety",
        "post-market",
    ),
    355: ("system3_phases_351_360_safety_automation", "run_phase_355_paper_trading_audit_trail", "safety", "eod"),
    356: ("system3_phases_351_360_safety_automation", "run_phase_356_safety_dashboard_snapshot", "safety", "live"),
    357: ("system3_phases_351_360_safety_automation", "run_phase_357_log_noise_filter", "automation", "post-market"),
    358: (
        "system3_phases_351_360_safety_automation",
        "run_phase_358_auto_checklist_generator",
        "automation",
        "post-market",
    ),
    359: (
        "system3_phases_351_360_safety_automation",
        "run_phase_359_self_healing_suggestions",
        "automation",
        "post-market",
    ),
    360: (
        "system3_phases_351_360_safety_automation",
        "run_phase_360_dry_run_readiness_gate",
        "automation",
        "post-market",
    ),
}

# Imported phase callables
PHASE_CALLABLES = {}


def load_phase_callables():
    """Dynamically load all phase callables."""
    global PHASE_CALLABLES

    for phase_num, (module_name, func_name, category, mode) in PHASES_331_360_REGISTRY.items():
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
    return [p for p, (m_name, f_name, cat, m) in PHASES_331_360_REGISTRY.items() if m == mode]


def get_phases_by_category(category: str):
    """Get all phase numbers for a given category (accuracy, hardening, safety, automation)."""
    return [p for p, (m_name, f_name, cat, m) in PHASES_331_360_REGISTRY.items() if cat == category]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=== Phase Registry ===")
    print(f"Total phases: {len(PHASES_331_360_REGISTRY)}")

    print("\nPhases by category:")
    for category in ["accuracy", "hardening", "safety", "automation"]:
        phases = get_phases_by_category(category)
        print(f"  {category}: {phases}")

    print("\nPhases by mode:")
    for mode in ["pre-market", "live", "post-market", "eod"]:
        phases = get_phases_by_mode(mode)
        print(f"  {mode}: {phases}")
