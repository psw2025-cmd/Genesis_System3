import urllib.request
import json
import ssl

def check_endpoints():
    base_url = "https://genesis-system3-web-802404398783.asia-south1.run.app"
    ctx = ssl.create_default_context()
    
    endpoints = [
        "/api/health",
        "/api/auto_gates",
        "/api/ml/validations",
        "/api/market_validation/latest",
        "/api/deploy_info"
    ]
    
    for ep in endpoints:
        url = f"{base_url}{ep}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                status = resp.status
                body = resp.read().decode("utf-8")
                try:
                    data = json.loads(body)
                    print(f"[OK {status}] {ep}")
                    if ep == "/api/auto_gates":
                        gates = data.get("gates", {})
                        for gname, ginfo in gates.items():
                            p = ginfo.get("pass")
                            b = ginfo.get("blocker_code") or ginfo.get("reason")
                            print(f"    - {gname}: pass={p} ({b})")
                    elif ep == "/api/ml/validations":
                        print(f"    - files: {len(data.get('validations', []))}")
                        print(f"    - avg_rho: {data.get('avg_rho')}")
                        print(f"    - ready_for_live: {data.get('ready_for_live')}")
                        print(f"    - proof_status: {data.get('proof_status')}")
                    elif ep == "/api/deploy_info":
                        print(f"    - git_sha: {data.get('git_sha')}")
                        print(f"    - deployed_at: {data.get('deployed_at')}")
                except Exception:
                    print(f"[OK {status}] {ep} (non-json: {body[:60]}...)")
        except Exception as e:
            print(f"[ERR] {ep}: {e}")

if __name__ == "__main__":
    check_endpoints()
