"""
System3 Phase 310 - Ultra Health Monitor

Overall health check for phases 301-310 and their integration with the system.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_ultra_health_310.md"
HEALTH_JSON = STORAGE_META / "system3_ultra_health_310.json"

# Expected output files for each phase
PHASE_OUTPUTS = {
    301: [
        "logs/research/system3_daily_live_vs_forward_report.md",
        "storage/meta/system3_daily_performance_301.json",
    ],
    302: [
        "logs/research/system3_regime_performance_302.md",
        "storage/meta/system3_regime_performance_302.json",
    ],
    303: [
        "logs/research/system3_edge_decay_303.md",
        "storage/meta/system3_edge_decay_profile_303.json",
    ],
    304: [
        "logs/research/system3_threshold_tuner_304.md",
        "storage/meta/system3_threshold_proposals_304.json",
    ],
    305: [
        "logs/ml/system3_confidence_tiering_305.md",
        "storage/live/angel_index_ai_signals_confidence_tagged_305.csv",
    ],
    306: [
        "logs/performance/system3_staleness_guard_306.md",
        "storage/meta/system3_staleness_flags_306.csv",
    ],
    307: [
        "logs/validation/system3_live_vs_test_consistency_307.md",
        "storage/meta/system3_live_vs_test_consistency_307.json",
    ],
    308: [
        "logs/research/system3_daily_dashboard_308.md",
        "storage/meta/system3_daily_dashboard_308.json",
    ],
    309: [
        "logs/performance/system3_schedule_hint_report_309.md",
        "storage/meta/system3_schedule_hints_309.json",
    ],
    310: [
        "logs/system3_ultra_health_310.md",
        "storage/meta/system3_ultra_health_310.json",
    ],
}


def check_file_freshness(path: Path, max_age_hours: int = 24) -> tuple[bool, float]:
    """Check if file exists and is fresh. Returns (exists_and_fresh, age_hours)."""
    if not path.exists():
        return False, 0.0

    try:
        mtime = path.stat().st_mtime
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        return age_hours <= max_age_hours, age_hours
    except Exception:
        return False, 0.0


def check_phase_implementation(phase_num: int) -> bool:
    """Check if phase module exists."""
    phase_file = PROJECT_ROOT / "core" / "engine" / f"system3_phase{phase_num}_*.py"
    import glob

    return len(list(glob.glob(str(phase_file)))) > 0


def run_phase310(**kwargs) -> Dict[str, Any]:
    """Run Phase 310: Ultra Health Monitor."""
    errors = []

    try:
        health_data = {
            "computation_timestamp": datetime.now().isoformat(),
            "phases": {},
            "overall_health_score": 0.0,
            "issues": [],
        }

        total_score = 0.0
        max_score = 0.0

        for phase_num in range(301, 311):
            phase_health = {
                "phase": phase_num,
                "implemented": check_phase_implementation(phase_num),
                "outputs_exist": [],
                "outputs_fresh": [],
                "issues": [],
            }

            # Check outputs
            expected_outputs = PHASE_OUTPUTS.get(phase_num, [])
            for output_path_str in expected_outputs:
                output_path = PROJECT_ROOT / output_path_str
                exists, age_hours = check_file_freshness(output_path)
                phase_health["outputs_exist"].append(exists)
                phase_health["outputs_fresh"].append(age_hours <= 24)

                if not exists:
                    phase_health["issues"].append(f"Missing output: {output_path_str}")
                elif age_hours > 24:
                    phase_health["issues"].append(f"Stale output: {output_path_str} (age: {age_hours:.1f} hours)")

            # Compute phase score
            phase_score = 0.0
            if phase_health["implemented"]:
                phase_score += 50.0
            max_score += 50.0

            if expected_outputs:
                output_score = (sum(phase_health["outputs_exist"]) / len(expected_outputs)) * 30.0
                freshness_score = (sum(phase_health["outputs_fresh"]) / len(expected_outputs)) * 20.0
                phase_score += output_score + freshness_score
                max_score += 50.0

            phase_health["health_score"] = phase_score
            total_score += phase_score

            health_data["phases"][phase_num] = phase_health

            if phase_health["issues"]:
                health_data["issues"].extend([f"Phase {phase_num}: {issue}" for issue in phase_health["issues"]])

        # Overall health score
        overall_score = (total_score / max_score * 100) if max_score > 0 else 0.0
        health_data["overall_health_score"] = overall_score

        # Generate report
        report_lines = [
            "# System3 Ultra Health Monitor Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Overall Health Score**: {overall_score:.1f}/100\n\n",
        ]

        if overall_score >= 90:
            report_lines.append("✅ **EXCELLENT** - System is healthy\n\n")
        elif overall_score >= 70:
            report_lines.append("⚠️ **GOOD** - Minor issues detected\n\n")
        elif overall_score >= 50:
            report_lines.append("⚠️ **FAIR** - Some issues need attention\n\n")
        else:
            report_lines.append("❌ **POOR** - Critical issues detected\n\n")

        report_lines.append("## Phase-by-Phase Health\n\n")
        report_lines.append("| Phase | Implemented | Outputs Exist | Outputs Fresh | Score | Issues |\n")
        report_lines.append("|-------|-------------|---------------|---------------|-------|--------|\n")

        for phase_num in range(301, 311):
            phase = health_data["phases"][phase_num]
            impl_icon = "✅" if phase["implemented"] else "❌"
            outputs_exist = sum(phase["outputs_exist"])
            outputs_total = len(phase["outputs_exist"])
            outputs_fresh = sum(phase["outputs_fresh"])
            score = phase["health_score"]
            issues_count = len(phase["issues"])

            report_lines.append(
                f"| {phase_num} | {impl_icon} | {outputs_exist}/{outputs_total} | {outputs_fresh}/{outputs_total} | "
                f"{score:.1f} | {issues_count} |\n"
            )

        if health_data["issues"]:
            report_lines.append("\n## Issues Detected\n\n")
            for issue in health_data["issues"][:20]:  # Limit to 20
                report_lines.append(f"- {issue}\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        # Save JSON
        with HEALTH_JSON.open("w", encoding="utf-8") as f:
            json.dump(health_data, f, indent=2)

        status = "OK"
        if overall_score < 70:
            status = "WARN"
        if overall_score < 50:
            status = "ERROR"

        return {
            "phase": 310,
            "status": status,
            "details": f"Overall health score: {overall_score:.1f}/100",
            "outputs": {
                "overall_health_score": overall_score,
                "phases_checked": 10,
                "issues_detected": len(health_data["issues"]),
                "report_file": str(REPORT_PATH),
                "json_file": str(HEALTH_JSON),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(str(e))
        return {
            "phase": 310,
            "status": "ERROR",
            "details": f"Exception: {e}",
            "outputs": {"report_file": str(REPORT_PATH), "json_file": str(HEALTH_JSON)},
            "errors": errors,
        }
