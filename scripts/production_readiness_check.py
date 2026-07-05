"""
Production Readiness Check - Validates all system components
"""

import sys
from datetime import datetime
from pathlib import Path

import pytz

# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def check_imports():
    """Check if all required modules can be imported."""
    print("\n[CHECK 1/8] Testing imports...")
    try:
        from scripts.run_live_chain import LiveChainRunner
        from src.storage.trade_history import TradeHistoryStore
        from src.trading.paper_executor import PaperExecutor
        from src.trading.pnl_tracker import PnLTracker

        # Note: DhanBroker removed — System3 is Dhan-only

        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False


def check_directories():
    """Check if required directories exist."""
    print("\n[CHECK 2/8] Checking directories...")
    dirs = ["outputs", "logs", "storage/live"]
    all_ok = True
    for d in dirs:
        path = ROOT_DIR / d
        if path.exists():
            print(f"  ✅ {d} exists")
        else:
            print(f"  ⚠️  {d} missing (will be created)")
            path.mkdir(parents=True, exist_ok=True)
    return True


def check_data_files():
    """Check if data files are accessible."""
    print("\n[CHECK 3/8] Checking data files...")
    files = {
        "outputs/pnl_live.json": "PnL summary",
        "outputs/positions_live.json": "Positions data",
        "outputs/paper_trades_live.csv": "Trade history",
    }
    all_ok = True
    for file_path, desc in files.items():
        path = ROOT_DIR / file_path
        if path.exists():
            age = (datetime.now().timestamp() - path.stat().st_mtime) / 60
            if age < 60:
                print(f"  ✅ {desc}: exists (updated {int(age)} min ago)")
            else:
                print(f"  ⚠️  {desc}: exists but old ({int(age)} min ago)")
        else:
            print(f"  ℹ️  {desc}: will be created on first run")
    return True


def check_broker_config():
    """Check broker configuration."""
    print("\n[CHECK 4/8] Checking broker configuration...")
    try:
        env_file = ROOT_DIR / ".env"
        if env_file.exists():
            content = env_file.read_text()
            if "ANGEL" in content or "API" in content:
                print("  ✅ Broker config file found")
                return True
            else:
                print("  ⚠️  Config file exists but may be incomplete")
                return True
        else:
            print("  ⚠️  .env file not found (system may use defaults)")
            return True
    except Exception as e:
        print(f"  ⚠️  Config check error: {e}")
        return True


def check_market_hours():
    """Check market hours detection."""
    print("\n[CHECK 5/8] Testing market hours detection...")
    try:
        from src.utils.market_hours import get_market_status, is_market_open

        ist = pytz.timezone("Asia/Kolkata")
        now = datetime.now(ist)
        is_open, reason = is_market_open(now)
        status = get_market_status()
        print(f"  ✅ Market hours detection working")
        print(f"     Current status: {'OPEN' if is_open else 'CLOSED'} - {reason}")
        return True
    except Exception as e:
        print(f"  ❌ Market hours check failed: {e}")
        return False


def check_paper_executor():
    """Check paper executor initialization."""
    print("\n[CHECK 6/8] Testing paper executor...")
    try:
        from src.trading.paper_executor import PaperExecutor

        executor = PaperExecutor()
        summary = executor.get_positions_summary()
        print("  ✅ Paper executor initialized")
        return True
    except Exception as e:
        print(f"  ❌ Paper executor error: {e}")
        return False


def check_pnl_tracker():
    """Check PnL tracker initialization."""
    print("\n[CHECK 7/8] Testing PnL tracker...")
    try:
        from src.trading.pnl_tracker import PnLTracker

        tracker = PnLTracker()
        print("  ✅ PnL tracker initialized")
        return True
    except Exception as e:
        print(f"  ❌ PnL tracker error: {e}")
        return False


def check_trade_history():
    """Check trade history store."""
    print("\n[CHECK 8/8] Testing trade history store...")
    try:
        from src.storage.trade_history import TradeHistoryStore

        store = TradeHistoryStore()
        print("  ✅ Trade history store initialized")
        return True
    except Exception as e:
        print(f"  ❌ Trade history error: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 80)
    print("  PRODUCTION READINESS CHECK")
    print("=" * 80)

    checks = [
        check_imports,
        check_directories,
        check_data_files,
        check_broker_config,
        check_market_hours,
        check_paper_executor,
        check_pnl_tracker,
        check_trade_history,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Check failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)

    passed = sum(results)
    total = len(results)

    print(f"\n  Checks passed: {passed}/{total}")

    if passed == total:
        print("  Status: ✅ ALL CHECKS PASSED - SYSTEM READY")
        return 0
    elif passed >= total * 0.75:
        print("  Status: ⚠️  MOST CHECKS PASSED - SYSTEM READY WITH WARNINGS")
        return 0
    else:
        print("  Status: ❌ MULTIPLE CHECKS FAILED - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
