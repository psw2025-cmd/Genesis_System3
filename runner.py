"""
System3 Runner CLI - Unified Control Interface
Provides start/stop/status/validation/learning commands for dashboard integration.
ENFORCES PAPER TRADING ONLY - No real orders possible.
"""

import sys
import os
import json
import time
import subprocess
import argparse
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

ROOT_DIR = Path(__file__).parent.absolute()
HEARTBEAT_FILE = ROOT_DIR / "system3_daily_heartbeat.json"
AUTORUN_MASTER = ROOT_DIR / "system3_autorun_master.py"
AUTORUN_MASTER_HARDENED = ROOT_DIR / "system3_autorun_master_hardened.py"
VENV_PYTHON = ROOT_DIR / "venv" / "Scripts" / "python.exe"
PID_FILE = ROOT_DIR / "runner.pid"

# Ensure project root in path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def enforce_dry_run():
    """Ensure all live trading flags are OFF."""
    os.environ["LIVE_TRADING_ENABLED"] = "False"
    os.environ["USE_LIVE_EXECUTION_ENGINE"] = "False"
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = ""
    os.environ["DRY_RUN"] = "True"
    os.environ["HEARTBEAT_CONTINUOUS"] = "1"
    os.environ["HEARTBEAT_INTERVAL_SECONDS"] = "60"


def get_runner_pid() -> Optional[int]:
    """Get PID of running autorun master from PID file or process list."""
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            # Verify process still exists
            if os.name == 'nt':  # Windows
                import subprocess
                result = subprocess.run(
                    ['tasklist', '/FI', f'PID eq {pid}'],
                    capture_output=True, text=True
                )
                if str(pid) in result.stdout:
                    return pid
            else:  # Unix
                try:
                    os.kill(pid, 0)
                    return pid
                except OSError:
                    pass
            PID_FILE.unlink()
        except:
            PID_FILE.unlink()
    return None


def find_autorun_processes() -> list:
    """Find all running autorun master processes."""
    pids = []
    if os.name == 'nt':  # Windows
        try:
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                capture_output=True, text=True
            )
            for line in result.stdout.split('\n')[1:]:
                if 'system3_autorun_master' in line or 'autorun' in line.lower():
                    # Try to extract PID (Windows tasklist format varies)
                    parts = line.split(',')
                    if len(parts) > 1:
                        try:
                            pid = int(parts[1].strip('"'))
                            pids.append(pid)
                        except:
                            pass
        except:
            pass
    else:  # Unix
        try:
            result = subprocess.run(
                ['ps', 'aux'], capture_output=True, text=True
            )
            for line in result.stdout.split('\n'):
                if 'system3_autorun_master' in line:
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            pids.append(int(parts[1]))
                        except:
                            pass
        except Exception:
            pass
    return pids


def cmd_start(refresh: int = 5, live: bool = False):
    """Start autorun master in PAPER mode."""
    print("=" * 70)
    print("SYSTEM3 RUNNER - STARTING AUTORUN (PAPER MODE ONLY)")
    print("=" * 70)
    
    # CRITICAL: Enforce DRY-RUN
    enforce_dry_run()
    print("[OK] DRY-RUN mode enforced (no real orders possible)")
    
    # Check if already running
    existing_pid = get_runner_pid()
    if existing_pid:
        print(f"[WARN] Autorun already running (PID: {existing_pid})")
        print("   Use 'runner.py stop' first, or 'runner.py status' to check")
        return {"success": False, "error": "Already running", "pid": existing_pid}
    
    # Choose autorun script
    autorun_script = AUTORUN_MASTER_HARDENED if AUTORUN_MASTER_HARDENED.exists() else AUTORUN_MASTER
    if not autorun_script.exists():
        return {"success": False, "error": f"Autorun script not found: {autorun_script}"}
    
    # Use venv Python if available
    python_exe = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    
    # Start autorun master
    try:
        if os.name == 'nt':  # Windows
            # Start in new window (detached)
            proc = subprocess.Popen(
                [python_exe, str(autorun_script)],
                cwd=str(ROOT_DIR),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                env=os.environ.copy()
            )
        else:  # Unix
            proc = subprocess.Popen(
                [python_exe, str(autorun_script)],
                cwd=str(ROOT_DIR),
                env=os.environ.copy(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        pid = proc.pid
        PID_FILE.write_text(str(pid))
        
        print(f"[OK] Autorun master started (PID: {pid})")
        print(f"   Script: {autorun_script.name}")
        print(f"   Mode: PAPER (DRY-RUN)")
        print(f"   Refresh: {refresh}s")
        print("   Waiting 5s for initialization...")
        time.sleep(5)
        
        # Verify heartbeat updates
        if HEARTBEAT_FILE.exists():
            hb_age = time.time() - HEARTBEAT_FILE.stat().st_mtime
            if hb_age < 120:
                print(f"[OK] Heartbeat active ({hb_age:.1f}s old)")
            else:
                print(f"[WARN] Heartbeat stale ({hb_age:.1f}s old)")
        
        return {
            "success": True,
            "pid": pid,
            "mode": "PAPER",
            "script": autorun_script.name
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def cmd_stop():
    """Stop autorun master gracefully."""
    print("=" * 70)
    print("SYSTEM3 RUNNER - STOPPING AUTORUN")
    print("=" * 70)
    
    pids = []
    
    # Check PID file
    pid_file_pid = get_runner_pid()
    if pid_file_pid:
        pids.append(pid_file_pid)
    
    # Also check process list
    found_pids = find_autorun_processes()
    for pid in found_pids:
        if pid not in pids:
            pids.append(pid)
    
    if not pids:
        print("[OK] No autorun processes found")
        if PID_FILE.exists():
            PID_FILE.unlink()
        return {"success": True, "stopped": 0}
    
    stopped = 0
    for pid in pids:
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                             capture_output=True, check=False)
            else:  # Unix
                os.kill(pid, signal.SIGTERM)
            print(f"[OK] Stopped process {pid}")
            stopped += 1
        except Exception as e:
            print(f"[WARN] Failed to stop PID {pid}: {e}")
    
    if PID_FILE.exists():
        PID_FILE.unlink()
    
    return {"success": True, "stopped": stopped, "pids": pids}


def cmd_status() -> Dict[str, Any]:
    """Get current runner status from heartbeat."""
    status = {
        "runner": "STOPPED",
        "pid": None,
        "mode": "UNKNOWN",
        "uptime_seconds": None,
        "heartbeat_age_seconds": None,
        "autopilot_running": False,
        "market_status": "UNKNOWN",
        "cycle_count": 0,
        "health_score": None
    }
    
    # Check if process is running
    pid = get_runner_pid()
    if pid:
        status["runner"] = "RUNNING"
        status["pid"] = pid
    
    # Read heartbeat file
    if HEARTBEAT_FILE.exists():
        try:
            hb = json.loads(HEARTBEAT_FILE.read_text())
            hb_age = time.time() - HEARTBEAT_FILE.stat().st_mtime
            status["heartbeat_age_seconds"] = int(hb_age)
            
            # Extract key info
            sys_info = hb.get("system_info", {})
            status["mode"] = sys_info.get("mode", "UNKNOWN")
            status["uptime_seconds"] = sys_info.get("uptime_seconds")
            
            phase_exec = hb.get("phase_execution", {})
            status["autopilot_running"] = phase_exec.get("autopilot_running", False)
            
            market = hb.get("market_awareness", {})
            if market.get("is_market_hours"):
                status["market_status"] = "OPEN"
            elif market.get("is_pre_market"):
                status["market_status"] = "PRE_MARKET"
            elif market.get("is_post_market"):
                status["market_status"] = "POST_MARKET"
            else:
                status["market_status"] = "CLOSED"
            
            ai_ctrl = hb.get("ai_controller", {})
            status["cycle_count"] = ai_ctrl.get("cycle", 0)
            status["health_score"] = ai_ctrl.get("health_score")
            
        except Exception as e:
            status["heartbeat_error"] = str(e)
    
    return status


def cmd_validation():
    """Run validation tests."""
    print("=" * 70)
    print("SYSTEM3 RUNNER - RUNNING VALIDATION")
    print("=" * 70)
    
    # Find validation script
    validation_scripts = [
        ROOT_DIR / "complete_end_to_end_validation.py",
        ROOT_DIR / "comprehensive_e2e_test_all_tabs.py",
        ROOT_DIR / "validation" / "run_all.py"
    ]
    
    validation_script = None
    for script in validation_scripts:
        if script.exists():
            validation_script = script
            break
    
    if not validation_script:
        return {
            "success": False,
            "error": "Validation script not found",
            "tests_passed": 0,
            "total_tests": 0
        }
    
    python_exe = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    
    try:
        result = subprocess.run(
            [python_exe, str(validation_script)],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            timeout=300  # 5 min max
        )
        
        # Try to parse output for test results
        output = result.stdout + result.stderr
        tests_passed = 0
        total_tests = 0
        
        # Look for common patterns
        if "PASS" in output.upper() or "SUCCESS" in output.upper():
            tests_passed = output.upper().count("PASS") + output.upper().count("SUCCESS")
            total_tests = max(tests_passed, output.upper().count("FAIL") + output.upper().count("ERROR"))
        
        return {
            "success": result.returncode == 0,
            "tests_passed": tests_passed,
            "total_tests": total_tests if total_tests > 0 else 1,
            "returncode": result.returncode,
            "output_preview": output[:500]  # First 500 chars
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Validation timed out after 5 minutes",
            "tests_passed": 0,
            "total_tests": 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "tests_passed": 0,
            "total_tests": 0
        }


def cmd_learning():
    """Run learning cycle."""
    print("=" * 70)
    print("SYSTEM3 RUNNER - RUNNING LEARNING CYCLE")
    print("=" * 70)
    
    enforce_dry_run()
    
    # Find learning script
    learning_scripts = [
        ROOT_DIR / "continuous_learning_system.py",
        ROOT_DIR / "learning" / "run_cycle.py"
    ]
    
    learning_script = None
    for script in learning_scripts:
        if script.exists():
            learning_script = script
            break
    
    if not learning_script:
        return {
            "success": False,
            "error": "Learning script not found"
        }
    
    python_exe = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    
    try:
        result = subprocess.run(
            [python_exe, str(learning_script)],
            cwd=str(ROOT_DIR),
            capture_output=True,
            text=True,
            timeout=600  # 10 min max
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "output_preview": (result.stdout + result.stderr)[:500]
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Learning cycle timed out after 10 minutes"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="System3 Runner CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start autorun master")
    start_parser.add_argument("--refresh", type=int, default=5, help="Refresh interval (seconds)")
    start_parser.add_argument("--live", action="store_true", help="(Ignored - always PAPER mode)")
    
    # Stop command
    subparsers.add_parser("stop", help="Stop autorun master")
    
    # Status command
    subparsers.add_parser("status", help="Get runner status")
    
    # Validation command
    subparsers.add_parser("validation", help="Run validation tests")
    
    # Learning command
    subparsers.add_parser("learning", help="Run learning cycle")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    result = None
    if args.command == "start":
        result = cmd_start(refresh=args.refresh, live=args.live)
    elif args.command == "stop":
        result = cmd_stop()
    elif args.command == "status":
        result = cmd_status()
    elif args.command == "validation":
        result = cmd_validation()
    elif args.command == "learning":
        result = cmd_learning()
    
    if result:
        print(json.dumps(result, indent=2))
        return 0 if result.get("success", True) else 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
