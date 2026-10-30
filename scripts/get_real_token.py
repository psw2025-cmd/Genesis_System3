import os
import pyotp
import requests
from google.cloud import secretmanager

project_id = "system3-openalgo-safe"
client = secretmanager.SecretManagerServiceClient()

def get_secret(name):
    path = f"projects/{project_id}/secrets/{name}/versions/latest"
    response = client.access_secret_version(request={"name": path})
    return response.payload.data.decode("UTF-8").strip()

print("Fetching PIN and TOTP from GCP...")
client_id = "1106583741"
pin = get_secret("dhan-pin")
totp_secret = get_secret("dhan-totp-secret")

print("Generating real TOTP...")
totp = pyotp.TOTP(totp_secret).now()

print("Requesting real token from Dhan...")
url = "https://api.dhan.co/v2/login"
payload = {"dhanClientId": client_id, "pin": pin, "totp": totp}
headers = {"Content-Type": "application/json"}
res = requests.post(url, json=payload, headers=headers)

if res.status_code == 200:
    real_token = res.json().get("accessToken")
    print("✅ Dhan returned a REAL token!")
    
    # Push to GCP Secret Manager
    parent = f"projects/{project_id}/secrets/dhan-access-token"
    try:
        client.add_secret_version(request={"parent": parent, "payload": {"data": real_token.encode("UTF-8")}})
        print("✅ Real token saved to Google Cloud Secret Manager.")
    except Exception as e:
        print(f"❌ Failed to save to GCP: {e}")
else:
    print(f"❌ Dhan rejected the request: {res.text}")
