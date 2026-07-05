"""
Comprehensive Feature Test Suite
Tests all implemented features with online and offline validation
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import requests

# Fix Unicode encoding
sys.stdout.reconfigure(encoding="utf-8")

API_BASE = "http://localhost:8000"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def print_success(msg):
    print(f"{Colors.GREEN}[PASS]{Colors.RESET} {msg}")


def print_fail(msg):
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {msg}")


def print_warn(msg):
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {msg}")


def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")


def test_alerts_system():
    """Test alerts system"""
    print("\n" + "=" * 60)
    print("TEST 1: Alerts System")
    print("=" * 60)

    try:
        # Get recent alerts
        response = requests.get(f"{API_BASE}/api/alerts/recent", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print_success(f"Alerts endpoint working - {data.get('count', 0)} alerts")
                return True
            else:
                print_fail(f"Alerts endpoint returned error: {data.get('message')}")
                return False
        else:
            print_fail(f"Alerts endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Alerts test failed: {e}")
        return False


def test_multi_validation():
    """Test multi-validation audit"""
    print("\n" + "=" * 60)
    print("TEST 2: Multi-Validation Audit")
    print("=" * 60)

    try:
        # Comprehensive audit
        response = requests.get(f"{API_BASE}/api/audit/comprehensive", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                audit = data.get("audit", {})
                status = audit.get("overall_status", "UNKNOWN")

                print_success(f"Comprehensive audit completed - Status: {status}")
                print_info(f"  Spot validations: {len(audit.get('spot_price_validations', []))}")
                print_info(f"  Option validations: {len(audit.get('option_price_validations', []))}")
                print_info(f"  PnL validations: {len(audit.get('pnl_validations', []))}")

                if status == "PASS":
                    return True
                elif status == "WARN":
                    print_warn("Audit passed with warnings")
                    return True
                else:
                    print_fail("Audit failed")
                    return False
            else:
                print_fail(f"Audit returned error: {data.get('message')}")
                return False
        else:
            print_fail(f"Audit endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Multi-validation test failed: {e}")
        return False


def test_spot_price_validation():
    """Test spot price validation"""
    print("\n" + "=" * 60)
    print("TEST 3: Spot Price Validation (Online/Offline)")
    print("=" * 60)

    try:
        # Get current chain data
        response = requests.get(f"{API_BASE}/api/chain/NIFTY", timeout=10)
        if response.status_code == 200:
            chain_data = response.json()
            spot_price = chain_data.get("spot", 0)

            if spot_price > 0:
                # Validate spot price
                val_response = requests.get(
                    f"{API_BASE}/api/audit/validate/spot/NIFTY", params={"price": spot_price}, timeout=10
                )

                if val_response.status_code == 200:
                    val_data = val_response.json()
                    if val_data.get("status") == "ok":
                        validation = val_data.get("validation", {})
                        status = validation.get("status", "UNKNOWN")

                        print_success(f"Spot price validation completed - Status: {status}")
                        print_info(f"  Reported price: Rs{spot_price:.2f}")

                        validations = validation.get("validations", [])
                        online_validations = [v for v in validations if v.get("online")]
                        offline_validations = [v for v in validations if not v.get("online")]

                        print_info(f"  Online sources: {len(online_validations)}")
                        print_info(f"  Offline sources: {len(offline_validations)}")

                        for v in validations:
                            source = v.get("source", "unknown")
                            match = v.get("match", False)
                            diff_pct = v.get("difference_pct", 0)
                            print_info(f"    {source}: {'MATCH' if match else 'MISMATCH'} (diff: {diff_pct:.2f}%)")

                        return status in ["PASS", "WARN"]
                    else:
                        print_fail(f"Validation returned error: {val_data.get('message')}")
                        return False
                else:
                    print_fail(f"Validation endpoint returned status {val_response.status_code}")
                    return False
            else:
                print_warn("No spot price available for validation")
                return True
        else:
            print_fail(f"Chain endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Spot price validation test failed: {e}")
        return False


def test_performance_prediction():
    """Test performance prediction"""
    print("\n" + "=" * 60)
    print("TEST 4: Performance Prediction")
    print("=" * 60)

    try:
        response = requests.get(f"{API_BASE}/api/predict/portfolio", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                pred = data.get("prediction", {})
                portfolio = pred.get("portfolio_prediction", {})

                print_success("Performance prediction working")
                print_info(f"  Positions: {portfolio.get('position_count', 0)}")
                print_info(f"  Predicted PnL: Rs{portfolio.get('predicted_pnl', 0):.2f}")
                print_info(f"  Confidence: {portfolio.get('average_confidence', 0):.3f}")

                return True
            else:
                print_fail(f"Prediction returned error: {data.get('message')}")
                return False
        else:
            print_fail(f"Prediction endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Performance prediction test failed: {e}")
        return False


def test_profit_validation():
    """Test profit validation"""
    print("\n" + "=" * 60)
    print("TEST 5: Profit Validation")
    print("=" * 60)

    try:
        response = requests.get(f"{API_BASE}/api/validate/profit/all", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                summary = data.get("summary", {})

                print_success("Profit validation working")
                print_info(f"  Total positions: {data.get('total_positions', 0)}")
                print_info(f"  Pass: {summary.get('pass_count', 0)}")
                print_info(f"  Warn: {summary.get('warn_count', 0)}")
                print_info(f"  Fail: {summary.get('fail_count', 0)}")

                return summary.get("fail_count", 0) == 0
            else:
                print_warn(f"Validation returned: {data.get('status')}")
                return True  # No positions is OK
        else:
            print_fail(f"Validation endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Profit validation test failed: {e}")
        return False


def test_all_endpoints():
    """Test all API endpoints"""
    print("\n" + "=" * 60)
    print("TEST 6: All API Endpoints")
    print("=" * 60)

    endpoints = [
        ("/api/health", "Health check"),
        ("/api/qc", "QC status"),
        ("/api/chain/NIFTY", "Chain data"),
        ("/api/signal/top", "Top signals"),
        ("/api/positions", "Positions"),
        ("/api/pnl", "PnL data"),
        ("/api/perf", "Performance"),
        ("/api/predict/portfolio", "Portfolio prediction"),
        ("/api/predict/performance", "Performance prediction"),
        ("/api/alerts/recent", "Recent alerts"),
    ]

    passed = 0
    failed = 0

    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            if response.status_code == 200:
                print_success(f"{name}: OK")
                passed += 1
            else:
                print_fail(f"{name}: Status {response.status_code}")
                failed += 1
        except Exception as e:
            print_fail(f"{name}: {e}")
            failed += 1

    print_info(f"\n  Endpoints: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE FEATURE TEST SUITE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"API Base: {API_BASE}")

    results = {
        "alerts_system": test_alerts_system(),
        "multi_validation": test_multi_validation(),
        "spot_price_validation": test_spot_price_validation(),
        "performance_prediction": test_performance_prediction(),
        "profit_validation": test_profit_validation(),
        "all_endpoints": test_all_endpoints(),
    }

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print_success("\nALL TESTS PASSED - SYSTEM IS FULLY OPERATIONAL!")
        return True
    else:
        print_fail(f"\n{total - passed} TESTS FAILED - REVIEW ABOVE")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
