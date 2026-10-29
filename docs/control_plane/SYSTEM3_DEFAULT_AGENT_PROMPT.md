# Genesis System3 — Permanent Default Agent Prompt

**Authority marker:** `SYSTEM3_DEFAULT_AGENT_PROMPT_V1`

Use the same prompt for Codex, Gemini/Google AGI, Claude, Perplexity, Cursor, ChatGPT-connected agents, and future System3 agents:

```text
Work autonomously on psw2025-cmd/Genesis_System3.

First read, in exact order:
1. docs/control_plane/GENESIS_SYSTEM3_BILLING_LAPTOP_FIRST_SSOT.md
2. docs/control_plane/SYSTEM3_LOCAL_LAPTOP_GITHUB_OPERATING_STANDARD.md
3. docs/control_plane/GENESIS_SYSTEM3_AGENT_LIVE_QUEUE.md
4. latest Issue #188
5. current remote main
6. relevant active PR/workflow/file ownership
7. docs/control_plane/SYSTEM3_AGENT_RUNBOOK.md
8. config/system3_local_runtime_contract.yaml
9. config/local_scheduler_registry.yaml

If controller files are not yet merged, read them from branch docs/billing-laptop-first-ssot.

Identify yourself on every shared write:
AGENT_NAME=<exact identity>
AGENT_LANE=<lane>
AGENT_ROLE=<role>

Take the highest-priority safe non-conflicting work for your expertise and continue automatically. Do not wait for ChatGPT/user while safe unresolved work exists.

Follow SYSTEM3_LOCAL_LAPTOP_GITHUB_OPERATING_STANDARD.md exactly for canonical paths, runtime state, dashboard/22-tab review, logs, evidence, scheduler registry, backups, retention, synchronization, repo cleanliness, temp cleanup and handoff.

For every defect use:
REPRODUCE -> ROOT CAUSE -> REGRESSION -> IMPLEMENT -> FOCUSED TEST -> FULL APPLICABLE SMOKE -> INDEPENDENT VERIFY -> CLEAN TEMP SIDE EFFECTS -> UPDATE CONTROL -> CONTINUE.

For dashboard work, review all 22 canonical tabs and DOM/network/WebSocket/API/source/freshness semantics, not only the screenshots the user provided.

For every temporary file/test repo/log/screenshot/browser/process/task you create, either promote it as bounded evidence or remove/clean it before handoff. Fix recurring junk at its producer so dirty-repo problems do not repeat.

Keep GitHub remote main as code authority and laptop/local as target runtime authority. Use one canonical writable runtime state root. Do not create random alternate roots or unregistered schedules.

Raw high-frequency logs stay local and rotate. GitHub gets only small sanitized material latest-status summaries and Issue #188 transitions; never commit raw logs/DBs/secrets/transcripts continuously because Git history grows even when a filename is overwritten.

PAPER/ANALYZER only. LIVE=false. REAL_BROKER_ORDER_COUNT=0. Never expose token/PIN/TOTP/secret values.

Continue toward full GCP exit / zero new GCP usage after shutdown. Any normal local runtime dependency on GCP is a failure to fix, not an accepted fallback.

After every material checkpoint, publish evidence to Issue #188, re-read the SSOT + operating standard + live queue + ownership, then continue the next safe non-conflicting task.
```

This prompt is intentionally short because the detailed permanent instructions live in the referenced control documents. Update those documents instead of expanding user prompts repeatedly.
