import json
import urllib.request
from pathlib import Path

token = ""
client = ""
sec_p = Path(r"C:\Genesis_System3_clean\.secrets\dhan.env")
if sec_p.is_file():
    for line in sec_p.read_text(encoding="utf-8-sig").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        if k.strip() == "DHAN_ACCESS_TOKEN":
            token = v.strip().strip('"').strip("'")
        elif k.strip() == "DHAN_CLIENT_ID":
            client = v.strip().strip('"').strip("'")

url = "https://api.dhan.co/v2/marketfeed/quote"
body = json.dumps({"IDX_I": [13, 25, 51]}).encode("utf-8")
req = urllib.request.Request(url, data=body, method="POST", headers={
    "access-token": token,
    "client-id": client,
    "Accept": "application/json",
    "Content-Type": "application/json"
})

try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("Dhan API Response:")
        print(json.dumps(res, indent=2))
except Exception as e:
    print("Dhan API Exception:", e)
