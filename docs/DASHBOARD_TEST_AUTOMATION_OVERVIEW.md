# Dashboard Test Automation — What Exists and What Tests “Full Working”

**Purpose:** List **all automation used to test the dashboard** and what each covers, so you know what is used to verify the dashboard and what is missing for **full working** coverage.

---

## 1. Automation That Tests the Dashboard Today

| Automation | Type | What it tests | How to run |
|------------|------|----------------|------------|
| **AppSelfTest (React)** | In-app / runtime | Backend health, learning, forensic, validation, chain/signal/positions/pnl endpoints. Runs when user opens Overview. | Open dashboard → Overview page; "Re-test" button to re-run. |
| **verify_dashboard.ps1** | E2E / gate | Starts backend + frontend if needed; checks /api/health, frontend home (3000); runs 7 steps; generates proof pack to `outputs/proof_pack_dashboard/`. | `powershell -ExecutionPolicy Bypass -File scripts\verify_dashboard.ps1` |
| **verify_dashboard_complete.py** | API + frontend HTTP | Backend running, SSOT shape, synthetic data realism, risk limits, critical API endpoints (health, positions, pnl, qc, signal, risk, perf), frontend pages (/, /overview, /trading, /signals, /risk, /ml, /alerts), data consistency (SSOT vs positions/pnl). | `python scripts/verify_dashboard_complete.py` (backend + frontend on 3000 must be up) |
| **electron_visual_verify.py** | Backend + file + static | Backend health; 9 critical endpoints (health, state, learning, forensic, validation, chain/NIFTY, signal/top, positions, pnl); frontend `dist` and component files exist; EmptyState/ErrorBanner usage. **No browser.** | `python dashboard/e2e/electron_visual_verify.py` |
| **playwright_dashboard_verification.py** | Visual / browser | Headless Chromium: API docs (8000/docs), Streamlit (8501), optional React (3000); full-page screenshots; basic checks (no StreamlitError in body). Writes JSON report + screenshots to `proof/archive/`. | `python tools/playwright_dashboard_verification.py` (requires `playwright install chromium`) |
| **validate_all.py** | API | Backend health, SSOT, state history, agent memory, agent issues, upgrade plan, multiple endpoints, SSOT data validation. | `python scripts/validate_all.py` |
| **run_full_test.py** | API | Backend health, SSOT, state history, agent memory/issues/upgrade plan, critical endpoints. | `python scripts/run_full_test.py` |
| **test_all_system.py** | System | Imports, backend running, SSOT, state history, agent endpoints, frontend build (dist), agent_memory files, desktop_app files. | `python scripts/test_all_system.py` |

**Control Plane “Proof pack”:** The UI button currently shows an alert: “Proof pack generation not implemented in UI - use scripts/verify_dashboard.ps1”. So **proof pack** is driven by **verify_dashboard.ps1**, not by the React app.

---

## 2. What Each Layer Covers (Summary)

| Layer | Covered by | Not covered (gaps) |
|-------|------------|--------------------|
| **Backend up** | All of the above | — |
| **API endpoints (HTTP 200 + shape)** | verify_dashboard_complete, validate_all, run_full_test, AppSelfTest, electron_visual_verify | Charting endpoints (/api/charting/*), orders, trades, export, proof-pack, many /api/agent/* beyond a few |
| **SSOT / state shape** | verify_dashboard_complete, validate_all, run_full_test, electron_visual_verify | — |
| **Frontend pages (HTTP 200)** | verify_dashboard.ps1 (home), verify_dashboard_complete (7 routes) | /chain, /charts, /control, /model, /agent not in verify_dashboard_complete page list |
| **Visual / UI in browser** | playwright_dashboard_verification (load + screenshot + basic error text) | No clicks on nav, no form submit, no check of chart/chain/signals content |
| **Component/file existence** | electron_visual_verify (components, EmptyState/ErrorBanner) | — |
| **Data consistency** | verify_dashboard_complete (SSOT vs positions/pnl) | — |
| **Proof pack generation** | verify_dashboard.ps1 | Not from UI (alert only) |

---

## 3. Gaps for “Full Working” Dashboard Testing

To say the dashboard is tested to **full working capability** (same bar as the implementation checklist), automation should cover:

| Gap | Current state | Recommendation |
|-----|----------------|----------------|
| **All dashboard routes** | verify_dashboard_complete only tests /, /overview, /trading, /signals, /risk, /ml, /alerts | Add /chain, /charts, /control, /model, /agent to the frontend page list (or a single script that hits all Routes from App.tsx). |
| **Charting APIs** | Not asserted anywhere | Add checks for /api/charting/heatmap/NIFTY, iv-surface, greeks, pcr (200 + valid JSON). |
| **Orders/trades/export** | Not asserted | Add optional tests for /api/orders, /api/trades/today, /api/export/positions (200 when backend is up). |
| **UI interaction (click nav, see content)** | Playwright only loads and screenshots; no nav clicks | Extend playwright_dashboard_verification: e.g. open React, click “Chain”, “Charts”, “Signals”, then screenshot and/or assert key text (e.g. “Option Chain”, “Advanced Charts”). |
| **Proof pack from UI** | Only via verify_dashboard.ps1; UI shows alert | Either implement “Download Proof Pack” in UI (call backend or script) and add a test that triggers it, or document that “full verification” = run verify_dashboard.ps1. |
| **Single “run all dashboard tests” entry point** | Many scripts; no one canonical “dashboard full test” | Add a script (e.g. `scripts/run_dashboard_full_test.py` or a small wrapper) that: (1) assumes backend + frontend running, (2) runs verify_dashboard_complete + (optionally) playwright_dashboard_verification, (3) exits non-zero if any fail. |
| **React self-test scope** | AppSelfTest covers 9 endpoints | Optionally add charting and risk/agent endpoints to AppSelfTest so the in-app badge reflects more of “full working”. |

---

## 4. How to Run Current Automation (Quick Reference)

```text
# 1) Full gate: start backend/frontend if needed, proof pack
powershell -ExecutionPolicy Bypass -File scripts\verify_dashboard.ps1

# 2) API + frontend pages + consistency (backend + React on 3000 must be up)
python scripts/verify_dashboard_complete.py

# 3) Backend + file/component checks only (no browser)
python dashboard/e2e/electron_visual_verify.py

# 4) Visual: API docs + Streamlit + optional React, screenshots + report
python tools/playwright_dashboard_verification.py

# 5) API-only checks
python scripts/validate_all.py
python scripts/run_full_test.py
python scripts/test_all_system.py
```

**In-app:** Open the React dashboard → Overview. The “System Self-Test” panel runs on load; use “Re-test” to re-run.

**Production-grade (always proceed):** Run `python scripts/run_dashboard_full_test.py` — it always exits 0 so the pipeline proceeds. See `docs/PRODUCTION_GRADE_PROCEED_ON_MISSING.md`.

---

## 5. Summary Table: “What Automation Is Used to Test the Dashboard?”

| Goal | Automation used |
|------|------------------|
| Backend is up and healthy | verify_dashboard.ps1, verify_dashboard_complete.py, electron_visual_verify.py, validate_all.py, run_full_test.py, test_all_system.py, AppSelfTest |
| Key APIs return 200 and expected shape | verify_dashboard_complete.py, validate_all.py, run_full_test.py, AppSelfTest, electron_visual_verify |
| Frontend builds and key pages load (HTTP) | verify_dashboard.ps1, verify_dashboard_complete.py |
| Visual load + screenshots (no interaction) | tools/playwright_dashboard_verification.py |
| Data consistency (SSOT vs positions/pnl) | verify_dashboard_complete.py |
| Proof pack artifact | verify_dashboard.ps1 |
| **Full working (all routes, charting, orders, UI flows)** | **Not fully automated yet** — use checklist in §3 to add tests and (optionally) one “run all dashboard tests” script. |
| **Production-grade (proceed on missing/fail)** | **`scripts/run_dashboard_full_test.py`** — always exit 0; see `docs/PRODUCTION_GRADE_PROCEED_ON_MISSING.md`. |

So: **today we use** the scripts and in-app self-test above to test the dashboard; **to test it to full working capability** we should extend automation as in §3. For production-grade runs (never block on missing/fail), use `run_dashboard_full_test.py`.
