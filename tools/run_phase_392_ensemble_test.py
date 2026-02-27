"""
Phase 392 Ensemble Integration Test Runner
===========================================

Validates Phase 392 ensemble integration implementation.

Test Checks:
    1. XGBoost models from Phase 391 load correctly
    2. Ultra models loader is callable
    3. Delta fallback always works
    4. Ensemble score computed for sample rows
    5. Score distribution sanity (no NaN/Inf, bounded [-1, 1])

Exit Code:
    0 = PASSED (all checks passed)
    1 = FAILED (one or more checks failed)

Author: System3 AI Team
Date: 2025-12-08
"""

import os
import sys
import json
import pickle
from pathlib import Path
from datetime import datetime

# CRITICAL: Change to project root FIRST, before any imports
project_root = Path(__file__).resolve().parents[2]
os.chdir(str(project_root))

# Add project root to path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.engine.system3_phase392_ensemble_integration import (
    run_phase_392,
    EnsembleConfig,
    load_ultra_models,
    load_xgboost_models,
    delta_fallback_score,
    ensemble_predict,
    SUPPORTED_UNDERLYINGS,
)
from core.engine.ultra_models_loader import load_ultra_model
from model_training_v2 import load_balanced_dataset

import numpy as np
import pandas as pd


def test_check_1_xgboost_models():
    """Test Check 1: XGBoost models from Phase 391 load correctly"""
    print("\n[TEST] Check 1: XGBoost models load correctly...")

    config = EnsembleConfig()
    models_dir = project_root / config.xgboost_models_dir

    if not models_dir.exists():
        print(f"  [FAIL] XGBoost directory not found: {models_dir}")
        return False

    try:
        xgb_models = load_xgboost_models(config)

        if len(xgb_models) != len(SUPPORTED_UNDERLYINGS):
            print(f"  [FAIL] Expected {len(SUPPORTED_UNDERLYINGS)} models, got {len(xgb_models)}")
            return False

        for underlying, entry in xgb_models.items():
            if entry["model"] is None:
                print(f"  [FAIL] Model for {underlying} is None")
                return False
            print(f"  [OK] {underlying} model loaded")

        print(f"  [OK] All {len(xgb_models)} XGBoost models loaded successfully")
        return True

    except Exception as e:
        print(f"  [FAIL] Error loading XGBoost models: {e}")
        return False


def test_check_2_ultra_models_loader():
    """Test Check 2: Ultra models loader is callable"""
    print("\n[TEST] Check 2: Ultra models loader is callable...")

    try:
        ultra_models = load_ultra_models()

        if not isinstance(ultra_models, dict):
            print(f"  [FAIL] Expected dict, got {type(ultra_models)}")
            return False

        if len(ultra_models) != len(SUPPORTED_UNDERLYINGS):
            print(f"  [FAIL] Expected {len(SUPPORTED_UNDERLYINGS)} models, got {len(ultra_models)}")
            return False

        loaded_count = sum(1 for m in ultra_models.values() if m is not None)
        print(f"  [OK] Ultra models loader called successfully")
        print(f"  [OK] {loaded_count}/{len(ultra_models)} Ultra models available")

        return True

    except Exception as e:
        print(f"  [FAIL] Error calling Ultra models loader: {e}")
        return False


def test_check_3_delta_fallback():
    """Test Check 3: Delta fallback always works"""
    print("\n[TEST] Check 3: Delta fallback always works...")

    try:
        # Test 1: Normal features
        features = np.array([0.5, 0.3, 0.7, 0.2, 0.1])
        score = delta_fallback_score(features)

        if np.isnan(score) or np.isinf(score):
            print(f"  [FAIL] Delta fallback returned NaN/Inf for normal features")
            return False

        if not (-1.0 <= score <= 1.0):
            print(f"  [FAIL] Delta score out of bounds: {score}")
            return False

        print(f"  [OK] Delta fallback works for normal features: {score:.4f}")

        # Test 2: Features with NaN
        features_nan = np.array([0.5, np.nan, 0.7, np.nan, 0.1])
        score_nan = delta_fallback_score(features_nan)

        if np.isnan(score_nan) or np.isinf(score_nan):
            print(f"  [FAIL] Delta fallback returned NaN/Inf for NaN features")
            return False

        if not (-1.0 <= score_nan <= 1.0):
            print(f"  [FAIL] Delta score with NaN out of bounds: {score_nan}")
            return False

        print(f"  [OK] Delta fallback works for NaN features: {score_nan:.4f}")

        # Test 3: Features with Inf
        features_inf = np.array([0.5, np.inf, 0.7, -np.inf, 0.1])
        score_inf = delta_fallback_score(features_inf)

        if np.isnan(score_inf) or np.isinf(score_inf):
            print(f"  [FAIL] Delta fallback returned NaN/Inf for Inf features")
            return False

        if not (-1.0 <= score_inf <= 1.0):
            print(f"  [FAIL] Delta score with Inf out of bounds: {score_inf}")
            return False

        print(f"  [OK] Delta fallback works for Inf features: {score_inf:.4f}")

        # Test 4: Empty features
        features_empty = np.array([])
        score_empty = delta_fallback_score(features_empty)

        if np.isnan(score_empty) or np.isinf(score_empty):
            print(f"  [FAIL] Delta fallback returned NaN/Inf for empty features")
            return False

        if not (-1.0 <= score_empty <= 1.0):
            print(f"  [FAIL] Delta score for empty out of bounds: {score_empty}")
            return False

        print(f"  [OK] Delta fallback works for empty features: {score_empty:.4f}")

        return True

    except Exception as e:
        print(f"  [FAIL] Error testing delta fallback: {e}")
        return False


def test_check_4_ensemble_score():
    """Test Check 4: Ensemble score computed for sample rows"""
    print("\n[TEST] Check 4: Ensemble score computed for sample rows...")

    try:
        # Load dataset
        config = EnsembleConfig()
        dataset_path = project_root / config.dataset_path

        if not dataset_path.exists():
            print(f"  [FAIL] Dataset not found: {dataset_path}")
            return False

        df = pd.read_csv(dataset_path)
        print(f"  [OK] Loaded dataset: {len(df)} rows × {len(df.columns)} columns")

        # Load models
        ultra_models = load_ultra_models()
        xgb_models = load_xgboost_models(config)

        # Sample 50 random rows
        sample_size = min(50, len(df))
        sample_indices = np.random.choice(len(df), size=sample_size, replace=False)

        valid_scores = 0
        failed_scores = 0

        for idx in sample_indices:
            try:
                row = df.iloc[idx]
                underlying = row.get("underlying", "UNKNOWN")

                # Extract features
                feature_cols = [c for c in df.columns if c not in ["underlying", "signal", "side", "strike"]]
                features = row[feature_cols].values.astype(float)
                features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)

                # Compute ensemble score
                score = ensemble_predict(features, underlying, ultra_models, xgb_models, config)

                if np.isnan(score) or np.isinf(score):
                    print(f"  [WARN] Row {idx}: NaN/Inf score")
                    failed_scores += 1
                elif not (-1.0 <= score <= 1.0):
                    print(f"  [WARN] Row {idx}: score out of bounds {score}")
                    failed_scores += 1
                else:
                    valid_scores += 1

            except Exception as e:
                print(f"  [WARN] Row {idx}: {e}")
                failed_scores += 1

        if valid_scores == 0:
            print(f"  [FAIL] No valid scores computed out of {sample_size}")
            return False

        print(f"  [OK] Computed {valid_scores}/{sample_size} valid ensemble scores")

        return True

    except Exception as e:
        print(f"  [FAIL] Error computing ensemble scores: {e}")
        return False


def test_check_5_score_distribution():
    """Test Check 5: Score distribution sanity (no NaN/Inf, bounded [-1, 1])"""
    print("\n[TEST] Check 5: Score distribution sanity check...")

    try:
        # Run Phase 392
        print("  [INFO] Running Phase 392 to generate scores...")
        result = run_phase_392()

        if result.get("status") != "SUCCESS":
            print(f"  [FAIL] Phase 392 execution failed: {result.get('error', 'unknown')}")
            return False

        # Check score statistics
        score_stats = result.get("score_stats", {})

        # Check for NaN/Inf
        nan_count = score_stats.get("nan_count", 0)
        inf_count = score_stats.get("inf_count", 0)

        if nan_count > 0:
            print(f"  [FAIL] Found {nan_count} NaN scores")
            return False

        if inf_count > 0:
            print(f"  [FAIL] Found {inf_count} Inf scores")
            return False

        print(f"  [OK] No NaN/Inf scores (nan={nan_count}, inf={inf_count})")

        # Check bounds
        score_min = score_stats.get("min", 0)
        score_max = score_stats.get("max", 0)

        if score_min < -1.0 or score_max > 1.0:
            print(f"  [FAIL] Scores out of bounds: [{score_min:.4f}, {score_max:.4f}]")
            return False

        print(f"  [OK] All scores within bounds: [{score_min:.4f}, {score_max:.4f}]")

        # Print statistics
        score_mean = score_stats.get("mean", 0)
        score_std = score_stats.get("std", 0)

        print(f"  [OK] Score distribution:")
        print(f"       Mean: {score_mean:.4f}")
        print(f"       Std: {score_std:.4f}")
        print(f"       Min: {score_min:.4f}")
        print(f"       Max: {score_max:.4f}")

        # Check per-underlying
        per_underlying = result.get("per_underlying", {})

        if len(per_underlying) == 0:
            print(f"  [WARN] No per-underlying statistics")
        else:
            print(f"  [OK] Per-underlying stats:")
            for underlying, stats in per_underlying.items():
                print(
                    f"       {underlying}: n={stats.get('score_count', 0)}, "
                    f"mean={stats.get('score_mean', 0):.4f}, "
                    f"std={stats.get('score_std', 0):.4f}"
                )

        return True

    except Exception as e:
        print(f"  [FAIL] Error checking score distribution: {e}")
        import traceback

        traceback.print_exc()
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================


def main():
    """Run all Phase 392 tests"""

    print("\n" + "=" * 80)
    print("PHASE 392 ENSEMBLE INTEGRATION - TEST SUITE")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Mode: DRY-RUN")

    start_time = datetime.now()

    # Run tests
    checks = [
        ("XGBoost Models Load", test_check_1_xgboost_models),
        ("Ultra Models Loader", test_check_2_ultra_models_loader),
        ("Delta Fallback", test_check_3_delta_fallback),
        ("Ensemble Score", test_check_4_ensemble_score),
        ("Score Distribution", test_check_5_score_distribution),
    ]

    results = {}
    passed = 0
    failed = 0

    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = "PASSED" if result else "FAILED"

            if result:
                passed += 1
            else:
                failed += 1

        except Exception as e:
            print(f"\n[ERROR] Check '{check_name}' crashed: {e}")
            import traceback

            traceback.print_exc()

            results[check_name] = "ERROR"
            failed += 1

    # Summary
    duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)

    for check_name, status in results.items():
        status_icon = "✓" if status == "PASSED" else "✗"
        print(f"{status_icon} {check_name}: {status}")

    print("\n" + "=" * 80)
    print(f"Passed: {passed}/{len(checks)}")
    print(f"Failed: {failed}/{len(checks)}")
    print(f"Duration: {duration_ms} ms")
    print("=" * 80)

    if failed == 0:
        print("\n✓ TEST SUITE PASSED\n")
        return 0
    else:
        print(f"\n✗ TEST SUITE FAILED ({failed} checks failed)\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
