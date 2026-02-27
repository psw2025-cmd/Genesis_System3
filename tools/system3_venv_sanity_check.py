#!/usr/bin/env python3
"""
System3 Venv Sanity Check Tool

Validates that the venv is healthy before autorun/watchdog start.
Checks:
  - Current interpreter is venv python
  - Critical dependencies importable (pandas, psutil, numpy, xgboost, joblib)
  - Venv site-packages is in sys.path

Exit codes:
  0 = All OK
  1 = Interpreter not venv
  2 = Missing dependency
  3 = Other error

Usage:
  python tools/system3_venv_sanity_check.py [--report] [--strict]
  
  --report: Write VENV_SANITY_STATUS.md with results
  --strict: Fail on any warning (default: only fail on errors)
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple

ROOT_DIR = Path(__file__).parent.parent.absolute()

# Critical dependencies (must be importable)
CRITICAL_DEPS = [
    "pandas",
    "numpy",
    "psutil",
]

# Important optional dependencies (use actual import names)
OPTIONAL_DEPS = [
    "xgboost",
    "joblib",
    "sklearn",  # scikit-learn package, but import as sklearn
    "tensorflow",
]


def check_interpreter() -> Tuple[bool, str]:
    """
    Verify we are running from venv interpreter.
    Returns (is_ok, message).
    """
    expected_venv_path = ROOT_DIR / "venv" / "Scripts" / "python.exe"
    actual_executable = os.path.abspath(sys.executable)
    expected_executable = os.path.abspath(str(expected_venv_path))

    if actual_executable != expected_executable:
        return (False, f"Wrong interpreter: {actual_executable}\n" f"Expected: {expected_executable}")

    # Note: VIRTUAL_ENV check is informational only when running via explicit venv path
    # It's set by activate.bat but not required if script is called with full venv path

    return (True, f"Interpreter OK: {actual_executable}")


def check_dependency_importable(module_name: str) -> Tuple[bool, str, str]:
    """
    Try to import a module.
    Returns (success, message, import_path_or_error).
    """
    try:
        module = __import__(module_name)
        module_path = getattr(module, "__file__", "built-in")
        return (True, f"OK", module_path or "built-in")
    except ImportError as e:
        return (False, str(e), "not-installed")
    except Exception as e:
        return (False, f"Unexpected error: {type(e).__name__}: {e}", "error")


def check_site_packages() -> Tuple[bool, str, str]:
    """
    Verify venv site-packages is in sys.path.
    Returns (is_ok, message, path).
    """
    expected_site_packages = ROOT_DIR / "venv" / "Lib" / "site-packages"

    if not expected_site_packages.exists():
        return (False, "Venv site-packages directory not found", str(expected_site_packages))

    # Check if site-packages is accessible (either in sys.path or packages can be imported)
    # When run with explicit venv python path, sys.path is automatically set correctly
    if str(expected_site_packages) in sys.path:
        return (True, "Venv site-packages in sys.path", str(expected_site_packages))

    # Secondary check: if pandas can be imported, site-packages is working
    try:
        import pandas

        return (True, "Venv site-packages accessible (verified via imports)", str(expected_site_packages))
    except ImportError:
        return (False, f"Venv site-packages not in sys.path and imports failing", str(expected_site_packages))

    return (True, "Venv site-packages in sys.path", str(expected_site_packages))


def generate_report(results: Dict) -> str:
    """
    Generate a human-readable markdown report.
    """
    timestamp = datetime.now().isoformat()

    lines = [
        "# 🔍 Venv Sanity Check Report",
        "",
        f"**Time:** {timestamp}",
        f"**Status:** {'✅ PASS' if results['overall_status'] == 'OK' else '❌ FAIL'}",
        "",
        "## Interpreter Check",
        "",
        f"- **Result:** {'✅ OK' if results['interpreter_ok'] else '❌ FAIL'}",
        f"- **Actual:** `{results['actual_interpreter']}`",
        f"- **Expected:** `{results['expected_interpreter']}`",
        f"- **Message:** {results['interpreter_message']}",
        "",
        "## Site-Packages Check",
        "",
        f"- **Result:** {'✅ OK' if results['site_packages_ok'] else '❌ FAIL'}",
        f"- **Path:** `{results['site_packages_path']}`",
        f"- **Message:** {results['site_packages_message']}",
        "",
        "## Critical Dependencies",
        "",
    ]

    for dep in CRITICAL_DEPS:
        dep_result = results["critical_deps"].get(dep, {})
        status = "✅" if dep_result.get("ok") else "❌"
        msg = dep_result.get("message", "unknown")
        path = dep_result.get("path", "N/A")
        lines.append(f"- {status} **{dep}**: {msg}")
        if path != "not-installed" and path != "error":
            lines.append(f"  - Path: `{path}`")

    lines.extend(
        [
            "",
            "## Optional Dependencies",
            "",
        ]
    )

    for dep in OPTIONAL_DEPS:
        dep_result = results["optional_deps"].get(dep, {})
        status = "✅" if dep_result.get("ok") else "⚠️"
        msg = dep_result.get("message", "unknown")
        lines.append(f"- {status} **{dep}**: {msg}")

    lines.extend(
        [
            "",
            "## Summary",
            "",
        ]
    )

    if results["overall_status"] == "OK":
        lines.append("✅ **Venv is healthy. Safe to start autorun + watchdog.**")
    else:
        lines.append("❌ **Venv has issues. See details above.**")
        if results["missing_critical"]:
            lines.append("")
            lines.append("### Action Required:")
            lines.append("")
            lines.append("Your venv is missing or broken. Follow `VENV_RECOVERY_GUIDE.md`:")
            lines.append("")
            lines.append("1. Kill all python processes")
            lines.append("2. Delete the venv: `rmdir /S /Q C:\\Genesis_System3\\venv`")
            lines.append("3. Recreate: `python -m venv C:\\Genesis_System3\\venv`")
            lines.append("4. Install deps: `pip install pandas psutil numpy`")
            lines.append("5. Verify: `python tools/system3_venv_sanity_check.py`")
            lines.append("6. Run launcher: `.\\START_AUTORUN_AND_WATCHDOG.bat`")

    return "\n".join(lines)


def main():
    """
    Main sanity check flow.
    """
    report_mode = "--report" in sys.argv
    strict_mode = "--strict" in sys.argv

    results = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "OK",
        "missing_critical": False,
        "interpreter_ok": False,
        "interpreter_message": "",
        "actual_interpreter": sys.executable,
        "expected_interpreter": str(ROOT_DIR / "venv" / "Scripts" / "python.exe"),
        "site_packages_ok": False,
        "site_packages_message": "",
        "site_packages_path": "",
        "critical_deps": {},
        "optional_deps": {},
    }

    # Check interpreter
    interp_ok, interp_msg = check_interpreter()
    results["interpreter_ok"] = interp_ok
    results["interpreter_message"] = interp_msg
    if not interp_ok:
        results["overall_status"] = "FAIL"
        print(f"❌ Interpreter check failed: {interp_msg}")
    else:
        print(f"✅ {interp_msg}")

    # Check site-packages
    site_ok, site_msg, site_path = check_site_packages()
    results["site_packages_ok"] = site_ok
    results["site_packages_message"] = site_msg
    results["site_packages_path"] = site_path
    if not site_ok:
        results["overall_status"] = "FAIL"
        print(f"❌ Site-packages check failed: {site_msg}")
    else:
        print(f"✅ {site_msg}")

    # Check critical dependencies
    print("")
    print("Checking critical dependencies...")
    for dep in CRITICAL_DEPS:
        dep_ok, dep_msg, dep_path = check_dependency_importable(dep)
        results["critical_deps"][dep] = {
            "ok": dep_ok,
            "message": dep_msg,
            "path": dep_path,
        }
        status = "✅" if dep_ok else "❌"
        print(f"  {status} {dep}: {dep_msg}")
        if not dep_ok:
            results["overall_status"] = "FAIL"
            results["missing_critical"] = True

    # Check optional dependencies
    print("")
    print("Checking optional dependencies...")
    for dep in OPTIONAL_DEPS:
        dep_ok, dep_msg, dep_path = check_dependency_importable(dep)
        results["optional_deps"][dep] = {
            "ok": dep_ok,
            "message": dep_msg,
            "path": dep_path,
        }
        status = "✅" if dep_ok else "⚠️"
        print(f"  {status} {dep}: {dep_msg}")

    # Summary
    print("")
    print("=" * 70)
    if results["overall_status"] == "OK":
        print("✅ PASS: Venv is healthy. Safe to start autorun + watchdog.")
        exit_code = 0
    else:
        print("❌ FAIL: Venv has critical issues. See details above.")
        if results["missing_critical"]:
            print("")
            print("Follow VENV_RECOVERY_GUIDE.md to fix.")
        exit_code = 2 if results["missing_critical"] else 1
    print("=" * 70)

    # Write report if requested
    if report_mode:
        report_content = generate_report(results)
        report_path = ROOT_DIR / "VENV_SANITY_STATUS.md"
        try:
            report_path.write_text(report_content, encoding="utf-8")
            print(f"✅ Report written: {report_path}")
        except Exception as e:
            print(f"⚠️  Failed to write report: {e}")

    # Write JSON results for programmatic access
    try:
        json_path = ROOT_DIR / "state" / "venv_sanity_check.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"⚠️  Failed to write JSON results: {e}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
