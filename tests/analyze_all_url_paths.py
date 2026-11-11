import json
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://127.0.0.1:8008"

def analyze_all_url_paths():
    print(f"Connecting to live Genesis System3 server at {BASE_URL}...")
    
    # Fetch all routes
    req = urllib.request.Request(f"{BASE_URL}/api/routes", headers={"User-Agent": "GenesisURLAnalyzer/1.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    routes = data["routes"]
    total = len(routes)
    print(f"Discovered {total} registered GET endpoints.")

    categories = {
        "Root & UI Dashboard": [],
        "Market Coverage & Breadth": [],
        "Live Data Truth & Provenance": [],
        "Options Intelligence": [],
        "Paper Trading & Ledger": [],
        "ML Prediction Validation": [],
        "Dhan Scanning Daemon & Router": [],
        "Core Analytics & Health": [],
        "Market Symbols (LTP/Truth/Predict)": [],
        "Truth Score & Forecast Suite": [],
        "Option Chain (Strike Grid)": [],
        "Institutional Scanners": [],
        "System, Governance & Risk": [],
        "OpenAPI Docs & Schema": []
    }

    t0 = time.time()
    tested_count = 0
    passed_count = 0
    failed_count = 0

    for idx, r in enumerate(routes, 1):
        path = r["path"]
        name = r["name"]
        
        # Classify
        if path in ("/", "/ui"):
            cat = "Root & UI Dashboard"
        elif path.startswith("/api/market/") and path in ("/api/market/inventory", "/api/market/breadth", "/api/market/sectors", "/api/market/missing-symbols"):
            cat = "Market Coverage & Breadth"
        elif path.startswith("/api/dhan/"):
            cat = "Dhan Scanning Daemon & Router"
        elif path.startswith("/api/options/"):
            cat = "Options Intelligence"
        elif path.startswith("/api/paper/"):
            cat = "Paper Trading & Ledger"
        elif path.startswith("/api/ml/"):
            cat = "ML Prediction Validation"
        elif path in ("/api/route-health", "/api/data/provenance", "/api/evidence"):
            cat = "Live Data Truth & Provenance"
        elif path.startswith("/api/market/") and len(path.split("/")) == 4:
            cat = "Market Symbols (LTP/Truth/Predict)"
        elif path.startswith("/api/truth/") or path.startswith("/api/predict/"):
            cat = "Truth Score & Forecast Suite"
        elif path.startswith("/api/option-chain/"):
            cat = "Option Chain (Strike Grid)"
        elif path.startswith("/api/scanner"):
            cat = "Institutional Scanners"
        elif path.startswith("/api/margin/") or path in ("/api/kill-switch", "/api/settings", "/api/logs", "/api/metrics", "/api/audit", "/api/hash-chain", "/api/var", "/api/drawdown"):
            cat = "System, Governance & Risk"
        elif path in ("/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"):
            cat = "OpenAPI Docs & Schema"
        else:
            cat = "Core Analytics & Health"

        # Formulate test path
        test_path = path
        if "{id}" in test_path:
            test_path = test_path.replace("{id}", "0")
        if "{strike}" in test_path:
            test_path = test_path.replace("{strike}", "1250")
        if "{SYM}" in test_path:
            test_path = test_path.replace("{SYM}", "RELIANCE")

        url = f"{BASE_URL}{test_path}"
        req_item = urllib.request.Request(url, headers={"User-Agent": "GenesisURLAnalyzer/1.0"})
        t_req = time.time()
        try:
            with urllib.request.urlopen(req_item, timeout=5) as res:
                code = res.status
                body = res.read()
                latency_ms = round((time.time() - t_req) * 1000, 2)
                categories[cat].append({
                    "path": path,
                    "test_path": test_path,
                    "name": name,
                    "status": code,
                    "latency_ms": latency_ms,
                    "bytes": len(body),
                    "ok": True
                })
                passed_count += 1
        except Exception as e:
            failed_count += 1
            latency_ms = round((time.time() - t_req) * 1000, 2)
            categories[cat].append({
                "path": path,
                "test_path": test_path,
                "name": name,
                "status": getattr(e, "code", 500),
                "latency_ms": latency_ms,
                "error": str(e),
                "ok": False
            })

        tested_count += 1
        if tested_count % 100 == 0 or tested_count == total:
            print(f"Tested {tested_count}/{total} URL endpoints... (Passed: {passed_count}, Failed: {failed_count})")

    elapsed = round(time.time() - t0, 2)
    print(f"\nCompleted complete analysis of {total} URL paths in {elapsed}s.")
    print(f"Total Passed: {passed_count} | Total Failed: {failed_count}")

    category_summary = {}
    for cat_name, items in categories.items():
        avg_lat = round(sum(i["latency_ms"] for i in items) / len(items), 2) if items else 0.0
        pass_items = sum(1 for i in items if i["ok"])
        category_summary[cat_name] = {
            "total_endpoints": len(items),
            "passed": pass_items,
            "failed": len(items) - pass_items,
            "avg_latency_ms": avg_lat,
            "sample_path": items[0]["path"] if items else None
        }

    out = {
        "analysis_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "base_url": BASE_URL,
        "total_endpoints": total,
        "passed": passed_count,
        "failed": failed_count,
        "duration_seconds": elapsed,
        "category_summary": category_summary,
        "all_categories": categories
    }

    out_file = Path("reports/latest/complete_url_paths_analysis.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Complete URL paths analysis saved to {out_file}")

    assert failed_count == 0, f"{failed_count} endpoints failed HTTP analysis!"
    return out

if __name__ == "__main__":
    analyze_all_url_paths()
