import json
import urllib.request
import urllib.error
from pathlib import Path

def test_dhan():
    env_path = Path(".secrets/dhan.env")
    creds = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                creds[k.strip()] = v.strip()

    client_id = creds.get("DHAN_CLIENT_ID") or creds.get("dhan-client-id") or ""
    token = creds.get("DHAN_ACCESS_TOKEN") or creds.get("dhan-access-token") or ""

    c_masked = client_id[:4] + "***" if len(client_id) > 4 else "NONE"
    print(f"Testing Dhan broker connection for client_id: {c_masked}")
    
    url = "https://api.dhan.co/v2/fundlimit"
    req = urllib.request.Request(url, headers={
        "access-token": token,
        "client-id": client_id,
        "Content-Type": "application/json"
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"Dhan API Response: HTTP {resp.status} SUCCESS")
            print("Response payload keys:", list(data.keys()))
            if "availabelBalance" in data or "availableBalance" in data or "dhanClientId" in data:
                print("Live Account Balance check: SUCCESS")
                return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        print(f"Dhan API HTTP Error {e.code}: {e.reason}")
        print("Error details:", err_msg)
        return False
    except Exception as e:
        print("Dhan API Connection error:", str(e))
        return False

if __name__ == "__main__":
    test_dhan()
