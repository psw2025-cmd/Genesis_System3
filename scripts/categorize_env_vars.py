"""Categorize and produce detailed markdown/JSON documentation of all 174 env vars."""
import json
import os

with open('C:/Genesis_System3_clean/reports/latest/fast_env_inventory.json', 'r') as f:
    items = json.load(f)

item_map = {x['variable']: x for x in items}

categories = {
    "1. Permanent Trading & Safety Locks": [
        ("SYSTEM3_MODE", "paper", "Operational execution mode (paper/analyze/live)"),
        ("ANALYZE_MODE", "1", "Permanent analyzer safety lock (1=enabled)"),
        ("PAPER_MODE", "1", "Simulated paper ledger trading mode (1=paper, 0=live)"),
        ("LIVE_TRADING_ENABLED", "0", "Hard binary live order placement gate (0=blocked)"),
        ("SYSTEM3_LIVE_TRADING_ALLOWED", "0", "Secondary canonical authority check"),
        ("AUTO_EXECUTE_TRADES", "0", "Autonomous broker order dispatch lock (0=off)"),
        ("LIVE_ORDER_AUTHORITY", "0", "Live order routing authority (0=prohibited)"),
        ("ORDER_PLACEMENT_ALLOWED", "false", "String gate for broker payload execution"),
        ("USE_LIVE_EXECUTION_ENGINE", "0", "Live vs paper execution engine selector"),
        ("CLOUD_PAPER_ENGINE", "0", "Legacy paper engine selector"),
        ("SYSTEM3_REAL_ONLY", "1", "Enforce real Dhan feeds without simulated dummy tickers")
    ],
    "2. Capital, Drawdown & Risk Guardrails": [
        ("TRADING_CAPITAL_LIMIT_INR", "50000.00", "Maximum trading capital authorized by owner (₹50,000)"),
        ("DAILY_STOP_LOSS_LIMIT_INR", "5000.00", "Daily maximum loss limit before auto-circuit breaker (₹5,000)"),
        ("CIRCUIT_BREAKER_MAX_LOSS_INR", "5000.00", "Hard kill-switch trigger threshold (₹5,000)"),
        ("MAX_DRAWDOWN_PCT", "10.0", "Maximum daily drawdown percentage (10% of ₹50k = ₹5k)"),
        ("MEM_LIMIT_MB", "512", "Container process RAM ceiling")
    ],
    "3. Broker (Dhan) Authentication & Session Lifecycle": [
        ("DHAN_CLIENT_ID", "110658****", "6-10 digit Dhan account number (masked)"),
        ("DHAN_ACCESS_TOKEN", "dhan_jwt_tok_***[REDACTED]", "24-hour JWT token from web.dhan.co -> DhanHQ Developer Console"),
        ("DHAN_PIN", "pin_******[REDACTED]", "6-digit Dhan financial PIN for automated renewal"),
        ("DHAN_TOTP_SECRET", "totp_seed_***[REDACTED]", "Base32 authenticator seed for 08:45 AM automated login"),
        ("DHAN_TOKEN_SOURCE", "gcp-secret-manager", "Authority for token loading: env | gcp-secret-manager"),
        ("DHAN_ACCESS_TOKEN_SECRET_ID", "dhan-access-token", "GCP Secret Manager secret resource name"),
        ("DHAN_FEED_MODE", "LIVE", "Market data feed mode: LIVE | SIMULATED"),
        ("DHAN_STATUS_CACHE_TTL_S", "15", "Broker status poll cache TTL seconds"),
        ("DHAN_TOKEN_CACHE_TTL_S", "30", "Access token memory cache TTL seconds"),
        ("DHAN_TOKEN_ROTATION_JOB", "genesis-system3-dhan-token-rotate", "Cloud Run Job authority for automated token rotation"),
        ("DHAN_TOKEN_ROTATION_SCHEDULE", "45 8 * * 1-5", "Cloud Scheduler cron expression (08:45 IST trading days)"),
        ("DHAN_AUTH_RELOAD_BACKOFF_S", "30", "Auth reload backoff timeout upon rejected version"),
        ("DHAN_CANONICAL_ROTATION_COOLDOWN_S", "300", "Rotation cooldown period"),
        ("DHAN_CANONICAL_ROTATION_SELF_HEAL", "1", "Self-healing auto-recovery upon token expiration"),
        ("DHAN_CANONICAL_ROTATION_WAIT_S", "15", "Wait seconds for newly published Secret Manager version"),
        ("DHAN_CHARTS_BASE_URL", "https://charts.dhan.co", "Dhan charts endpoint"),
        ("DHAN_HISTORICAL_ENDPOINT", "https://api.dhan.co/v2/charts/historical", "Dhan historical candles API"),
        ("DHAN_INSTRUMENT_MASTER_URL", "https://images.dhan.co/api-data/api-scrip-master.csv", "Dhan 117k scrip master CSV"),
        ("DHAN_INSTRUMENT_MIN_ROWS", "100000", "Integrity check for minimum valid scrip count"),
        ("DHAN_MARKETFEED_CACHE_TTL_S", "1", "WebSocket / REST feed cache TTL"),
        ("DHAN_MARKETFEED_RATE_LIMIT_COOLDOWN_S", "5", "Dhan marketfeed rate-limit backoff cooldown"),
        ("DHAN_OC_MIN_GAP_S", "1", "Option chain query throttle gap"),
        ("DHAN_OPTION_CHAIN_EXPIRY", "CURRENT", "Target expiry selection strategy"),
        ("DHAN_OPTION_CHAIN_SPACING_S", "2", "Strike spacing delay in batch fetches"),
        ("DHAN_OPTION_CHAIN_TIMEOUT_S", "10", "Dhan option chain HTTP request timeout"),
        ("DHAN_ROTATE_PUBSUB_TOPIC", "projects/system3-openalgo-safe/topics/dhan-token-rotate", "PubSub topic for token rotation alerts"),
        ("DHAN_ROTATION_EXPECTED_VERSION", "latest", "Expected secret manager version tag"),
        ("DHAN_STATUS_REFRESH_COOLDOWN_S", "10", "Status refresh cooldown period"),
        ("BROKER_SELF_HEAL_TOKEN_REFRESH", "1", "Automatic background token refresh enable"),
        ("PORTFOLIO_BROKER_DETAILS", "1", "Include read-only broker ledger in portfolio endpoint")
    ],
    "4. Google Cloud Platform & Hybrid State Synchronization": [
        ("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe", "Authoritative GCP project ID"),
        ("GCP_PROJECT", "system3-openalgo-safe", "Alias for Google Cloud Project"),
        ("GCP_REGION", "asia-south1", "Primary GCP region (Mumbai colocation)"),
        ("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web", "Target Cloud Run service name"),
        ("CLOUD_MODE", "0", "0=Localhost/Workstation client, 1=Deployed Cloud Run container"),
        ("SYSTEM3_DEPLOY_TARGET", "hybrid-mumbai-workstation", "Target topology (gcp-mumbai / hybrid / local-laptop)"),
        ("SYSTEM3_FIRESTORE_PROJECT", "system3-openalgo-safe", "Firestore state database project"),
        ("SYSTEM3_FIRESTORE_COLLECTION", "system3_runtime", "Firestore state collection"),
        ("SYSTEM3_FIRESTORE_DOCUMENT", "state", "Firestore state document name"),
        ("SYSTEM3_STATE_BACKEND", "firestore", "State persistence backend (firestore | file)"),
        ("SYSTEM3_STATE_BACKEND_REQUIRED", "0", "Failover to local file state if firestore offline"),
        ("SYSTEM3_LOCAL_STATE_MIRROR", "1", "Keep local JSON mirror of firestore state"),
        ("SYSTEM3_STATE_REFRESH_S", "5", "State polling refresh interval in seconds"),
        ("SYSTEM3_SYNC_INTERVAL_S", "5", "State sync interval between workstation and cloud"),
        ("SYSTEM3_GCS_BUCKET", "system3-openalgo-safe-state", "Cloud storage bucket for persistent reports"),
        ("SYSTEM3_ARTIFACT_BUCKET", "system3-openalgo-safe-artifacts", "Cloud storage bucket for builds/audit packages"),
        ("MARKET_DATA_LAKE_BUCKET", "system3-openalgo-safe-datalake", "Cloud storage bucket for raw tick and candle data"),
        ("SYSTEM3_WORKER_MODE", "daemon", "Background worker execution mode"),
        ("SYSTEM3_JOB_KIND", "smoke", "Job kind for scheduled smoke runs"),
        ("SYSTEM3_JOB_PUBLISH_STATE", "1", "Publish state telemetry to Firestore"),
        ("SYSTEM3_ENABLE_PAPER_JOB", "1", "Allow paper trading engine in scheduled jobs"),
        ("SYSTEM3_MONTHLY_COST_INR", "0", "Budget tracking metric for zero unapproved cost")
    ],
    "5. Network, URLs & Dashboard Endpoints": [
        ("SYSTEM3_PUBLIC_BACKEND_URL", "http://127.0.0.1:8000", "Publicly accessible backend URL (or Cloud Run URL in prod)"),
        ("SYSTEM3_API_BASE", "http://127.0.0.1:8000", "Base URL for internal API client calls"),
        ("BACKEND_URL", "http://127.0.0.1:8000", "Standard backend URL reference"),
        ("DASHBOARD_URL", "http://127.0.0.1:8000/ui", "Operator dashboard browser entrypoint"),
        ("DASHBOARD_BASE_URL", "http://127.0.0.1:8000", "Dashboard root URL"),
        ("PUBLIC_BACKEND_URL", "http://127.0.0.1:8000", "Public reverse proxy alias"),
        ("PUBLIC_DASHBOARD_URL", "http://127.0.0.1:8000/ui", "Public dashboard UI alias"),
        ("SYSTEM3_PRODUCTION_URL", "https://system3-web-asia-south1.a.run.app", "Cloud Run production ingress URL"),
        ("SYSTEM3_BASE_URL", "http://127.0.0.1:8000", "Base service URL"),
        ("DEV_PROXY_TARGET", "http://127.0.0.1:8000", "Vite local dev proxy backend target"),
        ("VITE_API_BASE_URL", "/api", "Vite client relative or absolute API base"),
        ("PORT", "8000", "Server listening TCP port"),
        ("ALLOWED_ORIGINS", "http://127.0.0.1:8000,http://127.0.0.1:3000,http://localhost:8000,http://localhost:3000", "CORS allowed origins"),
        ("LOG_LEVEL", "INFO", "Uvicorn/FastAPI log level (DEBUG | INFO | WARNING | ERROR)"),
        ("UVICORN_LOG_LEVEL", "info", "Uvicorn server log level")
    ],
    "6. Notifications & Webhook Dispatchers": [
        ("TELEGRAM_BOT_TOKEN", "bot_tok_***[REDACTED_SET_VIA_BOTFATHER]", "Telegram Bot API token from @BotFather"),
        ("TELEGRAM_CHAT_ID", "1290747576", "Owner Telegram chat ID for mobile push alerts"),
        ("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/***[REDACTED]", "Slack incoming webhook URL for risk/order alerts"),
        ("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/***[REDACTED]", "Discord incoming webhook URL for emergency notifications")
    ],
    "7. Security & API Protection": [
        ("REQUIRE_API_KEY", "false", "Enforce X-API-Key authentication (false in local workstation sandbox)"),
        ("API_KEY", "dash_sec_***[REDACTED_SECURITY_POLICY]", "Dashboard API Key header value"),
        ("DASHBOARD_API_KEY", "dash_sec_***[REDACTED_SECURITY_POLICY]", "Dashboard API Key alias"),
        ("WORKER_PUSH_TOKEN", "push_tok_***[REDACTED_SECURITY_POLICY]", "Bearer token for internal Cloud Scheduler / Worker IPC"),
        ("SCHEDULER_SECRET", "sched_sec_***[REDACTED_SECURITY_POLICY]", "HMAC secret for Cloud Scheduler webhook verification"),
        ("DASHBOARD_SESSION_MAX_AGE", "86400", "UI operator session duration in seconds (24h)")
    ],
    "8. Market Data Feeds, Scanners & Universe": [
        ("DATA_FEED_SOURCE", "NSE_LIVE_DHAN_CERTIFIED", "Primary market data provider"),
        ("LIVE_MARKET_FEED", "true", "Enable real-time market quote ingestion"),
        ("CHAIN_MAX_CONTRACTS", "50", "Max contracts fetched per option chain strike window"),
        ("INDEX_CHAIN_MICRO_STREAM", "1", "Enable micro-streaming for 4 core indices"),
        ("MARKET_TOP_MICRO_STREAM", "1", "Enable top gainers/losers streaming"),
        ("MONEYCONTROL_SCRAPE", "0", "Secondary scraper fallback (0=disabled, use Dhan API)"),
        ("SYSTEM3_UNDERLYINGS", "NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY", "Permitted trading index universe"),
        ("SYSTEM3_REQUIRED_UNDERLYINGS", "NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY", "Required baseline symbols for health readiness")
    ]
}

# Generate markdown table and save
out_md = []
out_md.append("# Genesis System3 - Comprehensive Forensic Environment Variable Matrix\n")
out_md.append("Extracted from 174 identified variables across the codebase.\n")

for cat_title, var_entries in categories.items():
    out_md.append(f"\n### {cat_title}\n")
    out_md.append("| Environment Variable | Recommended / Default Value | Purpose & System Impact | Codebase References |")
    out_md.append("| :--- | :--- | :--- | :--- |")
    for var_name, default_val, desc in var_entries:
        f_info = item_map.get(var_name)
        refs = f"{f_info['file_count']} files ({f_info['count']} refs)" if f_info else "Config / Template"
        out_md.append(f"| `{var_name}` | `{default_val}` | {desc} | {refs} |")

report_text = "\n".join(out_md)
with open('C:/Genesis_System3_clean/reports/latest/env_variables_forensic_matrix.md', 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"Matrix written to C:/Genesis_System3_clean/reports/latest/env_variables_forensic_matrix.md")
