# LEGACY Genesis orchestrator evidence ledger — 2026-11-23 cycle

Lane: LEGACY ONLY. Main SHA: `2dbac5cee02dda8f42b6118a2ac713d3e74f08e8`. No LIVE NEW files, credentials or proof included.

| Task ID | Goal / dependency | Owner | Evidence | State | Attempts | Next executable action |
|---|---|---|---|---|---:|---|
| LEG-UI-001 | Cold-cache 23 desktop + 23 mobile render, exact-head CI | Failure-resolution workstream | [45129210710](https://github.com/psw2025-cmd/Genesis_System3/actions/runs/45129210710), [45129210866](https://github.com/psw2025-cmd/Genesis_System3/actions/runs/45129210866), head `f59acdb0471e2a6207c4686cee0d77468299099f` | FAIL | 2 inspected jobs | Inspect pending competing fixes PR #661/#665, reproduce once without retry, verify no lazy fallback and resource fanout before merge |
| LEG-COUNCIL-002 | Independently verify real three-provider council verdicts / diff SHA256 / artifacts | Council audit | PR #650 merged 2026-11-17, merge SHA `0d1f67e3314a6e107a4b5d4ec1397b3789c1e22d`; provider response evidence not yet read back | NOT VERIFIED | 1 | Fetch trusted main-only council run artifacts and inspect three provider responses, SHA and failure conditions |
| LEG-PAPER-003 | Real feed -> paper order/fill/exit -> reconciled net P&L and UI screenshot | Paper lifecycle | No fresh broker / runtime ledger / UI screenshot readback in this cycle | NOT VERIFIED | 1 | Query read-only deployed health, broker feed timestamps, paper order/trade/position/P&L endpoints; do not claim profit |

## Failure-resolution evidence

Latest exact-head CI: Global Safety run 45129210866 failed frontend browser job 137540615888; frontend smoke run 45129210710 failed job 137540562056. Logs show `lazy_content_still_loading` on multiple routes and repeated `/api/market/live_board` HTTP timeouts of ~12s, `/api/state` ~20s, `/api/batch/market-data` ~25s. Compiled lazy JS assets can return HTTP 200 after >10s. This supports route/resource contention as a hypothesis, NOT a proven sole root cause. No timeout/threshold/assertion was weakened. Browser evidence is NOT live market/P&L proof.

## Resume cursor

1. Review PR #661 and #665 against this exact signature and inspect their exact-head CI; avoid duplicate fixes.
2. Reproduce with one cold-cache browser run, 23 desktop + 23 mobile; inspect API request fanout and preview-server resource timings.
3. Only after exact-head green and review, merge via normal protections and verify main. Keep PAPER-only safeguards.

Last updated: 2026-11-23 (cycle; exact wall-clock update not verified).
