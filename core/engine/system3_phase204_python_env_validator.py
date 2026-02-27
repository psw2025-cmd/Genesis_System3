"""
System3 Phase 204 - Python Environment Validator

Checks Python version and required packages.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "env"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_env_validator.log"

REQUIRED_PACKAGES = [
    "pandas",
    "numpy",
    "requests",
    "sklearn",
    "xgboost",
    "scipy",
    "joblib",
    "matplotlib",
    "seaborn",
]

MIN_PYTHON_VERSION = (3, 10)


def check_python_version() -> tuple[bool, str]:
    """Check if Python version meets requirements."""
    version = sys.version_info[:2]
    if version >= MIN_PYTHON_VERSION:
        return True, f"{version[0]}.{version[1]}"
    return False, f"{version[0]}.{version[1]} (requires {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+)"


def check_package(package_name: str) -> tuple[bool, str]:
    """Check if a package is importable."""
    try:
        __import__(package_name)
        return True, ""
    except ImportError as e:
        return False, str(e)


def run_phase204(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 204: Python Environment Validator.

    Returns:
        dict: {
            "phase": 204,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "python_version": str,
                "missing_packages": list,
                "install_script_path": str,
            },
            "errors": [],
        }
    """
    errors = []
    missing_packages = []

    try:
        with LOG_PATH.open("w", encoding="utf-8") as f:
            f.write(f"System3 Environment Validator Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            # Check Python version
            py_ok, py_version = check_python_version()
            f.write(f"Python Version: {sys.version}\n")
            f.write(f"Version Check: {'✅ OK' if py_ok else '❌ FAIL'}\n")
            f.write(f"Required: {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+\n\n")

            if not py_ok:
                errors.append(f"Python version {py_version} does not meet requirements")

            # Check packages
            f.write("Package Checks:\n")
            f.write("-" * 70 + "\n")
            for pkg in REQUIRED_PACKAGES:
                pkg_ok, error_msg = check_package(pkg)
                status = "✅" if pkg_ok else "❌"
                f.write(f"{status} {pkg}")
                if not pkg_ok:
                    f.write(f" - {error_msg}")
                    missing_packages.append(pkg)
                f.write("\n")

            f.write("\n")

        # Generate install script
        install_script = PROJECT_ROOT / "install_requirements.bat"
        if missing_packages:
            with install_script.open("w", encoding="utf-8") as f:
                f.write("@echo off\n")
                f.write("echo Installing missing System3 requirements...\n")
                for pkg in missing_packages:
                    f.write(f"pip install {pkg}\n")
                f.write("echo Done.\n")
                f.write("pause\n")

        status = "WARN" if missing_packages or not py_ok else "OK"
        details = f"Python {py_version}"
        if missing_packages:
            details += f", {len(missing_packages)} missing packages"

        return {
            "phase": 204,
            "status": status,
            "details": details,
            "outputs": {
                "python_version": py_version,
                "missing_packages": missing_packages,
                "install_script_path": str(install_script) if missing_packages else None,
                "log_path": str(LOG_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 204,
            "status": "ERROR",
            "details": f"Phase 204 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 204 - PYTHON ENVIRONMENT VALIDATOR")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase204()

    print(f"Phase 204: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nLog: {result['outputs']['log_path']}")
        print(f"Python: {result['outputs']['python_version']}")
        if result["outputs"]["missing_packages"]:
            print(f"Missing: {', '.join(result['outputs']['missing_packages'])}")
            print(f"Install script: {result['outputs']['install_script_path']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
