# Genesis System3 Temporal Truth and Live Evidence Policy

**Authority:** This policy is mandatory for every human, AI agent, CLI agent, workflow, audit, report, and dashboard proof process in `psw2025-cmd/Genesis_System3`.

**Policy marker:** `SYSTEM3_TEMPORAL_TRUTH_V1`

## Core law

`latest` is not the same as `live`.

A file under `reports/latest/`, the newest GitHub artifact, the newest screenshot, the newest workflow run, `SYSTEM_STATE.md`, `CHANGE_LOG.md`, a proof pack, a previous API response, or an earlier browser capture is **historical evidence after it is captured**. It may explain what happened, but it MUST NOT be represented as the current/present/live state unless a freshness contract explicitly permits that use.

For any claim containing or implying **now, current, present, live, still, currently, latest live, working now, visible now, connected now, healthy now, fixed now, UI now**, the evidence MUST be generated from a new live observation performed for that investigation/request.

## Mandatory request-scoped current-truth sequence

For UI-facing production truth, the only acceptable sequence is:

1. Record investigation/request start time in UTC.
2. If the investigation follows a deploy-triggering change, first prove the authoritative production service is serving the exact intended GitHub SHA.
3. Open the authoritative GCP production URL in a **new Chrome/WebDriver browser session**.
4. Capture the relevant live tab(s) after the request/investigation start time and after serving-SHA convergence.
5. Capture visible page text and a timestamped screenshot.
6. Capture the relevant read-only production APIs during the same proof session.
7. Compare UI-visible state with backend/API state and identify contradictions.
8. Re-check serving SHA at the end of capture; it must still match the intended SHA.
9. Record capture start/end UTC, source URL, tab, GitHub run ID/attempt/SHA, serving SHA/revision when applicable, and safety state.
10. Report the evidence time to the user/agent. Never hide evidence age.
11. If a fix is made, the previous capture becomes historical. Run a **new** production browser proof before claiming the fix is visible/live.

A pre-existing artifact MAY NOT satisfy a new request for `live/current/now`, even if it is the newest stored artifact.

## Exact-serving-SHA lock

A fresh browser session can still be wrong when it starts during a deployment race. A workflow triggered by the same `main` push as Cloud Run deployment can execute before the new revision receives production traffic.

Therefore, for any post-deploy/current-main UI proof:

- query the authoritative public `/api/deploy/info` endpoint before the capture;
- compare its serving `git_sha` with the intended/current GitHub SHA;
- wait boundedly for convergence rather than photographing the previous revision;
- fail closed as `NOT_CURRENT_SERVING_SHA` if convergence does not occur;
- capture only after convergence;
- re-check the serving SHA at the end of the browser lifecycle;
- reject the proof if the serving SHA changes or does not match at either boundary.

The production frontend itself consumes `/api/deploy/info`; proof code must use the same canonical route. A route spelling mismatch is a proof failure, not a reason to weaken or bypass the serving-SHA lock.

Artifact timestamp, GitHub run SHA, or workflow start time alone does **not** prove which revision the browser actually observed.

## Full live UI lifecycle authority

A claim that the System3 UI is healthy or complete requires fresh production-browser proof of every canonical dashboard tab, not only a local build and not only HTTP 200:

- decision-intel
- truth
- genesis
- e2e-proof
- overview
- sim-live
- options-intel
- chain
- signals
- trade
- paper
- positions
- risk-scenarios
- multibagger
- prediction-audit
- performance
- ml
- data-integrity
- broker
- alerts
- system
- gates

For each tab, capture:

- fresh screenshot;
- visible text snapshot;
- active/rendered state;
- capture UTC timestamp;
- any visible loading/unknown/waiting/degraded/empty state;
- semantic data evidence where the tab is data-bearing.

For required option-chain production proof, capture NIFTY, BANKNIFTY, FINNIFTY, and MIDCPNIFTY subviews separately and prove the visible symbol/source/contracts/strikes rather than assuming one default chain represents all required symbols.

The lifecycle proof must also capture broker, health, live-board, and `/api/deploy/info` at the start and end of the browser session so UI/API/revision contradictions cannot be hidden by timing.

## Evidence classes

| Class | Meaning | Can prove `live/current/now`? |
|---|---|---|
| `REQUEST_SCOPED_LIVE_BROWSER` | New production browser observation started after the current investigation/request began and, post-deploy, after exact-serving-SHA convergence | **YES** |
| `REQUEST_SCOPED_LIVE_API` | New read-only production API observation from the same investigation/request | **YES**, for API truth only |
| `LIVE_LOG_OBSERVATION` | New production log query scoped to the current investigation window | **YES**, for the logged fact only |
| `DEPLOYMENT_METADATA` | Serving revision/SHA/traffic queried during current investigation | **YES**, for deployment metadata only |
| `STORED_ARTIFACT` | Screenshot/report/workflow artifact from a prior observation | **NO** for a new current/live claim |
| `REPORTS_LATEST` | Any file under `reports/latest/` | **NO by path/name alone** |
| `SYSTEM_STATE_OR_CHANGE_LOG` | Repo state/history documents | **NO**; context/history only until live revalidated |
| `SOURCE_CODE` | Repository source/config | **NO** for runtime/UI state |

## Freshness rules

1. **Interactive current/live request:** a new observation must start after the request/investigation start time. Age alone is insufficient.
2. **Post-deploy current/live request:** capture must additionally begin after exact serving-SHA convergence.
3. **Scheduled/automated verdict:** evidence must declare `captured_at_utc` and a bounded `max_age_seconds`; default live-proof freshness ceiling is 300 seconds at verdict time.
4. If evidence exceeds its freshness ceiling, label it `STALE_HISTORICAL` and re-observe before a current-state verdict.
5. If capture time is absent, freshness is `UNKNOWN`; fail closed for current/live claims.
6. If clocks/timestamps or serving-SHA boundaries contradict, fail closed and refresh from authoritative live sources.

## Forbidden shortcuts

Agents/workflows MUST NOT:

- equate the directory name `latest` with current truth;
- use artifact creation time as proof that the underlying runtime is still in that state;
- reuse an earlier screenshot to answer a later `show me now` request;
- assume the GitHub run SHA equals the revision currently serving the browser;
- accept a same-push screenshot taken before Cloud Run serving-SHA convergence;
- call a localhost/Vite browser smoke production proof;
- call a successful CI/deploy job proof that live market data is populated;
- call HTTP 200 proof that a data-bearing UI is semantically healthy;
- infer current broker connectivity from a token expiry timestamp;
- infer current UI state from source code or backend JSON alone;
- hide `captured_at_utc`, evidence age, serving SHA, or source type when making current-state claims.

## Historical evidence use

Historical artifacts remain useful for:

- root-cause timelines;
- before/after comparison;
- regression analysis;
- reliability trends;
- proving what a prior deployment/run actually showed.

When used, explicitly label them **historical** and include their observation time. Historical evidence must never silently replace a current observation.

## Cross-agent rule

Every agent entry point (`AGENTS.md`, `GEMINI.md`, `.cursorrules`, `.github/CLAUDE_INSTRUCTIONS.md`, governance/master-goal docs) must point to this policy and treat it as a higher-priority temporal-truth override over older session notes, status files, reports, proof packs, or embedded historical claims.

When two agents disagree about current runtime/UI state, neither old artifact wins. Generate a new request-scoped live observation and use that as the arbiter.

After a deploy-triggering change, agents must additionally arbitrate against exact serving-SHA truth. A fresh screenshot from the wrong serving revision is not current proof.

## Safety

Live evidence collection is read-only:

- `ANALYZE_MODE=1`;
- LIVE trading remains OFF;
- automatic order execution remains OFF;
- no order/mutation endpoint is called;
- no broker secret payload is printed or stored;
- browser and API proof may exercise only public/read-only production surfaces.

## Machine enforcement

`scripts/system3_temporal_truth_guard.py` defines the machine-evaluable freshness contract. `tests/test_temporal_truth_contract.py` locks this policy into agent instructions and the live browser workflow.

`scripts/gcp_live_ui_snapshot.py` must wait for exact expected serving-SHA convergence through the same canonical `/api/deploy/info` route used by production UI, emit request/run-scoped timestamps and serving-SHA boundaries, capture the full production UI lifecycle, and fail closed if revision identity is not stable. Consumers must validate timestamps and serving identity before using stored evidence for time-sensitive claims.
