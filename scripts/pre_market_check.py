"""
Pre-Market Check - Run this before market opens to ensure everything is ready
"""

import sys
from datetime import datetime
from pathlib import Path

import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def pre_market_check():
    """Comprehensive pre-market check."""
    print("=" * 80)
    print("  PRE-MARKET CHECK - ENSURING EVERYTHING IS READY")
    print("=" * 80)

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    print(f"\nCurrent Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")
    print(f"Market Opens: 09:15 IST")
    print(f"Market Closes: 15:30 IST")

    # Check 1: Virtual environment
    print("\n[CHECK 1] Virtual Environment...")
    venv_path = ROOT_DIR / "venv" / "Scripts" / "activate.bat"
    if venv_path.exists():
        print("  [OK] Virtual environment exists")
    else:
        print("  [ERROR] Virtual environment not found!")
        return False

    # Check 2: Required files
    print("\n[CHECK 2] Required Files...")
    required_files = [
        "scripts/run_live_chain.py",
        "scripts/build_advanced_excel_with_ai_predictions.py",
        "scripts/pre_trading_validation.py",
        "scripts/multi_session_handler.py",
        "scripts/monitor_live_simulation.py",
        "config/.env",
    ]

    all_ok = True
    for file_path in required_files:
        full_path = ROOT_DIR / file_path
        if full_path.exists():
            print(f"  [OK] {file_path}")
        else:
            print(f"  [ERROR] {file_path} missing!")
            all_ok = False

    if not all_ok:
        return False

    # Check 3: Data files
    print("\n[CHECK 3] Data Files...")
    data_files = ["outputs/chain_raw_live.csv", "outputs/pnl_live.json"]

    for file_path in data_files:
        full_path = ROOT_DIR / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  [OK] {file_path} ({size} bytes)")
        else:
            print(f"  [WARNING] {file_path} missing (will be created)")

    # Check 4: Python dependencies
    print("\n[CHECK 4] Python Dependencies...")
    try:
        import numpy
        import openpyxl
        import pandas

        # pytz already imported at top
        print("  [OK] All required packages installed")
    except ImportError as e:
        print(f"  [ERROR] Missing package: {e}")
        return False

    # Check 5: Market hours detection
    print("\n[CHECK 5] Market Hours Detection...")
    try:
        from src.utils.market_hours import is_market_open

        market_open, reason = is_market_open(now)
        print(f"  [OK] Market hours detection working")
        print(f"  [INFO] Market is currently: {'OPEN' if market_open else 'CLOSED'}")
        print(f"  [INFO] Reason: {reason}")
    except Exception as e:
        print(f"  [ERROR] Market hours detection failed: {e}")
        return False

    # Check 6: System components
    print("\n[CHECK 6] System Components...")
    components = [
        "src.trading.paper_executor",
        "src.trading.pnl_tracker",
        "src.trading.advanced_position_sizing",
        "src.trading.dynamic_risk_management",
        "src.selector.strategy_engine",
    ]

    for component in components:
        try:
            __import__(component)
            print(f"  [OK] {component}")
        except Exception as e:
            print(f"  [ERROR] {component}: {e}")
            return False

    print("\n" + "=" * 80)
    print("  PRE-MARKET CHECK COMPLETE")
    print("=" * 80)
    print("\n[STATUS] ALL CHECKS PASSED - SYSTEM READY FOR LIVE TRADING")
    print("\nTo start live trading, run:")
    print("  START_LIVE_TRADING_AUTO.bat")
    print("\n" + "=" * 80)

    return True


if __name__ == "__main__":
    success = pre_market_check()
    sys.exit(0 if success else 1)
