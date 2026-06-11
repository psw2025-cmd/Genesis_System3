#!/usr/bin/env python3
"""
Desktop App Installation Diagnostic
Identifies issues with the System3 Ultra Desktop App after installation
"""

import os
import sys
from pathlib import Path
import json

def print_header(text):
    print(f"\n{'='*80}")
    print(f"{text.center(80)}")
    print(f"{'='*80}\n")

def check_file_exists(path, description):
    """Check if a file exists and report"""
    if Path(path).exists():
        size = Path(path).stat().st_size
        print(f"[OK] {description}: EXISTS ({size:,} bytes)")
        print(f"  Path: {path}")
        return True
    else:
        print(f"[MISSING] {description}: MISSING")
        print(f"  Expected path: {path}")
        return False

def analyze_desktop_app():
    """Analyze desktop app structure and identify issues"""
    print_header("SYSTEM3 ULTRA DESKTOP APP DIAGNOSTIC")
    
    issues = []
    
    # Check desktop app files
    print("1. DESKTOP APP SOURCE FILES")
    print("-" * 80)
    
    desktop_dir = Path("desktop_app")
    
    if not check_file_exists(desktop_dir / "main.js", "Main process"):
        issues.append("main.js missing")
    
    if not check_file_exists(desktop_dir / "preload.js", "Preload script"):
        issues.append("preload.js missing")
    
    if not check_file_exists(desktop_dir / "package.json", "Package config"):
        issues.append("package.json missing")
    
    # Check build output
    print("\n2. BUILD OUTPUT")
    print("-" * 80)
    
    dist_dir = desktop_dir / "dist"
    setup_exe = dist_dir / "System3 Ultra Setup 1.0.0.exe"
    
    if not check_file_exists(setup_exe, "Setup executable"):
        issues.append("Setup.exe not built")
    
    # Check frontend dist
    print("\n3. FRONTEND DISTRIBUTION")
    print("-" * 80)
    
    frontend_dist = Path("dashboard/frontend/dist")
    
    if not check_file_exists(frontend_dist / "index.html", "Frontend HTML"):
        issues.append("Frontend not built")
    
    if (frontend_dist / "assets").exists():
        assets = list((frontend_dist / "assets").glob("*"))
        print(f"[OK] Frontend assets: {len(assets)} files")
    else:
        print("[MISSING] Frontend assets: MISSING")
        issues.append("Frontend assets missing")
    
    # Check backend
    print("\n4. BACKEND FILES")
    print("-" * 80)
    
    backend_dir = Path("dashboard/backend")
    
    if not check_file_exists(backend_dir / "app.py", "Backend app"):
        issues.append("Backend app.py missing")
    
    if not check_file_exists(backend_dir / "requirements.txt", "Backend requirements"):
        issues.append("Backend requirements.txt missing")
    
    # Check main.js configuration
    print("\n5. MAIN.JS CONFIGURATION ANALYSIS")
    print("-" * 80)
    
    try:
        with open(desktop_dir / "main.js", 'r') as f:
            main_content = f.read()
        
        # Check for critical paths
        if "BACKEND_DIR" in main_content:
            print("[OK] BACKEND_DIR defined")
            if "../dashboard/backend" in main_content:
                print("  -> Points to: ../dashboard/backend")
        
        if "FRONTEND_DIST" in main_content:
            print("[OK] FRONTEND_DIST defined")
            if "../dashboard/frontend/dist" in main_content:
                print("  -> Points to: ../dashboard/frontend/dist")
        
        if "PYTHON_EXE" in main_content:
            print("[OK] PYTHON_EXE defined")
            if "isPackaged" in main_content and "pythonPaths" in main_content:
                print("  -> Uses auto-detection for installed app")
            elif "process.env.PYTHON_PATH" in main_content:
                print("  -> Uses environment variable or defaults to 'python'")
                print("  [WARNING] After installation, 'python' may not be in PATH")
                if "isPackaged" not in main_content:
                    issues.append("Python path not configured for installed app")
        
        if "BACKEND_PORT" in main_content:
            print("[OK] BACKEND_PORT defined")
            if "8000" in main_content:
                print("  -> Port: 8000")
        
    except Exception as e:
        print(f"[ERROR] Could not analyze main.js: {e}")
        issues.append(f"main.js analysis failed: {e}")
    
    # Identify the core issue
    print("\n6. IDENTIFIED ISSUES")
    print("-" * 80)
    
    if issues:
        print(f"Found {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("No issues found in source files")
    
    # Analyze the root cause
    print("\n7. ROOT CAUSE ANALYSIS")
    print("-" * 80)
    
    print("""
The desktop app likely fails after installation because:

1. **Relative Path Issue**:
   - main.js uses relative paths: ../dashboard/backend, ../dashboard/frontend/dist
   - After installation, these paths don't exist
   - The app is installed to Program Files, but backend/frontend are not included

2. **Python Path Issue**:
   - main.js uses process.env.PYTHON_PATH or defaults to 'python'
   - After installation, Python may not be in system PATH
   - The app can't find Python to start the backend

3. **Resource Bundling Issue**:
   - package.json specifies extraResources for backend and agent_memory
   - But paths are relative (../dashboard/backend)
   - electron-builder may not be copying these correctly

4. **Missing Icon**:
   - Config references assets/icon.png and assets/icon.ico
   - These files may not exist in desktop_app/assets/
    """)
    
    # Recommendations
    print("\n8. RECOMMENDED FIXES")
    print("-" * 80)
    
    print("""
Fix #1: Update main.js to use app.getPath() for installed app
  - Detect if running from installation vs development
  - Use electron app.getPath('userData') for resources
  - Bundle Python with the app or detect system Python

Fix #2: Fix package.json extraResources paths
  - Change from: ../dashboard/backend
  - To: Use absolute paths or copy files to desktop_app first

Fix #3: Create assets folder with icons
  - Create desktop_app/assets/icon.png
  - Create desktop_app/assets/icon.ico
  - Or remove icon references if not needed

Fix #4: Bundle Python or detect it properly
  - Option A: Bundle Python with the app (increases size)
  - Option B: Detect Python installation and set PYTHON_PATH
  - Option C: Require Python installation and document it
    """)
    
    return issues

def main():
    """Main diagnostic flow"""
    issues = analyze_desktop_app()
    
    print_header("DIAGNOSTIC COMPLETE")
    
    if issues:
        print(f"Status: [WARNING] {len(issues)} issue(s) found")
        print("\nNext steps:")
        print("1. Review the identified issues above")
        print("2. Apply recommended fixes")
        print("3. Rebuild the desktop app")
        print("4. Test the installation")
    else:
        print("Status: [OK] No critical issues found")
        print("\nThe desktop app source appears correct.")
        print("If the installed app doesn't work, the issue is likely:")
        print("- Python not in PATH after installation")
        print("- Backend resources not bundled correctly")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
