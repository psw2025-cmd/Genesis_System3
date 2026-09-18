# Genesis System3 — Local UI Lighthouse Performance MRI

AGENT_NAME=ChatGPT  
AGENT_LANE=D  
AGENT_ROLE=Controller / evidence reconciliation  
CREATED_BY=ChatGPT  
LAST_EDITED_BY=ChatGPT  
CREATED_AT_UTC=2026-09-02T07:55:00Z  
TASK_OR_ISSUE=#442  

## Scope
Canonical laptop UI: `http://127.0.0.1:8000/ui`.
PAPER/ANALYZER only. LIVE trading and real broker order placement remain disabled.

## Fresh Lighthouse evidence — broker tab
User-captured Chrome Lighthouse run on `ui?tab=broker` reported Performance 7, Accessibility 87, Best Practices 100, SEO 91. The run itself warns that Chrome extensions materially affected performance, so score 7 MUST NOT be treated as a clean baseline.

Observed metrics: FCP ~5.2 s, LCP ~6.0 s, TBT ~3.44 s, CLS ~0.404, Speed Index ~7.5 s. Main-thread work ~9.4 s. First-party JS bundle ~931 KiB with substantial unused JS reported. Batch chains payload ~659 KiB and NIFTY chain payload ~134 KiB.

Critical-path/API observations include approximately: market/live_board 16.8 s, broker/status 14.7 s, batch/chains 14.6 s, chain/NIFTY 13.6 s, positions-holdings 13.2 s, batch/market-data 11.9 s, state 11.5 s, deploy/info 11.3 s. Reproduce cleanly before attributing all delay to System3 because extensions polluted this run.

## Mandatory performance verification
1. Re-run Lighthouse in Incognito or a clean Chrome profile with extensions disabled.
2. Capture three runs per critical tab and use median results.
3. Preserve exact runtime Git SHA and timestamp.
4. Separate frontend CPU/render delay from backend/API latency.
5. Trace slow APIs server-side and identify duplicate/repeated requests.
6. Correctness/truth defects have priority over cosmetic Lighthouse score.
7. Test whether batch/chains can avoid sending unnecessary chains/fields to tabs that do not need them.
8. Test route/code splitting and lazy loading for tab-specific UI.
9. Investigate render delay, forced reflow and CLS after extension effects are removed.
10. Separate accessibility defects caused by extensions from first-party defects before changing app code.

## Broker-tab truth defects visible in same evidence
Broker UI shows connected/read-only/live-off and 4/4 required chains, while token source, secret version, token-loaded proof, token time-left and expiry proof remain pending. Local-only provenance must be proven without exposing secret values. Residual Google Cloud token-authority wording is forbidden under full-GCP-exit policy and must be removed from local runtime semantics.

## Acceptance
Accept performance work only after clean-profile reproduction, exact SHA, API/server trace, focused checks, 22-tab semantic smoke and independent verification. No false green, no stale/global 4/4 claim when any required chain is degraded, broker-state labels non-contradictory, LIVE OFF, real broker orders zero.
