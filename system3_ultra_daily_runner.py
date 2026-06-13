"""
System3 Ultra Daily Runner

Runs daily operational phases automatically:
- OP1: Pre-Market Diagnostic
- OP2: Live Signal Generation (if during market hours)
- OP3: Trade Decision & Planning
- OP4: Post-Market Analysis

All operations are shadow-only, with all safety locks enabled.
"""

import sys
from pathlib import Path
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.engine.ultra_safety import load_ultra_safety
from core.engine.dhan_automation_config import AUTOMATION_CONFIG


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


def run_op1_pre_market():
    """OP1: Pre-Market Diagnostic"""
    print("\n" + "="*70)
    print("OP1: PRE-MARKET DIAGNOSTIC")
    print("="*70)
    
    try:
        from core.engine.dhan_market_warmup_scanner import main
        main()
        print("\n[OK] OP1 complete")
        return True
    except Exception as e:
        print(f"\n[ERROR] OP1 failed: {e}")
        return False


def run_op2_live_signals():
    """OP2: Live Signal Generation"""
    print("\n" + "="*70)
    print("OP2: LIVE SIGNAL GENERATION")
    print("="*70)
    print("[INFO] This would run continuously during market hours.")
    print("[INFO] For automated loop, use: system3_ultra_runtime_loops.py")
    print("\n[SKIP] OP2 skipped (use runtime loops for continuous operation)")
    return True


def run_op3_trade_decision():
    """OP3: Trade Decision & Planning"""
    print("\n" + "="*70)
    print("OP3: TRADE DECISION & PLANNING")
    print("="*70)
    
    try:
        from core.engine.dhan_trade_decision import main
        main()
        print("\n[OK] OP3 complete")
        return True
    except Exception as e:
        print(f"\n[ERROR] OP3 failed: {e}")
        return False


def run_op4_post_market():
    """OP4: Post-Market Analysis"""
    print("\n" + "="*70)
    print("OP4: POST-MARKET ANALYSIS")
    print("="*70)
    
    try:
        from core.engine.dhan_daily_learning_digest import main
        main()
        print("\n[OK] OP4 complete")
        return True
    except Exception as e:
        print(f"\n[ERROR] OP4 failed: {e}")
        return False


def main():
    """Main entry point for daily runner."""
    print("\n" + "="*70)
    print("SYSTEM3 ULTRA - DAILY RUNNER")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not check_safety():
        print("\n[ERROR] Safety checks failed. Aborting.")
        return
    
    print("\n[INFO] Running daily operational phases...")
    print("[SAFETY] Shadow-only, no real trades, all safety locks enabled\n")
    
    results = {}
    
    # OP1: Pre-Market
    results["OP1"] = run_op1_pre_market()
    
    # OP2: Live Signals (skipped in automated run)
    results["OP2"] = run_op2_live_signals()
    
    # OP3: Trade Decision
    results["OP3"] = run_op3_trade_decision()
    
    # OP4: Post-Market
    results["OP4"] = run_op4_post_market()
    
    # Summary
    print("\n" + "="*70)
    print("DAILY RUNNER SUMMARY")
    print("="*70)
    for phase, success in results.items():
        status = "[OK]" if success else "[FAIL]"
        print(f"{phase}: {status}")
    
    all_ok = all(results.values())
    if all_ok:
        print("\n[OK] All daily phases completed successfully.")
    else:
        print("\n[WARN] Some phases had issues. Review logs.")
    
    print("\n[INFO] Daily runner complete.")


if __name__ == "__main__":
    main()

