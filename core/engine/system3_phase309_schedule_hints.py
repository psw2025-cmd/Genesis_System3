"""
System3 Phase 309 - Schedule Hints Generator

Analyzes phase execution patterns and suggests optimal scheduling for phases 301-310.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)

LOG_DIR = PROJECT_ROOT / "logs" / "performance"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_schedule_hint_report_309.md"
HINTS_JSON = STORAGE_META / "system3_schedule_hints_309.json"

# Phase dependencies (which phases need which others)
PHASE_DEPENDENCIES = {
    301: [],  # No dependencies
    302: [301],  # Needs Phase 301
    303: [],  # No dependencies (uses forward returns from 221)
    304: [301, 302, 303],  # Needs Phases 301-303
    305: [302, 303],  # Needs Phases 302-303
    306: [],  # No dependencies
    307: [],  # No dependencies
    308: [301, 302, 305, 307],  # Needs Phases 301, 302, 305, 307
    309: [],  # No dependencies
    310: list(range(301, 310)),  # Needs all phases 301-309
}


def run_phase309(**kwargs) -> Dict[str, Any]:
    """Run Phase 309: Schedule Hints Generator."""
    errors = []

    try:
        # Analyze dependencies and suggest execution order
        execution_order = []
        executed = set()

        # Topological sort based on dependencies
        phases = list(range(301, 311))

        while len(executed) < len(phases):
            progress = False
            for phase in phases:
                if phase in executed:
                    continue

                deps = PHASE_DEPENDENCIES.get(phase, [])
                if all(dep in executed for dep in deps):
                    execution_order.append(phase)
                    executed.add(phase)
                    progress = True

            if not progress:
                # Circular dependency or missing phase - add remaining phases
                for phase in phases:
                    if phase not in executed:
                        execution_order.append(phase)
                        executed.add(phase)
                break

        # Categorize phases
        post_market = [301, 302, 303, 304, 305, 308, 309, 310]  # Research/analysis phases
        intraday = [306, 307]  # Monitoring phases

        # Generate recommendations
        recommendations = {
            "execution_order": execution_order,
            "post_market_phases": post_market,
            "intraday_phases": intraday,
            "priority_levels": {
                "HIGH": [301, 302, 303, 308],  # Core analysis
                "MEDIUM": [304, 305, 306, 307],  # Optimization and monitoring
                "LOW": [309, 310],  # Meta-analysis
            },
        }

        # Generate report
        report_lines = [
            "# System3 Schedule Hints Report\n",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
            "## Recommended Execution Order\n\n",
        ]

        for i, phase in enumerate(execution_order, 1):
            deps = PHASE_DEPENDENCIES.get(phase, [])
            deps_str = ", ".join([f"Phase {d}" for d in deps]) if deps else "None"
            report_lines.append(f"{i}. **Phase {phase}** (Dependencies: {deps_str})\n")

        report_lines.append("\n## Scheduling Recommendations\n\n")
        report_lines.append("### Post-Market Phases (Run after market close)\n\n")
        for phase in post_market:
            report_lines.append(f"- Phase {phase}\n")

        report_lines.append("\n### Intraday Phases (Can run during market hours)\n\n")
        for phase in intraday:
            report_lines.append(f"- Phase {phase}\n")

        report_lines.append("\n## Priority Levels\n\n")
        for priority, phases in recommendations["priority_levels"].items():
            report_lines.append(f"### {priority} Priority\n\n")
            for phase in phases:
                report_lines.append(f"- Phase {phase}\n")
            report_lines.append("\n")

        report_lines.append("## Notes\n\n")
        report_lines.append("- Phases should be executed in dependency order\n")
        report_lines.append("- Post-market phases can be batched together\n")
        report_lines.append("- Intraday phases should run periodically (e.g., every 30 minutes)\n")
        report_lines.append("- High priority phases should complete before medium/low priority\n")

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.writelines(report_lines)

        # Save JSON
        json_data = {
            "computation_timestamp": datetime.now().isoformat(),
            "recommendations": recommendations,
            "dependencies": PHASE_DEPENDENCIES,
        }

        with HINTS_JSON.open("w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)

        return {
            "phase": 309,
            "status": "OK",
            "details": f"Generated schedule hints for {len(phases)} phases",
            "outputs": {
                "phases_analyzed": len(phases),
                "execution_order_length": len(execution_order),
                "report_file": str(REPORT_PATH),
                "json_file": str(HINTS_JSON),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(str(e))
        return {
            "phase": 309,
            "status": "ERROR",
            "details": f"Exception: {e}",
            "outputs": {"report_file": str(REPORT_PATH), "json_file": str(HINTS_JSON)},
            "errors": errors,
        }
