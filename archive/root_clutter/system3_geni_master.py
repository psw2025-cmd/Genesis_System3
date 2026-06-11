"""
System3 GENI Ultra Master Agent

High-level orchestration and validation entry point.
All operations are SAFE MODE - no real trades, no auto-promotion.

Usage:
    python system3_geni_master.py status
    python system3_geni_master.py full-validation
    python system3_geni_master.py daily-ultra
    python system3_geni_master.py panel-test
    python system3_geni_master.py all
"""

import sys
from pathlib import Path

# Ensure project root is in path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.geni.geni_orchestrator import run_geni_master


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("System3 GENI Ultra Master Agent")
        print("=" * 70)
        print("Usage:")
        print("  python system3_geni_master.py status")
        print("  python system3_geni_master.py full-validation")
        print("  python system3_geni_master.py daily-ultra")
        print("  python system3_geni_master.py panel-test")
        print("  python system3_geni_master.py all")
        print()
        print("All operations are SAFE MODE - no real trades, no auto-promotion.")
        return 1
    
    mode_arg = sys.argv[1].lower()
    
    # Map CLI arguments to internal modes
    mode_map = {
        "status": "status",
        "full-validation": "full_validation",
        "full_validation": "full_validation",
        "daily-ultra": "daily_ultra",
        "daily_ultra": "daily_ultra",
        "panel-test": "panel_test",
        "panel_test": "panel_test",
        "all": "all",
    }
    
    mode = mode_map.get(mode_arg)
    if not mode:
        print(f"[ERROR] Unknown mode: {mode_arg}")
        print("Valid modes: status, full-validation, daily-ultra, panel-test, all")
        return 1
    
    try:
        exit_code = run_geni_master(mode=mode)
        return exit_code
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
        return 130
    except Exception as e:
        print(f"\n[ERROR] GENI master failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

