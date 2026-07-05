"""
System3 Phase 203 - Config Consistency Check

Enumerates all JSON config files and validates their structure.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "config"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_config_consistency_report.md"

# Known config types and required keys
CONFIG_REQUIREMENTS = {
    "live_trade_config": ["live_trading_enabled", "dry_run"],
    "ultra_safety": ["AUTO_EXECUTE_TRADES"],
}


def validate_json_file(file_path: Path) -> tuple[bool, dict, str]:
    """Validate a JSON file and return (is_valid, data, error_msg)."""
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return True, data, ""
    except json.JSONDecodeError as e:
        return False, {}, f"JSON parse error: {e}"
    except Exception as e:
        return False, {}, f"Error reading file: {e}"


def run_phase203(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 203: Config Consistency Check.

    Returns:
        dict: {
            "phase": 203,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "checked_files": int,
                "invalid_files": list,
                "repaired_files": list,
            },
            "errors": [],
        }
    """
    errors = []
    checked_files = []
    invalid_files = []
    repaired_files = []

    try:
        # Find all JSON config files
        config_dirs = [
            PROJECT_ROOT / "config",
            PROJECT_ROOT / "core" / "config",
        ]

        json_files = []
        for config_dir in config_dirs:
            if config_dir.exists():
                json_files.extend(config_dir.glob("*.json"))

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Config Consistency Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Config Files Checked\n\n")

            for json_file in json_files:
                checked_files.append(str(json_file))
                f.write(f"### {json_file.name}\n\n")
                f.write(f"**Path**: `{json_file}`\n\n")

                is_valid, data, error_msg = validate_json_file(json_file)

                if not is_valid:
                    invalid_files.append(str(json_file))
                    f.write(f"**Status**: ❌ INVALID\n\n")
                    f.write(f"**Error**: {error_msg}\n\n")

                    # Attempt repair: backup and create minimal default
                    try:
                        backup_path = json_file.with_suffix(".json.bak")
                        json_file.rename(backup_path)
                        f.write(f"**Action**: Backed up to `{backup_path}`\n\n")

                        # Create minimal default based on filename
                        default_data = {}
                        if "live_trade" in json_file.name.lower():
                            default_data = {"live_trading_enabled": False, "dry_run": True}
                        elif "ultra_safety" in json_file.name.lower():
                            default_data = {"AUTO_EXECUTE_TRADES": False}

                        with json_file.open("w", encoding="utf-8") as wf:
                            json.dump(default_data, wf, indent=2)

                        repaired_files.append(str(json_file))
                        f.write(f"**Repaired**: Created minimal default schema\n\n")
                    except Exception as e:
                        errors.append(f"Failed to repair {json_file}: {e}")
                        f.write(f"**Repair Failed**: {e}\n\n")
                else:
                    f.write(f"**Status**: ✅ VALID JSON\n\n")

                    # Check for required keys (if config type is known)
                    missing_keys = []
                    for config_type, required_keys in CONFIG_REQUIREMENTS.items():
                        if config_type in json_file.name.lower():
                            for key in required_keys:
                                if key not in data:
                                    missing_keys.append(key)

                    if missing_keys:
                        f.write(f"**Warning**: Missing required keys: {', '.join(missing_keys)}\n\n")
                    else:
                        f.write(f"**Keys**: All required keys present\n\n")

                f.write("\n")

            f.write("## Summary\n\n")
            f.write(f"- **Files Checked**: {len(checked_files)}\n")
            f.write(f"- **Invalid Files**: {len(invalid_files)}\n")
            f.write(f"- **Repaired Files**: {len(repaired_files)}\n")

            if invalid_files and not repaired_files:
                f.write("\n⚠️ **ACTION REQUIRED**: Some config files are invalid and could not be auto-repaired.\n")
            elif repaired_files:
                f.write("\n✅ **AUTO-REPAIR**: Invalid config files were backed up and replaced with defaults.\n")
            else:
                f.write("\n✅ **STATUS**: All config files are valid.\n")

        status = "OK" if not invalid_files or repaired_files else "WARN"
        details = f"Checked {len(checked_files)} config files"
        if invalid_files:
            details += f", {len(invalid_files)} invalid"
        if repaired_files:
            details += f", {len(repaired_files)} repaired"

        return {
            "phase": 203,
            "status": status,
            "details": details,
            "outputs": {
                "checked_files": len(checked_files),
                "invalid_files": invalid_files,
                "repaired_files": repaired_files,
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 203,
            "status": "ERROR",
            "details": f"Phase 203 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 203 - CONFIG CONSISTENCY CHECK")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase203()

    print(f"Phase 203: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"Checked: {result['outputs']['checked_files']}")
        print(f"Invalid: {len(result['outputs']['invalid_files'])}")
        print(f"Repaired: {len(result['outputs']['repaired_files'])}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
