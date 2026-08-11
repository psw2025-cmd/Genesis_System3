# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 10:51 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `c240ff0c6cb5bd0261ab247ecaf173be5c85e6ac`.
- Compare proof: `b70af343340a73ed27ca548820d5893c779ab5bd..c240ff0c6cb5bd0261ab247ecaf173be5c85e6ac` is **15 commits ahead** and changes only `reports/latest/manual_repo_qc_audit/summary.md`; latest application/source HEAD therefore remains `b70af343340a73ed27ca548820d5893c779ab5bd`.
- PR #97 remains OPEN at head `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main`. Its synthetic-P&L suppression still substitutes zero for unavailable/rejected P&L, so it does not close null/provenance concerns.
- PR #96 remains the newest merged application/UI PR in the current evidence set.
- Exact application-HEAD workflow/runtime proof remains **NOT PROVEN**; the GitHub connector returned no workflow runs and no combined statuses bound to application HEAD `b70af343...` in this iteration.
- Google Cloud Run / Google Cloud services remain the sole deployment authority. Render-era runtime assumptions are migration debt only.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing are prohibited.
- This Markdown remains the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision provenance gate required |
| Dashboard auth/session | **FAIL / P0-P1** | **READY TO PATCH** |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH** via `SafetyTruth` |
| DB/state-store authority | **FAIL / P0-P1** | **READY TO PATCH** via `StateTruth` + domain-CAS |
| WebSocket/REST stream truth | **FAIL / P0-P1** | **READY TO PATCH** via `StreamTruth` |
| Option-chain normalization/cache | **FAIL / P0-P1** | **READY TO PATCH** via `OptionChainTruth` |
| Scanner/ranker freshness + stability | **FAIL / P0-P1** | **READY TO PATCH** via `ScannerTruth` |
| Paper mutation/lifecycle | **FAIL / P0** | **READY TO PATCH** immutable lifecycle |
| Paper P&L/reconciliation | **NOT PROVEN / P0-P1** | after-cost reconciliation required |
| Pre-trade risk authority | **FAIL / P0** | server-owned policy + mandatory risk service |
| Execution guardrail | **FAIL / P0** | fail-closed patch required |
| AI prediction ledger | **MISSING / P0-P1** | **READY TO PATCH/DESIGN** via `PredictionTruth` |
| Model provenance / leakage control | **INCOMPLETE / P0-P1** | **READY TO PATCH** |
| Probability calibration / drift | **NOT PROVEN / P1** | **READY TO PATCH/DESIGN** |
| Responsive/mobile workstation | **FAIL / P1** | **READY TO PATCH** via responsive shell |
| Accessibility/keyboard/focus/live-state semantics | **FAIL / P1** | **READY TO PATCH** via `AccessibleWorkstationShell` |
| Google Cloud deployment provenance | **FAIL / P0-P1** | **READY TO PATCH** via `DeploymentTruth` |
| Observability/runtime error truth | **INCOMPLETE / P1** | **READY TO PATCH/DESIGN** |
| Real-money trade ready | **NO** | locked |

## 2. Mandatory solution-driven audit rule

Every finding must include severity, exact proof, symptom, root cause, real-money impact, exact files/routes, target behavior, minimal safe implementation, ordered implementation steps, API/schema changes, compatibility notes, safety constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior, and implementation state `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing, stale, parse-failed, unauthenticated or unproven evidence must never become green, PASS, zero-risk, zero-P&L, zero-Greek, PAPER SAFE, LIVE, calibrated confidence, model-ready, fresh-market-data, broker-connected, deployed-current or trade-ready through defaults.

## 3. Retained findings registry

- `AUTH-001..004` OPEN: login contract mismatch, pre-auth polling, raw browser API-key storage, incomplete session expiry/revocation proof.
- `UI-001..019` OPEN: false-valid defaults, source inference, empty/error ambiguity, missing authoritative mode/provenance, weak responsive/accessibility and deployment/build truth.
- `CHAIN-001..014` OPEN: warming PCR false-data, weak Dhan proof, incomplete Greeks, null→zero parsing, spread validity, expiry-insensitive cache, weak disk-cache provenance, invented source, generic expiry fallback and parser-error collapse.
- `SCAN-001..010` OPEN: same-day stale rank acceptance, ignored refresh intent, scanner fallback auto-eligibility, hard-coded live provenance, rotating-shard high-watermark retention, stale-row restamping, disk-cache age/session ambiguity, duplicate REST/WS writers, load-heavy equity rotation and UI freshness/eligibility ambiguity.
- `READY-001..009` OPEN: missing safety evidence default-safe paths, semantic lifecycle/risk/economic gates incomplete, weak account-success semantics, Render-era Live Gate copy and evidence-poor human approval.
- `PAPER-001..016`, `TRADE-001..003`, `LEGACY-001` OPEN: default safety/data values, unproven mutation route, direct executor bypass, process-local lifecycle, stale-price handling, incomplete costs/reconciliation and legacy mutation UI residue.
- `RISK-001..009` OPEN: browser-owned limits, permissive defaults, zero-risk fallbacks, weak VaR contract, fail-open guardrail conditions, unproven canonical wiring and proxy gate semantics.
- `WS-001..011` OPEN/UNPROVEN: socket-open≠healthy stream, weak heartbeat truth, REST/WS ordering, stale-value re-stamping, malformed-event silence, stale-last-good semantics, duplicate transport policy, fake WebSocket proof, capped age and route-owner uncertainty.
- `GCP-001..011` OPEN: exact-revision proof missing, immutable digest absent, weak frontend SHA, double service mutation, legacy-key fallback, broad runtime IAM, default service-account fallback, weak typed safety/incident proof and incomplete Render retirement.
- `STATE-001..012` OPEN: file backend default, optional Firestore fallback, stale whole-snapshot overwrite, missing domain revisions/CAS, startup local-file promotion, plausible green defaults, duplicate SSOT methods, position error→empty collapse, weak identity, mixed-generation file sync and missing multi-writer tests.
- `ML-001..014` OPEN: missing immutable prediction ledger, overloaded model-proof boolean, dictionary-first model selection, rank→confidence misuse, ambiguous percentage units, unknown→zero metrics, tracker type bug, unsafe accuracy math, non-atomic tracker persistence, non-purged/non-global time split, incomplete artifact identity, selection/evaluation leakage, missing calibration and no prediction→after-cost linkage.
- `A11Y-001..012` OPEN: fixed shell, clipped truth, inefficient keyboard traversal, non-semantic interactive controls, color-only indicators, weak live-region semantics, very small text, fragile overflow ownership, inconsistent focus, dynamic-state announcement gap, contrast redundancy and missing exact-browser proof.

## 4. Latest deep slice — scanner/ranker contracts, freshness, stability and market-open load

### SCAN-001 / P0-P1 — same-day rank history can be treated as current without intraday freshness proof

**Exact proof:** `dashboard/backend/app.py:get_gain_rank()` loads `state/gain_rank_history.json`, selects the newest entry whose `date` equals today and sets `stale` only from date equality. It does not require `generated_utc`, source-event age, scanner cycle ID, market session or TTL before returning `status=ok`.

**Symptom/root cause:** a ranking produced earlier in the same trading day can remain authoritative for hours solely because its calendar date equals today.

**Real-money impact:** stale contracts can be presented as current opportunities even after price, liquidity, IV, expiry relevance or market leadership changed.

**Exact files/routes:** `dashboard/backend/app.py`, `/api/gain_rank`, gain-rank persistence producer, frontend `useData.ts`, `TradeTab.tsx`.

**Target behavior:** every rank payload is one immutable `ScannerSnapshot` with `snapshot_id`, source-event range, generated/received times, market session, age, TTL, universe ID and schema/rank-policy version. A current-day row whose TTL expired is `STALE`, never current.

**Minimal safe implementation:** reject or watermark stored rank history unless snapshot age and session identity validate. Historical rows remain available only through history/audit views.

**API/schema changes:** add `snapshot_id`, `generated_at`, `source_event_max_at`, `age_ms`, `ttl_ms`, `market_session_id`, `quality`, `rank_policy_version` and per-row evidence IDs.

**Regression risks:** dashboards becoming empty when no fresh scan is available; migration of old history records without timestamp metadata.

**Closure tests/PASS:** create a same-date fixture older than TTL and prove `/api/gain_rank` returns `STALE` and zero execution-eligible rows; verify fresh fixture returns current; verify market-session rollover invalidates yesterday/same-date test fixtures where session IDs disagree.

**Rollback/fail-safe:** stale historical data may remain visible with watermark for analysis, but scanner candidate eligibility is inhibited.

**Status:** `READY TO PATCH`.

### SCAN-002 / P1 — `/api/gain_rank?refresh=true` declares refresh intent but does not use it

**Exact proof:** `get_gain_rank(refresh: bool=False)` defines the query parameter, but the current function body does not branch on `refresh`; live fallback occurs only when the stored latest entry is stale/missing by the weak date rule.

**Symptom/root cause:** operator/client refresh intent is semantically misleading and may leave a same-day stale ranking unchanged.

**Real-money impact:** a visible refresh control/caller can imply the board was recomputed when no recomputation occurred.

**Solution:** either remove the parameter or make `refresh=true` enqueue/request a server-authoritative scan that returns a new `snapshot_id`; never block the event loop for an uncontrolled full scan. Return `202/PENDING` when a new scan is in progress rather than silently serving old data as refreshed.

**Tests/PASS:** stale same-day snapshot + `refresh=true` must yield a different snapshot ID or explicit `PENDING/FAILED`, never unchanged data labeled current.

**Status:** `READY TO PATCH`.

### SCAN-003 / P0-P1 — scanner fallback automatically marks rows option-eligible without liquidity/risk/evidence validation

**Exact proof:** both backend live fallback in `get_gain_rank()` and frontend WebSocket `market_top_update` mapping set `option_eligible: true` and `recommendation: 'WATCH'` for rows derived from top gain percentage. No spread, quote completeness, source age, expiry validity, contract identity, risk decision or prediction evidence is required at this point.

**Symptom/root cause:** ranking and eligibility are conflated. Being in a gainers table is treated as sufficient to mark an option contract eligible.

**Real-money impact:** a high-gain but illiquid, crossed, stale, wrong-expiry or otherwise invalid contract can appear operationally actionable.

**Solution:** `ranked` and `eligible` become independent typed states. Scanner produces `WATCH` candidates only. `eligible=true` may be set only by `CandidateValidationService` after `OptionChainTruth`, liquidity policy, `PredictionTruth` if required, and `PreTradeRiskService` evidence are present.

**Regression risks:** fewer green/eligible rows until validation services are wired; downstream code assuming boolean eligibility.

**Closure tests/PASS:** missing bid/ask, stale event age, unknown expiry, missing risk decision and incomplete quote must each force `WATCH/INELIGIBLE`; only an exact validated candidate may become paper-eligible.

**Status:** `READY TO PATCH`.

### SCAN-004 / P1 — contract rows hard-code live Dhan provenance independently of chain truth

**Exact proof:** `contract_gain_scanner.py:_contract_row()` assigns `data_provenance='DHAN_OPTION_CHAIN_LIVE'` and a `LIVE DHAN GAINER` note for every scored row, while source chain quality/status/freshness is handled separately at segment level. `get_gain_rank()` also falls back to `DHAN_OPTION_CHAIN_LIVE` when row provenance is absent.

**Symptom/root cause:** row provenance is manufactured by the ranking layer instead of inherited from a validated acquisition envelope.

**Real-money impact:** cached/EOD/stale or otherwise unproven chain rows can receive live-sounding provenance and appear fresher than the source evidence supports.

**Solution:** scanner rows may only reference a `chain_truth_id`/provider event ID. Provenance, session and freshness are copied from the authoritative `OptionChainTruth`; ranking code cannot invent them.

**Tests/PASS:** stale/EOD/cache chain input must produce corresponding stale/snapshot row quality and can never serialize `DHAN_OPTION_CHAIN_LIVE` unless the input truth was validated live.

**Status:** `READY TO PATCH`.

### SCAN-005 / P0-P1 — rotating-shard merge is a high-watermark algorithm that can retain obsolete gains

**Exact proof:** `contract_gain_scanner.py:merge_market_top_reports()` merges old and incoming rows by contract key and keeps the new row only when `incoming.gain_pct >= previous.gain_pct`. If the same contract's gain falls from e.g. 40% to 12%, the older 40% row remains. Contracts absent from the incoming shard are also retained.

**Symptom/root cause:** the board is a historical maximum-gain memory, not a current market snapshot.

**Real-money impact:** old winners can dominate current rankings after their gain collapses, creating false opportunity ordering and contaminating scanner→prediction/paper evidence.

**Solution:** never merge current market rank by historical maximum. Maintain a latest-observation map keyed by canonical contract identity with per-row event time/revision. Replace a contract row whenever a newer valid observation arrives, even if gain is lower; evict rows outside TTL/session/universe generation. Historical maxima belong in a separate analytics view.

**Regression risks:** visible rank volatility will increase because the board becomes truthful instead of sticky; consumers expecting monotonic gains may break.

**Closure tests/PASS:** old 40% row followed by newer 12% row must show 12%; absent rows older than TTL must disappear; out-of-order older observations must be rejected; ties use deterministic policy.

**Status:** `READY TO PATCH`.

### SCAN-006 / P0-P1 — merge re-stamps retained stale rows with the incoming refresh time

**Exact proof:** after combining rows, `merge_market_top_reports()` chooses one report-level `refreshed_at` and `_rank_table()` writes that same timestamp onto every row, including rows retained from the older base shard.

**Symptom/root cause:** row event time is discarded and replaced by board-generation time.

**Real-money impact:** an obsolete retained contract can look freshly observed even though it was not present in the newest shard/cycle.

**Solution:** preserve immutable `source_event_at` and `observed_at` per row; add separate `snapshot_generated_at` at board level. UI shows row age, not only board age. Retained rows beyond TTL are evicted instead of restamped.

**Tests/PASS:** merging a 5-minute-old base row with a new shard must keep the old row's original event time or evict it; no operation may advance `source_event_at` without a new provider observation.

**Status:** `READY TO PATCH`.

### SCAN-007 / P0-P1 — scanner disk state can be returned without explicit age/session validation

**Exact proof:** `/api/scanner/top_contract_gainers` checks `_MARKET_TOP_STATE_FILE`; if `contracts_scored_total > 0`, it caches and returns the disk object. In the inspected path there is no mandatory validation of source-event age, market session, universe generation, rank policy/schema version or exact application/runtime revision before promotion.

**Symptom/root cause:** persisted scanner state is treated as reusable current data based mainly on being non-empty.

**Real-money impact:** restart/failover can resurrect a prior market snapshot and present it as current.

**Solution:** persist a typed `ScannerSnapshotEnvelope`; startup/read path validates session, TTL, source age, schema/rank-policy versions and revision compatibility. Invalid persisted state becomes `STALE_LAST_GOOD` and cannot populate current opportunity state.

**Tests/PASS:** previous-session disk snapshot, malformed timestamp and incompatible schema must each be rejected from current board.

**Status:** `READY TO PATCH`.

### SCAN-008 / P1 — REST polling and WebSocket independently write the same scanner stores without snapshot ordering

**Exact proof:** `useData.ts` receives `gain_rank` through `/api/batch/market-data` and writes `setGainRank()`, while `market_top_update` WebSocket events independently rebuild and overwrite the same rank state. `MarketTopCePeTable.tsx` also polls `/api/scanner/top_contract_gainers` every 15 seconds and writes `setMarketTop()` while WS can write that store concurrently. No snapshot sequence/revision comparison is performed before writes.

**Symptom/root cause:** multiple transport writers race on shared client state.

**Real-money impact:** a slower REST response can overwrite a newer WS snapshot, rank rows can jump backward in time, and source badges can disagree with actual data generation.

**Solution:** one store reducer accepts `ScannerSnapshotEnvelope` and compares `snapshot_revision/source_event_at`. REST becomes fallback only; older/equal snapshots are rejected and counted. MarketTop and GainRank derive from the same canonical snapshot rather than separate writer paths.

**Tests/PASS:** inject WS revision 12 then REST revision 11 and prove revision 11 is rejected; verify duplicate equal revision is idempotent; reconnect fallback cannot decrease revision.

**Status:** `READY TO PATCH`.

### SCAN-009 / P1 — market-open equity rotation is intentionally expensive and can create timeout/thread pressure

**Exact proof:** `fetch_chains_for_market()` scans indices in a `ThreadPoolExecutor`, then serially sleeps ~3.15 seconds between each equity chain because of Dhan rate limiting. Default equity scan limit is 16, so equity enrichment alone can consume roughly 50 seconds before provider/network time. Request path timeouts and background rotations can therefore overlap under load. The app separately documents thread-pileup risk in another background path, confirming thread timeout behavior is already a known system concern.

**Symptom/root cause:** synchronous provider work, sleep-based pacing and request-triggered scanning are mixed with a real-time web API.

**Real-money impact:** scanner latency, Cloud Run concurrency pressure and timed-out background threads can degrade unrelated APIs, making old scanner data remain visible while new work is delayed.

**Solution:** move Dhan scanner acquisition into one bounded scheduler/worker with token-bucket rate limiting, per-symbol deduplication, bounded concurrency and cycle deadlines. HTTP/WS only read validated snapshots; they never start expensive scans. Expose queue depth, active workers, cycle duration, timeout count and last completed cycle ID.

**Regression risks:** worker/scheduler availability becomes explicit dependency; initial snapshot may be unavailable rather than synchronously computed.

**Closure tests/PASS:** load test market-open request rate while scanner worker rotates full target universe; p95 API latency stays within policy, worker count bounded, no unbounded thread growth, every cycle has one ID and deadline, stale snapshot ages visibly instead of being restamped.

**Status:** `READY TO PATCH/DESIGN`.

### SCAN-010 / P1 — product UI presents rank/freshness/eligibility with misleading fallbacks

**Exact proof:** `TradeTab.tsx` labels `GAIN %` using `row.gain_pct ?? row.gain_rank ?? 0`, so a rank-like field can still become percentage display. Missing OI/LTP in equity rows becomes zero. Equity status renders `${liveOk} live` when positive but otherwise the ambiguous `EOD/live`. `MarketTopCePeTable.tsx` describes Dhan HTTP fallback as `Dhan live · trading truth for paper MTM`, defaults missing row provenance to `DHAN_OPTION_CHAIN_LIVE`, and converts missing LTP/gain/volume/OI to numeric zero.

**Symptom/root cause:** the UI tries to remain visually complete even when source/age/numeric evidence is incomplete.

**Real-money impact:** unknown data can look live, eligible and numerically valid; operators cannot distinguish current scanner evidence from fallback/cached/no-data states.

**Solution:** scanner table columns must include `Snapshot`, `Event age`, `Source`, `Quote quality`, `Evidence`, and typed `Eligibility`. Null remains `—/UNKNOWN`; Dhan live label requires validated live source+TTL; EOD is explicitly `EOD SNAPSHOT`; fallback rank never substitutes for gain percent.

**Tests/PASS:** frontend fixtures for null fields, stale rows, EOD rows, REST fallback, WS current, crossed quote and missing evidence; no fixture may render invented zero/live/eligible labels.

**Status:** `READY TO PATCH`.

## 5. Prior deep slice — responsive, accessibility, keyboard and constrained-layout workstation behavior

### A11Y-001 / P1 — application shell is fixed-height/fixed-sidebar and has no responsive layout authority

**Exact proof:** `dashboard/frontend/src/App.tsx` uses a `100vh` flex column, a permanently rendered `Sidebar`, and a main region with `overflow:'hidden'`. `Sidebar.tsx` fixes navigation width to `190px` with 22 tab buttons. There is no breakpoint/drawer logic in these files.

**Symptom/root cause:** the desktop shell is treated as universal. A small viewport must fit a fixed sidebar plus workstation content instead of intentionally switching information architecture.

**Real-money impact:** critical status, risk, broker/data and order-safety controls can be clipped or forced below usable widths; an operator on tablet/mobile can miss authoritative warnings or select the wrong workspace.

**Exact files:** `dashboard/frontend/src/App.tsx`, `dashboard/frontend/src/components/Sidebar.tsx`, new responsive shell/layout primitives, relevant workspace tables.

**Target behavior:** desktop ≥1280px uses persistent navigation; tablet uses compact rail; mobile uses modal/drawer navigation and bottom quick-actions. Critical truth strip remains visible; secondary telemetry moves into drilldowns.

**Minimal safe implementation:** introduce `useViewportClass()` + CSS container/breakpoint tokens and a single `WorkstationShell`. Sidebar becomes `desktop | compact | drawer`; content regions receive explicit scroll ownership.

**Regression risks:** hiding controls at breakpoints, trapping focus in drawer, duplicate navigation state, content remount/data refetch.

**Closure tests/PASS:** Playwright viewport matrix 360×800, 390×844, 768×1024, 1024×768, 1366×768, 1920×1080; no clipped safety controls; all tabs reachable; no horizontal page scroll except deliberate data-table scrollers; active workspace survives orientation/layout change.

**Fail-safe:** when viewport rules fail, show a safe reduced control surface with live router still locked and truth/status visible.

**Status:** `READY TO PATCH`.

### A11Y-002 / P1 — TopBar hides overflow instead of prioritizing/reflowing critical controls

**Proof:** `TopBar.tsx` header sets `overflow:'hidden'`; index chips occupy a flex region also with `overflow:'hidden'`; owner identity, Cloud Build badge, clock, NIFTY/BANKNIFTY/FINNIFTY, sync age, market, Dhan, PAPER, LIVE OFF, WS and rho all compete for one fixed 56px row.

**Impact:** constrained width can silently remove market/broker/live/WS truth from view.

**Solution:** priority-tier header: Tier 0 always-visible safety (`MODE`, `LIVE LOCK`, market/session, broker/data age); Tier 1 index watch becomes horizontally scrollable; Tier 2 owner/build/rho moves to overflow/command panel. Never clip Tier 0.

**Tests:** screenshot/assert visibility at all supported widths; no Tier-0 element may have zero intersection with viewport.

**Status:** `READY TO PATCH`.

### A11Y-003 / P1 — navigation is technically button-based but not optimized for 22-tab keyboard operation

**Proof:** `Sidebar.tsx` renders every tab as a normal button, so keyboard users must traverse the entire 22-item sequence. There is no roving focus, group-level arrow navigation, workspace search or command palette.

**Impact:** slow navigation under incident/market pressure increases operator error and makes the workstation inefficient for keyboard-first use.

**Solution:** keep native buttons, add roving `tabIndex` within grouped navigation, Up/Down/Home/End movement, Left/Right group movement where appropriate, `Ctrl/Cmd+K` workspace command palette, and skip-to-content link. Preserve `aria-current=page`.

**Tests:** keyboard-only traversal of every workspace, focus order snapshot, no keyboard trap, command palette searchable by current and rationalized tab names.

**Status:** `READY TO PATCH`.

### A11Y-004 / P1 — broker TopBar navigation control is a clickable `span`, not an accessible control

**Proof:** `TopBar.tsx` uses `<span onClick={() => setActiveTab('broker')}>` with `cursor:'pointer'` for the Dhan broker status chip; it has no button role, no tab focus, and no Enter/Space behavior.

**Impact:** keyboard and assistive-technology operators cannot reliably activate a critical broker-health drilldown.

**Solution:** replace with native `<button type="button">`; preserve visual styling, add descriptive accessible name including broker quality, and maintain visible focus.

**Tests:** Tab reaches broker chip; Enter and Space open Broker workspace; axe has no interactive-role violation.

**Status:** `READY TO PATCH`.

### A11Y-005 / P1 — broker status in Sidebar has a color-only indicator

**Proof:** the Broker navigation item adds an unlabeled 7px colored dot based on `brokerConnected`; the button's text remains only `Broker`.

**Impact:** color-vision deficiency or screen-reader users do not receive the broker state represented by the dot.

**Solution:** decorative dot gets `aria-hidden=true`; accessible button name/description includes typed state (`Broker — connected`, `Broker — unknown`, etc.) sourced from broker truth, and visible text/badge uses words/icons as well as color.

**Status:** `READY TO PATCH`.

### A11Y-006 / P1 — login error/loading/status feedback lacks live-region semantics

**Proof:** `LoginPage.tsx` renders errors in a plain `<div>` with no `role="alert"`/`aria-live`; `AuthGate` loading text similarly has no status role. The login label has no `htmlFor`/input `id` relationship.

**Impact:** assistive technology may not announce authentication failure or loading changes; the field label association is weaker than required for a professional security surface.

**Solution:** `role="status" aria-live="polite"` for loading; `role="alert" aria-live="assertive"` for auth failures; explicit `label htmlFor`, input `id/name`, `aria-describedby`; use appropriate autocomplete policy and never expose the raw key after authentication.

**Security constraint:** this accessibility patch must align with `SOL-01`; the raw API key must be removed from `sessionStorage`, not made easier to persist.

**Status:** `READY TO PATCH`.

### A11Y-007 / P1-P2 — critical telemetry uses very small text sizes

**Proof:** `TopBar.tsx` and `Sidebar.tsx` use repeated `.45rem`, `.5rem`, `.52rem`, `.55rem`, `.6rem`, `9px`, and `10px` text for build identity, labels and status badges.

**Impact:** dense workstation information can become unreadable on high-DPI laptops/tablets and for low-vision users; status interpretation slows under pressure.

**Solution:** define minimum semantic type tokens: critical status ≥12px equivalent, secondary telemetry ≥11px, interactive labels ≥12px; support browser zoom 200% without loss of controls; use truncation only with accessible full text.

**Tests:** WCAG reflow at 200% zoom and 320 CSS px equivalent; no safety label clipped or hidden.

**Status:** `READY TO PATCH`.

### A11Y-008 / P1 — scroll ownership is fragile because body and main are both overflow-hidden

**Proof:** `index.css` sets `html, body { overflow:hidden }`; `App.tsx` also sets main `overflow:'hidden'`. Therefore every workspace must independently implement scrolling correctly or content becomes unreachable.

**Impact:** long tables, dialogs or error panels can become inaccessible, especially after zoom or on short-height screens.

**Solution:** one explicit shell scroll contract: app body stays fixed only if the active workspace root has guaranteed `overflow:auto`; use reusable `WorkspaceViewport` and `DataScroller`. Dialogs portal to body with their own scroll/focus lock.

**Tests:** automated content-height stress tests, 200% zoom, 600px viewport height and long-table fixtures; last interactive row/control remains reachable.

**Status:** `READY TO PATCH`.

### A11Y-009 / P1 — no consistent visible-focus design for workstation controls

**Proof:** `index.css` defines a custom focus border only for `select`; navigation and inline-styled critical controls do not use a shared `:focus-visible` token. Browser defaults may remain, but there is no product-level proof of consistent high-contrast focus.

**Impact:** keyboard operators can lose track of active control in a dense dark UI.

**Solution:** global `:focus-visible` ring token with ≥2px visible contrast, offset and no color-only ambiguity; native semantics first; modal focus trap/restoration standardized.

**Tests:** automated focus-outline snapshots across every interactive component and theme; no element with `outline:none` unless replaced by equal/stronger focus indicator.

**Status:** `READY TO PATCH`.

### A11Y-010 / P1 — dynamic market/broker/WS safety-state changes are not exposed through controlled live regions

**Proof:** TopBar updates market status, broker state, WS state and tick age visually but does not expose an accessibility announcement channel. ProductionProofBar has an `aria-label` but no `aria-live` state-change strategy.

**Impact:** a screen-reader user can remain unaware that market/data/broker state degraded or live-lock/readiness changed.

**Solution:** create a deduplicated `CriticalStatusAnnouncer` that announces only meaningful transitions (`HEALTHY→STALE`, `CONNECTED→ERROR`, `PAPER→UNKNOWN`, risk inhibit), not every market tick. Use `aria-live=polite`, escalating safety failures to assertive only when operator action is required.

**Tests:** transition-driven screen-reader DOM assertions; no announcement spam from per-second clock/tick updates.

**Status:** `READY TO PATCH`.

### A11Y-011 / P1 — status color semantics need text/icon redundancy and contrast proof

**Proof:** green/amber/red are heavily used for market, broker, WS, proof and sidebar states. Some controls contain text, but several micro-indicators and small labels rely strongly on hue.

**Solution:** every safety/data state includes icon + explicit word (`HEALTHY`, `STALE`, `UNKNOWN`, `ERROR`, `LOCKED`) and meets contrast targets. Do not encode direction/safety solely by red/green.

**Tests:** axe contrast checks plus monochrome/color-blind visual regression snapshots.

**Status:** `READY TO PATCH`.

### A11Y-012 / P1 — actual browser accessibility/runtime proof is absent

**Proof:** this iteration could statically inspect source but no exact-application-head browser/Playwright/axe workflow run exists in the current evidence set.

**Impact:** keyboard/focus/reflow/ARIA claims cannot be closed from code inspection alone.

**Solution:** add exact-revision `ui-accessibility-proof` workflow: build frontend, launch analyzer/paper backend with non-live fixtures, run Playwright + axe on every workspace at desktop/tablet/mobile/200%-zoom, capture console errors/screenshots/accessibility violations and bind artifact to source SHA.

**PASS criteria:** zero critical/serious axe violations; zero console runtime errors; all required workspaces keyboard reachable; no critical status clipped; modal focus restore works; live router remains locked.

**Status:** `READY TO PATCH/DESIGN`.

## 6. Positive foundations in the recent slices

- Sidebar uses native `<button>` elements for tabs, has `aria-label`, `aria-current`, and a named `<nav>` landmark.
- `ProductionProofBar` has an accessible label and explicit text values in addition to colors.
- `index.css` already honors `prefers-reduced-motion: reduce`; preserve this.
- Login uses a native `<form>`, password input and submit button.
- App contains a semantic `<main>` element.
- Scanner request code already caps query sizes, has bounded endpoint timeouts, separates index-first request scanning from slower equity enrichment, and documents provider pacing. These are useful foundations but are not sufficient without snapshot/freshness/order truth.

## 7. Canonical truth contracts

### 7.1 `SafetyTruth`
Mode, nullable live/auto flags, router/kill-switch state, source/runtime/image/policy revisions, verified time/age, `PROVEN|STALE|UNKNOWN|ERROR`.

### 7.2 `DataTruthEnvelope` / `StreamTruth`
Source/session/instrument, source/backend/frontend timestamps, uncapped age/TTL, schema/normalizer versions, transport vs heartbeat vs stream state, sequence/rejected-old events, quality and evidence.

### 7.3 `OptionChainTruth`
Underlying/security ID/segment, requested+resolved expiry authority, provider/session, times/age/TTL, expiry-aware cache identity, schema/normalizer versions, nullable quote/Greek fields + field quality, completeness, source/runtime revision and evidence ID.

### 7.4 `DeploymentTruth`
Exact source/tree SHA, Cloud Build ID, immutable image digest, final Cloud Run revision/traffic, frontend/backend SHA, runtime app/service account, policy/config hash, secret/scheduler provenance, verified time and evidence ID.

### 7.5 `StateTruth`
Required shared backend, collection/document, shared-state health, runtime/instance ID, last shared read/write, per-domain revision/writer/event/time/schema/quality/evidence. Global version is diagnostic only.

### 7.6 `PredictionTruth`
`prediction_id`, immutable issue time, target/horizon, instrument key, model artifact ID/hash, dataset/feature schema hash, frozen data cutoff, raw score, calibrated probability, uncertainty, evidence/counter-evidence, input truth IDs, runtime/source revision, maturity rule/state, later append-only outcome/calibration links.

### 7.7 `AccessibleWorkstationState`
Viewport class, navigation mode, focused workspace/control ID, modal/drawer state, critical-status announcement queue and density preference. This state is **non-authoritative for trading**; it must never affect risk/safety truth or live routing.

### 7.8 `ScannerTruth` — NEW
`snapshot_id`, scanner cycle ID, market session ID, universe/universe-generation ID, source-event min/max times, generated/received times, uncapped age+TTL, schema/rank-policy version, canonical contract identity, per-row event time/revision/source/quote quality, rank score/gain metric with explicit units, stable tie-break rule, row evidence ID, candidate-validation state, dropped-stale/out-of-order counters, worker/load diagnostics and exact runtime/source revision. A row belongs to exactly one current snapshot; old-shard observations are never restamped as fresh.

## 8. Canonical remediation roadmap

- `SOL-01 Auth/session — READY TO PATCH`: correct login body; cookie-only auth; remove raw API key; auth-gate polling/WS; TTL/revocation tests.
- `SOL-02 SafetyTruth — READY TO PATCH`: one backend authority; missing/stale => UNKNOWN.
- `SOL-03 DataTruthEnvelope — READY TO PATCH`: remove production zero/plausible defaults.
- `SOL-04 Semantic readiness — READY TO PATCH`: HTTP/object presence never PASS; lifecycle/reconciliation/risk/economics mandatory.
- `SOL-05 OptionChainTruth + Greeks — READY TO PATCH`: nullable parser, expiry-aware cache, explicit provenance/IV units/full Greeks.
- `SOL-06 Immutable paper lifecycle — READY TO PATCH`: durable event ledger, IDs/idempotency, restart replay/reconciliation, costed P&L.
- `SOL-07 ScannerTruth — READY TO PATCH`: replace high-watermark shard merge with latest-observation snapshots; per-row event age; current-session TTL; deterministic rank policy; rank/score/probability/forecast distinct; scanner outputs WATCH candidates only; canonical REST/WS ordering.
- `SOL-08 DeploymentTruth + GCP least privilege — READY TO PATCH`: immutable digest/final revision/source SHA, one service mutation, dedicated identities, WIF-only auth.
- `SOL-09 PreTradeRiskService — READY TO PATCH`: server-owned policy; fresh PASS required; UNKNOWN/ERROR denies.
- `SOL-10 Legacy UI quarantine — READY TO PATCH`: production entrypoint guard; no legacy mutation surface.
- `SOL-11 StreamTruth — READY TO PATCH`: transport != healthy stream; heartbeat schema; ordered REST/WS merge; uncapped age; true WS proof.
- `SOL-12 RuntimeEventEnvelope — READY TO PATCH/DESIGN`: incidents/logs bound to source SHA + digest + Cloud Run revision.
- `SOL-13 StateTruth + domain-CAS — READY TO PATCH`: Firestore required in GCP; sparse domain writes; no local authority fallback; restart/multi-writer proof.
- `SOL-14 PredictionTruth + ModelArtifactManifest — READY TO PATCH/DESIGN`: immutable prediction ledger, exact model/data identity, purged walk-forward, untouched holdout, calibrated probability, drift monitoring and after-cost outcome linkage.
- `SOL-15 AccessibleWorkstationShell — READY TO PATCH`: responsive shell, tiered truth header, drawer/compact navigation, command palette, keyboard model, focus-visible, live regions, table reflow and exact-revision Playwright/axe proof.
- `SOL-16 Scanner worker/load isolation — READY TO PATCH/DESIGN`: one bounded provider worker, token-bucket Dhan pacing, cycle IDs/deadlines, deduplicated symbol work, no request-triggered full scanner work, bounded thread/concurrency metrics and load proof.

### SOL-07 ordered implementation

1. Introduce `ScannerSnapshotEnvelope` + canonical contract identity.
2. Preserve provider/source event time on every row; separate snapshot-generation time.
3. Replace high-watermark merge with newer-observation replacement regardless of gain direction.
4. Evict TTL-expired, wrong-session, wrong-universe-generation and incompatible-schema rows.
5. Remove scanner-layer hard-coded live provenance; require `OptionChainTruth` reference.
6. Make scanner result state `WATCH` by default; separate `CandidateValidationService` owns paper eligibility.
7. Make `/api/gain_rank` validate snapshot age/session and either remove or correctly implement refresh semantics.
8. Route REST + WS through one revision-aware frontend reducer; reject older snapshots.
9. Replace null→zero and rank→gain UI fallbacks with typed unknown states.
10. Add event-age/source/evidence/eligibility columns and snapshot drilldown.
11. Add deterministic tie-break policy and rank-movement audit.
12. Run unit, integration, out-of-order, restart, market-session-rollover and browser tests.

**SOL-07 PASS criteria:** a newer lower gain always replaces an older higher gain for the same contract; expired/absent shard rows are evicted; no row freshness timestamp advances without a new provider observation; stale disk state never becomes current; rank/gain/probability cannot substitute for each other; scanner rows remain WATCH until independent validation; older REST/WS snapshots are rejected; UI displays age/source/evidence without invented zero/live labels.

### SOL-15 ordered implementation

1. Add viewport/layout tokens and `WorkstationShell` with explicit desktop/tablet/mobile modes.
2. Refactor Sidebar to persistent/compact/drawer modes with one source of active-tab truth.
3. Refactor TopBar into Tier-0 safety truth, Tier-1 market watch and Tier-2 overflow telemetry; never hide Tier-0.
4. Replace clickable non-semantic spans with native controls.
5. Add skip link, roving navigation keys and `Ctrl/Cmd+K` command palette.
6. Add shared `:focus-visible` design token and modal/drawer focus trap + restore.
7. Add `CriticalStatusAnnouncer` with transition deduplication; never announce per-tick noise.
8. Raise minimum type/touch-target sizing and preserve reduced-motion support.
9. Add reusable `WorkspaceViewport`, `DataScroller`, sticky table headers and mobile column-priority/card views.
10. Add explicit loading/empty/error/auth/market-closed/stale states with semantic roles.
11. Run Playwright + axe across all existing repo tabs, breakpoints, 200% zoom and keyboard-only scenarios.
12. Bind proof artifacts to exact source SHA/runtime revision; no PASS from static inspection alone.

**SOL-15 PASS criteria:** all current navigation destinations are reachable by keyboard and mobile; no Tier-0 safety truth is clipped; no dead/non-semantic interactive element remains; visible focus is consistent; critical state transitions are announced without spam; 200% zoom/reflow works; zero critical/serious axe violations and zero browser console runtime errors on the exact revision.

**Rollback/fail-safe:** if responsive/accessibility shell fails, render a reduced read-only layout with SafetyTruth/DataTruth visible and all trading mutation/live controls inhibited.

## 9. Verification counters

Independent reproduction paths only.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `3/20` | OPEN |
| AUTH-002 | `2/20` | OPEN |
| AUTH-003 | `2/20` | OPEN |
| UI-001 | `16/20` | OPEN |
| UI-002 | `5/20` | OPEN — scanner rank/gain fallback is another metric-semantics path |
| UI-003 | `8/20` | OPEN |
| UI-005 | `15/20` | OPEN — scanner live provenance/zero defaults add another false-valid path |
| UI-006 | `9/20` | OPEN |
| UI-007 | `11/20` | OPEN — scanner row age/source and REST/WS ordering add independent staleness paths |
| UI-009 | `6/20` | OPEN |
| UI-011 | `4/20` | OPEN |
| UI-016 | `10/20` | OPEN |
| UI-018 | `2/20` | OPEN |
| CHAIN-001..014 | retained previous counters | OPEN |
| SCAN-001..010 | `1/20` each | OPEN |
| READY-001 | `5/20` | OPEN |
| READY-003 | `3/20` | OPEN |
| READY-008 | `2/20` | OPEN |
| PAPER-001..016 | retained previous counters | OPEN |
| RISK-001..009 | `1/20` each | OPEN |
| WS-001..010 | `1/20` each | OPEN |
| WS-011 | `1/20` | UNPROVEN |
| GCP-001..011 | `1/20` each | OPEN |
| STATE-001..012 | `1/20` each | OPEN |
| ML-001..014 | `1/20` each | OPEN |
| A11Y-001..012 | `1/20` each | OPEN |

No finding is `LOCKED-20X`.

## 10. Prioritized implementation order

### P0 Wave 1 — eliminate false-green/fail-open authorities
1. SOL-01 auth contract + auth-gated startup.
2. SOL-02 authoritative `SafetyTruth`.
3. SOL-08 exact `DeploymentTruth` baseline.
4. SOL-13 shared `StateTruth` authority + domain-CAS.
5. SOL-05 OptionChainTruth null/cache/expiry correction.
6. SOL-11 StreamTruth and ordered REST/WS merge.
7. **SOL-07 ScannerTruth current-snapshot/high-watermark correction.**
8. SOL-09 server-owned risk + mandatory pre-trade authority.
9. SOL-06 durable lifecycle/idempotency/reconciliation.
10. SOL-14 model maturity split + score/confidence correction + immutable PredictionTruth foundation.
11. SOL-04 semantic readiness.
12. SOL-03 remaining zero/live/default-safe fallbacks.
13. SOL-10 legacy mutation UI quarantine.

### P1 Wave 2 — operator safety + statistical/economic proof
1. **SOL-16 scanner worker/load isolation and market-open load proof.**
2. SOL-15 responsive/accessibility shell and exact-revision browser proof.
3. Purged walk-forward + untouched holdout, calibration, drift, model/data hashes.
4. Prediction→paper→after-cost outcome linkage.
5. Full Greeks/model provenance and true WebSocket proof.
6. GCP IAM split/WIF-only auth and revision-bound runtime incidents.

### P2 Wave 3 — institutional operator quality
Advanced command palette/search, customizable density, saved workspace layouts, richer drilldowns, security/session settings and audit export. These remain secondary to truth/safety.

## 11. Product information architecture target

1. Command Center — Overview + Decision Intel + authoritative truth strip.
2. Market / Scanner — watch, scanner, ranker, signals, snapshot history/rank movement and candidate drilldown.
3. Options & Greeks — chain, expiry/cache/provenance, IV/OI/liquidity/full Greeks.
4. AI Decision Audit — Genesis Brain + Prediction Audit + model provenance + calibration/drift + evidence/outcome linkage.
5. Paper / Trade Lifecycle — capability-driven ticket, immutable orders/fills/positions/P&L/reconciliation.
6. Portfolio & Risk — server-owned policy, exposure, aggregate Greeks, scenarios.
7. Data & Broker Health — state authority, domain revisions, transport/heartbeat/source/freshness/account/cache truth.
8. Readiness / Proof — semantic E2E gates + Live Gate.
9. Observability — deployment identity, incidents, logs, schema/parse errors, latency/reconnects and revision-bound evidence.
10. Security / Settings — sessions, IAM/policies, permissions, audit export and non-authoritative preferences.

Current repo tabs remain represented through this rationalized hierarchy; conceptual renames never imply implemented capability.

## 12. Product UI visual evolution — V14

New concept: **Scanner & Ranker Truth V14** — actual System3 `Market / Scanner` product workspace.

Changes driven by this iteration:
- scanner board is explicitly one immutable current snapshot rather than rolling historical maxima;
- header shows market truth, snapshot ID, event age, universe, valid-row count and rank-policy version;
- every opportunity exposes event age, source, evidence and eligibility independently from rank;
- missing age/quote proof yields `STALE/REJECT` or `WATCH`, never paper eligibility;
- high-watermark carryover is explicitly forbidden;
- rank changes are tied to a new snapshot revision and deterministic policy;
- candidate drilldown contains prediction/risk/evidence references before any paper action;
- load/concurrency panel exposes scanner cycle ID, shard generation, worker count, timeouts and rejected stale writers;
- null values remain unknown rather than zero;
- live router remains locked.

Visual artifact: `Genesis_System3_Scanner_Ranker_Truth_Target_V14.png`.

## 13. Positive foundations to preserve

- Native Sidebar buttons, named navigation landmark and `aria-current`.
- ProductionProofBar accessible label and text status values.
- `prefers-reduced-motion` support in `index.css`.
- Semantic login form and main landmark.
- Prediction Audit's refusal to present gain-rank as a validated forecast.
- ML router's `ready_for_live=False` safety intent.
- Firestore transaction/local temp+replace foundations.
- Serialized/rate-paced Dhan option-chain traffic and WS reconnect backoff+jitter foundations.
- Scanner query bounds, index-first request path and explicit Dhan pacing comments.
- Live Gate approval does not automatically enable live trading.

These are foundations, not readiness/accessibility/profitability proof.

## 14. Historical proof/open-gate interpretation

Remain open:
- `EXACT_REVISION_CI_RUNTIME_NOT_PROVEN`
- `DEPLOYMENT_TRUTH_NOT_PROVEN`
- `SHARED_STATE_AUTHORITY_NOT_PROVEN`
- `RESTART_CONSISTENCY_NOT_PROVEN`
- `MULTI_WRITER_LOST_UPDATE_PROTECTION_NOT_PROVEN`
- `SCANNER_CURRENT_SNAPSHOT_NOT_PROVEN`
- `SCANNER_ROW_FRESHNESS_NOT_PROVEN`
- `SCANNER_LOAD_STABILITY_NOT_PROVEN`
- `SCANNER_CANDIDATE_ELIGIBILITY_NOT_PROVEN`
- `PREDICTION_LEDGER_NOT_PROVEN`
- `MODEL_ARTIFACT_IDENTITY_NOT_PROVEN`
- `PURGED_WALKFORWARD_NOT_PROVEN`
- `PROBABILITY_CALIBRATION_NOT_PROVEN`
- `MODEL_DRIFT_MONITORING_NOT_PROVEN`
- `PREDICTION_AFTER_COST_LINKAGE_NOT_PROVEN`
- `RESPONSIVE_WORKSTATION_NOT_PROVEN`
- `KEYBOARD_NAVIGATION_NOT_PROVEN`
- `ACCESSIBILITY_AXE_BROWSER_PROOF_NOT_PROVEN`
- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `REAL_PAPER_LIFECYCLE_NOT_PROVEN`
- `WEBSOCKET_STREAM_HEALTH_NOT_PROVEN`
- `OPTION_CHAIN_RUNTIME_TRUTH_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` remains required audit posture.

## 15. Closure standard

A finding becomes `CLOSED` only on the exact changed revision with source inspection; positive/negative tests; static/type/build checks; unit/integration/browser tests; route/schema reconciliation; model/data hashes and frozen-cutoff proof where applicable; leakage/purged-walk-forward/calibration/drift tests for ML; prediction→paper→after-cost reconciliation; concurrency/CAS/restart/failover tests; expiry/cache/freshness/order/reconnect tests as applicable; scanner current-snapshot/session/TTL/out-of-order/high-watermark/load tests; responsive viewport + 200%-zoom + keyboard + axe/console checks; immutable image digest + final Cloud Run revision/runtime proof; analyzer/live-off unchanged; and no contradictory independent evidence.

## 16. Next audit/solution slices

1. Security/session detail: cookie policy, CSRF, session revocation, command/settings permissions and audit export.
2. Scanner follow-up: locate micro-loop/state-file writer and prove whether overlapping cycles can write out of order under Cloud Run concurrency.
3. ML follow-up: exact market-validation file semantics and whether gain-rank post-market validation has frozen prediction IDs/cutoffs or look-ahead paths.
4. DB follow-up: exact paper/event persistence files and any SQLite/JSON/Firestore duplicate authorities not yet mapped.
5. Browser implementation follow-up once SOL-15 lands: exact Playwright/axe/console proof across every workspace.

## 17. Hard safety rule

A green UI, endpoint HTTP 200, socket OPEN, historical parser/training PASS, AUC/accuracy, rank-derived confidence, scanner rank, high-watermark cached winner, image tag, UI badge, workflow success description, global state version, Firestore transaction, local atomic write, zero-valued quote/Greek/risk/P&L, static PAPER SAFE, stale cache, inferred Dhan source, human approval, accessible-looking static markup or process-local simulator never substitutes for authoritative source+event time+domain/snapshot revision+writer+freshness+schema+ordering+immutable prediction/model/data evidence+calibration+forward validation+lifecycle+enforceable risk+reconciliation+positive after-cost expectancy+exact source SHA+immutable image digest+final serving runtime revision proof. Live order placement, modification, cancellation and routing remain prohibited during this audit.