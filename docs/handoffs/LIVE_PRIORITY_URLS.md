# Live priority URLs (keep open)

**Authority:** Google Cloud serving + GitHub — not laptop files.  
**Updated:** 2026-08-26

## Agent Live Proof Center (NO laptop/gcloud required)

| Priority | Purpose | URL / path |
|---|---|---|
| P0 | Proof center INDEX | `reports/latest/live_proof_center/LATEST/INDEX.md` |
| P0 | Proof center Excel MRI | `reports/latest/live_proof_center/LATEST/System3_LIVE_PROOF_CENTER.xlsx` |
| P0 | Pointer | `reports/coordination/LIVE_PROOF_CENTER_POINTER.md` |
| P0 | Workflow | https://github.com/psw2025-cmd/Genesis_System3/actions/workflows/live-proof-center.yml |
| P0 | Doc | `docs/handoffs/LIVE_PROOF_CENTER.md` |

Runs on `main` push + manual dispatch (no GitHub cron). Read this before claiming “no GCP/laptop access”.

## First priority — live System3

| Priority | Purpose | URL |
|---|---|---|
| P0 | UI Option Chain tab | https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=chain |
| P0 | Broker tab | https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=broker |
| P0 | Serving SHA truth | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/deploy_info |
| P0 | Broker status JSON | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/broker/status |
| P0 | System health | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/system_health |
| P0 | Chain NIFTY JSON | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/chain/NIFTY |
| P1 | Scheduler health | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/scheduler/health?refresh=true |
| P1 | Public state | https://genesis-system3-web-doq2wplepa-el.a.run.app/api/state |

## GitHub (code truth)

| Purpose | URL |
|---|---|
| Repo | https://github.com/psw2025-cmd/Genesis_System3 |
| `main` commits | https://github.com/psw2025-cmd/Genesis_System3/commits/main |
| Coordination #188 | https://github.com/psw2025-cmd/Genesis_System3/issues/188 |
| Actions / Auto Deploy | https://github.com/psw2025-cmd/Genesis_System3/actions/workflows/cloud-run-auto-deploy.yml |
| Live Proof Center workflow | https://github.com/psw2025-cmd/Genesis_System3/actions/workflows/live-proof-center.yml |

## Google Cloud (ops)

| Purpose | URL |
|---|---|
| Cloud Run service | https://console.cloud.google.com/run/detail/asia-south1/genesis-system3-web/metrics?project=system3-openalgo-safe |
| Rotate job | https://console.cloud.google.com/run/jobs/details/asia-south1/genesis-system3-dhan-token-rotate?project=system3-openalgo-safe |
| Scheduler | https://console.cloud.google.com/cloudscheduler?project=system3-openalgo-safe |
| Secret Manager | https://console.cloud.google.com/security/secret-manager?project=system3-openalgo-safe |

## Dhan (you open / keep available) — full market match reference

| Purpose | URL |
|---|---|
| Dhan home | https://web.dhan.co/index/home |
| Advanced option chain (index + equity) | https://web.dhan.co/advancedoptionchain |
| Positions | https://web.dhan.co/index/positions |
| Portfolio | https://web.dhan.co/index/portfolio |
| Dhan API docs | https://dhanhq.co/docs/v2/ |

Parity issue board: `reports/latest/dhan_parity/DHAN_LIVE_PARITY_ISSUES.md`  
RUHI §16 requires same-session Dhan compare before any chain/market PASS.
