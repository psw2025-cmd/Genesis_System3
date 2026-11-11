import json
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://127.0.0.1:8008"

def test_all_endpoints():
    print(f"Connecting to Genesis System3 service at {BASE_URL}...")
    
    # 1. Fetch route list from /api/routes
    routes_url = f"{BASE_URL}/api/routes"
    req = urllib.request.Request(routes_url, headers={"User-Agent": "GenesisVerifier/1.0"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    total_routes_reported = data["total"]
    routes = data["routes"]
    print(f"Total routes discovered via /api/routes: {total_routes_reported}")
    assert total_routes_reported >= 500, f"Expected >= 500 routes, got {total_routes_reported}"

    results = []
    success_count = 0
    fail_count = 0

    t_start = time.time()
    for idx, r in enumerate(routes, 1):
        path = r["path"]
        
        # Format parameter placeholders
        test_path = path
        if "{id}" in test_path:
            test_path = test_path.replace("{id}", "0")
        if "{strike}" in test_path:
            test_path = test_path.replace("{strike}", "1250")
        if "{SYM}" in test_path:
            test_path = test_path.replace("{SYM}", "RELIANCE")

        url = f"{BASE_URL}{test_path}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GenesisVerifier/1.0"})
            with urllib.request.urlopen(req, timeout=5) as res:
                code = res.status
                body = res.read()
                results.append({
                    "path": path,
                    "test_path": test_path,
                    "status": code,
                    "bytes": len(body),
                    "ok": True
                })
                success_count += 1
        except Exception as e:
            fail_count += 1
            results.append({
                "path": path,
                "test_path": test_path,
                "status": getattr(e, "code", 500),
                "error": str(e),
                "ok": False
            })

        if idx % 100 == 0 or idx == len(routes):
            print(f"Tested {idx}/{len(routes)} routes... (Success: {success_count}, Fail: {fail_count})")

    elapsed = time.time() - t_start
    print(f"\nCompleted testing {len(routes)} endpoints in {elapsed:.2f}s.")
    print(f"Passed: {success_count} | Failed: {fail_count}")

    # Test /ui explicitly
    ui_url = f"{BASE_URL}/ui"
    with urllib.request.urlopen(ui_url, timeout=5) as res:
        ui_code = res.status
        ui_html = res.read().decode("utf-8")
        assert ui_code == 200
        assert "GENESIS" in ui_html
        assert "Auto-Found @app.get" in ui_html
        print(f"UI verification passed: HTTP {ui_code}, length {len(ui_html)} bytes.")

    summary = {
        "verified": fail_count == 0 and success_count >= 500,
        "total_endpoints_tested": len(routes),
        "passed": success_count,
        "failed": fail_count,
        "duration_seconds": round(elapsed, 2),
        "ui_status": ui_code,
        "ui_length_bytes": len(ui_html),
        "sample_routes": results[:10]
    }

    report_path = Path("reports/latest/genesis_endpoints_audit.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Audit report saved to {report_path}")

    assert fail_count == 0, f"{fail_count} endpoints failed HTTP check!"
    return summary

if __name__ == "__main__":
    test_all_endpoints()
