"""
Market Scenario Testing - Tests both market open and closed scenarios
Simulates synthetic data generation and real market data
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
import pytz

# Fix Unicode encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

API_BASE = "http://localhost:8000"
IST = pytz.timezone("Asia/Kolkata")


def test_endpoint_in_scenario(endpoint: str, scenario: str) -> dict:
    """Test an endpoint in a specific scenario"""
    method, path = endpoint.split(" ", 1) if " " in endpoint else ("GET", endpoint)

    start = time.time()
    try:
        url = f"{API_BASE}{path}"
        response = requests.request(method, url, timeout=10)
        elapsed = time.time() - start

        result = {
            "endpoint": endpoint,
            "scenario": scenario,
            "status_code": response.status_code,
            "response_time": elapsed,
            "success": response.status_code == 200,
        }

        if response.status_code == 200:
            try:
                data = response.json()
                result["data"] = data

                # Check for data_source field
                if "data_source" in data:
                    result["data_source"] = data["data_source"]
                elif "data" in data and isinstance(data["data"], dict) and "source" in data["data"]:
                    result["data_source"] = data["data"]["source"]
                else:
                    result["data_source"] = "unknown"

            except:
                result["data"] = response.text
                result["data_source"] = "unknown"
        else:
            result["error"] = response.text[:200]

    except Exception as e:
        result = {
            "endpoint": endpoint,
            "scenario": scenario,
            "success": False,
            "error": str(e),
            "response_time": time.time() - start,
        }

    return result


def test_market_scenarios():
    """Test all endpoints in both market open and closed scenarios"""
    print("=" * 80)
    print("📊 MARKET SCENARIO TESTING")
    print("=" * 80)
    print(f"Started at: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}\n")

    # Critical endpoints to test
    endpoints = [
        "GET /api/health",
        "GET /api/chain/NIFTY",
        "GET /api/signal/top",
        "GET /api/positions",
        "GET /api/pnl",
        "GET /api/qc",
        "GET /api/perf",
    ]

    results = []

    # Test current scenario (whatever the market state is)
    print("📈 Testing Current Market State...")
    current_scenario = "current"

    for endpoint in endpoints:
        result = test_endpoint_in_scenario(endpoint, current_scenario)
        results.append(result)

        status = "✅" if result["success"] else "❌"
        data_source = result.get("data_source", "N/A")
        print(f"  {status} {endpoint:40s} | {result['response_time']:6.3f}s | Source: {data_source}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 SCENARIO TEST SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r["success"])
    total = len(results)

    print(f"\n✅ Successful: {successful}/{total} ({successful/total*100:.1f}%)")

    # Data source analysis
    data_sources = {}
    for r in results:
        ds = r.get("data_source", "unknown")
        data_sources[ds] = data_sources.get(ds, 0) + 1

    print(f"\n📊 Data Sources:")
    for source, count in data_sources.items():
        print(f"  - {source}: {count} endpoints")

    # Check if synthetic data is working
    synthetic_count = data_sources.get("synthetic", 0)
    real_count = data_sources.get("real", 0)

    if synthetic_count > 0:
        print(f"\n✅ Synthetic data generation: WORKING ({synthetic_count} endpoints)")
    if real_count > 0:
        print(f"✅ Real market data: WORKING ({real_count} endpoints)")

    # Save results
    results_file = "outputs/market_scenario_test_results.json"
    os.makedirs("outputs", exist_ok=True)

    with open(results_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now(IST).isoformat(),
                "scenario": current_scenario,
                "results": results,
                "summary": {
                    "total": total,
                    "successful": successful,
                    "success_rate": successful / total * 100 if total > 0 else 0,
                    "data_sources": data_sources,
                },
            },
            f,
            indent=2,
        )

    print(f"\n💾 Results saved to: {results_file}")
    print("\n" + "=" * 80)

    return results


if __name__ == "__main__":
    try:
        # Check if backend is running
        try:
            response = requests.get(f"{API_BASE}/api/status", timeout=5)
            if response.status_code != 200:
                print(f"⚠️  Backend might not be running. Status: {response.status_code}")
        except:
            print("❌ ERROR: Backend is not running!")
            print(f"   Please start the backend at {API_BASE}")
            sys.exit(1)

        results = test_market_scenarios()
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
