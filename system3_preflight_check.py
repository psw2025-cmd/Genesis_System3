#!/usr/bin/env python3
"""
System3 Pre-Flight Check
Comprehensive validation before starting autorun.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime, time as dt_time
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent
PYTHON_PATH = r"C:\Genesis_System3\venv\Scripts\python.exe"

ERROR_KEYWORDS = [
    "error", "exception", "traceback", "failed", "FileNotFound",
    "ModuleNotFound", "KeyError", "ValueError", "UnicodeEncodeError",
    "ImportError", "AttributeError", "TypeError", "NameError",
]

results = []
issues = []
warnings = []


def check_error_keywords(stderr: str) -> List[str]:
    """Check for error keywords in stderr."""
    stderr_lower = stderr.lower()
    found = [kw for kw in ERROR_KEYWORDS if kw.lower() in stderr_lower]
    return found


def run_command_report(cmd: List[str], description: str) -> Dict:
    """Run a command and generate execution report."""
    print(f"\n{'='*80}")
    print(f"Testing: {description}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=300,
        )
        
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
        
        # Check for errors
        error_keywords = check_error_keywords(stderr)
        has_errors = len(error_keywords) > 0
        
        # Determine success
        success = exit_code == 0 and not has_errors
        
        # Print report
        print(f"\n=== COMMAND EXECUTION REPORT ===")
        print(f"COMMAND: {' '.join(cmd)}")
        print(f"EXIT CODE: {exit_code}")
        print(f"STDOUT (first 20 lines):")
        for line in stdout.split('\n')[:20]:
            print(f"  {line}")
        print(f"STDERR (full):")
        print(stderr if stderr else "  (empty)")
        print(f"SUCCESS/FAILURE: {'SUCCESS' if success else 'FAILURE'}")
        if not success:
            reason = f"Exit code: {exit_code}"
            if error_keywords:
                reason += f", Error keywords: {error_keywords}"
            print(f"REASON: {reason}")
        else:
            print(f"REASON: Exit code 0, no error keywords in stderr")
        print("="*80)
        
        return {
            "description": description,
            "command": cmd,
            "success": success,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "error_keywords": error_keywords,
        }
        
    except subprocess.TimeoutExpired:
        return {
            "description": description,
            "command": cmd,
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": "Command timed out after 5 minutes",
            "error_keywords": ["timeout"],
        }
    except Exception as e:
        return {
            "description": description,
            "command": cmd,
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Exception: {str(e)}",
            "error_keywords": ["exception"],
        }


def main():
    """Run comprehensive pre-flight check."""
    print("="*80)
    print("SYSTEM3 PRE-FLIGHT CHECK")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Python Path: {PYTHON_PATH}")
    print("="*80)
    
    # STEP 1: Validate batch file & environment
    print("\n" + "="*80)
    print("STEP 1: VALIDATE BATCH FILE & ENVIRONMENT")
    print("="*80)
    
    # Check batch file
    batch_file = PROJECT_ROOT / "START_AUTORUN_AND_WATCHDOG.bat"
    if batch_file.exists():
        content = batch_file.read_text(encoding="utf-8")
        uses_canonical = PYTHON_PATH.replace("\\", "\\\\") in content or "venv\\Scripts\\python.exe" in content
        has_working_dir = "cd /d C:\\Genesis_System3" in content or "cd /d C:/Genesis_System3" in content
        
        if uses_canonical and has_working_dir:
            print("[OK] Batch file uses canonical Python path and sets working directory")
        else:
            issues.append("Batch file does not use canonical Python path or working directory")
            print("[ISSUE] Batch file path configuration")
    else:
        issues.append("START_AUTORUN_AND_WATCHDOG.bat not found")
        print("[ISSUE] Batch file not found")
    
    # Check required files
    required_files = [
        "system3_autorun_master.py",
        "system3_watchdog.py",
        "system3_daily_heartbeat.json",
    ]
    
    for file_name in required_files:
        file_path = PROJECT_ROOT / file_name
        if file_path.exists():
            print(f"[OK] {file_name} exists")
        else:
            issues.append(f"{file_name} not found")
            print(f"[ISSUE] {file_name} not found")
    
    # Check shutdown flag (optional)
    shutdown_flag = PROJECT_ROOT / "system3_shutdown_flag.json"
    if shutdown_flag.exists():
        print(f"[OK] system3_shutdown_flag.json exists")
    else:
        print("[OK] system3_shutdown_flag.json not found (optional)")
    
    # Test Python version
    python_check = run_command_report(
        [PYTHON_PATH, "--version"],
        "Python Version Check"
    )
    results.append(python_check)
    
    # STEP 2: Check shutdown flag & heartbeat
    print("\n" + "="*80)
    print("STEP 2: CHECK SHUTDOWN FLAG & HEARTBEAT")
    print("="*80)
    
    # Check shutdown flag
    if shutdown_flag.exists():
        try:
            with shutdown_flag.open("r", encoding="utf-8") as f:
                shutdown_data = json.load(f)
            shutdown_date = shutdown_data.get("shutdown_date", "")
            shutdown_time_str = shutdown_data.get("shutdown_time", "")
            
            today = datetime.now().strftime("%Y-%m-%d")
            if shutdown_date == today:
                # Check if time is after 16:00 (yesterday's session done)
                try:
                    shutdown_dt = datetime.fromisoformat(shutdown_time_str)
                    if shutdown_dt.hour >= 16:
                        print(f"[OK] Shutdown flag is from today after 4 PM (yesterday's session done)")
                    else:
                        warnings.append(f"Shutdown flag is from today before 4 PM - may need reset")
                        print(f"[WARN] Shutdown flag is from today before 4 PM")
                except:
                    print(f"[OK] Shutdown flag exists (date: {shutdown_date})")
            else:
                print(f"[OK] Shutdown flag is from {shutdown_date} (not today)")
        except Exception as e:
            warnings.append(f"Error reading shutdown flag: {e}")
            print(f"[WARN] Error reading shutdown flag: {e}")
    
    # Check heartbeat
    heartbeat_file = PROJECT_ROOT / "system3_daily_heartbeat.json"
    if heartbeat_file.exists():
        try:
            with heartbeat_file.open("r", encoding="utf-8") as f:
                heartbeat_data = json.load(f)
            
            timestamp_str = heartbeat_data.get("timestamp", "")
            status = heartbeat_data.get("status", "")
            
            print(f"[OK] Heartbeat file exists")
            print(f"  Timestamp: {timestamp_str}")
            print(f"  Status: {status}")
            
            # Check if status is "running" but no process
            if status == "running":
                # Try to check if process is actually running
                try:
                    import psutil
                    master_running = any("system3_autorun_master.py" in p.cmdline() for p in psutil.process_iter(['pid', 'name', 'cmdline']) if p.info.get('cmdline'))
                    if not master_running:
                        warnings.append("Heartbeat says 'running' but master process not found")
                        print("[WARN] Heartbeat says 'running' but master process not found")
                except:
                    pass
        except Exception as e:
            warnings.append(f"Error reading heartbeat: {e}")
            print(f"[WARN] Error reading heartbeat: {e}")
    else:
        issues.append("system3_daily_heartbeat.json not found")
        print("[ISSUE] Heartbeat file not found")
    
    # STEP 3: Core pipeline smoke tests
    print("\n" + "="*80)
    print("STEP 3: CORE PIPELINE SMOKE TESTS")
    print("="*80)
    
    # Phase 221
    phase221_result = run_command_report(
        [PYTHON_PATH, "core/engine/system3_phase221_forward_returns.py"],
        "Phase 221 - Forward Returns"
    )
    results.append(phase221_result)
    
    # Check output file
    output_221 = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals_with_forward.csv"
    if output_221.exists() and output_221.stat().st_size > 0:
        print(f"[OK] Phase 221 output file exists and is non-empty")
    else:
        if phase221_result["success"]:
            warnings.append("Phase 221 output file missing or empty")
            print("[WARN] Phase 221 output file missing or empty")
        else:
            issues.append("Phase 221 output file missing or empty")
            print("[ISSUE] Phase 221 output file missing or empty")
    
    # Phase 222
    phase222_result = run_command_report(
        [PYTHON_PATH, "core/engine/system3_phase222_signal_edge.py"],
        "Phase 222 - Signal Edge"
    )
    results.append(phase222_result)
    
    # Check output file
    output_222 = PROJECT_ROOT / "logs" / "research" / "system3_signal_edge_report.md"
    if output_222.exists():
        print(f"[OK] Phase 222 output file exists")
    else:
        if phase222_result["success"]:
            warnings.append("Phase 222 output file missing")
            print("[WARN] Phase 222 output file missing")
        else:
            issues.append("Phase 222 output file missing")
            print("[ISSUE] Phase 222 output file missing")
    
    # PnL Simulator
    pnl_result = run_command_report(
        [PYTHON_PATH, "core/engine/angel_pnl_simulator.py"],
        "PnL Simulator"
    )
    results.append(pnl_result)
    
    # Check output file
    output_pnl = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_pnl_log.csv"
    if output_pnl.exists():
        print(f"[OK] PnL simulator output file exists")
    else:
        if "No trades to evaluate" in pnl_result.get("stdout", ""):
            print("[OK] PnL simulator: No trades to evaluate (expected)")
        else:
            warnings.append("PnL simulator output file missing")
            print("[WARN] PnL simulator output file missing")
    
    # STEP 4: Check config, safety & DRY-RUN
    print("\n" + "="*80)
    print("STEP 4: CHECK CONFIG, SAFETY & DRY-RUN")
    print("="*80)
    
    # Search for config files
    config_files = [
        PROJECT_ROOT / "config" / "config.json",
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "config" / "system3_config.json",
    ]
    
    dry_run_confirmed = False
    for config_file in config_files:
        if config_file.exists():
            print(f"[INFO] Found config file: {config_file}")
            try:
                if config_file.suffix == ".json":
                    with config_file.open("r", encoding="utf-8") as f:
                        config_data = json.load(f)
                    # Check for DRY-RUN flags
                    if "LIVE_TRADING_ENABLED" in str(config_data) or "DRY_RUN" in str(config_data):
                        print(f"  Checking DRY-RUN flags...")
            except:
                pass
    
    # Check autorun master for DRY-RUN flags
    master_file = PROJECT_ROOT / "system3_autorun_master.py"
    if master_file.exists():
        master_content = master_file.read_text(encoding="utf-8")
        if "DRY-RUN" in master_content or "LIVE_TRADING_ENABLED" in master_content:
            # Check if it's set to False/disabled
            if "LIVE_TRADING_ENABLED" in master_content:
                if "LIVE_TRADING_ENABLED = False" in master_content or "LIVE_TRADING_ENABLED: False" in master_content:
                    print("[OK] LIVE_TRADING_ENABLED is False in autorun master")
                    dry_run_confirmed = True
                else:
                    issues.append("LIVE_TRADING_ENABLED may be True in autorun master")
                    print("[ISSUE] LIVE_TRADING_ENABLED may be enabled")
            else:
                print("[OK] DRY-RUN mode mentioned in autorun master")
                dry_run_confirmed = True
    
    # Check validation docs
    validation_docs = [
        "docs/SYSTEM3_CORE_STABLE_CONFIRMED.md",
        "docs/SYSTEM3_PRE_AUTORUN_VALIDATION_COMPLETE.md",
        "docs/SYSTEM3_STRICT_VERIFICATION_COMPLETE.md",
        "docs/SYSTEM3_FORENSIC_FIX_AND_VALIDATION_REPORT.md",
    ]
    
    for doc_path in validation_docs:
        doc_file = PROJECT_ROOT / doc_path
        if doc_file.exists():
            print(f"[OK] {doc_path} exists")
        else:
            warnings.append(f"{doc_path} not found")
            print(f"[WARN] {doc_path} not found")
    
    # STEP 5: Final decision
    print("\n" + "="*80)
    print("STEP 5: FINAL DECISION")
    print("="*80)
    
    # Count failures
    command_failures = [r for r in results if not r["success"]]
    
    print("\nPRE-MARKET PREFLIGHT SUMMARY")
    print("-" * 80)
    
    # Batch file & paths
    batch_ok = batch_file.exists() and uses_canonical and has_working_dir
    print(f"- Batch file & paths: {'OK' if batch_ok else 'ISSUE'}")
    if not batch_ok:
        print(f"  Details: {', '.join([i for i in issues if 'batch' in i.lower() or 'START_AUTORUN' in i])}")
    
    # Shutdown flag & heartbeat
    shutdown_ok = not any("shutdown" in i.lower() for i in issues)
    heartbeat_ok = heartbeat_file.exists()
    print(f"- Shutdown flag & heartbeat: {'OK' if shutdown_ok and heartbeat_ok else 'ISSUE'}")
    if not shutdown_ok or not heartbeat_ok:
        print(f"  Details: {', '.join([i for i in issues if 'shutdown' in i.lower() or 'heartbeat' in i.lower()])}")
    
    # Phase 221
    phase221_ok = phase221_result["success"]
    print(f"- Phase 221: {'OK' if phase221_ok else 'ISSUE'}")
    if not phase221_ok:
        print(f"  Details: Exit code {phase221_result['exit_code']}, Errors: {phase221_result['error_keywords']}")
    
    # Phase 222
    phase222_ok = phase222_result["success"]
    print(f"- Phase 222: {'OK' if phase222_ok else 'ISSUE'}")
    if not phase222_ok:
        print(f"  Details: Exit code {phase222_result['exit_code']}, Errors: {phase222_result['error_keywords']}")
    
    # PnL simulator
    pnl_ok = pnl_result["success"]
    print(f"- PnL simulator: {'OK' if pnl_ok else 'ISSUE'}")
    if not pnl_ok:
        print(f"  Details: Exit code {pnl_result['exit_code']}, Errors: {pnl_result['error_keywords']}")
    
    # Safety & DRY-RUN
    safety_ok = dry_run_confirmed or len([i for i in issues if "LIVE_TRADING" in i]) == 0
    print(f"- Safety & DRY-RUN: {'OK' if safety_ok else 'ISSUE'}")
    if not safety_ok:
        print(f"  Details: DRY-RUN not confirmed")
    
    # Final verdict
    all_ok = (
        batch_ok and
        shutdown_ok and heartbeat_ok and
        phase221_ok and phase222_ok and pnl_ok and
        safety_ok and
        len(command_failures) == 0
    )
    
    print("\n" + "="*80)
    if all_ok:
        print("FINAL VERDICT: ✅ READY TO START START_AUTORUN_AND_WATCHDOG.bat")
        print("="*80)
        print("\nAll checks passed. System is ready for today's market session.")
    else:
        print("FINAL VERDICT: ❌ NOT SAFE TO START")
        print("="*80)
        print("\nIssues found that must be resolved:")
        for issue in issues:
            print(f"  - {issue}")
        for failure in command_failures:
            print(f"  - {failure['description']} failed: {failure.get('stderr', 'Unknown error')[:100]}")
    
    if warnings:
        print("\nWarnings (non-blocking):")
        for warning in warnings:
            print(f"  - {warning}")
    
    # Manual actions
    manual_actions = []
    if shutdown_flag.exists():
        try:
            with shutdown_flag.open("r", encoding="utf-8") as f:
                shutdown_data = json.load(f)
            shutdown_date = shutdown_data.get("shutdown_date", "")
            today = datetime.now().strftime("%Y-%m-%d")
            if shutdown_date == today:
                shutdown_time_str = shutdown_data.get("shutdown_time", "")
                try:
                    shutdown_dt = datetime.fromisoformat(shutdown_time_str)
                    if shutdown_dt.hour < 16:
                        manual_actions.append("Delete/reset system3_shutdown_flag.json (stale from today before 4 PM)")
                except:
                    pass
        except:
            pass
    
    if manual_actions:
        print("\nManual actions required before starting:")
        for action in manual_actions:
            print(f"  - {action}")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

