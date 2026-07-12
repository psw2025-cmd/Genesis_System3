# System3 360° Root Cause Blocker Matrix

Owner/operator: **PRITAM S. WARGHADE**

Generated purpose: stop symptom-level fixes and track the real end-to-end blockers before any production-grade claim.

## Current truth

Status: **NOT PRODUCTION GRADE**

Reason: UI visibility is improving, but real trading chain is still blocked at broker auth, option-chain universe, scanner/ranker, paper lifecycle, ML/training proof, Render/fresh visual proof, GitHub/Render failure tracking, and final truth aggregation.

## Permanent operating authority and safety boundary

User grants standing authority to execute repo repair, dependency install checks, GitHub Actions proof workflows, Render verification workflows, dashboard visual proof, integration verification, and TODO/status reporting required to resolve System3 blockers.

This authority does **not** allow secrets to be pasted, printed, committed, logged, screenshotted, or stored in chat/repo files. Credentials may only be used through secure secret stores and workflow environment variables. Any missing/invalid credential must be reported as a blocker with redacted proof only.

Live trading remains OFF. Analyzer/paper/read-only broker proof is allowed. Live order placement, modification, cancellation, or routing remains blocked unless separately proven safe and explicitly enabled later by the owner.

## Absolute visual-claim rule

No issue, feature, fix, gate, workflow, model, broker state, paper state, scanner state, or production-grade status may be claimed DONE / fixed / resolved / passed unless the live Render dashboard UI is visually checked by automation after the latest relevant commit and shows the required proof text on screen.

Backend/API JSON, file existence, screenshot file size, logs, or chat statements are supporting evidence only. Final claim evidence must include dashboard UI visible proof from automated screenshot/text inspection.

If automated dashboard UI proof is missing, stale, red, blocked, pending, or contradictory, status must remain **PENDING** or **BLOCKED**. Do not use manual user screenshots as the final proof requirement.

## Critical root findings

1. Some backend router patches may not affect production because modular routers are imported but not included in `dashboard/backend/app.py`; old app-level routes remain active.
2. Render dashboard can show stale frontend/backend if the latest commit is not deployed and visually verified.
3. Dhan broker can appear connected/degraded while funds/token proof is failed; UI must treat invalid token as broker auth blocked.
4. Dhan auth failure blocks funds, broker truth, option-chain validation, scanner/ranker, CE/PE decision, paper lifecycle, and money readiness.
5. Screenshot file size is not proof. The actual visible text and blocker rows must be checked.
6. Final public truth can be stale if workflows do not run after latest patches.
7. No live trading remains correct; this is a safety pass, not a money-readiness pass.
8. Dependency/install health and credential presence must be audited automatically; manual chat claims do not count.
9. Any claim without automated live dashboard UI proof is invalid and must be reverted to PENDING/BLOCKED.
10. GitHub workflow failures and Render public endpoint failures must be tracked together in one TODO and resolved from proof, not from chat memory.

## Pending blocker count

Total pending blockers: **22**

| ID | Blocker | Owner | Required fix | Proof required |
|---|---|---|---|---|
| B01 | Dhan token/auth invalid or expired | User/Render | Refresh/update Dhan read-only API credentials in Render using secure process | Broker panel shows auth OK; funds API responds without auth error |
| B02 | Dhan client/account identity not confirmed by broker API | User/Render | Confirm correct Dhan client/account credentials are configured | Broker status shows valid client/account proof or clear broker limitation |
| B03 | Broker status contradiction | Code | UI/backend must not show CONNECTED when funds/status token proof fails | Broker screenshot shows BLOCKED/TOKEN ERROR when token invalid |
| B04 | Render deploy may be stale | Render/GitHub | Verify deployed commit equals latest expected commit | `/api/deploy/info` proof plus visual screenshot after deploy |
| B05 | Final public truth stale | GitHub workflow | Regenerate public truth after every critical patch | `reports/latest/system3_public_truth/index.md` latest commit and verdict |
| B06 | Modular backend router patches may not be active | Code | Move fixed logic into active app routes or enable routers safely without duplicate conflicts | Active endpoint response proves fixed logic |
| B07 | Dhan option-chain enabled universe 0/4 | User/Code/Render | Fix broker auth first, then verify Dhan option-chain per enabled symbol | Truth Control shows enabled universe rows and Dhan chain proof |
| B08 | Scanner segments 0/4 | Code/Data | Scanner must run only after valid Dhan chain rows exist | Signals tab shows scanner segments >0 or exact blocked reason |
| B09 | CE/PE decision missing | Code/ML | Ranker/model must output CE/PE side, strike, expiry, confidence, reason | Signals tab shows CE/PE decision or exact block reason |
| B10 | Paper lifecycle blocked | Code/Data | Paper engine must receive valid candidate and write paper entry/exit provenance | Paper tab shows paper truth provenance, entry/exit rows |
| B11 | ML training proof pending | Code/Data | CE/PE history dataset and model training proof must exist | ML tab shows dataset rows, train/test rows, accuracy/AUC or blocked reason |
| B12 | Historical CE/PE contract list not proven live | Code/Data | Build contracts from Dhan master and verify security IDs | Contract builder report PASS and contracts.csv proof |
| B13 | Dhan historical download not proven | User/Code | Dhan historical access or licensed CSV import must produce real candles | Training proof summary shows raw rows and no fake data |
| B14 | Model score not visually proven | Code/UI | ML tab must expose real score fields from proof JSON | ML screenshot visibly shows score/proof records |
| B15 | Paper provenance not visually proven | Code/UI | Paper tab must expose source file, rejected fake rows, order endpoints not called | Paper screenshot visibly shows provenance panel |
| B16 | Production Proof Bar not yet visually validated | UI/Render | Render latest UI and capture screenshots | Screenshot shows 7 proof gates visible |
| B17 | Render worker/scheduler proof not complete | Render/Workflow | Worker must write latest proof artifacts reliably | Reports show latest worker/scheduler proof timestamp/status |
| B18 | 360 integration gate missing | Workflow | One workflow must combine Render API, dashboard visual proof, broker truth, chain truth, scanner, paper, ML, and final verdict | Integration report PASS/BLOCKED with exact blocker list |
| B19 | Dependency/install health not continuously proven | Workflow | Run secure install audit for Python/Node/project dependency readiness | install audit report PASS/BLOCKED with exact failing package/command |
| B20 | Credential presence/format not continuously proven | Workflow/Render | Check required credential presence via secure workflow env only; never print values | credential audit report with redacted presence/format status |
| B21 | Claim made without automated dashboard visual proof | Assistant/Workflow | Revert claim to PENDING/BLOCKED and require visual issue tracker + dashboard proof board PASS | dashboard_visible_issue_tracker and autopilot proof board PASS after latest commit |
| B22 | GitHub workflow and Render failure tracker not proven PASS | Workflow/Render | Track GitHub failed runs and Render endpoint failures together every 30 minutes | `docs/SYSTEM3_GITHUB_RENDER_FAILURE_TODO.md` and `reports/latest/github_render_failure_tracker/summary.json` PASS |

## User-side fixes required

1. Refresh or replace Dhan read-only API token/session through the secure Dhan process when audit says invalid/expired.
2. Verify correct Dhan client ID/account is configured in Render when audit says missing/mismatch.
3. Do not paste secrets in chat.
4. After updating Render environment, redeploy backend and worker.
5. Screenshots from user are optional only; automated dashboard visual proof is mandatory.

## Code-side fixes required

1. Stop patching inactive routers when active routes live in `dashboard/backend/app.py`.
2. Centralize broker truth: connected=false if any token/funds/status auth proof fails.
3. Centralize public truth: latest commit, Render commit, visual proof commit, and dashboard UI must match.
4. Add one integration proof workflow that checks all required APIs and screenshots.
5. Keep live order paths disabled.
6. Track visible dashboard red/error/pending issues automatically until zero.
7. Track dependency/install and credential readiness automatically.
8. Block any DONE/resolved claim unless live dashboard UI proof is current and PASS.
9. Track GitHub workflow failures and Render endpoint failures in one persistent TODO.

## Render/workflow fixes required

1. Verify latest commit deployed.
2. Verify frontend bundle refreshed.
3. Verify backend API refresh after deploy.
4. Verify worker writes latest proof.
5. Verify final public truth regenerated after latest commit.
6. Verify required secrets are present through secure workflow env checks only.
7. Verify automated dashboard UI visual proof after latest commit.
8. Verify GitHub + Render failure tracker PASS.

## Required final proof before any resolved claim

1. Render deploy commit proof.
2. Broker auth proof.
3. Dhan chain proof for enabled universe.
4. Scanner/ranker proof.
5. CE/PE decision proof.
6. Paper lifecycle proof.
7. ML training score proof.
8. Dashboard visual proof with owner + proof bar.
9. Visible UI issue tracker PASS.
10. Autopilot proof board PASS.
11. GitHub + Render failure tracker PASS.
12. Integration report proof.
13. Workflow failure tracker proof.
14. Dependency/install + credential audit proof.
15. Final public truth proof.
