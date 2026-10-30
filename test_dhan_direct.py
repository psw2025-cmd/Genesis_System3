import os
from google.cloud import secretmanager
from dhanhq import DhanContext, dhanhq
import datetime
import pytz

# 1. Securely fetch credentials from Google Cloud
print("Fetching credentials from Google Cloud...")
client = secretmanager.SecretManagerServiceClient()
project_id = "system3-openalgo-safe"

def get_secret(name):
    path = f"projects/{project_id}/secrets/{name}/versions/latest"
    response = client.access_secret_version(request={"name": path})
    return response.payload.data.decode("UTF-8").strip()

client_id = get_secret("dhan-client-id")
access_token = get_secret("dhan-access-token")

print(f"✅ Authenticated for Client ID: {client_id}")

# --- THE FIX: Use DhanContext ---
# The new SDK requires passing credentials via a context object.
dhan_context = DhanContext(client_id, access_token)
dhan = dhanhq(dhan_context)
# --------------------------------

# 2. Test Holdings (Proves Auth 24/7)
print("\n--- TEST 1: HOLDINGS (24/7 Auth Test) ---")
try:
    holdings = dhan.get_holdings()
    if holdings.get("status") == "success":
        print(f"✅ SUCCESS: Retrieved {len(holdings.get('data', []))} holdings.")
        for h in holdings.get("data", [])[:3]:
            print(f"   - {h['tradingSymbol']}: {h['totalQty']} shares")
    else:
        print(f"❌ FAILED: {holdings}")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

# 3. Test Funds (Proves Auth 24/7)
print("\n--- TEST 2: FUNDS (24/7 Auth Test) ---")
try:
    funds = dhan.get_fund_limits()
    if funds.get("status") == "success":
        bal = funds.get("data", {}).get("availabelBalance", 0)
        print(f"✅ SUCCESS: Available Balance is {bal}")
    else:
        print(f"❌ FAILED: {funds}")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")

# 4. Test Option Chain (Proves Market Hours & Rate Limits)
print("\n--- TEST 3: OPTION CHAIN (Market Hours Test) ---")
ist = pytz.timezone('Asia/Kolkata')
now = datetime.datetime.now(ist)
print(f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S IST')}")

try:
    chain = dhan.option_chain(under_security_id=13, under_exchange_segment="IDX_I", expiry="2026-10-30")
    if chain.get("status") == "success":
        print(f"✅ SUCCESS: Retrieved option chain.")
    else:
        print(f"⚠️ DHAN REJECTED (Expected if market is closed): {chain}")
except Exception as e:
    print(f"❌ EXCEPTION: {e}")
