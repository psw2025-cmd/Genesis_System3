# RUHI Access / Provider / GCP Blocker Resolution Contract

Status: MANDATORY for every ChatGPT, Claude, Cursor, Codex, cloud/browser, GCP, GitHub, or future agent working on Genesis System3.

Authority: complements `docs/RUHI_RULE_V2.md`, `AGENTS.md`, Issue #188, and `docs/authority/AGENT_ACCESS_AND_AUTONOMY_GUIDE.md`.

## 1. Core rule — never report a blocker alone

When any agent discovers an access, permission, provider, GCP, GitHub, browser, CI, quota, API, IAM, Secret Manager metadata, Cloud Run, Cloud Scheduler, Cloud Logging/Monitoring, Dhan, NSE/BSE, or other external-system blocker that can slow the System3 goal, the agent MUST immediately convert it into an `ACCESS_RESOLUTION_CARD`.

Forbidden incomplete reports include:

- `blocked`
- `no access`
- `ask the user`
- `GCP issue`
- `provider issue`
- `permission denied`
- `quota issue`
- `cannot push`

unless the same update also contains the resolution card below.

## 2. ACCESS_RESOLUTION_CARD — mandatory fields

Every card must contain:

- `BLOCKER_ID`
- `FOUND_AT_IST`
- `AFFECTED_SYSTEM_GOAL`
- `EXACT_FAILURE`
- `IMPACT_NOW`
- `CAN_AGENT_FIX_NOW = YES/NO`
- `FASTEST_SAFE_OPTION`
- `FALLBACK_OPTION_2`
- `FALLBACK_OPTION_3` when a third practical option exists
- `EXACT_PROVIDER_OR_CONSOLE`
- `KID_LEVEL_PATH_OR_COMMAND`
- `MINIMUM_PERMISSION_OR_SETTING`
- `RESPONSIBLE_AGENT`
- `OWNER_ONLY_STEP` if genuinely required
- `PROOF_REQUIRED`
- `RECHECK_CADENCE`
- `PARALLEL_WORK_CONTINUES`
- `USER_ACTION_REQUIRED = YES/NO`

A blocker without these fields is not considered properly handled.

## 3. Agent-first rule

Before escalating to the owner, the discovering agent MUST try every safe capability already available to it, including where applicable:

1. current GitHub connector / repo access;
2. existing Cloud/GCP-capable agent lane;
3. approved GitHub Actions workflow or workflow_dispatch;
4. Live Proof Center / GCP-generated evidence;
5. current API/browser proof;
6. another already-authorized agent that has the missing capability;
7. provider-native keyless identity / WIF / GitHub App installation;
8. safe read-only alternative evidence path.

Do not ask the owner to act merely because the first agent lacks one tool.

## 4. Owner escalation boundary

`USER_ACTION_REQUIRED=YES` is permitted only when all safe agent paths above are exhausted and the remaining step is genuinely owner-only, such as:

- billing/subscription/payment/quota purchase;
- provider account ownership/consent;
- MFA or broker-account credential reset;
- GitHub/GCP/App installation or permission grant that the current agent is not authorized to change;
- destructive action requiring explicit approval;
- explicit LIVE trading authorization.

When owner action is required, instructions MUST be kid-level and actionable in one pass:

`Open <provider> -> click <menu> -> click <setting> -> choose <exact value> -> Save -> send/verify <non-secret proof>`.

Never send the owner vague instructions such as `fix IAM`, `check permissions`, or `configure GCP`.

## 5. Fastest-safe-path rule

For each blocker, agents must rank solutions in this order:

1. fastest safe permanent fix;
2. fastest safe temporary bridge that does not weaken security;
3. independent fallback provider/path if the primary remains unavailable.

Prefer permanent provider-native configuration over repeated manual work.

Examples:

- Prefer GitHub App / repository-scoped authorization over repeated patch emailing.
- Prefer GCP Workload Identity Federation/keyless identity over service-account JSON keys.
- Prefer canonical Cloud Run/Cloud Scheduler workflows over laptop scripts.
- Prefer metadata-only Secret Manager access for diagnostics; never expose secret payloads.
- Prefer approved deployment workflows over broad project Owner/Admin rights.

## 6. GCP minimum access matrix

The system should maintain least-privilege identities that allow agents to complete routine work without owner relay.

### Read/forensic identity
Needs enough permission to read:

- Cloud Run services, revisions, traffic and jobs;
- Cloud Scheduler jobs/execution status;
- Cloud Logging;
- Cloud Monitoring/alerts;
- Secret Manager secret names/version metadata only when required;
- deployment metadata and project resource state.

It must NOT read secret payload values merely for convenience.

### Developer/PR identity
Needs enough permission to:

- read/write branches;
- push commits to non-protected branches;
- create/update PRs;
- comment Issue #188;
- read Actions runs/logs/artifacts;
- trigger allow-listed diagnostic workflows.

### Controlled deploy identity
Used only by protected CI/workflow after required checks. It may deploy/rollback approved Cloud Run runtime changes, but should not edit project IAM or expose secrets.

### Broker/token operator
Used only by the guarded canonical token-recovery/rotation workflow. Normal coding agents must not receive broker secret payload access.

## 7. GCP/provider defect handling

Whenever a GCP/provider-related defect is observed, the agent must immediately answer all of these before moving on:

1. Is this a real production defect or only a probe/tool limitation?
2. Which exact GCP service/provider component owns it?
3. What live proof confirms it?
4. Can the agent repair it directly now?
5. What exact permission/configuration is missing if not?
6. What is the fastest permanent fix?
7. What fallback keeps work moving now?
8. What UI/API/runtime proof closes the blocker?
9. Who owns the next action?
10. When will it be rechecked?

## 8. No idle / no repeated nagging

If a blocker cannot be fixed immediately, agents must continue all non-overlapping work that does not depend on that blocker.

Do not repeatedly email the same unresolved owner action without new evidence. Track one `BLOCKER_ID`, its last proof, next check, and escalation status.

If new evidence changes impact/root cause/solution, update the same blocker rather than creating duplicate noise.

## 9. Current known corrections — 2026-08-28

These statements override stale historical guidance:

- GCP is the authoritative production/deployment platform. Render is legacy/non-authoritative and must not be presented as an active production dependency.
- GitHub `main` currently has active protection/ruleset governance; agents must live-verify before telling the owner to configure it again.
- `/api/healthz` flapping is a reliability defect to root-cause, not something to solve by muting/ignoring alerts.
- Current repo default branch is `main`; temporary `git init` messages mentioning `master` do not change repo authority.
- Current production/runtime truth must come from GCP/live proof, not laptop/local watcher state.
- Cursor/Bugbot quota exhaustion is an accelerator loss, not a reason for all engineering to stop; route review through another capable agent/CI path while quota is unresolved.

## 10. Completion rule

An access/provider blocker is `COMPLETE` only when:

`setting/access change -> agent can perform required operation -> operation succeeds -> exact proof recorded -> dependent System3 task proceeds`.

A screenshot of a settings page, a permission grant alone, or an agent statement that access 'should work' is not completion.

## 11. User-facing format

For owner-only action, keep the user message short and kid-level:

**Problem:** one sentence.

**Do this now:** exact click/path sequence.

**Why:** one sentence explaining what it unlocks.

**After that:** state exactly what agents will verify/do automatically.

If no owner action is required, say `USER ACTION: NONE` and continue the work instead of asking the user for confirmation.
