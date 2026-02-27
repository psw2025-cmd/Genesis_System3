"""
Comprehensive API Endpoint Testing
Tests all endpoints including new enhanced signals endpoint
"""
import sys
import requests
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

BASE_URL = "http://localhost:8000"
TIMEOUT = 10

def test_endpoint(name: str, method: str, path: str, expected_status: int = 200) -> Dict[str, Any]:
    """Test a single API endpoint."""
    try:
        if method.upper() == "GET":
            response = requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(f"{BASE_URL}{path}", timeout=TIMEOUT)
        else:
            return {
                "name": name,
                "status": "SKIPPED",
                "error": f"Unsupported method: {method}"
            }
        
        result = {
            "name": name,
            "path": path,
            "method": method,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "status": "PASS" if response.status_code == expected_status else "FAIL",
            "response_time_ms": response.elapsed.total_seconds() * 1000
        }
        
        # Try to parse JSON
        try:
            data = response.json()
            result["has_json"] = True
            result["json_keys"] = list(data.keys()) if isinstance(data, dict) else []
        except:
            result["has_json"] = False
        
        return result
    except requests.exceptions.ConnectionError:
        return {
            "name": name,
            "path": path,
            "status": "FAIL",
            "error": "Connection refused - backend not running"
        }
    except Exception as e:
        return {
            "name": name,
            "path": path,
            "status": "FAIL",
            "error": str(e)
        }

def main():
    """Run all API endpoint tests."""
    print("=" * 60)
    print("COMPREHENSIVE API ENDPOINT TESTING")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    # Core endpoints
    endpoints = [
        ("Health", "GET", "/api/health"),
        ("State", "GET", "/api/state"),
        ("Chain NIFTY", "GET", "/api/chain/NIFTY"),
        ("Chain BANKNIFTY", "GET", "/api/chain/BANKNIFTY"),
        ("Signal Top", "GET", "/api/signal/top"),
        ("Signals Enhanced", "GET", "/api/signals/enhanced"),
        ("Signals", "GET", "/api/signals"),
        ("Positions", "GET", "/api/positions"),
        ("PnL", "GET", "/api/pnl"),
        ("QC", "GET", "/api/qc"),
        ("Performance", "GET", "/api/perf"),
        ("Learning Status", "GET", "/api/learning/status"),
        ("Learning Insights", "GET", "/api/learning/insights"),
        ("Validation Status", "GET", "/api/validation/status"),
        ("Forensic Report", "GET", "/api/forensic/report"),
        ("Broker Status", "GET", "/api/broker/status"),
        ("Broker Deps", "GET", "/api/broker/deps"),
        ("Debug State Source", "GET", "/api/debug/state_source"),
    ]
    
    results = []
    for name, method, path in endpoints:
        print(f"Testing {name}...", end=" ")
        result = test_endpoint(name, method, path)
        results.append(result)
        status_icon = "✅" if result.get("status") == "PASS" else "❌"
        print(f"{status_icon} {result.get('status', 'UNKNOWN')}")
        if "error" in result:
            print(f"   Error: {result['error']}")
    
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed = sum(1 for r in results if r.get("status") == "FAIL")
    skipped = sum(1 for r in results if r.get("status") == "SKIPPED")
    
    print(f"Total: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️  Skipped: {skipped}")
    print()
    
    # Show failed endpoints
    if failed > 0:
        print("Failed Endpoints:")
        for r in results:
            if r.get("status") == "FAIL":
                print(f"  - {r.get('name')}: {r.get('error', 'Unknown error')}")
        print()
    
    # Test enhanced signals endpoint specifically
    print("=" * 60)
    print("ENHANCED SIGNALS ENDPOINT DETAILED TEST")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/signals/enhanced?limit=5", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint accessible")
            print(f"   Signals count: {data.get('count', 0)}")
            print(f"   Enhanced features:")
            features = data.get('enhanced_features', {})
            print(f"     - Ensemble: {'✅' if features.get('ensemble') else '❌'}")
            print(f"     - Regime: {'✅' if features.get('regime') else '❌'}")
            print(f"     - Multi-Timeframe: {'✅' if features.get('multi_timeframe') else '❌'}")
            
            if data.get('signals'):
                first_signal = data['signals'][0]
                print(f"\n   First signal structure:")
                print(f"     - Has ensemble: {'ensemble' in first_signal}")
                print(f"     - Has regime: {'regime' in first_signal}")
                print(f"     - Has multi_timeframe: {'multi_timeframe' in first_signal}")
        else:
            print(f"❌ Endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing enhanced signals: {e}")
    
    print()
    print("=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)
    
    # Save results
    results_file = Path("logs/forensic/api_verification_20260222_163926/api_test_results.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "base_url": BASE_URL,
            "results": results,
            "summary": {
                "total": len(results),
                "passed": passed,
                "failed": failed,
                "skipped": skipped
            }
        }, f, indent=2)
    
    print(f"Results saved to: {results_file}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
