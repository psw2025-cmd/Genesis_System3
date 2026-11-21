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
