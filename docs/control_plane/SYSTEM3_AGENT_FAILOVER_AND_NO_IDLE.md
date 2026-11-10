# SYSTEM3_AGENT_FAILOVER_AND_NO_IDLE_V1

Applies only to `psw2025-cmd/Genesis_System3` and GCP `system3-openalgo-safe`.

## Non-negotiable principle

No individual AI agent is a required gate. Evidence and safety predicates are the gates.

If ChatGPT, Claude, Cursor, Codex, Perplexity, Gemini, a laptop operator, or any other agent is unavailable because of billing, quota, access, outage, connector failure, timeout, tool limitation, or account state, work MUST NOT idle when another safe path exists.

Replace the unavailable agent, never weaken the proof requirement.

## Failover order

For each blocked action, try the first safe capable path and immediately move to the next when unavailable:

1. current agent's authoritative cloud connector;
2. governed GitHub Actions / cloud workflow using existing approved WIF authority;
3. GitHub workflow artifacts and cloud-origin evidence;
4. another authorized cloud agent;
5. authorized laptop operator executing CLOUD-ONLY commands against GitHub/GCP, never local runtime authority;
6. independent read-only verifier;
7. user only for genuine owner-only MFA, consent, billing/funding, destructive approval, credential reset, or explicit LIVE authorization.

A provider billing problem (including Claude billing) is an AGENT_AVAILABILITY incident, not a System3 production blocker when another safe verifier/executor exists.

## No-idle execution law

When the current agent cannot execute the next action it MUST, in the same cycle:

1. name the exact required result, not merely the missing tool;
2. attempt safe alternatives available to it;
3. post the blocker, evidence requirement, owner/failover lane, and non-overlap boundary to Issue #188;
4. route the task to the next capable agent without making the user a routine messenger;
5. continue a non-conflicting executable lane while the delegated action runs;
6. consume the first authoritative evidence returned to Issue #188 instead of duplicating work.

`WAITING_FOR_AGENT`, `CLAUDE_UNAVAILABLE`, `NO_CONNECTOR`, `BILLING_ISSUE`, or `I_CANNOT_ACCESS_GCP` are never terminal states by themselves.

## Proof must never be weakened

Failover changes WHO executes, not WHAT constitutes PASS.

User-visible completion still requires the applicable chain:

`current GitHub main -> governed GCP deployment/provenance -> exact serving revision -> same-session authoritative APIs -> frontend store/render -> canonical production /ui semantic proof -> required stability window`.

Backend-only, CI-only, local screenshots, local DBs, local token files, local schedulers, laptop runtime, old artifacts, or another agent's narrative cannot substitute for production proof.

## Cloud-only laptop boundary

A laptop agent may be used as an execution terminal only when it queries authoritative remote GitHub/GCP services. Its local repo, DB, scheduler, token file, `.env`, cached screenshots, or historical runtime remain NON-AUTHORITATIVE. It must post cloud-origin evidence to Issue #188 for cross-verification.

## Multi-validation requirement

Material production claims require independent validation across the applicable boundaries:

- GitHub: current main, PR ownership, exact head/merge SHA and gates;
- GCP: revision, traffic, deployment provenance, safety state;
- API: same-session read-only broker/data responses and metadata-only token authority;
- UI: exact-serving browser-visible semantics, source/freshness and contradictions;
- independent cross-check: second agent or separately generated cloud artifact when practical.

A contradiction fails closed and opens/narrows a blocker; majority vote never overrides fresher authoritative evidence.

## System3 safety invariants

Always preserve:

- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- no real order placement/modification/cancellation;
- no secret payload exposure;
- no blind Dhan mint/rotation;
- no IAM weakening to make evidence pass;
- GCP is the only runtime authority;
- GitHub current main is the only code authority;
- Issue #188 is the canonical coordination bus.

## Required report format

Every material report reconciles:

`PREVIOUS_COMMITMENTS -> COMPLETED -> NOT_COMPLETED -> PROOF -> ROOT_CAUSE -> ALTERNATIVES_TRIED -> FAILOVER_OWNER -> RECOMMENDATION -> NEXT_TARGET_BATCH -> HUMAN_ACTION_REQUIRED`.

`HUMAN_ACTION_REQUIRED=YES` is allowed only after safe agent/cloud alternatives are exhausted and a genuine external owner-only boundary is proven.

## User-facing result rule

Do not burden the user with agent/tool explanations when a safe alternative exists. Prefer:

`STATUS -> ACTION TAKEN -> PROOF -> NEXT ACTION`.

The user should see progress on the canonical production dashboard and Issue #188, not act as the message bus between agents.
