# GCP Resource / Runtime Map

**Capture:** request-scoped READ-ONLY after 2026-08-16T06:25:01Z

## Cloud Run service

```json
{
  "capture_note": "READ-ONLY forensic; env VALUES omitted; secret PAYLOADS omitted",
  "service": "genesis-system3-web",
  "project": "system3-openalgo-safe",
  "region": "asia-south1",
  "url": "https://genesis-system3-web-doq2wplepa-el.a.run.app",
  "latestReadyRevision": "genesis-system3-web-00384-tuw",
  "latestCreatedRevision": "genesis-system3-web-00384-tuw",
  "observedGeneration": 386,
  "image": "asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3:a48e7b3c7c08-1786830179",
  "serviceAccount": "genesis-system3-web@system3-openalgo-safe.iam.gserviceaccount.com",
  "cpu": "1",
  "memory": "1Gi",
  "containerConcurrency": 50,
  "timeoutSeconds": 300,
  "minInstances": "1",
  "maxInstances": "10",
  "cpuThrottling": "false",
  "executionEnvironment": null,
  "env_NAMES_only": [
    "BROKER_SELF_HEAL_TOKEN_REFRESH",
    "LIVE_TRADING_ENABLED",
    "SYSTEM3_LIVE_TRADING_ALLOWED",
    "AUTO_EXECUTE_TRADES",
    "REQUIRE_API_KEY",
    "ANALYZE_MODE",
    "SYSTEM3_MODE",
    "SYSTEM3_REAL_ONLY",
    "CLOUD_PAPER_ENGINE",
    "DEFER_INSTRUMENT_WARMUP",
    "SYSTEM3_STATE_BACKEND",
    "SYSTEM3_STATE_BACKEND_REQUIRED",
    "SYSTEM3_FIRESTORE_PROJECT",
    "SYSTEM3_STATE_REFRESH_S",
    "SYSTEM3_SYNC_INTERVAL_S",
    "DHAN_TOKEN_SOURCE",
    "DHAN_ACCESS_TOKEN_SECRET_ID",
    "DHAN_TOKEN_CACHE_TTL_S",
    "DHAN_TOKEN_ROTATION_JOB",
    "DHAN_TOKEN_ROTATION_SCHEDULE",
    "DHAN_STATUS_AUTO_REFRESH",
    "DHAN_STATUS_REFRESH_COOLDOWN_S",
    "DHAN_PERSIST_TOKEN_TO_SM",
    "SYSTEM3_STARTUP_TOKEN_REFRESH",
    "DHAN_CANONICAL_ROTATION_SELF_HEAL",
    "DHAN_CANONICAL_ROTATION_COOLDOWN_S",
    "DHAN_CANONICAL_ROTATION_WAIT_S",
    "CLOUD_MODE",
    "SYSTEM3_DEPLOY_TARGET",
    "MEM_LIMIT_MB",
    "MEM_WARN_MB",
    "MEM_GC_MB",
    "MARKET_TOP_MICRO_STREAM",
    "SYSTEM3_PUBLIC_BACKEND_URL",
    "SYSTEM3_API_BASE",
    "DEPLOY_GIT_SHA",
    "FORCE_RESTART_TIMESTAMP",
    "PUBLIC_BACKEND_URL",
    "PUBLIC_DASHBOARD_URL",
    "DEPLOY_STAMP",
    "DHAN_TOKEN_REMOUNT_STAMP"
  ],
  "secret_refs_NAMES": [
    {
      "env": "DHAN_CLIENT_ID",
      "secret": "system3-dhan-client-id",
      "key": "latest"
    },
    {
      "env": "WORKER_PUSH_TOKEN",
      "secret": "system3-dashboard-worker-push-token",
      "key": "latest"
    }
  ],
  "traffic": {
    "revision": "genesis-system3-web-00384-tuw",
    "percent": 100,
    "tag": null,
    "latestRevision": null
  },
  "conditions": [
    {
      "type": "Ready",
      "status": "True",
      "reason": null,
      "message": null
    },
    {
      "type": "ConfigurationsReady",
      "status": "True",
      "reason": null,
      "message": null
    },
    {
      "type": "RoutesReady",
      "status": "True",
      "reason": null,
      "message": null
    }
  ]
}
```

## Jobs / Scheduler

Jobs summary extract present: `True`  
Scheduler summary extract present: `True`

See `supporting_lane_extracts/lane_c_gcp__03_jobs_summary.json` and `...04_scheduler_summary.json`.

## Secret Manager (metadata only)

- Secret names include: dhan-access-token, dhan-pin, dhan-totp-secret, dhan-app-id/secret, system3-dhan-*
- **Enabled versions on dhan-access-token:** 257 (latest version id **257** created 2026-08-16T04:37:57Z)
- **NO payloads accessed**

## Storage services (discovered from env NAMES + code)

| Service | Status |
|---------|--------|
| Firestore | USED (SYSTEM3_STATE_BACKEND env present; state API shows firestore_updated_at) |
| Secret Manager | USED |
| Artifact Registry | USED |
| Cloud Scheduler | USED |
| Cloud Run Jobs | USED (token rotate) |
| GCS lake for OC history | NOT_FOUND / MISSING as PRODUCTION_DURABLE OC store |
| BigQuery / Memorystore | UNKNOWN / not proven in this pass |

## IAM

Read-only compare to baseline deferred to remediation wave; **do not declare IAM closed** while temporary deploy debt documented historically. This audit did not mutate IAM.
