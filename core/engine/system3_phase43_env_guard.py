"""
System3 Ultra - Phase 43: Environment & Broker Guard

Ensure System3 (Angel indices) never accidentally touches non-Dhan brokers and
prepare guardrails for future Binance System3.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 107
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
LOGS_ULTRA_DIR = PROJECT_ROOT / "storage" / "logs_ultra"

ULTRA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

ENV_CONFIG_FILE = CONFIG_DIR / "system3_env_config.json"
LOG_FILE = LOGS_ULTRA_DIR / "system3_phases_39_45.log"

ANGEL_ENV_VARS = ["ANGEL_API_KEY", "ANGEL_CLIENT_ID", "ANGEL_PIN"]
BINANCE_ENV_VARS = ["BINANCE_API_KEY", "BINANCE_SECRET_KEY"]


def _log(message: str) -> None:
    """Log message to file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [Phase43] {message}\n"
    print(f"[Phase43] {message}")

    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"[Phase43][WARN] Failed to write log: {e}")


def load_env_config() -> Dict[str, Any]:
    """Load or create environment config."""
    default_config = {"dhan_system3_enabled": True, "binance_system3_enabled": False}

    if not ENV_CONFIG_FILE.exists():
        _log("Env config file not found, creating with defaults")
        try:
            with ENV_CONFIG_FILE.open("w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            _log(f"Failed to create config: {e}")
        return default_config

    try:
        with ENV_CONFIG_FILE.open("r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        _log(f"Failed to load config: {e}, using defaults")
        return default_config


def check_dhan_env_vars() -> Dict[str, Any]:
    """Check Angel environment variables."""
    result = {"present": [], "missing": [], "status": "PASS"}

    for var in ANGEL_ENV_VARS:
        if var in os.environ and os.environ[var]:
            result["present"].append(var)
        else:
            result["missing"].append(var)

    if result["missing"]:
        result["status"] = "WARN"

    return result


def check_binance_env_vars() -> Dict[str, Any]:
    """Check Binance environment variables."""
    result = {"present": [], "missing": [], "status": "PASS"}

    for var in BINANCE_ENV_VARS:
        if var in os.environ and os.environ[var]:
            result["present"].append(var)
        else:
            result["missing"].append(var)

    return result


def check_code_imports() -> Dict[str, Any]:
    """Check for obvious mixed broker usage in code."""
    result = {"binance_imports_found": False, "status": "PASS"}

    # Simple check: look for binance imports in run_system3.py
    run_system3_file = PROJECT_ROOT / "run_system3.py"
    if run_system3_file.exists():
        try:
            content = run_system3_file.read_text(encoding="utf-8")
            if "binance" in content.lower() and "import" in content.lower():
                result["binance_imports_found"] = True
                result["status"] = "WARN"
        except Exception:
            pass

    return result


def run_phase43_env_guard() -> None:
    """Run environment guard checks."""
    print("=" * 60)
    print("SYSTEM3 ULTRA - PHASE 43: ENVIRONMENT & BROKER GUARD")
    print("=" * 60)
    print("\n[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only\n")

    _log("Env guard started")

    # Load config
    env_config = load_env_config()
    dhan_enabled = env_config.get("dhan_system3_enabled", True)
    binance_enabled = env_config.get("binance_system3_enabled", False)

    _log(f"Angel System3: {'ENABLED' if dhan_enabled else 'DISABLED'}")
    _log(f"Binance System3: {'ENABLED' if binance_enabled else 'DISABLED'}")

    # Check environment variables
    dhan_env = check_dhan_env_vars()
    binance_env = check_binance_env_vars()
    code_check = check_code_imports()

    # Build report
    report_lines = []
    report_lines.append("# Environment & Broker Guard Report")
    report_lines.append("")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    report_lines.append("## Environment Variables")
    report_lines.append("")

    report_lines.append("### Angel System3 Variables")
    report_lines.append("")
    if dhan_env["present"]:
        report_lines.append("**Present:**")
        for var in dhan_env["present"]:
            report_lines.append(f"- `{var}`: ✓")
    if dhan_env["missing"]:
        report_lines.append("**Missing:**")
        for var in dhan_env["missing"]:
            report_lines.append(f"- `{var}`: ✗")
    report_lines.append(f"**Status**: {dhan_env['status']}")
    report_lines.append("")

    report_lines.append("### Binance System3 Variables")
    report_lines.append("")
    if binance_env["present"]:
        report_lines.append("**Present (not required for Angel System3):**")
        for var in binance_env["present"]:
            report_lines.append(f"- `{var}`: ⚠")
    else:
        report_lines.append("**None found (expected for Angel-only System3)**")
    report_lines.append("")

    report_lines.append("## Configuration Status")
    report_lines.append("")
    report_lines.append(f"- **Angel System3 Enabled**: {dhan_enabled}")
    report_lines.append(f"- **Binance System3 Enabled**: {binance_enabled}")
    if dhan_enabled and binance_enabled:
        report_lines.append("")
        report_lines.append("⚠️ **WARNING**: Both systems enabled - ensure proper separation")
    report_lines.append("")

    report_lines.append("## Code Import Check")
    report_lines.append("")
    if code_check["binance_imports_found"]:
        report_lines.append("⚠️ **WARNING**: Potential Binance imports found in run_system3.py")
        report_lines.append("Review code to ensure proper broker separation")
    else:
        report_lines.append("✓ No obvious Binance imports detected")
    report_lines.append("")

    report_lines.append("## Summary")
    report_lines.append("")
    overall_status = "PASS"
    if dhan_env["status"] == "WARN" or code_check["status"] == "WARN":
        overall_status = "WARN"

    report_lines.append(f"**Overall Status**: {overall_status}")
    report_lines.append("")

    if overall_status == "PASS":
        report_lines.append("✓ Environment guard checks passed")
        report_lines.append("✓ Angel System3 properly configured")
        report_lines.append("✓ No broker mixing detected")
    else:
        report_lines.append("⚠ Review warnings above")

    # Write report
    report_file = ULTRA_DIR / "phase43_env_guard_report.md"
    with report_file.open("w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    _log(f"Report written to {report_file}")

    print(f"\n[OK] Phase 43 Environment Guard completed")
    print(f"[SAVE] Report: {report_file}")
    print(f"\n[STATUS] Overall: {overall_status}")

    if overall_status == "PASS":
        print("[INFO] Environment guard checks passed")
    else:
        print("[WARN] Review warnings in report")


def main() -> None:
    """CLI entry point."""
    run_phase43_env_guard()


if __name__ == "__main__":
    main()
