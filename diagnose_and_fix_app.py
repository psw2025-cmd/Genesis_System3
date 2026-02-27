#!/usr/bin/env python3
"""
Diagnose and Fix System3 Ultra Desktop App
Checks installation, fixes issues, and provides solutions
"""

import os
import sys
import subprocess
import requests
from pathlib import Path
from datetime import datetime

def print_header(text):
    print(f"\n{'='*80}")
    print(f"{text.center(80)}")
    print(f"{'='*80}\n")

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_warning(text):
    print(f"[WARNING] {text}")

def print_info(text):
    print(f"[INFO] {text}")

def check_installed_app():
    """Check installed app structure"""
    print_header("CHECKING INSTALLED APP")
    
    install_paths = [
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'System3 Ultra',
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'system3-ultra',
    ]
    
    found_install = None
    for path in install_paths:
        if path.exists():
            found_install = path
            break
    
    if not found_install:
        print_error("Installed app not found")
        print_info("Please install the app first: desktop_app\\dist\\System3 Ultra Setup 1.0.0.exe")
        return None
    
    print_success(f"Found installation: {found_install}")
    
    # Check resources
    resources_dir = found_install / "resources"
    if not resources_dir.exists():
        print_error("Resources directory missing - installation incomplete")
        return found_install
    
    print_success("Resources directory exists")
    
    # Check backend
    backend_dir = resources_dir / "backend"
    backend_app = backend_dir / "app.py"
    
    if backend_dir.exists():
        if backend_app.exists():
            print_success(f"Backend app.py exists: {backend_app}")
            # Count files
            files = list(backend_dir.glob("*.py"))
            print_info(f"Backend has {len(files)} Python files")
        else:
            print_error(f"Backend app.py missing: {backend_app}")
            print_warning("Backend directory exists but app.py is missing")
    else:
        print_error("Backend directory missing")
    
    # Check frontend
    frontend_dir = resources_dir / "frontend"
    frontend_index = frontend_dir / "index.html"
    
    if frontend_dir.exists():
        if frontend_index.exists():
            print_success(f"Frontend index.html exists: {frontend_index}")
            # Check assets
            assets_dir = frontend_dir / "assets"
            if assets_dir.exists():
                assets = list(assets_dir.glob("*"))
                print_info(f"Frontend has {len(assets)} asset files")
        else:
            print_error(f"Frontend index.html missing: {frontend_index}")
    else:
        print_error("Frontend directory missing")
    
    # Check agent_memory
    agent_dir = resources_dir / "agent_memory"
    if agent_dir.exists():
        print_success("Agent memory directory exists")
    else:
        print_warning("Agent memory directory missing (optional)")
    
    return found_install

def check_backend_running():
    """Check if backend is running"""
    print_header("CHECKING BACKEND STATUS")
    
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=2)
        if response.status_code == 200:
            print_success("Backend is running!")
            print_info(f"Response: {response.json()}")
            return True
    except requests.exceptions.ConnectionError:
        print_warning("Backend is not running")
        return False
    except Exception as e:
        print_warning(f"Could not check backend: {e}")
        return False

def start_backend_manually(install_path):
    """Start backend manually for testing"""
    print_header("MANUAL BACKEND START")
    
    if not install_path:
        print_error("No installation found")
        return False
    
    backend_dir = install_path / "resources" / "backend"
    app_py = backend_dir / "app.py"
    
    if not app_py.exists():
        print_error(f"app.py not found: {app_py}")
        print_info("You need to reinstall the app with the latest installer")
        return False
    
    print_info(f"Starting backend from: {backend_dir}")
    print_info("This will run in a new window...")
    
    # Find Python
    python_paths = [
        'C:\\Python314\\python.exe',
        'C:\\Python313\\python.exe',
        'python'
    ]
    
    python_exe = None
    for py_path in python_paths:
        if Path(py_path).exists() or py_path == 'python':
            python_exe = py_path
            break
    
    if not python_exe:
        print_error("Python not found")
        return False
    
    print_info(f"Using Python: {python_exe}")
    
    # Start backend
    try:
        subprocess.Popen(
            [python_exe, '-m', 'uvicorn', 'app:app', '--host', '0.0.0.0', '--port', '8000'],
            cwd=str(backend_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        print_success("Backend started in new window")
        print_info("Waiting 5 seconds for startup...")
        import time
        time.sleep(5)
        
        # Check if started
        if check_backend_running():
            return True
        else:
            print_warning("Backend may still be starting...")
            return False
    except Exception as e:
        print_error(f"Failed to start backend: {e}")
        return False

def run_validation():
    """Run production validation"""
    print_header("RUNNING VALIDATION")
    
    try:
        result = subprocess.run(
            [sys.executable, "production_grade_validation.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(result.stdout)
        return result.returncode == 0
    except Exception as e:
        print_error(f"Validation failed: {e}")
        return False

def main():
    """Main diagnostic flow"""
    print_header("SYSTEM3 ULTRA - DIAGNOSE AND FIX")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Check installation
    install_path = check_installed_app()
    
    # Step 2: Check backend
    backend_running = check_backend_running()
    
    # Step 3: Check if we can start backend from dev directory
    if not backend_running:
        print_info("\nAttempting to start backend from development directory...")
        dev_backend = Path("dashboard/backend/app.py")
        if dev_backend.exists():
            print_info("Starting backend from development directory...")
            try:
                subprocess.Popen(
                    [sys.executable, '-m', 'uvicorn', 'dashboard.backend.app:app', '--host', '0.0.0.0', '--port', '8000'],
                    cwd=str(Path.cwd()),
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                )
                print_success("Backend started from dev directory")
                import time
                time.sleep(5)
                backend_running = check_backend_running()
            except Exception as e:
                print_warning(f"Could not start backend: {e}")
    
    # Step 4: Run validation if backend is running
    if backend_running:
        print_info("\nRunning validation...")
        run_validation()
    else:
        print_warning("\nCannot run full validation without backend running")
        print_info("Options:")
        print("  1. Reinstall app with latest installer")
        print("  2. Start backend manually (see above)")
        print("  3. Check DevTools console in app for backend errors")
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    if install_path:
        print_success("Installation found")
    else:
        print_error("Installation not found - need to install")
    
    if backend_running:
        print_success("Backend is running")
    else:
        print_error("Backend is not running")
        print_info("This is why the dashboard is blank")
    
    print("\nNext Steps:")
    if not install_path or not (install_path / "resources" / "backend" / "app.py").exists():
        print("  1. Reinstall app: desktop_app\\dist\\System3 Ultra Setup 1.0.0.exe")
    if not backend_running:
        print("  2. Launch app and check DevTools (Ctrl+Shift+I) for backend errors")
        print("  3. Or start backend manually using the option above")
    if backend_running:
        print("  4. Dashboard should now show data")
        print("  5. Run: python production_grade_validation.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nDiagnostic interrupted")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
