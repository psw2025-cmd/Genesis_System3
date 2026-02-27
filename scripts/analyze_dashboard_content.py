"""
Dashboard Content Analysis - Tests and analyzes all dashboard content
Works with backend only (frontend optional)
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
FRONTEND_BASE = "http://localhost:3000"
IST = pytz.timezone("Asia/Kolkata")


def test_endpoint(name, endpoint, method="GET"):
    """Test an API endpoint and return detailed analysis"""
    try:
        start = time.time()
        url = f"{API_BASE}{endpoint}"
        response = requests.request(method, url, timeout=10)
        elapsed = time.time() - start

        result = {
            "name": name,
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "response_time": elapsed,
            "success": response.status_code == 200,
        }

        if response.status_code == 200:
            try:
                data = response.json()
                result["data"] = data
                result["data_type"] = type(data).__name__
                result["data_size"] = len(json.dumps(data))

                # Extract key information
                if isinstance(data, dict):
                    result["keys"] = list(data.keys())
                    result["data_source"] = data.get("data_source", "N/A")

            except:
                result["data"] = response.text[:500]  # First 500 chars
                result["data_type"] = "text"

        return result
    except Exception as e:
        return {"name": name, "endpoint": endpoint, "success": False, "error": str(e)}


def analyze_health_data(health_data):
    """Analyze health endpoint data"""
    print("\n" + "=" * 80)
    print("📊 HEALTH DATA ANALYSIS")
    print("=" * 80)

    analysis = {}

    # Market status
    market_status = health_data.get("market_status", "unknown")
    analysis["market_status"] = market_status
    print(f"📈 Market Status: {market_status}")

    # Broker status
    broker_status = health_data.get("broker_status", "unknown")
    analysis["broker_status"] = broker_status
    print(f"🔌 Broker Status: {broker_status}")

    # Data source
    data_source = health_data.get("data_source", "unknown")
    analysis["data_source"] = data_source
    print(f"💾 Data Source: {data_source}")

    # Trading metrics
    total_pnl = health_data.get("total_pnl", 0)
    daily_pnl = health_data.get("daily_pnl", 0)
    open_positions = health_data.get("open_positions", 0)
    trades_executed = health_data.get("trades_executed", 0)
    cycle_count = health_data.get("cycle_count", 0)

    analysis["trading"] = {
        "total_pnl": total_pnl,
        "daily_pnl": daily_pnl,
        "open_positions": open_positions,
        "trades_executed": trades_executed,
        "cycle_count": cycle_count,
    }

    print(f"\n💰 Trading Metrics:")
    print(f"  Total PnL: ₹{total_pnl:,.2f}")
    print(f"  Daily PnL: ₹{daily_pnl:,.2f}")
    print(f"  Open Positions: {open_positions}")
    print(f"  Trades Executed: {trades_executed}")
    print(f"  Cycle Count: {cycle_count}")

    # Performance SLA
    perf_sla = health_data.get("performance_sla", {})
    if perf_sla:
        cycle_duration = perf_sla.get("cycle_duration_sec", 0)
        fetch_duration = perf_sla.get("fetch_duration_sec", 0)
        strategy_duration = perf_sla.get("strategy_duration_sec", 0)
        sla_pass = perf_sla.get("sla_pass", False)

        analysis["performance"] = {
            "cycle_duration": cycle_duration,
            "fetch_duration": fetch_duration,
            "strategy_duration": strategy_duration,
            "sla_pass": sla_pass,
        }

        print(f"\n⚡ Performance SLA:")
        print(f"  Cycle Duration: {cycle_duration:.3f}s")
        print(f"  Fetch Duration: {fetch_duration:.3f}s")
        print(f"  Strategy Duration: {strategy_duration:.3f}s")
        print(f"  SLA Pass: {'✅' if sla_pass else '❌'}")

    return analysis


def analyze_chain_data(chain_data):
    """Analyze chain endpoint data"""
    print("\n" + "=" * 80)
    print("📊 CHAIN DATA ANALYSIS (NIFTY)")
    print("=" * 80)

    analysis = {}

    # Basic info
    underlying = chain_data.get("underlying", "NIFTY")
    spot = chain_data.get("spot", 0)
    pcr = chain_data.get("pcr", 0)
    status = chain_data.get("status", "unknown")
    data_source = chain_data.get("data_source", "unknown")

    analysis["basic"] = {
        "underlying": underlying,
        "spot": spot,
        "pcr": pcr,
        "status": status,
        "data_source": data_source,
    }

    print(f"📈 Underlying: {underlying}")
    print(f"💰 Spot Price: ₹{spot:,.2f}")
    print(f"📊 Put-Call Ratio: {pcr:.2f}")
    print(f"📋 Status: {status}")
    print(f"💾 Data Source: {data_source}")

    # Contracts
    contracts = chain_data.get("contracts", [])
    analysis["contracts"] = {
        "total": len(contracts),
        "calls": len([c for c in contracts if c.get("option_type") == "CE"]),
        "puts": len([c for c in contracts if c.get("option_type") == "PE"]),
    }

    print(f"\n📋 Contracts:")
    print(f"  Total: {analysis['contracts']['total']}")
    print(f"  Calls: {analysis['contracts']['calls']}")
    print(f"  Puts: {analysis['contracts']['puts']}")

    # Analyze contract data if available
    if contracts:
        # Find ATM contracts
        atm_calls = [c for c in contracts if abs(c.get("strike", 0) - spot) < 50]
        atm_puts = [c for c in contracts if abs(c.get("strike", 0) - spot) < 50]

        analysis["atm"] = {"calls_near_atm": len(atm_calls), "puts_near_atm": len(atm_puts)}

        print(f"  Near ATM Calls: {len(atm_calls)}")
        print(f"  Near ATM Puts: {len(atm_puts)}")

    return analysis


def analyze_positions_data(positions_data):
    """Analyze positions endpoint data"""
    print("\n" + "=" * 80)
    print("📊 POSITIONS DATA ANALYSIS")
    print("=" * 80)

    analysis = {}

    positions = positions_data.get("positions", [])
    if not isinstance(positions, list):
        positions = []

    analysis["count"] = len(positions)
    analysis["total_value"] = sum(p.get("current_value", 0) for p in positions if isinstance(p, dict))
    analysis["total_pnl"] = sum(p.get("unrealized_pnl", 0) for p in positions if isinstance(p, dict))

    print(f"📋 Total Positions: {analysis['count']}")
    print(f"💰 Total Value: ₹{analysis['total_value']:,.2f}")
    print(f"📈 Total Unrealized PnL: ₹{analysis['total_pnl']:,.2f}")

    if positions:
        print(f"\n📋 Position Details:")
        for i, pos in enumerate(positions[:10], 1):  # Show first 10
            symbol = pos.get("symbol", "N/A")
            qty = pos.get("quantity", 0)
            entry = pos.get("entry_price", 0)
            current = pos.get("current_price", 0)
            pnl = pos.get("unrealized_pnl", 0)
            print(f"  {i}. {symbol} | Qty: {qty} | Entry: ₹{entry:.2f} | Current: ₹{current:.2f} | PnL: ₹{pnl:.2f}")

    return analysis


def run_full_analysis():
    """Run complete dashboard content analysis"""
    print("=" * 80)
    print("🚀 DASHBOARD CONTENT ANALYSIS")
    print("=" * 80)
    print(f"Started at: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}\n")

    # Check backend
    print("🔍 Checking backend...")
    try:
        response = requests.get(f"{API_BASE}/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running\n")
        else:
            print(f"⚠️  Backend returned status {response.status_code}\n")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}\n")
        print("Please start the backend first using: START_ALL_SERVICES.bat")
        return None

    # Test all endpoints
    print("=" * 80)
    print("📡 TESTING ALL API ENDPOINTS")
    print("=" * 80)

    endpoints = [
        ("Root", "/"),
        ("Status", "/api/status"),
        ("Health", "/api/health"),
        ("QC", "/api/qc"),
        ("Performance", "/api/perf"),
        ("Chain NIFTY", "/api/chain/NIFTY"),
        ("Chain BANKNIFTY", "/api/chain/BANKNIFTY"),
        ("Signals", "/api/signal/top"),
        ("Positions", "/api/positions"),
        ("PnL", "/api/pnl"),
        ("Trades Today", "/api/trades/today"),
        ("Alerts Recent", "/api/alerts/recent"),
        ("Risk Portfolio", "/api/risk/portfolio"),
    ]

    results = {}
    for name, endpoint in endpoints:
        result = test_endpoint(name, endpoint)
        results[name] = result

        status = "✅" if result.get("success") else "❌"
        rt = result.get("response_time", 0)
        print(f"{status} {name:25s} | {rt:6.3f}s | {result.get('status_code', 'N/A')}")

    # Detailed analysis of key endpoints
    if "Health" in results and results["Health"].get("success"):
        health_analysis = analyze_health_data(results["Health"]["data"])
        results["Health"]["analysis"] = health_analysis

    if "Chain NIFTY" in results and results["Chain NIFTY"].get("success"):
        chain_analysis = analyze_chain_data(results["Chain NIFTY"]["data"])
        results["Chain NIFTY"]["analysis"] = chain_analysis

    if "Positions" in results and results["Positions"].get("success"):
        positions_analysis = analyze_positions_data(results["Positions"]["data"])
        results["Positions"]["analysis"] = positions_analysis

    # Summary
    print("\n" + "=" * 80)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results.values() if r.get("success"))
    total = len(results)

    print(f"\n✅ Successful: {successful}/{total} ({successful/total*100:.1f}%)")

    # Save results
    output = {
        "timestamp": datetime.now(IST).isoformat(),
        "summary": {
            "total_endpoints": total,
            "successful": successful,
            "success_rate": successful / total * 100 if total > 0 else 0,
        },
        "results": results,
    }

    results_file = "outputs/dashboard_content_analysis_full.json"
    os.makedirs("outputs", exist_ok=True)

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Full analysis saved to: {results_file}")
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)

    return output


if __name__ == "__main__":
    try:
        results = run_full_analysis()
        sys.exit(0 if results else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
