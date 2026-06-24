#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Doctor - Environment and Dependency Validator
Checks all prerequisites and dependencies for the Genesis System3
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Fix encoding for Windows console
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).parent.parent


def check_python() -> Tuple[bool, str]:
    """Check Python version"""
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True, timeout=5)
        version = result.stdout.strip()
        version_num = version.split()[-1]
        major, minor = map(int, version_num.split(".")[:2])
        if major >= 3 and minor >= 8:
            return True, version
        return False, f"{version} (requires Python 3.8+)"
    except Exception as e:
        return False, f"Error: {e}"


def check_node() -> Tuple[bool, str]:
    """Check Node.js version"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        version = result.stdout.strip()
        version_num = version.lstrip("v")
        major = int(version_num.split(".")[0])
        if major >= 16:
            return True, version
        return False, f"{version} (requires Node.js 16+)"
    except FileNotFoundError:
        return False, "Not installed"
    except Exception as e:
        return False, f"Error: {e}"


def check_npm() -> Tuple[bool, str]:
    """Check npm version"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=5)
        return True, result.stdout.strip()
    except FileNotFoundError:
        return False, "Not installed"
    except Exception as e:
        return False, f"Error: {e}"


def check_python_packages() -> Dict[str, Tuple[bool, str]]:
    """Check critical Python packages"""
    critical = ["pandas", "numpy", "scipy", "scikit-learn", "fastapi", "uvicorn", "requests", "pytz"]
    results = {}
    for pkg in critical:
        try:
            __import__(pkg.replace("-", "_"))
            results[pkg] = (True, "Installed")
        except ImportError:
            results[pkg] = (False, "Missing")
        except Exception as e:
            results[pkg] = (False, f"Error: {e}")
    return results


def check_node_packages() -> Tuple[bool, str]:
    """Check if node_modules exists"""
    frontend_dir = ROOT_DIR / "dashboard" / "frontend"
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        return True, "Installed"
    return False, "Not installed (run: npm install)"


def check_directories() -> Dict[str, bool]:
    """Check required directories exist"""
    required = ["dashboard/backend", "dashboard/frontend", "outputs", "logs", "config"]
    results = {}
    for dir_path in required:
        full_path = ROOT_DIR / dir_path
        results[dir_path] = full_path.exists()
    return results


def check_ports() -> Dict[str, Tuple[bool, str]]:
    """Check if ports are available"""
    import socket

    ports = {"8000": "Backend API", "3000": "Frontend Dashboard"}
    results = {}
    for port, name in ports.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("localhost", int(port)))
            sock.close()
            results[port] = (True, f"{name} port available")
        except OSError:
            results[port] = (False, f"{name} port in use")
        except Exception as e:
            results[port] = (False, f"Error: {e}")
    return results


def main():
    """Run all checks"""
    print("=" * 70)
    print("GENESIS SYSTEM3 - DOCTOR CHECK")
    print("=" * 70)
    print()

    all_ok = True

    # Python
    print("Python:")
    ok, msg = check_python()
    status = "[OK]" if ok else "[FAIL]"
    print(f"  {status} {msg}")
    if not ok:
        all_ok = False

    # Node.js
    print("\nNode.js:")
    ok, msg = check_node()
    status = "[OK]" if ok else "[FAIL]"
    print(f"  {status} {msg}")
    if not ok:
        all_ok = False

    # npm
    print("\nnpm:")
    ok, msg = check_npm()
    status = "[OK]" if ok else "[FAIL]"
    print(f"  {status} {msg}")
    if not ok:
        all_ok = False

    # Python packages
    print("\nPython Packages:")
    packages = check_python_packages()
    for pkg, (ok, msg) in packages.items():
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} {pkg}: {msg}")
        if not ok:
            all_ok = False

    # Node packages
    print("\nNode Packages:")
    ok, msg = check_node_packages()
    status = "[OK]" if ok else "[FAIL]"
    print(f"  {status} {msg}")
    if not ok:
        all_ok = False

    # Directories
    print("\nDirectories:")
    dirs = check_directories()
    for dir_path, exists in dirs.items():
        status = "[OK]" if exists else "[FAIL]"
        print(f"  {status} {dir_path}")
        if not exists:
            all_ok = False

    # Ports
    print("\nPorts:")
    ports = check_ports()
    for port, (ok, msg) in ports.items():
        status = "[OK]" if ok else "[WARN]"
        print(f"  {status} Port {port}: {msg}")
        if not ok:
            all_ok = False

    print()
    print("=" * 70)
    if all_ok:
        print("[SUCCESS] ALL CHECKS PASSED")
        return 0
    else:
        print("[WARNING] SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
