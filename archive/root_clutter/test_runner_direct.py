"""Direct test of smart_live_chain_runner"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

print("="*80)
print("TESTING SMART LIVE CHAIN RUNNER")
print("="*80)
print()

try:
    print("1. Importing SmartLiveChainRunner...")
    from scripts.smart_live_chain_runner import SmartLiveChainRunner
    print("   ✅ Import successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("2. Creating runner instance...")
    runner = SmartLiveChainRunner(
        refresh_interval=5,
        market_check_interval=30,
        use_websocket=False
    )
    print("   ✅ Runner created")
except Exception as e:
    print(f"   ❌ Creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("3. Testing run() method (will run for 10 seconds)...")
print("="*80)
print()

try:
    import signal
    import threading
    
    def timeout_handler():
        import time
        time.sleep(10)
        print("\n[TEST] 10 seconds elapsed - stopping test")
        runner.running = False
    
    timer = threading.Timer(10.0, timeout_handler)
    timer.start()
    
    runner.run(duration_minutes=None)
    timer.cancel()
    
    print()
    print("✅ Test completed successfully")
except KeyboardInterrupt:
    print("\n✅ Test interrupted by user")
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
