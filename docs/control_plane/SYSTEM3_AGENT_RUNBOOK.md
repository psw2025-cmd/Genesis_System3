# System3 Agent Runbook

## Purpose

This file controls how ChatGPT, Replit Agent, Cursor, Codex, Gemini, or any other agent must work on System3.

No agent should perform random fixes. Every action must improve a named blocker or proof gate.

## Standing Safety Rules

- Do not enable live trading.
- Do not change Dhan credentials, `.env`, `.secrets`, token files, or broker secrets.
- Do not change order placement from blocked to allowed.
- Do not claim live readiness.
- Do not delete old documentation without classification and approval.
- Do not patch runtime code before blocker evidence is logged.

## Standard Agent Cycle

```text
1. Read SYSTEM3_MASTER_TRACKER.md
2. Read SYSTEM3_BLOCKER_REGISTER.md
3. Read current runtime truth/proof if available
4. Generate blocker report before patching
5. Patch only the approved blocker
6. Run proof/test
7. Update master tracker and blocker register
8. Return changed files, commands, outputs, remaining blockers
```

## Required Agent Output

Every agent response must include:

| Output | Required |
|---|---|
| Goal being improved | Yes |
| Blocker ID | Yes |
| Files changed | Yes |
| Files intentionally not touched | Yes |
| Commands/tests run | Yes |
| Before proof | Yes |
| After proof | Yes |
| Remaining blockers | Yes |
| Safety confirmation | Yes |

## First Mandatory Reports

Before broad fixes, the agent must generate:

```text
reports/latest/markdown_inventory.md
reports/latest/markdown_inventory.json
reports/latest/documentation_contradictions.md
reports/latest/system3_blocker_report.md
reports/latest/system3_blocker_report.json
reports/latest/option_strike_visibility.md
reports/latest/option_strike_visibility.json
reports/latest/model_accuracy_report.md
reports/latest/model_accuracy_report.json
```

## Replit-Specific Rules

Because GitHub workflow may be unavailable due billing, Replit can be used as the active repair/staging workspace.

Replit agent must:

1. Work only on a safe copied project.
2. Use Replit Secrets for credentials.
3. Never commit credentials into code.
4. Generate reports locally before proposing deployment.
5. Export a safe ZIP after successful proof.
6. Keep Render/current dashboard unchanged unless user explicitly migrates runtime.

## GitHub-Specific Rules

If GitHub is usable:

1. Documentation-only commits are allowed when explicitly requested.
2. Runtime code changes should go through branch/PR where possible.
3. Do not merge old stale PRs without fresh proof.
4. Do not trust historical `FINAL/COMPLETE` docs over current runtime truth.

## Patch Approval Matrix

| Patch type | Allowed without extra confirmation? | Notes |
|---|---|---|
| Add markdown control files | Yes if requested | Safe documentation control |
| Add report scripts | Yes if no credentials touched | Must be read-only by default |
| Fix false alert logic | Yes after proof | Must keep PAPER/live blocked |
| Change dashboard hard-coded proof gates | Yes after report | Must clearly label runtime/static |
| Change strategy/model logic | No | Needs separate approval |
| Change broker/order routing | No | High risk |
| Enable live trading | No | Explicit future approval only |
| Delete old docs | No | Archive classification first |

## Proof Standard

A fix is accepted only if it includes:

```text
before state -> patch -> test command -> after state -> blocker update
```

If proof is missing, the blocker remains open.
