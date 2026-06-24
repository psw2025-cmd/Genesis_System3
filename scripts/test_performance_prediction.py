"""
Test Performance Prediction and Profit Validation
"""

import json
from datetime import datetime

import requests

API_BASE = "http://localhost:8000"


def test_portfolio_prediction():
    """Test portfolio prediction"""
    print("\n[TEST 1] Portfolio Prediction")
    print("-" * 50)

    try:
        response = requests.get(f"{API_BASE}/api/predict/portfolio", timeout=5)
        data = response.json()

        if data.get("status") == "ok":
            pred = data.get("prediction", {})
            portfolio = pred.get("portfolio_prediction", {})

            print(f"[PASS] Status: {data['status']}")
            print(f"   Positions: {portfolio.get('position_count', 0)}")
            print(f"   Predicted PnL: Rs{portfolio.get('predicted_pnl', 0):.2f}")
            print(f"   Avg Confidence: {portfolio.get('average_confidence', 0):.3f}")
            print(f"   Total Exposure: Rs{portfolio.get('total_exposure', 0):.2f}")

            return True
        else:
            print(f"[WARN] Status: {data.get('status')}")
            print(f"   Message: {data.get('message', 'Unknown')}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_performance_prediction():
    """Test performance prediction"""
    print("\n[TEST 2] Performance Prediction")
    print("-" * 50)

    try:
        response = requests.get(f"{API_BASE}/api/predict/performance", timeout=5)
        data = response.json()

        if data.get("status") == "ok":
            current = data.get("current_performance", {})
            predicted = data.get("predicted_performance", {})

            print(f"[PASS] Status: {data['status']}")
            print(f"\n   Current Performance:")
            print(f"     Total PnL: Rs{current.get('total_pnl', 0):.2f}")
            print(f"     Total Trades: {current.get('total_trades', 0)}")
            print(f"     Win Rate: {current.get('win_rate', 0):.1f}%")
            print(f"     Open Positions: {current.get('open_positions', 0)}")

            print(f"\n   Predicted Performance:")
            print(f"     Projected PnL: Rs{predicted.get('projected_pnl', 0):.2f}")
            print(f"     Projected Win Rate: {predicted.get('projected_win_rate', 0):.1f}%")
            print(f"     Confidence: {predicted.get('confidence', 0):.3f}")

            return True
        else:
            print(f"[WARN] Status: {data.get('status')}")
            print(f"   Message: {data.get('message', 'Unknown')}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_profit_validation():
    """Test profit validation"""
    print("\n[TEST 3] Profit Validation (All Positions)")
    print("-" * 50)

    try:
        response = requests.get(f"{API_BASE}/api/validate/profit/all", timeout=5)
        data = response.json()

        if data.get("status") == "ok":
            summary = data.get("summary", {})
            validations = data.get("validations", [])

            print(f"[PASS] Status: {data['status']}")
            print(f"   Total Positions: {data.get('total_positions', 0)}")
            print(f"\n   Validation Summary:")
            print(f"     Pass: {summary.get('pass_count', 0)}")
            print(f"     Warn: {summary.get('warn_count', 0)}")
            print(f"     Fail: {summary.get('fail_count', 0)}")
            print(f"     All Pass: {summary.get('all_pass', False)}")

            if validations:
                print(f"\n   Position Details:")
                for val in validations[:5]:  # Show first 5
                    pos_id = val.get("position_id", "unknown")
                    v = val.get("validation", {})
                    status = v.get("validation_status", "UNKNOWN")
                    confidence = v.get("confidence", 0)

                    print(f"     {pos_id}: {status} (Confidence: {confidence:.3f})")

            return True
        else:
            print(f"[WARN] Status: {data.get('status')}")
            print(f"   Message: {data.get('message', 'Unknown')}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def test_individual_position():
    """Test individual position prediction"""
    print("\n[TEST 4] Individual Position Prediction")
    print("-" * 50)

    # First get positions
    try:
        response = requests.get(f"{API_BASE}/api/positions", timeout=5)
        positions_data = response.json()
        positions = positions_data.get("positions", [])

        if not positions:
            print("[WARN] No open positions to test")
            return False

        # Test first position
        position = positions[0]
        position_id = position.get("position_id", "unknown")

        print(f"   Testing Position: {position_id}")

        # Predict profit
        response = requests.get(f"{API_BASE}/api/predict/profit/{position_id}", timeout=5)
        data = response.json()

        if data.get("status") == "ok":
            pred = data.get("prediction", {})

            print(f"[PASS] Prediction successful")
            print(f"   Predicted PnL: Rs{pred.get('predicted_pnl', 0):.2f}")
            print(f"   Confidence: {pred.get('confidence', 0):.3f}")
            print(f"   Current PnL: Rs{pred.get('current_pnl', 0):.2f}")

            risk = pred.get("risk_metrics", {})
            if risk:
                print(f"   Risk-Reward: {risk.get('risk_reward_ratio', 0):.2f}")
                print(f"   Prob of Profit: {risk.get('probability_of_profit', 0):.3f}")

            return True
        else:
            print(f"[WARN] Status: {data.get('status')}")
            print(f"   Message: {data.get('message', 'Unknown')}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("PERFORMANCE PREDICTION & PROFIT VALIDATION TEST")
    print("=" * 60)

    results = {
        "portfolio_prediction": test_portfolio_prediction(),
        "performance_prediction": test_performance_prediction(),
        "profit_validation": test_profit_validation(),
        "individual_position": test_individual_position(),
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
        print("\n[SUCCESS] ALL TESTS PASSED - SYSTEM IS WORKING!")
    else:
        print("\n[WARN] SOME TESTS FAILED - REVIEW ABOVE")

    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
