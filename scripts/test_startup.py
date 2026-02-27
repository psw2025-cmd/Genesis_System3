"""
Quick startup test - Verify script can run and produce output
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Fix Unicode
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

print("=" * 80, flush=True)
print("  STARTUP TEST - Verifying imports and initialization", flush=True)
print("=" * 80, flush=True)
print(flush=True)

try:
    print("[1] Testing imports...", flush=True)
    from scripts.smart_live_chain_runner import SmartLiveChainRunner

    print("  ✅ SmartLiveChainRunner imported", flush=True)

    print("[2] Creating runner instance...", flush=True)
    runner = SmartLiveChainRunner(refresh_interval=5, market_check_interval=30, use_websocket=False)
    print("  ✅ Runner created", flush=True)

    print("[3] Testing mode detection...", flush=True)
    mode_switched = runner.check_and_switch_mode()
    print(f"  ✅ Mode detection complete: {runner.current_mode}", flush=True)

    print(flush=True)
    print("=" * 80, flush=True)
    print("  ✅ ALL TESTS PASSED - System ready to run", flush=True)
    print("=" * 80, flush=True)
    print(flush=True)
    print("You can now run the full system.", flush=True)
    print(flush=True)

except Exception as e:
    print(f"", flush=True)
    print(f"❌ ERROR: {e}", flush=True)
    import traceback

    traceback.print_exc()
    sys.exit(1)
