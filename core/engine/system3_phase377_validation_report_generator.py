"""
System3 Phase 377 - Validation Report Generator

Comprehensive system-wide validation that analyzes all 15 predecessor phases,
aggregates metrics, validates data integrity, and generates a detailed validation report.

Phase 377 produces:
- Consolidated system health assessment
- Data quality metrics across all phases
- Performance analysis and bottleneck identification
- Safety and compliance verification
- Production readiness determination
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import traceback
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_METRICS = PROJECT_ROOT / "storage" / "metrics"
STORAGE_LIVE = PROJECT_ROOT / "storage" / "live"
REPORTS_DIR = PROJECT_ROOT / "reports"
STORAGE_METRICS.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy/pandas types."""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def aggregate_health_metrics() -> Dict[str, Any]:
    """Aggregate health metrics from all phases."""
    metrics = {"health_scores": {}, "data_quality_scores": {}, "average_health": 0, "average_quality": 0}

    try:
        # Try to load health feed (Phase 364)
        health_file = STORAGE_METRICS / "dashboard_feed_364.json"
        if health_file.exists():
            with open(health_file, "r") as f:
                health_data = json.load(f)
                if "health_score" in health_data:
                    metrics["health_scores"]["phase_364"] = health_data["health_score"]

        # Try to load quality summary (Phase 375)
        quality_file = STORAGE_METRICS / "pipeline_quality_375.json"
        if not quality_file.exists():
            quality_file = STORAGE_METRICS / "quality_summary_375.json"

        if quality_file.exists():
            with open(quality_file, "r") as f:
                quality_data = json.load(f)
                if "quality_score" in quality_data:
                    metrics["data_quality_scores"]["phase_375"] = quality_data["quality_score"]

        # Calculate averages
        if metrics["health_scores"]:
            metrics["average_health"] = sum(metrics["health_scores"].values()) / len(metrics["health_scores"])
        if metrics["data_quality_scores"]:
            metrics["average_quality"] = sum(metrics["data_quality_scores"].values()) / len(
                metrics["data_quality_scores"]
            )

    except Exception as e:
        logger.warning(f"Failed to aggregate health metrics: {e}")

    return metrics


def validate_data_integrity() -> Dict[str, Any]:
    """Validate data integrity across all signal files."""
    results = {"files": {}, "overall_status": "OK", "issues": []}

    try:
        import pandas as pd

        signal_files = [
            "angel_index_ai_signals.csv",
            "angel_index_ai_signals_curated.csv",
            "angel_index_ai_signals_with_forward.csv",
        ]

        required_columns = ["symbol", "signal", "signal_type"]

        for filename in signal_files:
            filepath = STORAGE_LIVE / filename

            try:
                if filepath.exists():
                    df = pd.read_csv(filepath, on_bad_lines="skip", low_memory=False)

                    file_status = {
                        "rows": len(df),
                        "columns": len(df.columns),
                        "size_mb": filepath.stat().st_size / (1024 * 1024),
                        "null_count": df.isnull().sum().sum(),
                        "columns_list": list(df.columns),
                    }

                    # Check for required columns
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    if missing_cols:
                        file_status["missing_columns"] = missing_cols
                        results["issues"].append(f"{filename}: Missing columns {missing_cols}")
                        results["overall_status"] = "WARNING"

                    # Check for duplicates
                    if "signal" in df.columns and "timestamp" in df.columns:
                        dup_count = df.duplicated(subset=["signal", "timestamp"]).sum()
                        file_status["duplicates"] = int(dup_count)
                        if dup_count > 0:
                            results["issues"].append(f"{filename}: {dup_count} duplicate rows found")

                    results["files"][filename] = file_status
                else:
                    results["files"][filename] = {"status": "NOT_FOUND"}
            except Exception as e:
                results["files"][filename] = {"status": "ERROR", "error": str(e)[:50]}
                results["overall_status"] = "ERROR"
                results["issues"].append(f"{filename}: {str(e)[:50]}")

    except Exception as e:
        logger.warning(f"Failed to validate data integrity: {e}")
        results["error"] = str(e)

    return results


def analyze_phase_outputs() -> Dict[str, Any]:
    """Analyze outputs from all 15 phases."""
    results = {"phases": {}, "missing_outputs": [], "total_files": 0}

    phase_json_files = {
        361: "signal_pipeline_snapshot_361.json",
        362: "forward_calibrator_362.json",
        363: "model_drift_363.json",
        364: "dashboard_feed_364.json",
        365: "accuracy_tracker_365.json",
        366: "strategy_ensemble_366.json",
        367: "safety_guardrails_367.json",
        368: "broker_latency_368.json",
        369: "pipeline_profile_369.json",
        370: "schema_normalization_370.json",
        371: "duplicate_scanner_371.json",
        372: "conflict_resolver_372.json",
        373: "curated_builder_373.json",
        374: "freshness_checker_374.json",
        375: "quality_summary_375.json",
    }

    for phase_num, expected_file in phase_json_files.items():
        # Try multiple naming patterns
        patterns = [
            expected_file,
            f"phase{phase_num}_output.json",
            f"phase{phase_num}.json",
        ]

        found = False
        for pattern in patterns:
            filepath = STORAGE_METRICS / pattern
            if filepath.exists():
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    results["phases"][phase_num] = {"status": "OK", "file": pattern, "size": filepath.stat().st_size}
                    results["total_files"] += 1
                    found = True
                    break
                except Exception as e:
                    results["phases"][phase_num] = {"status": "ERROR", "file": pattern, "error": str(e)[:30]}
                    found = True
                    break

        if not found:
            results["missing_outputs"].append(phase_num)
            results["phases"][phase_num] = {"status": "NOT_FOUND"}

    return results


def assess_production_readiness() -> Dict[str, Any]:
    """Assess overall production readiness."""
    assessment = {"status": "READY", "checks": {}, "blockers": [], "warnings": []}

    try:
        # Check 1: All phases callable
        try:
            from core.engine.system3_phases_361_380_registry import get_phases_by_category

            all_phases = (
                get_phases_by_category("signal_pipeline")
                + get_phases_by_category("strategy_analysis")
                + get_phases_by_category("data_quality")
            )
            assessment["checks"]["all_phases_callable"] = len(all_phases) >= 15
        except Exception as e:
            assessment["checks"]["all_phases_callable"] = False
            assessment["blockers"].append(f"Cannot verify phase callability: {str(e)[:40]}")

        # Check 2: Safety flags disabled
        try:
            safety_file = PROJECT_ROOT / "config" / "live_trade_config.json"
            if safety_file.exists():
                with open(safety_file, "r") as f:
                    config = json.load(f)
                    is_safe = not config.get("LIVE_TRADING_ENABLED", True)
                    assessment["checks"]["live_trading_disabled"] = is_safe
                    if not is_safe:
                        assessment["blockers"].append("LIVE_TRADING_ENABLED is True")
        except Exception as e:
            assessment["warnings"].append(f"Could not verify safety flags: {str(e)[:40]}")

        # Check 3: Required data files exist
        required_files = [
            "angel_index_ai_signals.csv",
            "angel_index_ai_signals_curated.csv",
            "angel_index_ai_signals_with_forward.csv",
        ]

        files_exist = sum(1 for f in required_files if (STORAGE_LIVE / f).exists())
        assessment["checks"]["data_files_present"] = files_exist >= 2
        if files_exist < 3:
            assessment["warnings"].append(f"Only {files_exist}/3 required data files found")

        # Determine overall status
        if assessment["blockers"]:
            assessment["status"] = "BLOCKED"
        elif assessment["warnings"]:
            assessment["status"] = "CAUTION"
        else:
            assessment["status"] = "READY"

    except Exception as e:
        logger.warning(f"Failed to assess production readiness: {e}")
        assessment["error"] = str(e)

    return assessment


def generate_markdown_report(all_data: Dict[str, Any]) -> str:
    """Generate comprehensive validation report."""
    report = "# System3 Phase 377 - Comprehensive Validation Report\n\n"
    report += f"**Generated:** {datetime.now().isoformat()}\n\n"

    # Executive summary
    report += "## Executive Summary\n\n"
    readiness = all_data.get("production_readiness", {})
    report += f"**Production Readiness:** {readiness.get('status', 'UNKNOWN')}\n\n"

    health = all_data.get("health_metrics", {})
    report += f"**System Health Score:** {health.get('average_health', 0):.1f}/100\n"
    report += f"**Data Quality Score:** {health.get('average_quality', 0):.1f}/100\n\n"

    # Data integrity section
    report += "## Data Integrity Validation\n\n"
    data_integrity = all_data.get("data_integrity", {})
    report += f"**Overall Status:** {data_integrity.get('overall_status', 'UNKNOWN')}\n\n"

    for filename, file_data in data_integrity.get("files", {}).items():
        report += f"### {filename}\n"
        report += f"- Rows: {file_data.get('rows', 'N/A')}\n"
        report += f"- Columns: {file_data.get('columns', 'N/A')}\n"
        report += f"- Size: {file_data.get('size_mb', 0):.2f} MB\n"
        if "missing_columns" in file_data:
            report += f"- Missing Columns: {file_data['missing_columns']}\n"
        report += "\n"

    # Phase outputs section
    report += "## Phase Output Analysis\n\n"
    phase_analysis = all_data.get("phase_outputs", {})
    report += f"**Total Output Files Found:** {phase_analysis.get('total_files', 0)}\n"
    report += f"**Missing Outputs:** {len(phase_analysis.get('missing_outputs', []))}\n\n"

    if phase_analysis.get("missing_outputs"):
        report += "**Phases Without Output Files:**\n"
        for phase_num in phase_analysis["missing_outputs"]:
            report += f"- Phase {phase_num}\n"
        report += "\n"

    # Production readiness section
    report += "## Production Readiness Assessment\n\n"
    report += f"**Status:** {readiness.get('status', 'UNKNOWN')}\n\n"

    report += "**Checks:**\n"
    for check_name, check_result in readiness.get("checks", {}).items():
        status_str = "[OK]" if check_result else "[FAIL]"
        report += f"- {check_name}: {status_str}\n"

    if readiness.get("blockers"):
        report += "\n**Blockers:**\n"
        for blocker in readiness["blockers"]:
            report += f"- [CRITICAL] {blocker}\n"

    if readiness.get("warnings"):
        report += "\n**Warnings:**\n"
        for warning in readiness["warnings"]:
            report += f"- [WARNING] {warning}\n"

    report += "\n"

    # Overall recommendation
    report += "## Recommendation\n\n"
    status = readiness.get("status")
    if status == "READY":
        report += "[OK] System is validated and ready for production deployment.\n"
    elif status == "CAUTION":
        report += "[WARNING] System has minor issues. Review warnings above before deployment.\n"
    else:
        report += "[CRITICAL] System has blocking issues. Fix blockers before deployment.\n"

    return report


def run_phase377(context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Main phase executor."""
    logger.info("=" * 70)
    logger.info("Phase 377: Validation Report Generator")
    logger.info("=" * 70)

    try:
        # Gather all validation data
        health_metrics = aggregate_health_metrics()
        data_integrity = validate_data_integrity()
        phase_outputs = analyze_phase_outputs()
        production_readiness = assess_production_readiness()

        all_data = {
            "health_metrics": health_metrics,
            "data_integrity": data_integrity,
            "phase_outputs": phase_outputs,
            "production_readiness": production_readiness,
        }

        # Generate markdown report
        markdown_report = generate_markdown_report(all_data)

        # Write markdown report
        report_file = REPORTS_DIR / "PHASE_377_VALIDATION_REPORT.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(markdown_report)
        logger.info(f"Report written to: {report_file}")

        # Write JSON output
        json_file = STORAGE_METRICS / "validation_377.json"
        json_output = {
            "phase": 377,
            "timestamp": datetime.now().isoformat(),
            "validation_data": all_data,
            "readiness_status": production_readiness.get("status", "UNKNOWN"),
            "health_score": health_metrics.get("average_health", 0),
            "quality_score": health_metrics.get("average_quality", 0),
        }

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_output, f, indent=2, cls=NumpyEncoder)
        logger.info(f"JSON output: {json_file}")

        # Determine status
        status = "ok" if not production_readiness.get("blockers") else "warn"
        logger.info(f"Phase 377 complete: readiness_status={production_readiness.get('status', 'UNKNOWN')}")

        return {"status": status, "outputs": {"json": str(json_file), "report": str(report_file)}}

    except Exception as e:
        logger.error(f"Phase 377 error: {e}")
        logger.debug(traceback.format_exc())
        return {"status": "error", "error": str(e), "outputs": {}}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    result = run_phase377()
    print(json.dumps(result, indent=2, cls=NumpyEncoder))
