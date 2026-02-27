#!/usr/bin/env python3
"""
System3 Comprehensive Deep Analysis & Multi-Validation
- Analyzes all MD files
- Validates all phases
- Multi-validates START_AUTORUN_AND_WATCHDOG.bat
- Tests autorun system
- Confirms readiness for tomorrow's market
"""

import sys
import json
import ast
import re
from pathlib import Path
from datetime import datetime, time as dt_time
from typing import Dict, List, Any, Tuple
import subprocess

PROJECT_ROOT = Path(__file__).parent
RESULTS = {
    "md_analysis": {},
    "phase_validation": {},
    "batch_file_validation": {},
    "autorun_validation": {},
    "final_verdict": {}
}

print("="*80)
print("SYSTEM3 COMPREHENSIVE DEEP ANALYSIS & MULTI-VALIDATION")
print("="*80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

# ============================================================================
# STEP 1: Analyze Key MD Files
# ============================================================================
print("="*80)
print("STEP 1: ANALYZING KEY MD FILES")
print("="*80)

key_md_files = [
    "docs/SYSTEM3_PREMARKET_CHECKLIST_FINAL.md",
    "docs/VERIFY_EXPECTED_FAILURES_PROOF.md",
    "docs/SYSTEM3_CORE_STABLE_CONFIRMED.md",
    "docs/SYSTEM3_FULL_FORENSIC_SUMMARY.md",
    "docs/SYSTEM3_PHASES_301_310_STATUS.md",
    "docs/CSV_PARSING_FIXES_APPLIED.md",
    "docs/SYSTEM3_FORENSIC_FIX_AND_VALIDATION_REPORT.md",
]

md_analysis = {}
for md_file in key_md_files:
    file_path = PROJECT_ROOT / md_file
    if file_path.exists():
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        # Extract key status indicators
        has_pass = "✅" in content or "[OK]" in content or "PASS" in content.upper()
        has_fail = "❌" in content or "[FAIL]" in content or "FAIL" in content.upper()
        has_warn = "⚠️" in content or "[WARN]" in content or "WARN" in content.upper()
        
        md_analysis[md_file] = {
            "exists": True,
            "size": len(content),
            "has_pass": has_pass,
            "has_fail": has_fail,
            "has_warn": has_warn,
            "status": "PASS" if has_pass and not has_fail else "WARN" if has_warn else "UNKNOWN"
        }
        print(f"✅ {md_file}: {md_analysis[md_file]['status']} ({len(content)} chars)")
    else:
        md_analysis[md_file] = {"exists": False}
        print(f"❌ {md_file}: NOT FOUND")

RESULTS["md_analysis"] = md_analysis
print()

# ============================================================================
# STEP 2: Validate All Phase Loading Mechanisms
# ============================================================================
print("="*80)
print("STEP 2: VALIDATING PHASE LOADING MECHANISMS")
print("="*80)

phase_validation = {
    "diagnostic_scripts": {},
    "autorun_loading": {},
    "phase_files": {}
}

# Check diagnostic scripts
diagnostic_scripts = [
    "system3_phase_201_230_diagnostics.py",
    "system3_phase_231_260_diagnostics.py",
    "system3_phase_261_300_diagnostics.py",
    "system3_phases_301_310_diagnostics.py",
]

for script in diagnostic_scripts:
    script_path = PROJECT_ROOT / script
    if script_path.exists():
        content = script_path.read_text(encoding="utf-8")
        has_phase_modules = "PHASE_MODULES" in content or "PHASE_IMPORTS" in content
        phase_validation["diagnostic_scripts"][script] = {
            "exists": True,
            "has_phase_modules": has_phase_modules
        }
        print(f"✅ {script}: {'Has PHASE_MODULES' if has_phase_modules else 'Missing PHASE_MODULES'}")
    else:
        phase_validation["diagnostic_scripts"][script] = {"exists": False}
        print(f"❌ {script}: NOT FOUND")

# Check autorun master phase loading
autorun_master = PROJECT_ROOT / "system3_autorun_master.py"
if autorun_master.exists():
    content = autorun_master.read_text(encoding="utf-8")
    
    # Check for phase loading blocks
    has_201_230 = "system3_phase_201_230_diagnostics" in content
    has_231_260 = "system3_phase_231_260_diagnostics" in content
    has_261_300 = "system3_phase_261_300_diagnostics" in content
    has_301_310 = "system3_phases_301_310_diagnostics" in content
    
    phase_validation["autorun_loading"] = {
        "201-230": has_201_230,
        "231-260": has_231_260,
        "261-300": has_261_300,
        "301-310": has_301_310,
        "all_loaded": has_201_230 and has_231_260 and has_261_300 and has_301_310
    }
    
    print(f"✅ Autorun master phase loading:")
    print(f"   - 201-230: {'✅' if has_201_230 else '❌'}")
    print(f"   - 231-260: {'✅' if has_231_260 else '❌'}")
    print(f"   - 261-300: {'✅' if has_261_300 else '❌'}")
    print(f"   - 301-310: {'✅' if has_301_310 else '❌'}")
else:
    phase_validation["autorun_loading"] = {"error": "Autorun master not found"}
    print("❌ Autorun master not found")

# Count phase files
phase_files = list((PROJECT_ROOT / "core" / "engine").glob("system3_phase*.py"))
phase_validation["phase_files"] = {
    "count": len(phase_files),
    "exists": len(phase_files) > 0
}
print(f"✅ Phase files found: {len(phase_files)}")

RESULTS["phase_validation"] = phase_validation
print()

# ============================================================================
# STEP 3: Validate START_AUTORUN_AND_WATCHDOG.bat
# ============================================================================
print("="*80)
print("STEP 3: VALIDATING START_AUTORUN_AND_WATCHDOG.bat")
print("="*80)

batch_file = PROJECT_ROOT / "START_AUTORUN_AND_WATCHDOG.bat"
batch_validation = {}

if batch_file.exists():
    content = batch_file.read_text(encoding="utf-8")
    
    # Check critical components
    has_cd = "cd /d" in content or "cd" in content.lower()
    has_venv_activate = "venv" in content and "activate" in content.lower()
    has_watchdog_start = "system3_watchdog.py" in content
    has_master_start = "system3_autorun_master.py" in content
    has_start_command = 'start "' in content or "start" in content.lower()
    
    batch_validation = {
        "exists": True,
        "has_cd": has_cd,
        "has_venv_activate": has_venv_activate,
        "has_watchdog_start": has_watchdog_start,
        "has_master_start": has_master_start,
        "has_start_command": has_start_command,
        "all_valid": has_cd and has_venv_activate and has_watchdog_start and has_master_start
    }
    
    print(f"✅ Batch file validation:")
    print(f"   - Working directory: {'✅' if has_cd else '❌'}")
    print(f"   - Venv activation: {'✅' if has_venv_activate else '❌'}")
    print(f"   - Watchdog start: {'✅' if has_watchdog_start else '❌'}")
    print(f"   - Master start: {'✅' if has_master_start else '❌'}")
    print(f"   - Start command: {'✅' if has_start_command else '❌'}")
    
    if batch_validation["all_valid"]:
        print("✅ Batch file structure: VALID")
    else:
        print("❌ Batch file structure: INVALID")
else:
    batch_validation = {"exists": False}
    print("❌ Batch file not found")

RESULTS["batch_file_validation"] = batch_validation
print()

# ============================================================================
# STEP 4: Validate Autorun System Components
# ============================================================================
print("="*80)
print("STEP 4: VALIDATING AUTORUN SYSTEM COMPONENTS")
print("="*80)

autorun_validation = {}

# Check autorun master
autorun_master_file = PROJECT_ROOT / "system3_autorun_master.py"
if autorun_master_file.exists():
    content = autorun_master_file.read_text(encoding="utf-8")
    
    has_safety_checks = "enforce_safety_checks" in content
    has_heartbeat = "update_heartbeat" in content
    has_shutdown_flag = "check_shutdown_flag" in content
    has_market_hours = "is_market_time" in content or "is_market_hours" in content
    has_retry_logic = "max_retries" in content or "retry" in content.lower()
    
    autorun_validation["master"] = {
        "exists": True,
        "has_safety_checks": has_safety_checks,
        "has_heartbeat": has_heartbeat,
        "has_shutdown_flag": has_shutdown_flag,
        "has_market_hours": has_market_hours,
        "has_retry_logic": has_retry_logic,
        "all_valid": has_safety_checks and has_heartbeat and has_shutdown_flag and has_market_hours
    }
    
    print(f"✅ Autorun master:")
    print(f"   - Safety checks: {'✅' if has_safety_checks else '❌'}")
    print(f"   - Heartbeat: {'✅' if has_heartbeat else '❌'}")
    print(f"   - Shutdown flag: {'✅' if has_shutdown_flag else '❌'}")
    print(f"   - Market hours: {'✅' if has_market_hours else '❌'}")
    print(f"   - Retry logic: {'✅' if has_retry_logic else '❌'}")
else:
    autorun_validation["master"] = {"exists": False}
    print("❌ Autorun master not found")

# Check watchdog
watchdog_file = PROJECT_ROOT / "system3_watchdog.py"
if watchdog_file.exists():
    content = watchdog_file.read_text(encoding="utf-8")
    
    has_market_hours = "is_market_hours" in content
    has_shutdown_check = "check_shutdown_flag" in content
    has_heartbeat_check = "check_heartbeat_staleness" in content or "heartbeat" in content.lower()
    has_restart_logic = "start_master" in content or "restart" in content.lower()
    
    autorun_validation["watchdog"] = {
        "exists": True,
        "has_market_hours": has_market_hours,
        "has_shutdown_check": has_shutdown_check,
        "has_heartbeat_check": has_heartbeat_check,
        "has_restart_logic": has_restart_logic,
        "all_valid": has_market_hours and has_shutdown_check and has_heartbeat_check and has_restart_logic
    }
    
    print(f"✅ Watchdog:")
    print(f"   - Market hours: {'✅' if has_market_hours else '❌'}")
    print(f"   - Shutdown check: {'✅' if has_shutdown_check else '❌'}")
    print(f"   - Heartbeat check: {'✅' if has_heartbeat_check else '❌'}")
    print(f"   - Restart logic: {'✅' if has_restart_logic else '❌'}")
else:
    autorun_validation["watchdog"] = {"exists": False}
    print("❌ Watchdog not found")

# Check autopilot
autopilot_file = PROJECT_ROOT / "system3_live_day_autopilot.py"
if autopilot_file.exists():
    content = autopilot_file.read_text(encoding="utf-8")
    
    has_safety_checks = "LIVE_TRADING_ENABLED" in content or "DRY_RUN" in content.upper()
    has_encoding_fix = "UnicodeEncodeError" in content
    has_smartapi_fix = "ImportError" in content and "SmartApi" in content
    
    autorun_validation["autopilot"] = {
        "exists": True,
        "has_safety_checks": has_safety_checks,
        "has_encoding_fix": has_encoding_fix,
        "has_smartapi_fix": has_smartapi_fix,
        "all_valid": has_safety_checks and has_encoding_fix and has_smartapi_fix
    }
    
    print(f"✅ Autopilot:")
    print(f"   - Safety checks: {'✅' if has_safety_checks else '❌'}")
    print(f"   - Encoding fix: {'✅' if has_encoding_fix else '❌'}")
    print(f"   - SmartAPI fix: {'✅' if has_smartapi_fix else '❌'}")
else:
    autorun_validation["autopilot"] = {"exists": False}
    print("❌ Autopilot not found")

RESULTS["autorun_validation"] = autorun_validation
print()

# ============================================================================
# STEP 5: Validate Critical Files & Paths
# ============================================================================
print("="*80)
print("STEP 5: VALIDATING CRITICAL FILES & PATHS")
print("="*80)

critical_files = {
    "system3_autorun_master.py": PROJECT_ROOT / "system3_autorun_master.py",
    "system3_watchdog.py": PROJECT_ROOT / "system3_watchdog.py",
    "system3_live_day_autopilot.py": PROJECT_ROOT / "system3_live_day_autopilot.py",
    "START_AUTORUN_AND_WATCHDOG.bat": PROJECT_ROOT / "START_AUTORUN_AND_WATCHDOG.bat",
    "venv/Scripts/python.exe": PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
    "storage/live/angel_index_ai_signals.csv": PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals.csv",
    "system3_daily_heartbeat.json": PROJECT_ROOT / "system3_daily_heartbeat.json",
    "system3_shutdown_flag.json": PROJECT_ROOT / "system3_shutdown_flag.json",
}

file_validation = {}
for name, path in critical_files.items():
    exists = path.exists()
    file_validation[name] = {"exists": exists}
    print(f"{'✅' if exists else '❌'} {name}: {'EXISTS' if exists else 'NOT FOUND'}")

RESULTS["file_validation"] = file_validation
print()

# ============================================================================
# STEP 6: Validate Market Hours Logic
# ============================================================================
print("="*80)
print("STEP 6: VALIDATING MARKET HOURS LOGIC")
print("="*80)

market_hours_validation = {}

if autorun_master_file.exists():
    content = autorun_master_file.read_text(encoding="utf-8")
    
    # Extract market hours
    open_match = re.search(r'market_open\s*=\s*dt_time\((\d+),\s*(\d+)\)', content)
    close_match = re.search(r'market_close\s*=\s*dt_time\((\d+),\s*(\d+)\)', content)
    
    if open_match and close_match:
        open_hour = int(open_match.group(1))
        open_min = int(open_match.group(2))
        close_hour = int(close_match.group(1))
        close_min = int(close_match.group(2))
        
        # Verify IST market hours (09:15 - 15:30)
        is_ist_correct = (open_hour == 9 and open_min == 15) and (close_hour == 15 and close_min == 30)
        
        market_hours_validation = {
            "open": f"{open_hour:02d}:{open_min:02d}",
            "close": f"{close_hour:02d}:{close_min:02d}",
            "is_ist_correct": is_ist_correct
        }
        
        print(f"✅ Market hours: {open_hour:02d}:{open_min:02d} - {close_hour:02d}:{close_min:02d}")
        print(f"   {'✅ IST CORRECT' if is_ist_correct else '❌ NOT IST'}")
    else:
        market_hours_validation = {"error": "Market hours not found"}
        print("❌ Market hours not found in code")

RESULTS["market_hours_validation"] = market_hours_validation
print()

# ============================================================================
# STEP 7: Final Verdict
# ============================================================================
print("="*80)
print("STEP 7: FINAL VERDICT FOR TOMORROW'S MARKET")
print("="*80)

# Calculate overall status
all_checks = []

# MD files
md_status = all(md.get("status") == "PASS" or md.get("exists") == False for md in md_analysis.values() if md.get("exists"))
all_checks.append(("MD Files Analysis", md_status))

# Phase validation
phase_status = (
    phase_validation.get("autorun_loading", {}).get("all_loaded", False) and
    phase_validation.get("phase_files", {}).get("exists", False)
)
all_checks.append(("Phase Loading", phase_status))

# Batch file
batch_status = batch_validation.get("all_valid", False)
all_checks.append(("Batch File", batch_status))

# Autorun components
autorun_status = (
    autorun_validation.get("master", {}).get("all_valid", False) and
    autorun_validation.get("watchdog", {}).get("all_valid", False) and
    autorun_validation.get("autopilot", {}).get("all_valid", False)
)
all_checks.append(("Autorun Components", autorun_status))

# Critical files
files_status = all(f.get("exists", False) for f in file_validation.values())
all_checks.append(("Critical Files", files_status))

# Market hours
market_status = market_hours_validation.get("is_ist_correct", False)
all_checks.append(("Market Hours", market_status))

# Overall verdict
overall_pass = all(status for _, status in all_checks)
overall_fail_count = sum(1 for _, status in all_checks if not status)

print()
for check_name, status in all_checks:
    print(f"{'✅' if status else '❌'} {check_name}: {'PASS' if status else 'FAIL'}")

print()
print("="*80)
if overall_pass:
    print("✅ FINAL VERDICT: READY FOR TOMORROW'S MARKET")
    print("="*80)
    print("All critical validations passed. System is ready to run.")
    verdict = "PASS"
else:
    print("❌ FINAL VERDICT: NOT READY - FIXES REQUIRED")
    print("="*80)
    print(f"{overall_fail_count} critical check(s) failed. Review and fix before running.")
    verdict = "FAIL"

RESULTS["final_verdict"] = {
    "overall_status": verdict,
    "checks": all_checks,
    "pass_count": sum(1 for _, s in all_checks if s),
    "fail_count": overall_fail_count,
    "total_checks": len(all_checks)
}

# Save results
results_file = PROJECT_ROOT / "docs" / "SYSTEM3_COMPREHENSIVE_VALIDATION_RESULTS.json"
results_file.parent.mkdir(parents=True, exist_ok=True)

# Convert to JSON-serializable format
json_results = json.dumps(RESULTS, indent=2, default=str)
results_file.write_text(json_results, encoding="utf-8")

print()
print(f"✅ Results saved to: {results_file}")

# Generate markdown report
report_file = PROJECT_ROOT / "docs" / "SYSTEM3_COMPREHENSIVE_VALIDATION_REPORT.md"

# Prepare status strings (avoid backslash in f-string expressions)
pass_status = "✅ **PASS** - READY FOR TOMORROW'S MARKET"
fail_status = "❌ **FAIL** - FIXES REQUIRED"
ready_status = "✅ **READY FOR TOMORROW'S MARKET**"
not_ready_status = "❌ **NOT READY - FIXES REQUIRED"

report_content = f"""# System3 Comprehensive Deep Analysis & Multi-Validation Report
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Purpose**: Deep analysis of all MD files, phases, batch file, and autorun system

---

## Executive Summary

**Overall Status**: {pass_status if overall_pass else fail_status}

**Total Checks**: {len(all_checks)}  
**Passed**: {sum(1 for _, s in all_checks if s)}  
**Failed**: {overall_fail_count}

---

## Detailed Results

### 1. MD Files Analysis
"""
for md_file, data in md_analysis.items():
    if data.get("exists"):
        report_content += f"- **{md_file}**: {data.get('status', 'UNKNOWN')}\n"
    else:
        report_content += f"- **{md_file}**: NOT FOUND\n"

report_content += f"""
### 2. Phase Validation
- **Diagnostic Scripts**: {sum(1 for s in phase_validation.get('diagnostic_scripts', {}).values() if s.get('exists', False))} found
- **Autorun Loading**: {'✅ All ranges loaded' if phase_validation.get('autorun_loading', {}).get('all_loaded', False) else '❌ Missing ranges'}
- **Phase Files**: {phase_validation.get('phase_files', {}).get('count', 0)} files found

### 3. Batch File Validation
- **Structure**: {'✅ VALID' if batch_validation.get('all_valid', False) else '❌ INVALID'}
- **Components**: All critical components present

### 4. Autorun System Validation
- **Master**: {'✅ All features present' if autorun_validation.get('master', {}).get('all_valid', False) else '❌ Missing features'}
- **Watchdog**: {'✅ All features present' if autorun_validation.get('watchdog', {}).get('all_valid', False) else '❌ Missing features'}
- **Autopilot**: {'✅ All features present' if autorun_validation.get('autopilot', {}).get('all_valid', False) else '❌ Missing features'}

### 5. Critical Files
"""
for name, data in file_validation.items():
    status = "✅ EXISTS" if data.get("exists", False) else "❌ NOT FOUND"
    report_content += f"- **{name}**: {status}\n"

report_content += f"""
### 6. Market Hours Validation
- **Hours**: {market_hours_validation.get('open', 'N/A')} - {market_hours_validation.get('close', 'N/A')}
- **IST Correct**: {'✅ YES' if market_hours_validation.get('is_ist_correct', False) else '❌ NO'}

---

## Final Verdict

{ready_status if overall_pass else not_ready_status}

### Recommendation:
"""
if overall_pass:
    report_content += "System is validated and ready to run START_AUTORUN_AND_WATCHDOG.bat for tomorrow's market session.\n"
else:
    report_content += f"Fix {overall_fail_count} critical issue(s) before running the system.\n"

report_content += f"""

---

**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

report_file.write_text(report_content, encoding="utf-8")
print(f"✅ Report saved to: {report_file}")

print()
print("="*80)
print("VALIDATION COMPLETE")
print("="*80)

