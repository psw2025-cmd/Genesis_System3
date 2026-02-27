"""
System3 Ultra Weekly Runner

Runs weekly operational phases automatically:
- OP5: Weekly Governance Review
- Ultra phase reviews
- Promotion checks (dry-run)
- Environment guard

All operations are read-only, shadow-only, with all safety locks enabled.
"""

import sys
from pathlib import Path
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.engine.ultra_safety import load_ultra_safety
from core.engine.angel_automation_config import AUTOMATION_CONFIG


def check_safety() -> bool:
    """Verify all safety mechanisms are in place."""
    safety = load_ultra_safety()
    
    checks = {
        "auto_execute_trades": not AUTOMATION_CONFIG.auto_execute_trades,
        "auto_simulate_pnl": not AUTOMATION_CONFIG.auto_simulate_pnl,
        "ultra_auto_execute": not safety.get("AUTO_EXECUTE_TRADES", False),
        "ultra_auto_update": not safety.get("AUTO_UPDATE_THRESHOLDS", False),
        "ultra_auto_retrain": not safety.get("AUTO_RETRAIN_MODELS", False),
        "ultra_auto_promote": not safety.get("AUTO_PROMOTE_MODELS", False),
    }
    
    if not all(checks.values()):
        print("[ERROR] Safety checks failed:")
        for key, value in checks.items():
            if not value:
                print(f"  - {key}: NOT SAFE")
        return False
    
    print("[SAFETY] All safety mechanisms confirmed.")
    return True


def run_op5_governance():
    """OP5: Weekly Governance Review"""
    print("\n" + "="*70)
    print("OP5: WEEKLY GOVERNANCE REVIEW")
    print("="*70)
    
    try:
        from core.engine.system3_phase40_weekly_governance_pack import run_phase40_weekly_pack
        run_phase40_weekly_pack()
        print("\n[OK] OP5 complete")
        return True
    except Exception as e:
        print(f"\n[ERROR] OP5 failed: {e}")
        return False


def run_ultra_phase_reviews():
    """Run Ultra phase reviews"""
    print("\n" + "="*70)
    print("ULTRA PHASE REVIEWS")
    print("="*70)
    
    results = {}
    
    # Phase 35: Decision Auditor
    print("\n[Phase 35] Decision Auditor...")
    try:
        from core.engine.system3_phase35_ultra_auditor import run_phase35_audit
        run_phase35_audit()
        results["Phase35"] = True
        print("[OK] Phase 35 complete")
    except Exception as e:
        print(f"[ERROR] Phase 35 failed: {e}")
        results["Phase35"] = False
    
    # Phase 37: Policy & Risk Monitor
    print("\n[Phase 37] Policy & Risk Monitor...")
    try:
        from core.engine.system3_phase37_policy_risk_monitor import run_phase37_policy_risk_dashboard
        run_phase37_policy_risk_dashboard()
        results["Phase37"] = True
        print("[OK] Phase 37 complete")
    except Exception as e:
        print(f"[ERROR] Phase 37 failed: {e}")
        results["Phase37"] = False
    
    # Phase 38: Governance Summary
    print("\n[Phase 38] Governance Summary...")
    try:
        from core.engine.system3_phase38_governance_summary import run_phase38_governance_summary
        run_phase38_governance_summary()
        results["Phase38"] = True
        print("[OK] Phase 38 complete")
    except Exception as e:
        print(f"[ERROR] Phase 38 failed: {e}")
        results["Phase38"] = False
    
    return results


def run_promotion_checks():
    """Run promotion checks (dry-run only)"""
    print("\n" + "="*70)
    print("PROMOTION CHECKS (DRY-RUN)")
    print("="*70)
    
    try:
        from core.engine.system3_phase33_promotion_planner import run_phase33_promotion_planner
        run_phase33_promotion_planner()
        print("\n[OK] Promotion checks complete (suggestions only)")
        return True
    except Exception as e:
        print(f"\n[ERROR] Promotion checks failed: {e}")
        return False


def run_environment_guard():
    """Run environment guard"""
    print("\n" + "="*70)
    print("ENVIRONMENT GUARD")
    print("="*70)
    
    try:
        from core.engine.system3_phase43_env_guard import run_phase43_env_guard
        run_phase43_env_guard()
        print("\n[OK] Environment guard complete")
        return True
    except Exception as e:
        print(f"\n[ERROR] Environment guard failed: {e}")
        return False


def main():
    """Main entry point for weekly runner."""
    print("\n" + "="*70)
    print("SYSTEM3 ULTRA - WEEKLY RUNNER")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not check_safety():
        print("\n[ERROR] Safety checks failed. Aborting.")
        return
    
    print("\n[INFO] Running weekly operational phases...")
    print("[SAFETY] Read-only, shadow-only, all safety locks enabled\n")
    
    results = {}
    
    # OP5: Weekly Governance
    results["OP5"] = run_op5_governance()
    
    # Ultra Phase Reviews
    phase_results = run_ultra_phase_reviews()
    results.update(phase_results)
    
    # Promotion Checks
    results["Promotion"] = run_promotion_checks()
    
    # Environment Guard
    results["Environment"] = run_environment_guard()
    
    # Summary
    print("\n" + "="*70)
    print("WEEKLY RUNNER SUMMARY")
    print("="*70)
    for phase, success in results.items():
        status = "[OK]" if success else "[FAIL]"
        print(f"{phase}: {status}")
    
    all_ok = all(results.values())
    if all_ok:
        print("\n[OK] All weekly phases completed successfully.")
    else:
        print("\n[WARN] Some phases had issues. Review logs.")
    
    print("\n[INFO] Weekly runner complete.")


if __name__ == "__main__":
    main()

