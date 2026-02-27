"""
System3 Phase 363 - Model Drift Checker

Detects if model behavior has drifted vs recent history by comparing
current signal quality metrics against historical baselines.
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
REPORTS_DIR = PROJECT_ROOT / "reports"

STORAGE_METRICS.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


def load_signal_history(days_back: int = 7) -> List[Dict[str, Any]]:
    """Load historical signal snapshots from Phase 361 outputs."""
    history = []

    # Try to load past snapshots
    for i in range(days_back):
        date = datetime.now() - timedelta(days=i)
        snapshot_file = STORAGE_METRICS / f"signal_pipeline_snapshot_361_{date.strftime('%Y%m%d')}.json"

        if snapshot_file.exists():
            try:
                with open(snapshot_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["snapshot_date"] = date.strftime("%Y-%m-%d")
                    history.append(data)
            except Exception as e:
                logger.warning(f"Could not load {snapshot_file.name}: {e}")

    # Also try the generic file (today's run)
    generic_file = STORAGE_METRICS / "signal_pipeline_snapshot_361.json"
    if generic_file.exists():
        try:
            with open(generic_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["snapshot_date"] = datetime.now().strftime("%Y-%m-%d")
                history.append(data)
        except Exception as e:
            logger.warning(f"Could not load {generic_file.name}: {e}")

    return history


def compute_drift_metrics(current_metrics: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare current metrics against historical baseline."""
    drift_analysis = {"drift_detected": False, "drift_signals": [], "metrics_comparison": {}}

    if len(historical) < 2:
        drift_analysis["drift_signals"].append("Insufficient history for drift detection (need 2+ snapshots)")
        return drift_analysis

    # Extract key metrics from history
    historical_totals = [h.get("total_signals", 0) for h in historical]
    historical_files = [h.get("total_files", 0) for h in historical]

    current_total = current_metrics.get("total_signals", 0)
    current_files = current_metrics.get("total_files", 0)

    # Compute baseline (mean of historical)
    baseline_signals = np.mean(historical_totals) if historical_totals else 0
    baseline_files = np.mean(historical_files) if historical_files else 0

    # Detect significant changes (>30% deviation)
    signal_change_pct = ((current_total - baseline_signals) / baseline_signals * 100) if baseline_signals > 0 else 0
    files_change_pct = ((current_files - baseline_files) / baseline_files * 100) if baseline_files > 0 else 0

    drift_analysis["metrics_comparison"] = {
        "signal_count": {
            "current": current_total,
            "baseline": round(baseline_signals, 1),
            "change_pct": round(signal_change_pct, 2),
        },
        "file_count": {
            "current": current_files,
            "baseline": round(baseline_files, 1),
            "change_pct": round(files_change_pct, 2),
        },
    }

    # Flag drift if change exceeds threshold
    DRIFT_THRESHOLD = 30  # 30% change triggers drift warning

    if abs(signal_change_pct) > DRIFT_THRESHOLD:
        drift_analysis["drift_detected"] = True
        drift_analysis["drift_signals"].append(
            f"Signal count changed by {signal_change_pct:.1f}% (threshold: {DRIFT_THRESHOLD}%)"
        )

    # Check signal distribution if available
    current_dist = current_metrics.get("signal_distribution", {})
    if current_dist and historical:
        # Compare signal type proportions
        for hist in historical[-3:]:  # Last 3 snapshots
            hist_dist = hist.get("signal_distribution", {})

            for signal_type, current_count in current_dist.items():
                hist_count = hist_dist.get(signal_type, 0)
                total_current = sum(current_dist.values())
                total_hist = sum(hist_dist.values())

                if total_current > 0 and total_hist > 0:
                    current_prop = current_count / total_current
                    hist_prop = hist_count / total_hist
                    prop_change = abs(current_prop - hist_prop) * 100

                    if prop_change > 20:  # 20% change in signal type proportion
                        drift_analysis["drift_signals"].append(
                            f"Signal type '{signal_type}' proportion changed by {prop_change:.1f}%"
                        )

    return drift_analysis


def analyze_forward_return_drift() -> Dict[str, Any]:
    """Check if forward return calibration has drifted."""
    calibration_file = STORAGE_METRICS / "forward_calibration_362.json"

    if not calibration_file.exists():
        return {"status": "no_calibration_data", "drift_detected": False}

    try:
        with open(calibration_file, "r", encoding="utf-8") as f:
            calib_data = json.load(f)

        drift_info = {"status": "ok", "drift_detected": False, "calibration_summary": {}}

        # Extract global score if available
        global_score = calib_data.get("global_score", {})
        if global_score:
            avg_win_rate = global_score.get("avg_win_rate", 0)
            drift_info["calibration_summary"]["avg_win_rate"] = round(avg_win_rate, 2)

            # Flag if win rate is suspiciously low or high
            if avg_win_rate < 40:
                drift_info["drift_detected"] = True
                drift_info["drift_signals"] = [f"Low win rate detected: {avg_win_rate:.1f}%"]
            elif avg_win_rate > 80:
                drift_info["drift_detected"] = True
                drift_info["drift_signals"] = [
                    f"Unrealistically high win rate: {avg_win_rate:.1f}% (check data quality)"
                ]

        return drift_info

    except Exception as e:
        logger.error(f"Error analyzing forward return drift: {e}")
        return {"status": "error", "error": str(e), "drift_detected": False}


def run_phase363(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute Phase 363: Model Drift Checker.

    Returns:
        dict: {
            "status": "ok" | "warn" | "error",
            "drift_detected": bool,
            "drift_signals": list of drift warnings,
            "outputs": {"json": path, "report": path}
        }
    """
    logger.info("=== Phase 363: Model Drift Checker ===")

    result = {
        "phase": 363,
        "name": "Model Drift Checker",
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "drift_detected": False,
        "drift_signals": [],
        "outputs": {},
    }

    try:
        # Load current snapshot from Phase 361
        current_snapshot_file = STORAGE_METRICS / "signal_pipeline_snapshot_361.json"

        if not current_snapshot_file.exists():
            result["status"] = "warn"
            result["message"] = "No current snapshot found from Phase 361. Run Phase 361 first."
            logger.warning(result["message"])
            return result

        with open(current_snapshot_file, "r", encoding="utf-8") as f:
            current_snapshot = json.load(f)

        # Load historical snapshots
        historical = load_signal_history(days_back=7)
        logger.info(f"Loaded {len(historical)} historical snapshots")

        # Compute drift metrics
        signal_drift = compute_drift_metrics(current_snapshot, historical)

        # Check forward return calibration drift
        fwd_return_drift = analyze_forward_return_drift()

        # Combine drift signals
        all_drift_signals = signal_drift.get("drift_signals", [])
        if fwd_return_drift.get("drift_detected"):
            all_drift_signals.extend(fwd_return_drift.get("drift_signals", []))

        drift_detected = signal_drift.get("drift_detected", False) or fwd_return_drift.get("drift_detected", False)

        result["drift_detected"] = drift_detected
        result["drift_signals"] = all_drift_signals
        result["signal_drift_analysis"] = signal_drift
        result["forward_return_drift_analysis"] = fwd_return_drift
        result["historical_snapshot_count"] = len(historical)

        if drift_detected:
            result["status"] = "warn"
            logger.warning(f"Model drift detected: {len(all_drift_signals)} signals")

        # Write JSON output
        json_output = STORAGE_METRICS / "model_drift_363.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        result["outputs"]["json"] = str(json_output)
        logger.info(f"JSON written to: {json_output}")

        # Write Markdown report
        md_output = REPORTS_DIR / "MODEL_DRIFT_STATUS_363.md"
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# Model Drift Status - Phase 363\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            if drift_detected:
                f.write("## ⚠️ DRIFT DETECTED\n\n")
                f.write(f"**Status:** {result['status'].upper()}\n\n")
                f.write("**Drift Signals:**\n\n")
                for signal in all_drift_signals:
                    f.write(f"- ⚠️ {signal}\n")
                f.write("\n")
            else:
                f.write("## ✅ NO DRIFT DETECTED\n\n")
                f.write("Model behavior is consistent with recent history.\n\n")

            f.write("---\n\n")
            f.write("## Signal Drift Analysis\n\n")

            comparison = signal_drift.get("metrics_comparison", {})
            if comparison:
                f.write("| Metric | Current | Baseline | Change |\n")
                f.write("|--------|---------|----------|--------|\n")

                for metric_name, metric_data in comparison.items():
                    f.write(
                        f"| {metric_name} | {metric_data['current']} | "
                        f"{metric_data['baseline']} | {metric_data['change_pct']:+.1f}% |\n"
                    )
                f.write("\n")

            f.write("---\n\n")
            f.write("## Forward Return Calibration\n\n")

            if fwd_return_drift.get("status") == "ok":
                calib_summary = fwd_return_drift.get("calibration_summary", {})
                if calib_summary:
                    f.write(f"**Average Win Rate:** {calib_summary.get('avg_win_rate', 'N/A')}%\n\n")
                else:
                    f.write("*No calibration summary available*\n\n")
            else:
                f.write(f"*Status:* {fwd_return_drift.get('status', 'unknown')}\n\n")

            f.write("---\n\n")
            f.write(f"**Historical Snapshots Analyzed:** {len(historical)}\n\n")
            f.write(
                f"**Recommendation:** {'Review model performance and consider retraining' if drift_detected else 'Continue monitoring'}\n"
            )

        result["outputs"]["report"] = str(md_output)
        logger.info(f"Report written to: {md_output}")

        logger.info(f"Phase 363 complete: drift_detected={drift_detected}")
        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Phase 363 error: {e}", exc_info=True)
        return result


def main():
    """Standalone execution."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    result = run_phase363()

    print("\n" + "=" * 60)
    print("PHASE 363 - MODEL DRIFT CHECKER")
    print("=" * 60)
    print(f"Status: {result['status'].upper()}")
    print(f"Drift Detected: {result['drift_detected']}")

    if result.get("drift_signals"):
        print(f"\nDrift Signals ({len(result['drift_signals'])}):")
        for signal in result["drift_signals"]:
            print(f"  - {signal}")

    if result.get("outputs"):
        print("\nOutputs:")
        for key, path in result["outputs"].items():
            print(f"  {key}: {path}")

    print("=" * 60)


if __name__ == "__main__":
    main()
