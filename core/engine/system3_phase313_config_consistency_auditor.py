"""
System3 Phase 313 - Config Consistency Auditor

Audits all critical configuration files for syntax, consistency, and conflicts.
"""

import sys
import json
from pathlib import Path

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
from datetime import datetime
from typing import Dict, Any, List
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Output directories
HEALTH_DIR = PROJECT_ROOT / "storage" / "system_health"
HEALTH_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = PROJECT_ROOT / "logs" / "integrity"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Config files to audit
CONFIG_FILES = [
    "config/system3_global_config.yml",
    "config/system3_broker_config.yml",
    "config/system3_risk_config.yml",
]

# Critical keys that must be present
REQUIRED_KEYS = {
    "system3_global_config.yml": ["LIVE_TRADING_ENABLED", "USE_LIVE_EXECUTION_ENGINE"],
    "system3_broker_config.yml": [],
    "system3_risk_config.yml": [],
}

# Safety-critical flags (must be False in DRY-RUN)
SAFETY_FLAGS = [
    "LIVE_TRADING_ENABLED",
    "USE_LIVE_EXECUTION_ENGINE",
    "auto_execute_trades",
]


def load_yaml_file(file_path: Path) -> tuple[bool, Any, str]:
    """
    Load YAML file and return (success, data, error).

    Returns:
        tuple: (syntax_ok, data, error_message)
    """
    if not YAML_AVAILABLE:
        return False, None, "YAML module not installed (install pyyaml)"

    if not file_path.exists():
        return False, None, f"File not found: {file_path}"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return True, data, ""
    except yaml.YAMLError as e:
        return False, None, f"YAML syntax error: {str(e)}"
    except Exception as e:
        return False, None, f"Failed to load: {str(e)}"


def check_required_keys(data: Any, required: List[str]) -> List[str]:
    """Check for missing required keys."""
    if not isinstance(data, dict):
        return required

    missing = []
    for key in required:
        if key not in data:
            missing.append(key)
    return missing


def extract_safety_values(data: Any, prefix: str = "") -> Dict[str, Any]:
    """Recursively extract safety-critical flag values."""
    values = {}

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if key in SAFETY_FLAGS:
                values[full_key] = value

            if isinstance(value, dict):
                nested = extract_safety_values(value, full_key)
                values.update(nested)

    return values


def run_phase313(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 313: Config Consistency Auditor

    Returns:
        dict: {
            "phase": 313,
            "status": "OK" | "WARN" | "ERROR",
            "details": "description of execution",
            "outputs": {"report_file": path, "conflicts_found": N},
            "errors": []
        }
    """
    errors = []
    outputs = {}

    try:
        today = datetime.now().strftime("%Y%m%d")
        report_json = HEALTH_DIR / "config_consistency_report.json"
        report_md = PROJECT_ROOT / "SYSTEM3_CONFIG_CONSISTENCY_REPORT.md"
        log_file = LOG_DIR / f"config_consistency_check_{today}.log"

        # Set up file logging
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        logger.info("Phase 313: Starting config consistency audit")

        file_results = []
        all_safety_values = {}
        conflicts = []

        # Audit each config file
        for config_path in CONFIG_FILES:
            full_path = PROJECT_ROOT / config_path
            logger.info(f"Auditing: {config_path}")

            syntax_ok, data, error = load_yaml_file(full_path)

            result = {
                "file": config_path,
                "exists": full_path.exists(),
                "syntax_ok": syntax_ok,
                "error": error if not syntax_ok else "",
                "missing_required_keys": [],
                "safety_values": {},
            }

            if syntax_ok and data:
                # Check required keys
                required = REQUIRED_KEYS.get(Path(config_path).name, [])
                missing = check_required_keys(data, required)
                result["missing_required_keys"] = missing

                if missing:
                    logger.warning(f"  Missing keys: {missing}")

                # Extract safety values
                safety_vals = extract_safety_values(data)
                result["safety_values"] = safety_vals
                all_safety_values.update({f"{config_path}:{k}": v for k, v in safety_vals.items()})

                logger.info(f"  Safety values: {safety_vals}")

            file_results.append(result)

        # Check for conflicts in safety values
        for key, value in all_safety_values.items():
            if value not in [False, "False", "false", 0, "0", None]:
                conflict = f"UNSAFE VALUE: {key} = {value} (should be False for DRY-RUN)"
                conflicts.append(conflict)
                logger.error(conflict)

        # Create JSON report
        report = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "files_audited": len(CONFIG_FILES),
            "syntax_errors": sum(1 for f in file_results if not f["syntax_ok"]),
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
            "effective_safety_values": all_safety_values,
            "files": file_results,
        }

        with open(report_json, "w") as f:
            json.dump(report, f, indent=2)

        # Create markdown summary
        md_lines = [
            "# System3 Config Consistency Report",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- Files audited: {len(CONFIG_FILES)}",
            f"- Syntax errors: {report['syntax_errors']}",
            f"- Conflicts found: {len(conflicts)}",
            "",
            "## Safety-Critical Flags",
            "",
        ]

        if all_safety_values:
            for key, value in sorted(all_safety_values.items()):
                status = "✅" if value in [False, "False", "false", 0, "0", None] else "⚠️"
                md_lines.append(f"{status} `{key}` = `{value}`")
        else:
            md_lines.append("*No safety flags found in configs*")

        if conflicts:
            md_lines.extend(["", "## Conflicts Detected", ""])
            for conflict in conflicts:
                md_lines.append(f"- ⚠️ {conflict}")

        md_lines.extend(["", "## File Details", ""])

        for f_result in file_results:
            md_lines.append(f"### {f_result['file']}")
            md_lines.append(f"- Exists: {'✅' if f_result['exists'] else '❌'}")
            md_lines.append(f"- Syntax: {'✅' if f_result['syntax_ok'] else '❌'}")
            if f_result["error"]:
                md_lines.append(f"- Error: {f_result['error']}")
            if f_result["missing_required_keys"]:
                md_lines.append(f"- Missing keys: {', '.join(f_result['missing_required_keys'])}")
            md_lines.append("")

        with open(report_md, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        logger.info(f"Config audit complete: {len(conflicts)} conflicts found")
        logger.info(f"Reports saved to: {report_json}, {report_md}")

        outputs = {
            "report_json": str(report_json),
            "report_md": str(report_md),
            "conflicts_found": len(conflicts),
            "syntax_errors": report["syntax_errors"],
            "log_file": str(log_file),
        }

        # Remove handler
        logger.removeHandler(file_handler)
        file_handler.close()

        status = "ERROR" if report["syntax_errors"] > 0 else ("WARN" if len(conflicts) > 0 else "OK")

        return {
            "phase": 313,
            "status": status,
            "details": f"Config audit complete: {len(conflicts)} conflicts, {report['syntax_errors']} syntax errors",
            "outputs": outputs,
            "errors": errors,
        }

    except Exception as e:
        logger.error(f"Phase 313 error: {e}", exc_info=True)
        return {
            "phase": 313,
            "status": "ERROR",
            "details": f"Phase 313 failed: {str(e)}",
            "outputs": outputs,
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase313()
    print(f"Phase {result['phase']}: {result['status']} - {result['details']}")
    if result["outputs"]:
        print(f"Outputs: {json.dumps(result['outputs'], indent=2)}")
