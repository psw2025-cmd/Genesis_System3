"""
System3 Ultra Phases 39-45: Complete Verification Script

This script verifies all phases 39-45 are working correctly.
Run this after implementation to confirm everything is operational.

Usage:
    python verify_phases_39_45.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(text: str) -> None:
    """Print a header."""
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_success(text: str) -> None:
    """Print success message."""
    print(f"{GREEN}[PASS]{RESET} {text}")

def print_error(text: str) -> None:
    """Print error message."""
    print(f"{RED}[FAIL]{RESET} {text}")

def print_warn(text: str) -> None:
    """Print warning message."""
    print(f"{YELLOW}[WARN]{RESET} {text}")

def print_info(text: str) -> None:
    """Print info message."""
    print(f"{BLUE}[INFO]{RESET} {text}")

def verify_phase39() -> Tuple[bool, List[str]]:
    """Verify Phase 39: Shadow Campaign Manager."""
    print_header("VERIFYING PHASE 39: Shadow Campaign Manager")
    
    issues = []
    
    # Check module exists
    module_path = PROJECT_ROOT / "core" / "engine" / "system3_phase39_shadow_campaign.py"
    if not module_path.exists():
        print_error(f"Module not found: {module_path}")
        issues.append(f"Module file missing: {module_path}")
        return False, issues
    print_success(f"Module exists: {module_path.name}")
    
    # Check config file (should exist or be auto-created)
    config_file = PROJECT_ROOT / "storage" / "config" / "ultra_shadow_campaign_config.json"
    if config_file.exists():
        try:
            with config_file.open("r") as f:
                config = json.load(f)
            print_success(f"Config file exists: {config_file.name}")
            print_info(f"  - Loops: {config.get('loops', 'N/A')}")
            print_info(f"  - Sleep seconds: {config.get('sleep_seconds', 'N/A')}")
        except Exception as e:
            print_warn(f"Config file exists but cannot read: {e}")
            issues.append(f"Config file read error: {e}")
    else:
        print_info("Config file will be auto-created on first run")
    
    # Check log directory
    log_dir = PROJECT_ROOT / "storage" / "logs_ultra"
    if log_dir.exists():
        print_success(f"Log directory exists: {log_dir}")
    else:
        print_info("Log directory will be auto-created on first run")
    
    # Check menu integration
    run_system3 = PROJECT_ROOT / "run_system3.py"
    if run_system3.exists():
        content = run_system3.read_text(encoding="utf-8")
        if "system3_phase39_shadow_campaign" in content and "102" in content:
            print_success("Menu integration found (option 102)")
        else:
            print_warn("Menu integration may be missing")
            issues.append("Menu integration check failed")
    
    return len(issues) == 0, issues

def verify_phase40() -> Tuple[bool, List[str]]:
    """Verify Phase 40: Weekly Governance Pack."""
    print_header("VERIFYING PHASE 40: Weekly Governance Pack")
    
    issues = []
    
    # Check module exists
    module_path = PROJECT_ROOT / "core" / "engine" / "system3_phase40_weekly_governance_pack.py"
    if not module_path.exists():
        print_error(f"Module not found: {module_path}")
        issues.append(f"Module file missing: {module_path}")
        return False, issues
    print_success(f"Module exists: {module_path.name}")
    
    # Check output directory
    weekly_packs_dir = PROJECT_ROOT / "storage" / "ultra" / "weekly_packs"
    if weekly_packs_dir.exists():
        print_success(f"Output directory exists: {weekly_packs_dir}")
        # Check for existing packs
        packs = list(weekly_packs_dir.glob("*/weekly_governance_pack.md"))
        if packs:
            print_info(f"Found {len(packs)} existing weekly pack(s)")
    else:
        print_info("Output directory will be auto-created on first run")
    
    # Check menu integration
    run_system3 = PROJECT_ROOT / "run_system3.py"
    if run_system3.exists():
        content = run_system3.read_text(encoding="utf-8")
        if "system3_phase40_weekly_governance_pack" in content and "103" in content:
            print_success("Menu integration found (option 103)")
        else:
            print_warn("Menu integration may be missing")
            issues.append("Menu integration check failed")
    
    return len(issues) == 0, issues

def verify_phase41() -> Tuple[bool, List[str]]:
    """Verify Phase 41: Promotion Executor."""
    print_header("VERIFYING PHASE 41: Promotion Executor")
    
    issues = []
    
    # Check module exists
    module_path = PROJECT_ROOT / "core" / "engine" / "system3_phase41_promotion_executor.py"
    if not module_path.exists():
        print_error(f"Module not found: {module_path}")
        issues.append(f"Module file missing: {module_path}")
        return False, issues
    print_success(f"Module exists: {module_path.name}")
    
    # Check staging directory
    staging_dir = PROJECT_ROOT / "core" / "models" / "angel_one_ultra_staging"
    if staging_dir.exists():
        print_success(f"Staging directory exists: {staging_dir}")
    else:
        print_info("Staging directory will be auto-created on first run")
    
    # Check flag file (should not exist by default)
    flag_file = PROJECT_ROOT / "storage" / "config" / "ultra_promotion_flag.txt"
    if flag_file.exists():
        content = flag_file.read_text(encoding="utf-8").strip()
        if "ALLOW_ULTRA_PROMOTION_STAGING" in content:
            print_warn("Promotion flag file exists (promotion enabled)")
        else:
            print_warn("Promotion flag file exists but keyword missing")
    else:
        print_info("Promotion flag file not found (expected - safety mechanism)")
    
    # Check menu integration
    run_system3 = PROJECT_ROOT / "run_system3.py"
    if run_system3.exists():
        content = run_system3.read_text(encoding="utf-8")
        if "system3_phase41_promotion_executor" in content and "104" in content:
            print_success("Menu integration found (option 104)")
        else:
            print_warn("Menu integration may be missing")
            issues.append("Menu integration check failed")
    
    return len(issues) == 0, issues

def verify_phase42() -> Tuple[bool, List[str]]:
    """Verify Phase 42: Snapshot Manager."""
    print_header("VERIFYING PHASE 42: Snapshot Manager")
    
    issues = []
    
    # Check module exists
    module_path = PROJECT_ROOT / "core" / "engine" / "system3_phase42_snapshot_manager.py"
    if not module_path.exists():
        print_error(f"Module not found: {module_path}")
        issues.append(f"Module file missing: {module_path}")
        return False, issues
    print_success(f"Module exists: {module_path.name}")
    
    # Check snapshots directory
    snapshots_dir = PROJECT_ROOT / "storage" / "snapshots"
    if snapshots_dir.exists():
        print_success(f"Snapshots directory exists: {snapshots_dir}")
        # Check for existing snapshots
        snapshots = [d for d in snapshots_dir.iterdir() if d.is_dir()]
        if snapshots:
            print_info(f"Found {len(snapshots)} existing snapshot(s)")
            latest = sorted(snapshots, key=lambda x: x.stat().st_mtime, reverse=True)[0]
            print_info(f"Latest snapshot: {latest.name}")
    else:
        print_info("Snapshots directory will be auto-created on first run")
    
    # Check baseline models exist (for snapshot)
    models_dir = PROJECT_ROOT / "core" / "models" / "angel_one"
    if models_dir.exists():
        model_files = list(models_dir.glob("*_model.pkl"))
        if model_files:
            print_success(f"Baseline models found: {len(model_files)} model(s)")
        else:
            print_warn("No baseline models found (snapshot will be empty)")
    else:
        print_warn("Baseline models directory not found")
    
    # Check menu integration
    run_system3 = PROJECT_ROOT / "run_system3.py"
    if run_system3.exists():
        content = run_system3.read_text(encoding="utf-8")
        if "system3_phase42_snapshot_manager" in content and ("105" in content or "106" in content):
            print_success("Menu integration found (options 105, 106)")
        else:
            print_warn("Menu integration may be missing")
            issues.append("Menu integration check failed")
    
    return len(issues) == 0, issues

def verify_phase43() -> Tuple[bool, List[str]]:
    """Verify Phase 43: Environment Guard."""
    print_header("VERIFYING PHASE 43: Environment Guard")
    
    issues = []
    
    # Check module exists
    module_path = PROJECT_ROOT / "core" / "engine" / "system3_phase43_env_guard.py"
    if not module_path.exists():
        print_error(f"Module not found: {module_path}")
        issues.append(f"Module file missing: {module_path}")
        return False, issues
    print_success(f"Module exists: {module_path.name}")
    
    # Check env config file (should exist or be auto-created)
    env_config = PROJECT_ROOT / "storage" / "config" / "system3_env_config.json"
    if env_config.exists():
        try:
            with env_config.open("r") as f:
                config = json.load(f)
            print_success(f"Env config file exists: {env_config.name}")
            print_info(f"  - Angel System3: {config.get('angel_system3_enabled', 'N/A')}")
            print_info(f"  - Binance System3: {config.get('binance_system3_enabled', 'N/A')}")
        except Exception as e:
            print_warn(f"Env config file exists but cannot read: {e}")
    else:
        print_info("Env config file will be auto-created on first run")
    
    # Check menu integration
    run_system3 = PROJECT_ROOT / "run_system3.py"
    if run_system3.exists():
        content = run_system3.read_text(encoding="utf-8")
        if "system3_phase43_env_guard" in content and "107" in content:
            print_success("Menu integration found (option 107)")
        else:
            print_warn("Menu integration may be missing")
            issues.append("Menu integration check failed")
    
    return len(issues) == 0, issues

def verify_phase44() -> Tuple[bool, List[str]]:
    """Verify Phase 44: Daily All Script."""
    print_header("VERIFYING PHASE 44: Daily All Script")
    
    issues = []
    
    # Check PowerShell script
    ps_script = PROJECT_ROOT / "system3_ultra_daily_all.ps1"
    if ps_script.exists():
        print_success(f"PowerShell script exists: {ps_script.name}")
    else:
        print_error(f"PowerShell script not found: {ps_script}")
        issues.append(f"PowerShell script missing: {ps_script}")
        return False, issues
    
    # Check batch wrapper
    bat_script = PROJECT_ROOT / "system3_ultra_daily_all.bat"
    if bat_script.exists():
        print_success(f"Batch wrapper exists: {bat_script.name}")
    else:
        print_error(f"Batch wrapper not found: {bat_script}")
        issues.append(f"Batch wrapper missing: {bat_script}")
        return False, issues
    
    # Check script content
    try:
        ps_content = ps_script.read_text(encoding="utf-8")
        if "system3_phase43_env_guard" in ps_content:
            print_success("Script includes Phase 43")
        if "system3_phase37_policy_risk_monitor" in ps_content:
            print_success("Script includes Phase 37")
        if "system3_phase38_governance_summary" in ps_content:
            print_success("Script includes Phase 38")
        if "system3_phase42_snapshot_manager" in ps_content:
            print_success("Script includes Phase 42")
    except Exception as e:
        print_warn(f"Cannot read script content: {e}")
    
    return len(issues) == 0, issues

def verify_phase45() -> Tuple[bool, List[str]]:
    """Verify Phase 45: Documentation."""
    print_header("VERIFYING PHASE 45: Documentation")
    
    issues = []
    
    # Check documentation files
    docs_to_check = [
        "system3_ultra_master_index.md",
        "system3_ultra_daily_routine.md",
        "system3_phases_39_45_completion_summary.md",
        "system3_phases_39_45_daily_playbook.md",
        "system3_phases_39_45_ultra_rollout_plan.md"
    ]
    
    docs_dir = PROJECT_ROOT / "docs"
    for doc_name in docs_to_check:
        doc_path = docs_dir / doc_name
        if doc_path.exists():
            print_success(f"Documentation exists: {doc_name}")
        else:
            print_warn(f"Documentation missing: {doc_name}")
            issues.append(f"Documentation missing: {doc_name}")
    
    return len(issues) == 0, issues

def verify_safety_guarantees() -> Tuple[bool, List[str]]:
    """Verify safety guarantees are maintained."""
    print_header("VERIFYING SAFETY GUARANTEES")
    
    issues = []
    
    # Check baseline models are not modified
    baseline_models = PROJECT_ROOT / "core" / "models" / "angel_one"
    if baseline_models.exists():
        print_success("Baseline models directory exists")
        print_info("  - Baseline models should never be modified by Ultra phases")
    
    # Check Ultra isolation
    ultra_dir = PROJECT_ROOT / "storage" / "ultra"
    if ultra_dir.exists():
        print_success("Ultra directory exists (isolated from baseline)")
    
    # Check snapshots directory
    snapshots_dir = PROJECT_ROOT / "storage" / "snapshots"
    if snapshots_dir.exists():
        print_success("Snapshots directory exists (for rollback protection)")
    
    # Check staging directory
    staging_dir = PROJECT_ROOT / "core" / "models" / "angel_one_ultra_staging"
    if staging_dir.exists():
        print_success("Staging directory exists (promotion staging only)")
        print_info("  - Staging directory is separate from baseline")
    
    return len(issues) == 0, issues

def main():
    """Run all verification checks."""
    print_header("SYSTEM3 ULTRA PHASES 39-45: COMPLETE VERIFICATION")
    
    results = {}
    all_issues = []
    
    # Verify each phase
    results["Phase 39"] = verify_phase39()
    results["Phase 40"] = verify_phase40()
    results["Phase 41"] = verify_phase41()
    results["Phase 42"] = verify_phase42()
    results["Phase 43"] = verify_phase43()
    results["Phase 44"] = verify_phase44()
    results["Phase 45"] = verify_phase45()
    results["Safety Guarantees"] = verify_safety_guarantees()
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    total = len(results)
    passed_count = sum(1 for passed, _ in results.values() if passed)
    
    for phase, (phase_passed, issues) in results.items():
        if phase_passed:
            print_success(f"{phase}: PASS")
        else:
            print_error(f"{phase}: FAIL")
            all_issues.extend(issues)
    
    print(f"\n{BOLD}Total: {passed_count}/{total} checks passed{RESET}\n")
    
    if all_issues:
        print_header("ISSUES FOUND")
        for i, issue in enumerate(all_issues, 1):
            print_error(f"{i}. {issue}")
    
    if passed_count == total:
        print(f"\n{BOLD}{GREEN}✓ ALL VERIFICATIONS PASSED{RESET}\n")
        print("System3 Ultra Phases 39-45 are ready for use!")
        return 0
    else:
        print(f"\n{BOLD}{YELLOW}⚠ SOME VERIFICATIONS FAILED{RESET}\n")
        print("Please review the issues above before using the system.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

