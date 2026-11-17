
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

# Independent evidence standard - EVIDENCE PASS CONTRACT V3
Version: 2026-11-12 V3 - FINAL - MULTI-VERIFIED - UI IS PROOF
Authority: OWNER_GOALS.md V3, root AGENTS.md, root GEMINI.md
This is a verification contract, not a generated certificate. Violation = Claim REJECTED.

## 1 YEAR LESSON - WHY AGENT FAKED PASS FOR 1 YEAR
1. Agent ran run_1872_acceptance_pipeline.py and copied its textual PASS as real proof. NEVER AGAIN.
2. Agent wrote BLOCKED for every FAIL to hide failure. NEVER AGAIN.
3. Agent showed backend log as proof, never checked UI. NEVER AGAIN.
4. Agent used old SHA as proof of real price. SHA proves file did not change, NOT that price is real.
5. Agent reused old screenshot as new proof. NEVER AGAIN.
6. Agent called replay data as live data. NEVER AGAIN.
7. Agent used dummy / stale price as live price. NEVER AGAIN.
8. Agent reviewed his own work. NEVER AGAIN.
9. Agent edited logs to hide FAIL. NEVER AGAIN.

## BANNED SCRIPT - HARD BAN
- scripts/run_1872_acceptance_pipeline.py is BANNED as acceptance proof.
- DO NOT RUN it for certification. DO NOT copy its PASS output.
- Its existing CSV and JSON output are HISTORICAL CLAIMS ONLY. Preserve them, DO NOT edit, DO NOT delete, DO NOT use as proof.
- If Agent runs it, that run = INVALID. Must re-verify with real check below.
- Only way to un-ban: Owner explicitly says REPAIR IT + it is independently tested + Owner approves in chat.

## FOR EACH CHECK ID - 15 ITEMS REQUIRED, MISSING 1 = UNVERIFIED
For each check ID, retain ALL:
1. Current UTC time + IST time both. Format: 2026-11-12 10:30:00 IST / 05:00:00 UTC. Only 1 timezone = REJECTED.
2. Actual workspace: C:\Genesis_System3_clean
3. Git SHA - GitHub Commit SHA + Branch + Pushed proof (git push output) + Commit URL
4. Deployed revision - Google Cloud Revision + Cloud URL + Deploy Time (when relevant)
5. Executed command / test path + exit code (0 = pass, non-zero = fail, full log, no edited log)
6. Expected versus observed behavior (what should happen vs what actually happened)
7. Raw source packets or sanitized logs with timestamps (raw, unedited, append-only)
8. Exact artifact URI, hash and reproduction instructions (how Owner can reproduce in 1 click)
9. Reviewer and decision distinct from generator - Reviewer MUST be: Second run with different method OR Owner check OR Independent script. Generator name != Reviewer name. Same name = REJECTED.
10. UI PROOF - For UI tasks: Cloud URL opened + Screenshot dated today + Cloud URL visible in screenshot + Time visible in screenshot + Value in UI matches backend value. 3-time check: After Fix, After Push, After Cloud Deploy.
11. GitHub + Cloud link - Commit URL + Cloud Console URL
12. DATA TYPE LABEL - MUST label: LIVE / CLOSED / REPLAY / DELAYED / SIMULATION. No label = REJECTED. Replay labelled as Live = FRAUD, claim REJECTED + BLOCKER.
13. FRESHNESS CHECK - Market data must be fresh: Live data max age 60 seconds. If data older than 60 sec, mark STALE, not LIVE. Stale marked as Live = REJECTED.
14. DUMMY CHECK - Price / OI / Volume must NOT be: 0 (unless real 0 with broker proof), 999 / 9999 / 12345, hardcoded, repeated same value for 10+ ticks, or yesterday's value. Dummy found = FAIL.
15. TIME SYNC CHECK - System time vs NSE/BSE time vs Broker timestamp must match within 5 seconds. Mismatch > 5 sec = BLOCKED, do not PASS.

## PASS / FAIL / BLOCKED / UNVERIFIED - STRICT DEFINITIONS
- PASS = All 15 items present + Repeated independent check passed + UI matches backend (if UI task) + GitHub pushed + Cloud deployed + Fresh + Not dummy + Correct label.
- FAIL = Actual failed assertion. Example: Expected LTP 100, Got 0 / Error / Wrong value / Dummy / Stale marked as Live. FAIL cannot be renamed to BLOCKED.
- BLOCKED = ONLY for these 4 reasons with proof: Tools down (screenshot of error), Auth expired (auth log), Market closed (NSE/BSE calendar proof + timestamp), Entitlement / Access limit (broker error). BLOCKED needs proof of blocker + Owner notified. Without proof, BLOCKED = FAIL.
- UNVERIFIED = Missing independent proof. No proof = UNVERIFIED. No exception. Code statement = UNVERIFIED. Narrative = UNVERIFIED. Old screenshot = UNVERIFIED.

## HARD RULES - WHAT IS NOT PROOF
- Do NOT transform self-authored narrative into evidence. Agent's own story = NOT proof.
- Do NOT treat SHA256 as proof that prices or fills are real. SHA proves file unchanged, NOT price real. Real price proof = Broker packet + Timestamp + UI match + Freshness.
- Do NOT count a GET endpoint as proof of a real broker session. GET 200 = Server up, NOT broker logged in. Broker proof = Auth token + Session ID + Live packet + UI match.
- Do NOT count localhost UI as Cloud proof. Localhost = Test only. Cloud URL UI = Real proof.
- Do NOT count backend log alone as UI proof. Backend PASS + UI FAIL = FAIL.
- Do NOT reuse screenshot. 1 Screenshot = 1 Check + 1 Time. Same screenshot for 2 checks = Both REJECTED.
- Do NOT edit logs. Logs are append-only. If log edited, check = INVALID. Keep original + new log both.
- Do NOT hide FAIL. If FAIL, write FAIL + BLOCKERS.md. Hiding FAIL = VIOLATION.
- Preserve safety and privacy. NEVER log secrets, tokens, API keys in evidence. Sanitize before saving. If secret leaked in evidence, STOP, rotate secret, notify Owner.

## EVIDENCE IMMUTABILITY - ANTI-TAMPER
- Once evidence written to INDEPENDENT_VERIFICATION.csv, DO NOT edit that row. If correction needed, add NEW row with Correction + Old SHA + New SHA + Reason + Time.
- Evidence file must be committed to GitHub after each batch. Uncommitted evidence = NOT COUNTED.
- If evidence file SHA changes without new commit, that evidence = INVALID.

## SINGLE SOURCE OF TRUTH - PATH FIX
- ONLY TRUTH FILE: C:\Genesis_System3_clean\agent_deep_audit\.agents\state\INDEPENDENT_VERIFICATION.csv
- IGNORE root .agents\state\ - Old / Duplicate. Do NOT read/write there.
- HISTORICAL CLAIMS: root GENESIS_1872_MASTER_CHECKLIST.csv + old evidence JSONs. Preserve, do not use as proof.
- If file not found, STOP, write BLOCKER: FILE_NOT_FOUND + full path.

## BATCH + STOP RULE
- Max 5 checks per turn. After 5, update PROGRESS.md, STOP, wait for Owner CONTINUE.
- If 1 P0 check FAILS, STOP, write BLOCKERS.md, do NOT go to next check.
- If same error 3 times, STOP loop, write LOOP_BLOCKER.
- If Agent tries to PASS without UI, STOP that claim, mark UNVERIFIED.

## UI IS PROOF - FINAL RULE
Without verifying UI, NO claim accepted which required UI / UX.
UI Task without Cloud URL + Dated Screenshot (URL + Time visible) + Backend Match + Freshness = REJECTED automatically.