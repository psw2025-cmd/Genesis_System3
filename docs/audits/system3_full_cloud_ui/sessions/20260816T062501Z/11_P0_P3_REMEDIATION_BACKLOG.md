# P0–P3 Remediation Backlog (DESIGN ONLY)

| ID | Sev | Status | Symptom | Min fix | Structural |
|----|-----|--------|---------|---------|------------|
| F-001 | P0 | CONFIRMED_DEFECT | GitHub main SHA != serving /api/deploy/info SHA | Classify commits as runtime-affecting vs proof-only; deploy when runti | Exact-serving-SHA gate already in policy; enforce in deploy contract |
| F-002 | P0 | CONFIRMED_MISSING | Full broker-supported NSE/BSE/equity option universe not proven vs master | Do not claim full-universe PASS; implement coverage metrics | Central market-data adapter + versioned master diffs + proof matrix |
| F-003 | P1 | DEGRADED | Concurrent chain fetches: NIFTY OK 462 contracts; BANKNIFTY/FINNIFTY/MIDCPNIFTY  | Shared cache + single-flight; never stampede OC | Coalescing batcher + durable snapshot store |
| F-004 | P1 | CONFIRMED_MISWIRING | PCR tiles empty due to pcr_oi/pcr_vol vs API pcr | Map pcr or emit pcr_oi/pcr_vol | Shared chain DTO types |
| F-005 | P1 | CONFIRMED_MISWIRING | Tab shows gates not prediction ledger | Wire predict APIs or rename tab | Prediction ledger store |
| F-006 | P1 | CONFIRMED_MISSING | API /api/accuracy_trend exists; SPA never calls it | Add chart/table on ML or Truth | Canonical metrics store |
| F-007 | P1 | CONFIRMED_MISSING | Option-chain history not PRODUCTION_DURABLE on Cloud Run | GCS/Parquet daily OC snapshots | Data lake + lineage IDs |
| F-008 | P1 | CONFIRMED_MISSING | Production ranking primarily heuristic; institutional ML registry missing | Label UI REAL_MODEL vs HEURISTIC honestly | Registry+gates per blueprint |
| F-009 | P2 | MARKET_HOURS_PROOF_REQUIRED | WAITING visible on weekend closed session | Session-aware empty states | Truth state machine |
| F-010 | P2 | DEGRADED | GCP logs show HTTP 429 capacity aborts on /data-truth-score etc. | Rate-limit/coalesce genesis probes; scale or cache | SLO for optional modules |
| F-011 | P2 | DEGRADED | 257 ENABLED versions retained | Disable older versions after N | Version retention policy |
| F-012 | P2 | CONFIRMED_DEFECT | Full Cloud Audit + Frontend Browser Smoke + Security Audit Evidence FAILED on c7 | Triage failures separately from this audit PR | Workflow priority policy |
| F-013 | P3 | CORRECT_BEHAVIOR | Hypothesis: source=dhan not visible | Fix proof selector if harness misses strip | Keep provenance strip mandatory |
| F-014 | P0 | CORRECT_BEHAVIOR | Safety flags | None | Keep locks |
| F-015 | P1 | CORRECT_BEHAVIOR | Prior handoff said disconnected; current connected | Do not mint from laptop | Keep Cloud Job sole mint |

| F-016 | P1 | CONFIRMED_DEFECT | Rotate job fails: dhan-totp-secret v8 DESTROYED | Point latest to ENABLED TOTP version / recreate secret version | Secret lifecycle + rotate health alert |

