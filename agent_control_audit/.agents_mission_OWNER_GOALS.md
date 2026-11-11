# Genesis System3 — permanent owner mission
Version: 2026-11-02
Authority: root AGENTS.md, root GEMINI.md, docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md, and agent_policy.yaml. This document does not supersede those rules.

## Ultimate goal
Build and independently verify a cloud-first Indian market-intelligence platform with authentic authorized exchange/broker data, complete dynamically discovered NSE/BSE cash/indices/F&O coverage, actionable CE/PE intelligence, credible prediction evaluation, risk controls, reproducible paper trading, a truthful dashboard, and auditable operational evidence. NEVER promise profits.

## Mandatory scope
- Universe: all exchange-eligible instruments within authorized broker entitlements; current instrument masters, token/ISIN identity, sector/index membership, expiry, strike, lot sizes, filters for suspended/expired instruments, coverage denominator and exclusions.
- Feeds: authenticated source identities, market timestamps, sequence continuity, latency, freshness, live/closed/replay/delayed distinctions, loss and reconnect behavior, depth integrity, reconciliation with independent source.
- Options: complete CE/PE chain, live LTP/bid/ask/volume/OI/OI-change, IV/Greeks/PCR, top CE and PE movers, liquidity gating and per-contract provenance; no dummy market prices.
- Intelligence: breadth, movers, unusual volume, sector heatmaps, scanners, searchable symbol explorer, alerts and real-time chart controls.
- Predictions: timestamped pre-outcome forecasts, matured outcomes, walk-forward and leakage testing, sample sizes, calibrated metrics, benchmark comparison, model version, drift gates.
- PAPER trades: no real orders; deterministic paper order lifecycle, reproducible fill/slippage/cost rules, positions, closed trade receipts, exact realized/unrealized net P&L reconciliation and safe failure tests.
- Operations: resilient cloud-only runtime, API contracts, rate limits, observability, startup/recovery, CI, revision/SHA provenance, security, backup, blocked/unknown and owner signoff.
- Dashboard: every displayed statistic bound to a verified backend source or explicitly marked simulation, unavailable, stale or unverified; never hardcode green readiness.

## Acceptance criteria
Scope is 52 domains, 624 base controls, 1872 FUNCTION/FAILURE/INDEPENDENT tests. The root GENESIS_1872_MASTER_CHECKLIST.csv and evidence JSONs are historical *claims*. Independent acceptance is tracked separately in .agents/state/INDEPENDENT_VERIFICATION.csv.
A PASS requires executed and reproducible observation, dated nonempty raw artifacts, expected-versus-actual assertion, relevant source and SHA/digest, a genuine independent check/reviewer, and a recorded conclusion. A source code statement is not execution proof. Absent proof stays UNVERIFIED/BLOCKED. All critical P0 and owner gates must pass before a production-paper readiness verdict.
Cloud changes, secret rotation, IAM, billing, deployment or opening live-trading authority require separate explicit approval. Permanent live order restriction always applies unless a future explicit owner directive and reviewed safety process authorize otherwise.
