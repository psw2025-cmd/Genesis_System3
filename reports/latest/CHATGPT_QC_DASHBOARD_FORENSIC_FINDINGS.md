# ChatGPT QC + Dashboard + Render Forensic Findings

**Repository:** `psw2025-cmd/Genesis_System3`  
**Branch:** `chatgpt/qc-dashboard-forensic-md`  
**Scope:** QC forensic analysis, anomaly detection, dashboard/frontend/backend/Render readiness, auto snapshot plan.  
**Mode:** Analyzer/Paper only. No live trading. No secrets touched.

---

## 0. Current Verdict

```text
QC_READY = false
DASHBOARD_READY = false
RENDER_READY = not_proven
ANOMALY_DETECTION_READY = partial
PAPER_ANALYZER_READY = partial / not_proven
LIVE_TRADING_READY = false
```

**Reason:** System has many useful QC/dashboard pieces, but they are scattered and not yet one single source-of-truth proof chain.

---

## Patch Pack 1 status

```text
QCValidator init-order bug: fixed
Dhan bid/ask aliases: fixed
OI-change aliases: helper/compatibility added
Tests added: tests/test_qc_validator_dhan_aliases.py
Live trading: unchanged disabled
Broker write APIs: not touched
```
---

## Dhan naming and platform truth

```text
Dhan Advance Platform: NOT_OFFICIAL_EXACT_NAME
DhanHQ API v2: OFFICIAL_SUPPORTED and current System3 authority
Dhan Cloud: OFFICIAL_SUPPORTED, separate future evaluation
Strategy hosting under Dhan Cloud: OFFICIAL_SUPPORTED
Dhan Cloud strategy templates: OFFICIAL_SUPPORTED as strategy-code starting templates
React/TypeScript frontend dashboard templates: NOT_VERIFIED
System3 migration recommendation: DO_NOT_MIGRATE_NOW
Current System3 mode: Analyzer/Paper only
```

System3 should continue as a DhanHQ API v2 integration in Analyzer/Paper mode. Dhan Cloud can be evaluated separately later after the Analyzer/Paper proof chain is stable. Do not enable live trading or order writes in this branch.
---

## 1. High-Level Findings

| Area | Finding | Severity | Status |
|---|---|---:|---|
| QC validator | `paper_sanity_mode` uses `underlying_min_contracts` before assignment | P0 | Needs fix |
| Dhan field compatibility | QC checks `bidPrice/offerPrice`, but Dhan uses `top_bid_price/top_ask_price` | P0 | Needs alias support |
| OI-change contract | React expects `dOI`; backend sends `oi_change` | P0 | Needs compatibility |
| Runtime QC | `/api/qc` reads `qc_report_live.json`, while `/api/chain` can fetch runtime data | P0 | Needs `/api/qc/runtime` |
| Dashboard source truth | React and legacy Vue dashboards both exist | P0 | Needs React authority decision |
| Render build | React build failure can silently fall back to Vue | P1 | Should fail deploy after React becomes authority |
| Hardcoded UI readiness | React `Overview.tsx` hardcodes gate values | P1 | Must use API truth |
| Auto proof | No stable auto snapshot folder yet | P1 | Add `reports/latest/dashboard_auto_snap/` |
| Existing QC audit | `comprehensive_qc_audit.py` hardcodes `c:/Genesis_System3` | P1 | Make root dynamic |
| Dashboard validation | `scripts/dashboard_data_validator.py` uses localhost only | P1 | Add `SYSTEM3_PUBLIC_BACKEND_URL` |

---

## 2. QC Forensic Findings

### 2.1 `QCValidator` initialization-order bug

**File:** `src/validation/qc_validator.py`

The constructor applies `paper_sanity_mode` before `self.underlying_min_contracts` is created.

**Current risk:**

```text
QCValidator(paper_sanity_mode=True) can fail during initialization.
```

**Recommendation:**

Move `self.underlying_min_contracts = {...}` above the `paper_sanity_mode` block.

---

### 2.2 Bid/ask alias mismatch

**Files:**

- `src/validation/qc_validator.py`
- `core/data/dhan_option_chain_parser.py`
- `dashboard/backend/chain_adapter.py`

**Problem:**

QC currently checks old columns:

```text
bidPrice
offerPrice
```

Dhan parser/backend chain path uses:

```text
top_bid_price
top_ask_price
bid_ask_spread
```

**Recommendation:**

QC should normalize aliases:

```text
bid = bidPrice or top_bid_price or bid
ask = offerPrice or top_ask_price or ask
```

Then run:

```text
ask < bid => CRITICAL
spread_pct too high => HIGH
missing bid/ask => MEDIUM unless source is bhavcopy/EOD
```

---

### 2.3 `dOI` vs `oi_change` mismatch

**Files:**

- `dashboard/frontend/src/components/OptionChain.tsx`
- `dashboard/backend/chain_adapter.py`
- `dashboard/backend/app.py`

**Problem:**

Frontend expects:

```text
dOI
```

Backend sends:

```text
oi_change
```

**Recommendation:**

Backend should emit both fields:

```json
{
  "oi_change": 123,
  "dOI": 123,
  "change_in_oi": 123
}
```

Frontend should read safely:

```ts
row.oi_change ?? row.dOI ?? row.change_in_oi ?? 0
```

---

### 2.4 Runtime QC gap

**File:** `dashboard/backend/app.py`

`/api/qc` reads output file:

```text
outputs/qc_report_live.json
```

But `/api/chain/{underlying}` may fetch current data through `DataSourceManager`.

**Risk:**

```text
/api/chain = current runtime data
/api/qc = old or missing file-based data
```

**Recommendation:**

Add:

```text
/api/qc/runtime
```

It should validate the same data returned by:

```text
/api/chain/NIFTY
/api/chain/BANKNIFTY
/api/chain/FINNIFTY
/api/chain/MIDCPNIFTY
/api/chain/SENSEX
```

and save proof to:

```text
reports/latest/qc_forensic_anomaly_audit/
```

---

## 3. Anomaly Detection Findings

### 3.1 Existing good anomaly guard

**File:** `core/data/datasource_manager.py`

There is already a useful bhavcopy phantom-price guard. It rejects unrealistic option rows where extrinsic value is too high.

**Status:** Good, but source-limited.

**Recommendation:** Extend similar anomaly checks to:

- Dhan live chain
- NSE live chain
- dashboard API output
- paper candidate gate
- auto snapshot proof

---

### 3.2 Synthetic fallback must not pass readiness

**File:** `core/data/datasource_manager.py`

`DataSourceManager` can create synthetic chain fallback. This is okay for UI/demo, but must not pass trade or readiness QC.

**Hard rule:**

```text
source contains synthetic => qc_passed=false for trade/readiness
```

Dashboard may display it as:

```text
DEMO_ONLY / NOT_TRADEABLE
```

---

### 3.3 Required anomaly matrix

| Category | Check | Severity |
|---|---|---:|
| Source | synthetic/yfinance+synthetic | CRITICAL for trade |
| Freshness | timestamp older than 60s during market open | HIGH |
| Contract count | below threshold per symbol | HIGH |
| Bid/ask | ask < bid | CRITICAL |
| Spread | too wide for too many rows | HIGH |
| LTP | negative / zero-heavy / extreme | CRITICAL/HIGH |
| IV | below 0 or above 300% | HIGH |
| OI | negative / impossible jump / missing | HIGH |
| Volume | zero-heavy during market open | MEDIUM/HIGH |
| ATM coverage | missing CE/PE near spot | HIGH |
| Spot | spot mismatch vs source | HIGH |
| Dashboard contract | frontend-required field missing | HIGH |
| Render | React dist missing / Vue fallback active | HIGH |
| Safety | live trading enabled | CRITICAL |

---

## 4. Dashboard / Frontend / Backend / Render Findings

### 4.1 Two dashboard systems exist

**Legacy Vue:**

```text
dashboard/index.html
dashboard/app.js
dashboard/style.css
```

**React/Vite:**

```text
dashboard/frontend/src/...
dashboard/frontend/dist
```

**Risk:**

Backend may serve React if `dist` exists, otherwise legacy Vue. If React build fails on Render, old Vue can appear.

**Recommendation:**

Set authority:

```text
Authoritative dashboard = React/Vite
Legacy Vue = temporary fallback only
```

After React proof is stable, remove or quarantine Vue fallback.

---

### 4.2 Render fallback risk

**File:** `dashboard/backend/Dockerfile`

React build currently can fail without failing Docker deployment, then fallback to legacy Vue.

**Recommendation:**

After React is declared authority:

```text
React build failure => deployment failure
```

No silent fallback.

---

### 4.3 Hardcoded React gate matrix

**File:** `dashboard/frontend/src/components/Overview.tsx`

Gate values such as `2/7 PASS`, `ρ=0.20`, and expectancy are hardcoded.

**Recommendation:**

All readiness/gate values must come from backend APIs:

- `/api/auto_gates`
- `/api/qc/runtime`
- `/api/state`
- `/api/health`
- `/api/instruments/health`

---

### 4.4 Proof scripts are mixed Vue/React

Some Playwright/audit scripts expect old Vue tab IDs, while React uses different tabs.

**Recommendation:**

Update dashboard proof scripts to target React tabs:

```text
Overview
Trade
Positions
Broker Data
Performance
Alerts
System
Gate Matrix
```

---

## 5. Auto Dashboard Snapshot Plan

### Goal

Generate latest dashboard proof automatically in repo so ChatGPT can inspect from GitHub.

### Folder

```text
reports/latest/dashboard_auto_snap/
```

### Latest files only

```text
latest_dashboard.png
latest_mobile.png
latest_state.json
latest_health.json
latest_qc.json
latest_chain_nifty.json
latest_broker_status.json
latest_instruments_health.json
latest_summary.md
latest_verdict.json
```

### Behavior

```text
Every 1 minute:
1. Open dashboard URL
2. Take desktop screenshot
3. Take mobile screenshot
4. Capture backend API JSON
5. Detect raw Vue tokens
6. Detect React vs Vue served
7. Detect live trading flag
8. Redact secrets
9. Overwrite latest files
10. Git commit/push only reports/latest/dashboard_auto_snap/
```

### Safety

Never commit:

```text
.env
.secrets/
tokens
PIN
TOTP
passwords
broker access token
full private logs
```

Only commit:

```text
reports/latest/dashboard_auto_snap/
```

---

## 6. Recommended Implementation Order

### Phase A — Living MD + proof folders

1. Keep this file updated.
2. Add `reports/latest/dashboard_auto_snap/` proof path.
3. Add `reports/latest/qc_forensic_anomaly_audit/` proof path.

### Phase B — QC fixes

1. Fix `QCValidator` initialization bug.
2. Add Dhan field aliases.
3. Add `dOI/oi_change/change_in_oi` compatibility.
4. Add runtime QC proof endpoint/script.
5. Block synthetic from trade/readiness QC.

### Phase C — Dashboard/Render fixes

1. Declare React as dashboard authority.
2. Make React build failure visible.
3. Remove hardcoded gate values.
4. Align proof scripts to React tabs.
5. Add Render frontend/backend status proof.

### Phase D — Auto snapshot

1. Add `tools/auto_dashboard_repo_snap.py`.
2. Test locally without auto push.
3. Enable auto push only for safe proof folder.
4. Schedule every minute using Windows Task Scheduler.

---

## 7. Manual Work Policy: ChatGPT + User Only

No Codex/Cursor/Claude/Gemini required.

Workflow:

```text
1. ChatGPT inspects repo and prepares exact fix/review.
2. ChatGPT gives one manual command/task.
3. User runs only what ChatGPT cannot run.
4. User pastes output or pushes proof folder.
5. ChatGPT reviews GitHub proof and gives next action.
```

Strict rules:

```text
Analyzer/Paper mode only
No live trading
No real orders
No .env/secrets/tokens touched
No unsafe cleanup
Proof-first changes only
```

---

## 8. Next Recommended File To Add

```text
tools/auto_dashboard_repo_snap.py
```

Purpose:

```text
Capture dashboard screenshots + API JSON every minute and overwrite reports/latest/dashboard_auto_snap/latest_* files.
```

---

## 9. Next Recommended Fix PR Scope

```text
Title: QC forensic anomaly detection and dashboard auto snapshot proof

Scope:
1. Fix QCValidator initialization bug.
2. Add Dhan/QC field aliases.
3. Add dOI/oi_change compatibility.
4. Add runtime QC proof script or endpoint.
5. Add auto dashboard snapshot proof folder/script.
6. Update dashboard proof to React tabs.
7. Do not enable live trading.
8. Do not touch secrets.
```

---

## 10. Latest Status

```text
Document created by ChatGPT as living forensic tracker.
Next action: create auto snapshot script and QC runtime anomaly proof.
```


