"""Comprehensive Verification Suite for Genesis System3 Environment Configuration.
Validates .env parser integrity, safety locks, risk parameters, Dhan credentials,
Telegram notifications, and live API endpoint health.
"""
import os
import sys
import json
import urllib.request
from dotenv import dotenv_values

ROOT_DIR = r"C:\Genesis_System3_clean"
ENV_FILE = os.path.join(ROOT_DIR, ".env")
EXAMPLE_FILE = os.path.join(ROOT_DIR, ".env.example")

def run_checks():
    failures = []
    print("=== STEP 1: Verifying .env and .env.example files exist ===")
    if not os.path.exists(ENV_FILE):
        failures.append(".env file does not exist")
    if not os.path.exists(EXAMPLE_FILE):
        failures.append(".env.example file does not exist")

    print("=== STEP 2: Parsing .env with python-dotenv ===")
    try:
        env_vars = dotenv_values(ENV_FILE)
        print(f"Parsed {len(env_vars)} environment variables successfully.")
        if len(env_vars) < 40:
            failures.append(f"Too few environment variables parsed: {len(env_vars)}")
    except Exception as e:
        failures.append(f"Failed to parse .env: {e}")
        return failures

    print("=== STEP 3: Verifying Permanent Safety & Paper Locks ===")
    required_locks = {
        "SYSTEM3_MODE": "paper",
        "ANALYZE_MODE": "1",
        "PAPER_MODE": "1",
        "LIVE_TRADING_ENABLED": "0",
        "SYSTEM3_LIVE_TRADING_ALLOWED": "0",
        "AUTO_EXECUTE_TRADES": "0",
        "LIVE_ORDER_AUTHORITY": "0",
        "ORDER_PLACEMENT_ALLOWED": "false"
    }
    for k, expected in required_locks.items():
        actual = env_vars.get(k)
        if actual != expected:
            failures.append(f"Safety Lock Mismatch for {k}: expected '{expected}', got '{actual}'")
        else:
            print(f"  [PASS] {k} = {actual}")

    print("=== STEP 4: Verifying Capital & Risk Guardrails (Owner Approved) ===")
    risk_checks = {
        "TRADING_CAPITAL_LIMIT_INR": "50000.00",
        "DAILY_STOP_LOSS_LIMIT_INR": "5000.00",
        "CIRCUIT_BREAKER_MAX_LOSS_INR": "5000.00",
        "MAX_DRAWDOWN_PCT": "10.0"
    }
    for k, expected in risk_checks.items():
        actual = env_vars.get(k)
        if actual != expected:
            failures.append(f"Risk Guardrail Mismatch for {k}: expected '{expected}', got '{actual}'")
        else:
            print(f"  [PASS] {k} = {actual}")

    print("=== STEP 5: Verifying Broker (Dhan) Credential Wiring ===")
    client_id = env_vars.get("DHAN_CLIENT_ID", "")
    token = env_vars.get("DHAN_ACCESS_TOKEN", "")
    if not client_id or len(client_id) < 6:
        failures.append(f"Invalid or missing DHAN_CLIENT_ID: {client_id}")
    else:
        print(f"  [PASS] DHAN_CLIENT_ID present: {client_id[:6]}****")

    if not token or len(token) < 20:
        failures.append("Invalid or missing DHAN_ACCESS_TOKEN")
    else:
        print(f"  [PASS] DHAN_ACCESS_TOKEN present (JWT length: {len(token)})")

    print("=== STEP 6: Verifying GCP Mumbai Hybrid Deployment Configuration ===")
    gcp_checks = {
        "GOOGLE_CLOUD_PROJECT": "system3-openalgo-safe",
        "GCP_REGION": "asia-south1",
        "SYSTEM3_DEPLOY_TARGET": "hybrid-mumbai-workstation",
        "SYSTEM3_FIRESTORE_PROJECT": "system3-openalgo-safe"
    }
    for k, expected in gcp_checks.items():
        actual = env_vars.get(k)
        if actual != expected:
            failures.append(f"GCP Config Mismatch for {k}: expected '{expected}', got '{actual}'")
        else:
            print(f"  [PASS] {k} = {actual}")

    print("=== STEP 7: Verifying Notification Webhook Parameters ===")
    tg_chat = env_vars.get("TELEGRAM_CHAT_ID", "")
    tg_token = env_vars.get("TELEGRAM_BOT_TOKEN", "")
    if tg_chat != "1290747576":
        failures.append(f"TELEGRAM_CHAT_ID expected '1290747576', got '{tg_chat}'")
    else:
        print(f"  [PASS] TELEGRAM_CHAT_ID = {tg_chat}")
    if not tg_token:
        failures.append("TELEGRAM_BOT_TOKEN is missing")
    else:
        print(f"  [PASS] TELEGRAM_BOT_TOKEN present (length: {len(tg_token)})")

    print("=== STEP 8: Verifying Live Uvicorn Backend Endpoints ===")
    backend_url = env_vars.get("SYSTEM3_PUBLIC_BACKEND_URL", "http://127.0.0.1:8000")
    test_endpoints = [
        "/api/health",
        "/api/broker/status",
        "/api/risk/portfolio",
        "/api/auto_gates"
    ]
    for ep in test_endpoints:
        url = backend_url + ep
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EnvVerifier/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status != 200:
                    failures.append(f"Endpoint {ep} returned HTTP {resp.status}")
                else:
                    data = json.loads(resp.read().decode("utf-8"))
                    print(f"  [PASS] {ep} -> HTTP 200 OK (keys: {len(data)})")
        except Exception as e:
            failures.append(f"Failed to query {ep}: {e}")

    return failures

if __name__ == "__main__":
    errs = run_checks()
    if errs:
        print(f"\n[FAIL] Environment Integrity Verification FAILED with {len(errs)} error(s):")
        for err in errs:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All 8 Environment Integrity Pillars PASSED with 0 errors!")
        sys.exit(0)
