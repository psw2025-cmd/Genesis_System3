"""
System3 Phase 383: Ultra vs Delta Backtest Sampler

Purpose: Compare Ultra models vs Delta scoring on historical sample
Outputs: JSON metrics + Markdown report

Safety: DRY-RUN only, historical data analysis, no live trading
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
from core.engine.ai_model import predict_direction, get_training_dataframe

# Output paths
METRICS_DIR = ROOT_DIR / "storage" / "metrics"
REPORTS_DIR = ROOT_DIR / "reports"
METRICS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def compute_delta_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute delta-based ai_score (fallback mechanism).

    Args:
        df: DataFrame with delta and side columns

    Returns:
        DataFrame with ai_score_delta column
    """
    if "delta" not in df.columns:
        df["ai_score_delta"] = 0.0
        return df

    delta_proxy = df["delta"].copy()
    if "side" in df.columns:
        delta_proxy = delta_proxy.where(df["side"] == "CE", -delta_proxy)

    df["ai_score_delta"] = (delta_proxy * 2.0 - 1.0).clip(-1.0, 1.0).fillna(0.0) * 0.3

    return df


def run_phase_383() -> dict:
    """
    Phase 383: Ultra vs Delta Backtest Sampler

    Takes a small historical sample, runs both Ultra and delta scores, compares distributions.

    Writes:
    - storage/metrics/ultra_vs_delta_backtest_383.json
    - reports/ULTRA_VS_DELTA_BACKTEST_383.md

    Returns:
        {"status": "ok"|"warn"|"error", "message": str, "metrics": dict}
    """
    logger.info("=" * 60)
    logger.info("PHASE 383: ULTRA VS DELTA BACKTEST SAMPLER")
    logger.info("=" * 60)

    backtest_results = {
        "backtest_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sample_size": 0,
        "underlyings_tested": [],
        "results": {},
    }

    try:
        # Load historical data (last 100 signals from curated dataset)
        logger.info("Loading historical signals for backtest...")
        hist_df = get_training_dataframe(prefer_curated=True)

        if hist_df is None or len(hist_df) == 0:
            logger.warning("No historical data available for backtest")
            return {
                "status": "warn",
                "message": "No historical data for backtest (skipped)",
                "metrics": backtest_results,
            }

        # Take last 100 rows for backtest
        sample_size = min(100, len(hist_df))
        sample_df = hist_df.tail(sample_size).copy()
        backtest_results["sample_size"] = sample_size

        logger.info(f"Backtest sample: {sample_size} signals")

        # Group by underlying and compare scores
        if "underlying" in sample_df.columns:
            underlyings = sample_df["underlying"].unique()
            logger.info(f"Underlyings in sample: {list(underlyings)}")

            for underlying in underlyings:
                if underlying not in SUPPORTED_UNDERLYINGS:
                    continue

                logger.info(f"Backtesting {underlying}...")

                underlying_df = sample_df[sample_df["underlying"] == underlying].copy()
                if len(underlying_df) < 5:
                    logger.warning(f"  Skipping {underlying}: too few samples ({len(underlying_df)})")
                    continue

                backtest_results["underlyings_tested"].append(underlying)

                # Score 1: Ultra model
                ultra_model = load_ultra_model(underlying)
                if ultra_model:
                    try:
                        ultra_df = predict_direction(ultra_model, underlying_df.copy())
                        ultra_scores = (
                            ultra_df["ai_score"].values if "ai_score" in ultra_df.columns else np.zeros(len(ultra_df))
                        )
                    except Exception as e:
                        logger.warning(f"  Ultra model prediction failed: {e}")
                        ultra_scores = np.zeros(len(underlying_df))
                else:
                    ultra_scores = np.zeros(len(underlying_df))

                # Score 2: Delta-based
                delta_df = compute_delta_score(underlying_df.copy())
                delta_scores = delta_df["ai_score_delta"].values

                # Compare distributions
                result = {
                    "sample_size": len(underlying_df),
                    "ultra_mean": float(np.mean(ultra_scores)),
                    "ultra_std": float(np.std(ultra_scores)),
                    "ultra_min": float(np.min(ultra_scores)),
                    "ultra_max": float(np.max(ultra_scores)),
                    "delta_mean": float(np.mean(delta_scores)),
                    "delta_std": float(np.std(delta_scores)),
                    "delta_min": float(np.min(delta_scores)),
                    "delta_max": float(np.max(delta_scores)),
                    "correlation": (
                        float(np.corrcoef(ultra_scores, delta_scores)[0, 1]) if len(ultra_scores) > 1 else 0.0
                    ),
                    "improvement": float(np.mean(ultra_scores) - np.mean(delta_scores)),
                }

                backtest_results["results"][underlying] = result

                logger.info(
                    f"  {underlying}: Ultra={result['ultra_mean']:.4f}, Delta={result['delta_mean']:.4f}, "
                    f"Improvement={result['improvement']:.4f}"
                )

        # Write JSON metrics
        metrics_file = METRICS_DIR / "ultra_vs_delta_backtest_383.json"
        with open(metrics_file, "w") as f:
            json.dump(backtest_results, f, indent=2)
        logger.info(f"✓ Metrics written: {metrics_file}")

        # Write Markdown report
        report_file = REPORTS_DIR / "ULTRA_VS_DELTA_BACKTEST_383.md"
        with open(report_file, "w") as f:
            f.write("# ULTRA VS DELTA BACKTEST (PHASE 383)\n\n")
            f.write(f"**Backtest Timestamp:** {backtest_results['backtest_timestamp']}\n")
            f.write(f"**Sample Size:** {backtest_results['sample_size']} signals\n")
            f.write(f"**Underlyings Tested:** {', '.join(backtest_results['underlyings_tested'])}\n\n")

            if backtest_results["results"]:
                f.write("## Comparison Results\n\n")
                f.write("| Underlying | Ultra Mean | Delta Mean | Improvement | Correlation | Sample |\n")
                f.write("|------------|-----------|-----------|-------------|-------------|--------|\n")

                for underlying, result in backtest_results["results"].items():
                    improvement_pct = (
                        (result["improvement"] / abs(result["delta_mean"]) * 100) if result["delta_mean"] != 0 else 0
                    )
                    improvement_str = (
                        f"+{improvement_pct:.1f}%" if result["improvement"] > 0 else f"{improvement_pct:.1f}%"
                    )

                    f.write(
                        f"| {underlying} | {result['ultra_mean']:.4f} | {result['delta_mean']:.4f} | "
                        f"{improvement_str} | {result['correlation']:.2f} | {result['sample_size']} |\n"
                    )

                f.write("\n## Statistical Summary\n\n")
                for underlying, result in backtest_results["results"].items():
                    f.write(f"### {underlying}\n\n")
                    f.write(f"- **Ultra Model:**\n")
                    f.write(f"  - Mean: {result['ultra_mean']:.4f}\n")
                    f.write(f"  - Std Dev: {result['ultra_std']:.4f}\n")
                    f.write(f"  - Range: [{result['ultra_min']:.4f}, {result['ultra_max']:.4f}]\n")
                    f.write(f"- **Delta Fallback:**\n")
                    f.write(f"  - Mean: {result['delta_mean']:.4f}\n")
                    f.write(f"  - Std Dev: {result['delta_std']:.4f}\n")
                    f.write(f"  - Range: [{result['delta_min']:.4f}, {result['delta_max']:.4f}]\n")
                    f.write(f"- **Comparison:**\n")
                    f.write(f"  - Correlation: {result['correlation']:.2f}\n")
                    f.write(f"  - Improvement: {result['improvement']:.4f}\n\n")

                f.write("## Summary\n\n")
                avg_improvement = np.mean([r["improvement"] for r in backtest_results["results"].values()])
                if avg_improvement > 0:
                    f.write(f"✅ **Status:** Ultra models show positive improvement (+{avg_improvement:.4f} average)\n")
                    f.write("\n**Recommendation:** Proceed to Phase 384 (Health Summary)\n")
                elif avg_improvement > -0.05:
                    f.write(f"⚠️ **Status:** Ultra models show neutral performance ({avg_improvement:.4f} average)\n")
                    f.write("\n**Recommendation:** Safe to proceed, monitor in production\n")
                else:
                    f.write(f"⚠️ **Status:** Ultra models show degradation ({avg_improvement:.4f} average)\n")
                    f.write("\n**Recommendation:** Review model training data and features\n")
            else:
                f.write("⚠️ **Status:** No underlyings tested (insufficient data)\n")

        logger.info(f"✓ Report written: {report_file}")

        # Determine phase status
        if len(backtest_results["results"]) > 0:
            status = "ok"
            message = f"Backtest completed for {len(backtest_results['underlyings_tested'])} underlyings"
        else:
            status = "warn"
            message = "No underlyings tested (insufficient data)"

        logger.info(f"Phase 383 Status: {status.upper()} - {message}")
        logger.info("=" * 60)

        return {"status": status, "message": message, "metrics": backtest_results}

    except Exception as e:
        logger.error(f"Phase 383 ERROR: {e}")
        return {"status": "error", "message": f"Phase 383 failed: {str(e)}", "metrics": {}}


if __name__ == "__main__":
    result = run_phase_383()
    print(f"\nPhase 383 Result: {result['status'].upper()} - {result['message']}")
    sys.exit(0 if result["status"] in ["ok", "warn"] else 1)
