# Agent Access & Autonomy Guide — Genesis System3

Read this if you are an AI agent (Claude Code, cloud or local, ChatGPT/Codex, Cursor, or any future agent) working on this repo and the owner wants to know why an agent is blocked and how to prevent repeat owner dependency.

Mandatory companion authority: `docs/authority/RUHI_ACCESS_PROVIDER_BLOCKER_CONTRACT.md`.

## 1. Never report an access/provider blocker alone

Any GCP, GitHub, provider, browser, CI, quota, IAM, API, Secret Manager metadata, Cloud Run, Cloud Scheduler, Cloud Logging/Monitoring, Dhan, NSE/BSE, or other access/configuration blocker must immediately be converted into the `ACCESS_RESOLUTION_CARD` defined in the companion RUHI contract.

Agents must provide the fastest safe permanent fix, practical fallbacks, exact owner-only click path when genuinely required, minimum permission/setting, proof, owner, and recheck cadence. Routine work continues in parallel.

## 2. Two different kinds of blocked — do not confuse them

### A. Real access/configuration problems

Examples: missing repo permission, unavailable GitHub App authorization, missing read-only GCP role, unavailable Actions permission, quota exhaustion, or a provider setting that prevents the required read/write operation.

These are configuration/dependency problems. Resolve them through the fastest safe least-privilege path and prove the dependent operation actually works afterward.

### B. Safety boundaries

Do not route around controls that prevent unsafe or irreversible operations such as exposing secret payloads, granting broad privilege without need, bypassing protected-branch controls, destructive production deletion, or enabling/placing LIVE trades without explicit authorization.

A safety boundary is not an excuse to stop. The agent must still provide the safest alternate path that achieves the legitimate engineering goal.

## 3. Current live corrections — 2026-08-28

Agents must live-verify access before repeating historical instructions. Current corrections:

1. **GitHub main protection/ruleset governance exists.** Do not tell the owner to create branch protection again unless a fresh live check proves it is missing or materially broken.
2. **GCP is the authoritative production/deployment platform.** Render is legacy/non-authoritative and must not be treated as an active production dependency.
3. **`/api/healthz` flapping is a reliability defect.** Do not recommend muting/ignoring the alert as the solution. Root-cause the probe/runtime behavior and fix or correctly redefine the probe.
4. **Repository default branch is `main`.** A temporary `git init` warning that says `master` is not repository authority.
5. **Cursor/Bugbot quota exhaustion is not a system-wide stop condition.** Route review/testing to another authorized agent or protected CI while quota is unavailable.
6. **Do not rely on long-lived PATs or service-account JSON when provider-native keyless authorization/WIF/GitHub Apps can satisfy the requirement.**

## 4. Preferred permanent access model

Use least privilege and separate identities by function.

### Read/forensic identity

Enough GCP permission to inspect Cloud Run services/revisions/traffic/jobs, Cloud Scheduler execution state, Logging, Monitoring/alerts, deployment metadata, and Secret Manager name/version metadata where required. It should not read secret payloads merely for routine diagnostics.

### Developer/PR identity

Enough GitHub permission to push non-protected branches, create/update PRs, comment Issue #188, read Actions logs/artifacts, and trigger allow-listed diagnostic workflows.

### Controlled deploy identity

Used only by protected CI/workflows after required checks. It may deploy or rollback approved Cloud Run changes but should not manage project IAM or expose secrets.

### Broker/token operator

Used only by the guarded canonical Dhan token workflow. Normal coding agents do not need broker secret payload access.

## 5. Where any agent finds current truth

Check these in this order instead of waiting for owner-forwarded messages:

1. Current GitHub `main` in `psw2025-cmd/Genesis_System3`.
2. GitHub Issue #188 — canonical coordination/status bus.
3. `reports/coordination/ruhi_task_ledger.csv` and current coordination artifacts.
4. `docs/RUHI_RULE_V2.md`, `AGENTS.md`, and `docs/authority/*`.
5. Authoritative GCP/live proof, including the Live Proof Center when available.
6. Production URL/API/browser evidence tied to serving SHA.
7. Gmail only as transport/notification; durable state belongs back in GitHub.

Local laptop state is not production authority.

## 6. When owner action is actually allowed

Owner action is reserved for genuine owner-only boundaries such as:

- billing/subscription/payment/quota purchase;
- provider account ownership/consent;
- MFA or broker-account credential reset;
- installation/authorization of a GitHub/GCP/provider app or permission grant that current agents cannot change;
- destructive action requiring explicit approval;
- explicit LIVE trading approval.

Even then, the agent must provide kid-level instructions in one pass:

`Open <provider> -> click <menu> -> click <setting> -> choose <exact value> -> Save -> verify <non-secret proof>`.

Never send vague instructions such as `fix IAM`, `check permissions`, or `configure GCP`.

## 7. Completion proof

Access/configuration work is complete only when the dependent operation succeeds.

Examples:

- GitHub access complete -> agent pushes a test/current branch or performs the intended repo operation successfully.
- Actions access complete -> intended workflow/log/artifact operation succeeds.
- GCP read access complete -> agent reads the required service/revision/log/metric evidence.
- controlled deploy access complete -> protected workflow can deploy/rollback the approved runtime change.

A screenshot of settings or a claim that access 'should work' is not completion.

## 8. Do not stop at the first unavailable tool

Before escalating to the owner, try safe available alternatives: another authorized cloud agent, GitHub connector, existing Actions workflow, Live Proof Center, production API/browser proof, or provider-native keyless bridge.

If one agent cannot push, another authorized agent should integrate the patch. If one reviewer has quota limits, use another reviewer/CI path. If direct GCP CLI is unavailable, consume current cloud-generated evidence while the missing access is repaired.

## 9. No repeated nagging

Track one blocker ID with current evidence, owner, next check and closure proof. Do not create repeated owner emails for the same unchanged blocker. Send a new escalation only when the root cause, impact, required action, or available solution materially changes.
