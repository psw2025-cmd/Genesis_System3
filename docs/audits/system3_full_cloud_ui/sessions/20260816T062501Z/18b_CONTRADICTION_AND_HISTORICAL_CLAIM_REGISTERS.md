# Contradiction + Historical Claim Registers (QC)

## Contradiction register

| ID | Contradiction | Side A | Side B | Authoritative | Root | Status |
|----|---------------|--------|--------|---------------|------|--------|
| C1 | GitHub main vs serving | main `c763ecf048478842688373cf674eb56a7dc04aa9` (now `41f7a80cf0c31711f4c26d46fdc0e3f26fc6a311`) | serving `a48e7b3c7c086a21352f718355d1c12d4a48955b` | **Serving for runtime UI** | deploy lag / proof commits | OPEN F-001 |
| C2 | Broker handoff disconnected vs live connected | 2026-08-15 handoff | 2026-08-16 API/UI | **Live API** | temporal | RESOLVED historical |
| C3 | 4-chain large bodies vs later NO_DHAN_DATA | first probe | summarize | **Both true** | concurrency/timeout | OPEN F-003 |
| C4 | Truth header Broker Waiting vs Connected chip | Truth tab button | Decision/Broker | **API broker.status** | UI labeling | OPEN P2 |
| C5 | GCP HTTP 429 vs Dhan 429 narrative | capacity abort logs | hypothesis Dhan 429 | **Log text** | not same | OPEN clarify |
| C6 | Prediction Audit vs name | gates API | predict APIs | **Code wiring** | miswire | OPEN F-005 |
| C7 | PCR tiles empty vs chain healthy | Options Intel fields | chain `pcr` | **Schema** | mismatch | OPEN F-004 |
| C8 | Rotate failed vs broker connected | job 25szr DESTROYED totp | status connected v257 | **Both** | token still valid; mint broken | OPEN F-016 |

## Historical claim validation

| Claim | Classification |
|-------|----------------|
| production ready | HISTORICAL_ONLY / DISPROVEN_CURRENT as absolute |
| IAM closed | NOT_RECHECKED fully; do not PASS |
| 22/22 healthy | PARTIAL_CURRENT (loaded; WAITING weekend) |
| all chains ready | DISPROVEN_CURRENT as absolute (flaky non-NIFTY) |
| connected | REVALIDATED_CURRENT (true) |
| source= missing | DISPROVEN_CURRENT |
| Issue #188 complete | DISPROVEN_CURRENT / NOT complete |
| Full Cloud Audit PASS | DISPROVEN_CURRENT (failed on main push) |

## Market-hours validation register (summary)

| Requirement | Why MH | Duration | Success | Automation |
|-------------|--------|----------|---------|------------|
| Live LTP/OI/IV/Greeks 4 indices | ticks static weekend | 30–60m | contracts>0 + freshness SLO | YES |
| Concurrent chain no timeout | load | 15m | no NO_DHAN_DATA stampede | YES |
| Equity OC sample ≥10 | #188 | 30m | rows+source | YES |
| India VIX freshness | board | 15m | age bound | YES |
| Dhan 429 under load | rate | 60m | RCA evidence | YES |
| Paper lifecycle | session | market day | entry→exit | YES |
| Issue #188 60m window | lock criteria | 60m | zero unexplained gaps | YES |
| WS reconnect | streams | 30m | resubscribe | YES |

See also `13_MARKET_HOURS_REPRO_PLAN.md`.
