"""
24-Hour Dashboard Monitoring System
Continuous tracking, issue detection, auto-recovery, and improvement
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytz
import requests

sys.stdout.reconfigure(encoding="utf-8")

IST = pytz.timezone("Asia/Kolkata")
MONITOR_LOG = Path(__file__).parent.parent / "logs" / "dashboard_monitor.log"
ISSUES_LOG = Path(__file__).parent.parent / "logs" / "dashboard_issues.log"
IMPROVEMENTS_LOG = Path(__file__).parent.parent / "logs" / "dashboard_improvements.log"
STATUS_FILE = Path(__file__).parent.parent / "outputs" / "dashboard_monitor_status.json"

# Ensure directories exist
MONITOR_LOG.parent.mkdir(parents=True, exist_ok=True)
ISSUES_LOG.parent.mkdir(parents=True, exist_ok=True)
STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


def log_message(message, level="INFO"):
    """Log message to file and console"""
    timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"

    with open(MONITOR_LOG, "a", encoding="utf-8") as f:
        f.write(log_entry)

    color_map = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "IMPROVEMENT": Colors.CYAN,
    }
    color = color_map.get(level, Colors.RESET)
    print(f"{color}[{level}]{Colors.RESET} {message}")


def log_issue(issue_type, description, resolution=""):
    """Log issue to issues log"""
    timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    issue_entry = {
        "timestamp": timestamp,
        "type": issue_type,
        "description": description,
        "resolution": resolution,
        "resolved": bool(resolution),
    }

    issues = []
    if ISSUES_LOG.exists():
        try:
            with open(ISSUES_LOG, "r", encoding="utf-8") as f:
                issues = json.load(f)
        except:
            pass

    issues.append(issue_entry)

    # Keep only last 1000 issues
    if len(issues) > 1000:
        issues = issues[-1000:]

    with open(ISSUES_LOG, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, default=str)


def log_improvement(improvement_type, description, impact=""):
    """Log improvement"""
    timestamp = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    improvement_entry = {"timestamp": timestamp, "type": improvement_type, "description": description, "impact": impact}

    improvements = []
    if IMPROVEMENTS_LOG.exists():
        try:
            with open(IMPROVEMENTS_LOG, "r", encoding="utf-8") as f:
                improvements = json.load(f)
        except:
            pass

    improvements.append(improvement_entry)

    # Keep only last 500 improvements
    if len(improvements) > 500:
        improvements = improvements[-500:]

    with open(IMPROVEMENTS_LOG, "w", encoding="utf-8") as f:
        json.dump(improvements, f, indent=2, default=str)


def check_backend_health():
    """Check backend health"""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {"status": "ok", "data": data, "response_time": response.elapsed.total_seconds()}
        else:
            return {
                "status": "error",
                "error": f"Status code: {response.status_code}",
                "response_time": response.elapsed.total_seconds(),
            }
    except requests.exceptions.ConnectionError:
        return {"status": "error", "error": "Connection refused - Backend not running"}
    except requests.exceptions.Timeout:
        return {"status": "error", "error": "Request timeout"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_frontend_health():
    """Check frontend health"""
    try:
        response = requests.get(FRONTEND_BASE, timeout=5)
        if response.status_code == 200:
            return {"status": "ok", "response_time": response.elapsed.total_seconds()}
        else:
            return {"status": "error", "error": f"Status code: {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "error": "Connection refused - Frontend not running"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_api_endpoints():
    """Check critical API endpoints"""
    endpoints = [
        "/api/health",
        "/api/chain/NIFTY",
        "/api/positions",
        "/api/pnl",
        "/api/alerts/recent",
        "/api/risk/portfolio",
    ]

    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            results[endpoint] = {
                "status": "ok" if response.status_code == 200 else "error",
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }
        except Exception as e:
            results[endpoint] = {"status": "error", "error": str(e)}

    return results


def restart_backend():
    """Restart backend"""
    log_message("Attempting to restart backend...", "WARNING")
    try:
        # Kill existing backend
        subprocess.run(
            ["taskkill", "/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq *uvicorn*"], capture_output=True, timeout=5
        )
        time.sleep(2)

        # Start backend
        backend_dir = Path(__file__).parent.parent / "dashboard" / "backend"
        venv_python = Path(__file__).parent.parent / "venv" / "Scripts" / "python.exe"

        if venv_python.exists():
            subprocess.Popen(
                [str(venv_python), "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
                cwd=str(backend_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:
            subprocess.Popen(
                ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
                cwd=str(backend_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )

        log_message("Backend restart initiated", "INFO")
        time.sleep(8)  # Wait for backend to start

        # Verify
        health = check_backend_health()
        if health["status"] == "ok":
            log_message("Backend restarted successfully", "SUCCESS")
            log_issue("backend_down", "Backend was down", "Auto-restarted successfully")
            return True
        else:
            log_message(f"Backend restart verification failed: {health.get('error')}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Backend restart failed: {e}", "ERROR")
        log_issue("backend_restart_failed", f"Failed to restart backend: {e}")
        return False


def restart_frontend():
    """Restart frontend"""
    log_message("Attempting to restart frontend...", "WARNING")
    try:
        # Kill existing frontend
        subprocess.run(["taskkill", "/F", "/IM", "node.exe"], capture_output=True, timeout=5)
        time.sleep(2)

        # Start frontend
        frontend_dir = Path(__file__).parent.parent / "dashboard" / "frontend"
        subprocess.Popen(["npm", "run", "dev"], cwd=str(frontend_dir), creationflags=subprocess.CREATE_NEW_CONSOLE)

        log_message("Frontend restart initiated", "INFO")
        time.sleep(10)  # Wait for frontend to start

        # Verify
        health = check_frontend_health()
        if health["status"] == "ok":
            log_message("Frontend restarted successfully", "SUCCESS")
            log_issue("frontend_down", "Frontend was down", "Auto-restarted successfully")
            return True
        else:
            log_message(f"Frontend restart verification failed: {health.get('error')}", "ERROR")
            return False
    except Exception as e:
        log_message(f"Frontend restart failed: {e}", "ERROR")
        log_issue("frontend_restart_failed", f"Failed to restart frontend: {e}")
        return False


def detect_and_resolve_issues():
    """Detect and auto-resolve issues"""
    issues_found = []

    # Check backend
    backend_health = check_backend_health()
    if backend_health["status"] != "ok":
        issues_found.append(
            {
                "type": "backend_down",
                "severity": "critical",
                "description": f"Backend is down: {backend_health.get('error')}",
                "action": "restart_backend",
            }
        )

    # Check frontend
    frontend_health = check_frontend_health()
    if frontend_health["status"] != "ok":
        issues_found.append(
            {
                "type": "frontend_down",
                "severity": "critical",
                "description": f"Frontend is down: {frontend_health.get('error')}",
                "action": "restart_frontend",
            }
        )

    # Check API endpoints if backend is up
    if backend_health["status"] == "ok":
        endpoint_results = check_api_endpoints()
        failed_endpoints = [ep for ep, result in endpoint_results.items() if result["status"] != "ok"]

        if failed_endpoints:
            issues_found.append(
                {
                    "type": "api_endpoints_failed",
                    "severity": "high",
                    "description": f"Failed endpoints: {', '.join(failed_endpoints)}",
                    "action": "monitor",
                }
            )

    # Resolve issues
    for issue in issues_found:
        log_issue(issue["type"], issue["description"])

        if issue["action"] == "restart_backend":
            log_message(f"Auto-resolving: {issue['description']}", "WARNING")
            restart_backend()
        elif issue["action"] == "restart_frontend":
            log_message(f"Auto-resolving: {issue['description']}", "WARNING")
            restart_frontend()
        else:
            log_message(f"Issue detected (monitoring): {issue['description']}", "WARNING")

    return issues_found


def check_market_transition():
    """Check if market status changed"""
    try:
        health = check_backend_health()
        if health["status"] == "ok":
            data = health["data"]
            market_status = data.get("market_status", "unknown")
            data_source = data.get("data_source", "unknown")

            return {
                "market_status": market_status,
                "data_source": data_source,
                "timestamp": datetime.now(IST).isoformat(),
            }
    except:
        pass
    return None


def save_status(status_data):
    """Save current status"""
    status_data["last_update"] = datetime.now(IST).isoformat()
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2, default=str)


def monitor_cycle():
    """Single monitoring cycle"""
    cycle_start = datetime.now(IST)

    log_message("=" * 60, "INFO")
    log_message(f"Monitoring Cycle: {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}", "INFO")

    # Check health
    backend_health = check_backend_health()
    frontend_health = check_frontend_health()

    status_data = {
        "cycle_time": cycle_start.isoformat(),
        "backend": backend_health,
        "frontend": frontend_health,
        "market": check_market_transition(),
    }

    # Log status
    if backend_health["status"] == "ok":
        log_message(f"Backend: OK (Response: {backend_health.get('response_time', 0):.2f}s)", "SUCCESS")
        if "data" in backend_health:
            data = backend_health["data"]
            log_message(
                f"  Mode: {data.get('mode')}, Market: {data.get('market_status')}, Source: {data.get('data_source')}",
                "INFO",
            )
    else:
        log_message(f"Backend: ERROR - {backend_health.get('error')}", "ERROR")

    if frontend_health["status"] == "ok":
        log_message(f"Frontend: OK (Response: {frontend_health.get('response_time', 0):.2f}s)", "SUCCESS")
    else:
        log_message(f"Frontend: ERROR - {frontend_health.get('error')}", "ERROR")

    # Detect and resolve issues
    issues = detect_and_resolve_issues()

    if issues:
        log_message(f"Found {len(issues)} issue(s)", "WARNING")
    else:
        log_message("No issues detected", "SUCCESS")

    # Check API endpoints (if backend is up)
    if backend_health["status"] == "ok":
        endpoint_results = check_api_endpoints()
        passed = sum(1 for r in endpoint_results.values() if r["status"] == "ok")
        total = len(endpoint_results)
        log_message(f"API Endpoints: {passed}/{total} passing", "INFO" if passed == total else "WARNING")
        status_data["api_endpoints"] = endpoint_results

    # Save status
    save_status(status_data)

    cycle_duration = (datetime.now(IST) - cycle_start).total_seconds()
    log_message(f"Cycle completed in {cycle_duration:.2f}s", "INFO")
    log_message("=" * 60, "INFO")

    return status_data


def main():
    """Main monitoring loop"""
    log_message("=" * 70, "INFO")
    log_message("24-HOUR DASHBOARD MONITORING SYSTEM STARTED", "INFO")
    log_message("=" * 70, "INFO")
    log_message(f"Start Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    log_message(f"API Base: {API_BASE}", "INFO")
    log_message(f"Frontend Base: {FRONTEND_BASE}", "INFO")
    log_message("", "INFO")

    cycle_count = 0
    check_interval = 30  # Check every 30 seconds

    try:
        while True:
            cycle_count += 1
            log_message(f"Cycle #{cycle_count}", "INFO")

            status = monitor_cycle()

            # Wait before next cycle
            log_message(f"Waiting {check_interval} seconds before next check...", "INFO")
            log_message("", "INFO")
            time.sleep(check_interval)

    except KeyboardInterrupt:
        log_message("", "INFO")
        log_message("Monitoring stopped by user", "WARNING")
    except Exception as e:
        log_message(f"Fatal error in monitoring: {e}", "ERROR")
        log_issue("monitor_fatal_error", f"Monitor crashed: {e}")
        raise


if __name__ == "__main__":
    main()
