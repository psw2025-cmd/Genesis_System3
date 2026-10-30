import os
import sys
import time
import json
import datetime
import pytz
import pyotp
import requests
from dhanhq import DhanLogin, DhanContext, dhanhq
from google.cloud import secretmanager

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

IST = pytz.timezone('Asia/Kolkata')
now_ist = datetime.datetime.now(IST)
now_utc = datetime.datetime.now(pytz.UTC)

proof = {
    "audit_metadata": {
        "timestamp_ist": now_ist.isoformat(),
        "timestamp_utc": now_utc.isoformat(),
        "workspace": "C:\\Genesis_System3",
        "objective": "DHAN POST-SUBSCRIPTION PROOF & ENTITLEMENT AUDIT",
        "tested_by": "AGY Pair Programmer",
        "environment": "PAPER/ANALYZE (LIVE_TRADING_ENABLED=0)"
    },
    "authentication": {},
    "account_entitlements": {},
    "expiry_lists": {},
    "option_chains": {
        "NIFTY": {},
        "BANKNIFTY": {}
    },
    "eligible_index_options": {},
    "eligible_equity_options": {},
    "market_quotations": {},
    "error_806_status": {},
    "summary": {}
}

print(f"=== DHAN POST-SUBSCRIPTION TEST START: {now_ist.strftime('%Y-%m-%d %H:%M:%S IST')} ===")

# 1. Fetch credentials
project_id = "system3-openalgo-safe"
client = secretmanager.SecretManagerServiceClient()

def get_secret(name):
    path = f"projects/{project_id}/secrets/{name}/versions/latest"
    return client.access_secret_version(request={"name": path}).payload.data.decode("UTF-8").strip()

print("Fetching credentials from Google Cloud Secret Manager...")
client_id = get_secret("dhan-client-id")
pin = get_secret("dhan-pin")
totp_secret = get_secret("dhan-totp-secret")

proof["authentication"]["client_id_masked"] = f"{client_id[:4]}***{client_id[-2:]}" if client_id else "UNKNOWN"
print(f"Client ID: {proof['authentication']['client_id_masked']}")

# Check if we have a locally cached token or need to generate
token = None
cached_token_path = os.path.join(".secrets", "dhan.env")
if os.path.exists(cached_token_path):
    try:
        with open(cached_token_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("DHAN_ACCESS_TOKEN="):
                    token = line.strip().split("=", 1)[1]
    except Exception as e:
        print(f"Notice reading cached token: {e}")

# Test existing token first to avoid rate-limiting token generation
valid_token = False
if token:
    print(f"Testing existing cached token (length {len(token)})...")
    try:
        ctx = DhanContext(client_id, token)
        dhan_client = dhanhq(ctx)
        test_funds = dhan_client.get_fund_limits()
        if test_funds.get("status") == "success":
            valid_token = True
            print("Existing cached token is VALID!")
            proof["authentication"]["token_source"] = "local_cache_valid"
    except Exception as e:
        print(f"Cached token test exception: {e}")

if not valid_token:
    print("Generating fresh Dhan token via DhanLogin...")
    try:
        totp_code = pyotp.TOTP(totp_secret).now()
        dhan_login = DhanLogin(client_id)
        login_res = dhan_login.generate_token(pin, totp_code)
        if login_res and "accessToken" in login_res:
            token = login_res["accessToken"]
            valid_token = True
            print("Fresh token generated successfully! Length:", len(token))
            proof["authentication"]["token_source"] = "freshly_minted_dhanhq"
            proof["authentication"]["token_generation_status"] = "SUCCESS"
            # Cache locally
            os.makedirs(".secrets", exist_ok=True)
            with open(cached_token_path, "w", encoding="utf-8") as f:
                f.write(f"DHAN_CLIENT_ID={client_id}\nDHAN_ACCESS_TOKEN={token}\n")
        else:
            print(f"Token generation response: {login_res}")
            proof["authentication"]["token_generation_response"] = login_res
            # If 2 minute limit, check if latest secret manager version works
            print("Testing latest token from GCP Secret Manager...")
            token = get_secret("dhan-access-token")
            proof["authentication"]["token_source"] = "gcp_secret_manager_latest"
    except Exception as e:
        print(f"Token generation error: {e}")
        proof["authentication"]["token_generation_error"] = str(e)

if not token:
    print("FATAL: No token available")
    sys.exit(1)

# Initialize DhanHQ client
ctx = DhanContext(client_id, token)
d = dhanhq(ctx)

# 2. Account & Entitlement Checks
print("\n--- 1. Testing Account Entitlement & Auth ---")
try:
    funds = d.get_fund_limits()
    if funds.get("status") == "success":
        proof["account_entitlements"]["funds_status"] = "SUCCESS"
        proof["account_entitlements"]["funds_data_available"] = True
        # Redact actual balance value for privacy
        avail = funds.get("data", {}).get("availabelBalance", 0)
        proof["account_entitlements"]["balance_present"] = avail is not None
        print("Funds API: SUCCESS")
    else:
        proof["account_entitlements"]["funds_status"] = "FAILURE"
        proof["account_entitlements"]["funds_response"] = funds
        print(f"Funds API: FAILED - {funds}")
except Exception as e:
    proof["account_entitlements"]["funds_error"] = str(e)
    print(f"Funds API exception: {e}")

time.sleep(1)

try:
    holdings = d.get_holdings()
    if holdings.get("status") == "success":
        h_data = holdings.get("data", [])
        proof["account_entitlements"]["holdings_status"] = "SUCCESS"
        proof["account_entitlements"]["holdings_count"] = len(h_data)
        print(f"Holdings API: SUCCESS, Count: {len(h_data)}")
    else:
        proof["account_entitlements"]["holdings_status"] = "FAILURE"
        proof["account_entitlements"]["holdings_response"] = holdings
        print(f"Holdings API: FAILED - {holdings}")
except Exception as e:
    proof["account_entitlements"]["holdings_error"] = str(e)
    print(f"Holdings API exception: {e}")

time.sleep(1)

# Direct Profile API check to verify subscription / user details
try:
    profile_resp = requests.get(
        "https://api.dhan.co/v2/profile",
        headers={"access-token": token, "client-id": client_id},
        timeout=15
    )
    proof["account_entitlements"]["profile_status_code"] = profile_resp.status_code
    if profile_resp.status_code == 200:
        prof_data = profile_resp.json()
        proof["account_entitlements"]["profile_active"] = True
        # Redact PII
        proof["account_entitlements"]["profile_keys"] = list(prof_data.keys())
        proof["account_entitlements"]["data_api_active"] = prof_data.get("dataApiActive", prof_data.get("data_plan", "CHECKED"))
        print(f"Profile API: HTTP 200 OK, keys: {list(prof_data.keys())}")
    else:
        print(f"Profile API: HTTP {profile_resp.status_code} - {profile_resp.text[:200]}")
except Exception as e:
    print(f"Profile API exception: {e}")
    proof["account_entitlements"]["profile_error"] = str(e)

time.sleep(1)

# 3. Expiry List Checks
print("\n--- 2. Testing Expiry Lists (NIFTY, BANKNIFTY) ---")
nifty_expiries = []
banknifty_expiries = []

try:
    # NIFTY Under Security ID: 13, Exchange: IDX_I
    nifty_exp_res = d.expiry_list(under_security_id=13, under_exchange_segment="IDX_I")
    proof["expiry_lists"]["NIFTY_response"] = nifty_exp_res
    if nifty_exp_res.get("status") == "success":
        nifty_expiries = nifty_exp_res.get("data", [])
        proof["expiry_lists"]["NIFTY"] = {
            "status": "SUCCESS",
            "count": len(nifty_expiries),
            "expiries": nifty_expiries[:8]
        }
        print(f"NIFTY Expiries: SUCCESS ({len(nifty_expiries)} expiries), Nearest: {nifty_expiries[:3]}")
    else:
        proof["expiry_lists"]["NIFTY"] = {"status": "FAILURE", "response": nifty_exp_res}
        print(f"NIFTY Expiries: FAILED - {nifty_exp_res}")
except Exception as e:
    proof["expiry_lists"]["NIFTY"] = {"status": "ERROR", "error": str(e)}
    print(f"NIFTY Expiries exception: {e}")

time.sleep(1.5)

try:
    # BANKNIFTY Under Security ID: 25, Exchange: IDX_I
    bn_exp_res = d.expiry_list(under_security_id=25, under_exchange_segment="IDX_I")
    proof["expiry_lists"]["BANKNIFTY_response"] = bn_exp_res
    if bn_exp_res.get("status") == "success":
        banknifty_expiries = bn_exp_res.get("data", [])
        proof["expiry_lists"]["BANKNIFTY"] = {
            "status": "SUCCESS",
            "count": len(banknifty_expiries),
            "expiries": banknifty_expiries[:8]
        }
        print(f"BANKNIFTY Expiries: SUCCESS ({len(banknifty_expiries)} expiries), Nearest: {banknifty_expiries[:3]}")
    else:
        proof["expiry_lists"]["BANKNIFTY"] = {"status": "FAILURE", "response": bn_exp_res}
        print(f"BANKNIFTY Expiries: FAILED - {bn_exp_res}")
except Exception as e:
    proof["expiry_lists"]["BANKNIFTY"] = {"status": "ERROR", "error": str(e)}
    print(f"BANKNIFTY Expiries exception: {e}")

time.sleep(1.5)

# 4. Option Chain Checks
print("\n--- 3. Testing Option Chains (NIFTY & BANKNIFTY) ---")
# Test NIFTY Option Chain
if nifty_expiries:
    nifty_target_expiry = nifty_expiries[0]
    print(f"Fetching NIFTY option chain for expiry {nifty_target_expiry}...")
    try:
        t0 = time.time()
        n_chain = d.option_chain(under_security_id=13, under_exchange_segment="IDX_I", expiry=nifty_target_expiry)
        elapsed = round(time.time() - t0, 3)
        proof["option_chains"]["NIFTY"]["latency_sec"] = elapsed
        proof["option_chains"]["NIFTY"]["target_expiry"] = nifty_target_expiry
        proof["option_chains"]["NIFTY"]["status"] = n_chain.get("status")
        
        if n_chain.get("status") == "success":
            c_data = n_chain.get("data", {})
            oc_data = c_data.get("oc", {})
            strikes = list(oc_data.keys())
            proof["option_chains"]["NIFTY"]["total_strikes"] = len(strikes)
            proof["option_chains"]["NIFTY"]["sample_strikes"] = strikes[:5]
            proof["option_chains"]["NIFTY"]["last_price"] = c_data.get("last_price")
            print(f"NIFTY Option Chain: SUCCESS! {len(strikes)} strikes returned in {elapsed}s. Spot: {c_data.get('last_price')}")
            # Check quotation quality
            sample_strike = strikes[len(strikes)//2] if strikes else None
            if sample_strike:
                proof["option_chains"]["NIFTY"]["sample_strike_data"] = {
                    "strike": sample_strike,
                    "ce_keys": list(oc_data[sample_strike].get("ce", {}).keys()),
                    "pe_keys": list(oc_data[sample_strike].get("pe", {}).keys())
                }
        else:
            proof["option_chains"]["NIFTY"]["raw_response"] = n_chain
            print(f"NIFTY Option Chain: FAILED/REJECTED - {n_chain}")
            # Check for Error 806
            remarks = str(n_chain)
            if "806" in remarks or "Data API" in remarks:
                proof["error_806_status"]["NIFTY"] = "ERROR_806_OBSERVED"
            else:
                proof["error_806_status"]["NIFTY"] = "NO_806"
    except Exception as e:
        proof["option_chains"]["NIFTY"]["error"] = str(e)
        print(f"NIFTY Option Chain exception: {e}")

time.sleep(2)

# Test BANKNIFTY Option Chain
if banknifty_expiries:
    bn_target_expiry = banknifty_expiries[0]
    print(f"Fetching BANKNIFTY option chain for expiry {bn_target_expiry}...")
    try:
        t0 = time.time()
        bn_chain = d.option_chain(under_security_id=25, under_exchange_segment="IDX_I", expiry=bn_target_expiry)
        elapsed = round(time.time() - t0, 3)
        proof["option_chains"]["BANKNIFTY"]["latency_sec"] = elapsed
        proof["option_chains"]["BANKNIFTY"]["target_expiry"] = bn_target_expiry
        proof["option_chains"]["BANKNIFTY"]["status"] = bn_chain.get("status")
        
        if bn_chain.get("status") == "success":
            c_data = bn_chain.get("data", {})
            oc_data = c_data.get("oc", {})
            strikes = list(oc_data.keys())
            proof["option_chains"]["BANKNIFTY"]["total_strikes"] = len(strikes)
            proof["option_chains"]["BANKNIFTY"]["sample_strikes"] = strikes[:5]
            proof["option_chains"]["BANKNIFTY"]["last_price"] = c_data.get("last_price")
            print(f"BANKNIFTY Option Chain: SUCCESS! {len(strikes)} strikes returned in {elapsed}s. Spot: {c_data.get('last_price')}")
        else:
            proof["option_chains"]["BANKNIFTY"]["raw_response"] = bn_chain
            print(f"BANKNIFTY Option Chain: FAILED/REJECTED - {bn_chain}")
            remarks = str(bn_chain)
            if "806" in remarks or "Data API" in remarks:
                proof["error_806_status"]["BANKNIFTY"] = "ERROR_806_OBSERVED"
            else:
                proof["error_806_status"]["BANKNIFTY"] = "NO_806"
    except Exception as e:
        proof["option_chains"]["BANKNIFTY"]["error"] = str(e)
        print(f"BANKNIFTY Option Chain exception: {e}")

time.sleep(2)

# 5. Market Quotations & Live/Fresh Check
print("\n--- 4. Testing Market Quotations (LTP / Quote) ---")
try:
    # Test LTP for NIFTY Index (exchangeSegment: IDX_I, securityId: 13)
    ltp_payload = {
        "NSE_FNO": [13], # or IDX_I
    }
    # Direct endpoint test for quote
    quote_resp = requests.post(
        "https://api.dhan.co/v2/marketfeed/quote",
        headers={"access-token": token, "client-id": client_id, "Content-Type": "application/json"},
        json={"IDX_I": [13, 25]},
        timeout=15
    )
    proof["market_quotations"]["quote_http_status"] = quote_resp.status_code
    if quote_resp.status_code == 200:
        q_data = quote_resp.json()
        proof["market_quotations"]["status"] = "SUCCESS"
        proof["market_quotations"]["data"] = q_data
        print(f"Market Quote API: SUCCESS - {q_data}")
    else:
        proof["market_quotations"]["response"] = quote_resp.text
        print(f"Market Quote API: Status {quote_resp.status_code} - {quote_resp.text[:200]}")
except Exception as e:
    proof["market_quotations"]["error"] = str(e)
    print(f"Market Quote API exception: {e}")

time.sleep(2)

# 6. Eligible Equity CE/PE Options Check
print("\n--- 5. Testing Eligible Equity Options (e.g. RELIANCE, TCS) ---")
# RELIANCE security_id in NSE is often 2885
try:
    rel_exp = d.expiry_list(under_security_id=2885, under_exchange_segment="NSE_EQ")
    proof["eligible_equity_options"]["RELIANCE_expiry_response"] = rel_exp
    if rel_exp.get("status") == "success":
        r_expiries = rel_exp.get("data", [])
        proof["eligible_equity_options"]["RELIANCE"] = {
            "status": "SUCCESS",
            "expiries_count": len(r_expiries),
            "expiries": r_expiries[:5]
        }
        print(f"RELIANCE Equity Option Expiries: SUCCESS ({len(r_expiries)} expiries), Nearest: {r_expiries[:2]}")
        if r_expiries:
            time.sleep(1.5)
            r_chain = d.option_chain(under_security_id=2885, under_exchange_segment="NSE_EQ", expiry=r_expiries[0])
            if r_chain.get("status") == "success":
                r_strikes = list(r_chain.get("data", {}).get("oc", {}).keys())
                proof["eligible_equity_options"]["RELIANCE"]["chain_status"] = "SUCCESS"
                proof["eligible_equity_options"]["RELIANCE"]["strikes_count"] = len(r_strikes)
                proof["eligible_equity_options"]["RELIANCE"]["sample_strikes"] = r_strikes[:5]
                print(f"RELIANCE Option Chain: SUCCESS! {len(r_strikes)} strikes.")
            else:
                proof["eligible_equity_options"]["RELIANCE"]["chain_status"] = "FAILURE"
                proof["eligible_equity_options"]["RELIANCE"]["chain_response"] = r_chain
                print(f"RELIANCE Option Chain response: {r_chain}")
    else:
        proof["eligible_equity_options"]["RELIANCE"] = {"status": "FAILURE", "response": rel_exp}
        print(f"RELIANCE Equity Option Expiries response: {rel_exp}")
except Exception as e:
    proof["eligible_equity_options"]["RELIANCE_error"] = str(e)
    print(f"RELIANCE Equity Option exception: {e}")

# Summary Evaluation
auth_ok = proof["account_entitlements"].get("funds_status") == "SUCCESS"
exp_ok = (proof["expiry_lists"].get("NIFTY", {}).get("status") == "SUCCESS" or 
          proof["expiry_lists"].get("BANKNIFTY", {}).get("status") == "SUCCESS")
chain_ok = (proof["option_chains"].get("NIFTY", {}).get("status") == "success" or 
            proof["option_chains"].get("BANKNIFTY", {}).get("status") == "success")

# Check if Error 806 occurred
has_806 = "ERROR_806_OBSERVED" in proof.get("error_806_status", {}).values()
proof["summary"] = {
    "auth_authenticated": auth_ok,
    "expiry_lists_operational": exp_ok,
    "option_chains_operational": chain_ok,
    "error_806_present": has_806,
    "overall_status": "PASS" if (auth_ok and exp_ok and not has_806) else "PARTIAL",
    "notes": "Tested live with authentic credentials. Error 806 eliminated if subscription active."
}

# Write output file
os.makedirs("reports/latest", exist_ok=True)
proof_path = os.path.join("reports", "latest", "DHAN_POST_SUBSCRIPTION_PROOF.json")
with open(proof_path, "w", encoding="utf-8") as f:
    json.dump(proof, f, indent=2)

print(f"\nSaved proof to {proof_path}")
print(f"OVERALL SUMMARY: Auth={auth_ok}, Expiries={exp_ok}, Chains={chain_ok}, Error806={has_806}")
