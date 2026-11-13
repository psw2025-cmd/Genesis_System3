# ANTIGRAVITY — PRODUCTION FORENSIC + LIVE UI + 100-COMMAND VALIDATION MISSION
Date: 2026-11-04 | Owner priority: production-grade, cloud-only, genuine market truth, PAPER ONLY.
Status: **MISSION / NOT CERTIFICATION**. Agent must run, collect and independently verify results. Do not mark PASS on the strength of this prompt.

## NON-NEGOTIABLE SAFETY
- PAPER_MODE=1, LIVE_TRADING_ENABLED=0, LIVE_ORDER_AUTHORITY=0, REAL_BROKER_ORDERS=0, AUTO_EXECUTE_TRADES=0. Do not place, modify or cancel a real broker order, even as a test. Do not turn these locks on. Never expose broker tokens, client IDs or secrets in output.
- Never claim market feed verified from JWT validity, Dhan profile HTTP 200, local cache mtime, simulated ticks, synthetic strikes, mock APIs, or a UI badge.
- Do not kill unrelated processes, mass-clean dirty worktrees, rotate credentials, merge, commit or deploy without owner approval and exact source/revision identification. Preserve existing evidence. Tests must be non-destructive, read-only or isolated paper simulations.
- The local repo is C:\Genesis_System3_clean on branch fix/scanner-219-equity-rotate, with a dirty worktree; owner also has C:\Genesis_System3 on another branch. First resolve authoritative source and production entrypoint. Cloud Run previously used dashboard/backend/app.py, while local port 8021 runs untracked content/app/app.py. **Local green does not mean production green.**
- Market hours: NSE 09:15–15:30 Asia/Kolkata on actual trading days; weekends, holidays, exchange halts and stale last-close data must be labeled. Do not generate traffic beyond Dhan API quotas (option chain roughly one request/3 seconds, verify current documentation).

## Known facts requiring re-verification, not assumptions
- Resolved Dhan detailed master: storage/instruments/api-scrip-master-detailed.csv, 201786 rows; NSE D OPTSTK 68663 rows and **218** unique UNDERLYING_SYMBOL, versus earlier target 219. BSE D OPTSTK 216 symbols. Do not manufacture the 219th. Check current exchange circulars, symbol renames, expiries and effective dates.
- Local chain cache has eight files, only two equity symbols (RELIANCE, COLPAL), zero fresh snapshots in last audit; cached NIFTY 171 contracts and total positive-LTP 929 are NOT live quotes. Evidence: reports/latest/ui_recovery/MASTER_OPTION_COVERAGE.json, EQUITY_219_PAPER_READINESS.json.
- Local safety .env 5/5 PASS, DhanReadOnly adapter order guards 11/11 PASS, API three safety flags PASS; **not a complete all-path order execution certification**. Evidence: READONLY_ORDER_GUARDS.json.
- Local canary http://127.0.0.1:8021/ui; actual production URLs and deploy revision must be discovered and read-only checked. Do not assume port 8021 is user-facing/cloud UI.
- Prior reports claim an authenticated Dhan quote with exchange timestamp via /api/verified-market, but this is a different route from option-chain streaming and needs independent provenance and freshness verification.
- User sees UI not updating during market hours; investigate source→ingestion→writer→cache→API→WebSocket/SSE/poll→frontend render, comparing OpenAlgo behavior and actual upstream quote timestamps. Avoid blaming frontend until measurements prove the bottleneck.

## FIRST: EVIDENCE BASELINE BEFORE CHANGES
Create immutable run folder reports/latest/ui_recovery/forensic_YYYYMMDD_HHMMSS/ with RUN_ID, UTC+IST timestamps, repo path, git SHA, dirty status, current deployed revision/image digest, python/env versions, local/cloud service inventory, safety locks, market session calendar and evidence hashes. Save redacted stdout/stderr, command, exit code, duration, and artifact for every command. Do not print .env or credentials in full. Existing tracker and old snapshots are historical only.

## 100 COMMAND / CHECK MATRIX — RUN AND RETEST, NOT 100 BLIND COMMANDS
Use separate numbered read-only or safe paper-only commands, each with PASS/FAIL/BLOCKED/NOT_VERIFIED and actual evidence. Adapt syntax to the platform; do not fake outputs. Run independent commands where possible, then rerun every failing gate after corrective action and at least 3 distinct observation times for stream freshness. Never hammer upstream.
01–10 provenance: (01) pwd, (02) git rev-parse HEAD, (03) git status --porcelain, (04) git branch, (05) tracked entrypoints, (06) Cloud Run revision, (07) image digest, (08) container CMD, (09) dependency lock, (10) deployment-vs-local code diff.
11–20 safety: (11) .env five flags redacted exact match, (12) process-effective flags, (13) cloud-effective flags via safe metadata, (14) paper-only API, (15) all broker adapters inventory, (16) read-only order guard tests, (17) route audit for order POST/PUT/DELETE, (18) paper ledger isolation, (19) risk/stop limits, (20) forbidden live order calls static scan.
21–30 instruments: (21) master source, (22) SHA/mtime/provider date, (23) NSE OPTSTK distinct symbols, (24) BSE OPTSTK distinct, (25) expiry validity, (26) CE/PE security ID uniqueness, (27) strike/lot/tick correctness, (28) symbol aliases and renames, (29) 218 vs 219 reconciliation, (30) missing/duplicate underlyings.
31–40 Dhan connectivity: (31) auth profile status only, (32) market quote read-only status, (33) option chain read-only auth, (34) 401/403 handling, (35) 429/backoff, (36) timeout, (37) request latency, (38) exchange quote timestamp, (39) broker timestamp timezone, (40) token expiry without leaking secrets.
41–50 chain coverage: (41) index NIFTY, (42) BANKNIFTY, (43) SENSEX, (44) RELIANCE, (45) COLPAL, (46) TCS, (47) HDFCBANK, (48) INFY, (49) sample 10 diversified OPTSTK, (50) full eligible universe coverage report. Only real authenticated snapshots count as fresh coverage; batch with rate limits.
51–60 streaming: (51) provider quote age t0, (52) provider quote age t+interval, (53) provider quote age t+2interval, (54) ingest lag, (55) queue backlog, (56) cache write lag, (57) API response lag, (58) WS/SSE delivery lag, (59) frontend render lag, (60) no-update root-cause attribution with timestamps. Distinguish low-volume no-trade periods from broken streaming.
61–70 UI: (61) screenshot dashboard desktop, (62) mobile viewport, (63) top CE, (64) top PE, (65) equity options, (66) index options, (67) strike/expiry/CE-PE detail, (68) stale/closed banners, (69) paper order ticket, (70) recovery-progress tab. Save screenshot files, browser console, network HAR with secrets stripped, API payload references. Compare before/after screenshots.
71–80 external parity: (71) NSE official contract identity, (72) NSE option-chain price/timestamp, (73) BSE applicable listing, (74) Dhan official quote, (75) Dhan contract master, (76) Moneycontrol public top movers, (77) another independent broker public view where accessible, (78) OpenAlgo latency/architecture comparison, (79) cross-source same-contract strike/expiry/right match, (80) discrepancies with source and timestamp. Respect websites' terms; public pages may be delayed, not exchange-certified; never claim exact parity without synchronized timestamps.
81–90 paper lifecycle: (81) eligible verified signal, (82) same-contract security ID, (83) expiry and lot, (84) risk guard, (85) paper-only entry request, (86) simulated fill and slippage, (87) position and mark, (88) paper exit, (89) fees/net P&L, (90) closed trade outcome reconciliation against later exchange quotes. Use isolated paper engine, no real orders, no invented fills. If no fresh quote, mark BLOCKED.
91–100 production: (91) API contract tests, (92) parser tests, (93) stale-cache fail-closed tests, (94) 401/429/timeout mocked tests, (95) websocket reconnect tests, (96) concurrent writer/lease tests, (97) frontend build, (98) E2E screenshot parity, (99) cloud deploy readiness/rollback plan without deployment, (100) final independent certification and unresolved blocker list.

## REQUIRED CORRECTIVE IMPLEMENTATION, IN ORDER
A. Diagnose and fix the actual streaming bottleneck, measure provider→UI latency (p50/p95/p99) with exchange timestamp and receipt time; use bounded queue, reconnect/backoff, heartbeat, dedup, stale cutoff, market-hours calendar, and per-symbol freshness. Do not label simulated streaming live. Streaming may be websocket for quotes while Dhan option chain is rate-limited snapshots; never promise millisecond chain refresh for 218 underlyings.
B. Build authoritative NSE OPTSTK eligible universe from fresh Dhan security master with security IDs, expiry, option type, strike, lot, exchange/segment, update schedule and reconciliation against NSE. Never use hardcoded 219 or fabricated proximity strikes.
C. Implement throttled option-chain ingestion with bounded concurrency, auth refresh, 429 retry/backoff, checkpoint resume, source quote timestamps, idempotent storage, failure counters, and coverage by symbol/expiry. Full universe sweep time must be explicitly calculated from actual provider quota; show each symbol's last verified age.
D. API returns real data only when authenticated and fresh; show stale last-close as stale, unknown as unknown. Ensure `/api/options/gainers`, `/api/chain/{symbol}`, `/api/market/top-gainers`, health/inventory and paper routes agree on same contract identity and freshness.
E. UI must show Dhan-style underlying, exchange, expiry, strike, CE/PE, trading symbol, LTP, price change %, OI, volume, source, last exchange update and freshness; index and equity options in correct sections, search/filter 218 symbols, no misleading NIFTY label in equity paper orders. Provide streaming status, connection state and market-closed last verified close.
F. Paper engine must use exact security ID/expiry/strike/right/lot, simulated fills with defensible slippage and fees, risk caps, persistent lifecycle, later-outcome matching, and reconciled P&L. Never allow broker order write calls.
G. Fix tests and build only after reproducing the issue; re-run affected and regression suites, compare UI screenshots and independent NSE/Dhan reference. No green status without artifact and timestamp.
H. Cloud-only architecture with Cloud Run/Scheduler, authenticated read-only health/control, durable store, one writer/lease, secrets manager, minimal privilege, audit logging, rollback and cost constraints. Deploy only after source of truth and explicit approval; distinguish local staging proof from deployed production proof.

## WORLD-CLASS COMPARISON (EVIDENCE, NOT COSMETICS)
Benchmark against exchange/broker reference views (NSE, BSE, Dhan, Moneycontrol and accessible independent broker/OpenAlgo), and professional terminal capabilities: timestamp/freshness visibility, contract lookup, option chain grouping, multi-underlying search, bid/ask/volume/OI, stale handling, latency transparency, reconnection, traceable paper fills, risk gates, accessibility and mobile responsiveness. Create feature matrix: ours, reference, gap, screenshot/URL/time, implementable fix, retest result. Do not copy proprietary UI/assets or scrape authenticated services without authorization.

## DELIVERABLES
- 00_RUN_MANIFEST.json (SHA, revision, timestamp, mode)
- 01_100_COMMAND_EVIDENCE.csv (id, command, exit, time, evidence, PASS/FAIL/BLOCKED/NOT_VERIFIED, root cause, retest)
- 02_UI_BEFORE_AFTER/ (screenshots + HAR sanitized + console)
- 03_SOURCE_TO_UI_LATENCY.csv (exchange_time, ingest_time, cache_time, API_time, UI_time, p50/p95/p99)
- 04_218_219_UNIVERSE_RECONCILIATION.csv
- 05_AUTHENTICATED_CHAIN_COVERAGE.csv (each symbol, expiry, last quote, age, verified yes/no, reason)
- 06_NSE_DHAN_MONEYCONTROL_PARITY.csv (matched contract, timestamps, quote, discrepancy)
- 07_PAPER_TRADE_CHAIN_OF_CUSTODY.csv (signal, risk, fill, exit, P&L, source IDs)
- 08_FIX_AND_REGRESSION_REPORT.md (file/line, before, after, test, residual risk)
- 09_PRODUCTION_READINESS.md (strict evidence-backed gates, cloud-only readiness)
- 10_OWNER_STATUS_HINDI.md (simple: fixed, pending, exact blocker, one owner action if necessary)

## STOP RULE
Do not stop at a test count or self-reported percentage. Run diagnostic→root cause→minimal safe fix→retest→independent parity→UI screenshot→evidence receipt repeatedly. If blocked by unavailable API entitlement, market closed, missing auth, worktree conflict, deployment authority, or external website limitations, record precise blocker and the smallest owner action. **Never mark 100% while any critical gate is unverified.**

## ADDENDUM A — NEW INDEPENDENT STATIC FORENSIC FINDINGS (2026-11-04; MUST REPRODUCE)
Read-only commands inspected content/app/app.py and content/app/templates/premium.html plus tracked files. These are observed code-level mismatches, not a claim of production runtime impact.
1. **CRITICAL: live-order UI still sends POST to broker-style endpoint**: premium.html lines 29–81 function `submitLiveOrder` constructs payload with `apikey:"institutional_test_key"`, `symbol`, `exchange:"NSE"`, `action`, `quantity`, `pricetype`, `product`, and fetches `/api/v1/placeorder`. Even if backend currently blocks, this is not an isolated paper-order endpoint; the UI's default symbol is `NIFTY` (line 438), with no expiry/strike/CE-PE/security ID/lot. **Do not invoke this POST in testing.** Trace route registration and every execution path statically; remove broker-style submit from PAPER UI or replace with strictly isolated paper ledger API only after authorization and fail-closed tests.
2. **CRITICAL: stale cache overrides market prices**: app.py lines 120–144 load local `state/chain_cache`, then copy cached spot into `BASE_PRICES` during module import. More usages around lines 528, 666, 933–934, 1053, 1335. Audit whether stale spot feeds paper risk, simulated ticks, chart or prediction; do not use stale cache as live price. Introduce authenticated quote timestamp and provenance guard, fail closed on stale.
3. **HIGH: option gainers endpoint blocks on broker profile call**: app.py lines 724–728 async route calls synchronous `get_profile()` on each request, before reading local cache. Measure route p50/p95 and event-loop blockage; remove unrelated authentication dependency from cached-data display, cache authorized health separately with TTL, use nonblocking I/O for live calls.
4. **HIGH: hard-coded local Windows chain path**: app.py line ~739 `Path(r"C:\Genesis_System3_clean\state\chain_cache")` prevents portable Cloud Run ingestion. Use app-root configurable data source/durable storage, not laptop drive. Avoid secret leakage.
5. **HIGH: WebSocket incomplete**: premium.html lines 83–114 connects `/ws/stream` and updates only `nifty`, `banknifty`, `sensex`; no equity option chain/strike updates, no reconnect, heartbeat, last exchange timestamp, stale banner or quote age. Verify backend message schema and cadence. It is impossible for this handler alone to refresh all equity CE/PE rows.
6. **HIGH: error handling disguises cause**: premium.html catches WebSocket exceptions and silently ignores malformed messages; fetch catch shows `Live trading is locked` even on network errors. Distinguish blocked execution from disconnected backend; sanitize UI rendering to avoid injecting untrusted backend `detail` via innerHTML.
7. **HIGH: deployment source split**: `git ls-files content/app/app.py dashboard/backend/app.py` returned only `dashboard/backend/app.py`; local premium UI/app are untracked. Cloud entrypoint differs; a local port 8021 fix does not reach cloud. Worktree has 1154 changed/untracked/deleted status lines. Do not deploy dirty source blindly.
8. **MEDIUM: fixed UI reasoning/metrics**: premium.html around lines 1728–1738 includes static `sharpe`, `score`, `stoploss`, `target` and narrative for symbols. Audit every displayed metric for live/simulated/static labeling and remove fabricated live implication.
9. **HIGH: contract identity omitted from order ticket**: premium.html lines 438–468 accepts free-text symbol, quantity, side, price type, product, but not exchange segment, expiry, strike, option type, security ID, lot size; `selectSymbol` around line 1738 updates chart titles, not an authenticated option contract selection. Implement strict same-contract paper ticket from verified chain.
10. **Safety nuance**: local .env 5/5 PASS and DhanReadOnly adapter 11/11 RuntimeError guards PASS; these do NOT prove all POST routes fail closed. Never send a live-order HTTP request to prove safety; use isolated mock/unit tests or static route analysis.

### ADDENDUM B — REQUIRED TRIAGE
For each finding above: map route/component → trace data provenance → reproduce in safe isolated harness → collect timestamped evidence → write minimal production-grade fix → run regression → inspect real UI screenshot and network/console → independently compare provider timestamp → update closure tracker. Add ten or more dedicated commands to the 100-check matrix or expand to 120 checks; retain the original 100 IDs and log each actual command. Distinguish verified code defect, suspected runtime impact, and unverified production effect. Never call a simulated feed 'streaming' merely because the browser WebSocket is connected.

## ADDENDUM D — ALL UNVERIFIED FINDINGS AND SOLUTIONS
Mandatory order: verify FIRST, then fix, then reverify. Never call an unexecuted test PASS.
UNVERIFIED: actual cloud revision versus local source; 218-versus-219 equity universe and latest master; Dhan authenticated option chain freshness for each eligible symbol; 09:15–15:30 IST exchange-to-UI quote latency and update frequency; WebSocket delivery and reconnection; NSE/BSE/Dhan/Moneycontrol same-contract price parity; desktop/mobile UI screenshots and browser errors; paper entry-to-exit fills and fees; all broker execution routes fail closed; cloud scheduler/writer/lease and durable data store; risk and stale-cache behavior; actual production deployment and rollback readiness; full pytest/CI suites and frontend build.
OBSERVED CODE MISMATCHES TO FIX ONLY AFTER SAFE REPRODUCTION: app.py import-time stale cache overwrites BASE_PRICES; async gainers calls synchronous get_profile; hardcoded C-drive cache directory; unconditional real/verified flags and fixed exchange timestamp in full-market discovery; hardcoded spot map and default spot in chain subscriptions; premium.html submits broker-style /api/v1/placeorder from paper UI with NIFTY default and no option contract identity; WebSocket only handles three index tickers and lacks reconnect; error messages can hide network failures; static performance metrics; untracked local app differs from tracked cloud entrypoint.
FOR EACH ISSUE create record: ID, exact file and line, old code excerpt, replacement code, why, dependencies, precondition, before evidence, exact safe command, expected assertion, actual stdout and exit, after evidence, screenshot, NSE/Dhan quote timestamp, regression results, rollback, status PASS/FAIL/BLOCKED/NOT_VERIFIED. Never fabricate successful output or send live broker orders. Preserve dirty worktree; obtain explicit approval before deployment. Produce a complete command manifest with at least 100 actually executed independent checks, not merely a numbered plan. If the environment blocks a write, report the blocker rather than claim saved.

## ADDENDUM E — COMPLETE MARKET-CLOSED VERIFICATION PROGRAM (2026-11-04)
Do not wait for market hours to test code quality, safety, identity, API correctness, recovery, or UI behavior. Market-closed PASS is not live-market PASS. For each command store timestamp, exact command, exit code, output and SHA256. Separate TEST PASS from AUTHENTICATED LIVE FEED NOT VERIFIED. No real order requests.

### Verified now, with real executed output
- `C:\Genesis_System3_clean\.venv\Scripts\python.exe -m py_compile C:\Genesis_System3_clean\content\app\app.py` => exit 0, no output (syntax PASS).
- `C:\Genesis_System3_clean\.venv\Scripts\python.exe C:\Genesis_System3_clean\reports\latest\ui_recovery\verify_readonly_order_guards.py` => `ENV 5 / 5 ORDER_GUARDS 11 / 11` exit 0; evidence `READONLY_ORDER_GUARDS.json`.
- GET `http://127.0.0.1:8021/api/health` => HTTP 200, response 923 bytes; GET `/api/market/inventory` => HTTP 200, response 1428 bytes. HTTP 200 is transport success, NOT market truth. GET `/api/chain/RELIANCE` was still pending at first observation; check final result separately.
- Earlier inspected code confirms order UI POST route, stale cache override, hardcoded path, profile dependency, three-index-only WebSocket, fixed verified timestamp and hardcoded spots. No fixes claimed.

### Safe offline / market-closed test techniques
1. Use fixture replay of **previously authenticated, timestamped, redacted** Dhan quotes and option-chain JSON. Store source hash, original exchange timestamp, schema version and fixture date; label REPLAY, never LIVE. Assert identical contract ID/expiry/right/strike and no lookahead.
2. Build local read-only fake Dhan server or dependency-injected transport that returns deterministic 200/401/403/429/500, empty JSON, malformed data, timeout, dropped packets and expired tokens. Never use real broker order endpoint. Test exponential backoff and provider quota.
3. Virtual clock with Asia/Kolkata session boundaries: 09:14:59, 09:15:00, 15:29:59, 15:30:00, weekends, exchange holidays, midnight UTC crossing, daylight-independent IST, and late exchange corrections. Assert stale versus market closed versus no data.
4. Fake streaming server in isolated test harness: 100 ms / 1 s / 5 s ticks, duplicate ticks, out-of-order exchange timestamps, silent socket, disconnect/reconnect, heartbeat timeout, browser hidden/resume, packet loss, stale state, backpressure. All data must visibly say SIMULATED/REPLAY.
5. Synthetic 218-symbol universe **for load only**, never represented as real market contracts; replay actual Dhan master to test 218 unique NSE OPTSTK underlyings, option ID uniqueness, expiry mapping, 219 target reconciliation and rename/corporate action edge cases.
6. Replay chain snapshots at t0,t1,t2 with frozen clock and known CE/PE gainers; assert deterministic sorting, change %, OI, volume, missing price, zero previous close, extreme spike, expiry, index/equity grouping, pagination and filters.
7. Test option-chain quota mathematically: for 218 symbols at minimum 3 seconds/request, one expiry each implies >=654 seconds (10m54s), excluding expiry-list calls, retries and processing; this is a planning lower bound, not measured actual throughput. Streaming full chain in subsecond time from polling is not realistic. Use a permitted streaming quote feed for selected contracts where provider supports it.
8. Replay exact-contract paper lifecycle offline in an isolated DB: no real broker adapter, buy/sell, partial fills, duplicates, restart recovery, fees, slippage, risk stop, expiry settlement, P&L and ledger reconciliation. Verify idempotency and source provenance; no fabricated 'market-verified' outcome.
9. Offline browser UI tests: Playwright or equivalent screenshots for desktop/mobile, browser console, network failure, no data, stale, market closed, authenticated replay, reconnect and contract selection. Capture before/after PNG and HAR with redacted tokens. Screenshots must show REPLAY badge for fixture data.
10. Contract tests against current tracked Cloud Run entrypoint, not just untracked local canary; static route diff, OpenAPI schema, request/response schemas, read-only GET smoke, dependency scanning, pip check, lint, AST compile, pytest, frontend build, accessibility, XSS escaping, secret scan, concurrency tests and deploy rollback dry run.
11. Read-only independent market reference after close: NSE/BSE official contract master, circulars, historical EOD or previous verified last-close snapshots, Dhan instrument master and timestamped cached quotes. Moneycontrol public view is supplementary and may be delayed. Do not claim live parity from EOD comparison.
12. Validate storage and operations without market: Cloud Run env flag audit (no secret values), scheduler schedule/paused state, IAM read-only access, durable state availability, single writer lease, job retries, cost cap, audit log provenance and health API. Do not restart production or enable scheduler without approval.

### Exact safe commands to run and save outputs (PowerShell)
`Set-Location C:\Genesis_System3_clean`
`git rev-parse HEAD`
`git status --porcelain`
`git ls-files content/app/app.py dashboard/backend/app.py`
`python -m compileall -q content/app core/brokers/dhan`
`python -m pip check`
`python -m pytest -q tests/test_dhan_single_token_authority.py`
`python -m pytest -q tests/test_br1_dhan_auth_reliability.py`
`python -m pytest -q tests/test_dhan_rotator_forensic_redaction.py`
`python reports/latest/ui_recovery/verify_readonly_order_guards.py`
`python reports/latest/ui_recovery/audit_master_option_coverage.py`
`Select-String -Path content/app/app.py -Pattern 'get_profile\(|VERIFIED_SPOT_MAP|BASE_PRICES\[s\]|exchange_timestamp|chain_dir ='`
`Select-String -Path content/app/templates/premium.html -Pattern 'placeorder|order-symbol|initLiveWebSocket|WebSocket'`
`Invoke-WebRequest http://127.0.0.1:8021/api/health -UseBasicParsing -TimeoutSec 15`
`Invoke-WebRequest http://127.0.0.1:8021/api/market/inventory -UseBasicParsing -TimeoutSec 15`
Use configured Python interpreter, redacted logs and bounded timeout. A failing suite is a finding; never force a green exit code. Run isolated unit tests for broker-order routes without network submission. The agent must create new tests for each missing case above, then run them.

### PASS versus NOT VERIFIED
Offline can prove parsing, data lineage, fail-closed safety, code coverage, deterministic UI updates, recovery and paper accounting. Offline CANNOT independently prove actual Dhan feed entitlement, real exchange-to-UI latency, market-hours refresh, NSE live parity or deployed-cloud real-time accuracy. These require fresh authorized data during an actual session. Keep separate evidence fields for `offline_verified`, `live_market_verified` and `production_deployed_verified`.

### Outputs
Add `11_OFF_MARKET_TEST_MATRIX.csv`, `12_REPLAY_FIXTURE_MANIFEST.json`, `13_STREAM_FAULT_INJECTION.md`, `14_BROWSER_SCREENSHOT_PROOF.md`, `15_LIVE_ONLY_GATES.md` to the original deliverables. Every row must include source, test mode, executed command, observed output, expected output, timestamp, artifact, fix and retest. Do not treat a plan as executed evidence.

## ADDENDUM F — VERIFIED OFFICIAL MARKET-DATA REFERENCES AND CORRECT STREAMING DESIGN
Official source links researched on 2026-11-04:
- NSE official option chain https://www.nseindia.com/option-chain ; BSE official option chain https://www.bseindia.com/markets/Derivatives/DeriReports/DeriOptionchain.html ; SEBI source directory https://www.sebi.gov.in/curation/equity_derivatives.html . Use only authorized access and honor NSE terms; public web pages are not a licensed production feed.
- DhanHQ live WebSocket https://dhanhq.co/docs/v2/live-market-feed/ : binary event-driven ticker/quote/full data; up to 5 connections/user, 5000 instruments/connection, 100 instruments per subscribe message, subject to actual entitlements. Decode binary packet security ID/segment and exchange timestamps. Never put access token in browser URL/log.
- DhanHQ option-chain API https://dhanhq.co/docs/v2/option-chain/ : POST /v2/optionchain and /v2/optionchain/expirylist, 1 request/3 seconds; gives OI, Greeks, volume, bid/ask and LTP for strikes. Separate slow chain snapshot enrichment from fast tick WebSocket; do not use 218 sequential option-chain polls as fast streaming.
- OpenAlgo broker-agnostic WebSocket https://docs.openalgo.in/api-documentation/v1/websockets and architecture https://docs.openalgo.in/developers/design-documentation/authentication-platforms : LTP, Quote and Depth modes, connection pooling and ZeroMQ architecture reference. Compare behavior, do not assume our current WebSocket equals OpenAlgo.
- Zerodha Kite official WebSocket https://kite.trade/docs/connect/v3/websocket/ and market quotes https://kite.trade/docs/connect/v3/market-quotes/ : reference for quote/heartbeat/subscription and exchange timestamp; independent broker comparison requires authorized data access.
- Moneycontrol is supplementary for visible top gainers, not a guaranteed synchronized or exchange-certified feed.

Required architecture: Dhan authenticated WebSocket -> binary decoder -> canonical contract security_id+segment+expiry+strike+right -> timestamped append-only tick log -> bounded hot cache and one durable writer -> authenticated backend stream -> browser per-contract rows; parallel rate-limited Dhan chain snapshots for OI/Greeks and instrument-master refresh. Include reconnect, heartbeat, data gaps, out-of-order/duplicate ticks, stale badges, exchange calendar, p50/p95/p99 end-to-end lag, per-symbol coverage, no-trade distinction. During pre-open show PREOPEN or previous verified close with timestamp; during session show LIVE only with fresh authenticated quote; post-close show LAST VERIFIED CLOSE, not fake changing prices. Match Dhan/NSE/BSE by identical contract and comparable timestamps; Moneycontrol and Kite may lag. A static UI refresh rate is not exchange quote cadence.

Agent MUST verify from docs and actual entitlement which Dhan websocket data modes include each needed option field. Never treat option-chain OI as tick-by-tick if provider updates it more slowly. No real orders. Evidence status for live parity remains NOT VERIFIED until measured.

## ADDENDUM G — MANDATORY ANTI-OMISSION EXECUTION CONTRACT (OWNER DIRECTIVE)
This section overrides vague completion statements. Follow ALL prior addenda A–F. Agent must NOT skip any item, substitute a mock for a real-feed certification, claim a code edit is deployed, or stop after creating plans. Continue autonomous safe work until actual access/approval blocker; log blocked items rather than silently omit.

### Historical failure modes to prevent
- Telegram/notification work distracted from priority Dhan verified data -> equity CE/PE gainers -> correct UI -> prediction/paper evidence. No unrelated feature work.
- Wrong repo or split-brain: C:\Genesis_System3 versus C:\Genesis_System3_clean; local untracked content/app versus cloud tracked dashboard/backend/app.py. Record SHA, branch, dirty state, deployed image digest and actual entrypoint BEFORE changing anything. No mass reset/clean.
- 219-symbol target versus 218 actual NSE OPTSTK underlying master: do not invent missing 219th symbol or claim full coverage.
- Profile HTTP 200 is authentication proof only, NOT live option-chain/streaming proof.
- Stale cache, seeded evidence, fixed timestamp/spot, hardcoded metrics and simulated ticks must never be labeled REAL/LIVE/VERIFIED.
- 100 checks in a Markdown plan are NOT 100 executed commands. Persist per-command receipt with timestamp, command, exit code, actual stdout/stderr, file hashes and pass criteria.
- Do not treat HTTP 200 as content correctness, or local port 8021 as Cloud Run production.
- Do not run a broker order POST for testing, even if paper flags are enabled. Unit-test order route safety with mocks and static analysis only.
- Do not skip browser desktop/mobile screenshots, streaming cadence measurements, API schema/contract identity, missing-data states, failed test suites, cloud-only operations, writer locks, or actual paper ledger proof.
- Do not silently remove or weaken safety guards to make tests green; no production deploy, scheduler enablement, merge or expense without owner approval.

### Mandatory command execution workflow (PowerShell)
Use correct verified repo, Python interpreter and output folder. Save this run manifest first:
`$root='C:\Genesis_System3_clean'; Set-Location $root; $run=Get-Date -Format 'yyyyMMdd_HHmmss'; $out=Join-Path $root ('reports\latest\ui_recovery\runs\'+$run); New-Item -ItemType Directory -Force -Path $out | Out-Null; git rev-parse HEAD | Set-Content (Join-Path $out 'git_sha.txt'); git status --porcelain | Set-Content (Join-Path $out 'git_status.txt'); Get-Date -Format o | Set-Content (Join-Path $out 'started_at.txt')`
Use a safe command runner for each test: log exact command and process exit code, capture stdout/stderr, time duration and result; never overwrite evidence from previous run. Store secrets redacted; do not dump .env, token or full authentication responses.
`$py=Join-Path $root '.venv\Scripts\python.exe'; & $py -m py_compile content\app\app.py; if($LASTEXITCODE -ne 0){throw 'SYNTAX_FAIL'}; & $py -m pip check; if($LASTEXITCODE -ne 0){throw 'DEPENDENCY_FAIL'}`
`& $py reports\latest\ui_recovery\verify_readonly_order_guards.py; if($LASTEXITCODE -ne 0){throw 'SAFETY_FAIL'}`
`$env:PYTHONPATH=$root; & $py reports\latest\ui_recovery\audit_master_option_coverage.py; if($LASTEXITCODE -ne 0){throw 'MASTER_AUDIT_FAIL'}`
`& $py -m pytest -q tests/test_dhan_single_token_authority.py tests/test_br1_dhan_auth_reliability.py tests/test_dhan_rotator_forensic_redaction.py`
Do not ignore pytest failures. Diagnose, fix and rerun; isolate tests from real broker/network/order routes. Review missing modules and test discovery before modifying tests.
`Select-String -Path content\app\app.py -Pattern 'get_profile\(|BASE_PRICES\[s\]|VERIFIED_SPOT_MAP|chain_dir =|exchange_timestamp'`
`Select-String -Path content\app\templates\premium.html -Pattern 'placeorder|order-symbol|initLiveWebSocket|WebSocket'`
`git ls-files content/app/app.py dashboard/backend/app.py`
`Invoke-WebRequest 'http://127.0.0.1:8021/api/health' -UseBasicParsing -TimeoutSec 15`
`Invoke-WebRequest 'http://127.0.0.1:8021/api/market/inventory' -UseBasicParsing -TimeoutSec 15`
`Invoke-WebRequest 'http://127.0.0.1:8021/api/chain/RELIANCE' -UseBasicParsing -TimeoutSec 15`
The GET smoke tests prove only endpoint availability; validate JSON body, freshness, contract identity and provenance separately. If local service is not running, do not start unrelated production processes; use isolated test server only.

### Required gates and deliverables
G0 provenance and repo/deploy source; G1 5/5 safety locks and every broker-write path fail closed; G2 actual instrument master and missing 219th reconciliation; G3 authenticated Dhan quote and chain data; G4 deterministic offline replay and failure injection; G5 fast streaming freshness and per-contract UI; G6 official NSE/BSE and supplementary broker comparisons; G7 paper lifecycle with verifiable ledger; G8 screenshots and UI usability; G9 all relevant test suites, security, cloud-only scheduling and single writer; G10 approved deployment, rollback and independent cloud verification. A gate is PASS only with linked evidence; otherwise FAIL/BLOCKED/NOT VERIFIED. Mark G3/G5/G6 live-market gates NOT VERIFIED when exchange is closed. Offline results must not be promoted to live evidence.

Agent must update `01_100_COMMAND_EVIDENCE.csv`, `08_FIX_AND_REGRESSION_REPORT.md`, `09_PRODUCTION_READINESS.md`, `10_OWNER_STATUS_HINDI.md` and Addendum E's 11–15 artifacts, with one issue row per missing/failed requirement. For every defect: exact path and lines, OLD and NEW snippet, root cause, before evidence, patch, safe command, expected assertion, actual output, retest, screenshot, rollback. Ensure 23-tab/113-check recovery workbook items map to these gates; do not claim Excel closure unless each issue has an evidence receipt. Give owner only a short Hindi status: verified fixes, still failing, blocked and exactly one action if owner approval truly needed.

### Stop/approval rules
Do all safe read-only and offline tests autonomously, and fix verified defects in isolated reviewed branches with minimal changes. Do not modify real broker settings, enable real orders, start paid services, merge to main, deploy to Cloud Run, or enable schedulers without explicit approval. Never expose secrets. On permission errors record exact denied action and least-privilege permission requested. If a command fails, preserve error output and continue independent safe checks; never mark skipped checks PASS.
