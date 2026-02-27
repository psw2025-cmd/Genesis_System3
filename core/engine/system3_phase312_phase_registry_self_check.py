"""
System3 Phase 312 - Phase Registry Self-Check

Validates phase registry vs actual code implementations and logging.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set
import logging
import ast
import importlib.util

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Output directories
HEALTH_DIR = PROJECT_ROOT / "storage" / "system_health"
HEALTH_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = PROJECT_ROOT / "logs" / "integrity"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Phase registry location
REGISTRY_FILE = PROJECT_ROOT / "storage" / "meta" / "system3_phase_registry.json"

# Phase implementation directories
PHASE_DIRS = [
    PROJECT_ROOT / "core" / "engine",
    PROJECT_ROOT / "engine" / "phases",
]


def load_registry() -> Dict[int, Dict[str, Any]]:
    """Load phase registry from JSON."""
    if not REGISTRY_FILE.exists():
        logger.warning(f"Registry file not found: {REGISTRY_FILE}")
        return {}

    try:
        with open(REGISTRY_FILE, "r") as f:
            data = json.load(f)

        # Convert to dict keyed by phase number
        if isinstance(data, list):
            return {p["phase"]: p for p in data if "phase" in p}
        elif isinstance(data, dict) and "phases" in data:
            return {p["phase"]: p for p in data["phases"] if "phase" in p}
        else:
            return data
    except Exception as e:
        logger.error(f"Failed to load registry: {e}")
        return {}


def find_phase_implementations() -> Dict[int, Path]:
    """Find all phase implementation files."""
    implementations = {}

    for phase_dir in PHASE_DIRS:
        if not phase_dir.exists():
            continue

        # Find all system3_phaseNNN_*.py files
        for py_file in phase_dir.glob("system3_phase*.py"):
            try:
                # Extract phase number from filename
                name_parts = py_file.stem.split("_")
                if len(name_parts) >= 2 and name_parts[0] == "system3":
                    phase_str = name_parts[1].replace("phase", "")
                    if phase_str.isdigit():
                        phase_num = int(phase_str)
                        implementations[phase_num] = py_file
            except Exception as e:
                logger.warning(f"Failed to parse {py_file}: {e}")

    return implementations


def check_phase_callable(phase_file: Path, phase_num: int) -> bool:
    """Check if phase file has a run_phaseNNN definition without executing the module."""
    try:
        source = phase_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_name = f"run_phase{phase_num}"
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if (
                    node.name == func_name
                    or node.name.startswith(f"{func_name}_")
                    or node.name.startswith(f"{func_name}")
                ):
                    return True
        return False
    except Exception as e:
        logger.warning(f"Failed to check callable in {phase_file}: {e}")
        return False


def run_phase312(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 312: Phase Registry Self-Check

    Returns:
        dict: {
            "phase": 312,
            "status": "OK" | "WARN" | "ERROR",
            "details": "description of execution",
            "outputs": {"report_file": path, "issues_found": N},
            "errors": []
        }
    """
    errors = []
    outputs = {}

    try:
        today = datetime.now().strftime("%Y%m%d")
        report_file = HEALTH_DIR / "phase_registry_check.json"
        log_file = LOG_DIR / f"phase_registry_check_{today}.log"

        # Set up file logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        logger.info("Phase 312: Starting phase registry self-check")

        # Load registry
        registry = load_registry()
        logger.info(f"Registry contains {len(registry)} phases")

        # Find implementations
        implementations = find_phase_implementations()
        logger.info(f"Found {len(implementations)} implementation files")

        # Build check results
        phase_results = []
        issues = []

        # Check all phases 1-330
        for phase_num in range(1, 331):
            in_registry = phase_num in registry
            has_implementation = phase_num in implementations

            result = {
                "phase_number": phase_num,
                "name_in_registry": registry[phase_num].get("name", "") if in_registry else "",
                "in_registry": in_registry,
                "implementation_found": has_implementation,
                "implementation_path": str(implementations[phase_num]) if has_implementation else "",
                "callable_verified": False,
            }

            # Verify callable if implementation exists
            if has_implementation:
                result["callable_verified"] = check_phase_callable(implementations[phase_num], phase_num)

            # Identify issues
            if in_registry and not has_implementation:
                issue = f"Phase {phase_num}: In registry but no implementation found"
                issues.append(issue)
                logger.warning(issue)
            elif has_implementation and not in_registry:
                issue = f"Phase {phase_num}: Implementation exists but not in registry"
                issues.append(issue)
                logger.warning(issue)
            elif has_implementation and not result["callable_verified"]:
                # Informational only; some historical phases are utilities without a run_phase entry.
                logger.info(f"Phase {phase_num}: Implementation present; callable not required")

            # Only include phases that exist in registry or have implementations
            if in_registry or has_implementation:
                phase_results.append(result)

        # Check for duplicates in registry
        phase_numbers = [p["phase"] for p in registry.values() if "phase" in p]
        phase_names = [p.get("name", "") for p in registry.values() if p.get("name")]

        if len(phase_numbers) != len(set(phase_numbers)):
            issue = "Duplicate phase numbers found in registry"
            issues.append(issue)
            logger.error(issue)

        if len(phase_names) != len(set(phase_names)):
            issue = "Duplicate phase names found in registry"
            issues.append(issue)
            logger.warning(issue)

        # Create report
        report = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "registry_file": str(REGISTRY_FILE),
            "registry_exists": REGISTRY_FILE.exists(),
            "total_in_registry": len(registry),
            "total_implementations": len(implementations),
            "issues_found": len(issues),
            "issues": issues,
            "phases": phase_results,
        }

        # Write report
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Registry check complete: {len(issues)} issues found")
        logger.info(f"Report saved to: {report_file}")

        outputs = {
            "report_file": str(report_file),
            "issues_found": len(issues),
            "total_in_registry": len(registry),
            "total_implementations": len(implementations),
            "log_file": str(log_file),
        }

        # Remove handler
        logger.removeHandler(file_handler)
        file_handler.close()

        status = "OK" if len(issues) == 0 else "WARN"

        return {
            "phase": 312,
            "status": status,
            "details": f"Phase registry check complete: {len(issues)} issues found",
            "outputs": outputs,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Phase 312 error: {e}", exc_info=True)
        return {
            "phase": 312,
            "status": "ERROR",
            "details": f"Phase 312 failed: {str(e)}",
            "outputs": outputs,
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase312()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
    if result["outputs"]:
        print(f"Outputs: {json.dumps(result['outputs'], indent=2)}")
