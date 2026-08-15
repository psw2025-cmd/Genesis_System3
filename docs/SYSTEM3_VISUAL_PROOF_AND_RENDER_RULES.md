# System3 Live Visual Proof Rules

**Temporal authority marker:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Canonical temporal policy: `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.

## Non-negotiable rule

No UI-facing feature, fix, broker state, market-data path, model surface, paper-trade surface, or dashboard change may be called resolved/current/live unless a **new request-scoped production browser observation** exists after the current investigation/change.

Stored proof under `reports/latest/`, GitHub artifacts, prior screenshots, or previous workflow runs is historical after capture. It may be used for comparison/root cause, but it cannot answer a later “what does the UI show now?” question.

## Production authority

- Runtime/UI authority: GCP project `system3-openalgo-safe`, region `asia-south1`.
- Cloud Run service: `genesis-system3-web`.
- Public UI: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`.
- Render is retired/non-authoritative and must not be used for current production proof.

## Assistant/agent-owned UI verification

The user is not required to send screenshots.

For a current UI claim the agent must:

1. record the investigation/request start UTC time;
2. start a **new Chrome/WebDriver session** after that time;
3. open the actual GCP production URL;
4. capture fresh screenshots and visible text;
5. capture same-session read-only broker/health/relevant API truth;
6. compare UI and API values/status;
7. record capture UTC timestamps and source URL;
8. after any fix/redeploy/recovery, repeat the browser capture.

Use `scripts/gcp_live_ui_snapshot.py` for full production UI lifecycle proof.
Use `scripts/system3_temporal_truth_guard.py` when evaluating a stored manifest for time-sensitive use.

## Full 22-tab lifecycle

A full UI audit must freshly capture:

`decision-intel`, `truth`, `genesis`, `e2e-proof`, `overview`, `sim-live`, `options-intel`, `chain`, `signals`, `trade`, `paper`, `positions`, `risk-scenarios`, `multibagger`, `prediction-audit`, `performance`, `ml`, `data-integrity`, `broker`, `alerts`, `system`, `gates`.

Each tab requires:
- screenshot;
- visible text;
- capture UTC time;
- active/rendered proof;
- semantic inspection for loading/empty/degraded/error/waiting/unknown states;
- relevant read-only API comparison where applicable.

## What does NOT count as live UI proof

- local Vite/localhost browser smoke;
- screenshot from an earlier workflow/run;
- newest file under `reports/latest/`;
- HTTP 200 alone;
- page root rendered alone;
- source code indicating a component exists;
- a backend JSON response without visual verification for a UI-facing claim;
- a token expiry timestamp used as a proxy for broker connectivity;
- a successful deployment used as a proxy for populated option-chain/market data.

## Semantic truth rule

A data-bearing tab is not PASS because it rendered.

Examples:
- Option Chain must visibly show the expected symbol/expiry/contract/strike data when that data is required for the test condition.
- Broker status in UI must agree with fresh `/api/broker/status` evidence.
- Health/readiness labels must agree with fresh health evidence.
- If market is closed, the audit must distinguish expected after-hours behavior from genuine missing/stale data.
- `—`, `UNKNOWN`, `WAITING`, `LOADING`, `POLL`, `NO DATA`, or similar markers are observations to classify; they must not be silently treated as healthy.
- Contradictory UI states are blockers even when each component rendered successfully.

## Evidence age

Interactive `now/current/live` requests require a new capture started after the request began; a previous artifact cannot be reused even if only minutes old.

Scheduled/automated live verdicts must declare capture time and bounded freshness. Default live-proof freshness ceiling at verdict time is 300 seconds unless a stricter domain rule applies.

If capture time is absent or stale, verdict is not current and a new observation is required.

## Before/after rule

For every UI fix:

1. capture/reproduce the current defect if needed;
2. implement and deploy the fix safely;
3. discard the pre-fix capture as proof of the post-fix state;
4. open a new production browser session;
5. capture the same affected tab(s) again;
6. compare before/after and same-session APIs;
7. only then call the issue resolved.

## Safety

Live proof is read-only:
- `ANALYZE_MODE=1`;
- LIVE trading OFF;
- auto order execution OFF;
- no order mutation endpoints;
- no secret payload exposure.

## Proof hierarchy for current UI

1. Fresh request-scoped GCP production browser capture.
2. Same-session fresh read-only production API evidence.
3. Fresh production logs/runtime metadata.
4. Current serving revision/SHA/config.
5. Source code.
6. Stored historical artifacts for comparison only.

When two agents or artifacts disagree, generate a new live observation. The newer stored artifact does not automatically win; the request-scoped authoritative observation does.
