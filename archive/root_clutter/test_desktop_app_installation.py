#!/usr/bin/env python3
"""
Comprehensive Desktop App Installation Test Script
Tests all aspects of System3 Ultra desktop app installation
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import shutil

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

def check_file_exists(path, description):
    """Check if file exists"""
    p = Path(path)
    if p.exists():
        size = p.stat().st_size
        print_success(f"{description}: EXISTS ({size:,} bytes)")
        return True
    else:
        print_error(f"{description}: MISSING")
        return False

def check_main_js_fixes():
    """Verify main.js has all required fixes"""
    print_header("CHECKING MAIN.JS FIXES")
    
    main_js = Path("desktop_app/main.js")
    if not main_js.exists():
        print_error("main.js not found")
        return False
    
    content = main_js.read_text(encoding='utf-8')
    issues = []
    
    # Check for isPackaged detection
    if "isPackaged" not in content:
        issues.append("Missing isPackaged detection")
    else:
        print_success("isPackaged detection found")
    
    # Check for resourcesPath usage
    if "resourcesPath" not in content:
        issues.append("Missing resourcesPath usage for installed app")
    else:
        print_success("resourcesPath usage found")
    
    # Check for Python auto-detection
    if "pythonPaths" not in content:
        issues.append("Missing Python auto-detection (pythonPaths array)")
    elif "C:\\Python314" not in content and "Python314" not in content:
        issues.append("Missing Python auto-detection (Python314 path)")
    else:
        print_success("Python auto-detection found")
    
    # Check for frontend path fix
    if "path.join(resourcesPath, 'frontend')" not in content:
        issues.append("Frontend path not using resourcesPath")
    else:
        print_success("Frontend path fix found")
    
    if issues:
        print_error(f"Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    return True

def check_package_json_fixes():
    """Verify package.json has all required fixes"""
    print_header("CHECKING PACKAGE.JSON FIXES")
    
    package_json = Path("desktop_app/package.json")
    if not package_json.exists():
        print_error("package.json not found")
        return False
    
    try:
        with open(package_json, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print_error(f"Could not parse package.json: {e}")
        return False
    
    issues = []
    
    # Check build target
    build_config = config.get("build", {})
    win_config = build_config.get("win", {})
    targets = win_config.get("target", [])
    
    has_nsis = False
    for target in targets:
        if isinstance(target, dict):
            if target.get("target") == "nsis":
                has_nsis = True
                break
        elif target == "nsis":
            has_nsis = True
            break
    
    if not has_nsis:
        issues.append("NSIS target not configured")
    else:
        print_success("NSIS target configured")
    
    # Check extraResources
    extra_resources = build_config.get("extraResources", [])
    has_backend = False
    has_frontend = False
    has_agent_memory = False
    
    for resource in extra_resources:
        if isinstance(resource, dict):
            to_path = resource.get("to", "")
            if to_path == "backend":
                has_backend = True
            elif to_path == "frontend":
                has_frontend = True
            elif to_path == "agent_memory":
                has_agent_memory = True
    
    if not has_backend:
        issues.append("Backend not in extraResources")
    else:
        print_success("Backend in extraResources")
    
    if not has_frontend:
        issues.append("Frontend not in extraResources")
    else:
        print_success("Frontend in extraResources")
    
    if not has_agent_memory:
        issues.append("Agent memory not in extraResources")
    else:
        print_success("Agent memory in extraResources")
    
    if issues:
        print_error(f"Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    return True

def check_build_prerequisites():
    """Check if all prerequisites for building are met"""
    print_header("CHECKING BUILD PREREQUISITES")
    
    all_ok = True
    
    # Check Node.js
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success(f"Node.js: {result.stdout.strip()}")
        else:
            print_error("Node.js not found or not working")
            all_ok = False
    except Exception as e:
        print_error(f"Node.js check failed: {e}")
        all_ok = False
    
    # Check npm (try multiple ways)
    npm_found = False
    try:
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success(f"npm: {result.stdout.strip()}")
            npm_found = True
    except Exception:
        pass
    
    # Try npx as alternative
    if not npm_found:
        try:
            result = subprocess.run(
                ["npx", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print_success(f"npx available: {result.stdout.strip()}")
                npm_found = True
        except Exception:
            pass
    
    if not npm_found:
        print_warning("npm/npx not found in PATH (may still work if Node.js is installed)")
        # Don't fail - npm might be available through other means
    
    # Check electron-builder
    desktop_app_dir = Path("desktop_app")
    node_modules = desktop_app_dir / "node_modules" / "electron-builder"
    if node_modules.exists():
        print_success("electron-builder installed")
    else:
        print_warning("electron-builder not found in node_modules")
        print_info("Run: cd desktop_app && npm install")
        all_ok = False
    
    # Check frontend build
    frontend_dist = Path("dashboard/frontend/dist/index.html")
    if frontend_dist.exists():
        print_success("Frontend built (dist/index.html exists)")
    else:
        print_error("Frontend not built - need to build frontend first")
        all_ok = False
    
    # Check backend files
    backend_app = Path("dashboard/backend/app.py")
    if backend_app.exists():
        print_success("Backend files exist")
    else:
        print_error("Backend files missing")
        all_ok = False
    
    return all_ok

def check_installer_exists():
    """Check if installer exe exists"""
    print_header("CHECKING INSTALLER")
    
    dist_dir = Path("desktop_app/dist")
    installer_patterns = [
        "System3 Ultra Setup*.exe",
        "System3 Ultra*.exe"
    ]
    
    found_installer = None
    for pattern in installer_patterns:
        matches = list(dist_dir.glob(pattern))
        if matches:
            found_installer = matches[0]
            break
    
    if found_installer:
        size = found_installer.stat().st_size
        print_success(f"Installer found: {found_installer.name} ({size:,} bytes)")
        return True, found_installer
    else:
        print_error("Installer exe not found")
        print_info("Expected location: desktop_app/dist/System3 Ultra Setup 1.0.0.exe")
        return False, None

def verify_bundled_resources():
    """Verify resources are bundled in unpacked build"""
    print_header("VERIFYING BUNDLED RESOURCES")
    
    unpacked_dir = Path("desktop_app/dist/win-unpacked")
    if not unpacked_dir.exists():
        print_error("Unpacked build not found")
        return False
    
    resources_dir = unpacked_dir / "resources"
    if not resources_dir.exists():
        print_error("Resources directory not found")
        return False
    
    all_ok = True
    
    # Check backend
    backend_dir = resources_dir / "backend"
    if backend_dir.exists():
        app_py = backend_dir / "app.py"
        if app_py.exists():
            print_success("Backend bundled")
        else:
            print_error("Backend bundled but app.py missing")
            all_ok = False
    else:
        print_error("Backend not bundled")
        all_ok = False
    
    # Check frontend
    frontend_dir = resources_dir / "frontend"
    if frontend_dir.exists():
        index_html = frontend_dir / "index.html"
        if index_html.exists():
            print_success("Frontend bundled")
        else:
            print_error("Frontend bundled but index.html missing")
            all_ok = False
    else:
        print_error("Frontend not bundled")
        all_ok = False
    
    # Check agent_memory
    agent_memory_dir = resources_dir / "agent_memory"
    if agent_memory_dir.exists():
        print_success("Agent memory bundled")
    else:
        print_warning("Agent memory not bundled (may be optional)")
    
    return all_ok

def test_build():
    """Test building the installer"""
    print_header("TESTING BUILD PROCESS")
    
    desktop_app_dir = Path("desktop_app")
    original_dir = os.getcwd()
    
    try:
        os.chdir(desktop_app_dir)
        print_info("Running: npm run build:win")
        
        result = subprocess.run(
            ["npm", "run", "build:win"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes max
        )
        
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print_success("Build completed successfully")
            print("\nBuild output:")
            print(result.stdout[-2000:])  # Last 2000 chars
            return True
        else:
            print_error("Build failed")
            print("\nError output:")
            print(result.stderr[-2000:])
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Build timed out (took more than 10 minutes)")
        return False
    except Exception as e:
        print_error(f"Build error: {e}")
        return False
    finally:
        os.chdir(original_dir)

def main():
    """Main test flow"""
    print_header("SYSTEM3 ULTRA DESKTOP APP INSTALLATION TEST")
    
    results = {}
    
    # Step 1: Check main.js fixes
    results['main_js'] = check_main_js_fixes()
    
    # Step 2: Check package.json fixes
    results['package_json'] = check_package_json_fixes()
    
    # Step 3: Check prerequisites
    results['prerequisites'] = check_build_prerequisites()
    
    # Step 4: Check if installer exists
    installer_exists, installer_path = check_installer_exists()
    results['installer_exists'] = installer_exists
    
    # Step 5: Verify bundled resources (if unpacked exists)
    results['bundled_resources'] = verify_bundled_resources()
    
    # Step 6: Summary
    print_header("TEST SUMMARY")
    
    all_passed = all([
        results['main_js'],
        results['package_json'],
        results['prerequisites'],
        results['bundled_resources']
    ])
    
    print("\nTest Results:")
    print(f"  Main.js fixes: {'[OK]' if results['main_js'] else '[FAIL]'}")
    print(f"  Package.json fixes: {'[OK]' if results['package_json'] else '[FAIL]'}")
    print(f"  Prerequisites: {'[OK]' if results['prerequisites'] else '[FAIL]'}")
    print(f"  Installer exists: {'[OK]' if results['installer_exists'] else '[FAIL]'}")
    print(f"  Bundled resources: {'[OK]' if results['bundled_resources'] else '[FAIL]'}")
    
    if not results['installer_exists'] and all_passed:
        print("\n[INFO] All fixes are in place, but installer needs to be built.")
        print("Run: cd desktop_app && npm run build:win")
        
        # Auto-build if all checks pass
        print("\n[INFO] All prerequisites met. Building installer...")
        if test_build():
            # Re-check installer
            installer_exists, installer_path = check_installer_exists()
            if installer_exists:
                print_success(f"\nInstaller ready: {installer_path}")
                # Verify bundled resources now
                print("\nVerifying bundled resources after build...")
                results['bundled_resources'] = verify_bundled_resources()
                print("\nNext steps:")
                print("1. Run the installer: " + str(installer_path))
                print("2. Install to a test location")
                print("3. Launch the installed app")
                print("4. Verify backend starts (check console logs)")
                print("5. Verify frontend loads")
                print("6. Check Python detection in logs")
            else:
                print_error("Build completed but installer not found")
                return 1
        else:
            print_error("Build failed. Check errors above.")
            return 1
    
    if not all_passed:
        print("\n[ERROR] Some tests failed. Fix issues before building installer.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
