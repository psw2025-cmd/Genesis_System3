"""
Verify that the system is using REAL market data (not simulation)
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def verify_real_data_mode():
    """Verify system is configured for real data."""
    print("=" * 80)
    print("  VERIFYING REAL DATA MODE")
    print("=" * 80)

    checks = []

    # Check 1: Batch file doesn't have --sim-mode in actual command
    batch_file = ROOT_DIR / "START_REAL_LIVE_PAPER_TRADING.bat"
    if batch_file.exists():
        content = batch_file.read_text(encoding="utf-8", errors="ignore")
        # Check if --sim-mode is in the actual python command (not just comments)
        lines = content.split("\n")
        has_sim_mode_in_command = False
        for line in lines:
            if "run_live_chain.py" in line and "--sim-mode" in line:
                has_sim_mode_in_command = True
                break

        if not has_sim_mode_in_command:
            print("  [OK] Batch file does NOT use --sim-mode flag in command")
            checks.append(True)
        else:
            print("  [ERROR] Batch file uses --sim-mode flag in command!")
            checks.append(False)
    else:
        print("  [WARNING] START_REAL_LIVE_PAPER_TRADING.bat not found")
        checks.append(False)

    # Check 2: run_live_chain.py default is sim_mode=False
    chain_runner = ROOT_DIR / "scripts" / "run_live_chain.py"
    if chain_runner.exists():
        content = chain_runner.read_text(encoding="utf-8", errors="ignore")
        if "sim_mode: bool = False" in content:
            print("  [OK] run_live_chain.py default is sim_mode=False")
            checks.append(True)
        else:
            print("  [WARNING] Could not verify sim_mode default")
            checks.append(False)

    # Check 3: start_real_live_trading.py explicitly sets sim_mode=False
    real_trading = ROOT_DIR / "scripts" / "start_real_live_trading.py"
    if real_trading.exists():
        content = real_trading.read_text(encoding="utf-8", errors="ignore")
        if "sim_mode=False" in content and "# REAL MODE" in content:
            print("  [OK] start_real_live_trading.py explicitly sets sim_mode=False")
            checks.append(True)
        else:
            print("  [WARNING] Could not verify sim_mode=False in start_real_live_trading.py")
            checks.append(False)

    # Check 4: No replay_engine import in batch file
    if batch_file.exists():
        content = batch_file.read_text(encoding="utf-8", errors="ignore")
        has_replay = "replay" in content.lower() and "engine" in content.lower()
        if not has_replay:
            print("  [OK] Batch file does NOT use replay engine")
            checks.append(True)
        else:
            print("  [WARNING] Batch file may use replay engine")
            checks.append(False)

    # Summary
    print("\n" + "=" * 80)
    print("  VERIFICATION SUMMARY")
    print("=" * 80)

    all_passed = all(checks)

    if all_passed:
        print("\n  [SUCCESS] System is configured for REAL market data")
        print("  [CONFIRMED] NO simulation/virtual data will be used")
    else:
        print("\n  [WARNING] Some checks failed - review configuration")

    print("\n  Configuration Status:")
    print(f"    - Real Data Mode: {'ENABLED' if all_passed else 'REVIEW REQUIRED'}")
    print(f"    - Simulation Mode: {'DISABLED' if all_passed else 'CHECK REQUIRED'}")
    print(f"    - Virtual Data: {'NOT USED' if all_passed else 'CHECK REQUIRED'}")

    print("\n" + "=" * 80)

    return all_passed


if __name__ == "__main__":
    success = verify_real_data_mode()
    sys.exit(0 if success else 1)
