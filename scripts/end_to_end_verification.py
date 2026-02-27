"""
End-to-End Verification - Complete System Check
Verifies entire pipeline from start to end
"""

import sys
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
import pytz
import time

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def verify_pre_trading():
    """Verify pre-trading setup."""
    print("\n[PHASE 1] PRE-TRADING VERIFICATION")
    print("-" * 80)

    issues = []

    # Check directories
    required_dirs = ["outputs", "logs", "storage/live"]
    for d in required_dirs:
        if not (ROOT_DIR / d).exists():
            issues.append(f"Directory missing: {d}")
        else:
            print(f"  [OK] Directory: {d}")

    # Check base CSV
    base_csv = ROOT_DIR / "storage" / "live" / "option_chain_ALL_INDICES.csv"
    if base_csv.exists():
        print(f"  [OK] Base CSV exists")
    else:
        print(f"  [WARN] Base CSV not found (will use default)")

    # Check components
    try:
        from src.trading.paper_executor import PaperExecutor
        from src.trading.pnl_tracker import PnLTracker
        from src.sim.replay_engine import ReplayEngine

        print(f"  [OK] All components importable")
    except Exception as e:
        issues.append(f"Component import failed: {e}")

    if issues:
        print(f"  [FAIL] {len(issues)} issues found")
        return False
    else:
        print(f"  [OK] Pre-trading checks passed")
        return True


def verify_during_trading():
    """Verify during trading."""
    print("\n[PHASE 2] DURING-TRADING VERIFICATION")
    print("-" * 80)

    # Wait a bit for system to start
    print("  Waiting 10 seconds for system to initialize...")
    time.sleep(10)

    issues = []

    # Check outputs are being generated
    pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
    if pnl_file.exists():
        try:
            pnl = json.load(open(pnl_file))
            print(f"  [OK] PnL file exists and valid")
            print(f"       Total PnL: Rs {pnl.get('total_pnl', 0):.2f}")
            print(f"       Trades: {pnl.get('total_trades', 0)}")
        except:
            issues.append("PnL file invalid")
    else:
        print(f"  [INFO] PnL file not yet created (may be normal)")

    trades_file = ROOT_DIR / "outputs" / "paper_trades_live.csv"
    if trades_file.exists():
        try:
            df = pd.read_csv(trades_file)
            print(f"  [OK] Trades CSV exists ({len(df)} rows)")
        except:
            issues.append("Trades CSV invalid")
    else:
        print(f"  [INFO] Trades CSV not yet created (may be normal)")

    if issues:
        print(f"  [WARN] {len(issues)} issues found")
    else:
        print(f"  [OK] During-trading checks passed")

    return len(issues) == 0


def verify_post_trading():
    """Verify post-trading."""
    print("\n[PHASE 3] POST-TRADING VERIFICATION")
    print("-" * 80)

    issues = []

    # Check final outputs
    pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
    if pnl_file.exists():
        pnl = json.load(open(pnl_file))
        print(f"  [OK] Final PnL: Rs {pnl.get('total_pnl', 0):.2f}")
        print(f"       Total Trades: {pnl.get('total_trades', 0)}")
        print(f"       Win Rate: {pnl.get('win_rate', 0):.1f}%")
    else:
        issues.append("Final PnL file missing")

    # Check archive
    archive_dir = ROOT_DIR / "storage" / "archive"
    if archive_dir.exists():
        archives = list(archive_dir.glob("session_*"))
        print(f"  [OK] Archive directory exists ({len(archives)} sessions archived)")
    else:
        print(f"  [INFO] Archive directory not yet created")

    if issues:
        print(f"  [WARN] {len(issues)} issues found")
    else:
        print(f"  [OK] Post-trading checks passed")

    return len(issues) == 0


def main():
    """Run end-to-end verification."""
    print("\n" + "=" * 80)
    print("  END-TO-END VERIFICATION")
    print("=" * 80)

    # Pre-trading
    pre_ok = verify_pre_trading()

    # During trading (if running)
    during_ok = verify_during_trading()

    # Post-trading
    post_ok = verify_post_trading()

    # Summary
    print("\n" + "=" * 80)
    print("  VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"  Pre-Trading: {'PASS' if pre_ok else 'FAIL'}")
    print(f"  During Trading: {'PASS' if during_ok else 'WARN'}")
    print(f"  Post-Trading: {'PASS' if post_ok else 'WARN'}")

    if pre_ok and during_ok and post_ok:
        print("\n  [OK] ALL VERIFICATIONS PASSED")
        return True
    else:
        print("\n  [WARN] Some verifications had issues")
        return False
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
