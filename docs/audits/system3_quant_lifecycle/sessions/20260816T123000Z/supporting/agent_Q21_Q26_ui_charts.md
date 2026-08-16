# Q21–Q26 URL-FIRST TRUTH Audit

**Scope:** `c:\System3\Genesis_System3\dashboard\frontend\src` + backend routes in `dashboard\backend\app.py`  
**Acceptance URL:** https://genesis-system3-web-doq2wplepa-el.a.run.app/ui  
**Source of truth for tabs:** wired `Sidebar.tsx` + `App.tsx` (not orphaned components)  
**Note:** Older forensic captures listed Decision Intel / Prediction Audit / Data Integrity; **current React SPA does not wire those tabs.**

---

## 1. Tab map (wired → production nav)

| Group | Tab label | `id` | Component | Status |
|---|---|---|---|---|
| Command | Truth Control | `truth` | `SystemTruthControl.tsx` | WIRED |
| Command | Genesis Brain | `genesis` | `GenesisTab.tsx` | WIRED |
| Command | E2E Proof | `e2e-proof` | `EndToEndProof.tsx` | WIRED |
| Command | Overview | `overview` | `Overview.tsx` | WIRED |
| Command | Sim Live | `sim-live` | `LiveSimulation.tsx` | WIRED |
| Market | Option Chain | `chain` | `OptionChain.tsx` | WIRED |
| Market | Signals | `signals` | `Signals.tsx` | WIRED |
| Trading | Trade | `trade` | `TradeTab.tsx` | WIRED |
| Trading | Paper Trades | `paper` | `PaperTrading.tsx` | WIRED |
| Trading | Positions | `positions` | `Positions.tsx` | WIRED |
| Analysis | Performance | `performance` | `PerformanceTab.tsx` | WIRED |
| Analysis | ML Model | `ml` | `MLPerformance.tsx` | WIRED |
| System | Broker | `broker` | `BrokerPanel.tsx` | WIRED |
| System | Alerts | `alerts` | `AlertsTab.tsx` | WIRED |
| System | System | `system` | `SystemTab.tsx` | WIRED |
| System | Live Gate | `gates` | `LiveTradingGate.tsx` | WIRED |

**Named surfaces NOT in current nav (UI_GAP / orphan):**

| Name (Q25 / forensic) | Repo reality |
|---|---|
| Decision Intel | Not in `Sidebar.tsx` |
| Prediction Audit | No component / route |
| Data Integrity | No dedicated tab (forensic only in `ControlPlane.tsx` orphan) |
| Options Intel / Multibagger / Risk & Scenarios | Not wired |
| `AdvancedCharts.tsx`, `Backtest.tsx`, `AgentConsole.tsx`, `ControlPlane.tsx`, `RiskDashboard.tsx`, `ChainAnalytics.tsx`, `BrokerProofPanel.tsx` | Exist on disk, **not imported by `App.tsx`** |

---

## 2. Q22 required user-visible surfaces

| Surface | Verdict | Best tab(s) | Component | API(s) | Gap notes |
|---|---|---|---|---|---|
| **SYSTEM STATUS** | **PARTIAL** | TopBar + System + Truth + Live Gate | `TopBar.tsx`, `SystemTab.tsx`, `SystemTruthControl.tsx`, `LiveTradingGate.tsx` | `/api/health`, `/api/state`, `/api/batch/*`, `/api/live-trading/gate` | SHA/revision via `deploy-provenance.json` build epoch only; **`/api/deploy/info` (`git_sha`) not consumed**. Token **version id** only in unwired `BrokerProofPanel` (`secret_version`); wired Broker shows `token_status` only. |
| → serving SHA | PARTIAL | TopBar | `TopBar.tsx` (`CloudBuildBadge`) | static `/ui/assets/deploy-provenance.json`; unused `/api/deploy/info` | Not Cloud Run revision SHA |
| → runtime revision | UI_OBSERVABILITY_GAP | — | — | `/api/deploy/info` exists | No UI field |
| → broker | PRESENT | TopBar / Broker / Truth | `BrokerPanel.tsx` | `/api/broker/*`, `/api/batch/positions-holdings` | |
| → token version id | PARTIAL | Broker (unwired proof) | `BrokerProofPanel.tsx` (unwired) | `brokerStatus.token_proof.secret_version` | Wired tab lacks version |
| → data status | PARTIAL | Overview / Truth | `Overview.tsx` | health/state/batch | Endpoint LOADED/WAITING, not full pipeline |
| → market session | PRESENT | TopBar / System | `TopBar.tsx` | store/`/api/health` | |
| → safety locks | PRESENT | System / Live Gate / Proof bar | `SystemTab.tsx`, `LiveTradingGate.tsx`, `App.tsx` | `/api/live-trading/gate`, `/api/auto_gates` | LIVE OFF hard-coded in UI |
| **DATA PIPELINE** | **PARTIAL** | Overview / Truth / Option Chain | above + `OptionChain.tsx` | `/api/batch/chains`, `/api/chain/{sym}`, `/api/instruments/health` | Universe/historical/429 timeline missing in UI |
| → instrument universe coverage | UI_OBSERVABILITY_GAP | — | — | `/api/instruments/health` | API only |
| → quote coverage | PARTIAL | Overview | `Overview.tsx` | batch market/broker | Coarse LOADED/ERROR |
| → option-chain coverage | PARTIAL | Truth / Option Chain | `SystemTruthControl.tsx`, `OptionChain.tsx` | `/api/batch/chains` | 4 required chains; no % coverage board |
| → historical-data coverage | UI_OBSERVABILITY_GAP | — | — | (backend audit helpers) | No UI |
| → freshness | PARTIAL | TopBar / Option Chain | tick age, chain age | batch/chain | No latency/429 charts |
| → missing data | PARTIAL | Overview / Truth | coverage rows | health/state | Not instrument-level missing list |
| → 429 status | UI_OBSERVABILITY_GAP | — | hooks only (`useData.ts`) | transient 429 handling | No timeline surface |
| **FEATURE PIPELINE** | **UI_OBSERVABILITY_GAP** | — | — | none wired | No feature-set version / generation / stale features UI |
| **MODEL** | **PARTIAL** | ML Model | `MLPerformance.tsx` | `/api/ml/performance`, `/api/ml/compare`, `/api/state` | Active + proof table; weak trained-date / training-period / validation detail |
| **TRAINING** | **UI_OBSERVABILITY_GAP** | ML Model (thin) | `MLPerformance.tsx` | same | No schedule, candidates list, promotion-blocked reason board; `best_model` only when proven |
| **PREDICTION** | **PARTIAL** | Signals / Performance | `Signals.tsx`, `PerformanceTab.tsx` | `/api/gain_rank`, scanner, `/api/pnl`; **`/api/accuracy_trend` orphan** | Confidence + ρ bars; no Prediction Audit / actual-result ledger |
| **BACKTEST** | **PARTIAL** | Performance | `PerformanceTab.tsx` | `/api/backtest/results` | JSON dump when ok; standalone `Backtest.tsx` unwired; metrics charts missing |
| **PAPER** | **PRESENT** | Paper Trades / Positions / Performance | `PaperTrading.tsx`, `Positions.tsx` | `/api/paper`, `/api/pnl`, `/api/trades/today`, `/api/state` | Open/closed/P&L/provenance largely visible |
| **STRATEGY** | **PARTIAL** | Signals | `Signals.tsx` | state/scanner | Single strategy string + confidence; no candidate/validation/why-chosen board |
| **AGENT / REMEDIATION PROGRESS** | **UI_OBSERVABILITY_GAP** | Genesis (thin) | `GenesisTab.tsx`; unwired `AgentConsole.tsx` | `/api/agent/*`, genesis routes | No wave/owner/PASS-FAIL/next-dependency matrix on URL |

---

## 3. Q23 / Q24 / Q25 (summary)

| Q | Verdict |
|---|---|
| **Q21** URL-first | Law applies; many truths still API/logs-only → mark **UI_OBSERVABILITY_GAP** where noted |
| **Q23** URL-only progress | **Confirmed gap** — no single consolidated read-only progress surface for all Q22 blocks |
| **Q24** verify via URL | Agents must still browser-prove on `/ui`; code/API-only is insufficient |
| **Q25** matrix template | Use tab map above; for missing tabs set **UI_GAP=TRUE** (Prediction Audit, Data Integrity, Decision Intel, Agent progress) |

### Q25 micro-part → tab hints

| Micro-part | Expected tab | Backend | UI_GAP? |
|---|---|---|---|
| broker reliability | Broker / Truth / System | `/api/broker/*`, batch | No |
| option-chain source | Option Chain | `/api/chain/*`, `/api/batch/chains` | No |
| model version | ML Model | `/api/ml/*`, `/api/state` | Partial |
| prediction performance | *(wanted: Prediction Audit)* / Performance | `/api/accuracy_trend`, gain_rank | **Yes** (no Prediction Audit) |
| historical coverage | *(wanted: Data Integrity)* | instruments/audit APIs | **Yes** |
| backtest metrics | Performance | `/api/backtest/results` | Partial |
| paper lifecycle | Paper / Positions / Performance | `/api/paper`, trades | No |

---

## 4. Q26 chart / graph checklist

| Category | Chart | Verdict | Where / notes |
|---|---|---|---|
| **PRICE** candlestick | MISSING | — | |
| line | MISSING | — | |
| multi-timeframe | MISSING | — | |
| **DERIVATIVES** CE/PE OI | PARTIAL (table bars, not graph) | `OptionChain.tsx` | OI bar cells |
| OI change | PARTIAL (numeric) | `OptionChain.tsx` | ChgOI columns |
| volume | PARTIAL (numeric) | `OptionChain.tsx` | |
| PCR | PARTIAL (scalar) | `OptionChain.tsx` | Full PCR-by-strike chart in unwired `AdvancedCharts.tsx` + `/api/charting/pcr` |
| IV smile | MISSING (wired) | API `/api/charting/iv-surface` + orphan charts | |
| IV skew | MISSING | — | |
| Greeks by strike | MISSING (wired) | orphan `AdvancedCharts` + `/api/charting/greeks` | |
| OI heatmap | MISSING (wired) | orphan + `/api/charting/heatmap` | |
| **MODEL** prediction vs actual | MISSING | — | |
| rolling accuracy | PARTIAL | `PerformanceTab.tsx` | CSS bar sparkline of Spearman ρ (not full chart) |
| calibration | MISSING | — | |
| model drift | MISSING | — | |
| feature importance | MISSING | — | |
| regime performance | MISSING | — | |
| **STRATEGY** equity curve | MISSING | — | |
| drawdown | MISSING (wired) | orphan `Backtest.tsx` has field | |
| trade distribution | MISSING | — | |
| expectancy | PARTIAL | gates / paper labels | not a graph |
| profit factor | MISSING | — | |
| regime split | MISSING | — | |
| **SYSTEM** quote freshness | PARTIAL | TopBar tick / chain age | not a graph |
| API latency | PARTIAL | BrokerProofPanel latency (unwired); no timeline | |
| HTTP 429 timeline | MISSING | — | |
| missing-symbol coverage | MISSING | — | |
| scheduler/job health | MISSING | APIs exist (`/api/scheduler/...`) | no UI |
| model-training timeline | MISSING | — | |

**Only meaningful wired “chart” today:** Performance ρ height bars. Recharts charts live only in unwired `AdvancedCharts.tsx`.

---

## 5. High-value backend vs UI orphans

| API exists | Wired UI consumer? |
|---|---|
| `/api/deploy/info` | No |
| `/api/accuracy_trend` | No |
| `/api/instruments/health` | No |
| `/api/charting/*` | No (orphaned AdvancedCharts) |
| `/api/agent/*` | No (orphaned AgentConsole) |
| `/api/ml/predictions` | No dedicated Prediction Audit |
| `/api/backtest`, `/api/backtest/results` | Results only inside PerformanceTab |

---

## 6. Required UI upgrades (product gaps, no secrets)

1. Wire **SHA/revision** from `/api/deploy/info` into System/Truth/TopBar.  
2. Wire **token version id** (from `token_proof.secret_version`) into Broker (or mount `BrokerProofPanel`).  
3. Add **Data Integrity** tab: universe/quote/chain/historical coverage, freshness, missing, 429.  
4. Add **Prediction Audit** tab: consume `/api/accuracy_trend` + prediction vs actual.  
5. Surface **feature / training / champion-challenger / agent wave** progress as read-only boards.  
6. Either wire `AdvancedCharts` / backtest graphs for Q26 items that answer a real question, or keep them out (no decorative graphs).

**Overall Q22/Q26 score:** PAPER + safety + broker path are strongest; consolidated URL truth for pipeline/features/training/agent/charts remains **UI_OBSERVABILITY_GAP**-heavy.