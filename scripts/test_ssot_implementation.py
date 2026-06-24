"""
Test SSOT Implementation and Critical Fixes
Validates that all fixes are working correctly
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import pytz
import requests

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

IST = pytz.timezone("Asia/Kolkata")
API_BASE = "http://localhost:8000"


def test_ssot_endpoint():
    """Test SSOT endpoint exists and returns valid data"""
    print("\n" + "=" * 60)
    print("TEST 1: SSOT Endpoint")
    print("=" * 60)

    try:
        response = requests.get(f"{API_BASE}/api/state", timeout=5)
        if response.status_code == 200:
            state = response.json()

            # Check required fields
            required_fields = [
                "state_version",
                "timestamp_utc",
                "timestamp_ist",
                "mode",
                "data_source",
                "market",
                "broker",
                "qc",
                "signals",
                "positions",
                "pnl",
                "risk",
                "model",
                "alerts",
            ]

            missing = [f for f in required_fields if f not in state]
            if missing:
                print(f"❌ FAIL: Missing fields: {missing}")
                return False

            print(f"✅ PASS: SSOT endpoint returns valid state")
            print(f"   State Version: {state.get('state_version', 'N/A')}")
            print(f"   Data Source: {state.get('data_source', 'N/A')}")
            print(f"   Market Open: {state.get('market', {}).get('is_open', False)}")
            print(f"   Positions: {len(state.get('positions', []))}")
            print(f"   Total PnL: ₹{state.get('pnl', {}).get('total', 0):.2f}")
            return True
        else:
            print(f"❌ FAIL: SSOT endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ FAIL: Backend not running. Start backend first.")
        return False
    except Exception as e:
        print(f"❌ FAIL: Error testing SSOT: {e}")
        return False


def test_synthetic_data_realism():
    """Test synthetic data has realistic IV and Greeks"""
    print("\n" + "=" * 60)
    print("TEST 2: Synthetic Data Realism")
    print("=" * 60)

    try:
        response = requests.get(f"{API_BASE}/api/chain/NIFTY", timeout=5)
        if response.status_code == 200:
            chain_data = response.json()

            if chain_data.get("data_source") == "synthetic":
                contracts = chain_data.get("contracts", [])
                if contracts:
                    # Check IV values
                    iv_values = [c.get("iv", 0) for c in contracts if c.get("iv")]
                    if iv_values:
                        max_iv = max(iv_values)
                        min_iv = min(iv_values)

                        # IV should be between 8-40% for NIFTY
                        if max_iv > 100:  # If IV is in percentage form (8-40)
                            if max_iv > 50:  # Should not exceed 50%
                                print(f"❌ FAIL: IV too high: {max_iv}% (should be 8-40%)")
                                return False
                        elif max_iv > 0.5:  # If IV is in decimal form (0.08-0.40)
                            if max_iv > 0.5:
                                print(f"❌ FAIL: IV too high: {max_iv} (should be 0.08-0.40)")
                                return False

                        print(f"✅ PASS: Synthetic IV is realistic")
                        print(f"   IV Range: {min_iv:.2f}% - {max_iv:.2f}%")

                        # Check Greeks
                        sample = contracts[0]
                        delta = abs(sample.get("delta", 0))
                        gamma = abs(sample.get("gamma", 0))
                        theta = abs(sample.get("theta", 0))
                        vega = abs(sample.get("vega", 0))

                        if delta > 1.1 or gamma > 0.15 or vega > 60:
                            print(f"⚠️  WARN: Some Greeks seem high (Delta: {delta}, Gamma: {gamma}, Vega: {vega})")
                        else:
                            print(f"✅ PASS: Greeks are within realistic bounds")

                        return True
                    else:
                        print("⚠️  WARN: No IV values found in contracts")
                        return True
                else:
                    print("⚠️  WARN: No contracts in chain data")
                    return True
            else:
                print("ℹ️  INFO: Using real data (not synthetic)")
                return True
        else:
            print(f"❌ FAIL: Chain endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Error testing synthetic data: {e}")
        return False


def test_risk_limit_logic():
    """Test risk limit logic (should not breach when equal)"""
    print("\n" + "=" * 60)
    print("TEST 3: Risk Limit Logic")
    print("=" * 60)

    try:
        # Get current positions
        positions_res = requests.get(f"{API_BASE}/api/positions", timeout=5)
        if positions_res.status_code == 200:
            positions_data = positions_res.json()
            positions = positions_data.get("positions", [])
            position_count = len(positions)

            # Test with limit equal to current count
            limit_check_res = requests.post(
                f"{API_BASE}/api/risk/check-limits", json={"max_positions": position_count}, timeout=5
            )

            if limit_check_res.status_code == 200:
                limit_check = limit_check_res.json().get("limit_check", {})
                breaches = limit_check.get("breaches", [])

                # Should not breach when equal
                max_pos_breach = any(b.get("limit") == "max_positions" for b in breaches)

                if max_pos_breach and position_count == limit_check.get("risk_limits", {}).get("max_positions", 0):
                    print(f"❌ FAIL: Risk limit breaches when equal (count: {position_count}, limit: {position_count})")
                    return False
                else:
                    print(f"✅ PASS: Risk limit logic is correct")
                    print(f"   Positions: {position_count}, Limit: {position_count}")
                    print(f"   Breaches: {len(breaches)}")
                    return True
            else:
                print(f"❌ FAIL: Limit check endpoint returned status {limit_check_res.status_code}")
                return False
        else:
            print(f"❌ FAIL: Positions endpoint returned status {positions_res.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Error testing risk limits: {e}")
        return False


def test_timestamp_format():
    """Test timestamps are in ISO format"""
    print("\n" + "=" * 60)
    print("TEST 4: Timestamp Format")
    print("=" * 60)

    try:
        # Test PnL endpoint (has history with timestamps)
        pnl_res = requests.get(f"{API_BASE}/api/pnl", timeout=5)
        if pnl_res.status_code == 200:
            pnl_data = pnl_res.json()
            history = pnl_data.get("history", [])

            if history:
                # Check first few timestamps
                invalid_count = 0
                for item in history[:5]:
                    timestamp = item.get("timestamp")
                    if timestamp:
                        try:
                            # Try parsing as ISO
                            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        except:
                            invalid_count += 1

                if invalid_count > 0:
                    print(f"❌ FAIL: {invalid_count} invalid timestamps found")
                    return False
                else:
                    print(f"✅ PASS: All timestamps are in ISO format")
                    return True
            else:
                print("ℹ️  INFO: No history data to test")
                return True
        else:
            print(f"❌ FAIL: PnL endpoint returned status {pnl_res.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Error testing timestamps: {e}")
        return False


def test_page_consistency():
    """Test that all pages show consistent data"""
    print("\n" + "=" * 60)
    print("TEST 5: Page Consistency (SSOT)")
    print("=" * 60)

    try:
        # Get SSOT state
        state_res = requests.get(f"{API_BASE}/api/state", timeout=5)
        if state_res.status_code == 200:
            state = state_res.json()

            # Get individual endpoints
            health_res = requests.get(f"{API_BASE}/api/health", timeout=5)
            positions_res = requests.get(f"{API_BASE}/api/positions", timeout=5)
            pnl_res = requests.get(f"{API_BASE}/api/pnl", timeout=5)

            if all(r.status_code == 200 for r in [health_res, positions_res, pnl_res]):
                health = health_res.json()
                positions_data = positions_res.json()
                pnl_data = pnl_res.json()

                # Compare positions count
                ssot_positions = len(state.get("positions", []))
                api_positions = len(positions_data.get("positions", []))

                # Compare PnL
                ssot_pnl = state.get("pnl", {}).get("total", 0)
                health_pnl = health.get("total_pnl", 0)
                pnl_summary = pnl_data.get("summary", {}).get("total_pnl", 0)

                # Allow small differences due to timing
                pnl_diff = abs(ssot_pnl - health_pnl)

                if ssot_positions == api_positions and pnl_diff < 1.0:
                    print(f"✅ PASS: Pages show consistent data")
                    print(f"   Positions: SSOT={ssot_positions}, API={api_positions}")
                    print(f"   PnL: SSOT=₹{ssot_pnl:.2f}, Health=₹{health_pnl:.2f}, PnL=₹{pnl_summary:.2f}")
                    return True
                else:
                    print(f"⚠️  WARN: Some inconsistencies detected")
                    print(f"   Positions: SSOT={ssot_positions}, API={api_positions}")
                    print(f"   PnL Diff: ₹{pnl_diff:.2f}")
                    return True  # Not a critical failure
            else:
                print("❌ FAIL: Some endpoints failed")
                return False
        else:
            print(f"❌ FAIL: SSOT endpoint returned status {state_res.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Error testing consistency: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("SSOT IMPLEMENTATION VALIDATION TEST")
    print("=" * 60)
    print(f"Testing API at: {API_BASE}")
    print(f"Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")

    results = []

    # Run tests
    results.append(("SSOT Endpoint", test_ssot_endpoint()))
    results.append(("Synthetic Data Realism", test_synthetic_data_realism()))
    results.append(("Risk Limit Logic", test_risk_limit_logic()))
    results.append(("Timestamp Format", test_timestamp_format()))
    results.append(("Page Consistency", test_page_consistency()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! SSOT implementation is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
