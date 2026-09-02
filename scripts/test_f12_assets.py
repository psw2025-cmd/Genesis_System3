"""Test F12 network assets and broker responses."""

import urllib.request

assets = [
    "/ui",
    "/ui/",
    "/ui/app.js",
    "/ui/style.css",
    "/api/broker/status",
    "/api/broker/truth",
    "/api/broker/positions",
    "/api/broker/holdings",
    "/api/broker/margins",
    "/api/broker/funds",
    "/api/state",
    "/api/health",
    "/api/agent-status",
    "/api/deploy/info",
]

print("=" * 80)
print("   GENESIS SYSTEM3 — F12 NETWORK & BROKER ASSET AUDIT")
print("=" * 80)

for a in assets:
    url = f"http://127.0.0.1:8000{a}"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "Accept": "*/*",
            }
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            ct = resp.headers.get("Content-Type", "")
            mime = ct.split(";")[0]
            body = resp.read()
            cl = len(body)
            print(f"   [200 OK] {a:<32} | Content-Type: {mime:<22} | Size: {cl:>8} bytes")
    except Exception as e:
        print(f"   [ERR]    {a:<32} | Error: {e}")

print("=" * 80)
