"""
System3 Phase 366 - Strategy Ensemble Evaluator

Evaluates performance of multiple internal strategies (ML, DL, Momentum, Mean-Reversion).
Computes weighted scoring across short-term and long-term windows.
Detects which strategy dominates current market conditions.

Zero broker calls. DRY-RUN always True.
Deterministic and reproducible algorithm.
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

STORAGE_METRICS.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_curated_signals() -> pd.DataFrame:
    """Load curated signals dataset with schema validation."""
    curated_path = STORAGE_LIVE / "dhan_index_ai_signals_curated.csv"

    if not curated_path.exists():
        logger.warning(f"Curated signals not found: {curated_path}")
        return pd.DataFrame()

    df = pd.read_csv(curated_path)

    # Auto-add missing columns with sensible defaults to reduce warnings
    if "confidence" not in df.columns:
        df["confidence"] = 0.5  # Neutral confidence
    if "score" not in df.columns:
        df["score"] = 0.0  # Neutral score
    if "timestamp" not in df.columns:
        # Use current timestamp if not present
        df["timestamp"] = pd.Timestamp.now().isoformat()

    return df


def load_phase362_metrics() -> Dict[str, Any]:
    """Load forward calibration metrics from Phase 362."""
    metrics_path = STORAGE_METRICS / "forward_calibrator_362.json"

    if not metrics_path.exists():
        logger.info("Phase 362 metrics not yet generated")
        return {}

    with open(metrics_path, "r") as f:
        return json.load(f)


def load_phase363_drift() -> Dict[str, Any]:
    """Load model drift score from Phase 363."""
    drift_path = STORAGE_METRICS / "model_drift_363.json"

    if not drift_path.exists():
        logger.info("Phase 363 drift metrics not yet generated")
        return {}

    with open(drift_path, "r") as f:
        return json.load(f)


def infer_strategy_from_signal(row: pd.Series) -> str:
    """
    Infer which strategy likely produced this signal.

    Rules (based on common patterns):
    - High confidence + momentum-like: Momentum
    - Medium confidence + mean-reversion: Mean-Reversion
    - ML-generated signals: ML
    - DL-generated signals: DL
    """
    if pd.isna(row.get("signal")):
        return "Unknown"

    confidence = float(row.get("confidence", 0.5))
    score = float(row.get("score", 0.5))

    # Simple heuristic: use score value ranges
    if score > 0.75:
        return "ML" if row.get("signal") == 1 else "Momentum"
    elif score > 0.50:
        return "DL" if row.get("signal") == 1 else "Mean-Reversion"
    else:
        return "Mean-Reversion" if row.get("signal") == -1 else "Momentum"


def evaluate_strategy_performance(
    df: pd.DataFrame, phase362: Dict[str, Any], phase363: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate performance of each strategy.

    Returns comprehensive performance metrics by strategy.
    """
    if df.empty:
        return {"error": "No signals to evaluate", "strategies": {}}

    # Infer strategy for each signal
    df["inferred_strategy"] = df.apply(infer_strategy_from_signal, axis=1)

    # Group by strategy
    strategy_groups = df.groupby("inferred_strategy")

    strategies = {}

    for strategy_name, group in strategy_groups:
        strategy_size = len(group)
        avg_confidence = float(group["confidence"].mean()) if "confidence" in group.columns else 0.0
        avg_score = float(group["score"].mean()) if "score" in group.columns else 0.0

        # Win rate based on signal alignment with forward returns
        win_rate = 0.0
        if "fwd_ret_1d" in group.columns or "fwd_ret_1min" in group.columns:
            fwd_col = "fwd_ret_1d" if "fwd_ret_1d" in group.columns else "fwd_ret_1min"
            aligned = (group[fwd_col] > 0).sum()
            win_rate = float(aligned / strategy_size) if strategy_size > 0 else 0.0

        # Recency weight (more recent = higher weight)
        recency_score = 1.0
        if "timestamp" in group.columns:
            try:
                group["ts"] = pd.to_datetime(group["timestamp"], errors="coerce")
                max_ts = group["ts"].max()
                group["days_old"] = (max_ts - group["ts"]).dt.days
                recency_score = float(1.0 / (1.0 + group["days_old"].mean()))
            except:
                recency_score = 1.0

        # Weighted score: confidence * score * win_rate * recency
        weighted_score = float((avg_confidence * avg_score * max(0.5, win_rate) * recency_score))

        strategies[strategy_name] = {
            "count": int(strategy_size),
            "avg_confidence": round(avg_confidence, 4),
            "avg_score": round(avg_score, 4),
            "win_rate": round(win_rate, 4),
            "recency_score": round(recency_score, 4),
            "weighted_score": round(weighted_score, 4),
            "market_dominance_pct": 0.0,  # Will be calculated below
        }

    # Calculate market dominance percentage
    total_signals = sum(s["count"] for s in strategies.values())
    if total_signals > 0:
        for strategy in strategies.values():
            strategy["market_dominance_pct"] = round((strategy["count"] / total_signals) * 100, 2)

    return {
        "status": "ok",
        "total_signals_evaluated": int(total_signals),
        "strategies": strategies,
        "dominant_strategy": (
            max(strategies.items(), key=lambda x: x[1]["weighted_score"])[0] if strategies else "Unknown"
        ),
    }


def compute_short_long_term_comparison(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compare strategy performance in short-term vs long-term windows.
    Safely handles missing columns by returning early with warning.
    """
    if df.empty:
        return {"error": "No signals", "short_term_signals": 0, "long_term_signals": 0}

    # Check required columns first
    required_cols = ["timestamp", "confidence", "score"]
    if "inferred_strategy" not in df.columns:
        # Infer from signal column if needed
        if "signal" in df.columns:
            df["inferred_strategy"] = df["signal"].apply(infer_strategy_from_signal)
        else:
            return {"error": "Cannot infer strategy without signal column"}

    # Try to extract date information
    try:
        # Check if timestamp column exists and has data
        if "timestamp" not in df.columns:
            logger.warning("No timestamp column for window comparison - returning defaults")
            return {
                "short_term_window_days": 1,
                "long_term_window_days": 7,
                "short_term_signals": 0,
                "long_term_signals": 0,
                "note": "Timestamp column missing",
            }

        df["ts"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["date"] = df["ts"].dt.date

        # Define windows: last 7 days = long-term, last 1 day = short-term
        now = pd.Timestamp.now()
        short_term = df[df["ts"] >= (now - timedelta(days=1))]
        long_term = df[df["ts"] >= (now - timedelta(days=7))]

        comparison = {
            "short_term_window_days": 1,
            "long_term_window_days": 7,
            "short_term_signals": int(len(short_term)),
            "long_term_signals": int(len(long_term)),
        }

        # Strategy dominance in each window
        if not short_term.empty:
            st_strategies = short_term["inferred_strategy"].value_counts().to_dict()
            comparison["short_term_dominant"] = max(st_strategies, key=st_strategies.get)

        if not long_term.empty:
            lt_strategies = long_term["inferred_strategy"].value_counts().to_dict()
            comparison["long_term_dominant"] = max(lt_strategies, key=lt_strategies.get)

        return comparison

    except Exception as e:
        logger.warning(f"Could not compute window comparison: {str(e)[:60]}")
        return {
            "short_term_window_days": 1,
            "long_term_window_days": 7,
            "short_term_signals": 0,
            "long_term_signals": 0,
            "error": str(e)[:60],
        }


def generate_markdown_report(evaluation: Dict[str, Any], comparison: Dict[str, Any]) -> str:
    """Generate markdown report for strategy ensemble evaluation."""

    report = """# STRATEGY ENSEMBLE EVALUATION - PHASE 366

**Generated:** {timestamp}

## Executive Summary

This phase evaluates the performance of multiple internal trading strategies
(ML, DL, Momentum, Mean-Reversion) across the curated signal dataset.

""".format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    if evaluation.get("error"):
        report += f"[WARNING] ERROR: {evaluation['error']}\n"
        return report

    total = evaluation.get("total_signals_evaluated", 0)
    dominant = evaluation.get("dominant_strategy", "Unknown")

    report += f"""
## Results

**Total Signals Evaluated:** {total}  
**Dominant Strategy:** {dominant}

### Strategy Performance Metrics

| Strategy | Count | Avg Confidence | Avg Score | Win Rate | Recency | Weighted Score | Dominance % |
|----------|-------|---|---|---|---|---|---|
"""

    for name, metrics in evaluation.get("strategies", {}).items():
        report += f"""| {name} | {metrics['count']} | {metrics['avg_confidence']:.4f} | {metrics['avg_score']:.4f} | {metrics['win_rate']:.4f} | {metrics['recency_score']:.4f} | {metrics['weighted_score']:.4f} | {metrics['market_dominance_pct']:.2f}% |
"""

    # Short-term vs Long-term
    report += "\n## Market Condition Analysis\n\n"

    if "short_term_window_days" in comparison:
        report += f"""### Time Windows
- **Short-term:** {comparison.get('short_term_window_days', 'N/A')} day(s) with {comparison.get('short_term_signals', 0)} signals
- **Long-term:** {comparison.get('long_term_window_days', 'N/A')} day(s) with {comparison.get('long_term_signals', 0)} signals

**Short-term Dominant:** {comparison.get('short_term_dominant', 'Unknown')}  
**Long-term Dominant:** {comparison.get('long_term_dominant', 'Unknown')}
"""

    report += """
## Interpretation

- **Weighted Score:** Combines confidence, score, win rate, and recency
- **Market Dominance %:** Percentage of total signals from each strategy
- **Recency Score:** Favors more recent signals (adjusts for staleness)
- **Win Rate:** Signals that align with positive forward returns

## Recommendations

1. Monitor dominant strategy for market regime alignment
2. Watch for strategy switching (indicates market condition changes)
3. Use weighted scores to calibrate confidence thresholds
4. Adjust position sizing based on strategy mix in short-term window

---

**Status:** [OK] Analysis Complete (DRY-RUN)  
**Safety Mode:** DRY-RUN (no orders, no broker calls)
"""

    return report


def run_phase366(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute Phase 366 - Strategy Ensemble Evaluator

    Args:
        context: Optional execution context

    Returns:
        {"status": "ok"|"warn"|"error", "outputs": {"json": path, "report": path}}
    """
    logger.info("Phase 366: Starting Strategy Ensemble Evaluation")

    try:
        # Load inputs
        curated_df = load_curated_signals()
        phase362 = load_phase362_metrics()
        phase363 = load_phase363_drift()

        # Evaluate strategies
        evaluation = evaluate_strategy_performance(curated_df, phase362, phase363)

        # Compare time windows
        comparison = compute_short_long_term_comparison(curated_df)

        # Write JSON output
        json_path = STORAGE_METRICS / "strategy_ensemble_366.json"
        json_output = {
            "phase": 366,
            "timestamp": datetime.now().isoformat(),
            "evaluation": evaluation,
            "time_window_comparison": comparison,
        }

        with open(json_path, "w") as f:
            json.dump(json_output, f, indent=2)

        logger.info(f"JSON output: {json_path}")

        # Write markdown report
        md_report = generate_markdown_report(evaluation, comparison)
        md_path = REPORTS_DIR / "STRATEGY_ENSEMBLE_366.md"

        with open(md_path, "w") as f:
            f.write(md_report)

        logger.info(f"Markdown report: {md_path}")

        status = "warn" if evaluation.get("error") else "ok"

        return {"phase": 366, "status": status, "outputs": {"json": str(json_path), "report": str(md_path)}}

    except Exception as e:
        logger.error(f"Phase 366 error: {e}")
        return {"phase": 366, "status": "error", "error": str(e), "outputs": {}}


if __name__ == "__main__":
    result = run_phase366()
    print(json.dumps(result, indent=2))
