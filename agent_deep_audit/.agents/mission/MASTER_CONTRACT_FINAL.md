
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


PART 13 - CONTINUE LOOP V3 - AGENT WILL NOT STOP AFTER REPLY - FINAL FIX 2026-11-12
Reason: Owner gave CONTINUE, Agent replied once and stopped. Loop broke because Agent asked open question.


### 13.1 CONTINUE KA MATLAB - NEW DEFINITION
- CONTINUE = NOT 1 turn. CONTINUE = Keep working until ALL 5 files DONE or P0 BLOCKER comes.
- CONTINUE = Agent will do: SELF-FIND -> FIX 5 files -> VERIFY -> 5-LINE REPORT -> AUTOMATICALLY START NEXT 5 FILES - WITHOUT WAITING.
- Agent will STOP only for: P0 FAIL after 3 fixes, Secret Leak, Deploy Needs YES, Billing/IAM/Delete, Live Trading Risk, Owner says STOP.
- Agent will NEVER STOP just because it sent a report. Report is NOT stop. Report is checkpoint.

### 13.2 AGENT WILL NEVER ASK OPEN QUESTION - DEFAULT ACTION RULE - GOOGLE / META STYLE
- BANNED: "Kya karu?" / "Kya restore karun?" / "Kya aage badhu?" / "Permission du?"
- ALLOWED: Agent will propose Default Action + Proceed.
- Format: "BLOCKER found: [Tracker missing]. DEFAULT ACTION: I will restore from [Previous Good SHA] in next turn. If you say NO in 1 min, I will STOP. Else I will proceed."
- If Owner does NOT reply in next turn, Agent will assume DEFAULT ACTION = YES and proceed. Silence = Proceed for non-dangerous fix. Silence = NO ONLY for Deploy / Billing / IAM / Delete / Live.
- In screenshot case: Tracker missing = Non-dangerous. Agent should NOT have asked. Agent should have said: "I will restore tracker from previous good SHA, proceeding."

### 13.3 LOOP COMMAND - OWNER WILL USE THIS ONE COMMAND ONLY
- Owner will NOT say just "CONTINUE" alone. Owner will say:
  "CONTINUE LOOP - Do NOT ask, Do NOT stop after report, Do Default Action and proceed to next 5 files. Stop ONLY for P0 / Deploy / Secret / Billing. Send 5-line report after every 5 files and auto-continue."
- This ONE command = Full Autopilot Loop. Agent must repeat it internally after every 5 files.

### 13.4 BANNED SCRIPT - DO NOT READ AS PROOF - AGAIN
- scripts/run_1872_acceptance_pipeline.py - Its line "FULL ACCEPTANCE CERTIFIED. All 1,872 PASS" is BANNED CLAIM. Do NOT read it, Do NOT quote it, Do NOT use it as proof.
- If Agent sees this file, Agent MUST write: "BANNED SCRIPT FOUND - Ignoring its PASS claim, using fresh 15-point proof only."
- Agent approved to run Get-Content on this file = APPROVAL IS REVOKED. Do NOT auto-approve this file.

### 13.5 IF AGENT STOPS AFTER 1 REPLY - SELF-RESTART RULE
- If Agent stops after 1 reply without P0/Deploy/Secret/Billing reason, that is VIOLATION: LOOP_BROKEN.
- On next CONTINUE, Agent MUST first write: "LOOP_BROKEN fixed, resuming from [Last SHA + Last File], not restarting from zero."
- Agent will NOT restart from zero. Agent will resume from last saved SHA + last file.


## Current continuation - 2026-11-12T06:49:03.832600+00:00 UTC
PART 14 saved once and GitHub read-back verified at 2eb65f90acc832b21fd07794f3ce303b7c2c39d8 (blob 292f298a5f141e23916aebfbae3e556d0b25625d). Startup pointers added to read it every Genesis turn.
Follow-on branch: fix/source-failure-ui-truth-20261112, based on that SHA; no restart of original mission.
Implemented in small source batches: unknown startup instead of browser clock; source outage no longer CLOSED; 60-second STALE threshold; desktop/mobile/session labels preserve UNKNOWN; special-session transport reads source status. Node behavior contract is now a mandatory prebuild gate.
Validation: 31 targeted Python regressions, TypeScript typecheck, production build and all prebuild behavior contracts executed successfully. Browser visual proof is NOT PASS: attempt 1 HTTP-only isolation admitted a WebSocket session update and failed the assertion; attempt 2 isolated both transports but hung; attempt 3 added explicit 15s limits/progress output and also hung. Stopped only verified test process trees. LOOP_BLOCKER_BROWSER_SIMULATION: no fourth retry; external/tool-state investigation required before visual acceptance. Product UI remains UNVERIFIED.
Fresh source scan at 2026-11-12 12:08:45 IST / 06:38:45 UTC: official NSE calendar/session JSON APIs HTTP 200; NSE session packet age 45.58s, Dhan quote age -0.42s (within 5s tolerance); both source age checks fresh. Independent clock and synchronized UI/price parity remain UNVERIFIED. No website scraping, token renewal or order call in source probe.
Cloud read-only: serving revision 00131-2md unchanged; health HTTP 200. Local summary arithmetic matches 0.01 only, not cost/slippage/cloud receipt proof. Disk 77.38%; managed token expiry, option expiry, quotas, dependency vulnerabilities and corporate actions not fully verified. No production certification.
Correction: earlier main auto-deploy warning came from divergent local checkout. The fetched approved main workflow inventory does NOT contain cloud-run-auto-deploy.yml. Separate explicit owner deployment approval remains mandatory regardless.
Next: review pushed follow-on draft and resolve browser tooling LOOP_BLOCKER; do not deploy or claim UI PASS. Roles: PM resumed, Developer fixed source truth, Tester checked behavior/build, Auditor/Critic withheld visual and production acceptance, Risk kept PAPER/order restrictions.

PART 14 - PERMANENT MEMORY - NEVER FORGET - TOP COMPANY RULE - 2026-11-12 LOCKED:

1. USER PROFILE: User ko coding, computer, path, folder kuch nahi pata. User sirf READY PRODUCT chahta hai. User se kabhi path mat pucho. Tum khud dhoondho, khud fix karo, khud verify karo. User sirf CONTINUE LOOP / YES / NO / STOP bolega.

2. NEVER ASSUME - ALWAYS CHECK FROM NSE + DHAN - PERMANENT:
- Kabhi assume mat karo. Hamesha NSE Calendar + Dhan se check karo.
- NSE se data na aana = MARKET CLOSED NAHI HAI. NSE se data na aana = DATA SOURCE DOWN HAI.
- MARKET CLOSED sirf tab bologe jab NSE Calendar me aaj Holiday / Weekend / Special Closed likha ho. Calendar Proof ke bina CLOSED bolna = VIOLATION.
- Aaj ka example yaad rakho: 12/11/2026 ko User ne nseindia.com pe LIVE check kiya, Market OPEN tha, lekin tumne STALE data ko CLOSED bol diya tha. Future me ye galti kabhi mat karna.

3. TOP COMPANY JAISA KARO - BLOOMBERG / ZERODHA / GOOGLE SRE / META:
- 3 SOURCE FALLBACK: Pehle NSE, NSE fail to Dhan, Dhan fail to BSE. Teenon fail to bologe DATA SOURCE DOWN, kabhi MARKET CLOSED nahi bologe.
- LABEL SAHI: Data <60s = LIVE. Data >60s = STALE - UI pe likhoge "STALE - Last Update [Time], Market OPEN hai". CLOSED sirf Calendar Holiday pe.
- NSE WEBSITE SCRAPE MAT KARO: nseindia.com bot ko block karta hai. User browser me dekh sakta hai, tum code se nahi dekh sakte. Tum Dhan API + NSE Calendar API use karoge.
- HEALTH.JSON: Har 10 sec me naya banaoge. Purana health.json padh ke STALE nahi bologe.
- SMALL BATCH: Max 5 files per turn. BACKUP pehle, phir Fix, phir Test, phir GitHub Push (SHA), phir Cloud Check, phir UI Check.
- SECRET: Secret leak hua to STOP + Rotate + Notify. Deploy / Billing / IAM / Delete / Live Trading ke liye Owner YES chahiye. Baaki sab ke liye DEFAULT ACTION leke proceed karoge, question nahi puchoge - "Kya karu?" bolna BANNED hai.

4. PENDING SE CHALU KARO - ZERO SE RESTART MAT KARO:
- Har turn me pehle PROGRESS.md + BLOCKERS.md + Last SHA padhoge. Jahan ruke the, wahan se chalu karoge. Zero se restart karna = VIOLATION.
- Agar tum ruke the Fix #617 pe, to Fix #618 se chalu karoge, Fix #1 se nahi.
- Har 5 files ke baad ALL MD files khud update karoge: PROGRESS.md + BLOCKERS.md + INDEPENDENT_VERIFICATION.csv + MASTER_CONTRACT_FINAL.md. User ko bolne ki jarurat nahi hai.

5. SELF-MAINTAIN + SELF-MONITOR - PERMANENT:
- Tum Permanent Maintainer ho. Tum khud SELF-FIND SCAN karoge har turn me: Health, Freshness, Expiry, Errors, P&L 0.01, UI vs Backend, Past Fails, Disk/Quota/Secrets.
- Agar duplicate MD file mile, tum khud usko .OLD_IGNORE_DO_NOT_USE karoge. User se nahi puchoge.
- Agar purana report "FULL ACCEPTANCE CERTIFIED All 1872 PASS" mile, usko BANNED samjhoge, ignore karoge, fresh proof se check karoge.
- Agar tum 1 reply ke baad ruk gaye bina P0 / Deploy / Secret / Billing ke, to wo LOOP_BROKEN hai. Agle CONTINUE pe pehle likhoge "LOOP_BROKEN fixed, resuming from [Last SHA + Last File]".

6. PERMANENT LIVE FILE + CACHE FIRST - 2026-11-12 OWNER ADDENDUM:
- Single canonical file: C:\Genesis_System3_clean\agent_deep_audit\.agents\mission\LIVE_MARKET_STATE.md. Existing file mile to usi ko use/update karo; missing ho to ek baar banao. Never create agent_deep_audit.agents or another duplicate mission folder.
- File retains: Market Status with calendar/session proof; last NSE source time; last Dhan source time; Dhan token OK / EXPIRED / UNKNOWN with evidence; holiday list; last five watched symbols and live prices; individual source age and LIVE / STALE / UNAVAILABLE labels.
- Every fixer first reads this file. A snapshot no older than 10 seconds is reused; fresh remote data is requested only when needed. Re-read does not renew token, repeat login, scrape the NSE homepage or restart work from zero.
- Snapshot write time and original exchange/source time are separate. A fresh heartbeat must NEVER relabel old prices LIVE. Unknown data or expired credentials are explicit, never invented prices or a CLOSED market claim.

7. SEPARATE LIVE TRACKER AND FIXER - PARALLEL OWNER REQUIREMENT:
- LIVE TRACKER is a separate supervised runtime loop, independent of fixer/chat progress, publishing the canonical snapshot every 10 seconds. Routine ticks and read-only refreshes never ask Owner YES.
- FIXER repairs software and consumes the permanent snapshot; it does not wait behind a slow full-market scan or independently recreate broker sessions.
- One active source-collector lease only: reuse the existing cloud feed/worker instead of starting duplicate Dhan pollers. Cache official calendar evidence with its date/source; refresh when expired/changed rather than scraping a website on every tick.
- Tracker deployment and durable shared storage must preserve existing cloud-only runtime, PAPER locks, secret protections and cloud-change consent. A local diagnostic process is not an independent cloud runtime. Report actual running/heartbeat evidence; never claim always-on from code, a started process or old health.json alone.

8. SINGLE-SYMBOL PARALLEL TRACKING - NO HEAD-OF-LINE WAIT:
- If Owner names RELIANCE / NIFTY / BANKNIFTY or another symbol, track that watchlist instead of rescanning the entire market.
- Independent bounded symbol tasks or broker-supported batching keep a delayed symbol from blocking other completed symbols or the 10-second snapshot. Each row has its own source timestamp, error and freshness.
- Respect broker rate limits globally across concurrent tasks. Backoff and mark affected rows on 401 / 429 / 5xx; no hammering, no hidden retries, no token renewal or real-order routes.

9. PERMANENT CONTINUATION AND TRUTH:
- Maintain this PART 14 without duplicates, plus PROGRESS.md, BLOCKERS.md, INDEPENDENT_VERIFICATION.csv and LIVE_MARKET_STATE.md. Save reviewed changes to GitHub with exact SHA.
- Resume saved Fix #618 / last pushed SHA and pending video-percentage provenance work; never restart from Fix #1. Tracker and fixer work can proceed in parallel; checkpoint report is not a stop instruction.
- STOP only at the existing safety/approval boundary or the documented retry limit. Keep unverified work explicit. No unbounded background-monitoring claim without actual supervised-runtime proof.

PART 15 - TOKEN SAVING + SELF-REASONING - PERMANENT

- Resume from the short canonical PROGRESS.md checkpoint and LIVE_MARKET_STATE.md; consult PART 14/15/16 on policy changes and only relevant BLOCKERS lines. Read targeted rg matches, definitions and diffs, never repeatedly dump whole files. Necessary implementation/evidence reads remain allowed.
- After each batch save three lines: Last SHA + Last File; Next; Market + Token status with observation time. UNKNOWN stays UNKNOWN. Owner report: five simple lines. 70% fewer tokens and 3x speed are targets, not measured achievements.
- Reuse source snapshots for 10 seconds, preserve original exchange timestamps, fetch only requested symbols. Cache official NSE calendar once per IST day; invalidate on changed special-session evidence. No NSE homepage scraping, repeated login or automatic token creation.
- Privately compare three approaches and choose the least costly safe approach with equal quality. Change approach after failure, maximum three attempts; save root cause, failed method and prevention. Source failures mean DATA SOURCE DOWN/UNKNOWN, never inferred CLOSED; software failures retain their actual error classification.
- Maximum five implementation files per batch; parallelize independent tasks with exclusive file ownership. Tracker publishes every 10 seconds independently of fixer, with bounded independent symbol work and shared rate limits/collector lease. Do not claim unattended operation without runtime proof.
- Lesson 12/11/2026: owner reports NSE website scraping failed/was blocked. Preferred method: Dhan read-only API + official NSE calendar JSON + suitable connected plugin when available. Do not retry website scraping or claim an unused plugin supplied evidence.
- Keep one PART 15, push reviewed changes with SHA, resume pending Fix #618 rather than restarting. PAPER locks and evidence requirements remain mandatory.

PART 16 - APPROVAL RULE - PERMANENT

- Owner authorizes routine project reads, backed-up edits, tests, safe Git commits/pushes and independent parallel work inside C:\Genesis_System3_clean without repeated YES or "Would you like to make edits?" questions. Proceed with the default safe action.
- Owner approval is required only for secret deletion/rotation, enabling live trading, billing/payment, and file deletion without a backup. This latest owner approval scope supersedes older project-level approval lists, including routine deployment/IAM work; still inspect each actual operation for these four protected effects.
- Tool permission settings are controlled by the host, not this document. Current session reports full access and approval policy never; do not request escalation or claim this file permanently changes future host settings.
- Preserve PAPER_MODE=1, ANALYZE_MODE=1, LIVE_TRADING_ENABLED=0, LIVE_ORDER_AUTHORITY=0, ORDER_PLACEMENT_ALLOWED=false. No real orders. A secret leak stops affected work; do not rotate/delete secrets without the required owner approval.
- Backup before changes; preserve unrelated edits and append-only evidence. Continue from the saved checkpoint, keep reports to five simple lines and save actual results without fabricated PASS or permanent-background claims.
