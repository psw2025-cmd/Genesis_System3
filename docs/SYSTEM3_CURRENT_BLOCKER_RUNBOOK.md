# System3 Current Blocker Runbook

**Temporal authority marker:** `SYSTEM3_TEMPORAL_TRUTH_V1`

Canonical temporal policy: `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`.

This runbook is fail-closed. It does not enable broker orders, expose credentials, or permit a production-grade claim from stored evidence alone.

## Safety invariants

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- Never print, commit, or copy API keys, access tokens, TOTP/PIN, cookies, or broker secret payloads into proof artifacts.
- Never mark a blocker resolved from HTTP 200 alone.
- Never mark a UI/runtime blocker resolved from a pre-existing screenshot/report.

## Current evidence precedence

There is **no “newest stored report wins” rule** for current/live truth.

When current state matters, generate new request-scoped observations after the investigation starts:

1. Fresh GCP production browser observation for UI-visible truth.
2. Fresh same-session production API observation.
3. Fresh production logs/runtime/deployment metadata for diagnosis.
4. Current source/config for intended implementation.
5. Stored reports/artifacts only as historical comparison.

A file in `reports/latest/` has no automatic current-state authority. Its timestamp tells when it was observed, not what is true now.

If two stored reports disagree, do not choose the newer one as the live arbiter. Re-observe the authoritative production boundary.

## Production authority

- Project: `system3-openalgo-safe`
- Region: `asia-south1`
- Service: `genesis-system3-web`
- UI: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`
- Broker: Dhan
- Render is retired/non-authoritative.

## P0 — Request-scoped proof freshness

For every current/live investigation:

1. record the current request/investigation UTC start time;
2. start a new production browser session after that time;
3. capture the affected tab(s), or all 22 tabs for a full UI audit;
4. capture same-session broker/health/relevant APIs;
5. save per-tab capture timestamps;
6. compare UI-visible state with backend truth;
7. after any change/recovery/deployment, capture again.

Use:

```text
scripts/gcp_live_ui_snapshot.py
scripts/system3_temporal_truth_guard.py
```

A previous successful capture becomes historical immediately for a later `show me now` request.

## P1 — Broker read-only truth

Broker status must be freshly observed. Required safe proof:

- `connected=true` when claiming connected;
- `error=null` or the exact error reported;
- dynamic approved token source metadata only;
- token secret value not exposed;
- `live_trading_enabled=false`;
- `order_placement_allowed=false`.

A token expiry timestamp cannot substitute for an actual broker status request.

## P2 — Required market/option-chain truth

Required index symbols include:
- NIFTY
- BANKNIFTY
- FINNIFTY
- MIDCPNIFTY

For a claim that option-chain data is working now, verify fresh production data and visible UI semantics appropriate to market state:

- expected symbol/expiry;
- positive contract/strike rows when the source should provide them;
- source/provenance;
- freshness/timestamp;
- no hidden fallback presented as Dhan truth;
- UI value agrees with API/backend observation.

Market closed/after-hours must be classified separately from genuine missing/stale data.

## P3 — Full UI lifecycle

A full UI audit requires fresh production screenshots + visible text for all 22 canonical tabs listed in the temporal policy.

Render-only PASS is not semantic PASS. Investigate visible markers such as:

- `—`
- `UNKNOWN`
- `WAITING`
- `LOADING`
- `POLL`
- `NO DATA`
- `DISCONNECTED`
- `NO AUTH`
- `ERROR`
- `FAILED`
- `DEGRADED`

Their meaning depends on market/session context; do not silently treat them as healthy.

## P4 — Scanner / Signals / CE-PE evidence

Do not fabricate candidates. A current scanner/signals PASS requires fresh data-backed candidates or a truthful no-candidate state with reason/provenance. If the product requirement is active candidate discovery and none exists, keep readiness blocked.

## P5 — Paper lifecycle

HTTP 200 or an empty table is transport/render proof only. Full paper lifecycle proof requires durable signal -> entry -> management -> exit -> PnL evidence, timestamps/provenance, and no broker order mutation.

## P6 — ML/prediction evidence

UI visibility is not model proof. Require matured prediction-vs-actual evidence, sample size/horizon, metrics, and artifact provenance. Historical metrics must be labeled with their evaluation window.

## P7 — IAM/automation authority

Current IAM authority must be queried when making a current IAM claim. Stored inventories are historical after capture. Do not call strict scheduler-only authority PASS while temporary/excess project-level job-run authority remains.

## Required fix loop

For any blocker:

1. **Observe current truth** from the authoritative live boundary.
2. **Classify** evidence as live vs historical.
3. **Investigate root cause** from logs/code/config.
4. **Implement** the smallest safe fix.
5. **Run exact-head tests/CI**.
6. **Deploy/recover** only through bounded authority.
7. **Re-observe fresh production truth** after the change.
8. **Compare before/after**.
9. Close only if the requested end state is now directly proven.

## Closure contract

A blocker may be called resolved only when:

- the proof was generated after the current request/change;
- the authoritative production boundary is the source;
- capture/observation UTC time is recorded;
- UI and backend/API truth are consistent where applicable;
- no required semantic blocker remains;
- safety flags remain PAPER/ANALYZER and LIVE/order execution OFF.

If proof is stale, absent, or contradictory, status is `NOT_PROVEN`, `BLOCKED`, or `FAIL`—never inferred PASS.
