#!/usr/bin/env python3
"""
Comprehensive Electron App Verification
Verifies ALL requirements before building
"""
import sys
import time
import requests
import subprocess
import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000"

def phase1_backend_contract_verification():
    """Phase 1: Verify all backend endpoints return HTTP 200"""
    print("="*80)
    print("PHASE 1: BACKEND CONTRACT VERIFICATION".center(80))
    print("="*80)
    
    endpoints = {
        "Health": "/api/health",
        "State": "/api/state",
        "Learning Insights": "/api/learning/insights",
        "Learning Status": "/api/learning/status",
        "Forensic Report": "/api/forensic/report",
        "Validation Status": "/api/validation/status",
        "Chain NIFTY": "/api/chain/NIFTY",
        "Chain BANKNIFTY": "/api/chain/BANKNIFTY",
        "Chain FINNIFTY": "/api/chain/FINNIFTY",
        "Signal Top": "/api/signal/top",
        "Positions": "/api/positions",
        "PnL": "/api/pnl",
        "QC": "/api/qc",
        "Performance": "/api/perf"
    }
    
    errors = []
    contracts = {}
    
    for name, path in endpoints.items():
        try:
            res = requests.get(f"{BASE_URL}{path}", timeout=5)
            if res.status_code == 200:
                data = res.json()
                contracts[name] = {
                    "path": path,
                    "status": 200,
                    "has_data": bool(data),
                    "keys": list(data.keys()) if isinstance(data, dict) else []
                }
                print(f"[OK] {name}: HTTP 200, Keys: {len(contracts[name]['keys'])}")
            else:
                errors.append(f"{name}: HTTP {res.status_code}")
                print(f"[FAIL] {name}: HTTP {res.status_code}")
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
            print(f"[FAIL] {name}: {e}")
    
    if errors:
        print(f"\n[FAIL] Phase 1: {len(errors)} endpoint errors")
        return False, errors, contracts
    
    print(f"\n[OK] Phase 1: All {len(endpoints)} endpoints return HTTP 200")
    return True, [], contracts

def phase2_electron_connectivity_test():
    """Phase 2: Test Electron ↔ Backend connectivity"""
    print("\n" + "="*80)
    print("PHASE 2: ELECTRON <-> BACKEND CONNECTIVITY".center(80))
    print("="*80)
    print("[INFO] This phase requires Electron app to be running")
    print("[INFO] Run electron_app_connectivity_test.js in DevTools Console")
    print("[INFO] Checking if backend is accessible from localhost...")
    
    # Test if backend is running
    try:
        res = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if res.status_code == 200:
            print("[OK] Backend is running and accessible")
            print("[OK] CORS should be configured (check in Electron DevTools)")
            return True, []
        else:
            print(f"[FAIL] Backend returned HTTP {res.status_code}")
            return False, [f"Backend HTTP {res.status_code}"]
    except requests.exceptions.ConnectionError:
        print("[FAIL] Backend not running - start backend first")
        return False, ["Backend not running"]
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False, [str(e)]

def phase3_frontend_state_binding():
    """Phase 3: Verify frontend components have proper state handling"""
    print("\n" + "="*80)
    print("PHASE 3: FRONTEND STATE BINDING".center(80))
    print("="*80)
    
    components_to_check = {
        "Overview": "dashboard/frontend/src/components/Overview.tsx",
        "Signals": "dashboard/frontend/src/components/Signals.tsx",
        "ControlPlane": "dashboard/frontend/src/components/ControlPlane.tsx"
    }
    
    # First verify EmptyState and ErrorBanner exist
    empty_state_file = ROOT_DIR / "dashboard/frontend/src/components/EmptyState.tsx"
    error_banner_file = ROOT_DIR / "dashboard/frontend/src/components/ErrorBanner.tsx"
    
    if not empty_state_file.exists():
        print("[FAIL] EmptyState.tsx not found")
        return False, ["EmptyState.tsx not found"]
    
    if not error_banner_file.exists():
        print("[FAIL] ErrorBanner.tsx not found")
        return False, ["ErrorBanner.tsx not found"]
    
    print("[OK] EmptyState.tsx exists")
    print("[OK] ErrorBanner.tsx exists")
    
    issues = []
    
    for comp_name, comp_path in components_to_check.items():
        file_path = ROOT_DIR / comp_path
        if not file_path.exists():
            issues.append(f"{comp_name}: File not found")
            print(f"[FAIL] {comp_name}: File not found")
            continue
        
        content = file_path.read_text(encoding='utf-8')
        
        # Check for EmptyState usage
        if "EmptyState" not in content or "from './EmptyState'" not in content and "from '../EmptyState'" not in content:
            issues.append(f"{comp_name}: Does not import/use EmptyState")
            print(f"[FAIL] {comp_name}: Does not use EmptyState component")
        else:
            print(f"[OK] {comp_name}: Uses EmptyState")
        
        # Check for ErrorBanner usage
        if "ErrorBanner" not in content or ("from './ErrorBanner'" not in content and "from '../ErrorBanner'" not in content):
            issues.append(f"{comp_name}: Does not import/use ErrorBanner")
            print(f"[FAIL] {comp_name}: Does not use ErrorBanner component")
        else:
            print(f"[OK] {comp_name}: Uses ErrorBanner")
        
        # Check for loading state
        if "isLoading" not in content and "Loading" not in content:
            issues.append(f"{comp_name}: May be missing loading state")
            print(f"[WARN] {comp_name}: May be missing loading state")
        
        # Check for dangerous null returns (should not exist)
        if "return null" in content or "return <></>" in content:
            # Check if it's in a safe context (commented or conditional)
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if ("return null" in line or "return <></>" in line) and "//" not in line[:max(0, line.find("return"))]:
                    issues.append(f"{comp_name}: May return null at line {i+1}")
                    print(f"[WARN] {comp_name}: May return null at line {i+1}")
    
    if issues:
        critical_issues = [i for i in issues if "Does not" in i or "not found" in i]
        if critical_issues:
            print(f"\n[FAIL] Phase 3: {len(critical_issues)} critical issues")
            return False, critical_issues
        else:
            print(f"\n[WARN] Phase 3: {len(issues)} warnings (acceptable)")
            return True, []
    
    print(f"\n[OK] Phase 3: All {len(components_to_check)} components have proper empty/error states")
    return True, []

def phase4_live_app_verification():
    """Phase 4: Automated Electron visual verification"""
    print("\n" + "="*80)
    print("PHASE 4: AUTOMATED ELECTRON VISUAL VERIFICATION".center(80))
    print("="*80)
    
    e2e_script = ROOT_DIR / "dashboard" / "e2e" / "electron_visual_verify.py"
    
    if not e2e_script.exists():
        print("[FAIL] E2E verification script not found")
        return False, ["electron_visual_verify.py not found"]
    
    print("[INFO] Running automated E2E verification...")
    
    try:
        result = subprocess.run(
            [sys.executable, str(e2e_script)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(ROOT_DIR)
        )
        
        if result.returncode == 0:
            print("[OK] E2E verification passed")
            print("[OK] All UI components verified")
            print("[OK] No blank screens detected")
            return True, []
        else:
            print("[FAIL] E2E verification failed")
            print(result.stdout)
            print(result.stderr)
            return False, ["E2E verification failed - check logs/e2e_electron_verify_*.log"]
    except subprocess.TimeoutExpired:
        print("[FAIL] E2E verification timed out")
        return False, ["E2E verification timed out"]
    except Exception as e:
        print(f"[FAIL] E2E verification error: {e}")
        return False, [str(e)]

def phase5_self_test_verification():
    """Phase 5: Verify self-test component exists"""
    print("\n" + "="*80)
    print("PHASE 5: SELF-TEST COMPONENT".center(80))
    print("="*80)
    
    self_test_file = ROOT_DIR / "dashboard/frontend/src/components/AppSelfTest.tsx"
    overview_file = ROOT_DIR / "dashboard/frontend/src/components/Overview.tsx"
    
    if not self_test_file.exists():
        print("[FAIL] AppSelfTest.tsx not found")
        return False, ["AppSelfTest.tsx not found"]
    
    print("[OK] AppSelfTest.tsx exists")
    
    if overview_file.exists():
        content = overview_file.read_text(encoding='utf-8')
        if "AppSelfTest" in content:
            print("[OK] AppSelfTest imported in Overview.tsx")
        else:
            print("[FAIL] AppSelfTest not imported in Overview.tsx")
            return False, ["AppSelfTest not imported"]
    else:
        print("[WARN] Overview.tsx not found")
    
    print("[OK] Phase 5: Self-test component verified")
    return True, []

def phase6_final_gate(phase_results):
    """Phase 6: Final pre-build gate"""
    print("\n" + "="*80)
    print("PHASE 6: FINAL PRE-BUILD GATE".center(80))
    print("="*80)
    
    requirements = {
        "Backend running": phase_results.get("Phase 1", {}).get("ok", False),
        "All endpoints HTTP 200": phase_results.get("Phase 1", {}).get("ok", False),
        "Frontend components checked": phase_results.get("Phase 3", {}).get("ok", False),
        "Self-test component exists": phase_results.get("Phase 5", {}).get("ok", False),
        "Visual verification done": phase_results.get("Phase 4", {}).get("ok", False)
    }
    
    print("\nREQUIREMENTS STATUS:")
    for req, status in requirements.items():
        status_str = "[OK]" if status else "[FAIL]"
        print(f"  {status_str} {req}")
    
    all_met = all(requirements.values())
    
    if all_met:
        print("\n[OK] All requirements met - READY FOR BUILD")
        print("[SUCCESS] All 6 phases passed - System is production-ready")
    else:
        print("\n[FAIL] Some requirements not met - DO NOT BUILD YET")
        failed = [req for req, status in requirements.items() if not status]
        print(f"[INFO] Failed requirements: {', '.join(failed)}")
        print("[INFO] Complete all phases before building")
    
    return all_met, requirements

def main():
    """Main verification"""
    print("="*80)
    print("COMPREHENSIVE ELECTRON APP VERIFICATION".center(80))
    print("="*80)
    print("\n[RULE] DO NOT BUILD until ALL phases pass")
    print("="*80)
    
    results = {}
    
    # Phase 1
    p1_ok, p1_errors, contracts = phase1_backend_contract_verification()
    results["Phase 1"] = {"ok": p1_ok, "errors": p1_errors, "contracts": contracts}
    
    if not p1_ok:
        print("\n[STOP] Phase 1 failed - fix endpoints before continuing")
        return False
    
    # Phase 2
    p2_ok, p2_errors = phase2_electron_connectivity_test()
    results["Phase 2"] = {"ok": p2_ok, "errors": p2_errors}
    
    # Phase 3
    p3_ok, p3_issues = phase3_frontend_state_binding()
    results["Phase 3"] = {"ok": p3_ok, "issues": p3_issues}
    
    if not p3_ok:
        print("\n[STOP] Phase 3 failed - fix empty states before continuing")
        return False
    
    # Phase 4
    p4_ok, p4_issues = phase4_live_app_verification()
    results["Phase 4"] = {"ok": p4_ok, "issues": p4_issues}
    
    if not p4_ok:
        print("\n[STOP] Phase 4 failed - fix E2E verification issues")
        return False
    
    # Phase 5
    p5_ok, p5_errors = phase5_self_test_verification()
    results["Phase 5"] = {"ok": p5_ok, "errors": p5_errors}
    
    if not p5_ok:
        print("\n[STOP] Phase 5 failed - fix self-test component")
        return False
    
    # Phase 6
    p6_ok, requirements = phase6_final_gate(results)
    results["Phase 6"] = {"ok": p6_ok, "requirements": requirements}
    
    # Final summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY".center(80))
    print("="*80)
    
    for phase, result in results.items():
        status = "[OK]" if result["ok"] else "[FAIL]"
        print(f"{status} {phase}")
    
    all_phases_ok = all(r["ok"] for r in results.values())
    
    if all_phases_ok:
        print("\n[SUCCESS] [OK] ALL PHASES PASSED")
        print("[INFO] You may proceed with build (after visual verification)")
    else:
        print("\n[FAIL] [ERROR] SOME PHASES FAILED")
        print("[RULE] DO NOT BUILD until all phases pass")
    
    return all_phases_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
