## GENESIS_PERMANENT_MEMORY_BOOT_20261112
Before every Genesis turn, read agent_deep_audit/.agents/mission/MASTER_CONTRACT_FINAL.md PART 14, canonical PROGRESS.md and BLOCKERS.md, and last pushed SHA. Resume pending work; do not restart. PART 14 is the latest source-truth and continuation instruction. No website scraping; source outage is not market closure. Keep permanent PAPER locks and separate cloud-mutation approval.


## OWNER_NSE_DHAN_LIVE_CHECK_20261112 - current owner instruction

- Always check the actual current market using official NSE https://www.nseindia.com/
  and authenticated Dhan read-only market data. Never infer LIVE or market ON/OFF
  solely from weekday, local time, static calendars, HTTP 200, cached files or old reports.
- Verify NSE segment/session status, exchange timestamp, holidays, Muhurat and special
  sessions; inspect corporate actions before interpreting price jumps. Cross-check Dhan
  packet timestamps and same-instrument identity with NSE. Capture UTC and IST.
- LIVE requires fresh market packets (age <=60 seconds), valid positive price and
  independently checked clocks within 5 seconds. Retrieval time is not exchange time.
  A stale page that says Open is STALE, not evidence of current market status.
- Missing, denied, expired, stale or conflicting sources => UNKNOWN/UNVERIFIED or STALE;
  show the reason, never assume market closed or invent prices or green readiness.
- Dhan reads only: never call order routes or auto-renew tokens during a check.
  Do not print secrets. Stop on authentication/rate-limit errors; no retry hammering.
- Canonical mission/state: agent_deep_audit/.agents/mission and state. Other copies
  are OLD_IGNORE_DO_NOT_USE. Preserve historical evidence; do not import old PASS as proof.
- Latest owner permits autonomous discovery, backup, fixes, tests and safe branch push.
  Continue small batches; separate explicit YES still required for deployment, billing,
  IAM, secrets and deletion. No real orders. No unattended-monitoring claim without proof.

# GENESIS SYSTEM3 - MASTER CONTRACT FINAL V1
Version: 2026-11-12 FINAL - LOCKED - NO MORE CHANGES WITHOUT OWNER YES
Owner: ADMIN - Navi Mumbai
Temporal Marker: SYSTEM3_TEMPORAL_TRUTH_V1
Authority: This file + docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md + docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md + AGENTS.md
Rule: If any other file disagrees with this file, THIS FILE WINS + Owner chat YES wins over all files.
Multi-Verified: 4 times - Past History + 4 MD Files + World Best + Anti-Cheat Check

PART 0 - FUTURE ME OWNER KO KUCH BOLNE KI JARURAT NAHI - AUTO RULE

- Agent will NOT ask Owner for small decisions. Agent will follow this file.
- Agent will STOP only for: P0 FAIL, Secret Leak, Live Trading Risk, Deploy Request, Money / Billing / IAM change.
- For all other things, Agent will: Backup -> Fix -> Test -> Push -> Report in 5 lines -> STOP and wait for CONTINUE.
- Owner will only say: CONTINUE / YES / NO / STOP. Nothing else needed.

PART 1 - SINGLE TRUTH - 40 COPIES KA JAAL BAND

CANONICAL - ONLY THESE 4 PATHS ARE TRUTH. REST ARE FAKE / OLD / TEMP:
1. GEMINI.md: C:\Genesis_System3_clean\GEMINI.md
2. OWNER_GOALS.md: C:\Genesis_System3_clean\agent_deep_audit\.agents\mission\OWNER_GOALS.md
3. EVIDENCE: C:\Genesis_System3_clean\agent_deep_audit\.agents\state\INDEPENDENT_VERIFICATION.csv
4. PROGRESS: C:\Genesis_System3_clean\agent_deep_audit\.agents\state\PROGRESS.md

BANNED - NEVER READ / NEVER WRITE:
- C:\Users\ADMIN\AppData\Local\Temp\... - Temp trash
- C:\temp\... - Pytest temp
- *.bak / *.bak_master / *.bak_forensic - Backup old
- C:\Genesis_System3\ - Old folder
- C:\Genesis_System3_paper_verify\ - Old folder
- C:\Users\ADMIN\Genesis_System3_repo\ - Old repo
- C:\Antigravity_Audit\ / C:\Users\ADMIN\antigravity\ - Audit cache
- C:\Genesis_System3_clean\.agents\... - OLD .agents, IGNORE. Only agent_deep_audit\.agents\ is truth.
- C:\Genesis_System3_clean\agent_control_audit\... - Sub-scope only, Root wins.

IF MULTIPLE FILES FOUND: STOP. Use Canonical only. Do NOT pick newest by date. Date != Truth. Canonical Path = Truth.
IF CANONICAL NOT FOUND: STOP, BLOCKER: CANONICAL_NOT_FOUND + Full Path, Wait for Owner. Do NOT use backup.

PART 2 - ENVIRONMENT CHAIN - LAPTOP = GITHUB = CLOUD = UI

1. LAPTOP - DEV ONLY: C:\Genesis_System3_clean - Writing code here is NOT proof.
2. GITHUB - SOURCE OF TRUTH: Every DONE MUST be Committed + Pushed to approved main + SHA + Commit URL. Unpushed = NOT DONE.
3. GOOGLE CLOUD - REAL RUNTIME: Intended production GCP system3-openalgo-safe / asia-south1. Currently NO deployment certified until fresh re-verified.
4. UI - FINAL PROOF: Owner must see it in Dashboard UI on Cloud URL. If UI does not show, claim REJECTED.

FLOW: Laptop Fix -> GitHub Push -> Cloud Deploy (ONLY after Owner YES) -> UI Verify 3 Times. Skip 1 step = NOT DONE.

PART 3 - UI IS PROOF - GOLDEN RULE - GOOGLE / META STYLE

For ALL UI / UX tasks: Backend PASS is NOT enough. API JSON is NOT enough. Localhost is NOT enough.
REQUIRED: Cloud URL Opened + Screenshot Dated Today + Cloud URL Visible in Screenshot + Time Visible + Value in UI = Value in Backend.
MULTI-TIME UI VERIFY 3 TIMES: 1. After Fix, 2. After GitHub Push, 3. After Cloud Deploy.
REJECTED: "Backend works, UI will work" / "Localhost works" / "Old Screenshot" / "Code correct, UI not checked"
ACCEPTED: "Cloud URL opened, UI shows X, Screenshot today, Backend Y matches, SHA Z"

PART 4 - DEPLOY RULE - CONFLICT FIX - OWNER YES REQUIRED

Owner Consent: Autonomous GitHub fixes, tests, CI, read-only GCP verification ONLY.
Agent CAN: Fix code, Push GitHub, Run tests, Read Cloud status.
Agent CANNOT: Deploy, Billable build, Mutate Cloud Run / Scheduler / IAM / Secrets / Billing / Artifacts WITHOUT separate explicit Owner YES in chat.
Silence = NO. No reply = NO.
Process: Prepare Deploy -> Write DEPLOY_REQUEST.md (What, SHA, Risk, Rollback Plan, Previous Good SHA) -> STOP -> Wait Owner YES -> Deploy -> UI Verify 3x.
No Auto-Deploy. No Unapproved Auto-Deployment.

ROLLBACK - GOOGLE SRE STYLE:
Every deploy MUST have Rollback Plan. If deploy FAILS or UI shows error, ROLLBACK immediately to Previous Good SHA. Do NOT fix on Live Cloud. Write BLOCKER: DEPLOY_ROLLED_BACK + Reason.

PART 5 - SAFETY LOCKS - NEVER BREAK - FINANCE GRADE

PERMANENT LOCKS: ANALYZE_MODE=1, PAPER_MODE=1, LIVE_TRADING_ENABLED=0, SYSTEM3_LIVE_TRADING_ALLOWED=0, AUTO_EXECUTE_TRADES=0, LIVE_ORDER_AUTHORITY=0, ORDER_PLACEMENT_ALLOWED=false
No real orders, no order-shaped production tests, no broker secret payloads, no service-account JSON keys.
If any lock wrong: STOP, BLOCKER: SAFETY_LOCK_BROKEN.
Broker Authority: Dhan ONLY. Render / Angel-era = Historical, Non-Authoritative.
Dhan Proof is NOT GET 200. Dhan Proof = Auth + Session ID + Live Packet + Timestamp + UI Match + Freshness < 60 sec.

SECRET LEAK - META STYLE:
If secret / token / key / JSON appears in log / evidence / GitHub / UI / Screenshot: STOP. Delete line, Rotate secret, Notify Owner in 1 line: SECRET_LEAKED + Where + What Rotated. Hiding leak = VIOLATION.

PART 6 - EVIDENCE - 15 POINTS - MISSING 1 = UNVERIFIED

BANNED SCRIPT: scripts/run_1872_acceptance_pipeline.py - NEVER use as proof. Its CSV/JSON = Historical Claims Only. Preserve, Do NOT edit/delete/use.
BANNED: evidence_gate.py if it is same as above. Use ONLY this contract.
For Each Check ID, retain ALL 15:
1. UTC + IST both. Format: 2026-11-12 10:30:00 IST / 05:00:00 UTC. Only 1 timezone = REJECTED.
2. Workspace: C:\Genesis_System3_clean
3. GitHub SHA + Branch + Push Proof + Commit URL
4. Cloud Revision + Cloud URL + Deploy Time
5. Command / Test Path + Exit Code (0=pass, non-zero=fail, Full Unedited Log)
6. Expected vs Observed
7. Raw Source Packets / Sanitized Logs with Timestamps (Append-Only, No Edit)
8. Artifact URI + Hash + Reproduction in 1 Click
9. Reviewer Distinct from Generator (Second Method / Second Run / Owner). Same Name = REJECTED.
10. UI Proof (For UI tasks): Cloud URL + Dated Screenshot + URL+Time Visible + Backend Match + 3-Time Check
11. GitHub + Cloud Console URL
12. DATA LABEL: LIVE / CLOSED / REPLAY / DELAYED / SIMULATION. No Label = REJECTED. Replay as Live = FRAUD.
13. FRESHNESS: Live data max age 60 sec. Older = STALE, not LIVE. Stale as Live = REJECTED.
14. DUMMY CHECK: Price/OI/Volume NOT 0 / 999 / 9999 / 12345 / Hardcoded / Same value 10+ ticks / Yesterday value. Dummy = FAIL.
15. TIME SYNC: System vs NSE/BSE vs Broker within 5 sec. Mismatch > 5 sec = BLOCKED.

PASS = All 15 + Independent Repeat Pass + UI Match + GitHub Pushed + Cloud Deployed + Fresh + Not Dummy + Correct Label.
FAIL = Actual Failed Assertion. FAIL cannot be renamed to BLOCKED.
BLOCKED = ONLY: Tools Down (Screenshot), Auth Expired (Log), Market Closed (Calendar Proof), Entitlement Limit (Broker Error). Without Proof, BLOCKED = FAIL.
UNVERIFIED = Missing Proof. Code Statement = UNVERIFIED. Narrative = UNVERIFIED. Old Screenshot = UNVERIFIED.

WHAT IS NOT PROOF:
- Self Narrative != Evidence. SHA256 != Real Price Proof. GET 200 != Broker Session. Localhost != Cloud. Backend Log != UI Proof.
- 1 Screenshot = 1 Check + 1 Time. Same Screenshot for 2 Checks = Both REJECTED.
- Logs Append-Only. Edited Log = INVALID. Evidence Row Once Written, Do NOT Edit. Correction = NEW Row + Old SHA + New SHA + Reason + Time.
- 100% Match / 100% Win Rate = REJECTED until Sample Size + Method + Live/Backtest Label shown.

EVIDENCE IMMUTABILITY: Evidence file committed to GitHub after each batch. Uncommitted Evidence = NOT COUNTED. SHA changes without commit = INVALID.

PART 7 - SCOPE - 52 DOMAINS / 624 CONTROLS / 1872 TESTS - TOTAL, NOT TODAY

Total Scope is 52 domains, 624 controls, 1872 FUNCTION/FAILURE/INDEPENDENT tests. NOT today's task.
Today Task = MAX 5 files per turn. After 5, update PROGRESS.md, STOP, Wait CONTINUE.
1 File = Backup -> Check -> Fix -> SAVE -> GitHub Push -> Cloud Check (Read-Only) -> UI Check -> Mark DONE in TASK_LIST.md -> Next File.
If 1 P0 FAILS: STOP, Write BLOCKERS.md: File, Test, Expected, Actual, SHA. Do NOT go to next file.
If same error 3 times: STOP loop, LOOP_BLOCKER. Do NOT retry same fix.
If TASK_LIST.md says ALL DONE: Write ALL DONE and STOP. Do NOT invent new work.

PRIORITY - GOOGLE OKR STYLE:
P0 - SAFETY + TRUTH: Paper only, Dashboard only verified data, No hardcoded green, No dummy prices.
P1 - CORE: Universe, Feeds, Options CE/PE, Paper P&L.
P2 - INTELLIGENCE: Breadth, Movers, Scanners, Predictions, Alerts.
P3 - OPERATIONS: Cloud, CI, Backup, Observability.
Do NOT touch P1 before P0 100% DONE.

MANDATORY SCOPE:
Universe: All exchange-eligible, Token/ISIN, Sector/Index, Expiry/Strike/Lot, Suspended/Expired filter, Coverage denominator + Exclusions.
Feeds: Source Identity, Market Timestamp, Sequence, Latency, Freshness, Live/Closed/Replay/Delayed, Loss/Reconnect, Depth, Reconciliation.
Options: Full CE/PE Chain, LTP/Bid/Ask/Vol/OI/OI-Change, IV/Greeks/PCR, Top Movers, Liquidity Gate, Per-Contract Provenance, No Dummy Prices.
Intelligence: Breadth, Movers, Unusual Volume, Heatmaps, Scanners, Symbol Explorer, Alerts, Chart Controls.
Predictions: Timestamped Pre-Outcome, Matured Outcomes, Walk-Forward, Leakage Test, Sample Size, Calibrated Metrics, Benchmark, Model Version, Drift Gate.
PAPER Trades: No Real Orders, Deterministic Lifecycle, Fill/Slippage/Cost Rules, Positions, Receipts, Exact P&L Reconciliation, Safe Failure Tests.
Operations: Cloud Runtime, API Contracts, Rate Limits, Observability, Startup/Recovery, CI, Revision/SHA, Security, Backup, Blocked/Unknown, Owner Signoff.
Dashboard: Every number bound to verified backend OR marked Simulation / Unavailable / Stale / Unverified. Never hardcode green.

P&L EXACT MATCH - FINANCE GRADE:
Realized + Unrealized + Costs + Slippage must match to 0.01. Mismatch > 0.01 = FAIL. No rounding excuse.
Every closed trade MUST have Receipt: Entry, Exit, Qty, Price, Cost, Slippage, Net P&L, SHA, Time.
QC FAIL Rule: QC FAIL must be FIXED, NOT auto-cleared. Auto-clearing QC FAIL = BANNED.

PART 8 - PAST HISTORY - ALL 20 ISSUES FIXED - WORLD BEST COMPARE

1. Old CSV/JSON as Proof -> BANNED, Historical Only. [Google: Evidence must be fresh]
2. 1872 Tests at Once -> BANNED, Max 5 per turn. [Google: Small batch]
3. Wrong Path -> Single Path Rule. [Meta: Single Source of Truth]
4. Owner YES Assumed -> Silence = NO. [OpenAI: Human-in-Loop]
5. Continue on FAIL -> STOP on P0 FAIL. [Amazon: Stop on Fail]
6. Laptop Code = DONE -> Laptop+GitHub+Cloud+UI = DONE. [Google: End-to-End]
7. Backend PASS = UI DONE -> UI IS PROOF. [Meta: User-Visible Proof]
8. Old Screenshot Reuse -> 1 Screenshot = 1 Check. [OpenAI: Fresh Evidence]
9. Replay as Live -> Label Required, Fraud if mislabelled. [Finance: Label]
10. Dummy Price -> Dummy Check. [Finance: No Dummy]
11. Stale as Live -> Freshness 60 sec. [Google SRE: Freshness SLO]
12. Self-Review -> Reviewer != Generator. [Meta: Independent Review]
13. Edited Logs -> Append-Only. [Amazon: Immutable Audit]
14. Timezone Confusion -> IST + UTC Both. [Google: Dual Time]
15. BLOCKED Misuse -> BLOCKED needs proof, else FAIL. [Microsoft: Strict Status]
16. Deploy Without Approval -> Owner YES Required. [Google: Approval Gate]
17. Secret Leak Hidden -> STOP + Rotate + Notify. [Meta: Leak Protocol]
18. Market Closed Loop -> Calendar Check + BLOCKED. [Exchange: Calendar]
19. API Hammering -> Exponential Backoff 30/60/120, Max 3 Retries. [OpenAI: Backoff]
20. No Backup -> Backup Before Fix, .bak with Date. [Amazon: Backup First]
21. No Rollback -> Rollback Plan Mandatory. [Google SRE: Rollback]
22. P&L Rounding -> 0.01 Exact Match. [Finance: Exact]
23. Long Logs -> 5-Line Report Only. [Top Company: Executive Summary]
24. QC FAIL Auto-Clear -> BANNED, Must Fix. [Quality: No Hiding]
25. 100% Claims -> Sample Size + Method Required. [Science: No 100%]

PART 9 - OPERATIONAL RULES - DAILY

MARKET CLOSED RULE: Before Live check, check NSE/BSE Calendar + IST. If CLOSED: Mark BLOCKED: MARKET_CLOSED + Calendar Proof. Do NOT loop, Do NOT retry every 10 sec.
RATE LIMIT RULE: If Dhan returns 429/401/500: STOP hitting. Backoff 30s -> 60s -> 120s. Max 3 retries. After 3, BLOCKER: API_RATE_LIMITED. Never hammer.
BACKUP RULE: Before edit ANY file: Copy to FileName_2026-11-12_HHMM.bak. Before delete: Move to backup, NOT permanent delete without Owner YES. No Backup = Do NOT start fix.
BATCH RULE: Max 5 files / 5 checks per turn. After 5, STOP.
LOOP RULE: Same error 3 times = LOOP_BLOCKER, STOP.
PROGRESS RULE: PROGRESS.md is SUMMARY ONLY, NOT Evidence. Real Evidence ONLY in INDEPENDENT_VERIFICATION.csv. Any FIX in PROGRESS without 15 points = UNVERIFIED.
HISTORICAL FILES: GENESIS_1872_MASTER_CHECKLIST.csv + Old Evidence JSONs = Historical Claims Only. Preserve, Do NOT edit/delete/use as proof.

PART 10 - OWNER REPORT - 5 LINES ONLY - AFTER EVERY BATCH

Agent MUST report in this exact format, no 500-line log:
1. DONE: [Files + GitHub SHA]
2. CLOUD: [URL + Revision OR Waiting for Owner YES]
3. UI: [Verified YES/NO + Screenshot Date]
4. BLOCKER: [None OR File + Reason]
5. NEXT: [Next 5 Files OR Waiting for CONTINUE]
If Agent sends long log, Owner will say: SEND 5-LINE REPORT.

PART 11 - DONE DEFINITION - FINAL

1 File = DONE only when: Syntax Pass + P0 Pass + GitHub Pushed + Cloud Ready (or Waiting YES) + UI Verified (if UI task) + Saved + Logged + Backup Done.
1 Domain = DONE only when ALL its P0 tests have 15-point proof.
Project = DONE only when P0 = 100% DONE + INDEPENDENT_VERIFICATION.csv complete + Cloud UI shows all P0 green with real data + Owner YES.
No model is sole controller; Issue #188 is context, not proof. Issue number != Proof. Fresh evidence = Proof.


# Genesis System3 — permanent owner mission
Version: 2026-11-12 V3 - FINAL - UI IS PROOF
Authority: root AGENTS.md, root GEMINI.md, docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md, and agent_policy.yaml. This document does not supersede those rules.
Supersedes: OWNER_GOALS.md Version 2026-11-02, V2

## 1 YEAR LESSON - WHY AGENT FAILED BEFORE - READ FIRST
In last 1 year, Agent failed for same 6 reasons. NEVER repeat them:
1. NEVER treat old CSV / old JSON as proof. Old files are CLAIMS, not proof.
2. NEVER try to do 1872 tests at once. Agent looped and finished 0.
3. NEVER guess path. Only 1 path is truth (see Section 6).
4. NEVER assume Owner YES. If Owner did not say YES, it is NO.
5. NEVER continue on FAIL. On P0 FAIL, STOP, write BLOCKER, wait.
6. NEVER say DONE on laptop code only. If UI does not show it, it is NOT DONE.

## Ultimate goal
Build and independently verify a cloud-first Indian market-intelligence platform with authentic authorized exchange/broker data, complete dynamically discovered NSE/BSE cash/indices/F&O coverage, actionable CE/PE intelligence, credible prediction evaluation, risk controls, reproducible paper trading, a truthful dashboard, and auditable operational evidence. NEVER promise profits.
Final Product = Full Software, not code files. It must run on Google Cloud and be usable from UI by Owner.

## ENVIRONMENT CHAIN - LAPTOP = GITHUB = GOOGLE CLOUD = UI
This is the ONLY flow. No step can be skipped.
1. LAPTOP - DEV ONLY: C:\Genesis_System3_clean - Agent writes code here. This is NOT proof.
2. GITHUB - SOURCE OF TRUTH: Every DONE file MUST be committed + pushed to GitHub with SHA. If not pushed, it is NOT DONE. No local-only DONE.
3. GOOGLE CLOUD - REAL RUNTIME: Code MUST deploy / run on Google Cloud. If it only runs on laptop, it is NOT DONE. Cloud URL + revision + SHA must be recorded.
4. UI - FINAL PROOF: Owner must see it working in Dashboard UI. If UI does not show it, claim is REJECTED.

RULE: Laptop DONE -> GitHub Pushed -> Cloud Deployed -> UI Verified. Skip 1 step = NOT DONE.

## UI IS PROOF - GOLDEN RULE - NO UI = NO CLAIM
For ALL UI / UX dependent tasks, this rule overrides everything:
- Dashboard number, chart, CE/PE chain, P&L, scanner, alert, heatmap - if it is not VISIBLE and CORRECT in UI, it is UNVERIFIED.
- Backend code passing test is NOT enough for UI tasks.
- API returning JSON is NOT enough for UI tasks.
- Screenshot / Screen Recording / Live UI check is MANDATORY for UI tasks.
- Agent MUST do MULTI-TIME UI VERIFY: Check UI 3 times - 1. After fix, 2. After GitHub push, 3. After Cloud deploy. All 3 must match.

REJECTED CLAIMS:
- "Backend works, UI will work" = REJECTED
- "Code is correct, UI not checked" = REJECTED
- "Localhost UI works, Cloud UI not checked" = REJECTED
- "Screenshot is old" = REJECTED, screenshot must be dated today + with Cloud URL visible

ACCEPTED CLAIM:
- "Cloud URL opened, UI shows X, Screenshot dated today, Value matches backend Y, SHA = Z" = ACCEPTED

## GITHUB RULE - ALL TASKS
- Every task = 1 Branch OR 1 Commit with clear message: [P0/P1] + File + What fixed + SHA.
- No commit without running syntax check + P0 test.
- No force push. No deleting history.
- After push, record in INDEPENDENT_VERIFICATION.csv: Repo, Branch, Commit SHA, Files changed, Cloud Revision.
- If GitHub push fails, STOP. Write BLOCKER: GITHUB_PUSH_FAILED. Do NOT say DONE on local.

## GOOGLE CLOUD RULE
- Cloud is the ONLY production runtime. Laptop localhost is for testing only.
- Every deployment must record: Project, Service, Revision, URL, SHA, Deploy Time.
- If Cloud deploy fails / Cloud URL shows old version / Cloud shows error, task = BLOCKED, not DONE.
- Never expose secrets in GitHub / Cloud logs / UI. Use Secret Manager only.

## PRIORITY - TOP COMPANY RULE - GOOGLE OKR STYLE
Agent will work ONLY in this order. Do NOT touch P1 before P0 is 100% DONE.
- P0 - SAFETY + TRUTH: PAPER trades = no real orders, Dashboard shows only verified data, No hardcoded green readiness, No dummy market prices.
- P1 - CORE: Universe, Feeds, Options CE/PE chain, Paper P&L reconciliation.
- P2 - INTELLIGENCE: Breadth, Movers, Scanners, Predictions, Alerts.
- P3 - OPERATIONS: Cloud runtime, CI, Backup, Observability.
If P0 is not DONE, P1/P2/P3 = NOT STARTED, even if code exists.

## Mandatory scope
- Universe: all exchange-eligible instruments within authorized broker entitlements; current instrument masters, token/ISIN identity, sector/index membership, expiry, strike, lot sizes, filters for suspended/expired instruments, coverage denominator and exclusions.
- Feeds: authenticated source identities, market timestamps, sequence continuity, latency, freshness, live/closed/replay/delayed distinctions, loss and reconnect behavior, depth integrity, reconciliation with independent source.
- Options: complete CE/PE chain, live LTP/bid/ask/volume/OI/OI-change, IV/Greeks/PCR, top CE and PE movers, liquidity gating and per-contract provenance; no dummy market prices.
- Intelligence: breadth, movers, unusual volume, sector heatmaps, scanners, searchable symbol explorer, alerts and real-time chart controls.
- Predictions: timestamped pre-outcome forecasts, matured outcomes, walk-forward and leakage testing, sample sizes, calibrated metrics, benchmark comparison, model version, drift gates.
- PAPER trades: no real orders; deterministic paper order lifecycle, reproducible fill/slippage/cost rules, positions, closed trade receipts, exact realized/unrealized net P&L reconciliation and safe failure tests.
- Operations: resilient cloud-only runtime, API contracts, rate limits, observability, startup/recovery, CI, revision/SHA provenance, security, backup, blocked/unknown and owner signoff.
- Dashboard: every displayed statistic bound to a verified backend source or explicitly marked simulation, unavailable, stale or unverified; never hardcode green readiness.

## Acceptance criteria - EVIDENCE FIRST - META / OPENAI STYLE
Scope is 52 domains, 624 base controls, 1872 FUNCTION/FAILURE/INDEPENDENT tests. This is TOTAL scope, NOT today's task. Today task = max 5 files per turn.
A PASS requires ALL 9, missing 1 = UNVERIFIED:
1. Executed and reproducible observation (run command + output)
2. Dated nonempty raw artifacts (file exists, size > 0, date = today)
3. Expected-versus-actual assertion (what should happen vs what happened)
4. Relevant source file + SHA/digest
5. A genuine independent check/reviewer (second run / second method, NOT same code)
6. Recorded conclusion in INDEPENDENT_VERIFICATION.csv
7. No hardcoded PASS / No edited old proof
8. GitHub Commit SHA + Pushed proof
9. UI Verification (for UI tasks) OR Cloud URL Verification (for non-UI tasks) - 3-time check

A source code statement is NOT execution proof. A comment saying "works" is NOT proof. Absent proof stays UNVERIFIED/BLOCKED. All critical P0 and owner gates must pass before a production-paper readiness verdict.

## SINGLE SOURCE OF TRUTH - AMAZON STYLE
- ONLY TRUTH FILE: agent_deep_audit\.agents\state\INDEPENDENT_VERIFICATION.csv
- HISTORICAL CLAIMS ONLY, NEVER USE AS PROOF: root GENESIS_1872_MASTER_CHECKLIST.csv and old evidence JSONs. DO NOT edit, DO NOT delete, DO NOT copy from them. Only read to know what was claimed before.
- If 2 files disagree, INDEPENDENT_VERIFICATION.csv wins.

## SINGLE PATH RULE - FIX FOR 1 YEAR PATH ERROR
- ALL state files are ONLY here: C:\Genesis_System3_clean\agent_deep_audit\.agents\
- IGNORE root .agents\ folder. It is old / duplicate. Do NOT read/write there.
- If file not found, STOP and report BLOCKER: FILE_NOT_FOUND + full path. Do NOT guess new path.

## BATCH + STOP RULE - ANTI-LOOP - WORLD TOP RULE
- 1 Turn = MAX 5 files. After 5 files, update PROGRESS.md and STOP. Wait for Owner CONTINUE.
- 1 File = Backup -> Check -> Fix -> SAVE -> GitHub Push -> Cloud Check -> UI Check -> Mark DONE in TASK_LIST.md -> Next file.
- If 1 P0 test FAILS: STOP immediately. Write to BLOCKERS.md: File, Test, Expected, Actual, SHA. Do NOT go to next file.
- If same error repeats 3 times: STOP loop. Write LOOP_BLOCKER. Do NOT retry same fix.
- If TASK_LIST.md says ALL DONE, write ALL DONE and STOP. Do NOT invent new work.

## APPROVAL RULE - HUMAN-IN-THE-LOOP
Cloud changes, secret rotation, IAM, billing, deployment, delete, or opening live-trading authority require separate explicit Owner YES in chat.
- Silence = NO. No reply = NO. Agent guessing YES = VIOLATION.
- Permanent live order restriction always applies unless a future explicit owner directive and reviewed safety process authorize otherwise.

## DONE DEFINITION - FINAL
1 File = DONE only when: Syntax passes + P0 test passes + GitHub Pushed + Cloud Deployed + UI Verified (if UI task) + Saved + Logged.
1 Domain = DONE only when ALL its P0 tests have 9-point proof above.
Project = DONE only when P0 = 100% DONE + INDEPENDENT_VERIFICATION.csv complete + Cloud UI shows all P0 green with real data.