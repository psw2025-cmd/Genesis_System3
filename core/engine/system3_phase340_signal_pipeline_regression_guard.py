"""
System3 Phase 340 - Signal Pipeline Regression Guard

Final gate before signal usage - checks for regressions in signal quality.
Compares current metrics against historical baselines.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Regression thresholds
MIN_SIGNAL_COUNT_THRESHOLD = 30  # Minimum acceptable signal count
MAX_DUPLICATE_RATE = 0.05  # Max 5% duplicates
MAX_CONFLICT_RATE = 0.02  # Max 2% conflicts
MIN_COMPLETENESS_RATE = 0.60  # Min 60% forward return completeness


def _read_live_flag(root: Path) -> bool:
    """Return True if any config indicates live trading enabled; default False."""
    candidates = [
        root / "config" / "live_trade_config.json",
        root / "config" / "system3_config.json",
        root / "storage" / "config" / "system3_master_session_config.json",
    ]
    for path in candidates:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                for key in [
                    "LIVE_TRADING_ENABLED",
                    "USE_LIVE_EXECUTION_ENGINE",
                    "USE_ANGELONE_LIVE_EXECUTION",
                    "auto_execute_trades",
                    "AUTO_EXECUTE_TRADES",
                    "live_trading_enabled",
                ]:
                    val = data.get(key)
                    if isinstance(val, bool) and val:
                        return True
        except Exception:
            continue
    return False


def run_phase340_signal_pipeline_regression_guard(root_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Phase 340: Signal Pipeline Regression Guard

    Returns:
        Dict with phase status and results
    """
    logger.info("=" * 70)
    logger.info("PHASE 340: Signal Pipeline Regression Guard")
    logger.info("=" * 70)

    root = Path(root_path) if root_path else PROJECT_ROOT
    diagnostics_dir = root / "storage" / "live" / "diagnostics"

    # Load daily summary
    summary_file = diagnostics_dir / "daily_signal_pipeline_summary.json"

    if not summary_file.exists():
        logger.warning(f"Daily summary not found: {summary_file}")
        return {"phase": 340, "status": "WARN", "outputs": {"error": "Daily summary not found - run Phase 339 first"}}

    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            summary = json.load(f)

        regression_signals = []
        blocking_issues = []
        live_trading_enabled = _read_live_flag(root)

        # Check 1: Signal count
        signal_count = summary.get("phase_results", {}).get("332_signal_volume", {}).get("total_rows", 0)
        low_volume = signal_count < MIN_SIGNAL_COUNT_THRESHOLD
        if low_volume:
            msg = f"Signal count too low: {signal_count} < {MIN_SIGNAL_COUNT_THRESHOLD}"
            if live_trading_enabled:
                blocking_issues.append(msg)
                logger.error(f"❌ BLOCKING: {msg}")
            else:
                regression_signals.append(f"LOW_VOLUME: {msg}")
                logger.warning(f"⚠️  LOW VOLUME (DRY-RUN): {msg}")
        else:
            logger.info(f"✓ Signal count OK: {signal_count}")

        # Check 2: Duplicate rate
        consistency_data = summary.get("phase_results", {}).get("333_signal_consistency", {})
        duplicates = consistency_data.get("duplicates", 0)
        if signal_count > 0:
            duplicate_rate = duplicates / signal_count
            if duplicate_rate > MAX_DUPLICATE_RATE:
                regression_signals.append(f"High duplicate rate: {duplicate_rate:.2%} > {MAX_DUPLICATE_RATE:.2%}")
                logger.warning(f"⚠️  High duplicate rate: {duplicate_rate:.2%}")

        # Check 3: Conflict rate
        conflicts = consistency_data.get("conflicts", 0)
        if signal_count > 0:
            conflict_rate = conflicts / signal_count
            if conflict_rate > MAX_CONFLICT_RATE:
                regression_signals.append(f"High conflict rate: {conflict_rate:.2%} > {MAX_CONFLICT_RATE:.2%}")
                logger.warning(f"⚠️  High conflict rate: {conflict_rate:.2%}")

        # Check 4: Forward return completeness
        forward_quality_file = diagnostics_dir / "forward_return_quality_report.json"
        if forward_quality_file.exists():
            with open(forward_quality_file, "r", encoding="utf-8") as f:
                fwd_data = json.load(f)

            completeness_pct = fwd_data.get("quality_metrics", {}).get("fwd_ret_1_completeness_pct", 0)
            completeness_rate = completeness_pct / 100.0

            if completeness_rate < MIN_COMPLETENESS_RATE:
                regression_signals.append(
                    f"Low forward return completeness: {completeness_rate:.2%} < {MIN_COMPLETENESS_RATE:.2%}"
                )
                logger.warning(f"⚠️  Low forward return completeness: {completeness_rate:.2%}")

        # Check 5: Model drift
        drift_detected = (
            summary.get("phase_results", {}).get("335_model_drift_analyzer", {}).get("drift_detected", False)
        )
        if drift_detected:
            regression_signals.append("Model drift detected by Phase 335")
            logger.warning("⚠️  Model drift detected")

        # Check 6: Critical issues from summary
        total_issues = summary.get("total_issues", 0)
        if total_issues > 0:
            blocking_issues.append(f"{total_issues} critical issues found in daily summary")
            logger.error(f"❌ BLOCKING: {total_issues} critical issues")

        # Build guard report
        guard_report = {
            "timestamp": datetime.now().isoformat(),
            "phase": 340,
            "gate_status": "PASS",
            "blocking_issues": blocking_issues,
            "regression_signals": regression_signals,
            "live_trading_enabled": live_trading_enabled,
            "low_volume": {
                "flag": low_volume,
                "min_required_signals": MIN_SIGNAL_COUNT_THRESHOLD,
                "actual_signals": signal_count,
            },
            "checks": {
                "signal_count": {
                    "value": signal_count,
                    "threshold": MIN_SIGNAL_COUNT_THRESHOLD,
                    "passed": signal_count >= MIN_SIGNAL_COUNT_THRESHOLD,
                },
                "duplicate_rate": {
                    "value": duplicate_rate if signal_count > 0 else 0.0,
                    "threshold": MAX_DUPLICATE_RATE,
                    "passed": (duplicate_rate <= MAX_DUPLICATE_RATE) if signal_count > 0 else True,
                },
                "conflict_rate": {
                    "value": conflict_rate if signal_count > 0 else 0.0,
                    "threshold": MAX_CONFLICT_RATE,
                    "passed": (conflict_rate <= MAX_CONFLICT_RATE) if signal_count > 0 else True,
                },
                "model_drift": {
                    "detected": drift_detected,
                    "passed": not drift_detected,
                },
            },
        }

        # Determine gate status
        if blocking_issues:
            guard_report["gate_status"] = "BLOCKED"
            logger.error("=" * 70)
            logger.error("❌ REGRESSION GUARD: BLOCKED")
            logger.error("=" * 70)
            for issue in blocking_issues:
                logger.error(f"  BLOCKING: {issue}")
        elif regression_signals:
            guard_report["gate_status"] = "WARN"
            logger.warning("=" * 70)
            logger.warning("⚠️  REGRESSION GUARD: WARN")
            logger.warning("=" * 70)
            for signal in regression_signals:
                logger.warning(f"  WARNING: {signal}")
        else:
            guard_report["gate_status"] = "PASS"
            logger.info("=" * 70)
            logger.info("✓ REGRESSION GUARD: PASS")
            logger.info("=" * 70)

        # Write guard report
        diagnostics_dir.mkdir(parents=True, exist_ok=True)

        guard_file = diagnostics_dir / "regression_guard_report.json"
        with open(guard_file, "w", encoding="utf-8") as f:
            json.dump(guard_report, f, indent=2)

        logger.info(f"Regression guard report written to: {guard_file}")

        # Determine phase status
        if guard_report["gate_status"] == "BLOCKED":
            status = "ERROR"
        elif guard_report["gate_status"] == "WARN":
            status = "WARN"
        else:
            status = "OK"

        logger.info("=" * 70)
        logger.info(f"Phase 340 Complete: {status}")
        logger.info(f"Gate Status: {guard_report['gate_status']}")
        logger.info("=" * 70)

        return {
            "phase": 340,
            "status": status,
            "outputs": guard_report,
        }

    except Exception as e:
        logger.error(f"Error in Phase 340: {e}")
        return {"phase": 340, "status": "ERROR", "outputs": {"error": str(e)}}


def run_phase_340(**kwargs) -> str:
    """Wrapper for autorun integration - returns status string."""
    result = run_phase340_signal_pipeline_regression_guard(**kwargs)
    return result.get("status", "ERROR")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    result = run_phase340_signal_pipeline_regression_guard()
    print(f"\nPhase 340 Status: {result['status']}")
