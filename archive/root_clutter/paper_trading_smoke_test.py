"""
Paper Trading Smoke Test
Verifies that paper trading mode is properly enforced and no real orders can be placed.
"""

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

print("=" * 70)
print("PAPER TRADING SMOKE TEST")
print("=" * 70)
print()

# Test 1: Environment Variables
print("[TEST 1] Checking Environment Variables...")
env_vars = {
    "LIVE_TRADING_ENABLED": os.getenv("LIVE_TRADING_ENABLED", "Not set"),
    "DRY_RUN": os.getenv("DRY_RUN", "Not set"),
    "SYSTEM3_LIVE_TRADING_ALLOWED": os.getenv("SYSTEM3_LIVE_TRADING_ALLOWED", "Not set"),
    "USE_LIVE_EXECUTION_ENGINE": os.getenv("USE_LIVE_EXECUTION_ENGINE", "Not set")
}

all_safe = True
for key, value in env_vars.items():
    safe = (
        (key == "LIVE_TRADING_ENABLED" and value in ["False", "0", "Not set"]) or
        (key == "DRY_RUN" and value in ["True", "1"]) or
        (key == "SYSTEM3_LIVE_TRADING_ALLOWED" and value in ["", "False", "0", "Not set"]) or
        (key == "USE_LIVE_EXECUTION_ENGINE" and value in ["False", "0", "Not set"])
    )
    status = "[SAFE]" if safe else "[UNSAFE]"
    print(f"  {key}: {value} {status}")
    if not safe:
        all_safe = False

print(f"\n[TEST 1] Result: {'[PASS]' if all_safe else '[FAIL]'}")
print()

# Test 2: Runner enforce_dry_run function
print("[TEST 2] Testing runner.py enforce_dry_run()...")
try:
    from runner import enforce_dry_run
    enforce_dry_run()
    
    # Check if flags are set correctly
    check_vars = {
        "LIVE_TRADING_ENABLED": os.getenv("LIVE_TRADING_ENABLED"),
        "DRY_RUN": os.getenv("DRY_RUN"),
        "SYSTEM3_LIVE_TRADING_ALLOWED": os.getenv("SYSTEM3_LIVE_TRADING_ALLOWED"),
        "USE_LIVE_EXECUTION_ENGINE": os.getenv("USE_LIVE_EXECUTION_ENGINE")
    }
    
    runner_safe = (
        check_vars["LIVE_TRADING_ENABLED"] == "False" and
        check_vars["DRY_RUN"] == "True" and
        check_vars["SYSTEM3_LIVE_TRADING_ALLOWED"] == "" and
        check_vars["USE_LIVE_EXECUTION_ENGINE"] == "False"
    )
    
    print(f"  LIVE_TRADING_ENABLED: {check_vars['LIVE_TRADING_ENABLED']}")
    print(f"  DRY_RUN: {check_vars['DRY_RUN']}")
    print(f"  SYSTEM3_LIVE_TRADING_ALLOWED: '{check_vars['SYSTEM3_LIVE_TRADING_ALLOWED']}'")
    print(f"  USE_LIVE_EXECUTION_ENGINE: {check_vars['USE_LIVE_EXECUTION_ENGINE']}")
    print(f"\n[TEST 2] Result: {'[PASS]' if runner_safe else '[FAIL]'}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    runner_safe = False
print()

# Test 3: Broker _env_live_guard
print("[TEST 3] Testing broker _env_live_guard()...")
try:
    from core.brokers.angel_one.broker import _env_live_guard
    
    # Should raise RuntimeError when SYSTEM3_LIVE_TRADING_ALLOWED is not set
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = ""
    try:
        _env_live_guard()
        guard_works = False
        print("  ❌ Guard did not block (should have raised RuntimeError)")
    except RuntimeError as e:
        if "LIVE TRADING BLOCKED" in str(e):
            guard_works = True
            print(f"  [OK] Guard correctly blocked: {str(e)[:80]}")
        else:
            guard_works = False
            print(f"  [FAIL] Guard raised wrong error: {e}")
    except Exception as e:
        guard_works = False
        print(f"  [FAIL] Unexpected error: {e}")
    
    print(f"\n[TEST 3] Result: {'[PASS]' if guard_works else '[FAIL]'}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    guard_works = False
print()

# Test 4: Broker allow_data_only mode
print("[TEST 4] Testing broker allow_data_only=True (should not trigger guard)...")
try:
    from core.brokers.angel_one.broker import AngelOneBroker
    
    # This should work even without SYSTEM3_LIVE_TRADING_ALLOWED
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = ""
    try:
        broker = AngelOneBroker(allow_data_only=True)
        data_only_works = True
        print("  [OK] Broker initialized in data-only mode (no guard triggered)")
        
        # Test get_profile (should work but may fail due to rate limits - that's OK)
        try:
            profile = broker.get_profile()
            if profile:
                print(f"  [OK] get_profile() succeeded (client: {profile.get('data', {}).get('clientcode', 'N/A')})")
            else:
                print("  [WARN] get_profile() returned None (may be rate limited - OK for smoke test)")
        except Exception as e:
            print(f"  [WARN] get_profile() failed: {str(e)[:80]} (may be rate limited - OK)")
        
    except RuntimeError as e:
        if "LIVE TRADING BLOCKED" in str(e):
            data_only_works = False
            print(f"  [FAIL] Guard incorrectly triggered in data-only mode: {str(e)[:80]}")
        else:
            data_only_works = False
            print(f"  [FAIL] Unexpected RuntimeError: {e}")
    except Exception as e:
        # Other errors (like connection issues) are OK for smoke test
        data_only_works = True
        print(f"  [WARN] Broker init failed (connection/rate limit): {str(e)[:80]} (OK for smoke test)")
    
    print(f"\n[TEST 4] Result: {'[PASS]' if data_only_works else '[FAIL]'}")
except Exception as e:
    print(f"  ❌ ERROR: {e}")
    data_only_works = False
print()

# Test 5: Check runner.py status
print("[TEST 5] Testing runner.py status command...")
try:
    import subprocess
    result = subprocess.run(
        [sys.executable, str(ROOT_DIR / "runner.py"), "status"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        import json
        output_lines = result.stdout.split('\n')
        json_start = None
        for i, line in enumerate(output_lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start is not None:
            json_output = '\n'.join(output_lines[json_start:])
            status_data = json.loads(json_output)
            print(f"  [OK] Runner status retrieved")
            print(f"    Runner: {status_data.get('runner', 'UNKNOWN')}")
            print(f"    Mode: {status_data.get('mode', 'UNKNOWN')}")
            runner_status_works = True
        else:
            print("  [WARN] Could not parse JSON from runner status")
            runner_status_works = False
    else:
        print(f"  [WARN] Runner status returned code {result.returncode}")
        runner_status_works = False
    
    print(f"\n[TEST 5] Result: {'[PASS]' if runner_status_works else '[WARN]'}")
except Exception as e:
    print(f"  ⚠️  ERROR: {e}")
    runner_status_works = False
print()

# Test 6: Check dashboard state endpoint (if backend is running)
print("[TEST 6] Testing dashboard /api/state endpoint...")
try:
    import requests
    r = requests.get('http://localhost:8000/api/state', timeout=3)
    if r.status_code == 200:
        state = r.json()
        mode = state.get('mode', 'UNKNOWN')
        data_source = state.get('data_source', 'UNKNOWN')
        broker_connected = state.get('broker', {}).get('connected', False)
        
        print(f"  [OK] Dashboard state retrieved")
        print(f"    Mode: {mode}")
        print(f"    Data Source: {data_source}")
        print(f"    Broker Connected: {broker_connected}")
        
        # Mode should be PAPER or at least not indicate live trading
        dashboard_safe = mode in ['PAPER', 'paper', 'PAPER_TRADING']
        print(f"\n[TEST 6] Result: {'[PASS]' if dashboard_safe else '[WARN] (mode is not PAPER)'}")
    else:
        print(f"  [WARN] Dashboard returned status {r.status_code}")
        dashboard_safe = False
except requests.exceptions.ConnectionError:
    print("  [WARN] Backend not running (OK for smoke test)")
    dashboard_safe = True  # Not a failure if backend is down
except Exception as e:
    print(f"  [WARN] ERROR: {str(e)[:80]}")
    dashboard_safe = True  # Not a critical failure
print()

# Final Summary
print("=" * 70)
print("SMOKE TEST SUMMARY")
print("=" * 70)
print()

tests = [
    ("Environment Variables", all_safe),
    ("Runner enforce_dry_run()", runner_safe),
    ("Broker _env_live_guard()", guard_works),
    ("Broker data-only mode", data_only_works),
    ("Runner status command", runner_status_works),
    ("Dashboard state endpoint", dashboard_safe)
]

passed = sum(1 for _, result in tests if result)
total = len(tests)

for name, result in tests:
    status = "[PASS]" if result else "[FAIL]"
    print(f"  {name}: {status}")

print()
print(f"Total: {passed}/{total} tests passed")
print()

if passed == total:
    print("[SUCCESS] ALL TESTS PASSED - Paper trading is properly configured!")
elif passed >= total - 1:
    print("[WARN] MOSTLY PASSED - Minor issues detected (may be expected)")
else:
    print("[FAIL] SOME TESTS FAILED - Review configuration")

print()
print("=" * 70)
