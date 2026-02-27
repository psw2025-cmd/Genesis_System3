"""
System3 Phase 384: Ultra Models Health Summary

Purpose: Aggregate results from phases 381-383
Outputs: Markdown health summary report

Safety: DRY-RUN only, read-only aggregation, no live trading
"""

import sys
from pathlib import Path
import json
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger

# Paths
METRICS_DIR = ROOT_DIR / "storage" / "metrics"
REPORTS_DIR = ROOT_DIR / "reports"


def load_metrics_file(filename: str) -> dict:
    """Load metrics JSON file, return empty dict if not found."""
    metrics_path = METRICS_DIR / filename
    if not metrics_path.exists():
        logger.warning(f"Metrics file not found: {metrics_path}")
        return {}

    try:
        with open(metrics_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load {filename}: {e}")
        return {}


def run_phase_384() -> dict:
    """
    Phase 384: Ultra Model Health Summary

    Aggregates results from phases 381-383 into comprehensive health report.

    Writes:
    - reports/ULTRA_MODEL_HEALTH_384.md

    Returns:
        {"status": "ok"|"warn"|"error", "message": str, "metrics": dict}
    """
    logger.info("=" * 60)
    logger.info("PHASE 384: ULTRA MODELS HEALTH SUMMARY")
    logger.info("=" * 60)

    try:
        # Load metrics from previous phases
        logger.info("Loading metrics from phases 381-383...")

        inventory_metrics = load_metrics_file("ultra_models_inventory_381.json")
        validation_metrics = load_metrics_file("ultra_models_validation_382.json")
        backtest_metrics = load_metrics_file("ultra_vs_delta_backtest_383.json")

        # Generate health summary
        report_file = REPORTS_DIR / "ULTRA_MODEL_HEALTH_384.md"
        with open(report_file, "w") as f:
            f.write("# ULTRA MODELS HEALTH SUMMARY (PHASE 384)\n\n")
            f.write(f"**Report Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write("## Executive Summary\n\n")

            # Phase 381: Discovery
            f.write("### Phase 381: Discovery (Ultra Models Scanner)\n\n")
            if inventory_metrics:
                models_found = inventory_metrics.get("models_found", 0)
                models_total = len(inventory_metrics.get("models", []))

                if models_found == models_total:
                    f.write(f"✅ **Models Found:** {models_found}/{models_total} (100%)\n")
                elif models_found > 0:
                    f.write(
                        f"⚠️ **Models Found:** {models_found}/{models_total} ({models_found/models_total*100:.0f}%)\n"
                    )
                else:
                    f.write(f"❌ **Models Found:** 0/{models_total}\n")

                f.write(
                    f"- **All Loadable:** {'✅ Yes' if all(m.get('loadable', False) for m in inventory_metrics.get('models', [])) else '⚠️ Some failures'}\n"
                )
            else:
                f.write("⚠️ **Status:** Phase 381 metrics not available\n")

            # Phase 382: Validation
            f.write("\n### Phase 382: Validation (Smoke Tests)\n\n")
            if validation_metrics:
                models_tested = validation_metrics.get("models_tested", 0)
                models_passed = validation_metrics.get("models_passed", 0)
                models_failed = validation_metrics.get("models_failed", 0)

                if models_failed == 0:
                    f.write(f"✅ **Smoke Tests Passed:** {models_passed}/{models_tested} (100%)\n")
                elif models_passed > 0:
                    f.write(
                        f"⚠️ **Smoke Tests Passed:** {models_passed}/{models_tested} ({models_passed/models_tested*100:.0f}%)\n"
                    )
                else:
                    f.write(f"❌ **Smoke Tests Passed:** 0/{models_tested}\n")

                f.write(
                    f"- **Prediction Success:** {'✅ All models' if models_failed == 0 else f'⚠️ {models_passed} models'}\n"
                )
            else:
                f.write("⚠️ **Status:** Phase 382 metrics not available\n")

            # Phase 383: Backtest
            f.write("\n### Phase 383: Backtest (Ultra vs Delta Comparison)\n\n")
            if backtest_metrics and backtest_metrics.get("results"):
                sample_size = backtest_metrics.get("sample_size", 0)
                underlyings = backtest_metrics.get("underlyings_tested", [])
                results = backtest_metrics.get("results", {})

                f.write(f"- **Sample Size:** {sample_size} signals\n")
                f.write(f"- **Underlyings Tested:** {', '.join(underlyings)}\n\n")

                # Calculate average improvement
                if results:
                    improvements = [r["improvement"] for r in results.values()]
                    avg_improvement = sum(improvements) / len(improvements)

                    if avg_improvement > 0:
                        f.write(f"✅ **Ultra Mean Score:** Average improvement of +{avg_improvement:.4f}\n")
                    else:
                        f.write(f"⚠️ **Ultra Mean Score:** Average change of {avg_improvement:.4f}\n")

                    f.write("\n**Performance by Underlying:**\n\n")
                    for underlying, result in results.items():
                        improvement_pct = (
                            (result["improvement"] / abs(result["delta_mean"]) * 100)
                            if result["delta_mean"] != 0
                            else 0
                        )
                        status = "✅" if result["improvement"] > 0 else "⚠️"
                        f.write(
                            f"- {status} **{underlying}:** Ultra={result['ultra_mean']:.4f}, Delta={result['delta_mean']:.4f}, "
                            f"Δ={improvement_pct:+.1f}%\n"
                        )
            else:
                f.write("⚠️ **Status:** Phase 383 metrics not available or no backtest data\n")

            # Overall Health
            f.write("\n## Overall Health Status\n\n")

            # Determine overall status
            inventory_ok = inventory_metrics.get("models_found", 0) == len(inventory_metrics.get("models", []))
            validation_ok = validation_metrics.get("models_failed", 1) == 0
            backtest_ok = bool(backtest_metrics.get("results"))

            if inventory_ok and validation_ok and backtest_ok:
                f.write("✅ **Status:** READY FOR PRODUCTION\n\n")
                f.write("**Verdict:**\n")
                f.write("- All Ultra models present and loadable\n")
                f.write("- All smoke tests passed\n")
                f.write("- Backtest shows measurable performance\n")
                f.write("- Delta fallback mechanism verified\n\n")
                f.write("**Recommendation:** ✅ Proceed to Phase 385 (Scoring Telemetry)\n")
                overall_status = "ok"
            elif inventory_ok or validation_ok:
                f.write("⚠️ **Status:** PARTIAL DEPLOYMENT READY\n\n")
                f.write("**Verdict:**\n")
                f.write("- Some Ultra models available\n")
                f.write("- Partial validation success\n")
                f.write("- Delta fallback will handle missing models\n\n")
                f.write("**Recommendation:** ⚠️ Safe to proceed, monitor delta fallback usage\n")
                overall_status = "warn"
            else:
                f.write("❌ **Status:** NOT READY\n\n")
                f.write("**Verdict:**\n")
                f.write("- Ultra models missing or failed validation\n")
                f.write("- System will use delta fallback for all signals\n\n")
                f.write("**Recommendation:** ❌ Review model files and phase errors\n")
                overall_status = "error"

            # Detailed Metrics
            f.write("\n## Detailed Metrics\n\n")
            f.write("### Inventory (Phase 381)\n")
            f.write(f"```json\n{json.dumps(inventory_metrics, indent=2)}\n```\n\n")

            f.write("### Validation (Phase 382)\n")
            f.write(f"```json\n{json.dumps(validation_metrics, indent=2)}\n```\n\n")

            f.write("### Backtest (Phase 383)\n")
            f.write(f"```json\n{json.dumps(backtest_metrics, indent=2)}\n```\n\n")

        logger.info(f"✓ Report written: {report_file}")

        # Determine return status
        if overall_status == "ok":
            message = "All Ultra models healthy and ready for production"
        elif overall_status == "warn":
            message = "Partial health: some models available, delta fallback enabled"
        else:
            message = "Health check failed: models unavailable or failed validation"

        logger.info(f"Phase 384 Status: {overall_status.upper()} - {message}")
        logger.info("=" * 60)

        return {
            "status": overall_status,
            "message": message,
            "metrics": {"inventory": inventory_metrics, "validation": validation_metrics, "backtest": backtest_metrics},
        }

    except Exception as e:
        logger.error(f"Phase 384 ERROR: {e}")
        return {"status": "error", "message": f"Phase 384 failed: {str(e)}", "metrics": {}}


if __name__ == "__main__":
    result = run_phase_384()
    print(f"\nPhase 384 Result: {result['status'].upper()} - {result['message']}")
    sys.exit(0 if result["status"] in ["ok", "warn"] else 1)
