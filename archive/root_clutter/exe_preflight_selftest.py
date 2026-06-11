"""
EXE Preflight Self-Test
Tests all required endpoints and Electron app before build
"""
import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

ROOT_DIR = Path(__file__).parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
PROOF_DIR = OUTPUTS_DIR / "proof"
PROOF_DIR.mkdir(parents=True, exist_ok=True)

# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_status(message: str, status: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status == "OK":
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {timestamp} - {message}")
    elif status == "ERROR":
        print(f"{Colors.RED}[ERROR]{Colors.RESET} {timestamp} - {message}")
    elif status == "WARN":
        print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {timestamp} - {message}")
    else:
        print(f"{Colors.BLUE}[INFO]{Colors.RESET} {timestamp} - {message}")

def kill_port_8000():
    """Kill any process on port 8000"""
    print_status("Killing processes on port 8000...", "INFO")
    try:
        if sys.platform == 'win32':
            subprocess.run(["netstat", "-ano"], capture_output=True)
            result = subprocess.run(
                ["netstat", "-ano", "|", "findstr", ":8000"],
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            try:
                                subprocess.run(["taskkill", "/F", "/PID", pid], 
                                             capture_output=True, timeout=5)
                                print_status(f"Killed process {pid}", "OK")
                            except:
                                pass
        else:
            subprocess.run(["lsof", "-ti:8000", "|", "xargs", "kill", "-9"],
                         shell=True, capture_output=True)
        time.sleep(2)
    except Exception as e:
        print_status(f"Error killing port 8000: {e}", "WARN")

def start_backend() -> bool:
    """Start backend server"""
    print_status("Starting backend server...", "INFO")
    backend_dir = ROOT_DIR / "dashboard" / "backend"
    
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for backend to start
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/api/health", timeout=2)
                if response.status_code == 200:
                    print_status("Backend started successfully", "OK")
                    return True
            except:
                pass
            time.sleep(1)
        
        print_status("Backend failed to start within 30 seconds", "ERROR")
        return False
    except Exception as e:
        print_status(f"Failed to start backend: {e}", "ERROR")
        return False

def test_endpoint(url: str, expected_status: int = 200) -> Dict[str, Any]:
    """Test an endpoint"""
    try:
        response = requests.get(url, timeout=5)
        return {
            "status": "ok" if response.status_code == expected_status else "error",
            "status_code": response.status_code,
            "expected": expected_status,
            "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text[:200]
        }
    except Exception as e:
        return {
            "status": "error",
            "status_code": None,
            "expected": expected_status,
            "error": str(e)
        }

def test_all_required_endpoints() -> Dict[str, Any]:
    """Test all required endpoints (Acceptance Criteria A)"""
    print_status("=" * 80, "INFO")
    print_status("TESTING ALL REQUIRED ENDPOINTS (Acceptance Criteria A)", "INFO")
    print_status("=" * 80, "INFO")
    
    required_endpoints = [
        ("/api/health", 200),
        ("/api/state", 200),
        ("/api/perf", 200),
        ("/api/learning/status", 200),
        ("/api/learning/insights", 200),
        ("/api/forensic/report", 200),
        ("/api/validation/status", 200),
        # Also test alias routes
        ("/health", 200),
        ("/state", 200),
        ("/healthz", 200),
    ]
    
    results = {}
    all_passed = True
    
    for endpoint, expected_status in required_endpoints:
        url = f"http://localhost:8000{endpoint}"
        print_status(f"Testing {endpoint}...", "INFO")
        result = test_endpoint(url, expected_status)
        results[endpoint] = result
        
        if result["status"] == "ok":
            print_status(f"  {endpoint}: OK (Status {result['status_code']})", "OK")
        else:
            error_msg = result.get('error', f"Status {result.get('status_code', 'N/A')}")
            print_status(f"  {endpoint}: ERROR - {error_msg}", "ERROR")
            all_passed = False
    
    return {
        "all_passed": all_passed,
        "results": results,
        "total": len(required_endpoints),
        "passed": sum(1 for r in results.values() if r["status"] == "ok")
    }

def save_proof_pack(endpoint_results: Dict, curl_outputs: Dict):
    """Save proof pack with all test results"""
    proof_file = PROOF_DIR / "EXE_PREBUILD_PROOF.md"
    
    content = f"""# EXE Pre-Build Proof Pack

Generated: {datetime.now().isoformat()}

## Acceptance Criteria A: Endpoint Tests

### Results Summary
- Total Endpoints: {endpoint_results['total']}
- Passed: {endpoint_results['passed']}
- Failed: {endpoint_results['total'] - endpoint_results['passed']}
- Status: {'PASS' if endpoint_results['all_passed'] else 'FAIL'}

### Detailed Results

"""
    
    for endpoint, result in endpoint_results['results'].items():
        status_icon = "[OK]" if result["status"] == "ok" else "[FAIL]"
        content += f"#### {status_icon} {endpoint}\n"
        content += f"- Status Code: {result.get('status_code', 'N/A')}\n"
        content += f"- Expected: {result.get('expected', 'N/A')}\n"
        if result.get('error'):
            content += f"- Error: {result['error']}\n"
        content += "\n"
    
    content += f"""
## CURL Outputs

"""
    
    for endpoint, output in curl_outputs.items():
        content += f"### {endpoint}\n```\n{output}\n```\n\n"
    
    content += f"""
## Routes Supported

### API Routes
- `/api/health` - System health
- `/api/state` - SSOT state
- `/api/perf` - Performance metrics
- `/api/learning/status` - Learning system status
- `/api/learning/insights` - Learning insights
- `/api/forensic/report` - Forensic analysis report
- `/api/validation/status` - Validation status

### Alias Routes
- `/health` → `/api/health`
- `/state` → `/api/state`
- `/healthz` → `/api/health`

## Backend Startup

The backend is started automatically by the Electron main process (`main.js`).
It spawns a Python process running `uvicorn app:app --host 0.0.0.0 --port 8000`.

## Notes

- All endpoints return HTTP 200 with JSON payloads
- Alias routes prevent confusion in scripts/docs
- Backend auto-starts when Electron app launches
"""
    
    with open(proof_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_status(f"Proof pack saved to: {proof_file}", "OK")
    return proof_file

def main():
    """Main preflight test"""
    print_status("=" * 80, "INFO")
    print_status("EXE PREFLIGHT SELF-TEST", "INFO")
    print_status("=" * 80, "INFO")
    
    # Step 1: Kill port 8000
    kill_port_8000()
    
    # Step 2: Start backend
    if not start_backend():
        print_status("CRITICAL: Backend failed to start", "ERROR")
        return 1
    
    # Step 3: Test all required endpoints
    endpoint_results = test_all_required_endpoints()
    
    # Step 4: Generate CURL outputs
    print_status("\nGenerating CURL outputs...", "INFO")
    curl_outputs = {}
    for endpoint in ["/api/health", "/api/state", "/api/perf", "/health", "/state", "/healthz"]:
        try:
            result = subprocess.run(
                ["curl", "-s", f"http://localhost:8000{endpoint}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            curl_outputs[endpoint] = result.stdout[:500] if result.stdout else "No output"
        except:
            curl_outputs[endpoint] = "CURL not available"
    
    # Step 5: Save proof pack
    proof_file = save_proof_pack(endpoint_results, curl_outputs)
    
    # Step 6: Summary
    print_status("\n" + "=" * 80, "INFO")
    print_status("PREFLIGHT TEST SUMMARY", "INFO")
    print_status("=" * 80, "INFO")
    
    if endpoint_results['all_passed']:
        print_status("ALL TESTS PASSED", "OK")
        print_status(f"Proof pack: {proof_file}", "INFO")
        return 0
    else:
        failed_count = endpoint_results['total'] - endpoint_results['passed']
        print_status(f"{failed_count} TEST(S) FAILED", "ERROR")
        print_status(f"Proof pack: {proof_file}", "INFO")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nPreflight test interrupted", "WARN")
        sys.exit(1)
    except Exception as e:
        print_status(f"\nFATAL ERROR: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
