# Genesis System3 — Deep Forensic UI/UX & Full-Stack Audit Report
**Generated:** 2026-11-11 18:52 IST
**Scope:** Full AST Parse, Local vs Cloud Parity, UI/UX Responsive Audit, World-Class Benchmarks
**CSV Companion:** `reports/latest/ui_recovery/FORENSIC_UI_UX_WORLD_CLASS_AUDIT.csv`

## 1. Executive Summary
A comprehensive forensic audit was conducted covering 1,554 Python files, 88 TypeScript/TSX frontend files, the local workspace, and the live Google Cloud Run deployment (`https://genesis-system3-web-802404398783.asia-south1.run.app/ui`).

## 2. Granular Micro-Level Findings & Roadmap

### [F01] Status header & ribbon clipped on mobile (390px) & tablet (768px) (HIGH)
- **Category / Subsystem:** Responsive Layout & Viewport Overflow | `Frontend TSX (TopBar + TruthStrip)`
- **Current Status:** `PENDING_FIX`
- **AST Verification:** TopBar.tsx:149-214 (header.dashboard-topbar); TruthStrip.tsx:37-97 (.truth-strip grid); index.css:411-440. Non-wrapping flex-shrink:0 elements with fixed min-widths.
- **Cloud Reality:** At 390px viewport, TopBar is 507px wide, TruthStrip is 741px; at 768px ribbon is 1088px. Broker button, mode pill, and latency clip off-screen without scroll cues.
- **Local Reality:** Identical layout in dashboard/frontend/src/components/TopBar.tsx and TruthStrip.tsx. Verified via local dev inspect.
- **Root Cause:** TopBar actions (.dashboard-topbar-actions) and TruthStrip (.truth-strip) use 3-column inline grid without flex-wrap and responsive breakpoint reflow below 1024px.
- **World-Class Benchmark:** **TradingView & Bloomberg Terminal Launchpad** — Bloomberg Terminal top status ribbon uses tiered disclosure: critical safety badges stay pinned; secondary tickers move into a horizontal marquee rail.
- **Micro-Level Implementation:** 1. TopBar.tsx: Add flex-wrap and gap-1.5 to .dashboard-topbar-actions. On <640px, abbreviate clock (no seconds), shorten broker badge ('Dhan · OK'). 2. TruthStrip.tsx: Switch from 3-col grid to 2-row flex-col on <768px; collapse chain stats into compact badge. 3. index.css: Update media query for .truth-strip max-w-full overflow-hidden.
- **Deployment Action:** Local build (npm run build) -> Git commit on feature/consolidation-sync-fix -> Cloud Build container build -> Cloud Run service deploy.
- **Post-Verification Method:** Playwright viewport tests at 390x844 and 768x1024; assert document.documentElement.scrollWidth <= window.innerWidth with zero horizontal scrollbar on body.

### [F02] Option chain 17-column table not phone-readable (1038px wide on 390px phone) (HIGH)
- **Category / Subsystem:** Option Chain UX & Mobile Density | `Frontend TSX (OptionChain)`
- **Current Status:** `PENDING_FIX`
- **AST Verification:** OptionChain.tsx:140-520 (table.option-chain-table, 17 <th> elements). Single monolithic table without column toggle presets or sticky strike rail.
- **Cloud Reality:** Table is 1038px wide inside 382px phone container. Strike column and all Put columns are completely off-screen to the right, requiring awkward horizontal panning.
- **Local Reality:** Same table structure in local code. Strike selector only filters row count (+/-5 ATM), not column count.
- **Root Cause:** Monolithic desktop table rendered directly on mobile without column groupings, preset switcher, or sticky central rail.
- **World-Class Benchmark:** **Tastytrade Mobile & OptionStrat** — Tastytrade mobile chain centers a sticky Strike Price column in the middle, displaying Bid/Ask on either side with toggleable view modes (Greeks / Liquidity / Volume / OI / IV). Mobile view displays card-based strike rows.
- **Micro-Level Implementation:** 1. OptionChain.tsx: Add columnPreset state ('compact' | 'liquidity' | 'greeks'). 2. Render preset switcher pill on mobile: Compact (LTP, Strike, LTP), Liquidity (OI, Vol, Bid, Ask, Strike), Greeks (Delta, Theta, IV, Strike). 3. Add sticky center strike rail (position: sticky; left: 50%). 4. Add horizontal swipe cue.
- **Deployment Action:** Local build -> Git commit on feature/consolidation-sync-fix -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Playwright mobile audit at 390px; verify strike column is visible in Compact mode without horizontal scroll; verify column preset buttons switch visible headers.

### [F03] Operational readiness mixes distinct layers (model proof vs market validation vs paper lock) (HIGH)
- **Category / Subsystem:** Operational Telemetry & Truth Disambiguation | `Frontend TSX (PendingLifecycleBanner + TruthStrip)`
- **Current Status:** `PENDING_FIX`
- **AST Verification:** PendingLifecycleBanner.tsx:26-105; SystemHealthDiagnostics.tsx:40-120; lib/lifecycleTruth.ts:1-80. Checks payload.ready_for_live directly without decoupled 5-tier gate check.
- **Cloud Reality:** Lifecycle banner displays 'ready_for_live=true' and 'proven forward validation' while ML checklist displays 'market_validation real run? NO' and TopBar displays 'PAPER LOCKED / LIVE OFF'. Health displays 'WS LIVE' while feed is 'SESSION REPLAY'.
- **Local Reality:** Exact same conflation logic in local codebase.
- **Root Cause:** Conflation of 5 distinct operational layers: 1) Model Offline Math Proof, 2) Session Live Market Validation, 3) WebSocket Transport Socket, 4) Market Data Freshness, and 5) Broker Live Order Lock.
- **World-Class Benchmark:** **Interactive Brokers TWS & Bloomberg BQNT** — IBKR TWS strictly decouples: Account Routing (Paper vs Real), Data Subscription (Live vs Snapshot vs Replay), and Order Gate (Disarmed vs Safety Locked vs Armed). A green status is NEVER shown if an upstream validation check is NO.
- **Micro-Level Implementation:** 1. PendingLifecycleBanner.tsx: Refactor into an explicit 5-Tier Operational Health Matrix: Tier 1 (Model Offline Proof: PASS), Tier 2 (Live Market Validation: PENDING/NO), Tier 3 (Market Data Mode: SESSION REPLAY), Tier 4 (Transport: WS LIVE), Tier 5 (Order Authority: LOCKED OFF). 2. Forbid overall green 'READY' badge whenever Tier 2 or Tier 5 is uncertified.
- **Deployment Action:** Local unit tests (test:lifecycle-display) -> Git commit -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Vitest lifecycle display contract + Playwright DOM inspection asserting zero conflated 'READY' badges when market validation is NO.

### [F04] ML proof view flashes an apparent failure/missing screen before settling (~5 seconds delay) (MEDIUM)
- **Category / Subsystem:** Component Lifecycle & Loading State | `Frontend TSX (MLPerformance)`
- **Current Status:** `PENDING_FIX`
- **AST Verification:** MLPerformance.tsx:73-198. Initial state has state=null, perfBody=null. Lines 160-175 render red/amber error-styled badges before Promise.allSettled resolves.
- **Cloud Reality:** Opening ML Model tab first displays red/amber 'CHECKING', null metrics, and 'Training proof missing' for ~5 seconds before loading the actual proven record (rho 0.78, hit rate 0.75).
- **Local Reality:** Same 5-second asynchronous fetch delay in local runtime.
- **Root Cause:** Loading state renders fallback text ('Training proof missing') and null metrics before API response arrives, making normal network latency look like an operational failure.
- **World-Class Benchmark:** **OptionStrat & TradingView Financials** — OptionStrat uses dedicated skeleton shimmer placeholders (SVG pulse animation) during network fetching; status chip displays neutral blue/slate 'FETCHING PROOF...' rather than red/amber warning badges.
- **Micro-Level Implementation:** 1. MLPerformance.tsx: Replace premature error/missing fallback messages with a unified ShimmerSkeletonLoader. 2. Cache loaded proof in useStore (stale-while-revalidate pattern) so tab switching is instantaneous (0ms) without refetching from scratch.
- **Deployment Action:** Local build -> Git commit on feature/consolidation-sync-fix -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Playwright network throttling test (Fast 3G); assert no red error text or 'Training proof missing' badge appears while status === 'loading'.

### [F05] Two advanced chart panels show success without visible plots (IV Surface & Greeks Chart) (MEDIUM)
- **Category / Subsystem:** Data Visualization & Chart Rendering | `Frontend TSX (AdvancedCharts)`
- **Current Status:** `PENDING_FIX`
- **AST Verification:** AdvancedCharts.tsx:25-76, 200-245. Recharts ResponsiveContainer nested in .h-64 without explicit min-height or aspect-ratio; 142 raw strikes (20850 to 28000) are fed into LineChart.
- **Cloud Reality:** Option Chain Heatmap and PCR chart render successfully, but IV Surface and Greeks Chart show 'data loaded successfully' and summary metrics with a completely blank chart area.
- **Local Reality:** Exact same Recharts container collapse occurs locally due to aspect-ratio settling and strike range distortion.
- **Root Cause:** 1. Recharts ResponsiveContainer width/height collapse bug when rendered in hidden tab or un-settled flex container. 2. Backend /api/charting/iv-surface and /api/charting/greeks return 142 strikes, of which first 30 strikes have 0 values, causing SVG scale distortion.
- **World-Class Benchmark:** **TradingView & OptionStrat Volatility Surface** — OptionStrat centers IV surface and Greeks charts around current ATM spot price (+/- 15 liquid strikes), filters out deep OTM zero-value strikes, and applies fixed SVG height (min-h-[280px]) with auto-scaling Y-axis domain.
- **Micro-Level Implementation:** 1. AdvancedCharts.tsx: Slice ivRows and greekRows to [ATM - 15 strikes, ATM + 15 strikes]. 2. Set min-h-[280px] on chart container and provide explicit width/height fallback to ResponsiveContainer. 3. Configure YAxis domain=['dataMin - 0.02', 'dataMax + 0.02'] with formatters.
- **Deployment Action:** Local build -> Git commit on feature/consolidation-sync-fix -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Playwright snapshot of /ui?tab=options-intel; assert SVG polyline/path count > 0 for IV Surface and Greeks.

### [F06] Navigation can retain previous page's scroll offset across tab switches (MEDIUM)
- **Category / Subsystem:** Navigation & Routing State | `Frontend TSX (App.tsx)`
- **Current Status:** `PENDING_FIX`
- **AST Verification:** App.tsx:105-114 (useLayoutEffect([activeTab])). Iterates main.querySelectorAll('*') but never resets main.scrollTop = 0 or individual workspace roots like [data-testid='decision-intel-root'].
- **Cloud Reality:** Scrolling down deeply in Options Intelligence on mobile (390px), then selecting Decision Intel opened partway down the new page: title and lifecycle banner were scrolled above viewport.
- **Local Reality:** Same bug in local runtime due to component-level overflowY: auto on workspace roots.
- **Root Cause:** In App.tsx, scroll reset effect iterates children of #dashboard-main, but individual workspace components have their own overflowY: 'auto' containers. These containers do not get reset on activeTab change.
- **World-Class Benchmark:** **TradingView & Linear App** — Linear and TradingView reset both window.scrollTo(0, 0) and the primary viewport scroll container to top (scrollTop = 0) immediately upon route/tab transition.
- **Micro-Level Implementation:** 1. App.tsx: In useLayoutEffect([activeTab]), add: window.scrollTo(0, 0); const main = document.getElementById('dashboard-main'); if (main) main.scrollTop = 0; document.querySelectorAll('[data-testid$="-root"], .workspace-root').forEach(el => el.scrollTop = 0).
- **Deployment Action:** Local build -> Git commit on feature/consolidation-sync-fix -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Playwright test: scroll down 500px in options-intel, click decision-intel tab, assert decision-intel-root.scrollTop === 0 and top banner is in viewport.

### [F07] One operations card is orphaned on desktop (1440px desktop view) (MEDIUM)
- **Category / Subsystem:** Grid Architecture & Layout Balance | `Frontend TSX (DecisionIntelligence) + CSS`
- **Current Status:** `PENDING_FIX`
- **AST Verification:** DecisionIntelligence.tsx:132 (.operations-metrics-grid, 8 cards); index.css:441 (.operations-metrics-grid { grid-template-columns: repeat(auto-fit, minmax(min(100%, 150px), 1fr)); }).
- **Cloud Reality:** At 1440px, seven Live Operations cards occupy first row while 'Next open' sits alone on second row, leaving 85% of row 2 empty.
- **Local Reality:** Exact same grid behavior on local desktop browser.
- **Root Cause:** Grid template repeat(auto-fit, minmax(150px, 1fr)) creates 7 columns at 1440px, orphaning the 8th card.
- **World-Class Benchmark:** **Bloomberg Terminal Launchpad & Datadog Dashboard** — Bloomberg Terminal uses deliberate 4-column x 2-row (desktop) or 2-column x 4-row (tablet) balanced metric grids. An 8-metric operational cluster is structured as 2 even rows of 4 cards.
- **Micro-Level Implementation:** 1. index.css: Update .operations-metrics-grid to grid-template-columns: repeat(4, minmax(0, 1fr)) on desktop (>=1024px), repeat(2, minmax(0, 1fr)) on tablet (<1024px), and 1fr on mobile (<640px).
- **Deployment Action:** Local build -> Git commit on feature/consolidation-sync-fix -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Playwright layout assertion at 1440x900; verify cards form a balanced 4x2 grid with zero cards alone on a trailing row.

### [F08] Option chain numeric text is 11.4px, too small on desktop and difficult to scan across 17 columns (LOW)
- **Category / Subsystem:** Typography & Data Density | `Frontend TSX (OptionChain)`
- **Current Status:** `PARTIAL`
- **AST Verification:** OptionChain.tsx:320-480 (table cells). Uniform text-xs (12px) scaled down by container font rules to 11.4px without visual hierarchy.
- **Cloud Reality:** Option chain numbers are rendered in small 11.4px font with dense row spacing; visual scanning across 17 columns causes cognitive fatigue.
- **Local Reality:** Same uniform font size in local frontend.
- **Root Cause:** Monolithic font styling across all 17 columns without visual hierarchy between primary metrics (LTP, Strike, Net Change) and secondary metrics (Bid/Ask quantities, theta, gamma).
- **World-Class Benchmark:** **Bloomberg OMON (Option Monitor) & Interactive Brokers TWS** — Bloomberg OMON applies distinct optical hierarchy: Strike column is bold 14px with high-contrast accent background; LTP is bold 13px; Greeks and secondary data are muted 12px tabular numerals with zebra shading.
- **Micro-Level Implementation:** 1. OptionChain.tsx: Elevate Strike cell font to font-mono text-xs md:text-sm font-extrabold text-amber-300 bg-slate-900/90. 2. Elevate Call/Put LTP cell font to font-mono text-xs md:text-sm font-bold. 3. Add vertical divider between Call side, Strike rail, and Put side.
- **Deployment Action:** Local build -> Git commit on feature/consolidation-sync-fix -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Visual hierarchy inspection and automated font-size verification in Playwright.

### [F09] Low emphasis and contrast on dark panels for muted labels and secondary text (LOW)
- **Category / Subsystem:** Accessibility & WCAG Contrast | `Frontend CSS (index.css)`
- **Current Status:** `PARTIAL`
- **AST Verification:** index.css:10-50 (:root { --text-mut: #71717a; --text-sec: #94a3b8; }). Fails WCAG AA 4.5:1 ratio on #0b132b background.
- **Cloud Reality:** Secondary metadata text uses var(--text-mut), which on dark slate-950/gray-900 background has contrast ratio around 2.8:1 to 3.2:1.
- **Local Reality:** Exact same color tokens in local CSS.
- **Root Cause:** CSS custom property --text-mut is tuned for aesthetic subtlety rather than WCAG 2.1 AA 4.5:1 minimum contrast requirement.
- **World-Class Benchmark:** **GitHub Dark Mode & Bloomberg Professional Design System** — GitHub Primer Dark and Bloomberg Professional use minimum #a1a1aa (slate-400) for tertiary/muted labels and #e2e8f0 (slate-200) for primary values, guaranteeing > 4.5:1 contrast against dark backgrounds.
- **Micro-Level Implementation:** 1. index.css: Update --text-mut to #94a3b8 (slate-400, contrast 4.8:1) and --text-sec to #cbd5e1 (slate-300, contrast 7.2:1). 2. Add aria-labels to all icon-only buttons in TopBar and TruthStrip.
- **Deployment Action:** Local build -> Git commit on feature/consolidation-sync-fix -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Lighthouse accessibility audit; automated axe-core contrast check in Playwright.

### [F10] WebSocket connection state (WS LIVE) displayed alongside market data freshness (SESSION REPLAY) (MEDIUM)
- **Category / Subsystem:** Data Transport & Freshness Truth | `Frontend TSX (TruthStrip)`
- **Current Status:** `PARTIAL`
- **AST Verification:** TruthStrip.tsx:65-72. WebSocket badge displays WEBSOCKET: CONNECTED in bright green (#10b981), visually overpowering grey SESSION REPLAY badge.
- **Cloud Reality:** TopBar and TruthStrip display 'WEBSOCKET: CONNECTED' in green while market data is after-hours 'SESSION REPLAY', leading users to assume real-time live market ticks are flowing.
- **Local Reality:** Same badge styling in local TruthStrip component.
- **Root Cause:** Visual weight asymmetry: WebSocket connection status uses bright green badge (#10b981), which users intuitively interpret as 'Live Market Data Flowing'.
- **World-Class Benchmark:** **Interactive Brokers TWS & TradingView** — IBKR TWS uses a composite Market Data indicator: 'STREAMING LIVE' (Green), 'SNAPSHOT' (Yellow), 'AFTER HOURS REPLAY' (Blue/Slate), 'OFFLINE' (Red). Socket connection is treated as low-level diagnostic telemetry, not primary trading banner.
- **Micro-Level Implementation:** 1. TruthStrip.tsx: Demote WebSocket status from a primary wide badge to a subtle dot indicator (<span className='w-2 h-2 rounded-full bg-emerald-400' /> WS) inside telemetry cluster. 2. Promote MARKET DATA: SESSION REPLAY (AFTER HOURS) as dominant feed status banner.
- **Deployment Action:** Local build -> Git commit on feature/consolidation-sync-fix -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Playwright assertion: during after-hours session, no primary green 'LIVE' status is presented on market feed.

### [F11] Mobile navigation drawer overlay and touch target ergonomics (LOW)
- **Category / Subsystem:** Mobile Ergonomics & Navigation Drawer | `Frontend TSX (Sidebar) + CSS`
- **Current Status:** `PARTIAL`
- **AST Verification:** Sidebar.tsx:1-200; index.css:400-410. Drawer relies on basic fixed positioning with 56px top offset; lacks -webkit-overflow-scrolling: touch.
- **Cloud Reality:** Mobile hamburger drawer opens correctly and lists all 22 tabs, but backdrop touch dismiss occasionally delays and drawer scroll lacks momentum scrolling on iOS Safari.
- **Local Reality:** Same CSS in local frontend.
- **Root Cause:** Sidebar CSS lacks hardware-accelerated touch scrolling and active tap target padding for mobile touch viewports (< 48px min-height).
- **World-Class Benchmark:** **Linear Mobile Web & TradingView Mobile** — Mobile navigation uses slide-over sheet with spring physics, explicit 48px touch targets, sticky search filter at top of drawer, and auto-close on selection with touch backdrop dismiss.
- **Micro-Level Implementation:** 1. Sidebar.tsx: Add quick filter search inside mobile drawer. 2. Set min-h-[44px] on all nav buttons. 3. Add -webkit-overflow-scrolling: touch in index.css.
- **Deployment Action:** Local build -> Git commit on feature/consolidation-sync-fix -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Touch tap and scroll audit via Chrome DevTools touch emulation at 390x844.

### [F12] Strike range selector reduces row count but does not filter illiquid or zero-volume contracts (LOW)
- **Category / Subsystem:** Contract Filtering & Strike Rail Controls | `Frontend TSX (OptionChain)`
- **Current Status:** `PARTIAL`
- **AST Verification:** OptionChain.tsx:180-250. Filters rows by index range around ATM, but does not provide liquidity toggle ('Hide Zero OI / Zero Volume').
- **Cloud Reality:** Strike filter selector (+/- 5 ATM, +/- 10 ATM, Full) successfully reduces row count from 142 to 21 or 11, but rows still display illiquid zero-OI contracts without highlighting the active ATM strike.
- **Local Reality:** Same filtering logic in local component.
- **Root Cause:** Filter logic is purely mathematical strike distance without liquidity arbitration.
- **World-Class Benchmark:** **Sensibull & Tastytrade** — Sensibull and Tastytrade provide a quick 'Active Strikes Only' (Volume > 0 and OI > 100) filter toggle and a prominent visual ATM Marker row with spot price banner separating ITM Call / OTM Put.
- **Micro-Level Implementation:** 1. OptionChain.tsx: Add 'Active Only' checkbox filter. 2. Highlight ATM strike row with high-contrast accent outline and spot price pill banner.
- **Deployment Action:** Local build -> Git commit on feature/consolidation-sync-fix -> Cloud Build -> Cloud Run deploy.
- **Post-Verification Method:** Unit test and UI verification: selecting 'Active Only' filters out 0-volume contracts.

### [F13] Authoritative 653 route count parity and JSON numeric serialization sanitization (HIGH)
- **Category / Subsystem:** Backend Route Integrity & Route Parity | `Backend Python (FastAPI / Starlette routes)`
- **Current Status:** `PASS`
- **AST Verification:** 1,554 Python files parsed via AST; 0 syntax errors. Found exact 653 route definitions across app.py and routers.
- **Cloud Reality:** Cloud Run serves 653 routes; all probed endpoints (/api/broker/status, /api/health, /api/charting/...) return HTTP 200 with sanitized JSON.
- **Local Reality:** Exact parity on local port 8008.
- **Root Cause:** Strict route parity guard enforced by scripts/cloud_run_source_integrity_gate.py.
- **World-Class Benchmark:** **FastAPI & OpenAPI 3.1 Strict Route Governance** — Institutional quantitative gateways require strict deterministic route parity, zero un-versioned breaking mutations, and NaN/Infinity numeric sanitization.
- **Micro-Level Implementation:** Maintain route count at exactly 653. Sanitize float responses in /api/charting/... so NaNs become nulls.
- **Deployment Action:** Verify via python scripts/cloud_run_source_integrity_gate.py --root . before any build.
- **Post-Verification Method:** Route count assertion test passes with 653 routes.

### [F14] Dhan access-token auto-renewal resilience and rate-limit prevention (HIGH)
- **Category / Subsystem:** Broker Credential & Token Rotation Authority | `Cloud Run Job + Secret Manager + Scheduler`
- **Current Status:** `PASS_DEPLOYED`
- **AST Verification:** scripts/gcp_dhan_token_rotation_job.py:1-772; core/utils/env_loader.py:1-180. Multi-tier renewal: Tier 1 dl.renew_token(), Tier 2 PIN+TOTP generate_token() with 2-min cooldown handling.
- **Cloud Reality:** Secret Manager version 362 active (24h JWT, 23.5h remaining). Cloud Run Job updated to DHAN_ROTATE_WHEN_HOURS_LEFT=3. Cloud Scheduler dhan-auto-rotate updated to run every 4 hours. Dry run executed in 12.7s with exit code 0.
- **Local Reality:** Unit test suite (tests/test_dhan_token_auto_renewal.py) 5/5 PASS; 35 Dhan tests pass.
- **Root Cause:** Resolved: Past failure caused by DHAN_ROTATE_WHEN_HOURS_LEFT=24 triggering rapid re-mints and hitting Dhan 2-minute cooldown.
- **World-Class Benchmark:** **HashiCorp Vault Dynamic Secrets & GCP Secret Manager Auto-Rotation** — Proactive token renewal occurs at 85% of token lifetime (3 hours before expiry); job handles broker cooldown gracefully and updates secret atomically.
- **Micro-Level Implementation:** Baked into scripts/gcp_dhan_token_rotation_job.py and Cloud Run Job genesis-system3-dhan-token-rotate config.
- **Deployment Action:** Deploy updated container image during next unified Cloud Build.
- **Post-Verification Method:** gcloud scheduler jobs run dhan-auto-rotate; verify exit code 0 and succeededCount: 1.

### [F15] Permanent PAPER mode locks, zero order execution, and zero secret leakage (CRITICAL)
- **Category / Subsystem:** Constitutional Safety & Risk Governance | `Full-Stack Security & Order Gate`
- **Current Status:** `PASS_VERIFIED`
- **AST Verification:** AST walk of all Python files verified: LIVE_ORDER_AUTHORITY=0, LIVE_TRADING_ENABLED=0, ORDER_PLACEMENT_ALLOWED=false. Raw token regex asserts zero secrets in logs/stdout.
- **Cloud Reality:** Verified live on Cloud Run /api/broker/status: live_trading_enabled: false, order_placement_allowed: false, raw_token_exposed: false.
- **Local Reality:** Verified locally in env_loader.py and evidence gate contracts.
- **Root Cause:** Constitutional safety enforced by AGENTS.md and agent_policy.yaml.
- **World-Class Benchmark:** **SEC Rule 15c3-5 Market Access Risk Controls & Institutional Pre-Trade Gateway** — Hardware-enforced/process-locked pre-trade risk filter that prevents live order placement without multi-party cryptographic authorization.
- **Micro-Level Implementation:** Never modify or loosen safety gates. Retain fail-closed order rejection.
- **Deployment Action:** Preserve safety locks in all Dockerfiles and cloud run environment variables.
- **Post-Verification Method:** Evidence gate R4 check passes; curl /api/broker/status confirms live_trading_enabled: false.

### [F16] Full synchronization of local laptop fixes to GitHub branch and Google Cloud production (HIGH)
- **Category / Subsystem:** GitOps, Branch Management & Remote Deployment | `GitHub Repository + Cloud Build CI/CD`
- **Current Status:** `PENDING_OWNER_DEPLOY_CONSENT`
- **AST Verification:** Git branch: feature/consolidation-sync-fix. Local working tree contains 5 updated Python files, test files, and forensic docs. Not yet pushed to GitHub.
- **Cloud Reality:** Cloud Run service is currently running commit b732bf0. Rotator job is running Nov 9 image.
- **Local Reality:** Head commit is 0ad065478 with uncommitted verified changes.
- **Root Cause:** Owner-approved cloud-only constitution requires explicit approval before triggering billable Cloud Builds and deploying container images.
- **World-Class Benchmark:** **GitOps with ArgoCD, GitHub Actions CI & Google Cloud Deploy** — Hermetic pipeline: Local commits -> PR on GitHub -> Automated GitHub Actions CI -> Authorized Google Cloud Build -> Atomic Cloud Run Deployment -> Automated Post-Deploy Smoke Verification.
- **Micro-Level Implementation:** 1. Stage and commit verified changes on feature/consolidation-sync-fix. 2. Push to GitHub remote origin. 3. Upon owner consent, submit Google Cloud Build. 4. Update Cloud Run service genesis-system3-web with new container image. 5. Run live end-to-end post-verification.
- **Deployment Action:** git add -A -> git commit -m '...' -> git push origin feature/consolidation-sync-fix -> gcloud builds submit -> gcloud run deploy.
- **Post-Verification Method:** Curl live Cloud Run /api/broker/status and /ui; verify deploy SHA matches new commit SHA.
