import urllib.request
import json
from pathlib import Path

p = Path(r"C:\Genesis_System3_clean\.secrets\dhan.env")
creds = {}
for line in p.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        creds[k.strip()] = v.strip().strip('"').strip("'")

print("Testing Dhan v2 marketfeed quote...")
url = "https://api.dhan.co/v2/marketfeed/quote"
headers = {
    "access-token": creds["DHAN_ACCESS_TOKEN"],
    "client-id": creds["DHAN_CLIENT_ID"],
    "Content-Type": "application/json",
    "Accept": "application/json"
}
body = json.dumps({"IDX_I": [13, 25, 51]}).encode("utf-8")
req = urllib.request.Request(url, data=body, headers=headers, method="POST")
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("HTTP Status:", resp.status)
        data = json.loads(resp.read().decode())
        print("Status field:", data.get("status"))
        idx_data = data.get("data", {}).get("IDX_I", {})
        for sec_id, info in idx_data.items():
            print(f"SecID {sec_id}: last_price={info.get('last_price')}, trade_time={info.get('last_trade_time')}")
except Exception as e:
    print("Error:", e)
