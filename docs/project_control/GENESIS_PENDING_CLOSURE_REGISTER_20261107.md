# Genesis System3 — Pending Closure Register (2026-11-07)

This register is **not** proof of production readiness. Statuses are evidence-scoped. Keep prior unresolved work visible across PRs; never turn an unverified item into PASS from a synthetic fixture.

| ID | Area | Current evidence | Status | Closure requirement |
|---|---|---|---|---|
| SYS3-001 | Deterministic PAPER market replay and fault matrix | PR #562 merged; six workflows PASS | CI PASS | Separate real broker/market evidence |
| SYS3-002 | Synthetic prediction/outcome calculation | PR #560 merged | CI PASS | Real prediction IDs joined to actual option ticks |
| SYS3-003 | Synthetic lifecycle UI | PR #561 merged | CI PASS | Deployed UI visual verification |
| SYS3-004 | Walk-forward chronological separation | PR #563 merged; six workflows PASS | CI PASS | Live model lineage and unseen out-of-sample validation |
| SYS3-005 | Multibagger static data falsely labeled verified | PR #564 superseded by #565 | OPEN — CI | #565 all checks PASS and merged |
| SYS3-006 | Dhan entire EQ inventory | Three hardcoded names in research service | NOT VERIFIED | Authenticated Dhan EQ master, symbol/security ID coverage and count reconciliation |
| SYS3-007 | Dhan option CE/PE equity universe | Historical 219-symbol target | NOT VERIFIED | Dhan security-ID mapping, all eligible contracts, freshness and exchange comparison |
| SYS3-008 | Actual 5m/15m/30m/EOD prediction accuracy | 2026-10-29 report: four rows, zero proof passes | BLOCKED | Prediction-before-move, strike/token, actual outcome windows |
| SYS3-009 | Trade-wise net expectancy | Historical one-day report fails; no certified recent costed sample | BLOCKED | Realistic bid/ask, fees, slippage, closed PAPER reconciliation |
| SYS3-010 | Model training, drift and champion promotion | Modules and model artifacts exist | NOT VERIFIED | Versioned dataset, model hash, leak-free walk-forward and promotion audit |
| SYS3-011 | News, filings, catalysts | Integration into model unproven | NOT VERIFIED | Source/published/ingested timestamps and causal features |
| SYS3-012 | 23-tab frontend runtime | CI frontend smoke PASS | PARTIAL | All 23 tabs visited with screenshots, console and network assertions |
| SYS3-013 | Production Cloud Run release | Deployment revision not independently matched to main SHA | NOT VERIFIED | Image digest, revision, traffic split, health, endpoint and rollback evidence |
| SYS3-014 | Recovery Progress tab and 113 micro checks | Owner workbook baseline, not synchronized to live deployed UI | NOT VERIFIED | Issue ID/status/evidence timestamp/revision linked to deployment |
| SYS3-015 | Cloud-only unattended operation | Scheduler jobs previously paused | NOT VERIFIED | Safe cloud schedule, durable writer lock, monitoring, alerts, no laptop |
| SYS3-016 | PAPER safety and risk caps | CI safety PASS | CI PASS | Verify deployed runtime has PAPER_MODE=1, live authority=0, capital ₹50k and daily loss ₹5k |
| SYS3-017 | Duplicate writers and data provenance | Prior audit requested | NOT VERIFIED | RUN_ID/GIT_SHA/WRITER_ID/image digest, single writer and reconciliation |
| SYS3-018 | Benchmark vs NSE/BSE top gainers | No verified same-window comparison | NOT VERIFIED | Official same-day benchmark and survivorship-safe rankings |
| SYS3-019 | Market closed snapshot semantics | Earlier market-closed guard and snapshot labeling | PARTIAL | Verify latest closed snapshot and stale labels in deployed UI |
| SYS3-020 | PAPER learning and retraining | Model scheduler exists | NOT VERIFIED | Label maturity, backtest reproducibility, challenger and rollback |
| SYS3-021 | 200+ equity option scope | Earlier scanner counts not a current completeness receipt | NOT VERIFIED | Contract universe reconciliation per market day |
| SYS3-022 | Security and secrets | Six workflow gates on #563 PASS | CI PASS | Deployed IAM, secret sourcing, audit log, no exposed credentials |
| SYS3-023 | Dhan holdings and broker parity | Historical snapshot, not current | NOT VERIFIED | Authenticated live broker account and holdings parity without order routing |

## Release policy

1. Synthetic replay is **testing**, never real prediction accuracy.
2. PR merge requires **all six workflows PASS**, mergeable head, no unsafe trading changes.
3. Cloud Run deployment is separate from GitHub CI. Prefer tagged 0%-traffic revision, smoke tests, image digest verification, controlled traffic promotion and rollback.
4. Keep real broker order authority disabled. Do not enable live trading, auto-execution or order placement.
5. Do not erase unresolved findings when creating a new PR. Update this register with independent evidence and dates.
