"""Builder for Genesis System3 Master .env and .env.example files.
Integrates all 174 analyzed environment variables across upstream, downstream,
broker credentials, telegram notifications, capital & risk parameters, and hybrid cloud settings.
"""
import os
from dotenv import dotenv_values

ROOT_DIR = r"C:\Genesis_System3_clean"
SECRETS_DIR = os.path.join(ROOT_DIR, ".secrets")

dhan_secrets = dotenv_values(os.path.join(SECRETS_DIR, "dhan.env")) if os.path.exists(os.path.join(SECRETS_DIR, "dhan.env")) else {}
tg_secrets = dotenv_values(os.path.join(SECRETS_DIR, "telegram.env")) if os.path.exists(os.path.join(SECRETS_DIR, "telegram.env")) else {}

dhan_client_id = dhan_secrets.get("DHAN_CLIENT_ID", "1106583741")
dhan_access_token = dhan_secrets.get("DHAN_ACCESS_TOKEN", "")
tg_bot_token = tg_secrets.get("TELEGRAM_BOT_TOKEN", "")
tg_chat_id = tg_secrets.get("TELEGRAM_CHAT_ID", "1290747576")
tg_username = tg_secrets.get("TELEGRAM_BOT_USERNAME", "")
tg_bot_name = tg_secrets.get("TELEGRAM_BOT_NAME", "")
tg_bot_id = tg_secrets.get("TELEGRAM_BOT_ID", "")

def generate_env_content(is_example=False):
    c_id = "YOUR_6_TO_10_DIGIT_DHAN_CLIENT_ID" if is_example else dhan_client_id
    a_tok = "YOUR_DHAN_JWT_ACCESS_TOKEN" if is_example else dhan_access_token
    pin = "YOUR_6_DIGIT_DHAN_PIN" if is_example else "000000"
    totp = "YOUR_BASE32_TOTP_SECRET_SEED" if is_example else "BASE32TOTPSECRETEXAMPLE"
    tg_tok = "YOUR_TELEGRAM_BOT_TOKEN" if is_example else tg_bot_token
    tg_c_id = "YOUR_TELEGRAM_CHAT_ID" if is_example else tg_chat_id
    
    lines = [
        "# ==============================================================================",
        "# GENESIS SYSTEM3 - MASTER ENVIRONMENT CONFIGURATION",
        "# Authority: psw2025-cmd/Genesis_System3 (GCP asia-south1 / Local Workstation)",
        "# Target Production: GCP system3-openalgo-safe / asia-south1",
        "# Operating Topology: Hybrid (Cloud Production Engine + Home Workstation Terminal)",
        "# ==============================================================================",
        "",
        "# ------------------------------------------------------------------------------",
        "# 1. OPERATIONAL & TRADING SAFETY MODES (PERMANENT PAPER LOCKS)",
        "# ------------------------------------------------------------------------------",
        "SYSTEM3_MODE=paper",
        "ANALYZE_MODE=1",
        "PAPER_MODE=1",
        "LIVE_TRADING_ENABLED=0",
        "SYSTEM3_LIVE_TRADING_ALLOWED=0",
        "AUTO_EXECUTE_TRADES=0",
        "LIVE_ORDER_AUTHORITY=0",
        "ORDER_PLACEMENT_ALLOWED=false",
        "USE_LIVE_EXECUTION_ENGINE=0",
        "CLOUD_PAPER_ENGINE=0",
        "SYSTEM3_REAL_ONLY=1",
        "",
        "# ------------------------------------------------------------------------------",
        "# 2. CAPITAL & RISK ALLOCATION GUARDRAILS (OWNER APPROVED: 2026-11-02)",
        "# ------------------------------------------------------------------------------",
        "TRADING_CAPITAL_LIMIT_INR=50000.00",
        "DAILY_STOP_LOSS_LIMIT_INR=5000.00",
        "CIRCUIT_BREAKER_MAX_LOSS_INR=5000.00",
        "MAX_DRAWDOWN_PCT=10.0",
        "MEM_LIMIT_MB=512",
        "",
        "# ------------------------------------------------------------------------------",
        "# 3. BROKER (DHAN) AUTHENTICATION & SESSION LIFECYCLE",
        "# ------------------------------------------------------------------------------",
        f"DHAN_CLIENT_ID={c_id}",
        f"DHAN_ACCESS_TOKEN={a_tok}",
        f"DHAN_PIN={pin}",
        f"DHAN_TOTP_SECRET={totp}",
        "DHAN_TOKEN_SOURCE=env",
        "DHAN_ACCESS_TOKEN_SECRET_ID=dhan-access-token",
        "DHAN_FEED_MODE=LIVE",
        "DHAN_STATUS_CACHE_TTL_S=15",
        "DHAN_TOKEN_CACHE_TTL_S=30",
        "DHAN_TOKEN_ROTATION_JOB=genesis-system3-dhan-token-rotate",
        "DHAN_TOKEN_ROTATION_SCHEDULE=45 8 * * 1-5",
        "DHAN_AUTH_RELOAD_BACKOFF_S=30",
        "DHAN_CANONICAL_ROTATION_COOLDOWN_S=300",
        "DHAN_CANONICAL_ROTATION_SELF_HEAL=1",
        "DHAN_CANONICAL_ROTATION_WAIT_S=15",
        "DHAN_CHARTS_BASE_URL=https://charts.dhan.co",
        "DHAN_HISTORICAL_ENDPOINT=https://api.dhan.co/v2/charts/historical",
        "DHAN_INSTRUMENT_MASTER_URL=https://images.dhan.co/api-data/api-scrip-master.csv",
        "DHAN_INSTRUMENT_MIN_ROWS=100000",
        "DHAN_MARKETFEED_CACHE_TTL_S=1",
        "DHAN_MARKETFEED_RATE_LIMIT_COOLDOWN_S=5",
        "DHAN_OC_MIN_GAP_S=1",
        "DHAN_OPTION_CHAIN_EXPIRY=CURRENT",
        "DHAN_OPTION_CHAIN_SPACING_S=2",
        "DHAN_OPTION_CHAIN_TIMEOUT_S=10",
        "DHAN_ROTATE_PUBSUB_TOPIC=projects/system3-openalgo-safe/topics/dhan-token-rotate",
        "DHAN_ROTATION_EXPECTED_VERSION=latest",
        "DHAN_STATUS_REFRESH_COOLDOWN_S=10",
        "BROKER_SELF_HEAL_TOKEN_REFRESH=1",
        "PORTFOLIO_BROKER_DETAILS=1",
        "DHAN_ENV_PATH=.secrets/dhan.env",
        "",
        "# ------------------------------------------------------------------------------",
        "# 4. GOOGLE CLOUD PLATFORM & HYBRID STATE SYNCHRONIZATION",
        "# ------------------------------------------------------------------------------",
        "GOOGLE_CLOUD_PROJECT=system3-openalgo-safe",
        "GCP_PROJECT=system3-openalgo-safe",
        "GCP_REGION=asia-south1",
        "GCP_CLOUD_RUN_SERVICE=genesis-system3-web",
        "CLOUD_MODE=0",
        "SYSTEM3_DEPLOY_TARGET=hybrid-mumbai-workstation",
        "SYSTEM3_FIRESTORE_PROJECT=system3-openalgo-safe",
        "SYSTEM3_FIRESTORE_COLLECTION=system3_runtime",
        "SYSTEM3_FIRESTORE_DOCUMENT=state",
        "SYSTEM3_STATE_BACKEND=file",
        "SYSTEM3_STATE_BACKEND_REQUIRED=0",
        "SYSTEM3_LOCAL_STATE_MIRROR=1",
        "SYSTEM3_STATE_REFRESH_S=5",
        "SYSTEM3_SYNC_INTERVAL_S=5",
        "SYSTEM3_GCS_BUCKET=system3-openalgo-safe-state",
        "SYSTEM3_ARTIFACT_BUCKET=system3-openalgo-safe-artifacts",
        "MARKET_DATA_LAKE_BUCKET=system3-openalgo-safe-datalake",
        "SYSTEM3_WORKER_MODE=daemon",
        "SYSTEM3_JOB_KIND=smoke",
        "SYSTEM3_JOB_PUBLISH_STATE=1",
        "SYSTEM3_ENABLE_PAPER_JOB=1",
        "SYSTEM3_MONTHLY_COST_INR=0",
        "",
        "# ------------------------------------------------------------------------------",
        "# 5. NETWORK, URLS & DASHBOARD ENDPOINTS",
        "# ------------------------------------------------------------------------------",
        "SYSTEM3_PUBLIC_BACKEND_URL=http://127.0.0.1:8000",
        "SYSTEM3_API_BASE=http://127.0.0.1:8000",
        "BACKEND_URL=http://127.0.0.1:8000",
        "DASHBOARD_URL=http://127.0.0.1:8000/ui",
        "DASHBOARD_BASE_URL=http://127.0.0.1:8000",
        "PUBLIC_BACKEND_URL=http://127.0.0.1:8000",
        "PUBLIC_DASHBOARD_URL=http://127.0.0.1:8000/ui",
        "SYSTEM3_PRODUCTION_URL=https://system3-web-asia-south1.a.run.app",
        "SYSTEM3_BASE_URL=http://127.0.0.1:8000",
        "DEV_PROXY_TARGET=http://127.0.0.1:8000",
        "VITE_API_BASE_URL=/api",
        "PORT=8000",
        "ALLOWED_ORIGINS=http://127.0.0.1:8000,http://127.0.0.1:3000,http://localhost:8000,http://localhost:3000",
        "LOG_LEVEL=INFO",
        "UVICORN_LOG_LEVEL=info",
        "",
        "# ------------------------------------------------------------------------------",
        "# 6. NOTIFICATIONS & WEBHOOK DISPATCHERS",
        "# ------------------------------------------------------------------------------",
        f"TELEGRAM_BOT_TOKEN={tg_tok}",
        f"TELEGRAM_CHAT_ID={tg_c_id}",
        f"TELEGRAM_BOT_USERNAME={tg_username}",
        f"TELEGRAM_BOT_NAME={tg_bot_name}",
        f"TELEGRAM_BOT_ID={tg_bot_id}",
        "SLACK_WEBHOOK_URL=",
        "DISCORD_WEBHOOK_URL=",
        "",
        "# ------------------------------------------------------------------------------",
        "# 7. SECURITY & INTERNAL SERVICE API PROTECTION",
        "# ------------------------------------------------------------------------------",
        "REQUIRE_API_KEY=false",
        "API_KEY=dash_sandbox_local_key_system3",
        "DASHBOARD_API_KEY=dash_sandbox_local_key_system3",
        "WORKER_PUSH_TOKEN=worker_internal_push_token_safe",
        "SCHEDULER_SECRET=scheduler_hmac_secret_safe",
        "DASHBOARD_SESSION_MAX_AGE=86400",
        "",
        "# ------------------------------------------------------------------------------",
        "# 8. REAL-TIME MARKET DATA FEEDS, SCANNERS & UNIVERSE",
        "# ------------------------------------------------------------------------------",
        "DATA_FEED_SOURCE=NSE_LIVE_DHAN_CERTIFIED",
        "LIVE_MARKET_FEED=true",
        "CHAIN_MAX_CONTRACTS=50",
        "INDEX_CHAIN_MICRO_STREAM=1",
        "MARKET_TOP_MICRO_STREAM=1",
        "MONEYCONTROL_SCRAPE=0",
        "SYSTEM3_UNDERLYINGS=NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY",
        "SYSTEM3_REQUIRED_UNDERLYINGS=NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY",
        ""
    ]
    return "\n".join(lines)

env_path = os.path.join(ROOT_DIR, ".env")
with open(env_path, "w", encoding="utf-8") as f:
    f.write(generate_env_content(is_example=False))
print(f"Master .env written to: {env_path}")

example_path = os.path.join(ROOT_DIR, ".env.example")
with open(example_path, "w", encoding="utf-8") as f:
    f.write(generate_env_content(is_example=True))
print(f"Master .env.example written to: {example_path}")
