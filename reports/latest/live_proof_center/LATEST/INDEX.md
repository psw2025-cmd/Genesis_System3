# SYSTEM3 Live Proof Center

**Generated (UTC):** `2026-08-26T08:32:28Z`  
**Public base:** https://genesis-system3-web-doq2wplepa-el.a.run.app  
**Audience:** ChatGPT / Claude / Cursor / Codex — **no laptop gcloud required**

## Authority

1. GitHub `origin/main` tip (code history)
2. GCP Cloud Run `/api/deploy_info` (what is serving now)
3. This folder — continuously refreshed sanitized forensic pack

Laptop checkouts are **NON-AUTHORITATIVE**.

## Cross-verify snapshot

| Field | Value |
|---|---|
| GitHub main | `afd28722e25d3e66c894c2fc6487722c698a1206` |
| Serving SHA | `fb4772f9d52b67a31b55ee85aab8604e525bbad6` |
| Match | `False` |
| Class | `DIVERGED_CHECK_PATH_FILTER` |
| Revision | `genesis-system3-web-00617-vif` |
| Broker | connected=`True` auth=`AUTH_OK` LIVE=`False` |
| Scheduler healthy | `False` severity=`warning` |
| Gates | `2/7` |
| 4/4 chains ready | `True` |
| API probes OK | 23/23 |
| UI tabs HTTP OK | 22/22 (mount only — semantic NOT_PROVEN) |

## Files in this pack

| File | Purpose |
|---|---|
| `INDEX.md` | This landing page |
| `MANIFEST.json` | Machine SSOT |
| `System3_LIVE_PROOF_CENTER.xlsx` | **12 forensic sheets** (Excel MRI) |
| `CROSS_VERIFY.json` | main vs serving classification |
| `dashboard_tabs.json` | All 22 tab HTTP forensics |
| `gcp_inventory.json` | Cloud Run / jobs / scheduler / secret **names** |
| `api/*.json` | Per-endpoint sanitized dumps |

## Excel sheets (12)

1. `00_Agent_README`
2. `01_Executive`
3. `02_Deploy_Identity`
4. `03_Broker_TokenMeta`
5. `04_Health_State_QC`
6. `05_Option_Chains`
7. `06_Scheduler_Obs`
8. `07_Auto_Gates`
9. `08_API_Probe_Matrix`
10. `09_Dashboard_Tabs_22`
11. `10_FE_BE_Map`
12. `11_GCP_Inventory` + `12_Gaps_Blockers`

## Safety

- No secret **values**, no LIVE enablement, no order calls
- Workflow: `.github/workflows/live-proof-center.yml` (schedule + manual)
- Coordination bus: Issue #188

## How agents must use this

1. Read `MANIFEST.json` + `INDEX.md` first every session  
2. Do not invent PASS from stale laptop MRI  
3. HTTP tab OK ≠ semantic acceptance  
4. If GCP sheet empty, trust public API sheets; ask Cursor only for WIF failures  
