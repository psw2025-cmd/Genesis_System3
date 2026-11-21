# LEGACY Genesis first-attempt browser failure — evidence ledger

Lane: LEGACY ONLY. Do not use for LIVE NEW acceptance.
Updated: 2026-11-21 17:20 IST
Parent SHA: e5dcacfe866db707a930449eda60b8fb93a664a0
Source PR: https://github.com/psw2025-cmd/Genesis_System3/pull/663
Evidence: https://github.com/psw2025-cmd/Genesis_System3/actions/runs/44858068117

| Task ID | Lane | Goal | Dependency | Owner/workstream | Evidence | Last verified SHA/run | State | Attempts | Next executable action | Updated |
|---|---|---|---|---|---|---|---|---|---|---|
| LEG-BROWSER-001 | LEGACY | Prove first-attempt desktop/mobile render | browser instrumentation | failure-resolution | workflow job 136704814814 | e5dcacf / 44858068117 | FAIL | 2 historical attempts | Instrumentation committed 82b5b6d; run exact-head CI, inspect first-attempt BROWSER_STAGE markers, correct demonstrated bottleneck | 2026-11-21 15:54 IST |
| LEG-COUNCIL-002 | LEGACY | Verify independent OpenAI/Anthropic/Gemini verdict artifacts and hashes | trusted workflow outputs | council audit | PR #650 | NOT VERIFIED this cycle | NOT VERIFIED | 0 this cycle | Fetch provider artifacts, compare reviewed SHA and SHA256 | 2026-11-21 15:54 IST |
| LEG-UI-003 | LEGACY | Verify 23 tabs and deployed SHA | production access and exact SHA | UI/runtime | 44858068117 production steps skipped | e5dcacf | NOT VERIFIED | 0 this cycle | Request-scoped read-only live proof, compare serving SHA | 2026-11-21 15:54 IST |

## Observed failure signature

Attempt 1: 2026-11-21 02:51:32–02:54:32 UTC, `timeout 180s`, exit 124; no stage-level output to distinguish preview startup, Chrome session creation, desktop tab wait, mobile tab wait, screenshot, or cleanup. Attempt 2 passed at 02:55:27 UTC, including Genesis desktop and mobile. Three deterministic cold-cache tests passed before the browser step. An overall successful workflow is **not** first-attempt reliability proof.

## Safe architectural correction

Instrument `scripts/frontend_local_runtime_smoke.py` with flushed monotonic stage timing (preview ready, chromedriver status, session created, first navigation, each desktop/mobile tab and cleanup), emit bounded sanitized diagnostic JSON even on timeout via an outer supervisor, and preserve existing 180s attempt deadline and all assertions. Add a regression test proving that attempt 1 FAIL plus attempt 2 PASS is not classified as first-attempt PASS. Do not mask timeout, disable assertions, or equate synthetic tests with live market proof. No production deployment or trading action is authorized by this ledger.

## Cycle 2026-11-21 17:20 IST

Committed stage-level flushed diagnostic markers to `scripts/frontend_local_runtime_smoke.py` at `82b5b6df8699e3a8facbe9d40db0b178741f6baa` on isolated PR #664. GitHub file readback confirmed marker locations. No timeout, assertion or trading gate changed. Exact-head CI and actual first-attempt reliability remain NOT VERIFIED. PR #664 contains inherited frontend/test changes; review dependency overlap with PR #663 before merge. LIVE NEW folder query returned only the control workbook, while BUILD_LOG still records v0.9 as local-only; independent archive hash remains NOT VERIFIED.

## Next-cycle cursor

Read current PR head and this ledger first. Reconcile changes before applying instrumentation. Reproduce first attempt with exact SHA, inspect diagnostics, implement minimal root-cause fix on an isolated branch, rerun CI and verify review requirements. LIVE NEW must maintain a separate ledger in its independent workspace; no evidence transfer.

## Cycle 2026-11-21 18:05 IST — NEW FAIL evidence

Fresh PR #664 head is `b4fc21d1d471bac7000a13bb6e0f76022960969e`; main is `2dbac5cee02dda8f42b6118a2ac713d3e74f08e8`. Exact-head CI: https://github.com/psw2025-cmd/Genesis_System3/actions/runs/44901057503 **FAIL**. Job 136836852832 shows the browser step failed despite six other inspected workflows succeeding. Cold-cache acceptance tests PASS, but actual browser attempt 1 FAIL exit 124 and attempt 2 FAIL exit 1. Instrumentation is working: ChromeDriver ready at 0.53s and Chrome session created at 0.76s in attempt 2, eliminating slow Chrome startup as the primary explanation for that attempt. First attempt repeatedly spends approximately 10 seconds per tab in `lazy_content_still_loading` and times out during desktop traversal near `system-readiness` at elapsed 171.65s. Attempt 2 completes desktop/mobile traversal but `broker:lazy_content_still_loading` persists; final `FRONTEND_RUNTIME_SMOKE=FAIL` at 49.94s. Thus this is an actual frontend lazy-content/render defect, not merely a startup timeout. Do not increase timeouts or accept retry-masked green.

| Task ID | Lane | Goal | Dependency | Owner/workstream | Evidence | Last verified SHA/run | State | Attempts | Next executable action | Updated |
|---|---|---|---|---|---|---|---|---|---|---|
| LEG-BROWSER-001 | LEGACY | Resolve lazy-content desktop/mobile rendering without masking | exact-head browser logs and source | failure-resolution | run 44901057503 job 136836852832 | b4fc21d / 44901057503 | FAIL | 2 in latest run | Inspect `dashboard/frontend/src/App.tsx` lazy/Suspense and broker route; reproduce with isolated focused test; fix real lazy content, preserve assertions, rerun exact-SHA CI | 2026-11-21 18:05 IST |

### Next cursor

Prioritize `broker` Suspense fallback plus any shared lazy route loader: inspect frontend source at exact PR head, capture browser console/network errors and confirm whether lazy import rejects, backend-dependent render blocks, or UI active-tab state is stale. Make minimal isolated patch and rerun 23-tab smoke. Council provider artifact validation and LIVE NEW independent archive verification remain NOT VERIFIED. PR #664 must not merge until exact-head CI and reviews pass. No cross-lane data or cloud actions.
