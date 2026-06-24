"""
System3 Phase 339 - Daily Signal Pipeline Summary Report

Generates comprehensive daily summary of signal pipeline health.
Aggregates findings from Phases 331-338.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)


def load_diagnostic_file(file_path: Path) -> Dict[str, Any]:
    """Load a diagnostic JSON file, return empty dict if not found."""
    if not file_path.exists():
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load {file_path}: {e}")
        return {}


def run_phase339_daily_signal_pipeline_summary(root_path: str = None, **kwargs) -> Dict[str, Any]:
    """
    Phase 339: Daily Signal Pipeline Summary Report

    Returns:
        Dict with phase status and results
    """
    logger.info("=" * 70)
    logger.info("PHASE 339: Daily Signal Pipeline Summary Report")
    logger.info("=" * 70)

    root = Path(root_path) if root_path else PROJECT_ROOT
    diagnostics_dir = root / "storage" / "live" / "diagnostics"

    # Load all diagnostic reports
    integrity_report = load_diagnostic_file(diagnostics_dir / "signal_integrity_report.json")
    volume_summary = load_diagnostic_file(diagnostics_dir / "signal_volume_summary.json")
    consistency_report = load_diagnostic_file(diagnostics_dir / "signal_consistency_report.json")
    drift_snapshot = load_diagnostic_file(diagnostics_dir / "model_drift_daily.csv")  # Will be empty dict
    drift_status = load_diagnostic_file(diagnostics_dir / "model_drift_status.json")
    safety_recommendation = load_diagnostic_file(diagnostics_dir / "next_day_safety_recommendation.json")
    forward_quality = load_diagnostic_file(diagnostics_dir / "forward_return_quality_report.json")
    correlation_report = load_diagnostic_file(diagnostics_dir / "signal_outcome_correlation_report.json")

    # Aggregate warnings and issues
    all_warnings = []
    all_issues = []

    # From integrity (Phase 331)
    if integrity_report:
        all_issues.extend(integrity_report.get("issues", []))
        all_warnings.extend(integrity_report.get("warnings", []))

    # From volume (Phase 332)
    if volume_summary:
        all_warnings.extend(volume_summary.get("warnings", []))

    # From consistency (Phase 333)
    if consistency_report:
        all_warnings.extend(consistency_report.get("warnings", []))

    # From drift (Phase 335)
    if drift_status:
        if drift_status.get("drift_detected"):
            all_warnings.extend(drift_status.get("drift_signals", []))

    # From forward quality (Phase 337)
    if forward_quality:
        all_warnings.extend(forward_quality.get("warnings", []))

    # From correlation (Phase 338)
    if correlation_report:
        all_warnings.extend(correlation_report.get("warnings", []))

    # Build summary
    summary = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "phase": 339,
        "overall_status": "OK",
        "total_issues": len(all_issues),
        "total_warnings": len(all_warnings),
        "phase_results": {
            "331_signal_integrity": {
                "status": integrity_report.get("status", "UNKNOWN"),
                "files_checked": integrity_report.get("files_checked", 0),
                "issues": len(integrity_report.get("issues", [])),
            },
            "332_signal_volume": {
                "status": volume_summary.get("status", "UNKNOWN") if volume_summary else "UNKNOWN",
                "total_rows": volume_summary.get("total_rows", 0) if volume_summary else 0,
            },
            "333_signal_consistency": {
                "status": consistency_report.get("status", "UNKNOWN") if consistency_report else "UNKNOWN",
                "duplicates": consistency_report.get("duplicate_count", 0) if consistency_report else 0,
                "conflicts": consistency_report.get("conflict_count", 0) if consistency_report else 0,
            },
            "334_model_drift_snapshot": {
                "status": "OK",  # Always runs silently
            },
            "335_model_drift_analyzer": {
                "status": drift_status.get("status", "UNKNOWN") if drift_status else "UNKNOWN",
                "drift_detected": drift_status.get("drift_detected", False) if drift_status else False,
            },
            "336_safe_mode_suggestor": {
                "recommendation": (
                    safety_recommendation.get("recommendation", "UNKNOWN") if safety_recommendation else "UNKNOWN"
                ),
            },
            "337_forward_quality": {
                "status": forward_quality.get("status", "UNKNOWN") if forward_quality else "UNKNOWN",
                "warnings": len(forward_quality.get("warnings", [])) if forward_quality else 0,
            },
            "338_correlation": {
                "status": correlation_report.get("status", "UNKNOWN") if correlation_report else "UNKNOWN",
                "n_valid_rows": correlation_report.get("n_valid_rows", 0) if correlation_report else 0,
            },
        },
        "all_warnings": all_warnings,
        "all_issues": all_issues,
    }

    # Determine overall status
    if len(all_issues) > 0:
        summary["overall_status"] = "ERROR"
    elif len(all_warnings) > 0:
        summary["overall_status"] = "WARN"
    else:
        summary["overall_status"] = "OK"

    # Write summary report
    diagnostics_dir.mkdir(parents=True, exist_ok=True)

    summary_file = diagnostics_dir / "daily_signal_pipeline_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Daily summary written to: {summary_file}")

    # Log summary
    logger.info("=" * 70)
    logger.info("DAILY SIGNAL PIPELINE SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Overall Status: {summary['overall_status']}")
    logger.info(f"Total Issues: {len(all_issues)}")
    logger.info(f"Total Warnings: {len(all_warnings)}")
    logger.info("")

    for phase_name, phase_data in summary["phase_results"].items():
        logger.info(f"{phase_name}: {phase_data}")

    if all_issues:
        logger.error("ISSUES:")
        for issue in all_issues[:10]:  # Show first 10
            logger.error(f"  - {issue}")

    if all_warnings:
        logger.warning("WARNINGS:")
        for warning in all_warnings[:10]:  # Show first 10
            logger.warning(f"  - {warning}")

    logger.info("=" * 70)
    logger.info(f"Phase 339 Complete: {summary['overall_status']}")
    logger.info("=" * 70)

    return {
        "phase": 339,
        "status": summary["overall_status"],
        "outputs": summary,
    }


def run_phase_339(**kwargs) -> str:
    """Wrapper for autorun integration - returns status string."""
    result = run_phase339_daily_signal_pipeline_summary(**kwargs)
    return result.get("status", "ERROR")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    result = run_phase339_daily_signal_pipeline_summary()
    print(f"\nPhase 339 Status: {result['status']}")
