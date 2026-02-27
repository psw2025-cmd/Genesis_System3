"""Step by step import test"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

print("Step 1: Testing basic imports...")
try:
    from scripts.run_live_chain import LiveChainRunner
    print("  [OK] LiveChainRunner imported")
except Exception as e:
    print(f"  [FAIL] LiveChainRunner failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 2: Testing market_hours...")
try:
    from src.utils.market_hours import is_market_open
    print("  [OK] is_market_open imported")
except Exception as e:
    print(f"  [FAIL] is_market_open failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 3: Testing logger...")
try:
    from core.utils.logger import logger
    print("  [OK] logger imported")
except Exception as e:
    print(f"  [FAIL] logger failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 4: Testing smart_market_auto_switch...")
try:
    from scripts.smart_market_auto_switch import SmartMarketAutoSwitch
    print("  [OK] SmartMarketAutoSwitch imported")
except Exception as e:
    print(f"  [FAIL] SmartMarketAutoSwitch failed: {e}")
    import traceback
    traceback.print_exc()
    print("  (Will use fallback)")

print("Step 5: Testing smart_live_chain_runner import...")
try:
    import scripts.smart_live_chain_runner as m
    print(f"  [OK] Module imported: {m}")
    print(f"  Has SmartLiveChainRunner: {hasattr(m, 'SmartLiveChainRunner')}")
    print(f"  Dir: {[x for x in dir(m) if not x.startswith('_')]}")
except Exception as e:
    print(f"  [FAIL] Module import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 6: Testing class import...")
try:
    from scripts.smart_live_chain_runner import SmartLiveChainRunner
    print("  [OK] SmartLiveChainRunner imported")
except Exception as e:
    print(f"  [FAIL] SmartLiveChainRunner import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll tests passed!")
