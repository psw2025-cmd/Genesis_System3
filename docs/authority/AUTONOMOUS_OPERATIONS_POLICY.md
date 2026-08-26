# Genesis System3 Autonomous Operations Policy

**Temporal authority marker:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Canonical temporal policy: `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.

Canonical user-action/autonomy-speed policy: `docs/authority/USER_ACTION_AUTONOMY_SPEED_POLICY.md` (`SYSTEM3_USER_ACTION_AUTONOMY_SPEED_V1`).

## Authority

- Google Cloud project `system3-openalgo-safe` is the authoritative production/runtime platform.
- GitHub repository `psw2025-cmd/Genesis_System3` is the authoritative code/configuration source.
- Render.com hosting is forbidden (retired host). Never recreate `render.yaml`, never deploy to Render, never treat Render as production. Google Cloud Run is the only production deploy. Canonical lock: `docs/authority/RENDER_HOSTING_FORBIDDEN.md`.
- GitHub Actions authenticates to Google Cloud only through keyless Workload Identity Federation (WIF). User-managed Google service-account JSON keys are forbidden.

## Operating objective

Routine production engineering must not depend on the user running technical commands. The control plane should investigate, patch, test, deploy, roll back, repair declared IAM drift, collect logs/evidence, and verify runtime/UI truth through GitHub Actions and Google Cloud.

The control plane must also proactively identify any account/settings/access step that the user can perform to materially accelerate safe autonomy. `HUMAN_ACTION_REQUIRED=NO` must never be used as shorthand for `there is nothing useful the user can do`. Before claiming `USER_ACTION=NONE`, agents must complete the 19-point self-MRI in `USER_ACTION_AUTONOMY_SPEED_POLICY.md` and separately report `MANDATORY_USER_ACTION` and `OPTIONAL_ACCELERATION_ACTION`.

## User-action acceleration contract

For any useful user-side action, agents must provide kid-level instructions containing `WHY`, `WHERE`, `CLICK`, `SET`, `DO NOT`, `RESULT`, `PROOF`, and `URGENCY`. Agents must continue all safe autonomous work in parallel and may not make the user run technical commands the connected control plane can execute itself.

A useful optional acceleration step must be surfaced early, before hours of retries or coordination delay. Examples include repository ruleset/review configuration, connector authorization, environment protection, external account approval, billing/org settings, or any other account-level control the agent cannot set itself. Faster operation must come from removing avoidable coordination/access friction, never from weakening safety, skipping failed checks, exposing secrets, or enabling LIVE trading.

## Temporal truth override

No autonomous agent/workflow may promote stored evidence into a current/live claim merely because it is named `latest`, is the newest artifact, or came from the newest successful workflow.

For any new `now/current/live/present/still/fixed now/connected now/UI now` investigation, a new observation must be generated after the investigation/request start time. For UI-facing claims this means a new Chrome/WebDriver session against the authoritative GCP production URL, fresh screenshots/visible text, and same-session read-only API evidence.

`SYSTEM_STATE.md`, `CHANGE_LOG.md`, `reports/latest/`, proof packs, prior screenshots, PR descriptions, old workflow artifacts, and source code are historical/contextual unless refreshed at the authoritative boundary.

Use `scripts/gcp_live_ui_snapshot.py` for full request-scoped production UI proof and `scripts/system3_temporal_truth_guard.py` for machine freshness validation. After a fix/deployment/recovery, pre-change evidence becomes historical and must not be reused as post-change proof.

If parallel agents disagree on a current runtime/UI state, generate a new live observation; old artifacts do not arbitrate.

## Safety boundary

The autonomous control plane MUST NOT:

1. enable LIVE trading;
2. set `AUTO_EXECUTE_TRADES=1`;
3. place, modify, cancel, or square-off real orders;
4. print/read broker secret payloads except inside the dedicated runtime identity that already requires them;
5. create or export service-account private keys;
6. delete the Google Cloud project or change billing ownership;
7. remove unknown IAM principals automatically without forensic classification.

Analyzer/PAPER remains the default. `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, and `ANALYZE_MODE=1` are mandatory production deployment locks until a separate explicit human live-enablement process exists.

## Identity separation

- `genesis-system3-automation`: normal deployment/configuration identity. No broker secret payload role.
- `gs3-iam-repair`: primary guarded IAM-reconciliation identity.
- `gs3-iam-repair-b`: fallback guarded IAM-reconciliation identity used only if the primary repair path itself fails. Either repair identity may restore only the repository-declared System3 IAM baseline and known safety deny-lists through the canonical repair workflow; neither may execute the Dhan rotation job or read broker secret payloads.
- `genesis-system3-dhan-rotator`: only identity that reads PIN/TOTP/client-id/access-token material and adds a new canonical access-token version.
- `gs3-scheduler`: normal 07:30 Asia/Kolkata Dhan rotation invoker.
- `gs3-token-recovery`: bounded manual/recovery invoker.
- `genesis-system3-web`: runtime web identity; may read canonical client-id/access-token and worker token, but must not mint Dhan tokens.

## IAM drift behavior

`deploy/gcp/system3_iam_baseline.json` is the machine-readable minimum authority baseline.

When Cloud Run Auto Deploy fails due to missing declared IAM:

1. `GCP Authority Repair` runs from trusted `main`.
2. It first authenticates as `gs3-iam-repair` through a WIF claim restricted to the exact repair workflow. If that path fails, `gs3-iam-repair-b` performs the same bounded reconciliation.
3. It compares live IAM with the declared baseline.
4. It restores only declared bindings and removes only explicit safety deny-list entries: forbidden broker-secret payload roles on deploy/repair identities and forbidden Dhan rotator invokers.
5. It never reads Secret Manager payloads and never invokes the rotator.
6. It invokes the existing guarded Cloud Run deployment once only when IAM drift was actually repaired.
7. If no declared IAM drift exists, it stops; no retry loop is permitted.

The two repair identities reduce single-identity IAM drift risk. They do not claim immunity from project-owner removal, WIF-provider deletion, organization-level policy changes, account suspension, or other failures above the delegated project control plane.

## Deploy-authority least-privilege state

`genesis-system3-automation` and `github-actions-deploy` do not hold project `roles/run.admin`. Deployment automation operates with Cloud Run developer authority under the repository-declared least-privilege baseline. The machine baseline records `strict_scheduler_only_iam=false` and `deployer_run_admin_temporary=false`.

`strict_scheduler_only_iam=false` remains fail-closed until the project/job authority inventory independently proves that only the intended scheduler and bounded control identities can execute Cloud Run jobs. That separate proof is required before changing strict scheduler-only authority to PASS; it does not justify restoring project-level `roles/run.admin` to deployment identities.

## Broker rotation authority

- Daily scheduler at 07:30 Asia/Kolkata remains the normal mint authority.
- Web self-heal minting is ON for auth-reject only (`DHAN_CANONICAL_ROTATION_SELF_HEAL=1`): web never mints inline; it invokes Job `genesis-system3-dhan-token-rotate` with 900s cooldown. Canonical secret remains `dhan-access-token` only.
- Deploy workflows configure the rotator/scheduler but must not execute the rotator.
- Recovery must remain single-flight/cooldown guarded; repeated mint retries are forbidden.

## Evidence rule

No production-ready claim is allowed from source code alone. Current production proof must be request-scoped/fresh and include applicable exact deployed SHA/revision, runtime safety flags, broker status, health status, and visible production UI data.

A green deployment or 22/22 render-only smoke does not prove semantic data readiness. Stored evidence is historical after capture and must be freshness-validated before time-sensitive use.

## Human-only break-glass boundary

Human intervention can still be required for external account/billing suspension, organization-level policy outside this project, revoked GitHub/GCP account ownership, WIF-provider destruction when neither delegated repair identity can authenticate, external broker identity/MFA reset, or intentionally destructive actions. These are not normal System3 operational tasks.

Even when none of these mandatory human-only blockers exists, agents must still report any optional user-side acceleration action found by the 19-point self-MRI instead of writing a misleading blanket `no action required` statement.
