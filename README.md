# GENESIS SYSTEM 3

Automated Indian F&O trading system (analyzer/paper mode). **Deployed on Google Cloud Run.**

## Deployment (Google Cloud Run — the ONLY production target)

- **Project:** `system3-openalgo-safe` · **Region:** `asia-south1`
- **Web service:** `genesis-system3-web` → https://genesis-system3-web-doq2wplepa-el.a.run.app
- **Token rotation:** Cloud Run Job `genesis-system3-dhan-token-rotate` (07:30 IST daily via Cloud Scheduler)
- **Secrets:** GCP Secret Manager (`dhan-access-token`, `dhan-pin`, `dhan-totp-secret`, `system3-dhan-client-id`)
- **Deploy:** `python scripts/gcp_cloud_run_auto_deploy.py` (builds image tagged with git SHA, forces safe env)

## Token management rules (SYS3-BLK-011 — do not break these)

1. Dhan invalidates ALL prior access tokens the moment a new PIN+TOTP login happens.
2. Therefore only the rotation job may generate tokens. The web service never mints
   (`BROKER_SELF_HEAL_TOKEN_REFRESH=0`, `DHAN_STATUS_AUTO_REFRESH=0`).
3. Every new token is live-validated against `https://api.dhan.co/v2/fundlimit`
   before being persisted to Secret Manager (`core/brokers/dhan/token_manager.py`).
4. Forced Secret Manager reloads are throttled to 1 per 30s (`cloud_token_provider.py`).

## Local development (optional)

```bash
python -m uvicorn dashboard.backend.app:app --host 127.0.0.1 --port 8000
```

## Safety defaults

- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `SYSTEM3_REAL_ONLY=1`
- Real order placement remains blocked unless proof gates and explicit live flags pass.

## Key endpoints

- `GET /api/broker/status` — broker truth (+ `stability` block, SYS3-BLK-001)
- `GET /api/broker/token-health` — rotation health card (SYS3-BLK-011)
- `GET /api/audit/option-visibility` — PE/CE strike+token proof (SYS3-BLK-003)

### Final Operator Message
`I AM ALIVE. I AM LEARNING. ANALYZER MODE IS RUNNING. REAL EARNING IS NOT CLAIMED UNTIL PAPER AND LIVE PROOF PASS.`
