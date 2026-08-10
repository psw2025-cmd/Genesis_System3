# PRD — GENESIS SYSTEM 3 (GCP debugging engagement)

## Original problem statement
User's automated Indian F&O trading system (pre-existing, large codebase) deployed on Google Cloud Run
was stuck in a "Token Paradox" churn loop: Dhan broker invalidates all prior access tokens whenever a
new PIN+TOTP login occurs. The web service's self-heal kept minting new tokens, invalidating the one
just stored, causing infinite DH-906 failures and Secret Manager hammering (~4 reads/sec, reload_count 25k+).
User also accidentally overwrote GCP secret `dhan-pin` with the literal string "NEW_VALUE".

## Deployment reality (CRITICAL for future agents)
- App does NOT run in this pod. It runs on Google Cloud Run.
- Project: `system3-openalgo-safe` (number 802404398783), region `asia-south1`
- Web service: `genesis-system3-web` → https://genesis-system3-web-doq2wplepa-el.a.run.app
- Token rotation: Cloud Run Job `genesis-system3-dhan-token-rotate`
- Deploy script: `scripts/gcp_cloud_run_auto_deploy.py` (forces safe env incl. BROKER_SELF_HEAL_TOKEN_REFRESH=0)
- Test backend changes via curl against the live GCP URL; user executes gcloud commands in Cloud Shell.

## Implemented (2026-08-11)
1. **Secret recovery** (user-executed script): restored dhan-pin (v10), disabled corrupt v9, re-ran rotation
   job → token v35, /fundlimit HTTP 200, live `/api/broker/status` shows connected:true. VERIFIED.
2. **SYS3-BLK-011 permanent fix (code, awaiting redeploy):**
   - `core/brokers/dhan/token_manager.py`: `_validate_token_live()` + `_validated_persist()` — every
     generated/renewed token is proven against /fundlimit BEFORE persisting to Secret Manager.
   - `core/brokers/dhan/cloud_token_provider.py`: `force_reload()` throttled to 1 per 30s (stops SM hammering).
   - `dashboard/backend/app.py`: BROKER_SELF_HEAL_TOKEN_REFRESH default flipped "1"→"0"; fixed busy-loop
     bug where `continue` skipped `asyncio.sleep` in the self-heal watchdog.
   - Local mocked tests: 5/5 passed.
3. **SYSTEM_STATE.md** updated: GCP reality (was falsely claiming Render/Windows), token management SSOT rules.

## User actions pending
- Run gcloud: set BROKER_SELF_HEAL_TOKEN_REFRESH=0 on live service (immediate, no redeploy).
- Create Cloud Scheduler cron 07:30 IST daily for rotation job.
- Redeploy web service to activate code fixes.
- SECURITY: user posted Dhan PIN (197819) in chat — must change PIN on Dhan platform.

## Backlog
- P1 SYS3-BLK-001: false BROKER_DISCONNECTED alert loop — enforce 3-consecutive-failure threshold in
  `dashboard/backend/broker_alert_deduplicator.py` / `broker_truth_validator.py`.
- P2 SYS3-BLK-003: PE/CE strike/token visibility missing.
- P2 SYS3-BLK-004: Equity F&O eligibility not proven before trade readiness.
- P3 SYS3-BLK-006: Markdown doc sprawl cleanup (README.md still mentions Render).
