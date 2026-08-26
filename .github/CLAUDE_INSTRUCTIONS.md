# Genesis System3 — Permanent Claude Operating Instructions

**Highest-priority temporal rule:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Read first:
1. `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`
2. `docs/authority/AUTONOMOUS_OPERATIONS_POLICY.md`
3. `docs/project_control/SYSTEM3_MASTER_GOAL_LOCK.md`
4. `AGENTS.md`

## Authority

- GitHub repository: `psw2025-cmd/Genesis_System3`.
- Production platform: Google Cloud project `system3-openalgo-safe`.
- Region: `asia-south1`.
- Cloud Run service: `genesis-system3-web`.
- Production UI: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`.
- Dhan rotator job: `genesis-system3-dhan-token-rotate`.
- Broker: **Dhan**.
- Hosting lock: GCP Cloud Run only. Render.com is forbidden. Never recreate `render.yaml`, never add Render as production, never deploy workers to Render. Canonical lock: `docs/authority/RENDER_HOSTING_FORBIDDEN.md`. Angel-era material is historical/non-authoritative.
- Normal cloud authentication: GitHub Actions keyless Workload Identity Federation. Do not create/export long-lived service-account JSON keys.

## Temporal truth: mandatory for every Claude instance

`latest` does not mean `live`.

Do not use the newest stored screenshot, `reports/latest/`, prior workflow artifact, prior API response, `SYSTEM_STATE.md`, `CHANGE_LOG.md`, PR description, or old proof pack to answer a later question about what is happening now.

For any claim implying **now/current/live/present/still/fixed now/connected now/UI now**:

1. Record the investigation/request start time in UTC.
2. Generate a new observation after that time.
3. For UI claims, open a **new Chrome/WebDriver session** to the actual GCP production URL.
4. Capture fresh screenshots + visible text.
5. Capture relevant read-only production APIs in the same proof session.
6. Compare UI/backend truth and report contradictions.
7. Include capture time/evidence age.
8. After any fix, deployment, broker recovery, or token rotation, run a new capture. Pre-change proof is historical.

Use `scripts/gcp_live_ui_snapshot.py` for the fresh full production UI lifecycle and `scripts/system3_temporal_truth_guard.py` when evaluating stored evidence.

A CI/deploy SUCCESS means only that its actual assertions passed. It does not prove live market data is populated. HTTP 200 and “tab rendered” are not enough for semantic UI readiness.

## Full UI proof

For a full UI/current-state investigation, capture all 22 canonical tabs from the actual production service in one request-scoped browser lifecycle. Save screenshots, visible text, per-tab timestamps, and start/end broker/health API snapshots. Investigate semantic empty/loading/degraded states even if rendering succeeds.

## Safety

- PAPER/ANALYZER only.
- `ANALYZE_MODE=1`.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- No real order placement/modification/cancellation/square-off.
- No broker secret payload exposure.
- Read-only production UI/API/market-data verification is allowed.
- Dhan token minting only through the dedicated bounded scheduler/recovery authority defined in governance.

## Engineering and multi-agent behavior

- Inspect current `main`, serving production state, and relevant open PRs before editing.
- Other agents may run in parallel; do not silently overwrite newer changes.
- An old PR narrative cannot establish current runtime truth.
- Verify the symptom from current authoritative evidence, then investigate root cause.
- Implement on a branch; run exact-head tests/CI; merge only proven changes.
- After merge/deploy, prove the actual end state with a new live observation.
- If agents disagree about current production state, generate a new live observation. Do not vote between stale artifacts.

## User-action boundary

Routine engineering should be autonomous through GitHub/GCP: investigation, code fixes, CI, deployment, IAM drift repair, logs, browser proof, and bounded broker recovery. User action is reserved for true break-glass/account-level events outside delegated authority.

## Dashboard-impact blocker and owner escalation

Claude must apply `SYSTEM3_USER_ACTION_ESCALATION_V2`. When a verified owner
account/access/settings action can accelerate any dashboard/data/API↔UI/broker/
prediction/PAPER/deploy/proof dependency, report the fastest safe option and
all materially distinct safe alternatives, continue unblocked forensic work,
and publish a stable action card to chat, verified connected mail, and Issue
#188. Track it until practical proof, not acknowledgement, closes it. Never
guess a recipient or expose secrets.

## Evidence hierarchy for a current-state claim

1. Request-scoped fresh production browser evidence.
2. Same-session fresh production API evidence.
3. Fresh production logs/runtime metadata.
4. Current serving SHA/revision/config.
5. Source code.
6. Stored reports/artifacts/history, clearly labeled historical.

**Canonical temporal policy:** `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.
