# Genesis System3 — Gemini Operating Contract

**Highest-priority temporal rule:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Before every investigation read:
1. `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`
2. `docs/authority/AUTONOMOUS_OPERATIONS_POLICY.md`
3. `docs/project_control/SYSTEM3_MASTER_GOAL_LOCK.md`
4. `AGENTS.md`

Any older session note, `SYSTEM_STATE.md`, `CHANGE_LOG.md`, `reports/latest/`, screenshot, proof pack, PR narrative, or workflow artifact is historical/contextual until it is revalidated against current production.

## Authority

- Code/config: `psw2025-cmd/Genesis_System3`.
- Production: Google Cloud project `system3-openalgo-safe`, region `asia-south1`, service `genesis-system3-web`.
- Public production UI: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`.
- Broker: **Dhan**. Angel/Render-era instructions are retired/non-authoritative.
- Keyless GitHub Actions -> GCP WIF is the normal automation path.

## Current/live evidence law

Never answer or reason about `now/current/live/present/still/fixed now/visible now` using an existing stored artifact.

For any new live UI/runtime question, create a new request-scoped observation after the current investigation starts:

- new Chrome/WebDriver production session;
- actual GCP production URL;
- fresh screenshot + visible text;
- same-session read-only production API truth;
- explicit capture UTC time;
- UI/API contradiction check.

For full UI analysis, use the 22-tab lifecycle in `scripts/gcp_live_ui_snapshot.py`. A green local browser smoke or green deployment is not equivalent to populated production data.

`reports/latest/` means newest stored report only. It has zero automatic authority for a later `live/current` claim.

Use `scripts/system3_temporal_truth_guard.py` when consuming stored temporal evidence. If capture time is absent, older than the allowed window, or started before the current request, fail closed and re-observe.

## Gemini investigation duty

For each problem:

1. Establish whether the evidence is fresh-live or historical.
2. Independently verify current production truth before accepting another agent's runtime conclusion.
3. Inspect source/logs/config only after the current symptom is established.
4. Produce root-cause hypotheses and compare safe alternatives.
5. Cross-check the proposed fix for regressions, safety, and semantic correctness.
6. After implementation, require a **new** production proof. Never reuse pre-fix evidence.

If another agent's current-state claim is based on an older screenshot/report, reject the current-state conclusion and request/generate new live evidence.

## Safety

- PAPER/ANALYZER only.
- `ANALYZE_MODE=1`.
- `LIVE_TRADING_ENABLED=0`.
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`.
- `AUTO_EXECUTE_TRADES=0`.
- No real order mutation.
- No secret payload exposure.
- Read-only production UI/API/market-data verification is permitted for evidence.
- Dhan token minting is restricted to the dedicated scheduler/recovery path in repository governance.

## Multi-agent coordination

Other agents may change the repository concurrently. Always inspect current main/open PR state before proposing or editing. Never silently overwrite newer work or use stale PR descriptions as current runtime truth.

When agents disagree about a live state, the arbiter is a newly generated authoritative observation—not consensus and not the newest stored artifact.

## Evidence hierarchy for current truth

1. Fresh request-scoped production browser observation.
2. Fresh same-session production API observation.
3. Fresh production logs/runtime metadata.
4. Current deployed revision/SHA/config.
5. Source code.
6. Historical artifacts/reports, explicitly labeled historical.
