#!/usr/bin/env python3
"""
Check all requirements before building System3 Ultra installer.
Run this first; fix any [FAIL] before running build_fresh_installer.bat.
"""
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def ok(msg):
    print(f"  [OK]   {msg}")

def fail(msg):
    print(f"  [FAIL] {msg}")

def warn(msg):
    print(f"  [WARN] {msg}")

def section(title):
    print(f"\n--- {title} ---")

def main():
    print("=" * 60)
    print("  PRE-BUILD REQUIREMENTS CHECK")
    print("  (Fix any [FAIL] before building)")
    print("=" * 60)

    all_ok = True

    # --- Python ---
    section("1. Python")
    try:
        v = sys.version_info
        ver = f"{v.major}.{v.minor}.{v.micro}"
        if v.major >= 3 and v.minor >= 8:
            ok(f"Python {ver} (need 3.8+)")
        else:
            fail(f"Python {ver} - need 3.8 or higher")
            all_ok = False
    except Exception as e:
        fail(f"Could not get Python version: {e}")
        all_ok = False

    # --- Virtual environment ---
    section("2. Virtual environment (venv)")
    in_venv = getattr(sys, "prefix", None) != getattr(sys, "base_prefix", None) or hasattr(sys, "real_prefix")
    if in_venv:
        ok("Running inside a virtual environment")
    else:
        venv_dir = ROOT / "venv"
        if venv_dir.is_dir():
            warn("Not inside venv. Activate it for builds:")
            print("      PowerShell:  .\\venv\\Scripts\\Activate.ps1")
            print("      CMD:         venv\\Scripts\\activate.bat")
        else:
            fail("No venv found. Create one:  python -m venv venv")
            all_ok = False

    # --- Python packages (root + backend) ---
    section("3. Python dependencies")
    try:
        import requests
        ok("requests")
    except ImportError:
        fail("requests - run: pip install -r requirements.txt")
        all_ok = False
    try:
        import pandas
        ok("pandas")
    except ImportError:
        fail("pandas - run: pip install -r requirements.txt")
        all_ok = False
    try:
        import fastapi
        ok("fastapi (backend)")
    except ImportError:
        fail("fastapi - run: pip install -r dashboard/backend/requirements.txt")
        all_ok = False
    try:
        import uvicorn
        ok("uvicorn (backend)")
    except ImportError:
        fail("uvicorn - run: pip install -r dashboard/backend/requirements.txt")
        all_ok = False

    # --- Node.js & npm ---
    section("4. Node.js and npm")
    for cmd, name, min_ver in [("node", "Node.js", 18), ("npm", "npm", 8)]:
        try:
            out = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=15, shell=True)
            ver_str = (out.stdout or out.stderr or "").strip().lstrip("v")
            if out.returncode == 0 and ver_str:
                try:
                    major = int(ver_str.split(".")[0])
                    if major >= min_ver:
                        ok(f"{name} {ver_str} (need {min_ver}+)")
                    else:
                        fail(f"{name} {ver_str} - need {min_ver}+")
                        all_ok = False
                except (ValueError, IndexError):
                    ok(f"{name} {ver_str}")
            else:
                fail(f"{name} not found - install Node.js 18+ from https://nodejs.org")
                all_ok = False
        except Exception as e:
            fail(f"{name} not found or error: {e}")
            all_ok = False

    # --- Frontend node_modules ---
    section("5. Frontend (dashboard/frontend)")
    frontend = ROOT / "dashboard" / "frontend"
    pkg = frontend / "package.json"
    node_mod = frontend / "node_modules"
    if not pkg.exists():
        fail("dashboard/frontend/package.json not found")
        all_ok = False
    elif not node_mod.is_dir():
        fail("dashboard/frontend/node_modules missing - run:  cd dashboard/frontend  &&  npm install")
        all_ok = False
    else:
        ok("package.json and node_modules present")

    # --- Desktop app node_modules ---
    section("6. Desktop app (desktop_app)")
    desktop = ROOT / "desktop_app"
    dpkg = desktop / "package.json"
    dnode = desktop / "node_modules"
    if not dpkg.exists():
        fail("desktop_app/package.json not found")
        all_ok = False
    elif not dnode.is_dir():
        fail("desktop_app/node_modules missing - run:  cd desktop_app  &&  npm install")
        all_ok = False
    else:
        ok("package.json and node_modules present")

    # --- Required folders for packaging ---
    section("7. Folders packaged into installer")
    backend_dir = ROOT / "dashboard" / "backend"
    if backend_dir.is_dir():
        ok("dashboard/backend (packaged as backend)")
    else:
        fail("dashboard/backend folder missing")
        all_ok = False
    agent_mem = ROOT / "agent_memory"
    if agent_mem.is_dir():
        ok("agent_memory (packaged into app)")
    else:
        warn("agent_memory folder missing - create if your app needs it")

    # --- Summary ---
    print("\n" + "=" * 60)
    if all_ok:
        print("  ALL CHECKS PASSED - you can run build_fresh_installer.bat")
    else:
        print("  SOME CHECKS FAILED - fix [FAIL] items above, then run this script again")
        sys.exit(1)
    print("=" * 60 + "\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
