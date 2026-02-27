"""
System3 Phase 382: Ultra Models Sanity Validator

Purpose: Load each Ultra model and run quick smoke test (synthetic batch prediction)
Outputs: JSON metrics + Markdown report

Safety: DRY-RUN only, uses synthetic data, no live trading
"""

import sys
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger
from core.engine.ultra_models_loader import load_ultra_model, SUPPORTED_UNDERLYINGS
from core.engine.ai_model import predict_direction

# Output paths
METRICS_DIR = ROOT_DIR / "storage" / "metrics"
REPORTS_DIR = ROOT_DIR / "reports"
METRICS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def create_synthetic_test_data(underlying: str, num_rows: int = 5) -> pd.DataFrame:
    """
    Create synthetic test DataFrame with typical features.

    Args:
        underlying: "NIFTY", "BANKNIFTY", etc.
        num_rows: Number of test rows

    Returns:
        DataFrame with all required features for prediction
    """
    np.random.seed(42)  # Reproducible

    df = pd.DataFrame(
        {
            "underlying": [underlying] * num_rows,
            "strike": np.random.choice([23000, 23500, 24000], num_rows),
            "side": np.random.choice(["CE", "PE"], num_rows),
            "spot": [23450.0] * num_rows,
            # Greeks
            "delta": np.random.uniform(0.2, 0.8, num_rows),
            "gamma": np.random.uniform(0.001, 0.02, num_rows),
            "theta": np.random.uniform(-1.0, -0.1, num_rows),
            "vega": np.random.uniform(5.0, 20.0, num_rows),
            "iv": np.random.uniform(0.15, 0.35, num_rows),
            # Price features
            "ltp": np.random.uniform(50.0, 200.0, num_rows),
            "oi": np.random.randint(10000, 100000, num_rows),
            "volume": np.random.randint(1000, 50000, num_rows),
            # Trend features (basic)
            "trend_score": np.random.uniform(-0.5, 0.5, num_rows),
            "volatility_score": np.random.uniform(0.0, 1.0, num_rows),
            "breakout_score": np.random.uniform(-0.3, 0.3, num_rows),
            "momentum_score": np.random.uniform(-0.4, 0.4, num_rows),
        }
    )

    return df


def run_phase_382() -> dict:
    """
    Phase 382: Ultra Model Sanity Validator

    Quick load + predict on small synthetic batch to confirm models run without error.

    Writes:
    - storage/metrics/ultra_models_validation_382.json
    - reports/ULTRA_MODELS_VALIDATION_382.md

    Returns:
        {"status": "ok"|"warn"|"error", "message": str, "metrics": dict}
    """
    logger.info("=" * 60)
    logger.info("PHASE 382: ULTRA MODELS SANITY VALIDATOR")
    logger.info("=" * 60)

    validation_results = {
        "validation_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "models_tested": 0,
        "models_passed": 0,
        "models_failed": 0,
        "test_results": [],
    }

    try:
        for underlying in SUPPORTED_UNDERLYINGS:
            logger.info(f"Testing {underlying}...")

            test_result = {
                "underlying": underlying,
                "model_loaded": False,
                "prediction_success": False,
                "error_message": None,
                "output_shape": None,
            }

            try:
                # Step 1: Load model
                model = load_ultra_model(underlying)
                if not model:
                    test_result["error_message"] = "Model not found"
                    validation_results["models_failed"] += 1
                    validation_results["test_results"].append(test_result)
                    logger.warning(f"  ❌ {underlying}: Model not found")
                    continue

                test_result["model_loaded"] = True

                # Step 2: Create synthetic test data
                test_df = create_synthetic_test_data(underlying, num_rows=5)

                # Step 3: Run prediction
                result_df = predict_direction(model, test_df)

                # Step 4: Verify output
                if "ai_score" in result_df.columns:
                    test_result["prediction_success"] = True
                    test_result["output_shape"] = f"{len(result_df)} rows"
                    validation_results["models_passed"] += 1
                    logger.info(f"  ✅ {underlying}: Prediction successful ({len(result_df)} rows)")
                else:
                    test_result["error_message"] = "No ai_score column in output"
                    validation_results["models_failed"] += 1
                    logger.warning(f"  ⚠️ {underlying}: No ai_score in output")

            except Exception as e:
                test_result["error_message"] = str(e)
                validation_results["models_failed"] += 1
                logger.error(f"  ❌ {underlying}: {e}")

            validation_results["test_results"].append(test_result)
            validation_results["models_tested"] += 1

        # Write JSON metrics
        metrics_file = METRICS_DIR / "ultra_models_validation_382.json"
        with open(metrics_file, "w") as f:
            json.dump(validation_results, f, indent=2)
        logger.info(f"✓ Metrics written: {metrics_file}")

        # Write Markdown report
        report_file = REPORTS_DIR / "ULTRA_MODELS_VALIDATION_382.md"
        with open(report_file, "w") as f:
            f.write("# ULTRA MODELS VALIDATION (PHASE 382)\n\n")
            f.write(f"**Validation Timestamp:** {validation_results['validation_timestamp']}\n")
            f.write(f"**Models Tested:** {validation_results['models_tested']}\n")
            f.write(f"**Models Passed:** {validation_results['models_passed']}\n")
            f.write(f"**Models Failed:** {validation_results['models_failed']}\n\n")

            f.write("## Smoke Test Results\n\n")
            f.write("| Underlying | Model Loaded | Prediction Success | Output | Error |\n")
            f.write("|------------|--------------|-------------------|--------|-------|\n")

            for result in validation_results["test_results"]:
                model_status = "✅" if result["model_loaded"] else "❌"
                pred_status = "✅" if result["prediction_success"] else "❌"
                output = result["output_shape"] if result["output_shape"] else "N/A"
                error = result["error_message"] if result["error_message"] else "-"

                f.write(f"| {result['underlying']} | {model_status} | {pred_status} | {output} | {error} |\n")

            f.write("\n## Summary\n\n")
            if validation_results["models_failed"] == 0:
                f.write("✅ **Status:** All Ultra models passed smoke tests\n")
                f.write("\n**Recommendation:** Proceed to Phase 383 (Backtest Sampler)\n")
            elif validation_results["models_passed"] > 0:
                f.write(
                    f"⚠️ **Status:** Partial validation ({validation_results['models_passed']}/{validation_results['models_tested']} passed)\n"
                )
                f.write("\n**Recommendation:** Failed models will use delta fallback\n")
            else:
                f.write("❌ **Status:** All models failed validation\n")
                f.write("\n**Recommendation:** Review error logs and model files\n")

        logger.info(f"✓ Report written: {report_file}")

        # Determine phase status
        if validation_results["models_failed"] == 0:
            status = "ok"
            message = f"All {validation_results['models_passed']} models passed smoke tests"
        elif validation_results["models_passed"] > 0:
            status = "warn"
            message = f"{validation_results['models_passed']}/{validation_results['models_tested']} models passed"
        else:
            status = "error"
            message = "All models failed validation"

        logger.info(f"Phase 382 Status: {status.upper()} - {message}")
        logger.info("=" * 60)

        return {"status": status, "message": message, "metrics": validation_results}

    except Exception as e:
        logger.error(f"Phase 382 ERROR: {e}")
        return {"status": "error", "message": f"Phase 382 failed: {str(e)}", "metrics": {}}


if __name__ == "__main__":
    result = run_phase_382()
    print(f"\nPhase 382 Result: {result['status'].upper()} - {result['message']}")
    sys.exit(0 if result["status"] in ["ok", "warn"] else 1)
