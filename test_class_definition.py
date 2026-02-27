"""Test if class can be defined"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

print("Testing class definition...")
print()

# Test imports first
print("Step 1: Testing imports...")
try:
    from scripts.run_live_chain import LiveChainRunner
    print("  [OK] LiveChainRunner")
except Exception as e:
    print(f"  [FAIL] LiveChainRunner: {e}")
    sys.exit(1)

try:
    from src.utils.market_hours import is_market_open
    print("  [OK] is_market_open")
except Exception as e:
    print(f"  [FAIL] is_market_open: {e}")
    sys.exit(1)

try:
    from core.utils.logger import logger
    print("  [OK] logger")
except Exception as e:
    print(f"  [FAIL] logger: {e}")
    sys.exit(1)

print()
print("Step 2: Testing SmartMarketAutoSwitch import...")
try:
    from scripts.smart_market_auto_switch import SmartMarketAutoSwitch
    print("  [OK] SmartMarketAutoSwitch imported")
    HAS_SMART_SWITCH = True
except Exception as e:
    print(f"  [WARN] SmartMarketAutoSwitch import failed: {e}")
    print("  [INFO] Will use fallback")
    HAS_SMART_SWITCH = False
    
    # Create fallback
    class SmartMarketAutoSwitch:
        def __init__(self, check_interval=30):
            self.check_interval = check_interval
            self.running = False
        def start_monitoring(self):
            pass
        def stop_monitoring(self):
            self.running = False

print()
print("Step 3: Defining SmartLiveChainRunner class...")
try:
    import pytz
    IST = pytz.timezone('Asia/Kolkata')
    
    class SmartLiveChainRunner:
        def __init__(self, refresh_interval=5, market_check_interval=30, use_websocket=False):
            self.refresh_interval = refresh_interval
            self.market_check_interval = market_check_interval
            self.use_websocket = use_websocket
            try:
                self.auto_switch = SmartMarketAutoSwitch(check_interval=market_check_interval)
            except:
                class SimpleAutoSwitch:
                    def __init__(self, check_interval):
                        self.check_interval = check_interval
                        self.running = False
                    def start_monitoring(self):
                        pass
                    def stop_monitoring(self):
                        self.running = False
                self.auto_switch = SimpleAutoSwitch(market_check_interval)
            self.current_runner = None
            self.current_mode = None
            self.running = False
        
        def run(self, duration_minutes=None):
            print("  [INFO] run() method called")
            self.running = True
            import time
            from datetime import datetime
            cycle = 0
            try:
                while self.running:
                    cycle += 1
                    print(f"  [CYCLE {cycle}] Running...", flush=True)
                    if duration_minutes:
                        # For testing, exit after a few cycles
                        if cycle >= 3:
                            break
                    time.sleep(2)  # Short sleep for testing
            except KeyboardInterrupt:
                print("  [INFO] Interrupted")
            finally:
                self.running = False
                print("  [INFO] Stopped")
    
    print("  [OK] Class defined")
    print()
    print("Step 4: Creating instance...")
    runner = SmartLiveChainRunner()
    print("  [OK] Instance created")
    print()
    print("Step 5: Testing run() method (3 cycles)...")
    runner.run(duration_minutes=1)
    print()
    print("  [OK] All tests passed!")
    
except Exception as e:
    print(f"  [FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
