"""
System3 Phases 389-400 Registry
================================

Registry metadata for ML Pipeline Upgrade phases (389-400).

Author: System3 AI Team
Date: 2025-12-08
"""

PHASES_389_400_REGISTRY = {
    389: {
        "id": 389,
        "name": "Feature Engineering Upgrade",
        "module": "core.engine.ai_model.feature_engineering_v2",
        "function": "run_phase_389",
        "dependencies": [],
        "outputs": ["storage/datasets/feature_engineered_389.csv", "storage/metrics/feature_engineering_389.json"],
        "description": "Add 40+ high-variance features (Greeks momentum, IV regimes, price/moneyness, volume/OI, time-based, multi-timeframe)",
    },
    390: {
        "id": 390,
        "name": "SMOTE Data Balancing",
        "module": "core.engine.system3_phase390_smote_balancing",
        "function": "run_phase_390",
        "dependencies": [389],
        "outputs": ["storage/datasets/phase_390_balanced_features.csv", "storage/metrics/phase_390_smote_report.json"],
        "description": "Balance BUY/SELL/HOLD classes from imbalanced to 33/33/33 using SMOTE with upsampling fallback",
    },
    391: {
        "id": 391,
        "name": "XGBoost Model Training",
        "module": "core.engine.system3_phase391_xgboost_training",
        "function": "run_phase_391",
        "dependencies": [390],
        "inputs": ["storage/datasets/phase_390_balanced_features.csv"],
        "outputs": [
            "models/xgboost_v1/{UNDERLYING}_xgb_model.pkl",
            "models/xgboost_v1/{UNDERLYING}_xgb_meta.json",
            "storage/metrics/phase_391_xgb_metrics.json",
        ],
        "description": "Train per-underlying XGBoost classifiers on balanced Phase 390 dataset (BUY/SELL/HOLD). Generates models, metrics, and feature importance.",
        "safety_mode": "DRY_RUN_ONLY",
        "tags": ["ml", "training", "xgboost", "balanced_data", "ensemble_input"],
        "target_accuracy": "60-70%",
        "supports_fallback": True,
        "fallback_method": "GradientBoostingClassifier",
    },
    392: {
        "id": 392,
        "name": "Ultra + ML + Delta Ensemble",
        "module": "core.engine.system3_phase392_ensemble_integration",
        "function": "run_phase_392",
        "dependencies": [391],
        "inputs": [
            "models/xgboost_v1/{UNDERLYING}_xgb_model.pkl",
            "core/models/angel_one_ultra/{UNDERLYING}_ultra_model.pkl",
            "storage/datasets/phase_390_balanced_features.csv",
        ],
        "outputs": [
            "storage/outputs/phase_392_ensemble_scores_sample.csv",
            "storage/metrics/phase_392_ensemble_report.json",
        ],
        "description": "Three-layer ensemble (Ultra 50%, XGBoost 40%, Delta 10%) with score normalization to [-1, +1]",
        "safety_mode": "DRY_RUN_ONLY",
        "tags": ["ensemble", "integration", "three-layer", "ultra+ml+delta", "weighted_voting"],
        "target_accuracy": "70-75%",
        "supports_fallback": True,
        "fallback_method": "delta_fallback_score",
    },
    393: {
        "id": 393,
        "name": "Score Normalization Engine",
        "module": "core.engine.system3_phases_393_400",
        "function": "run_phase_393",
        "dependencies": [392],
        "outputs": ["storage/metrics/score_normalization_393.json"],
        "description": "Min-max, z-score, and Sorenson similarity normalization",
    },
    394: {
        "id": 394,
        "name": "Real PnL Outcome Learning",
        "module": "core.engine.system3_phases_393_400",
        "function": "run_phase_394",
        "dependencies": [393],
        "outputs": ["storage/metrics/pnl_learning_394.json"],
        "description": "Learn from real trades in pnl_log.csv with 3x weighting",
    },
    395: {
        "id": 395,
        "name": "Drift Detector Upgrade",
        "module": "core.engine.system3_phases_393_400",
        "function": "run_phase_395",
        "dependencies": [394],
        "outputs": ["storage/metrics/drift_detection_395.json"],
        "description": "KS test, feature drift detection, and auto-retrain triggering",
    },
    396: {
        "id": 396,
        "name": "Daily Auto-Retraining Engine",
        "module": "core.engine.system3_phases_393_400",
        "function": "run_phase_396",
        "dependencies": [395],
        "outputs": ["storage/metrics/auto_retrain_396.json"],
        "description": "EOD batch retraining (18:00 IST daily)",
    },
    397: {
        "id": 397,
        "name": "Probability-Based Risk Controller",
        "module": "core.engine.system3_phases_393_400",
        "function": "run_phase_397",
        "dependencies": [396],
        "outputs": ["storage/metrics/dynamic_risk_397.json"],
        "description": "Dynamic thresholds per underlying (NIFTY:0.10, BANKNIFTY:0.12, FINNIFTY:0.15)",
    },
    398: {
        "id": 398,
        "name": "Paper Trading Validation Loop",
        "module": "core.engine.system3_phases_393_400",
        "function": "run_phase_398",
        "dependencies": [397],
        "outputs": ["storage/metrics/paper_trading_validation_398.json"],
        "description": "30-snapshot test comparing Ultra vs XGBoost vs Ensemble",
    },
    399: {
        "id": 399,
        "name": "Scoring Telemetry v2.0",
        "module": "core.engine.system3_phases_393_400",
        "function": "run_phase_399",
        "dependencies": [398],
        "outputs": ["storage/metrics/scoring_telemetry_399.json"],
        "description": "Capture 20+ metrics per signal",
    },
    400: {
        "id": 400,
        "name": "Production-Readiness Report",
        "module": "core.engine.system3_phases_393_400",
        "function": "run_phase_400",
        "dependencies": list(range(389, 400)),  # All previous phases
        "outputs": ["storage/metrics/production_readiness_400.json"],
        "description": "7-point checklist and Go/No-Go decision",
    },
}


def get_phase_info(phase_id: int) -> dict:
    """Get registry information for a specific phase."""
    return PHASES_389_400_REGISTRY.get(phase_id, {})


def get_all_phases() -> dict:
    """Get complete registry."""
    return PHASES_389_400_REGISTRY


def get_phase_dependencies(phase_id: int) -> list:
    """Get dependencies for a phase."""
    phase_info = get_phase_info(phase_id)
    return phase_info.get("dependencies", [])


def get_phases_in_order() -> list:
    """Get phases in execution order (sorted by ID)."""
    return sorted(PHASES_389_400_REGISTRY.keys())
