#!/usr/bin/env python3
"""
System3 Core Commands Validation Script
Runs critical System3 commands and logs results with strict error detection.
"""

import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path

# Canonical Python path
PYTHON_PATH = r"C:\Genesis_System3\venv\Scripts\python.exe"
PROJECT_ROOT = Path(__file__).parent
LOG_DIR = PROJECT_ROOT / "logs" / "validation"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "agent_run_log.md"

# Error keywords to detect
ERROR_KEYWORDS = [
    "is not recognized",
    "Traceback",
    "Error:",
    "ERROR",
    "Exception",
    "ModuleNotFoundError",
    "ImportError",
]

def log_entry(timestamp, command, output, status, error_summary=None, fix_applied=None):
    """Append log entry to agent_run_log.md"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n## {timestamp}\n\n")
        f.write(f"**Command**: `{command}`\n\n")
        f.write(f"**Status**: {status}\n\n")
        if error_summary:
            f.write(f"**Error Summary**: {error_summary}\n\n")
        if fix_applied:
            f.write(f"**Fix Applied**: {fix_applied}\n\n")
        f.write(f"**Output**:\n```\n{output}\n```\n\n")
        f.write("---\n\n")

def check_errors(output):
    """Check if output contains error keywords"""
    output_lower = output.lower()
    for keyword in ERROR_KEYWORDS:
        if keyword.lower() in output_lower:
            return True, keyword
    return False, None

def run_command(script_path, description):
    """Run a Python script and validate output"""
    print(f"\n{'='*80}")
    print(f"Running: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*80}\n")
    
    if not os.path.exists(script_path):
        error_msg = f"Script not found: {script_path}"
        print(f"[ERROR] {error_msg}")
        log_entry(
            datetime.now().isoformat(),
            f"{PYTHON_PATH} {script_path}",
            error_msg,
            "FAILED",
            error_summary="Script file not found"
        )
        return False
    
    try:
        result = subprocess.run(
            [PYTHON_PATH, script_path],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=300  # 5 minute timeout
        )
        
        output = result.stdout + result.stderr
        has_error, error_keyword = check_errors(output)
        
        if result.returncode != 0 or has_error:
            status = "FAILED"
            error_summary = f"Exit code: {result.returncode}, Error keyword: {error_keyword}"
            print(f"[FAILED] {error_summary}")
            print(f"Output:\n{output}")
            log_entry(
                datetime.now().isoformat(),
                f"{PYTHON_PATH} {script_path}",
                output,
                status,
                error_summary=error_summary
            )
            return False
        else:
            status = "SUCCESS"
            print(f"[SUCCESS] Command completed without errors")
            print(f"Output:\n{output[:500]}...")  # First 500 chars
            log_entry(
                datetime.now().isoformat(),
                f"{PYTHON_PATH} {script_path}",
                output,
                status
            )
            return True
            
    except subprocess.TimeoutExpired:
        error_msg = "Command timed out after 5 minutes"
        print(f"[ERROR] {error_msg}")
        log_entry(
            datetime.now().isoformat(),
            f"{PYTHON_PATH} {script_path}",
            error_msg,
            "FAILED",
            error_summary="Timeout"
        )
        return False
    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        print(f"[ERROR] {error_msg}")
        log_entry(
            datetime.now().isoformat(),
            f"{PYTHON_PATH} {script_path}",
            error_msg,
            "FAILED",
            error_summary=f"Exception: {type(e).__name__}"
        )
        return False

def main():
    """Run all critical commands"""
    print("="*80)
    print("SYSTEM3 CORE COMMANDS VALIDATION")
    print("="*80)
    print(f"Python Path: {PYTHON_PATH}")
    print(f"Log File: {LOG_FILE}")
    print("="*80)
    
    # Initialize log file
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# System3 Agent Run Log\n\n")
            f.write("This log tracks all command executions with strict error detection.\n\n")
            f.write("---\n\n")
    
    # Verify Python path exists
    if not os.path.exists(PYTHON_PATH):
        print(f"[ERROR] Python not found at: {PYTHON_PATH}")
        print("Please verify the virtual environment is set up correctly.")
        return 1
    
    # Test Python version first
    print("\n" + "="*80)
    print("STEP 0: Verify Python Installation")
    print("="*80)
    try:
        result = subprocess.run(
            [PYTHON_PATH, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        version_output = result.stdout.strip()
        print(f"[OK] Python Version: {version_output}")
        log_entry(
            datetime.now().isoformat(),
            f"{PYTHON_PATH} --version",
            version_output,
            "SUCCESS"
        )
    except Exception as e:
        print(f"[ERROR] Failed to get Python version: {e}")
        return 1
    
    # Run critical commands
    commands = [
        ("core/engine/system3_phase221_forward_returns.py", "Phase 221 - Forward Returns"),
        ("core/engine/system3_phase222_signal_edge.py", "Phase 222 - Signal Edge"),
        ("core/engine/angel_pnl_simulator.py", "PnL Simulator"),
    ]
    
    results = []
    for script_path, description in commands:
        success = run_command(script_path, description)
        results.append((description, success))
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    for description, success in results:
        status = "[OK]" if success else "[FAILED]"
        print(f"{status} {description}")
    
    all_passed = all(success for _, success in results)
    if all_passed:
        print("\n[SUCCESS] All critical commands passed validation!")
        return 0
    else:
        print("\n[FAILED] Some commands failed. Check log for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

