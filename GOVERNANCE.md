# Genesis System3 Production Governance

**Temporal authority marker:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Canonical temporal policy: `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.

## Authority

- Code/config authority: `psw2025-cmd/Genesis_System3`.
- Production authority: GCP project `system3-openalgo-safe`, region `asia-south1`, Cloud Run service `genesis-system3-web`.
- Broker authority: Dhan.
- Render.com hosting is retired. Angel-era deployment/broker material is historical/non-authoritative.
- PAPER/ANALYZER is the production safety posture until separately and explicitly proven/authorized otherwise.

## No permanent “Production Ready” sentence

A historical document, previous PASS, old proof pack, or old screenshot must never permanently declare the system production-ready.

**Production readiness is a time-bounded verdict**, not a repository fact. It must be recomputed from fresh evidence for the current serving deployment and current investigation window.

Any old statement such as “Production Ready as of <date>” is historical only and cannot satisfy a current readiness claim.

## Temporal truth governance

`latest` is not `live`.

- `reports/latest/` = latest stored report, not current runtime truth.
- `SYSTEM_STATE.md` / `CHANGE_LOG.md` = context/history, not current runtime truth.
- GitHub artifact/workflow = evidence of what that run observed, not a guarantee the state persists.
- Source code = intended behavior, not proof of serving runtime/UI behavior.

For any claim implying `now/current/live/present/still/fixed now/connected now/UI now`, generate new request-scoped evidence after the current investigation begins.

For production UI truth, use a new Chrome/WebDriver session against the actual GCP production URL and capture fresh screenshots/visible text plus same-session read-only API evidence.

Use:
- `scripts/gcp_live_ui_snapshot.py` for the 22-tab production UI lifecycle;
- `scripts/system3_temporal_truth_guard.py` for machine freshness validation.

## Production-ready gate

A current production-ready verdict requires all applicable conditions to be proven from current evidence:

1. Exact serving GCP revision and source SHA are identified.
2. Runtime safety flags prove ANALYZER/PAPER; LIVE/order execution remains disabled.
3. Broker truth is freshly observed and internally consistent.
4. Health/readiness truth is freshly observed.
5. All 22 canonical production UI tabs are freshly captured from the actual production URL.
6. Data-bearing tabs have semantic proof of expected data/state; render-only or HTTP 200 is insufficient.
7. Option-chain/market-data freshness is proven where applicable.
8. UI-visible status matches same-session backend/API truth; contradictions are blockers.
9. Required CI/security/deployment gates for the exact relevant source are satisfied or explicitly classified.
10. IAM/runtime authority is within the declared safety policy; known temporary debt is not mislabeled as closed.
11. No unresolved P0/P1 blocker remains hidden by an older green artifact.

If any required condition is missing, stale, contradictory, or not observable, verdict is `NOT_PROVEN`, `BLOCKED`, or `FAIL` as appropriate—not PASS.

## UI lifecycle governance

A full UI audit means the actual production service, not localhost/Vite, and includes:

`decision-intel`, `truth`, `genesis`, `e2e-proof`, `overview`, `sim-live`, `options-intel`, `chain`, `signals`, `trade`, `paper`, `positions`, `risk-scenarios`, `multibagger`, `prediction-audit`, `performance`, `ml`, `data-integrity`, `broker`, `alerts`, `system`, `gates`.

For each tab capture:
- screenshot;
- visible text;
- UTC observation time;
- rendered/active state;
- semantic loading/empty/error/degraded observations;
- relevant API comparison.

A 22/22 render PASS alone is not production data readiness.

## Evidence classification

Use the classes defined in the temporal policy. Only request-scoped live browser/API/log observations or freshly queried deployment metadata can support a current claim within their exact scope.

Stored artifacts become historical after capture. They remain valid for timeline, regression, before/after, and root-cause analysis, but cannot silently answer a later “what is true now?” question.

## Safety governance

Mandatory until separate live-enablement authority exists:

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- no real order place/modify/cancel/square-off;
- no broker secret payload exposure;
- read-only production UI/API verification is allowed;
- Dhan token mint authority remains restricted to dedicated scheduler/recovery identities.

## Multi-agent governance

All agents must read the temporal policy before using state/proof artifacts.

Before changing code or claiming current status:
- inspect current main/open PRs;
- inspect current serving production evidence when runtime-relevant;
- do not overwrite parallel agent work;
- do not use a stale branch/PR narrative as current truth;
- if agents disagree about live state, generate a new observation and use it as arbiter.

## Completion rule

Code written != complete.
CI green != complete.
Deployment green != complete.
HTTP 200 != complete.
Tab rendered != complete.

Completion requires the requested end state to be freshly and directly proven at the authoritative boundary where the user experiences it.
