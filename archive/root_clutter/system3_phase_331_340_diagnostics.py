"""
System3 Phases 331-340 Diagnostics Module

Provides phase imports for autorun master integration.
"""

# Phase modules for phases 331-340
PHASE_MODULES = {
    331: "system3_phase331_signal_integrity",
    332: "system3_phase332_signal_volume_coverage",
    333: "system3_phase333_signal_consistency",
    334: "system3_phase334_model_drift_snapshot",
    335: "system3_phase335_model_drift_analyzer",
    336: "system3_phase336_safe_mode_suggestor",
    337: "system3_phase337_forward_return_quality_tracker",
    338: "system3_phase338_signal_outcome_correlation",
    339: "system3_phase339_daily_signal_pipeline_summary",
    340: "system3_phase340_signal_pipeline_regression_guard",
}

# Phase imports mapping (module_name, function_name)
PHASE_IMPORTS = {
    331: ("system3_phase331_signal_integrity", "run_phase_331"),
    332: ("system3_phase332_signal_volume_coverage", "run_phase_332"),
    333: ("system3_phase333_signal_consistency", "run_phase_333"),
    334: ("system3_phase334_model_drift_snapshot", "run_phase_334"),
    335: ("system3_phase335_model_drift_analyzer", "run_phase_335"),
    336: ("system3_phase336_safe_mode_suggestor", "run_phase_336"),
    337: ("system3_phase337_forward_return_quality_tracker", "run_phase_337"),
    338: ("system3_phase338_signal_outcome_correlation", "run_phase_338"),
    339: ("system3_phase339_daily_signal_pipeline_summary", "run_phase_339"),
    340: ("system3_phase340_signal_pipeline_regression_guard", "run_phase_340"),
}
