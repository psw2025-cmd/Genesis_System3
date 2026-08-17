# Broker Secret Policy

- Canonical Secret: `dhan-access-token`
- Banned Secrets: `system3-dhan-access-token`, `DHAN_BROKER_TOKEN` (quarantined in GCP)
- Service: `genesis-system3-web` @ `asia-south1` (Mumbai / operator IST)
- Auto-Heal: On DH-906 / TOKEN_EXPIRED_OR_INVALID, web invokes Cloud Run Job `genesis-system3-dhan-token-rotate` (sole mint authority), waits for Secret Manager version advance, hot-reloads `dhan-access-token`, retries once
- Mutex: single-flight lock in web process + Job expected-version coordination; cooldown default 900s (15 min)
- Pub/Sub topic (event contract): `broker-token-rotate` — optional fan-in signal; mint still executes only via the Cloud Run Job
- LIVE trading remains OFF unless explicitly enabled by human authority
- Label trap: `TOKEN_EXPIRED_OR_INVALID` often means **Dhan auth reject (DH-906)** while JWT clock still has hours left — not Storage / GCS failure
- GCP Storage Insights incident NHLVNDD (us-central1 metadata snapshots) is **UNRELATED** to broker disconnect
- Incident write-up (ChatGPT): `docs/incidents/BROKER_AUTH_20260816_IST.md`

## Production health acceptance checklist

A green workflow or HTTP 200 alone is not broker-health proof. Confirm all of:

- `/api/broker/status`: `connected=true`, `error=null`, source
  `GCP_SECRET_MANAGER_DYNAMIC`, and no token value exposed.
- `/api/health`: broker connected and analyzer ready.
- `/api/batch/market-data`: broker connected with current live data.
- `/api/gain_rank`: current market date and verified spot values.
- `/api/chain/NIFTY` and `/api/chain/BANKNIFTY`: positive Dhan spots and
  populated contracts.
- Production UI, opened in a new browser session: TopBar and Broker tab agree
  with the API; Option Chain displays real Dhan rows.
- `/api/deploy/info.git_sha` equals GitHub `main` and the 100%-traffic Cloud Run
  revision.
- LIVE and order locks remain false.
- Scheduler is enabled; rotation Job is Ready; quarantined aliases have no
  enabled versions or Cloud Run consumers.

Latest request-scoped proof: `reports/latest/broker_health_confirmed/README.md`.
