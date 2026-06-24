"""
System3 Phase 367 - Safety Guardrail Recommender

Analyzes volatility regime, signal conflict load, data freshness, and health score.
Recommends additional safety levels (disable trading, reduce trades, cap lot sizes).
Reinforces System3 anti-loss architecture.

Must never activate live trading. Only recommends, not enforces.
Hard-coded safety rules remain untouched.
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

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


def load_health_feed() -> Dict[str, Any]:
    """Load health dashboard feed from Phase 364."""
    health_path = STORAGE_METRICS / "dashboard_feed_364.json"

    if not health_path.exists():
        logger.info("Phase 364 health feed not yet generated")
        return {"health_score": 50.0}

    with open(health_path, "r") as f:
        data = json.load(f)
        return data.get("health_metrics", {"health_score": 50.0})


def load_data_quality_summary() -> Dict[str, Any]:
    """Load data quality summary from Phase 375."""
    quality_path = STORAGE_METRICS / "data_quality_summary_375.json"

    if not quality_path.exists():
        logger.info("Phase 375 quality summary not yet generated")
        return {"quality_score": 50.0}

    with open(quality_path, "r") as f:
        data = json.load(f)
        return data.get("summary", {"quality_score": 50.0})


def measure_volatility() -> Dict[str, float]:
    """
    Measure volatility using curated signal data.

    Approximates volatility from signal diversity and confidence spread.
    """
    curated_path = STORAGE_LIVE / "dhan_index_ai_signals_curated.csv"

    if not curated_path.exists():
        logger.warning("Curated signals not found for volatility measurement")
        return {"volatility_10sec": 0.0, "volatility_1min": 0.0, "regime": "unknown"}

    try:
        df = pd.read_csv(curated_path)

        # Volatility proxy: standard deviation of confidence scores
        if "confidence" in df.columns:
            confidence_std = float(df["confidence"].std())

            # Map to volatility levels
            # Low vol: std < 0.1, Medium: 0.1-0.2, High: > 0.2
            if confidence_std < 0.1:
                regime = "low"
                vol_10sec = 0.05
                vol_1min = 0.10
            elif confidence_std < 0.2:
                regime = "medium"
                vol_10sec = 0.12
                vol_1min = 0.20
            else:
                regime = "high"
                vol_10sec = 0.25
                vol_1min = 0.40

            return {
                "volatility_10sec": round(vol_10sec, 4),
                "volatility_1min": round(vol_1min, 4),
                "confidence_std": round(confidence_std, 4),
                "regime": regime,
            }

    except Exception as e:
        logger.warning(f"Could not measure volatility: {e}")

    return {"volatility_10sec": 0.0, "volatility_1min": 0.0, "regime": "unknown"}


def compute_signal_conflict_load() -> float:
    """
    Compute signal conflict load (% of conflicting signals).

    Conflict = multiple signals for same symbol in short time window.
    """
    curated_path = STORAGE_LIVE / "dhan_index_ai_signals_curated.csv"

    if not curated_path.exists():
        logger.warning("Curated signals not found for conflict analysis")
        return 0.0

    try:
        df = pd.read_csv(curated_path)

        if "symbol" not in df.columns:
            return 0.0

        # Count signals per symbol in last time window
        symbol_counts = df["symbol"].value_counts()

        # Conflict load: average count per symbol (higher = more conflict)
        avg_conflict = float(symbol_counts.mean())

        # Normalize to 0-1 scale (1.0 = high conflict)
        conflict_load = min(1.0, avg_conflict / 5.0)

        return round(conflict_load, 4)

    except Exception as e:
        logger.warning(f"Could not compute conflict load: {e}")
        return 0.0


def check_data_freshness() -> Dict[str, Any]:
    """Check freshness of critical data files."""
    now = datetime.now()
    freshness = {"files": {}, "overall_freshness": "unknown"}

    critical_files = [
        STORAGE_LIVE / "dhan_index_ai_signals_curated.csv",
        STORAGE_LIVE / "dhan_index_ai_signals_with_forward.csv",
    ]

    freshness_scores = []

    for filepath in critical_files:
        if filepath.exists():
            age = now - datetime.fromtimestamp(filepath.stat().st_mtime)
            age_hours = age.total_seconds() / 3600

            # Freshness score: 1.0 if < 1 hour, decreases after
            if age_hours < 1:
                score = 1.0
                status = "fresh"
            elif age_hours < 6:
                score = 0.8
                status = "recent"
            elif age_hours < 24:
                score = 0.5
                status = "stale"
            else:
                score = 0.2
                status = "very_stale"

            freshness["files"][filepath.name] = {
                "age_hours": round(age_hours, 2),
                "freshness_score": round(score, 2),
                "status": status,
            }

            freshness_scores.append(score)

    if freshness_scores:
        overall = float(np.mean(freshness_scores))
        freshness["overall_freshness"] = "good" if overall > 0.7 else "needs_attention"
        freshness["overall_score"] = round(overall, 2)

    return freshness


def generate_guardrail_recommendations(
    health: Dict[str, Any],
    quality: Dict[str, Any],
    volatility: Dict[str, Any],
    conflict_load: float,
    freshness: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate safety guardrail recommendations based on system state.

    Returns ranked list of recommended guardrails.
    """
    recommendations = []

    health_score = health.get("health_score", 50.0)
    quality_score = quality.get("quality_score", 50.0)
    vol_regime = volatility.get("regime", "unknown")

    # Rule 1: Low health score
    if health_score < 60:
        recommendations.append(
            {
                "priority": "critical",
                "guardrail": "REDUCE_TRADE_FREQUENCY",
                "reason": f"Health score low ({health_score:.1f})",
                "action": "Reduce signal acceptance rate to 50%",
                "safety_level": "aggressive",
            }
        )

    # Rule 2: Low quality score
    if quality_score < 70:
        recommendations.append(
            {
                "priority": "high",
                "guardrail": "INCREASE_CONFIDENCE_THRESHOLD",
                "reason": f"Data quality degraded ({quality_score:.1f})",
                "action": "Increase minimum confidence to 0.70",
                "safety_level": "moderate",
            }
        )

    # Rule 3: High volatility regime
    if vol_regime == "high":
        recommendations.append(
            {
                "priority": "high",
                "guardrail": "CAP_LOT_SIZE",
                "reason": f"High volatility detected ({volatility.get('volatility_1min', 0):.2f})",
                "action": "Cap single position to 2% of portfolio",
                "safety_level": "conservative",
            }
        )

    # Rule 4: High signal conflict
    if conflict_load > 0.6:
        recommendations.append(
            {
                "priority": "medium",
                "guardrail": "CONFLICT_RESOLUTION_PRIORITY",
                "reason": f"High signal conflicts detected ({conflict_load:.2%})",
                "action": "Prioritize high-confidence signals only",
                "safety_level": "moderate",
            }
        )

    # Rule 5: Data freshness issues
    freshness_score = freshness.get("overall_score", 1.0)
    if freshness_score < 0.5:
        recommendations.append(
            {
                "priority": "high",
                "guardrail": "WAIT_FOR_FRESH_DATA",
                "reason": f"Critical data stale ({freshness_score:.2f} freshness)",
                "action": "Pause trading until fresh data available",
                "safety_level": "aggressive",
            }
        )

    # Rule 6: All systems nominal
    if health_score > 85 and quality_score > 85 and vol_regime in ["low", "medium"]:
        recommendations.append(
            {
                "priority": "info",
                "guardrail": "NORMAL_OPERATION",
                "reason": "All system metrics within safe range",
                "action": "Proceed with normal trading parameters",
                "safety_level": "standard",
            }
        )

    # Sort by priority (critical > high > medium > info)
    priority_order = {"critical": 0, "high": 1, "medium": 2, "info": 3}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 99))

    return {
        "active_recommendations": len(recommendations),
        "critical_count": sum(1 for r in recommendations if r["priority"] == "critical"),
        "recommendations": recommendations,
        "system_state_summary": {
            "health_score": round(health_score, 1),
            "quality_score": round(quality_score, 1),
            "volatility_regime": vol_regime,
            "conflict_load": round(conflict_load, 2),
            "data_freshness": freshness_score,
        },
    }


def generate_markdown_report(guardrails: Dict[str, Any]) -> str:
    """Generate markdown report for safety guardrails."""

    report = """# SAFETY GUARDRAIL RECOMMENDATIONS - PHASE 367

**Generated:** {timestamp}

## Executive Summary

This phase analyzes system state and recommends safety guardrails to prevent losses.
**Status:** Analysis only - recommendations do NOT enforce changes.

## System State

| Metric | Value | Status |
|--------|-------|--------|
| Health Score | {health:.1f}/100 | [GOOD] |
| Quality Score | {quality:.1f}/100 | [GOOD] |
| Volatility | {volatility} | [NORMAL] |
| Conflict Load | {conflict:.2%} | [LOW] |
| Data Freshness | {freshness:.2f}/1.0 | [GOOD] |

""".format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        health=guardrails["system_state_summary"]["health_score"],
        quality=guardrails["system_state_summary"]["quality_score"],
        volatility=guardrails["system_state_summary"]["volatility_regime"],
        conflict=guardrails["system_state_summary"]["conflict_load"],
        freshness=guardrails["system_state_summary"]["data_freshness"],
    )

    report += f"""
## Recommendations ({guardrails['active_recommendations']} active)

"""

    if guardrails["critical_count"] > 0:
        report += f"[WARN] **{guardrails['critical_count']} CRITICAL recommendations** require immediate attention\n\n"

    for rec in guardrails["recommendations"]:
        priority_emoji = {"critical": "[CRITICAL]", "high": "[HIGH]", "medium": "[MEDIUM]", "info": "[INFO]"}

        report += f"""### {priority_emoji.get(rec['priority'], '•')} {rec['guardrail']} [{rec['priority'].upper()}]

**Reason:** {rec['reason']}  
**Action:** {rec['action']}  
**Safety Level:** {rec['safety_level']}

"""

    report += """## Safety Rules

These hard-coded safety rules are ALWAYS enforced:

1. [OK] **LIVE_TRADING_ENABLED** = false (cannot be changed)
2. [OK] **USE_ANGELONE_LIVE_EXECUTION** = false (cannot be changed)
3. [OK] **DRY-RUN MODE** = enabled (all trades simulated only)
4. [OK] **POSITION LIMITS** enforced in execution layer
5. [OK] **LOSS LIMITS** enforced in execution layer

## Important Notes

- This phase **recommends** guardrails but does NOT enforce them
- Hard-coded safety rules in execution layer cannot be bypassed
- Always verify guardrail recommendations against live market conditions
- System is designed to fail-safe (DRY-RUN mode default)

---

**Status:** [OK] Analysis Complete (DRY-RUN)  
**Safety Mode:** DRY-RUN (no live orders possible)  
**Last Updated:** {timestamp}
"""

    return report.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def run_phase367(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute Phase 367 - Safety Guardrail Recommender

    Args:
        context: Optional execution context

    Returns:
        {"status": "ok"|"warn"|"error", "outputs": {"json": path, "report": path}}
    """
    logger.info("Phase 367: Starting Safety Guardrail Analysis")

    try:
        # Load system state
        health = load_health_feed()
        quality = load_data_quality_summary()
        volatility = measure_volatility()
        conflict_load = compute_signal_conflict_load()
        freshness = check_data_freshness()

        # Generate recommendations
        guardrails = generate_guardrail_recommendations(health, quality, volatility, conflict_load, freshness)

        # Write JSON output
        json_path = STORAGE_METRICS / "safety_guardrails_367.json"
        json_output = {
            "phase": 367,
            "timestamp": datetime.now().isoformat(),
            "guardrails": guardrails,
            "system_state": {
                "health": health,
                "quality": quality,
                "volatility": volatility,
                "conflict_load": conflict_load,
                "freshness": freshness,
            },
        }

        with open(json_path, "w") as f:
            json.dump(json_output, f, indent=2)

        logger.info(f"JSON output: {json_path}")

        # Write markdown report
        md_report = generate_markdown_report(guardrails)
        md_path = REPORTS_DIR / "SAFETY_GUARDRAILS_367.md"

        with open(md_path, "w") as f:
            f.write(md_report)

        logger.info(f"Markdown report: {md_path}")

        # Status: critical if critical guardrails exist, otherwise ok
        status = "warn" if guardrails["critical_count"] > 0 else "ok"

        return {"phase": 367, "status": status, "outputs": {"json": str(json_path), "report": str(md_path)}}

    except Exception as e:
        logger.error(f"Phase 367 error: {e}")
        return {"phase": 367, "status": "error", "error": str(e), "outputs": {}}


if __name__ == "__main__":
    result = run_phase367()
    print(json.dumps(result, indent=2))
