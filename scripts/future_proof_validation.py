"""
Future-Proof Validation - Ensures system is robust and maintainable
Tests error handling, edge cases, and system resilience
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import pytz
import requests

# Fix Unicode encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"
IST = pytz.timezone("Asia/Kolkata")


def test_error_handling():
    """Test error handling for invalid requests"""
    print("\n" + "=" * 80)
    print("🛡️  TESTING ERROR HANDLING")
    print("=" * 80)

    error_tests = [
        ("GET", "/api/chain/INVALID_SYMBOL", 200),  # Should handle gracefully
        ("GET", "/api/chain/", 404),  # Missing symbol
        ("GET", "/api/nonexistent", 404),  # Non-existent endpoint
        ("GET", "/api/health?invalid=param", 200),  # Extra params (should work)
    ]

    results = []
    for method, endpoint, expected_status in error_tests:
        try:
            url = f"{API_BASE}{endpoint}"
            response = requests.request(method, url, timeout=5)
            passed = response.status_code == expected_status
            status = "✅" if passed else "❌"
            print(f"  {status} {method} {endpoint:40s} | Expected: {expected_status}, Got: {response.status_code}")
            results.append(
                {"endpoint": endpoint, "expected": expected_status, "actual": response.status_code, "passed": passed}
            )
        except Exception as e:
            print(f"  ❌ {method} {endpoint:40s} | Error: {str(e)[:50]}")
            results.append(
                {"endpoint": endpoint, "expected": expected_status, "actual": "error", "passed": False, "error": str(e)}
            )

    passed = sum(1 for r in results if r["passed"])
    print(f"\n  ✅ Error Handling: {passed}/{len(results)} tests passed")
    return results


def test_concurrent_access():
    """Test concurrent access to critical endpoints"""
    print("\n" + "=" * 80)
    print("👥 TESTING CONCURRENT ACCESS (Simulating Multiple Users)")
    print("=" * 80)

    endpoints = [
        "/api/health",
        "/api/chain/NIFTY",
        "/api/signal/top",
        "/api/positions",
        "/api/pnl",
    ]

    def make_request(endpoint):
        start = time.time()
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            elapsed = time.time() - start
            return {
                "endpoint": endpoint,
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": elapsed,
            }
        except Exception as e:
            return {"endpoint": endpoint, "success": False, "error": str(e), "response_time": time.time() - start}

    # Simulate 100 concurrent requests (20 per endpoint)
    print("  Simulating 100 concurrent requests (20 per endpoint)...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for endpoint in endpoints:
            for _ in range(20):
                futures.append(executor.submit(make_request, endpoint))

        results = []
        for future in as_completed(futures):
            results.append(future.result())

    total_time = time.time() - start_time
    successful = sum(1 for r in results if r["success"])

    print(f"  ✅ Total Requests: {len(results)}")
    print(f"  ✅ Successful: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print(f"  ⏱️  Total Time: {total_time:.2f}s")
    print(f"  📊 Requests/Second: {len(results)/total_time:.2f}")

    # Group by endpoint
    by_endpoint = {}
    for r in results:
        ep = r["endpoint"]
        if ep not in by_endpoint:
            by_endpoint[ep] = {"total": 0, "success": 0, "times": []}
        by_endpoint[ep]["total"] += 1
        if r["success"]:
            by_endpoint[ep]["success"] += 1
        if "response_time" in r:
            by_endpoint[ep]["times"].append(r["response_time"])

    print(f"\n  📊 Per-Endpoint Results:")
    for endpoint, stats in by_endpoint.items():
        avg_time = sum(stats["times"]) / len(stats["times"]) if stats["times"] else 0
        success_rate = (stats["success"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(
            f"    - {endpoint:30s} | {stats['success']:3d}/{stats['total']:3d} ({success_rate:5.1f}%) | Avg: {avg_time:.3f}s"
        )

    return results


def test_data_consistency_across_requests():
    """Test that data remains consistent across multiple requests"""
    print("\n" + "=" * 80)
    print("🔄 TESTING DATA CONSISTENCY")
    print("=" * 80)

    # Make 10 requests to the same endpoint and check consistency
    endpoint = "/api/health"
    print(f"  Testing {endpoint} (10 requests)...")

    responses = []
    for i in range(10):
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                responses.append(data)
        except Exception as e:
            print(f"    ❌ Request {i+1} failed: {e}")

    if len(responses) < 2:
        print("  ⚠️  Not enough successful responses to test consistency")
        return []

    # Check key fields for consistency
    consistency_checks = []

    # Check cycle_count (should be same or increasing)
    cycle_counts = [r.get("cycle_count", 0) for r in responses]
    if all(c == cycle_counts[0] for c in cycle_counts) or all(
        cycle_counts[i] <= cycle_counts[i + 1] for i in range(len(cycle_counts) - 1)
    ):
        consistency_checks.append({"field": "cycle_count", "consistent": True})
        print("  ✅ cycle_count: Consistent")
    else:
        consistency_checks.append({"field": "cycle_count", "consistent": False})
        print("  ⚠️  cycle_count: Inconsistent (may be expected if system is running)")

    # Check data_source (should be same)
    data_sources = [r.get("data_source", "unknown") for r in responses]
    if len(set(data_sources)) == 1:
        consistency_checks.append({"field": "data_source", "consistent": True})
        print(f"  ✅ data_source: Consistent ({data_sources[0]})")
    else:
        consistency_checks.append({"field": "data_source", "consistent": False})
        print(f"  ⚠️  data_source: Inconsistent ({set(data_sources)})")

    return consistency_checks


def run_future_proof_validation():
    """Run all future-proof validation tests"""
    print("=" * 80)
    print("🔮 FUTURE-PROOF VALIDATION TEST SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}")

    all_results = {}

    # 1. Error handling
    all_results["error_handling"] = test_error_handling()

    # 2. Concurrent access
    all_results["concurrent_access"] = test_concurrent_access()

    # 3. Data consistency
    all_results["data_consistency"] = test_data_consistency_across_requests()

    # Summary
    print("\n" + "=" * 80)
    print("📊 FUTURE-PROOF VALIDATION SUMMARY")
    print("=" * 80)

    error_handling_passed = sum(1 for r in all_results["error_handling"] if r["passed"])
    concurrent_success = sum(1 for r in all_results["concurrent_access"] if r["success"])
    consistency_passed = sum(1 for r in all_results["data_consistency"] if r.get("consistent", False))

    print(f"\n✅ Error Handling: {error_handling_passed}/{len(all_results['error_handling'])} tests passed")
    print(f"✅ Concurrent Access: {concurrent_success}/{len(all_results['concurrent_access'])} requests successful")
    print(f"✅ Data Consistency: {consistency_passed}/{len(all_results['data_consistency'])} checks passed")

    # Save results
    results_file = "outputs/future_proof_validation_results.json"
    os.makedirs("outputs", exist_ok=True)

    with open(results_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now(IST).isoformat(),
                "results": all_results,
                "summary": {
                    "error_handling": f"{error_handling_passed}/{len(all_results['error_handling'])}",
                    "concurrent_access": f"{concurrent_success}/{len(all_results['concurrent_access'])}",
                    "data_consistency": f"{consistency_passed}/{len(all_results['data_consistency'])}",
                },
            },
            f,
            indent=2,
        )

    print(f"\n💾 Results saved to: {results_file}")
    print("\n" + "=" * 80)
    print("✅ FUTURE-PROOF VALIDATION COMPLETE")
    print("=" * 80)

    return all_results


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

        results = run_future_proof_validation()
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
