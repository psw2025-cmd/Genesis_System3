"""
System3 Phase 364 - Health Dashboard Feed Generator

Aggregates key health metrics from phases 361-363 and system logs
into a single dashboard-ready JSON feed for monitoring tools.
"""

import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"

STORAGE_METRICS.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


def load_heartbeat_status() -> Dict[str, Any]:
    """Load system heartbeat if available."""
    heartbeat_file = PROJECT_ROOT / "system3_daily_heartbeat.json"

    if not heartbeat_file.exists():
        return {"status": "not_found", "message": "No heartbeat file found"}

    try:
        with open(heartbeat_file, "r", encoding="utf-8") as f:
            heartbeat = json.load(f)

        # Check freshness
        last_update = heartbeat.get("last_update", "")
        if last_update:
            last_dt = datetime.fromisoformat(last_update)
            age_minutes = (datetime.now() - last_dt).total_seconds() / 60
            heartbeat["age_minutes"] = round(age_minutes, 1)
            heartbeat["is_stale"] = age_minutes > 60  # Stale if >1 hour old

        return {"status": "ok", "data": heartbeat}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def scan_recent_logs() -> Dict[str, Any]:
    """Scan recent autorun logs for errors/warnings."""
    log_summary = {"errors": 0, "warnings": 0, "recent_messages": []}

    if not LOGS_DIR.exists():
        return log_summary

    try:
        # Find today's autorun log
        today_log = LOGS_DIR / f"system3_autorun_master_{datetime.now().strftime('%Y%m%d')}.log"

        if today_log.exists():
            with open(today_log, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

                # Count errors and warnings
                for line in lines[-200:]:  # Last 200 lines
                    if "[ERROR]" in line:
                        log_summary["errors"] += 1
                        if len(log_summary["recent_messages"]) < 5:
                            log_summary["recent_messages"].append(line.strip())
                    elif "[WARNING]" in line:
                        log_summary["warnings"] += 1
                        if len(log_summary["recent_messages"]) < 5:
                            log_summary["recent_messages"].append(line.strip())

        return log_summary

    except Exception as e:
        logger.error(f"Error scanning logs: {e}")
        return log_summary


def check_data_freshness() -> Dict[str, Any]:
    """Check if signal data files are fresh."""
    freshness_check = {"fresh_files": [], "stale_files": [], "missing_files": []}

    signal_files = [
        "angel_index_ai_signals.csv",
        "angel_index_ai_signals_curated.csv",
        "angel_index_ai_signals_with_forward.csv",
    ]

    STALE_THRESHOLD_HOURS = 24

    for filename in signal_files:
        file_path = STORAGE_LIVE / filename

        if not file_path.exists():
            freshness_check["missing_files"].append(filename)
            continue

        # Check modification time
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        age_hours = (datetime.now() - mod_time).total_seconds() / 3600

        file_info = {
            "filename": filename,
            "age_hours": round(age_hours, 1),
            "last_modified": mod_time.strftime("%Y-%m-%d %H:%M"),
        }

        if age_hours > STALE_THRESHOLD_HOURS:
            freshness_check["stale_files"].append(file_info)
        else:
            freshness_check["fresh_files"].append(file_info)

    return freshness_check


def aggregate_phase_metrics() -> Dict[str, Any]:
    """Load and aggregate metrics from phases 361-363."""
    phase_metrics = {}

    # Phase 361: Signal Pipeline Snapshot
    phase361_file = STORAGE_METRICS / "signal_pipeline_snapshot_361.json"
    if phase361_file.exists():
        try:
            with open(phase361_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                phase_metrics["phase_361"] = {
                    "status": data.get("status", "unknown"),
                    "total_signals": data.get("total_signals", 0),
                    "total_files": data.get("total_files", 0),
                    "signal_distribution": data.get("signal_distribution", {}),
                }
        except Exception as e:
            phase_metrics["phase_361"] = {"status": "error", "error": str(e)}
    else:
        phase_metrics["phase_361"] = {"status": "not_run"}

    # Phase 362: Forward Calibrator
    phase362_file = STORAGE_METRICS / "forward_calibration_362.json"
    if phase362_file.exists():
        try:
            with open(phase362_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                phase_metrics["phase_362"] = {
                    "status": data.get("status", "unknown"),
                    "global_score": data.get("global_score", {}),
                }
        except Exception as e:
            phase_metrics["phase_362"] = {"status": "error", "error": str(e)}
    else:
        phase_metrics["phase_362"] = {"status": "not_run"}

    # Phase 363: Model Drift Checker
    phase363_file = STORAGE_METRICS / "model_drift_363.json"
    if phase363_file.exists():
        try:
            with open(phase363_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                phase_metrics["phase_363"] = {
                    "status": data.get("status", "unknown"),
                    "drift_detected": data.get("drift_detected", False),
                    "drift_signal_count": len(data.get("drift_signals", [])),
                }
        except Exception as e:
            phase_metrics["phase_363"] = {"status": "error", "error": str(e)}
    else:
        phase_metrics["phase_363"] = {"status": "not_run"}

    return phase_metrics


def run_phase364(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute Phase 364: Health Dashboard Feed Generator.

    Returns:
        dict: {
            "status": "ok" | "warn" | "error",
            "health_score": float (0-100),
            "outputs": {"json": path, "report": path}
        }
    """
    logger.info("=== Phase 364: Health Dashboard Feed Generator ===")

    result = {
        "phase": 364,
        "name": "Health Dashboard Feed",
        "timestamp": datetime.now().isoformat(),
        "status": "ok",
        "outputs": {},
    }

    try:
        # Gather all health data
        heartbeat = load_heartbeat_status()
        logs = scan_recent_logs()
        freshness = check_data_freshness()
        phase_metrics = aggregate_phase_metrics()

        # Compute overall health score (0-100)
        health_score = 100.0
        health_issues = []

        # Deduct points for issues
        if heartbeat.get("status") != "ok":
            health_score -= 20
            health_issues.append("Heartbeat not available")
        elif heartbeat.get("data", {}).get("is_stale"):
            health_score -= 10
            health_issues.append("Heartbeat is stale")

        if logs["errors"] > 0:
            health_score -= min(logs["errors"] * 5, 25)
            health_issues.append(f"{logs['errors']} errors in recent logs")

        if logs["warnings"] > 5:
            health_score -= min((logs["warnings"] - 5) * 2, 15)
            health_issues.append(f"{logs['warnings']} warnings in recent logs")

        if len(freshness["stale_files"]) > 0:
            health_score -= len(freshness["stale_files"]) * 10
            health_issues.append(f"{len(freshness['stale_files'])} stale data files")

        if len(freshness["missing_files"]) > 0:
            health_score -= len(freshness["missing_files"]) * 15
            health_issues.append(f"{len(freshness['missing_files'])} missing data files")

        if phase_metrics.get("phase_363", {}).get("drift_detected"):
            health_score -= 15
            health_issues.append("Model drift detected")

        health_score = max(0, health_score)

        # Build dashboard feed
        dashboard_feed = {
            "phase": 364,
            "timestamp": result["timestamp"],
            "health_score": round(health_score, 1),
            "health_status": "healthy" if health_score >= 80 else ("degraded" if health_score >= 50 else "critical"),
            "health_issues": health_issues,
            "heartbeat": heartbeat,
            "log_summary": logs,
            "data_freshness": freshness,
            "phase_metrics": phase_metrics,
        }

        result["health_score"] = dashboard_feed["health_score"]
        result["health_status"] = dashboard_feed["health_status"]
        result["health_issues"] = health_issues

        if health_score < 80:
            result["status"] = "warn"

        # Write JSON output
        json_output = STORAGE_METRICS / "dashboard_feed_364.json"
        with open(json_output, "w", encoding="utf-8") as f:
            json.dump(dashboard_feed, f, indent=2)

        result["outputs"]["json"] = str(json_output)
        logger.info(f"Dashboard feed written to: {json_output}")

        # Write Markdown report
        md_output = REPORTS_DIR / "DASHBOARD_HEALTH_FEED_364.md"
        with open(md_output, "w", encoding="utf-8") as f:
            f.write("# System Health Dashboard - Phase 364\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # Health score badge
            if health_score >= 80:
                badge = "🟢 HEALTHY"
            elif health_score >= 50:
                badge = "🟡 DEGRADED"
            else:
                badge = "🔴 CRITICAL"

            f.write(f"## {badge}\n\n")
            f.write(f"**Health Score:** {health_score:.1f}/100\n\n")

            if health_issues:
                f.write("### Issues Detected\n\n")
                for issue in health_issues:
                    f.write(f"- ⚠️ {issue}\n")
                f.write("\n")
            else:
                f.write("✅ No issues detected\n\n")

            f.write("---\n\n")

            # Heartbeat status
            f.write("## Heartbeat Status\n\n")
            if heartbeat.get("status") == "ok":
                hb_data = heartbeat["data"]
                f.write(f"**Status:** {'🟢 Active' if not hb_data.get('is_stale') else '🟡 Stale'}\n")
                f.write(f"**Last Update:** {hb_data.get('last_update', 'N/A')}\n")
                f.write(f"**Age:** {hb_data.get('age_minutes', 'N/A')} minutes\n\n")
            else:
                f.write(f"**Status:** ⚠️ {heartbeat.get('status')}\n\n")

            # Log summary
            f.write("## Recent Log Activity\n\n")
            f.write(f"**Errors:** {logs['errors']}\n")
            f.write(f"**Warnings:** {logs['warnings']}\n\n")

            if logs["recent_messages"]:
                f.write("**Recent Messages:**\n\n")
                f.write("```\n")
                for msg in logs["recent_messages"][:5]:
                    f.write(msg + "\n")
                f.write("```\n\n")

            # Data freshness
            f.write("## Data Freshness\n\n")
            f.write(f"**Fresh Files:** {len(freshness['fresh_files'])}\n")
            f.write(f"**Stale Files:** {len(freshness['stale_files'])}\n")
            f.write(f"**Missing Files:** {len(freshness['missing_files'])}\n\n")

            if freshness["stale_files"]:
                f.write("**Stale Files:**\n\n")
                for file_info in freshness["stale_files"]:
                    f.write(f"- {file_info['filename']} (age: {file_info['age_hours']}h)\n")
                f.write("\n")

            # Phase metrics summary
            f.write("## Phase Metrics Summary\n\n")
            f.write("| Phase | Status | Key Metrics |\n")
            f.write("|-------|--------|-------------|\n")

            for phase_name, metrics in phase_metrics.items():
                status_emoji = (
                    "✅" if metrics.get("status") == "ok" else ("⚠️" if metrics.get("status") == "warn" else "❌")
                )

                if phase_name == "phase_361":
                    key_metric = f"{metrics.get('total_signals', 0)} signals"
                elif phase_name == "phase_362":
                    global_score = metrics.get("global_score", {})
                    key_metric = f"Win rate: {global_score.get('avg_win_rate', 'N/A')}"
                elif phase_name == "phase_363":
                    drift = "Drift detected" if metrics.get("drift_detected") else "No drift"
                    key_metric = drift
                else:
                    key_metric = "N/A"

                f.write(f"| {phase_name} | {status_emoji} {metrics.get('status', 'unknown')} | {key_metric} |\n")

            f.write("\n---\n\n")
            f.write(f"**Next Refresh:** Check dashboard in 30 minutes\n")

        result["outputs"]["report"] = str(md_output)
        logger.info(f"Report written to: {md_output}")

        logger.info(f"Phase 364 complete: health_score={health_score:.1f}")
        return result

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Phase 364 error: {e}", exc_info=True)
        return result


def main():
    """Standalone execution."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    result = run_phase364()

    print("\n" + "=" * 60)
    print("PHASE 364 - HEALTH DASHBOARD FEED")
    print("=" * 60)
    print(f"Status: {result['status'].upper()}")
    print(f"Health Score: {result.get('health_score', 'N/A')}/100")
    print(f"Health Status: {result.get('health_status', 'N/A').upper()}")

    if result.get("health_issues"):
        print(f"\nHealth Issues ({len(result['health_issues'])}):")
        for issue in result["health_issues"]:
            print(f"  - {issue}")

    if result.get("outputs"):
        print("\nOutputs:")
        for key, path in result["outputs"].items():
            print(f"  {key}: {path}")

    print("=" * 60)


if __name__ == "__main__":
    main()
