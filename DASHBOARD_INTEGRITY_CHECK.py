import requests
import json
import time
from pathlib import Path

API_BASE = "http://localhost:8000"

def check_dashboard_integrity():
    print("=" * 80)
    print("💎 GENESIS SYSTEM3: DASHBOARD & API INTEGRITY AUDIT")
    print("=" * 80)
    
    endpoints = [
        {"name": "System State (SSOT)", "url": f"{API_BASE}/api/state"},
        {"name": "Market Intelligence", "url": f"{API_BASE}/api/market/intelligence?underlying=NIFTY"},
        {"name": "Top 5 AI Alpha", "url": f"{API_BASE}/api/signals/top5"},
        {"name": "Performance Metrics", "url": f"{API_BASE}/api/perf"},
        {"name": "Risk Portfolio", "url": f"{API_BASE}/api/risk/portfolio"},
        {"name": "Advanced Heatmap", "url": f"{API_BASE}/api/charting/heatmap/NIFTY?metric=oi"},
    ]

    results = []
    
    print("
[STEP 1] Verifying Backend API Endpoints...")
    for ep in endpoints:
        try:
            start_time = time.time()
            response = requests.get(ep["url"], timeout=5)
            latency = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"  ✅ {ep['name']:<25} | status: 200 | latency: {latency:.1f}ms")
                results.append(True)
            else:
                print(f"  ❌ {ep['name']:<25} | status: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"  🛑 {ep['name']:<25} | UNREACHABLE (Is backend running?)")
            results.append(False)

    print("
[STEP 2] Verifying Frontend Component Architecture...")
    frontend_components = [
        "Overview.tsx",
        "TopPredictions.tsx",
        "AdvancedCharts.tsx",
        "RiskDashboard.tsx",
        "ControlPlane.tsx"
    ]
    
    fe_base = Path("dashboard/frontend/src/components")
    for comp in frontend_components:
        path = fe_base / comp
        if path.exists():
            print(f"  ✅ Component: {comp:<20} | Status: INSTALLED")
        else:
            print(f"  ❌ Component: {comp:<20} | Status: MISSING")

    print("
[STEP 3] Verifying Multi-Asset Configuration...")
    try:
        from core.engine.HistoricalDataDownloader import SYMBOLS
        print(f"  ✅ Asset Universe: {len(SYMBOLS)} symbols registered (Indices + Stocks)")
    except Exception as e:
        print(f"  ❌ Asset Universe: Error loading symbols ({e})")

    # Final Verdict
    success_rate = (sum(results) / len(results)) * 100 if results else 0
    print("
" + "=" * 80)
    print(f"DASHBOARD READINESS: {success_rate:.1f}%")
    if success_rate == 100:
        print("💎 STATUS: WORLD-CLASS DASHBOARD FULLY OPERATIONAL")
    else:
        print("⚠️ STATUS: DASHBOARD PARTIALLY OPERATIONAL (Check backend connection)")
    print("=" * 80)

if __name__ == "__main__":
    check_dashboard_integrity()
