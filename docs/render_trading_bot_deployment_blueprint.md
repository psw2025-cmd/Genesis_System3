# Genesis System3 Render Trading Bot Deployment Blueprint

Status: analyzer/paper only. Live trading must remain disabled until proof artifacts explicitly pass.

## Purpose

This document is the permanent Render deployment rulebook for Genesis System3. It converts the external learning material about FastAPI + Render + worker deployments into repo-specific operating rules.

## Non-negotiable architecture

| Layer | Render service | Responsibility | Must not do |
|---|---|---|---|
| Web/API | `genesis-system3-backend` | FastAPI dashboard, API routes, health, read-only broker views, truth reports | Long broker polling loops, order placement, blocking scan jobs |
| Worker | `genesis-system3-worker` | Dhan token daemon, watchdog, scheduler, chain polling, paper/analyzer pipeline | Public dashboard serving, live broker order execution |
| GitHub Actions | proof workflows | Render runtime proof, UI proof, live log watch, latest public truth | Store secrets in repo or claim PASS without evidence |
| Render env groups | `dhan-shared-credentials` | Dhan credentials, worker push token, dashboard API key | Commit secret values to GitHub |

## Current render.yaml alignment

The repo blueprint already defines two services:

- `genesis-system3-backend` as a Render web service.
- `genesis-system3-worker` as a Render worker service.

It uses the shared env group `dhan-shared-credentials` for Dhan credentials, `WORKER_PUSH_TOKEN`, and `API_KEY`.

Live trading is explicitly locked off on both services:

```text
SYSTEM3_MODE=analyzer
ANALYZE_MODE=1
LIVE_TRADING_ENABLED=0
SYSTEM3_LIVE_TRADING_ALLOWED=0
```

## Required Render settings

### Shared environment group: `dhan-shared-credentials`

Set these in Render only. Never commit values.

```text
DHAN_CLIENT_ID
DHAN_ACCESS_TOKEN
DHAN_PIN
DHAN_TOTP_SECRET
DHAN_APP_ID
DHAN_APP_SECRET
WORKER_PUSH_TOKEN
API_KEY
```

### Web service env

```text
REQUIRE_API_KEY=true
WEB health check path=/api/health
CLOUD_PAPER_ENGINE=1
DEFER_INSTRUMENT_WARMUP=0
```

### Worker service env

```text
WEB_SERVICE_URL=https://genesis-system3-backend.onrender.com
CLOUD_WORKER=true
CLOUD_PAPER_ENGINE=1
SYSTEM3_PAPER_PIPELINE_V8_ENABLED=1
```

## Service separation rules

### Web/API service

The web service must respond fast to:

```text
/api/health
/api/auth/status
/api/state
/api/chain/<symbol>
/api/broker/dhan/status
/api/broker/funds
/api/broker/holdings
/api/broker/positions/live
/api/gain_rank
/api/scanner/top_contract_gainers?top_n=5
/api/trades/today
/api/auto_gates
```

Slow broker polling must be moved to worker or cached snapshots.

### Worker service

The worker must:

1. Refresh or validate Dhan token.
2. Poll official Dhan option chain only.
3. Persist chain files for paper/analyzer pipeline.
4. Push chain snapshots to the web service using `WORKER_PUSH_TOKEN`.
5. Run paper/analyzer lifecycle only.
6. Never enable live broker order execution.

## Option-chain universe

Enabled money-readiness universe:

```text
NIFTY
BANKNIFTY
FINNIFTY
MIDCPNIFTY
```

Optional watchlist until official Dhan proof is green:

```text
SENSEX
```

SENSEX belongs to the BSE derivatives path. It must be fetched through Dhan only and must not use dummy, CSV, Yahoo, fake, or stale fallback data.

## Proof gates

The system is not considered resolved until the latest repo truth says PASS:

```text
reports/latest/system3_public_truth/index.md
reports/latest/system3_public_truth/index.json
```

Minimum proof required:

| Proof | Required result |
|---|---|
| `cloud_runtime_check` | PASS or acceptable WARN with no deploy mismatch blocker |
| `dashboard_live_ui_proof` | PASS |
| `permanent_live_log_watch` | PASS |
| Enabled Dhan chains | 4/4 PASS, source=dhan, contracts>0, spot>0 |
| Scanner/ranker | candidates present |
| CE/PE decision evidence | present |
| Paper lifecycle | endpoint healthy; paper rows expected only when market/strategy produces candidates |
| Live-money safety lock | PASS, live disabled |

## Render failure patterns and fixes

| Symptom | Meaning | Fix |
|---|---|---|
| `401` from worker push | `WORKER_PUSH_TOKEN` mismatch/missing | Set identical value on web and worker |
| `401` from proof API | `DASHBOARD_API_KEY` does not match Render `API_KEY` | Set same value in GitHub secret and Render env group |
| `429` during proof | proof runner calling API too fast or Render/API rate-limit | Use throttled proof scripts; wait before rerun |
| `502` | Render restart/cold/OOM/temporary unavailable | Check deploy log, memory, wait and rerun proof |
| chain 0 rows | Dhan did not return current/verified option-chain rows | Do not fallback; inspect segment/security id/expiry |
| UI tab timeout | API auth/rate limit or frontend not deployed | Confirm `/ui/`, auth, built assets, proof screenshot |
| ML performance timeout | optional ML panel slow/noisy | Do not block trading-readiness unless core gates depend on it |

## Manual deployment checklist

Before deploy:

```text
1. Confirm latest main branch commit.
2. Confirm Render web + worker are connected to same repo/branch.
3. Confirm env group values exist.
4. Confirm live flags are all 0.
5. Confirm GitHub secret DASHBOARD_API_KEY equals Render API_KEY.
6. Confirm WORKER_PUSH_TOKEN equal on web + worker.
```

Deploy order:

```text
1. Deploy web service.
2. Deploy worker service.
3. Wait 2-3 minutes for chain push loop.
4. Trigger System3 Latest Truth Publish.
5. Read reports/latest/system3_public_truth/index.md.
```

PASS rule:

```text
If latest truth is FAIL or BLOCKED_NOT_TRADE_READY, system is not resolved.
If PASS, system is analyzer/paper-ready only.
Live trading still requires separate manual gate and order-path audit.
```

## Prohibited shortcuts

Do not:

```text
- Enable LIVE_TRADING_ENABLED.
- Commit Dhan tokens or API keys.
- Use fake/synthetic/CSV/Yahoo chain as live data.
- Mark SENSEX as PASS without Dhan rows.
- Treat screenshots as proof without repo artifact.
- Claim money-ready from partial proof.
```

## Operating command for future agents

```text
Read this file first.
Then read render.yaml.
Then read reports/latest/system3_public_truth/index.md.
Patch only the blocker shown by proof.
Never change live order route or secrets.
Trigger truth after each safe patch.
```
