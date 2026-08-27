# Agent Access & Autonomy Guide — Genesis System3

Read this if you are an AI agent (Claude Code, cloud or local, ChatGPT/Codex, Cursor,
or any future agent) working on this repo, and the owner wants to know:
*"why did my agent get blocked, and how do I make sure it never happens again?"*

## 1. Two totally different kinds of "blocked" — don't confuse them

**A. Real access problems (fixable, one-time, permanent once done)**
Missing GitHub permissions, revoked collaborator access, no branch protection,
legacy auto-deploy fighting the real one, missing cloud IAM roles. These are
plain configuration gaps. Fix the config once, they never come back.

**B. The safety guard (NOT fixable, not a setting, intentional forever)**
Every well-built AI agent has a built-in check that stops it from: touching
real money/trades, handling passwords/tokens/secrets, force-pushing or deleting
things, or granting itself more power. This is not stored in any settings file
— you cannot switch it off, and no agent should ever be asked to. It exists so
that even if 5 different agents are all working on this repo unsupervised, none
of them can accidentally (or under confused instructions) do something
irreversible. **Treat requests to remove this as a red flag, not a task.**

If an agent tells you "I can't do that, it's a hard safety guard" — that is
correct behavior, not a bug to route around. Ask it for the plain-English
version of the manual step instead (it should offer one).

## 2. The real access issues found in this repo (as of 2026-08-27) — one-time fixes

| # | Problem | One-time fix | Who does it |
|---|---|---|---|
| 1 | No branch protection on `main` → 24+ PRs stuck in conflict, agents keep re-fixing the same bugs | GitHub → repo **Settings → Branches → Add rule** → branch = `main` → check "Require a pull request before merging" + "Require status checks to pass" → **Create** | Owner (human), 1x |
| 2 | Cursor's push access to the repo was revoked | GitHub → repo **Settings → Collaborators** (or reinstall the Cursor GitHub App) → re-add Cursor | Owner (human), 1x |
| 3 | Legacy Render auto-deploy still fighting the real GCP Cloud Run deploy (issue #179) | Render dashboard → the old backend/worker services → turn OFF auto-deploy | Owner (human), 1x |
| 4 | An agent has no GitHub credentials at all (fresh machine/cloud sandbox) | That agent runs `gh auth login` once (or is given a repo-scoped token with `repo`+`workflow` scopes) | Whoever sets up that agent, 1x per agent |
| 5 | `/api/healthz` alert emails fire every 20-90 min | This is a flaky check, not a real outage (issue #187) — safe to mute/ignore until someone fixes the check's sensitivity | No action needed urgently |

Do all 5, once, and the *actual* recurring problems agents have been emailing
about go away. Nothing needs to be "re-done" — GitHub settings and IAM roles
are permanent until someone changes them again.

## 3. Where any agent finds live 24/7 truth — no need to ask the owner

Every agent (cloud or local) should check these, in this order, instead of
guessing or waiting on an email:

1. **GitHub Issue #188** — `psw2025-cmd/Genesis_System3` — the live status bus.
   Anyone can `gh issue view 188 --repo psw2025-cmd/Genesis_System3` 24/7, no
   special access needed beyond read access to the repo.
2. **Live health/state, no auth needed:**
   `https://genesis-system3-web-doq2wplepa-el.a.run.app/api/healthz`
   `https://genesis-system3-web-doq2wplepa-el.a.run.app/api/state`
3. **`AGENTS.md`** (repo root) — architecture, authority, safety defaults.
4. **`docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md`** and
   **`docs/authority/*`** — full operating rules.
5. **This file** — access/permission troubleshooting.

None of these require the owner to forward an email. Any agent with plain
read access to the repo and a browser/HTTP client already has 24/7 access to
the real, current truth.

## 4. What will always still need a one-time human click

- Anything involving real money/trades — permanently blocked, by design.
- Anything involving passwords, API keys, tokens, service-account JSON.
- Deleting branches, force-pushing, merging straight to `main` without review.
- Changing security/branch-protection/IAM settings themselves.

These aren't "access issues" to fix — they're the whole point of the safety
gate. Fixing items 1–5 in section 2 removes every *real* blocker; these four
stay, on purpose, forever.
