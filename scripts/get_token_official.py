import os
import pyotp
from dhanhq import DhanLogin
from google.cloud import secretmanager

project_id = "system3-openalgo-safe"
client = secretmanager.SecretManagerServiceClient()

def get_secret(name):
    path = f"projects/{project_id}/secrets/{name}/versions/latest"
    response = client.access_secret_version(request={"name": path})
    return response.payload.data.decode("UTF-8").strip()

print("Fetching credentials from GCP...")
client_id = "1106583741"
pin = get_secret("dhan-pin")
totp_secret = get_secret("dhan-totp-secret")

# The library generate_token takes (pin, totp_code), NOT totp_secret!
print("Generating TOTP code from secret...")
totp_code = pyotp.TOTP(totp_secret).now()

print("Requesting real token via official Dhan library...")
dhan_login = DhanLogin(client_id)
access_token_data = dhan_login.generate_token(pin, totp_code)

if access_token_data and "accessToken" in access_token_data:
    real_token = access_token_data["accessToken"]
    print("✅ Dhan returned a REAL token!")
    
    # Push to GCP Secret Manager
    parent = f"projects/{project_id}/secrets/dhan-access-token"
    try:
        client.add_secret_version(request={"parent": parent, "payload": {"data": real_token.encode("UTF-8")}})
        print("✅ Real token saved to Google Cloud Secret Manager.")
    except Exception as e:
        print(f"❌ Failed to save to GCP: {e}")
else:
    print(f"❌ Dhan rejected the request: {access_token_data}")
