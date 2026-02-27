#!/usr/bin/env python3
"""
GENESIS System3 - Monday Pre-Market Automated Sequence
Executes full pre-market validation chain: Options 5→10→1→3→33→Block Test

Safety-first design:
- Checks safety flags BEFORE any operations
- Validates each step before proceeding
- Auto-generates timestamped summary report
- Clear GREEN/YELLOW/RED verdict

Usage:
    python system3_monday_premarket_sequence.py

Expected runtime: 2-4 minutes
Expected output: MONDAY_PREMARKET_EXECUTION_SUMMARY_[timestamp].md
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================
PROJECT_ROOT = Path(__file__).parent
PYTHON_PATH = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_FILE = PROJECT_ROOT / f"MONDAY_PREMARKET_EXECUTION_SUMMARY_{TIMESTAMP}.md"

# ============================================================================
# SAFETY FLAGS TO CHECK
# ============================================================================
SAFETY_CHECKS = [
    ("config/live_trade_config.py", "LIVE_TRADING_ENABLED", False),
    ("config/live_trade_config.py", "USE_LIVE_EXECUTION_ENGINE", False),
    ("config/angel_automation_config.json", "auto_execute_trades", False),
    ("core/config/system3_ultra_safety.json", "AUTO_EXECUTE_TRADES", False),
]

# ============================================================================
# SEQUENCE STEPS
# ============================================================================
SEQUENCE_STEPS = [
    {
        "step": 1,
        "name": "Verify Instruments (Option 5)",
        "command": [str(PYTHON_PATH), "-c", "from core.engine.test_angelone_instruments import main; main()"],
        "expected_patterns": ["Total instruments loaded", "AngelOne instruments test completed"],
        "blocking_errors": ["error", "failed", "exception", "traceback"],
        "max_runtime": 30,
    },
    {
        "step": 2,
        "name": "Train/Verify Models (Option 10)",
        "command": [str(PYTHON_PATH), "-c", "from core.engine.train_angel_models import main; main()"],
        "expected_patterns": ["MODEL ACCURACY", "saved"],
        "blocking_errors": ["training data load failed", "cannot import sklearn", "no module named sklearn"],
        "max_runtime": 60,
    },
    {
        "step": 3,
        "name": "Core Boot / Generate Signals (Option 1)",
        "command": [str(PYTHON_PATH), "-c", "from core.engine.main_launcher import main; main()"],
        "expected_patterns": ["System ready"],
        "blocking_errors": ["error", "failed", "exception"],
        "max_runtime": 30,
    },
    {
        "step": 4,
        "name": "Data Pipeline Test (Option 3)",
        "command": [str(PYTHON_PATH), "-c", "from core.engine.test_data_pipeline import main; main()"],
        "expected_patterns": ["Test completed", "saved at"],
        "blocking_errors": ["error", "failed"],
        "max_runtime": 30,
    },
    {
        "step": 5,
        "name": "Real Data Extractor (Option 33)",
        "command": [str(PYTHON_PATH), "-c", "from core.engine.angel_real_data_extractor import main; main()"],
        "expected_patterns": ["REAL DATA EXTRACTOR"],
        "blocking_errors": [],  # Non-blocking
        "max_runtime": 30,
    },
    {
        "step": 6,
        "name": "Block Test 331-360",
        "command": [str(PYTHON_PATH), "tools/run_phases_331_360_block_test.py"],
        "expected_patterns": ["Test result: PASS", "Block test completed successfully"],
        "blocking_errors": [],  # Exit code + patterns are sufficient; block test logs include benign "ERROR: 0/30"
        "max_runtime": 90,
    },
]

# ============================================================================
# RESULT STORAGE
# ============================================================================
sequence_results = []


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_safety_flags() -> Tuple[bool, List[str]]:
    """Check all safety flags. Return (all_safe, violations)."""
    violations = []
    
    for file_path, flag_name, expected_value in SAFETY_CHECKS:
        full_path = PROJECT_ROOT / file_path
        
        if not full_path.exists():
            violations.append(f"Missing file: {file_path}")
            continue
        
        try:
            if file_path.endswith(".json"):
                with open(full_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                actual_value = data.get(flag_name)
            elif file_path.endswith(".py"):
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                # Simple parsing for Python files
                for line in content.split("\n"):
                    if flag_name in line and "=" in line and not line.strip().startswith("#"):
                        if "True" in line:
                            actual_value = True
                        elif "False" in line:
                            actual_value = False
                        else:
                            actual_value = None
                        break
                else:
                    actual_value = None
            else:
                violations.append(f"Unknown file type: {file_path}")
                continue
            
            if actual_value != expected_value:
                violations.append(
                    f"{flag_name} in {file_path}: expected {expected_value}, got {actual_value}"
                )
        
        except Exception as e:
            violations.append(f"Error checking {file_path}: {e}")
    
    return len(violations) == 0, violations


def run_command(cmd: List[str], timeout: int) -> Tuple[int, str, str]:
    """Run command and return (exit_code, stdout, stderr).

    Force UTF-8 decode with replacement to avoid Windows cp1252 decode errors
    when subprocess output contains non-ASCII bytes.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=PROJECT_ROOT,
            timeout=timeout,
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", f"Exception: {str(e)}"


def check_patterns(text: str, patterns: List[str]) -> Tuple[bool, List[str]]:
    """Check if expected patterns are present. Return (all_found, missing)."""
    text_lower = text.lower()
    missing = [p for p in patterns if p.lower() not in text_lower]
    return len(missing) == 0, missing


def check_errors(text: str, error_keywords: List[str]) -> List[str]:
    """Check for blocking error keywords. Return list of found errors."""
    if not error_keywords:
        return []
    text_lower = text.lower()
    return [kw for kw in error_keywords if kw.lower() in text_lower]


def validate_files_after_sequence() -> Dict[str, any]:
    """Validate critical files exist and have recent timestamps."""
    checks = {}
    
    # Signal files
    signal_files = [
        "storage/live/angel_index_ai_signals.csv",
        "storage/live/angel_index_ai_signals_curated.csv",
        "storage/live/angel_index_ai_signals_with_forward.csv",
    ]
    
    for file_path in signal_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            stat = full_path.stat()
            age_minutes = (datetime.now().timestamp() - stat.st_mtime) / 60
            checks[file_path] = {
                "exists": True,
                "size_bytes": stat.st_size,
                "age_minutes": round(age_minutes, 1),
            }
        else:
            checks[file_path] = {"exists": False}
    
    # Model files
    model_files = [
        "core/models/angel_one/NIFTY_model.pkl",
        "core/models/angel_one/BANKNIFTY_model.pkl",
        "core/models/angel_one/FINNIFTY_model.pkl",
        "core/models/angel_one/MIDCPNIFTY_model.pkl",
        "core/models/angel_one/SENSEX_model.pkl",
    ]
    
    for file_path in model_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            stat = full_path.stat()
            checks[file_path] = {
                "exists": True,
                "size_bytes": stat.st_size,
            }
        else:
            checks[file_path] = {"exists": False}
    
    return checks


def run_sequence() -> str:
    """Execute full pre-market sequence. Return verdict: GREEN/YELLOW/RED."""
    print("=" * 80)
    print("GENESIS SYSTEM3 - MONDAY PRE-MARKET SEQUENCE")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Report file: {REPORT_FILE.name}")
    print()
    
    # Step 0: Safety flag check
    print("[STEP 0] Checking safety flags...")
    all_safe, violations = check_safety_flags()
    
    if not all_safe:
        print("❌ SAFETY FLAG VIOLATIONS DETECTED - ABORTING")
        for v in violations:
            print(f"   - {v}")
        sequence_results.append({
            "step": 0,
            "name": "Safety Flag Check",
            "status": "FAIL",
            "details": violations,
        })
        return "RED"
    else:
        print("✅ All safety flags OK")
        sequence_results.append({
            "step": 0,
            "name": "Safety Flag Check",
            "status": "PASS",
            "details": "All flags verified False",
        })
    
    print()
    
    # Run sequence steps
    for step_config in SEQUENCE_STEPS:
        step_num = step_config["step"]
        step_name = step_config["name"]
        
        print(f"[STEP {step_num}] {step_name}...")
        print(f"  Command: {' '.join(step_config['command'][:3])}...")
        
        exit_code, stdout, stderr = run_command(
            step_config["command"],
            step_config["max_runtime"]
        )
        
        combined_output = (stdout or "") + "\n" + (stderr or "")
        
        # Check for expected patterns
        patterns_found, missing_patterns = check_patterns(
            combined_output,
            step_config["expected_patterns"]
        )
        
        # Check for blocking errors
        found_errors = check_errors(
            combined_output,
            step_config["blocking_errors"]
        )
        
        # Determine status
        # Special case: Step 2 (model training) may exit with code 1 but still succeed
        if exit_code != 0 and step_num != 2:
            status = "FAIL"
            print(f"  ❌ FAIL - Exit code: {exit_code}")
        elif found_errors:
            status = "FAIL"
            print(f"  ❌ FAIL - Blocking errors found: {found_errors}")
        elif not patterns_found:
            status = "WARN"
            print(f"  ⚠️  WARN - Missing expected patterns: {missing_patterns}")
        elif exit_code != 0 and step_num == 2:
            # Model training with non-zero exit but no blocking errors and patterns found
            status = "WARN"
            print(f"  ⚠️  WARN - Exit code {exit_code} but patterns found")
        else:
            status = "PASS"
            print(f"  ✅ PASS")
        
        sequence_results.append({
            "step": step_num,
            "name": step_name,
            "status": status,
            "exit_code": exit_code,
            "patterns_found": patterns_found,
            "missing_patterns": missing_patterns,
            "found_errors": found_errors,
            "stdout_lines": len((stdout or "").split("\n")),
            "stderr_lines": len((stderr or "").split("\n")),
        })
        
        # If blocking failure, abort sequence
        if status == "FAIL" and step_num < 6 and step_num != 4:  # Don't abort on block test or data pipeline (crypto test)
            print()
            print(f"❌ ABORTING SEQUENCE - Step {step_num} failed")
            return "RED"
        
        print()
    
    # Post-sequence file validation
    print("[POST-CHECK] Validating files...")
    file_checks = validate_files_after_sequence()
    
    sequence_results.append({
        "step": 7,
        "name": "File Validation",
        "status": "INFO",
        "details": file_checks,
    })
    
    print()
    
    # Determine final verdict
    statuses = [r["status"] for r in sequence_results if r["step"] > 0]
    
    if "FAIL" in statuses:
        verdict = "RED"
    elif "WARN" in statuses:
        verdict = "YELLOW"
    else:
        verdict = "GREEN"
    
    print("=" * 80)
    print(f"FINAL VERDICT: {verdict}")
    print("=" * 80)
    
    return verdict


def generate_report(verdict: str):
    """Generate markdown report."""
    lines = [
        "# MONDAY PRE-MARKET EXECUTION SUMMARY",
        "",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
        f"**Time:** {datetime.now().strftime('%H:%M:%S')}",
        f"**Verdict:** {verdict}",
        "",
        "---",
        "",
        "## Sequence Results",
        "",
    ]
    
    for result in sequence_results:
        step_num = result["step"]
        step_name = result["name"]
        status = result["status"]
        
        if status == "PASS":
            icon = "✅"
        elif status == "WARN":
            icon = "⚠️"
        elif status == "FAIL":
            icon = "❌"
        else:
            icon = "ℹ️"
        
        lines.append(f"### {icon} Step {step_num}: {step_name}")
        lines.append("")
        lines.append(f"**Status:** {status}")
        lines.append("")
        
        if "exit_code" in result:
            lines.append(f"- Exit code: {result['exit_code']}")
            lines.append(f"- Patterns found: {result['patterns_found']}")
            if result.get("missing_patterns"):
                lines.append(f"- Missing patterns: {result['missing_patterns']}")
            if result.get("found_errors"):
                lines.append(f"- Blocking errors: {result['found_errors']}")
            lines.append(f"- Output lines: stdout={result['stdout_lines']}, stderr={result['stderr_lines']}")
        
        if "details" in result:
            if isinstance(result["details"], dict):
                lines.append("")
                lines.append("**Details:**")
                lines.append("```json")
                lines.append(json.dumps(result["details"], indent=2))
                lines.append("```")
            elif isinstance(result["details"], list):
                lines.append("")
                lines.append("**Details:**")
                for detail in result["details"]:
                    lines.append(f"- {detail}")
            else:
                lines.append(f"- {result['details']}")
        
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## Verdict Explanation",
        "",
        f"**{verdict}**",
        "",
    ])
    
    if verdict == "GREEN":
        lines.append("All steps passed successfully. System ready for market open.")
    elif verdict == "YELLOW":
        lines.append("Some warnings detected (likely data-driven). Review warnings above.")
        lines.append("If warnings are expected (low volume, stale Sunday data), proceed with caution.")
    else:
        lines.append("Critical failures detected. DO NOT proceed to market open.")
        lines.append("Review failed steps above and resolve issues before retrying.")
    
    lines.extend([
        "",
        "---",
        "",
        "## Next Steps",
        "",
    ])
    
    if verdict == "GREEN":
        lines.extend([
            "1. ✅ Safety confirmed - all flags remain False",
            "2. ✅ Models loaded/trained successfully",
            "3. ✅ Signals pipeline operational",
            "4. ✅ Block test 331-360 passed",
            "5. 🚀 Ready to start Option 11 (Live AI Signals Loop) at 09:10 AM",
        ])
    elif verdict == "YELLOW":
        lines.extend([
            "1. Review WARN steps above",
            "2. If WARNs are data-driven (low volume, stale data), proceed",
            "3. Monitor first 30 minutes of Option 11 closely",
            "4. Rerun block test after first live data writes to confirm WARN→OK",
        ])
    else:
        lines.extend([
            "1. ❌ DO NOT start Option 11",
            "2. Review FAIL steps above",
            "3. Fix blocking issues",
            "4. Rerun this script: `python system3_monday_premarket_sequence.py`",
            "5. Only proceed when verdict is GREEN or YELLOW",
        ])
    
    lines.extend([
        "",
        "---",
        "",
        f"**Report generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Script:** system3_monday_premarket_sequence.py",
    ])
    
    # Write report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print()
    print(f"📄 Report saved: {REPORT_FILE.name}")
    print()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point."""
    try:
        verdict = run_sequence()
        generate_report(verdict)
        
        if verdict == "RED":
            sys.exit(1)
        elif verdict == "YELLOW":
            sys.exit(2)
        else:
            sys.exit(0)
    
    except KeyboardInterrupt:
        print()
        print("⚠️  Sequence interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        print()
        print(f"❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
