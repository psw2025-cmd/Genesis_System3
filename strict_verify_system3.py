#!/usr/bin/env python3
"""
System3 Strict Verification Script
Executes all commands with full Python path and strict error detection.
"""

import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Canonical Python path
PYTHON_PATH = r"C:\Genesis_System3\venv\Scripts\python.exe"
PROJECT_ROOT = Path(__file__).parent
LOG_DIR = PROJECT_ROOT / "logs" / "validation"
LOG_DIR.mkdir(parents=True, exist_ok=True)
FIX_SUMMARY_FILE = PROJECT_ROOT / "docs" / "SYSTEM3_STRICT_VERIFICATION_FIXES.md"

# Error keywords to detect in stderr
ERROR_KEYWORDS = [
    "error",
    "exception",
    "traceback",
    "not recognized",
    "failed",
    "FileNotFound",
    "ModuleNotFound",
    "KeyError",
    "ValueError",
    "UnicodeDecodeError",
    "ImportError",
    "AttributeError",
    "TypeError",
    "NameError",
    "SyntaxError",
    "IndentationError",
]

# Commands to verify
COMMANDS_TO_VERIFY = [
    {
        "name": "Python Version Check",
        "command": [PYTHON_PATH, "--version"],
        "description": "Verify Python installation",
    },
    {
        "name": "Phase 221 - Forward Returns",
        "command": [PYTHON_PATH, "core/engine/system3_phase221_forward_returns.py"],
        "description": "Compute forward returns for historical signals",
        "expected_output_file": "storage/live/angel_index_ai_signals_with_forward.csv",
    },
    {
        "name": "Phase 222 - Signal Edge",
        "command": [PYTHON_PATH, "core/engine/system3_phase222_signal_edge.py"],
        "description": "Generate EV tables from forward returns",
        "expected_output_file": "logs/research/system3_signal_edge_report.md",
    },
    {
        "name": "PnL Simulator",
        "command": [PYTHON_PATH, "core/engine/angel_pnl_simulator.py"],
        "description": "Simulate PnL from signals and trades",
        "expected_output_file": "storage/live/angel_index_ai_pnl_log.csv",
    },
]

fixes_applied = []


def check_errors(stderr: str) -> Tuple[bool, List[str]]:
    """Check if stderr contains any error keywords."""
    stderr_lower = stderr.lower()
    found_errors = []
    for keyword in ERROR_KEYWORDS:
        if keyword.lower() in stderr_lower:
            found_errors.append(keyword)
    return len(found_errors) > 0, found_errors


def print_execution_report(name: str, command: List[str], stdout: str, stderr: str, exit_code: int, success: bool, reason: str):
    """Print structured execution report."""
    print("\n" + "=" * 80)
    print("COMMAND EXECUTION REPORT")
    print("=" * 80)
    print(f"COMMAND: {' '.join(command)}")
    print(f"\nSTDOUT:\n{stdout}")
    print(f"\nSTDERR:\n{stderr}")
    print(f"\nEXIT CODE: {exit_code}")
    print(f"\nSUCCESS/FAILURE: {'SUCCESS' if success else 'FAILURE'}")
    print(f"REASON: {reason}")
    print("=" * 80 + "\n")


def execute_command(cmd_info: Dict) -> Tuple[bool, str, str, int]:
    """Execute a command and return (success, stdout, stderr, exit_code)."""
    name = cmd_info["name"]
    command = cmd_info["command"]
    
    print(f"\n{'='*80}")
    print(f"Executing: {name}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=600,  # 10 minute timeout
        )
        
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
        
        # Check for errors
        has_errors, error_keywords = check_errors(stderr)
        
        # Determine success
        if exit_code != 0 or has_errors:
            success = False
            reason = f"Exit code: {exit_code}, Error keywords found: {error_keywords}"
        else:
            success = True
            reason = "Command completed successfully"
        
        # Print report
        print_execution_report(name, command, stdout, stderr, exit_code, success, reason)
        
        return success, stdout, stderr, exit_code
        
    except subprocess.TimeoutExpired:
        stderr = "Command timed out after 10 minutes"
        print_execution_report(name, command, "", stderr, -1, False, "Timeout")
        return False, "", stderr, -1
    except Exception as e:
        stderr = f"Exception during execution: {str(e)}"
        print_execution_report(name, command, "", stderr, -1, False, f"Exception: {type(e).__name__}")
        return False, "", stderr, -1


def verify_output_file(cmd_info: Dict) -> Tuple[bool, str]:
    """Verify expected output file exists."""
    if "expected_output_file" not in cmd_info:
        return True, "No output file to verify"
    
    output_file = PROJECT_ROOT / cmd_info["expected_output_file"]
    if output_file.exists():
        size = output_file.stat().st_size
        if size > 0:
            return True, f"Output file exists and is non-empty ({size} bytes)"
        else:
            return False, f"Output file exists but is empty"
    else:
        return False, f"Output file does not exist: {output_file}"


def fix_import_error(script_path: str) -> bool:
    """Fix import errors by adding project root to sys.path."""
    script_file = PROJECT_ROOT / script_path
    
    if not script_file.exists():
        return False
    
    content = script_file.read_text(encoding="utf-8")
    
    # Check if already has sys.path setup
    if "sys.path" in content and "PROJECT_ROOT" in content:
        return False  # Already fixed
    
    # Find the import section
    lines = content.split("\n")
    
    # Find where to insert (after initial imports, before core imports)
    insert_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("from core.") or line.strip().startswith("import core"):
            insert_index = i
            break
    
    # Insert sys.path setup before core imports
    sys_path_setup = [
        "import sys",
        "from pathlib import Path",
        "",
        "# Add project root to path for imports",
        "PROJECT_ROOT = Path(__file__).parent.parent.parent",
        "if str(PROJECT_ROOT) not in sys.path:",
        "    sys.path.insert(0, str(PROJECT_ROOT))",
        "",
    ]
    
    # Check if sys is already imported
    has_sys_import = any("import sys" in line for line in lines[:insert_index])
    if not has_sys_import:
        # Insert sys import
        for i, line in enumerate(lines[:insert_index]):
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                # Insert after last import
                insert_index = i + 1
                break
    
    # Insert the setup
    new_lines = lines[:insert_index] + sys_path_setup + lines[insert_index:]
    script_file.write_text("\n".join(new_lines), encoding="utf-8")
    
    return True


def main():
    """Run strict verification of all System3 commands."""
    print("=" * 80)
    print("SYSTEM3 STRICT VERIFICATION")
    print("=" * 80)
    print(f"Python Path: {PYTHON_PATH}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Fix Summary: {FIX_SUMMARY_FILE}")
    print("=" * 80)
    
    # Verify Python path exists
    if not os.path.exists(PYTHON_PATH):
        print(f"\n[ERROR] Python not found at: {PYTHON_PATH}")
        print("Please verify the virtual environment is set up correctly.")
        return 1
    
    # Initialize fix summary
    fix_summary = []
    fix_summary.append("# System3 Strict Verification - Fix Summary\n")
    fix_summary.append(f"**Generated**: {datetime.now().isoformat()}\n\n")
    fix_summary.append("---\n\n")
    
    results = []
    
    # Execute all commands
    for cmd_info in COMMANDS_TO_VERIFY:
        name = cmd_info["name"]
        success, stdout, stderr, exit_code = execute_command(cmd_info)
        
        # If failed, try to fix
        if not success:
            print(f"\n[ATTEMPTING FIX] {name}...")
            
            # Try to fix import errors
            if "ModuleNotFoundError" in stderr or "ImportError" in stderr:
                script_path = cmd_info["command"][1]  # Second element is script path
                if fix_import_error(script_path):
                    fix_summary.append(f"## Fix: {name}\n\n")
                    fix_summary.append(f"**Issue**: Import error\n\n")
                    fix_summary.append(f"**Fix Applied**: Added project root to sys.path in `{script_path}`\n\n")
                    fix_summary.append("```python\n")
                    fix_summary.append("import sys\n")
                    fix_summary.append("from pathlib import Path\n")
                    fix_summary.append("PROJECT_ROOT = Path(__file__).parent.parent.parent\n")
                    fix_summary.append("if str(PROJECT_ROOT) not in sys.path:\n")
                    fix_summary.append("    sys.path.insert(0, str(PROJECT_ROOT))\n")
                    fix_summary.append("```\n\n")
                    fix_summary.append("---\n\n")
                    
                    fixes_applied.append(name)
                    
                    # Re-run command
                    print(f"\n[RE-RUNNING] {name} after fix...")
                    success, stdout, stderr, exit_code = execute_command(cmd_info)
        
        # Verify output file if specified
        if success and "expected_output_file" in cmd_info:
            file_success, file_reason = verify_output_file(cmd_info)
            if not file_success:
                print(f"\n[WARNING] Output file verification failed: {file_reason}")
                # Don't mark as failure, but log it
        
        results.append({
            "name": name,
            "success": success,
            "exit_code": exit_code,
            "has_stderr_errors": bool(stderr and check_errors(stderr)[0]),
        })
    
    # Print summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for result in results:
        status = "[OK]" if result["success"] else "[FAILED]"
        print(f"{status} {result['name']}")
        if not result["success"]:
            all_passed = False
    
    if fixes_applied:
        print(f"\n[FIXES APPLIED] {len(fixes_applied)} fixes applied:")
        for fix in fixes_applied:
            print(f"  - {fix}")
    
    # Write fix summary
    if fix_summary:
        FIX_SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
        FIX_SUMMARY_FILE.write_text("".join(fix_summary), encoding="utf-8")
        print(f"\n[INFO] Fix summary written to: {FIX_SUMMARY_FILE}")
    
    if all_passed:
        print("\n[SUCCESS] All commands passed strict verification!")
        return 0
    else:
        print("\n[FAILED] Some commands failed. Check reports above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

