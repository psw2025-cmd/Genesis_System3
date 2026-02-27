"""
System3 Phases 381-388 Registry

Registers all 8 phases (Ultra Models implementation) with metadata.
"""

PHASES_381_388 = [
    {
        "phase_id": 381,
        "name": "Ultra Models Scanner",
        "module": "core.engine.system3_phase381_ultra_models_scanner",
        "function": "run_phase_381",
        "description": "Scan and inventory all available Ultra models",
        "category": "discovery",
        "dependencies": [],
        "outputs": ["storage/metrics/ultra_models_inventory_381.json", "reports/ULTRA_MODELS_INVENTORY_381.md"],
    },
    {
        "phase_id": 382,
        "name": "Ultra Models Validator",
        "module": "core.engine.system3_phase382_ultra_models_validator",
        "function": "run_phase_382",
        "description": "Quick smoke test - load each model and predict on synthetic batch",
        "category": "validation",
        "dependencies": [381],
        "outputs": ["storage/metrics/ultra_models_validation_382.json", "reports/ULTRA_MODELS_VALIDATION_382.md"],
    },
    {
        "phase_id": 383,
        "name": "Ultra Backtest Sampler",
        "module": "core.engine.system3_phase383_ultra_backtest_sampler",
        "function": "run_phase_383",
        "description": "Compare Ultra models vs Delta scoring on historical sample",
        "category": "analysis",
        "dependencies": [381, 382],
        "outputs": ["storage/metrics/ultra_vs_delta_backtest_383.json", "reports/ULTRA_VS_DELTA_BACKTEST_383.md"],
    },
    {
        "phase_id": 384,
        "name": "Ultra Health Summary",
        "module": "core.engine.system3_phase384_ultra_health_summary",
        "function": "run_phase_384",
        "description": "Aggregate results from phases 381-383",
        "category": "reporting",
        "dependencies": [381, 382, 383],
        "outputs": ["reports/ULTRA_MODEL_HEALTH_384.md"],
    },
    {
        "phase_id": 385,
        "name": "Scoring Telemetry",
        "module": "core.engine.system3_phase385_scoring_telemetry",
        "function": "run_phase_385",
        "description": "Track how often Ultra vs Delta scoring is used in live runs",
        "category": "monitoring",
        "dependencies": [381],
        "outputs": ["storage/metrics/scoring_telemetry_385.json", "reports/SCORING_TELEMETRY_385.md"],
    },
    {
        "phase_id": 386,
        "name": "Fail-Safe Guard",
        "module": "core.engine.system3_phase386_failsafe_guard",
        "function": "run_phase_386",
        "description": "Verify delta fallback works if Ultra models are missing/broken",
        "category": "safety",
        "dependencies": [381, 382],
        "outputs": ["storage/metrics/failsafe_guard_386.json", "reports/FAILSAFE_GUARD_386.md"],
    },
    {
        "phase_id": 387,
        "name": "Impact Preview",
        "module": "core.engine.system3_phase387_impact_preview",
        "function": "run_phase_387",
        "description": "Estimate expected improvement in win-rate from Ultra models",
        "category": "analysis",
        "dependencies": [383],
        "outputs": ["reports/ULTRA_MODELS_IMPACT_PREVIEW_387.md"],
    },
    {
        "phase_id": 388,
        "name": "Health Gate",
        "module": "core.engine.system3_phase388_health_gate",
        "function": "run_phase_388",
        "description": "Final gate check before declaring phases 381-388 complete",
        "category": "verification",
        "dependencies": [381, 382, 383, 384, 385, 386, 387],
        "outputs": ["storage/metrics/phase_381_388_health_gate.json", "reports/PHASE_381_388_HEALTH_GATE.md"],
    },
]


def get_phase(phase_id: int) -> dict:
    """Get phase metadata by ID."""
    for phase in PHASES_381_388:
        if phase["phase_id"] == phase_id:
            return phase
    return None


def get_all_phases() -> list:
    """Get all phases 381-388."""
    return PHASES_381_388


def get_phases_by_category(category: str) -> list:
    """Get phases by category (discovery, validation, analysis, reporting, monitoring, safety, verification)."""
    return [p for p in PHASES_381_388 if p["category"] == category]


if __name__ == "__main__":
    print("SYSTEM3 PHASES 381-388 REGISTRY")
    print("=" * 60)
    print(f"Total Phases: {len(PHASES_381_388)}")
    print("\nPhases:")
    for phase in PHASES_381_388:
        print(f"  Phase {phase['phase_id']}: {phase['name']} ({phase['category']})")
