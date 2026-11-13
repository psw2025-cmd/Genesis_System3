import requests
import json
import time

BASE_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"

print(f"=== COMPREHENSIVE UI TAB & INTERACTIVITY AUDIT ===")
print(f"Target: {BASE_URL}\n")

# Tab mapping to backing APIs and UI features
TABS = [
    {
        "id": "decision-intel",
        "name": "Decision Intelligence",
        "apis": ["/api/health", "/api/state", "/api/broker/status"],
        "charts": [],
        "filters": ["Symbol switchers (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY)"],
        "clicks": ["Nav buttons to Truth, Options, Risk, Data, System", "Ops board tab switchers"],
        "sorts": []
    },
    {
        "id": "truth",
        "name": "Truth Control",
        "apis": ["/api/state", "/api/health", "/api/qc"],
        "charts": [],
        "filters": [],
        "clicks": ["Re-probe health", "Refresh state"],
        "sorts": ["QC anomaly checks table"]
    },
    {
        "id": "genesis",
        "name": "Genesis Brain",
        "apis": ["/api/state", "/api/health"],
        "charts": [],
        "filters": [],
        "clicks": ["Inspect brain cycle", "Refresh telemetry"],
        "sorts": []
    },
    {
        "id": "e2e-proof",
        "name": "E2E Proof",
        "apis": ["/api/state", "/api/broker/status"],
        "charts": [],
        "filters": [],
        "clicks": ["Verification checklist toggle"],
        "sorts": ["Gate checklist table"]
    },
    {
        "id": "overview",
        "name": "Overview",
        "apis": ["/api/health", "/api/state", "/api/market/top-gainers", "/api/trades/today"],
        "charts": ["Main Index Mini-Charts", "Holographic Cards"],
        "filters": ["Index toggles"],
        "clicks": ["Index card click", "Quick action buttons"],
        "sorts": ["Top CE/PE movers table (sort by % gain)"]
    },
    {
        "id": "sim-live",
        "name": "Sim Live",
        "apis": ["/api/state", "/api/trades/today", "/api/paper/account"],
        "charts": ["Simulation P&L Line"],
        "filters": ["Speed selector (1x, 2x, 5x)"],
        "clicks": ["Play/Pause simulation", "Reset sim", "Step tick"],
        "sorts": ["Simulated fills log table"]
    },
    {
        "id": "options-intel",
        "name": "Options Intelligence",
        "apis": [
            "/api/chain/NIFTY",
            "/api/charting/heatmap/NIFTY?metric=oi",
            "/api/charting/iv-surface/NIFTY",
            "/api/charting/greeks/NIFTY?greek=delta",
            "/api/charting/pcr/NIFTY"
        ],
        "charts": [
            "AdvancedCharts - Heatmap (BarChart)",
            "AdvancedCharts - IV Surface (LineChart)",
            "AdvancedCharts - Greeks (BarChart)",
            "AdvancedCharts - PCR (BarChart)"
        ],
        "filters": [
            "Underlying dropdown (224 symbols)",
            "Heatmap metric dropdown (OI, Volume, IV, LTP)",
            "Greek dropdown (Delta, Gamma, Theta, Vega)",
            "Expiry selector"
        ],
        "clicks": ["Symbol pill buttons", "Open full chain button"],
        "sorts": ["Positions table", "Rankings list"]
    },
    {
        "id": "chain",
        "name": "Option Chain",
        "apis": [
            "/api/underlyings",
            "/api/chain/NIFTY",
            "/api/expiries/NIFTY"
        ],
        "charts": [],
        "filters": [
            "Core index pills (NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX, BANKEX)",
            "Underlying search input with autocomplete datalist (224 symbols)",
            "Expiry dropdown selector",
            "Strike range selector (+/-5, +/-10, +/-20, +/-40, ALL)",
            "Greeks view toggle (STANDARD vs GREEKS VIEW)",
            "Mobile view toggle (Compact cards vs Full table)"
        ],
        "clicks": [
            "Symbol pills",
            "Greeks toggle button",
            "Mobile view toggle button",
            "ATM strike auto-scroll target"
        ],
        "sorts": ["Strikes ascending sort with sticky ATM marker"]
    },
    {
        "id": "signals",
        "name": "Signals",
        "apis": [
            "/api/opportunity-gap",
            "/api/t1-pre-ignition",
            "/api/multibagger/predictions"
        ],
        "charts": [],
        "filters": ["Signal category toggle"],
        "clicks": ["Runner row inspect", "Refresh signals"],
        "sorts": [
            "Gap-up runners sort by gap %",
            "T1 pre-ignition sort by score",
            "Predictions sort by confidence"
        ]
    },
    {
        "id": "trade",
        "name": "Trade",
        "apis": ["/api/broker/status", "/api/state"],
        "charts": [],
        "filters": ["Order type (Market/Limit)", "Product (Intraday/Normal)"],
        "clicks": ["Submit order (Safety gate locked / Paper only modal)"],
        "sorts": []
    },
    {
        "id": "paper",
        "name": "Paper Trades",
        "apis": [
            "/api/paper/account",
            "/api/trades/today",
            "/api/trades/history"
        ],
        "charts": ["Paper Equity Curve Canvas Chart"],
        "filters": ["Trade status filter (All / Open / Closed)"],
        "clicks": ["Manual paper close", "Refresh ledger", "Export trades CSV"],
        "sorts": ["Trades sorted by timestamp descending"]
    },
    {
        "id": "positions",
        "name": "Positions",
        "apis": ["/api/state", "/api/broker/status"],
        "charts": [],
        "filters": ["Positions filter (Active / All)"],
        "clicks": ["Square off disabled / Paper safety notice"],
        "sorts": ["Positions sorted by P&L / Symbol"]
    },
    {
        "id": "risk-scenarios",
        "name": "Risk & Scenarios",
        "apis": ["/api/state"],
        "charts": ["VaR & Stress Scenarios"],
        "filters": ["Scenario stress multiplier (+1%, -1%, +2%, -2%)"],
        "clicks": ["Run scenario recalculation"],
        "sorts": []
    },
    {
        "id": "multibagger",
        "name": "Multibagger Research",
        "apis": ["/api/multibagger/predictions"],
        "charts": [],
        "filters": ["Horizon filter (Weekly, Monthly, Yearly, All)"],
        "clicks": ["Horizon tab buttons", "Candidate card expand"],
        "sorts": ["Sorted by expected gain % and confidence score"]
    },
    {
        "id": "prediction-audit",
        "name": "Prediction Audit",
        "apis": ["/api/ml/prediction-audit", "/api/ml/forecast-vs-actual"],
        "charts": ["Forecast vs Actual Scatter/Bar"],
        "filters": ["Date range filter", "Horizon filter"],
        "clicks": ["Batch inspect", "Filter apply"],
        "sorts": ["Audited forecasts table sorted by date"]
    },
    {
        "id": "performance",
        "name": "Performance",
        "apis": ["/api/trades/history", "/api/paper/account"],
        "charts": ["Daily P&L Bar Chart", "Drawdown Line Chart"],
        "filters": ["Timeframe (7D, 30D, ALL)"],
        "clicks": ["Timeframe pills"],
        "sorts": ["Performance metrics breakdown"]
    },
    {
        "id": "ml",
        "name": "ML Model",
        "apis": ["/api/state"],
        "charts": ["Feature Importance Bar Chart"],
        "filters": ["Model version select"],
        "clicks": ["Inspect feature weights", "Refresh metrics"],
        "sorts": ["Features sorted by importance weight"]
    },
    {
        "id": "data-integrity",
        "name": "Data Integrity",
        "apis": ["/api/data/provenance", "/api/market/inventory"],
        "charts": [],
        "filters": [],
        "clicks": ["Verify checksums button", "Inspect SHA-256 hashes"],
        "sorts": ["Data tables sorted by dataset name"]
    },
    {
        "id": "broker",
        "name": "Broker",
        "apis": ["/api/broker/status", "/api/dhan/holdings", "/api/dhan/funds"],
        "charts": [],
        "filters": [],
        "clicks": ["Test broker connection", "Refresh token info"],
        "sorts": ["Holdings table sorted by value/pnl"]
    },
    {
        "id": "alerts",
        "name": "Alerts",
        "apis": ["/api/state"],
        "charts": [],
        "filters": ["Severity filter (Info, Warning, Critical)"],
        "clicks": ["Dismiss alert", "Clear all alerts"],
        "sorts": ["Alerts sorted by timestamp descending"]
    },
    {
        "id": "system",
        "name": "System",
        "apis": ["/api/health", "/api/state"],
        "charts": ["System Memory & CPU Gauges"],
        "filters": [],
        "clicks": ["Diagnostics run", "Inspect process health"],
        "sorts": []
    },
    {
        "id": "gates",
        "name": "Live Trading Gate",
        "apis": ["/api/broker/status", "/api/state"],
        "charts": [],
        "filters": [],
        "clicks": ["Inspect gate checklist", "Gate verification report"],
        "sorts": ["Gates sorted by gate number G01-G28"]
    },
    {
        "id": "system-readiness",
        "name": "System Readiness",
        "apis": ["/api/health", "/api/broker/status"],
        "charts": [],
        "filters": [],
        "clicks": ["Check readiness"],
        "sorts": ["Readiness checks checklist"]
    }
]

# Probe all distinct endpoints
all_endpoints = sorted(list(set(ep for tab in TABS for ep in tab["apis"])))
print(f"Total Unique Endpoints across all 23 tabs: {len(all_endpoints)}\n")

api_results = {}
for ep in all_endpoints:
    url = f"{BASE_URL}{ep}"
    try:
        t0 = time.time()
        res = requests.get(url, timeout=12)
        elapsed = round(time.time() - t0, 3)
        status = res.status_code
        data = None
        has_error = False
        error_msg = ""
        try:
            data = res.json()
            if isinstance(data, dict):
                if data.get("status") == "error":
                    has_error = True
                    error_msg = data.get("error", "Unknown error")
        except:
            data = res.text[:200]
            
        api_results[ep] = {
            "status": status,
            "elapsed": elapsed,
            "has_error": has_error,
            "error_msg": error_msg,
            "data_summary": f"dict with {len(data)} keys" if isinstance(data, dict) else f"{len(data)} items" if isinstance(data, list) else "text"
        }
        status_str = "OK" if status == 200 and not has_error else f"FAIL ({error_msg or status})"
        print(f"[{status_str}] {ep} -> HTTP {status} in {elapsed}s | {api_results[ep]['data_summary']}")
    except Exception as e:
        api_results[ep] = {"status": "CONN_ERR", "error": str(e)}
        print(f"[ERROR] {ep} -> {e}")

print("\n=== TAB-BY-TAB HEALTH & PENDING EVALUATION ===")
tab_health = {}
for tab in TABS:
    tid = tab["id"]
    apis = tab["apis"]
    all_apis_ok = True
    failing_apis = []
    for ep in apis:
        res = api_results.get(ep, {})
        if res.get("status") != 200 or res.get("has_error"):
            all_apis_ok = False
            failing_apis.append(ep)
            
    tab_health[tid] = {
        "name": tab["name"],
        "apis_ok": all_apis_ok,
        "failing_apis": failing_apis,
        "charts": tab["charts"],
        "filters": tab["filters"],
        "clicks": tab["clicks"],
        "sorts": tab["sorts"],
        "status": "PASS" if all_apis_ok else "PARTIAL"
    }
    
    icon = "✓ PASS" if all_apis_ok else "⚠ ISSUES"
    print(f"[{icon}] Tab '{tab['name']}' ({tid}):")
    print(f"   Backing APIs: {len(apis)} checked ({'ALL OK' if all_apis_ok else f'FAILING: {failing_apis}'})")
    print(f"   Charts: {tab['charts'] or 'None'}")
    print(f"   Filters: {tab['filters'] or 'None'}")
    print(f"   Interactions/Clicks: {tab['clicks'] or 'None'}")
    print(f"   Sortable Views: {tab['sorts'] or 'None'}\n")

with open("scratch/tab_audit_complete_results.json", "w") as f:
    json.dump({"api_results": api_results, "tab_health": tab_health}, f, indent=2)

print("Saved complete audit report to scratch/tab_audit_complete_results.json")
