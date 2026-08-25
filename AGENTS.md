# Genesis System3 — Universal Agent Operating Contract

**Applies to:** Codex and every generic/unknown AI agent working in this repository.

**Highest-priority temporal rule:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Read first:
0. `docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md` — persistent autonomous end-to-end self-instruction and completion-ledger contract; re-read before every merge, deployment, production mutation, issue closure, and final response
1. `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`
2. `docs/authority/AUTONOMOUS_OPERATIONS_POLICY.md`
3. `docs/authority/USER_ACTION_AUTONOMY_SPEED_POLICY.md` — permanent user-action/autonomy-speed law; complete its 19-point self-MRI before saying `USER_ACTION=NONE` or `HUMAN_ACTION_REQUIRED=NO`
4. `docs/project_control/SYSTEM3_MASTER_GOAL_LOCK.md`
5. `docs/END_TO_END_ISSUES_SOLUTIONS_AGENT_POLICY.md` + flowchart `docs/agent_memory/END_TO_END_ISSUES_SOLUTIONS_FLOWCHART.png` (**permanent — all agents**)
6. `docs/gemini-code-1786899974029.md` + `agent_policy.yaml` (autonomous loop invariants)
7. `docs/CONTINUOUS_CLOSURE_SYSTEM.md` — repo-first scan → multi-verify → watchdog → blocker cards → auto-resume
8. `docs/PREFLIGHT_CONTROL_PLANE.md` — current main + all workflow latest runs + actionable failures + artifacts + Issue #188/PR state before every production transition
9. `docs/architecture/INFINITE_GITOPS_AGENT_PROMPT.md` — infinite GitOps ticks without waiting for the user on routine work; LIVE remains a human gate
10. `docs/project_control/REPO_CLEAN_FORENSIC_TOOLKIT.md` — permanent full-repo cleanup/storage authority; improve this toolkit instead of creating competing cleanup scanners
11. `docs/project_control/PREDICTION_WORLD_CLASS_BENCHMARK_POLICY.md` — permanent data/feature/model/prediction benchmark authority; compare material prediction changes against current primary research, simple baselines and relevant contemporary challengers before promotion

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

Every active remediation update should state `STATUS`, `IN_PROGRESS`, `CURRENT_STEP`, `NEXT_ACTION`, `MANDATORY_USER_ACTION`, and `OPTIONAL_ACCELERATION_ACTION`.

## Dashboard-impact blocker and dual-channel escalation

For every new or materially changed blocker, check whether it directly or
indirectly slows or corrupts dashboard content, market data, source/freshness
truth, API↔UI parity, broker state, predictions, PAPER records, deployment,
proof, or multi-agent throughput.

If the owner can unblock or materially accelerate it through an account,
permission, connector, ruleset, review, environment, billing, subscription,
identity/consent, or external-provider action:

1. create a stable `USER_ACTION_ID` and link every blocked task ID;
2. continue all safe non-overlapping agent work;
3. notify the owner immediately in the current chat and through the verified
   connected mail channel;
4. put `FASTEST_SAFE_RECOMMENDED` first and list every materially different
   safe alternative with expected time, benefit, risk, and proof;
5. provide `WHY / WHERE / CLICK / SET / DO NOT / RESULT / PROOF / URGENCY`;
6. track `DISCOVERED -> NOTIFIED -> ACKNOWLEDGED -> IN_PROGRESS ->
   PROVEN_COMPLETE` in Issue #188/the active ledger;
7. repeat the unresolved delta at material transitions and on the governed
   reminder cadence until fresh evidence proves completion;
8. mark mail delivery failure as its own blocker; never pretend an email was
   sent.

Access that safely unlocks several downstream dashboard/data/proof tasks has
priority over isolated low-impact work. Never request secret values or weaker
safety. The canonical details are in
`docs/authority/USER_ACTION_AUTONOMY_SPEED_POLICY.md`.

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
6. Check the 19-point user-action/autonomy-speed MRI and surface any safe setup action that materially accelerates progress.
7. Implement the smallest production-grade fix on a branch.
8. Run focused tests + mandatory current CI gates.
9. Merge only when the exact head is proven safe.
10. Verify the resulting production state with **new** live evidence.
11. Do not stop at “workflow green” if the user-visible/runtime end state is still wrong.

## Multi-agent concurrency

Other agents may work in parallel. Before editing or merging:

- inspect current `main` and relevant open PRs;
- do not overwrite another agent's newer work silently;
- rebase/recreate from current main when a branch has become stale;
- never use an old PR's “current state” narrative as current truth;
- when agents disagree about current runtime state, generate a new live observation—old artifacts do not arbitrate.

## User-action boundary

Routine code, CI, deployment, IAM-drift repair, logs, browser proof, broker investigation, and safe recovery should be handled through repository/GCP automation without waiting for chat approval. Ask the user for mandatory manual action only for genuine break-glass/account-level conditions that delegated automation cannot perform: LIVE enablement, real orders, billing/org, WIF destruction, broker MFA.

However, a lack of mandatory human action does **not** mean the user has no useful acceleration step. Before saying `USER_ACTION=NONE`, `HUMAN_ACTION_REQUIRED=NO`, or equivalent, read `docs/authority/USER_ACTION_AUTONOMY_SPEED_POLICY.md`, complete its 19-point self-MRI, and report two separate fields:

- `MANDATORY_USER_ACTION=` true blocker or `NONE`;
- `OPTIONAL_ACCELERATION_ACTION=` fastest safe user-side setup improvement or `NONE`.

If a user-side setting, connector authorization, ruleset/review configuration, environment protection, billing/org control, or external account action would materially reduce delay or improve autonomous execution, surface it immediately with kid-level `WHY / WHERE / CLICK / SET / DO NOT / RESULT / PROOF / URGENCY` instructions while continuing all safe agent work in parallel.

## Evidence hierarchy

For current runtime/UI claims, prefer:

1. request-scoped fresh production browser evidence;
2. same-session fresh production API evidence;
3. same-window production logs/runtime metadata;
4. current deployed revision/SHA/config;
5. source code;
6. historical artifacts/reports for comparison only.

Historical evidence must be labeled with its capture/observation time. Never silently promote historical evidence to current truth.

## Permanent repo-clean / storage rule

When the user asks to clean the repo, remove duplicates, reduce repository size, free GitHub storage, check repository “memory”, or verify files for deletion:

1. Fresh-read current `main` and active cleanup PR ownership.
2. Run `scripts/system3_repo_clean_forensic_toolkit.py` or the canonical `Repo Clean Forensic Toolkit` workflow.
3. Read `00_EXECUTIVE_DELETE_DECISION.md` first and use the exact current-run artifact only.
4. Distinguish **current tracked worktree**, **Git history/object database**, **GitHub Actions artifacts**, and **local ignored/untracked disk**. They are different storage layers.
5. Never delete from filename similarity, “old/backup/archive” naming, one grep result, age, or an old report.
6. Only `DELETE_PROVEN_100` rows may seed an automated cleanup PR. Source/runtime duplicates remain fail-closed until their cleanup PR passes normal CI.
7. The toolkit itself must remain report-only. No source deletion, artifact deletion, history rewrite, force push, broker/order call, LIVE change, secret read, or IAM mutation is part of the scan.
8. If a cleanup false positive/negative is found, add a regression test and improve the canonical toolkit instead of forking another cleanup scanner.

## Permanent world-class prediction rule

For any request involving prediction accuracy, AI/ML models, ranking, feature engineering, market-data expansion, retraining, self-learning, strategy search or model promotion:

1. Fresh-read `docs/project_control/PREDICTION_WORLD_CLASS_BENCHMARK_POLICY.md` and current prediction/data ownership before changing code.
2. Compare current System3 capability against current primary research, official provider capabilities, the existing champion and simple baselines; do not equate newer/deeper AI with better alpha.
3. Fix data truth, historical coverage, point-in-time lineage and leakage risk before using model complexity to compensate for missing data.
4. Maintain an explicit versioned feature/label/model/tournament matrix. New features require lineage, availability time, freshness, leakage test and OOS ablation.
5. Every candidate must use the same-window/same-data/same-horizon/same-cost champion-challenger evaluation and include relevant statistical, economic, calibration and robustness metrics.
6. A single raw accuracy, hit-rate, P&L or Spearman threshold can never prove promotion readiness. Use leakage-safe OOS evaluation, realistic costs, regime breakdown, calibrated uncertainty and overfitting diagnostics.
7. Predictions require row-level lineage (`prediction_id`, data/feature/model versions, horizon, confidence/interval and realized outcome) before aggregate accuracy can become authority.
8. Treat current foundation models, LOB transformers, alternative data and LLM features as challengers only. Promote only when System3-specific evidence proves incremental net value over simpler baselines.
9. Self-learning is bounded retraining/recalibration/challenger testing with rollback; it never means uncontrolled code mutation, automatic LIVE enablement or automatic capital deployment.
10. Keep ANALYZE/PAPER and all LIVE/order safety locks unchanged while accuracy/research gates are incomplete.
