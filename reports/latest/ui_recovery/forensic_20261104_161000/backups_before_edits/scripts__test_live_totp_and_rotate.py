import base64
import hashlib
import hmac
import json
import struct
import subprocess
import time
import urllib.request
import urllib.error
from pathlib import Path

def get_totp(secret_b32: str) -> str:
    secret = secret_b32.strip().replace(" ", "").upper()
    secret += "=" * ((8 - len(secret) % 8) % 8)
    key = base64.b32decode(secret)
    counter = int(time.time() // 30)
    msg = struct.pack(">Q", counter)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = h[19] & 15
    code = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return f"{code:06d}"

def fetch_gcp_secret(secret_name: str) -> str:
    cmd = [
        "gcloud.cmd", "secrets", "versions", "access", "latest",
        f"--secret={secret_name}",
        "--project=system3-openalgo-safe"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    return res.stdout.strip()

def run_totp_test():
    print("Fetching credentials from Google Secret Manager...")
    try:
        cid = fetch_gcp_secret("dhan-client-id")
        pin = fetch_gcp_secret("dhan-pin")
        totp_secret = fetch_gcp_secret("dhan-totp-secret")
    except Exception as e:
        print(f"Failed fetching secrets from GCP: {e}")
        return False

    print(f"Secrets loaded successfully from GCP (client_id: {cid[:4]}***)")
    totp_code = get_totp(totp_secret)
    print(f"Computed live 6-digit TOTP (length={len(totp_code)}): SUCCESS")

    url = f"https://auth.dhan.co/app/generateAccessToken?dhanClientId={cid}&pin={pin}&totp={totp_code}"
    req = urllib.request.Request(url, method="POST", headers={"User-Agent": "GenesisSystem3/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "accessToken" in data:
                token = data["accessToken"]
                print(f"Dhan Access Token Generated Successfully! (length={len(token)})")
                
                # Test the new token against Dhan API
                fund_url = "https://api.dhan.co/v2/fundlimit"
                fund_req = urllib.request.Request(fund_url, headers={
                    "access-token": token,
                    "client-id": cid,
                    "Content-Type": "application/json"
                })
                with urllib.request.urlopen(fund_req, timeout=10) as fund_resp:
                    fund_data = json.loads(fund_resp.read().decode("utf-8"))
                    print(f"Dhan Broker API Verification: HTTP {fund_resp.status} LIVE CONFIRMED!")
                    print(f"Account Keys: {list(fund_data.keys())}")
                    
                # Update local .secrets/dhan.env
                env_file = Path(".secrets/dhan.env")
                env_content = f"DHAN_CLIENT_ID={cid}\nDHAN_ACCESS_TOKEN={token}\n"
                env_file.write_text(env_content, encoding="utf-8")
                print("Updated local .secrets/dhan.env with fresh token!")
                return True
            else:
                print("Unexpected response:", data)
                return False
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        print(f"Dhan Auth HTTP Error {e.code}: {e.reason}")
        print("Details:", err)
        return False
    except Exception as e:
        print("Error during auth:", str(e))
        return False

if __name__ == "__main__":
    run_totp_test()
