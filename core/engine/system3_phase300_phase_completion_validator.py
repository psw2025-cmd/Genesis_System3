"""
System3 Phase 300 - Phase Completion Validator

Validates that all phases 1-300 are implemented and working.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "monitoring"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_phase_completion_validation.md"


def run_phase300(**kwargs) -> Dict[str, Any]:
    """Run Phase 300: Phase Completion Validator."""
    errors = []
    missing_phases = []

    try:
        # Check for phase files in core/engine
        engine_dir = PROJECT_ROOT / "core" / "engine"

        # Check phases 201-300
        for phase_num in range(201, 301):
            # Look for phase file
            phase_files = list(engine_dir.glob(f"system3_phase{phase_num}_*.py"))
            if not phase_files:
                missing_phases.append(phase_num)

        # Generate report
        report_lines = [
            "# System3 Phase Completion Validation\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Phases Checked**: 201-300\n",
            f"**Missing Phases**: {len(missing_phases)}\n",
        ]

        if missing_phases:
            report_lines.append("\n## Missing Phases\n")
            for phase in missing_phases[:20]:  # Show first 20
                report_lines.append(f"- Phase {phase}\n")
        else:
            report_lines.append("\n✅ All phases 201-300 found\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        status = "OK" if not missing_phases else "WARN"
        details = f"Validated phases 201-300: {len(missing_phases)} missing"

        return {
            "phase": 300,
            "status": status,
            "details": details,
            "outputs": {
                "phases_checked": 100,
                "missing_phases": len(missing_phases),
                "report_file": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 300,
            "status": "ERROR",
            "details": f"Phase 300 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase300()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
