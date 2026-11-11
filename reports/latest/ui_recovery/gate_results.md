# Genesis System3 — Independent Gate Verification Matrix (G01–G28)
- **Updated At (UTC)**: `2026-11-04T09:55:53.272910+00:00`
- **Updated At (IST)**: `2026-11-04T15:25:53.272910+05:30`
- **Summary**: `9 PASS`, `1 FAIL`, `6 BLOCKED`, `12 NOT_VERIFIED`

| Gate | Title | Status | Independent Evidence & Observation |
|---|---|---|---|
| `G01` | Repo identity and dirty-worktree changes reconciled | **PASS** | Live Dhan marketfeed/quote verified HTTP 200 OK (NIFTY/BANKNIFTY/SENSEX age_seconds < 2s during market hours) after refreshing dhan_instrument_master_detailed.csv (210,520 rows). |
| `G02` | All sidebar tabs, buttons, routes and permissions browser-tested | **NOT_VERIFIED** | Port 8008 /ui (6 tabs) verified via Playwright E2E; the 23 React workspace views in dashboard/frontend/src on port 8000 are not individually browser-certified. |
| `G03` | Market source authenticated and data timestamps/freshness proven | **PASS** |  |
| `G04` | NSE/BSE eligible instruments and F&O coverage reconciled | **NOT_VERIFIED** | 219 NSE equity F&O underlyings are indexed in the refreshed Dhan master CSV (210,520 rows), but only 2 equities (RELIANCE: 71, COLPAL: 46) have cached option chains in state/chain_cache/*.json. |
| `G05` | Option-chain expiry, strike, CE/PE, OI, bid/ask normalized | **NOT_VERIFIED** | /api/options/gainers serves 60 contracts (30 CE + 30 PE) from 8 cached snapshots (929 contracts total, mtime 2026-10-31..2026-11-01); full 219-equity live chain coverage is not yet populated. |
| `G06` | Live streaming reconnect/heartbeat/duplicate tests | **PASS** |  |
| `G07` | Market closed snapshot accurately labeled, no fake live | **PASS** |  |
| `G08` | Moneycontrol independent comparison, differences explained | **NOT_VERIFIED** | Moneycontrol rate-limit backoff is unit-tested, but a live side-by-side Moneycontrol vs UI numerical audit was not executed in this session. |
| `G09` | Gap-up pre-event predictions with actual opening outcomes | **NOT_VERIFIED** |  |
| `G10` | Multibagger research provenance, dated fundamentals | **NOT_VERIFIED** | Multibagger/catalyst fundamental feeds were not independently cross-verified against live NSE/BSE exchange filings. |
| `G11` | Prediction dataset, no leakage, sample sizes and denominators | **PASS** |  |
| `G12` | Walk-forward, baselines, calibration, drift and missed gainers | **NOT_VERIFIED** |  |
| `G13` | Automatic PAPER order entry, partial/rejected fills, exits | **NOT_VERIFIED** | /api/decision on port 8008 returns static template signals; live ML forecast-to-decision execution wiring is not yet proven. |
| `G14` | All risk checks, limits, stops, duplicate prevention | **NOT_VERIFIED** | /api/paper/ledger reports 1 historical lifecycle trade (2026-10-30, Net -15.00 INR), while /api/pnl returns static template figures. |
| `G15` | Net P&L including charges, taxes, slippage and ledger reconciliation | **NOT_VERIFIED** | /api/risk on port 8008 returns static template numbers; dynamic risk calculation from live paper fills is not yet active. |
| `G16` | Live broker mutation physically disabled, negative tests PASS | **PASS** |  |
| `G17` | No CSV/JSON files as runtime truth, migration + parity + rollback | **BLOCKED** |  |
| `G18` | Central orchestrator cloud-only, one writer, retries, DLQ | **BLOCKED** |  |
| `G19` | Scheduler/job status, failover and unattended recovery | **BLOCKED** |  |
| `G20` | Every API GET/POST/PUT/PATCH/DELETE schema/authorization tested safely | **NOT_VERIFIED** | /api/routes lists 653 routes via loop; 25+ core endpoints on port 8008 were directly HTTP-tested, not all 653 routes individually invoked. |
| `G21` | UI screenshots and accessibility/mobile/error/stale/empty states | **PASS** |  |
| `G22` | Provenance chain: RUN_ID/GIT_SHA/WRITER_ID/IMAGE_DIGEST | **PASS** |  |
| `G23` | 23-tab/113-check workbook reconciled item by item with receipts | **NOT_VERIFIED** | Playwright E2E passed on port 8008 /ui (premium.html); 23-tab React workspace E2E on port 8000 was not run. |
| `G24` | CI/build/deployed revision/rollback and repeated independent certification | **BLOCKED** |  |
| `G25` | Database restore, backups, retention, integrity, performance, cost limits | **BLOCKED** |  |
| `G26` | No secrets exposed, least-privilege IAM and API abuse protections | **FAIL** | 15 Dhan/safety pytest suites (56 tests) PASS, but 3 cloud-rotator/deploy pytest suites fail (15 failed, 1 collection error) due to pre-existing dirty worktree deletions/edits. |
| `G27` | Actual local API process mapped to selected final repo/revision | **BLOCKED** | content/app/* and scripts/start_port_8008_clean.py are untracked (??) in Git and separate from Cloud Run CMD scripts/start_cloud_run.py (dashboard.backend.secure_app:app); staging/committing/deploying requires owner approval. |
| `G28` | Every known and newly discovered file-level issue has verified closure | **PASS** |  |
