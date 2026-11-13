import urllib.request

url = "http://127.0.0.1:8008/ui"
with urllib.request.urlopen(url) as resp:
    html = resp.read().decode("utf-8")

print("Length of /ui HTML:", len(html))
assert "AUTH_REQUIRED" not in html, "AUTH_REQUIRED found in HTML"
assert "Dhan market data credentials not configured" not in html, "Credentials error found in HTML"
assert "LIVE VERIFIED" in html, "LIVE VERIFIED missing from HTML"
assert "DHANHQ FEED CONNECTED" in html, "DHANHQ FEED CONNECTED missing from HTML"
assert "loadDhanHoldings" in html, "loadDhanHoldings missing from HTML"
assert "loadDhanAccount" in html, "loadDhanAccount missing from HTML"
assert "holdings-tbody" in html, "holdings-tbody missing from HTML"

print("ALL UI ASSERTIONS PASSED!")
