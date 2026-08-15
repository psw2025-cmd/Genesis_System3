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
2. Open the authoritative GCP production URL in a **new Chrome/WebDriver browser session**.
3. Capture the relevant live tab(s) after the request/investigation start time.
4. Capture visible page text and a timestamped screenshot.
5. Capture the relevant read-only production APIs during the same proof session.
6. Compare UI-visible state with backend/API state and identify contradictions.
7. Record capture start/end UTC, source URL, tab, GitHub run ID/attempt/SHA when applicable, and safety state.
8. Report the evidence time to the user/agent. Never hide evidence age.
9. If a fix is made, the previous capture becomes historical. Run a **new** production browser proof before claiming the fix is visible/live.

A pre-existing artifact MAY NOT satisfy a new request for `live/current/now`, even if it is the newest stored artifact.

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

The lifecycle proof must also capture broker and health APIs at the start and end of the browser session so UI/API contradictions cannot be hidden by timing.

## Evidence classes

| Class | Meaning | Can prove `live/current/now`? |
|---|---|---|
| `REQUEST_SCOPED_LIVE_BROWSER` | New production browser observation started after the current investigation/request began | **YES** |
| `REQUEST_SCOPED_LIVE_API` | New read-only production API observation from the same investigation/request | **YES**, for API truth only |
| `LIVE_LOG_OBSERVATION` | New production log query scoped to the current investigation window | **YES**, for the logged fact only |
| `DEPLOYMENT_METADATA` | Serving revision/SHA/traffic queried during current investigation | **YES**, for deployment metadata only |
| `STORED_ARTIFACT` | Screenshot/report/workflow artifact from a prior observation | **NO** for a new current/live claim |
| `REPORTS_LATEST` | Any file under `reports/latest/` | **NO by path/name alone** |
| `SYSTEM_STATE_OR_CHANGE_LOG` | Repo state/history documents | **NO**; context/history only until live revalidated |
| `SOURCE_CODE` | Repository source/config | **NO** for runtime/UI state |

## Freshness rules

1. **Interactive current/live request:** a new observation must start after the request/investigation start time. Age alone is insufficient.
2. **Scheduled/automated verdict:** evidence must declare `captured_at_utc` and a bounded `max_age_seconds`; default live-proof freshness ceiling is 300 seconds at verdict time.
3. If evidence exceeds its freshness ceiling, label it `STALE_HISTORICAL` and re-observe before a current-state verdict.
4. If capture time is absent, freshness is `UNKNOWN`; fail closed for current/live claims.
5. If clocks/timestamps contradict, fail closed and refresh from authoritative live sources.

## Forbidden shortcuts

Agents/workflows MUST NOT:

- equate the directory name `latest` with current truth;
- use artifact creation time as proof that the underlying runtime is still in that state;
- reuse an earlier screenshot to answer a later `show me now` request;
- call a localhost/Vite browser smoke production proof;
- call a successful CI/deploy job proof that live market data is populated;
- call HTTP 200 proof that a data-bearing UI is semantically healthy;
- infer current broker connectivity from a token expiry timestamp;
- infer current UI state from source code or backend JSON alone;
- hide `captured_at_utc`, evidence age, or source type when making current-state claims.

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

The production browser proof script must emit request/run-scoped timestamps and evidence classification. Consumers must validate those timestamps before using stored evidence for time-sensitive claims.
