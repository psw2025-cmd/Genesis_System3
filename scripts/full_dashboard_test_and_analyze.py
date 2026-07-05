"""
Full Dashboard Test and Analysis
Starts services if needed, then performs comprehensive testing and content analysis
"""

import json
import os
import subprocess
import sys
import time
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


def check_service(url, name, timeout=5):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False


def start_backend():
    """Start the backend service"""
    print("🚀 Starting backend...")
    backend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "backend")

    try:
        # Start backend in a new window
        subprocess.Popen(
            ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=backend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
        )
        print("  ✅ Backend starting...")
        time.sleep(8)  # Wait for backend to start
        return True
    except Exception as e:
        print(f"  ❌ Failed to start backend: {e}")
        return False


def start_frontend():
    """Start the frontend service"""
    print("🚀 Starting frontend...")
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "frontend")

    try:
        # Check if node_modules exists
        if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
            print("  📦 Installing dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, timeout=120)

        # Start frontend
        subprocess.Popen(
            ["npm", "run", "dev", "--", "--host", "0.0.0.0"],
            cwd=frontend_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
        )
        print("  ✅ Frontend starting...")
        time.sleep(5)  # Wait for frontend to start
        return True
    except Exception as e:
        print(f"  ❌ Failed to start frontend: {e}")
        return False


def ensure_services_running():
    """Ensure backend and frontend are running"""
    print("=" * 80)
    print("🔍 CHECKING SERVICES")
    print("=" * 80)

    backend_running = check_service(f"{API_BASE}/api/status", "Backend")
    frontend_running = check_service(FRONTEND_BASE, "Frontend")

    if backend_running:
        print("✅ Backend: RUNNING")
    else:
        print("⚠️  Backend: NOT RUNNING - Starting...")
        if not start_backend():
            print("❌ Failed to start backend")
            return False
        # Verify it started
        for i in range(10):
            time.sleep(1)
            if check_service(f"{API_BASE}/api/status", "Backend"):
                print("✅ Backend: STARTED")
                backend_running = True
                break
        if not backend_running:
            print("❌ Backend failed to start")
            return False

    if frontend_running:
        print("✅ Frontend: RUNNING")
    else:
        print("⚠️  Frontend: NOT RUNNING - Starting...")
        if not start_frontend():
            print("❌ Failed to start frontend")
            return False
        # Verify it started
        for i in range(10):
            time.sleep(1)
            if check_service(FRONTEND_BASE, "Frontend"):
                print("✅ Frontend: STARTED")
                frontend_running = True
                break
        if not frontend_running:
            print("⚠️  Frontend may still be starting (this is OK)")

    return True


def analyze_all_tabs():
    """Analyze all dashboard tabs"""
    print("\n" + "=" * 80)
    print("🖥️  ANALYZING ALL DASHBOARD TABS")
    print("=" * 80)

    tabs = [
        ("/", "Overview"),
        ("/chain", "Chain Analytics"),
        ("/signals", "Signals"),
        ("/trading", "Paper Trading"),
        ("/alerts", "Alerts"),
        ("/risk", "Risk Dashboard"),
        ("/charts", "Advanced Charts"),
        ("/ml", "ML Performance"),
        ("/model", "Model Behavior"),
        ("/control", "Control Plane"),
    ]

    results = {}
    for path, name in tabs:
        try:
            url = f"{FRONTEND_BASE}{path}"
            response = requests.get(url, timeout=10)

            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {name:25s} | Status: {response.status_code} | Size: {len(response.text)} bytes")

            results[name] = {
                "status_code": response.status_code,
                "url": url,
                "size": len(response.text),
                "has_content": len(response.text) > 1000,
            }
        except Exception as e:
            print(f"❌ {name:25s} | Error: {str(e)[:50]}")
            results[name] = {"error": str(e)}

    return results


def analyze_all_apis():
    """Analyze all API endpoints"""
    print("\n" + "=" * 80)
    print("📡 ANALYZING ALL API ENDPOINTS")
    print("=" * 80)

    endpoints = {
        "Root": "/",
        "Status": "/api/status",
        "Health": "/api/health",
        "QC": "/api/qc",
        "Performance": "/api/perf",
        "Chain NIFTY": "/api/chain/NIFTY",
        "Chain BANKNIFTY": "/api/chain/BANKNIFTY",
        "Signals": "/api/signal/top",
        "Positions": "/api/positions",
        "PnL": "/api/pnl",
        "Trades Today": "/api/trades/today",
        "Alerts Recent": "/api/alerts/recent",
        "Risk Portfolio": "/api/risk/portfolio",
    }

    results = {}
    for name, endpoint in endpoints.items():
        try:
            start = time.time()
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            elapsed = time.time() - start

            if response.status_code == 200:
                try:
                    data = response.json()
                    data_size = len(json.dumps(data))

                    # Extract key info
                    info = {}
                    if isinstance(data, dict):
                        info["keys"] = list(data.keys())[:10]  # First 10 keys
                        info["data_source"] = data.get("data_source", "N/A")
                        if "total_pnl" in data:
                            info["total_pnl"] = data["total_pnl"]
                        if "open_positions" in data:
                            info["open_positions"] = data["open_positions"]

                    status = "✅"
                    print(f"{status} {name:25s} | {elapsed:6.3f}s | Size: {data_size} bytes | {json.dumps(info)[:60]}")

                    results[name] = {"status": "ok", "response_time": elapsed, "data_size": data_size, "info": info}
                except:
                    status = "✅"
                    print(f"{status} {name:25s} | {elapsed:6.3f}s | Non-JSON response")
                    results[name] = {"status": "ok", "response_time": elapsed}
            else:
                status = "❌"
                print(f"{status} {name:25s} | Status: {response.status_code}")
                results[name] = {"status": "error", "status_code": response.status_code}

        except Exception as e:
            print(f"❌ {name:25s} | Error: {str(e)[:50]}")
            results[name] = {"status": "error", "error": str(e)}

    return results


def analyze_content_details():
    """Analyze detailed content from key endpoints"""
    print("\n" + "=" * 80)
    print("🔍 DETAILED CONTENT ANALYSIS")
    print("=" * 80)

    analysis = {}

    # Health data
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            analysis["health"] = {
                "market_status": health.get("market_status", "unknown"),
                "broker_status": health.get("broker_status", "unknown"),
                "data_source": health.get("data_source", "unknown"),
                "total_pnl": health.get("total_pnl", 0),
                "daily_pnl": health.get("daily_pnl", 0),
                "open_positions": health.get("open_positions", 0),
                "trades_executed": health.get("trades_executed", 0),
                "cycle_count": health.get("cycle_count", 0),
            }
            print(f"📊 Health Data:")
            print(f"  Market: {analysis['health']['market_status']}")
            print(f"  Broker: {analysis['health']['broker_status']}")
            print(f"  Data Source: {analysis['health']['data_source']}")
            print(f"  PnL: ₹{analysis['health']['total_pnl']:.2f} (Daily: ₹{analysis['health']['daily_pnl']:.2f})")
            print(
                f"  Positions: {analysis['health']['open_positions']} | Trades: {analysis['health']['trades_executed']}"
            )
    except Exception as e:
        print(f"❌ Health analysis error: {e}")

    # Chain data
    try:
        response = requests.get(f"{API_BASE}/api/chain/NIFTY", timeout=10)
        if response.status_code == 200:
            chain = response.json()
            analysis["chain"] = {
                "spot": chain.get("spot", 0),
                "pcr": chain.get("pcr", 0),
                "contracts_count": len(chain.get("contracts", [])),
                "data_source": chain.get("data_source", "unknown"),
                "status": chain.get("status", "unknown"),
            }
            print(f"\n📊 Chain Data (NIFTY):")
            print(f"  Spot: ₹{analysis['chain']['spot']:.2f}")
            print(f"  PCR: {analysis['chain']['pcr']:.2f}")
            print(f"  Contracts: {analysis['chain']['contracts_count']}")
            print(f"  Source: {analysis['chain']['data_source']}")
    except Exception as e:
        print(f"❌ Chain analysis error: {e}")

    # Positions
    try:
        response = requests.get(f"{API_BASE}/api/positions", timeout=10)
        if response.status_code == 200:
            positions = response.json()
            pos_list = positions.get("positions", [])
            analysis["positions"] = {
                "count": len(pos_list) if isinstance(pos_list, list) else 0,
                "total_value": sum(p.get("current_value", 0) for p in pos_list if isinstance(p, dict)),
            }
            print(f"\n📊 Positions:")
            print(f"  Count: {analysis['positions']['count']}")
            print(f"  Total Value: ₹{analysis['positions']['total_value']:.2f}")
    except Exception as e:
        print(f"❌ Positions analysis error: {e}")

    return analysis


def run_full_analysis():
    """Run complete dashboard test and analysis"""
    print("=" * 80)
    print("🚀 FULL DASHBOARD TEST AND ANALYSIS")
    print("=" * 80)
    print(f"Started at: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}\n")

    # Ensure services are running
    if not ensure_services_running():
        print("\n❌ Services not available. Please start backend and frontend manually.")
        return None

    # Analyze tabs
    tab_results = analyze_all_tabs()

    # Analyze APIs
    api_results = analyze_all_apis()

    # Detailed content analysis
    content_analysis = analyze_content_details()

    # Generate summary
    print("\n" + "=" * 80)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 80)

    tabs_ok = sum(1 for r in tab_results.values() if r.get("status_code") == 200)
    apis_ok = sum(1 for r in api_results.values() if r.get("status") == "ok")

    print(f"\n✅ Tabs: {tabs_ok}/{len(tab_results)} OK")
    print(f"✅ APIs: {apis_ok}/{len(api_results)} OK")

    # Save results
    results = {
        "timestamp": datetime.now(IST).isoformat(),
        "tabs": tab_results,
        "apis": api_results,
        "content_analysis": content_analysis,
        "summary": {
            "tabs_tested": len(tab_results),
            "tabs_ok": tabs_ok,
            "apis_tested": len(api_results),
            "apis_ok": apis_ok,
        },
    }

    results_file = "outputs/full_dashboard_analysis.json"
    os.makedirs("outputs", exist_ok=True)

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Full analysis saved to: {results_file}")
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)

    return results


if __name__ == "__main__":
    try:
        results = run_full_analysis()
        if results and results["summary"]["tabs_ok"] == results["summary"]["tabs_tested"]:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
