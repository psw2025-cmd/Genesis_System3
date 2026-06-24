"""
Dhan Index Options - Environment Consistency Checker

Checks Python packages, directory structure, config flags.
SAFE MODE ONLY - Reporting only, no auto-fix.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent


def check_python_packages() -> Dict[str, Any]:
    """
    Check required Python packages.

    Returns:
        Dict with package check results
    """
    required_packages = [
        "pandas",
        "numpy",
        "scikit-learn",
        "joblib",
    ]

    package_checks = {}
    missing = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            package_checks[package] = True
        except ImportError:
            package_checks[package] = False
            missing.append(package)

    return {
        "status": "PASS" if not missing else "FAIL",
        "checked": package_checks,
        "missing": missing,
    }


def check_directory_structure() -> Dict[str, Any]:
    """
    Check directory structure consistency.

    Returns:
        Dict with directory check results
    """
    required_dirs = [
        "core/engine",
        "core/models/dhan",
        "storage/live",
        "storage/training",
        "storage/config",
        "storage/reports",
        "storage/learning",
    ]

    dir_checks = {}
    missing = []

    for dir_path in required_dirs:
        full_path = PROJECT_ROOT / dir_path
        exists = full_path.exists()
        dir_checks[dir_path] = exists
        if not exists:
            missing.append(dir_path)

    return {
        "status": "PASS" if not missing else "WARN",
        "checked": dir_checks,
        "missing": missing,
    }


def check_config_flags() -> Dict[str, Any]:
    """
    Check configuration flags (read-only).

    Returns:
        Dict with config flag check results
    """
    try:
        from core.engine.dhan_automation_config import AUTOMATION_CONFIG
        from core.engine.dhan_ultramode_prep import load_ultramode_config

        ultramode = load_ultramode_config()

        flags = {
            "auto_execute_trades": AUTOMATION_CONFIG.auto_execute_trades,
            "auto_simulate_pnl": AUTOMATION_CONFIG.auto_simulate_pnl,
            "ultramode_read_only": ultramode.read_only_mode,
            "ultramode_auto_trade": ultramode.auto_trade_execution,
        }

        all_safe = (
            not flags["auto_execute_trades"]
            and not flags["auto_simulate_pnl"]
            and flags["ultramode_read_only"]
            and not flags["ultramode_auto_trade"]
        )

        return {
            "status": "PASS" if all_safe else "FAIL",
            "flags": flags,
            "all_safe": all_safe,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
        }


def run_consistency_check() -> Dict[str, Any]:
    """
    Run complete consistency check.

    Returns:
        Dict with all check results
    """
    print("=== ANGEL ONE INDEX OPTIONS - ENVIRONMENT CONSISTENCY CHECKER ===")
    print("[INFO] SAFE MODE - Reporting only, no auto-fix\n")

    results = {
        "python_packages": check_python_packages(),
        "directory_structure": check_directory_structure(),
        "config_flags": check_config_flags(),
    }

    # Print results
    print("=== PYTHON PACKAGES ===")
    pkg_check = results["python_packages"]
    status_icon = "✅" if pkg_check["status"] == "PASS" else "❌"
    print(f"{status_icon} Status: {pkg_check['status']}")
    for pkg, available in pkg_check["checked"].items():
        icon = "✅" if available else "❌"
        print(f"  {icon} {pkg}")
    if pkg_check.get("missing"):
        print(f"  Missing: {', '.join(pkg_check['missing'])}")

    print("\n=== DIRECTORY STRUCTURE ===")
    dir_check = results["directory_structure"]
    status_icon = "✅" if dir_check["status"] == "PASS" else "⚠️"
    print(f"{status_icon} Status: {dir_check['status']}")
    for dir_path, exists in dir_check["checked"].items():
        icon = "✅" if exists else "❌"
        print(f"  {icon} {dir_path}")
    if dir_check.get("missing"):
        print(f"  Missing: {', '.join(dir_check['missing'])}")

    print("\n=== CONFIG FLAGS ===")
    config_check = results["config_flags"]
    status_icon = "✅" if config_check["status"] == "PASS" else "❌"
    print(f"{status_icon} Status: {config_check['status']}")
    if "flags" in config_check:
        for flag, value in config_check["flags"].items():
            icon = "✅" if not value or (flag == "ultramode_read_only" and value) else "❌"
            print(f"  {icon} {flag}: {value}")
        print(f"  All Safe: {config_check.get('all_safe', False)}")

    # Overall status
    all_pass = all(r.get("status") == "PASS" for r in results.values())

    print(f"\n=== OVERALL STATUS: {'✅ PASS' if all_pass else '⚠️ WARN/FAIL'} ===")

    return results


def main() -> None:
    """Main entry point."""
    run_consistency_check()


if __name__ == "__main__":
    main()
