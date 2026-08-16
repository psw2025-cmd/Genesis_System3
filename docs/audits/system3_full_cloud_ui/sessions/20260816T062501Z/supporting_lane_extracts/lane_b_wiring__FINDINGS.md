# Lane B — Frontend↔Backend Wiring Forensic

**Worktree:** `C:\System3\Genesis_System3_audit_main_c763ecf`  
**Pinned SHA:** `c763ecf048478842688373cf674eb56a7dc04aa9` (verified `git rev-parse HEAD`)  
**Scope:** CURRENT GitHub `main` source ONLY from that worktree. Read-only; scratch reports only.  
**Date:** 2026-08-16

---

## 1. Canonical tab slugs (22)

Source of truth: `dashboard/frontend/src/components/Sidebar.tsx` → `DASHBOARD_TABS`.  
URL sync: `dashboard/frontend/src/App.tsx` → `?tab=<id>` via `DASHBOARD_TAB_IDS`.

| # | slug | label | group | React component (`App.tsx` switch) |
|---|------|-------|-------|-------------------------------------|
| 1 | `decision-intel` | Decision Intel | main | `workspaces/DecisionIntelligence.tsx` |
| 2 | `truth` | Truth Control | main | `SystemTruthControl.tsx` |
| 3 | `genesis` | Genesis Brain | main | `GenesisTab.tsx` |
| 4 | `e2e-proof` | E2E Proof | main | `EndToEndProof.tsx` |
| 5 | `overview` | Overview | main | `Overview.tsx` |
| 6 | `sim-live` | Sim Live | main | `LiveSimulation.tsx` |
| 7 | `options-intel` | Options Intel | market | `workspaces/OptionsIntelligence.tsx` |
| 8 | `chain` | Option Chain | market | `OptionChain.tsx` |
| 9 | `signals` | Signals | market | `Signals.tsx` |
| 10 | `trade` | Trade | trading | `TradeTab.tsx` |
| 11 | `paper` | Paper Trades | trading | `PaperTrading.tsx` |
| 12 | `positions` | Positions | trading | `Positions.tsx` |
| 13 | `risk-scenarios` | Risk & Scenarios | analysis | `workspaces/RiskAndScenarios.tsx` (+ embeds `RiskDashboard.tsx`) |
| 14 | `multibagger` | Multibagger | analysis | `workspaces/MultibaggerResearch.tsx` |
| 15 | `prediction-audit` | Prediction Audit | analysis | `workspaces/PredictionAudit.tsx` |
| 16 | `performance` | Performance | analysis | `PerformanceTab.tsx` |
| 17 | `ml` | ML Model | analysis | `MLPerformance.tsx` |
| 18 | `data-integrity` | Data Integrity | system | `workspaces/DataIntegrity.tsx` (+ `SystemHealthDiagnostics`) |
| 19 | `broker` | Broker | system | `BrokerProofPanel.tsx` (+ `BrokerPanel`) |
| 20 | `alerts` | Alerts | system | `AlertsTab.tsx` |
| 21 | `system` | System | system | `SystemTab.tsx` |
| 22 | `gates` | Live Gate | system | `LiveTradingGate.tsx` |

Global poller (all tabs): `dashboard/frontend/src/hooks/useData.ts` + WebSocket.

---

## 2. Major-tab wiring map

Legend: **S** = Zustand store from `useData` / WS; **D** = component-direct fetch.

| Tab | Primary APIs | Backend owner |
|-----|--------------|---------------|
| decision-intel | S: `/api/batch/market-data`, `/api/state`, broker batch | `app.py` batch + state |
| truth | S: health/state/broker/chain/gainRank/auto_gates/paper | same |
| genesis | S + D: `/genesis-production-brief`, `/autonomous-brain`, `/hidden-secrets-lab`, `/never-die-monitor`, `/hunger-meter`, `/data-truth-score`, `/health`, `/api/system_health`, `/final-message` | legacy non-`/api` routes in `app.py` + `/api/system_health` |
| e2e-proof | S only (proof scoring over store) | — |
| overview | S only | — |
| sim-live | D: `/api/simulation/live/state?scenario=` | `app.py` (registered **twice** ~5461 and ~9764) |
| options-intel | S: chain, marketTop, gainRank, brokerPositions | chain via `/api/batch/chains` + `/api/chain/{sym}`; marketTop via WS/`scanner` |
| chain | S chain + D: `/api/underlyings`, `/api/expiries/{sym}`, `/api/chain-expiry/{sym}?expiry=` | `app.py` underlyings/chain; expiries/chain-expiry via `routers/chain.py` `install_legacy_bridge()` |
| signals | D: `/api/state`, `/api/scanner/top_contract_gainers?top_n=5&market_top_n=25&include_equity=true`, `/api/gain_rank` + `MarketTopCePeTable` (+ moneycontrol) | `app.py` |
| trade | S + D: `/api/scanner/equity_options?top_n=8`, `/api/chain/{sym}` + MarketTop | `app.py` |
| paper | D: `/api/state`, `/api/paper`, `/api/pnl`, `/api/trades/today` | `app.py` |
| positions | S: paper + brokerPositions | batch positions-holdings |
| risk-scenarios | S + D `/api/risk/portfolio` (via RiskDashboard) | `app.py` |
| multibagger | S: `/api/research/multibagger` (useData secondary) | `app.py` |
| prediction-audit | S: `/api/auto_gates` (+ state signals) — **not** a prediction ledger API | `app.py` |
| performance | D: `/api/pnl`, `/api/backtest/results` | `app.py` |
| ml | D: `/api/state`, `/api/ml/performance`, `/api/ml/compare` | `app.py` |
| data-integrity | S + deployInfo `/api/deploy/info` | `app.py` |
| broker | S: `/api/batch/positions-holdings` → status/funds/holdings/positions (+ enrich `/api/broker/status`) | `app.py` |
| alerts | S: alerts from batch (`/api/alerts/recent`) | `app.py` |
| system | S: health/brokerStatus/ws | `app.py` |
| gates | D: `/api/live-trading/gate` | `app.py` |

### Shared poller endpoints (`useData.ts`)

| Path | Role |
|------|------|
| `/api/batch/market-data` | health, slim state, paper, gain_rank, pnl, alerts, auto_gates |
| `/api/state` | preferred full live state |
| `/api/batch/positions-holdings` | broker status/funds/holdings/positions |
| `/api/broker/status` | enrich token_proof when batch slim |
| `/api/market/live_board` | TopBar index/VIX ribbon |
| `/api/batch/chains` + `/api/chain/{sym}` | option chains |
| `/api/deploy/info` | deploy SHA |
| `/api/research/multibagger` | research tab feed |
| `/api/alerts/recent?limit=30` | fallback alerts |
| `/api/auto_gates` | fallback gates |

---

## 3. Option-chain endpoints (paths + query params)

### Canonical live paths (exist on main)

| Method | Path | Query | Registered in |
|--------|------|-------|---------------|
| GET | `/api/chain/{underlying}` | (none required) | `dashboard/backend/app.py` |
| GET | `/api/batch/chains` | (none) | `app.py` |
| GET | `/api/underlyings` | (none) | `app.py` (endpoint swapped by bridge) |
| GET | `/api/expiries/{underlying}` | (none) | `routers/chain.py` → `install_legacy_bridge()` after FastAPI create |
| GET | `/api/chain-expiry/{underlying}` | **`expiry=YYYY-MM-DD`** (required for rows) | same bridge |
| POST | `/api/chain/push` | body push from worker | `app.py` |
| GET | `/api/simulation/live/chain` | simulation-only | `app.py` |

Bridge call site (must run after `app = FastAPI(...)`):

```309:312:C:\System3\Genesis_System3_audit_main_c763ecf\dashboard\backend\app.py
try:
    chain_router.install_legacy_bridge()
except Exception as _chain_bridge_exc:
    ...
```

Comment in `routers/chain.py`: importing the module **before** FastAPI exists previously left `/api/expiries/{underlying}` unregistered → UI `EXPIRY DATA HTTP_404`. Current main calls `install_legacy_bridge()` post-construction.

### `/api/option_chain` — production 404 explained

- **No** `@app.get("/api/option_chain")` (or router equivalent) in `dashboard/backend` on this SHA.
- **No** frontend call to `/api/option_chain` under `dashboard/frontend/src`.
- Live UI uses **`/api/chain/{underlying}`**, not `/api/option_chain`.
- A probe/client hitting `/api/option_chain` on production will correctly get **HTTP 404** (wrong path), not a missing Option Chain feature.

Also: legacy alias `GET /chain/{symbol}` (no `/api` prefix) exists late in `app.py` — not used by React SPA.

### UI consumption

| Consumer | Paths |
|----------|-------|
| `OptionChain.tsx` | `/api/underlyings`, `/api/expiries/{sym}`, `/api/chain-expiry/{sym}?expiry=`, store `chain[sym]` from poller |
| `useData.ts` | `/api/batch/chains`, `/api/chain/{sym}` |
| `TradeTab.tsx` | `/api/chain/{sym}`, `/api/scanner/equity_options?top_n=8` |
| `ChainAnalytics.tsx` | `/api/chain/{selected}` — **orphan component** (not in App switch) |

---

## 4. `source=` / `source=dhan` provenance (option chain)

**Primary render (Option Chain tab):**  
`OptionChain.tsx` status strip (exact `source=` token):

- Reads `data?.data_source ?? state?.data_source`
- Also shows `priority=`, `status=`, `universe=` (from discovery.source), expiry, age, fetched
- Stream chips: `LIVE DHAN` / `DHAN EXPIRY SNAPSHOT` / etc. using `verified_live_dhan` / `live`

**Backend stamps:**

- `chain_adapter.py`: `"data_source": source` (normalized to `dhan`), `"source_priority": "dhan_option_chain_live"` when dhan
- `app.py` `/api/chain/{underlying}`: various statuses with `data_source` often forced to `"dhan"` after middleware
- `middleware/memory_guard.py`: rewrites non-Dhan chain GETs to explicit `NO_DHAN_DATA`; allowed sources `dhan`, `dhan_option_chain_live`
- `useData.ts`: merges `data_source: 'dhan'` / `source: 'dhan_live_board'` for live_board spots

**Other UI surfaces:**

| Location | Field shown |
|----------|-------------|
| `OptionsIntelligence.tsx` | `SOURCE` chip: `currentChain?.source ?? currentChain?.data_source` |
| `EndToEndProof` / `SystemTruthControl` | dhanish check on `data_source`/`source`/`source_priority` |
| `gcp_live_ui_snapshot.py` (tooling, not SPA) | documents `· source=dhan · universe=...` contract |

**Note:** Contract provenance string often appears as **`source=dhan`** in UI copy while JSON field is **`data_source`**. Universe metadata (`universe=security_id_list.csv` / `dhan_security_master`) is **not** the data-source truth (tests in `test_live_ui_truth_remediation_contract.py`).

---

## 5. India VIX wiring

| Layer | Evidence |
|-------|----------|
| Security id | `core/brokers/dhan/market_ltp.py` → `INDEX_SECURITY_IDS["INDIAVIX"] = "26"`; in `DEFAULT_INDEX_BOARD` |
| Backend board | `GET /api/market/live_board` builds board via `build_index_board`, fallback loop includes `INDIAVIX` |
| Frontend poll | `useData.pollLiveBoard` → merges `board.indices` spots into `chain[sym]` |
| UI | `TopBar.tsx` → `getSpot('INDIAVIX')` → ticker label **"India VIX"**; missing labels: `Dhan no quote` / `Dhan unavailable` / `Feed warming` / `After-hours n/a` |

No dedicated `/api/vix` route. VIX is **index LTP board**, not option-chain.

---

## 6. ML / prediction / accuracy — APIs vs UI

| Backend endpoint | Used by wired UI? | Notes |
|------------------|-------------------|-------|
| `GET /api/ml/performance` | **Yes** — `MLPerformance.tsx` (`ml` tab) | Merges tracker + `reports/latest/model_accuracy_report.json` |
| `GET /api/ml/compare` | **Yes** — same | |
| `GET /api/accuracy_trend` | **No SPA caller** | Spearman ρ trend from `market_validations/*.json`; dual field `rank_correlation_spearman` \| `spearman_correlation` |
| `GET /api/gain_rank` | Yes — Signals + batch slim | |
| `GET /api/auto_gates` | Yes — Prediction Audit, Overview, proof bar | ML gate chip via `ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS` |
| `GET /api/ml/predictions` | **No** wired tab | Exists late in `app.py` |
| `GET /api/predict/performance`, `/api/predict/portfolio`, `/api/predict/profit/{id}` | **No** wired tab | |
| `GET /api/performance` | **No** (Performance tab uses `/api/pnl` + backtest) | |
| Prediction Audit tab | Uses **gates + state.signals**, not prediction ledger | Explicit PENDING copy: dedicated ledger not enabled |

---

## 7. Miswiring catalog (evidence from code)

### A. Wrong / missing path (high impact)

1. **`/api/option_chain` 404 on production** — path does not exist; correct path is `/api/chain/{underlying}`. Evidence: no route + no FE reference on SHA.
2. **Historical expiries 404** — if `install_legacy_bridge()` fails/deferred, `/api/expiries/*` and `/api/chain-expiry/*` missing; `OptionChain.tsx` shows `EXPIRY DATA HTTP_404`. Mitigated on this SHA by post-FastAPI bridge call.

### B. Schema mismatches (UI vs backend payload)

1. **`OptionsIntelligence` PCR fields:** UI reads `pcr_oi` / `pcr_vol`; `chain_adapter` / `app.py` emit single **`pcr`**. Result: PCR tiles show `—` even when chain is healthy.
2. **`ChainAnalytics` (orphan):** treats `data_source === 'real' \|\| 'live'` as good; live adapter emits **`dhan`** / `dhan_option_chain_live` → false “not real” UX if ever remounted.
3. **`PredictionAudit` naming:** tab implies prediction ledger; data is **auto_gates** only.
4. **ML accuracy:** backend `/api/accuracy_trend` unused by React; ML tab never shows Spearman ρ time series despite backend + gate chip elsewhere.

### C. UI without dedicated API (store-only — OK if poller healthy)

`overview`, `truth`, `e2e-proof`, `positions`, `alerts`, `system`, `decision-intel`, `data-integrity` (mostly) — rely on `useData`. Failure mode: blank/pending if batch endpoints degrade.

### D. API without wired UI (orphan backend / orphan components)

**Orphan React modules (exist, not in `App.tsx` switch):**

- `ControlPlane.tsx` → runner/learning/forensic/validation mutate+read
- `AgentConsole.tsx` → `/api/agent/*`, `/api/proof-pack`
- `AdvancedCharts.tsx` → `/api/charting/*`
- `ChainAnalytics.tsx` → `/api/chain/{sym}`
- `ModelBehavior.tsx` → `/api/logs/tail`, `/api/audit/secrets`, `/api/qc`
- `AppSelfTest.tsx` → health/learning/forensic/validation/chain/signal/positions/pnl
- `Backtest.tsx` → `/api/backtest/results` (PerformanceTab has its own fetch)
- `Alerts.tsx` → alerts/unread (AlertsTab uses store)
- `SignalsTab.tsx` — superseded by `Signals.tsx`

**Notable backend APIs with no active-tab consumer:**  
`/api/accuracy_trend`, `/api/portfolio/unified`, `/api/trader/requirements`, `/api/ml/predictions`, `/api/predict/*`, `/api/charting/*` (except orphan AdvancedCharts), `/api/agent/*` (except orphan AgentConsole), many `/validate/*` and export routes.

### E. Duplicate / confusing routes

1. Modular routers **disabled** in `app.py` (comments: duplicates broke tabs); bridge still used for expiries.
2. `GET /api/simulation/live/state` defined **twice** in `app.py`.
3. Genesis tab mixes **`/api/*`** and legacy **`/autonomous-brain`**-style paths — optional modules fail soft; shared store remains.

### F. Scanner query params (wired correctly)

| Caller | Path + query |
|--------|----------------|
| Signals / MarketTopCePeTable | `/api/scanner/top_contract_gainers?top_n=5&market_top_n=25&include_equity=true` |
| MarketTopCePeTable | `/api/scanner/moneycontrol_gainers?top_n=25` |
| TradeTab | `/api/scanner/equity_options?top_n=8` |

Backend clamps: `top_n` 1–20, `market_top_n` 5–50.

---

## Top wiring defects (summary)

1. **Wrong option-chain URL:** `/api/option_chain` → 404; use `/api/chain/{underlying}` (+ expiry helpers).
2. **PCR schema break on Options Intel:** UI `pcr_oi`/`pcr_vol` vs API `pcr`.
3. **`/api/accuracy_trend` orphaned from SPA** while ML/gates claim Spearman story.
4. **Prediction Audit ≠ prediction API** — gates-only, no ledger endpoint wired.
5. **Large orphan FE surface** (charts/agent/control-plane) calling live APIs but unreachable from nav.
6. **Expiries/chain-expiry depend on bridge** — any startup failure recreates Option Chain `HTTP_404` for expiry UX.
7. **India VIX** is wired (live_board → TopBar) but not via option-chain; missing quote is environmental, not a missing route.

---

## Artifact index

| File | Purpose |
|------|---------|
| `FINDINGS.md` | This report |
| `tab_api_map.csv` | 22-tab → component → APIs |
| `miswirings.csv` | Defect catalog |
| `api_paths_extract.txt` / `fe_api_all.txt` | Path inventories |
| `_extract_*.py` | Scratch extractors (non-functional) |

---

## Success criteria for this lane

- [x] Worktree SHA matched `c763ecf048478842688373cf674eb56a7dc04aa9`
- [x] All 22 tab slugs listed from Sidebar/App
- [x] Option-chain paths + `/api/option_chain` 404 root-caused
- [x] `source=dhan` provenance render located
- [x] India VIX path traced
- [x] ML/accuracy endpoints vs UI cataloged
- [x] Miswirings with code evidence documented
- [x] No functional code modified
