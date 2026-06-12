"""
run_system3.py — LEGACY ANGEL ONE MENU (DISABLED)

System3 is Dhan-only. All menu options in this file target Angel One /
SmartAPI data paths that are disabled. Any menu option that attempts to
use the broker will raise RuntimeError from the disabled shim.

Do not use this script for live operation. Use system3_ultra.py instead,
which routes to the active Dhan/analyzer paths.
"""

import sys
import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# Guarded imports — may fail when optional deps (sklearn, pyotp) are absent.
try:
    from core.engine.train_angel_models import main as train_angel_models_main
    from core.engine.build_angel_training_dataset import main as build_angel_training_main
    _ANGEL_TRAINING_AVAILABLE = True
except ImportError:
    train_angel_models_main = None
    build_angel_training_main = None
    _ANGEL_TRAINING_AVAILABLE = False

from core.brokers.angel_one.broker import AngelOneBroker  # disabled shim — safe to import

try:
    from core.engine.main_launcher import main as launch_core
    from core.engine.health_check import main as health_main
    from core.engine.test_data_pipeline import main as data_test_main
    from core.engine.test_angelone_api import main as angelone_test_main
    from core.engine.test_angelone_instruments import main as angelone_instr_test_main
    from core.engine.angel_options_watch import main as angel_options_watch_main
    from core.engine.angel_options_watch_loop import (
        main as angel_options_watch_loop_main,
        _build_full_snapshot,
    )
    from core.engine.angel_options_analyze import main as angel_options_analyze_main
    from core.engine import angel_live_ai_signals
    from core.engine.angel_synthetic_backtester import run_backtest as angel_synthetic_backtest_run
    _ANGEL_ENGINE_AVAILABLE = True
except ImportError as _e:
    launch_core = health_main = data_test_main = angelone_test_main = None
    angelone_instr_test_main = angel_options_watch_main = None
    angel_options_watch_loop_main = _build_full_snapshot = None
    angel_options_analyze_main = angel_live_ai_signals = angel_synthetic_backtest_run = None
    _ANGEL_ENGINE_AVAILABLE = False


def show_menu() -> str:
    print("\n=== GENESIS SYSTEM 3 — LEGACY MENU (DISABLED) ===")
    print()
    print("  [DISABLED] All options in this script target Angel One / SmartAPI")
    print("  data paths that are no longer active. System3 is Dhan-only.")
    print()
    print("  Use system3_ultra.py instead:")
    print("    python system3_ultra.py")
    print()
    print("0) Exit")
    # Former options 1-107 mapped to Angel One broker / SmartAPI paths — removed.
    return input("Select option [0 to exit]: ").strip()


def main():
    while True:
        choice = show_menu()
        if choice == "0":
            print("Exiting.")
            break
        else:
            print("[DISABLED] Use system3_ultra.py for active Dhan operations.")


if __name__ == "__main__":
    main()
