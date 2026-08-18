# Genesis System3 — Universal Agent Operating Contract

**Applies to:** Codex and every generic/unknown AI agent working in this repository.

**Highest-priority temporal rule:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Read first:
1. `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`
2. `docs/authority/AUTONOMOUS_OPERATIONS_POLICY.md`
3. `docs/project_control/SYSTEM3_MASTER_GOAL_LOCK.md`
4. `docs/END_TO_END_ISSUES_SOLUTIONS_AGENT_POLICY.md` + flowchart `docs/agent_memory/END_TO_END_ISSUES_SOLUTIONS_FLOWCHART.png` (**permanent — all agents**)
5. `docs/gemini-code-1786899974029.md` + `agent_policy.yaml` (autonomous loop invariants)
6. `docs/CONTINUOUS_CLOSURE_SYSTEM.md` — repo-first scan → multi-verify → watchdog → blocker cards → auto-resume
7. `docs/PREFLIGHT_CONTROL_PLANE.md` — current main + all workflow latest runs + actionable failures + artifacts + Issue #188/PR state before every production transition
8. `docs/architecture/INFINITE_GITOPS_AGENT_PROMPT.md` — infinite GitOps ticks without waiting for the user on routine work; LIVE remains a human gate
9. `docs/CHATGPT_MUST_REVIEW_NOW.md` — current ChatGPT consolidator handoff (live-pinned); Cursor instructions inbound at `docs/chatgpt_to_cursar-5.md`

Old session notes, `SYSTEM_STATE.md`, `CHANGE_LOG.md`, `reports/latest/`, proof packs, screenshots, workflow artifacts, and historical agent reports are **context/history only** until revalidated against current authoritative sources.

## Mandatory preflight before proceeding

Before any production-relevant transition, run or consume a freshly generated `scripts/system3_preflight_control_plane.py` snapshot and independently revalidate critical current claims. Do not infer the next step from a previous message or stale report.

Transition law:
- exact-head mandatory CI green → merge without unnecessary waiting;
- merge complete → check canonical Cloud Run deployment immediately;
- deployment active → report `STATUS=WAITING` but continue any non-conflicting safe work;
- deployment complete → re-read current remote main, verify exact production serving SHA, then generate a NEW semantic production URL proof;
- URL proof failure → freeze evidence, investigate, and open/continue the next remediation immediately;
- current-main/active-PR workflow failure → inspect failed job/step/log/artifact before proceeding;
- unrelated historical failure → context only unless fresh evidence makes it relevant;
- stop only for a verified external dependency or genuine user approval/account-level action.

Every active remediation update should state `STATUS`, `IN_PROGRESS`, `CURRENT_STEP`, `NEXT_ACTION`, and `USER_ACTION`.

## Production authority

- Repository authority: `psw2025-cmd/Genesis_System3`.
- Runtime/deployment authority: Google Cloud project `system3-openalgo-safe`, region `asia-south1`.
- Production service: `genesis-system3-web`.
- Production UI: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`.
- Broker authority: **Dhan**. Legacy Angel/Render instructions are retired/non-authoritative.
- GitHub Actions -> Google Cloud uses keyless WIF. Do not create/export service-account JSON keys.

## Absolute current/live truth rule

Never infer `now`, `current`, `present`, `live`, `still working`, `fixed now`, `connected now`, or `UI now` from a stored artifact.

For a new current/live UI investigation:

1. Record the investigation/request UTC start time.
2. Start a **new** production Chrome/WebDriver session after that time.
3. Open the actual GCP production URL.
4. Capture fresh screenshots + visible text for relevant tabs; for full UI audit capture all 22 canonical tabs.
5. Capture relevant read-only APIs during the same proof session.
6. Compare UI and API truth; surface contradictions.
7. Report capture time and evidence age.
8. After any fix/deploy/recovery, capture again. Pre-fix evidence is historical.

`reports/latest/` means latest stored report, **not live runtime truth**. A green deploy/CI run proves only what its gates actually tested. HTTP 200 or “tab rendered” does not prove populated/semantically correct market data.

Use `scripts/gcp_live_ui_snapshot.py` for fresh production UI lifecycle proof and `scripts/system3_temporal_truth_guard.py` to validate stored evidence freshness. See the canonical temporal policy for the full contract.

## Full UI lifecycle

Canonical tabs:

`decision-intel`, `truth`, `genesis`, `e2e-proof`, `overview`, `sim-live`, `options-intel`, `chain`, `signals`, `trade`, `paper`, `positions`, `risk-scenarios`, `multibagger`, `prediction-audit`, `performance`, `ml`, `data-integrity`, `broker`, `alerts`, `system`, `gates`.

A production UI PASS requires fresh production-browser evidence plus semantic data/state checks appropriate to each tab. Local Vite/browser smoke is useful for rendering regressions but is `LOCAL_NON_PRODUCTION` and cannot prove GCP runtime/broker/data truth.

## Safety boundary

- `ANALYZE_MODE=1`.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- Do not place/modify/cancel/square-off real orders.
- Do not expose broker secret payloads.
- Read-only production broker/status/market-data/UI verification is allowed when needed for proof.
- Token rotation may occur only through the dedicated bounded Dhan rotation/recovery authority defined in repository governance.

## Autonomous engineering behavior

When an issue is found:

1. Verify the symptom from a current authoritative source.
2. Classify whether evidence is live or historical.
3. Reproduce/read logs/code only as required.
4. Identify root cause and affected surfaces.
5. Compare multiple safe solution paths when useful.
6. Implement the smallest production-grade fix on a branch.
7. Run focused tests + mandatory current CI gates.
8. Merge only when the exact head is proven safe.
9. Verify the resulting production state with **new** live evidence.
10. Do not stop at “workflow green” if the user-visible/runtime end state is still wrong.

## Multi-agent concurrency

Other agents may work in parallel. Before editing or merging:

- inspect current `main` and relevant open PRs;
- do not overwrite another agent's newer work silently;
- rebase/recreate from current main when a branch has become stale;
- never use an old PR's “current state” narrative as current truth;
- when agents disagree about current runtime state, generate a new live observation—old artifacts do not arbitrate.

## User-action boundary

Routine code, CI, deployment, IAM-drift repair, logs, browser proof, broker investigation, and safe recovery should be handled through repository/GCP automation without waiting for chat approval. Ask the user for manual action only for genuine break-glass/account-level conditions that delegated automation cannot perform: LIVE enablement, real orders, billing/org, WIF destruction, broker MFA.

## Evidence hierarchy

For current runtime/UI claims, prefer:

1. request-scoped fresh production browser evidence;
2. same-session fresh production API evidence;
3. same-window production logs/runtime metadata;
4. current deployed revision/SHA/config;
5. source code;
6. historical artifacts/reports for comparison only.

Historical evidence must be labeled with its capture/observation time. Never silently promote historical evidence to current truth.
