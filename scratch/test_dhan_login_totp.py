import os
import pyotp
from pathlib import Path
from dhanhq import DhanLogin

# Read .env directly
env_path = Path(".env")
env_vars = {}
for line in env_path.read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.split("=", 1)
        env_vars[k.strip()] = v.strip().strip("'\"")

client_id = env_vars.get("DHAN_CLIENT_ID", "")
pin = env_vars.get("DHAN_PIN", "")
totp_secret = env_vars.get("DHAN_TOTP_SECRET", "")

print(f"Client ID: {client_id[:4]}****, PIN len: {len(pin)}, TOTP secret len: {len(totp_secret)}")

if client_id and pin and totp_secret:
    try:
        totp = pyotp.TOTP(totp_secret)
        current_totp = totp.now()
        print(f"Generated TOTP code: {current_totp[:2]}****")
        print("Attempting DhanLogin with client_id, pin, and totp...")
        dhan_login = DhanLogin(client_id=client_id, user_pin=pin, totp=current_totp)
        token_data = dhan_login.consume_login()
        print("DhanLogin result keys:", list(token_data.keys()) if isinstance(token_data, dict) else token_data)
        if isinstance(token_data, dict) and "accessToken" in token_data:
            print("Successfully minted fresh Dhan access token!")
            # We can save this to state/new_token_temp.json
        else:
            print("DhanLogin failed to return accessToken:", token_data)
    except Exception as e:
        print("DhanLogin exception:", e)
else:
    print("Missing client_id, pin, or totp_secret in .env!")
