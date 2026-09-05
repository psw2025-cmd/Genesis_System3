# Master Finding Table

## F-001 (P0) — CONFIRMED_DEFECT

- **tab:** deploy
- **component:** Cloud Run genesis-system3-web
- **symptom:** GitHub main SHA != serving /api/deploy/info SHA
- **utc:** 2026-08-16T06:25:01Z
- **ist:** 2026-08-16 11:55:01 IST
- **expected:** Serving SHA equals intended runtime-affecting main after deploy
- **actual:** main=c763ecf048478842688373cf674eb56a7dc04aa9 serving=a48e7b3c7c086a21352f718355d1c12d4a48955b revision=genesis-system3-web-00384-tuw
- **evidence:** REQUEST_SCOPED_LIVE_API+LIVE_GCP_RESOURCE
- **fe:** 
- **be:** /api/deploy/info
- **upstream:** Artifact Registry
- **gcp:** genesis-system3-web
- **root:** Deploy lag or proof-only commits on main without web rebuild
- **blast:** All UI proofs risk photographing older revision
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** Classify commits as runtime-affecting vs proof-only; deploy when runtime; document expected serving SHA
- **struct:** Exact-serving-SHA gate already in policy; enforce in deploy contract

## F-002 (P0) — CONFIRMED_MISSING

- **tab:** issue-188
- **component:** universe coverage
- **symptom:** Full broker-supported NSE/BSE/equity option universe not proven vs master
- **utc:** 2026-08-16T06:25:01Z
- **ist:** 2026-08-16 11:55:01 IST
- **expected:** Parity matrix green per Issue #188
- **actual:** Index stream hardcoded to 4-5 symbols; equity FO discovery exists but paced stream/Market Top do not cover full master
- **evidence:** CURRENT_GITHUB_MAIN+REQUEST_SCOPED_LIVE_API
- **fe:** OptionChain.tsx
- **be:** /api/underlyings,/api/chain/{u}
- **upstream:** security_id_list.csv/Dhan
- **gcp:** genesis-system3-web
- **root:** Architecture scopes live paced OC to index subset
- **blast:** Issue #188 remains OPEN
- **conf:** CONFIRMED
- **mh:** MARKET_HOURS_VALIDATION_REQUIRED
- **min_fix:** Do not claim full-universe PASS; implement coverage metrics
- **struct:** Central market-data adapter + versioned master diffs + proof matrix

## F-003 (P1) — DEGRADED

- **tab:** chain
- **component:** paced OC / DSM
- **symptom:** Concurrent chain fetches: NIFTY OK 462 contracts; BANKNIFTY/FINNIFTY/MIDCPNIFTY intermittently NO_DHAN_DATA CHAIN_FETCH_TIMEOUT
- **utc:** 2026-08-16T06:31:13Z
- **ist:** 2026-08-16 12:01:13 IST
- **expected:** Stable verified Dhan rows or explicit stale snapshot for all streamed indices
- **actual:** First parallel probe returned large bodies for all 4; second summarize saw timeouts on 3 symbols
- **evidence:** REQUEST_SCOPED_LIVE_API
- **fe:** OptionChain.tsx
- **be:** /api/chain/{underlying}
- **upstream:** DataSourceManager paced OC
- **gcp:** genesis-system3-web
- **root:** Serialized 3.4s OC + timeout under concurrency/weekend closed path
- **blast:** UI/E2E four-chain proofs flaky
- **conf:** CONFIRMED
- **mh:** YES
- **min_fix:** Shared cache + single-flight; never stampede OC
- **struct:** Coalescing batcher + durable snapshot store

## F-004 (P1) — CONFIRMED_MISWIRING

- **tab:** options-intel
- **component:** OptionsIntelligence.tsx
- **symptom:** PCR tiles empty due to pcr_oi/pcr_vol vs API pcr
- **utc:** 2026-08-16T06:35:47Z
- **ist:** 2026-08-16 12:05:47 IST
- **expected:** PCR displays when chain healthy
- **actual:** Schema mismatch (lane B)
- **evidence:** CURRENT_GITHUB_MAIN
- **fe:** OptionsIntelligence.tsx
- **be:** chain_adapter.py
- **upstream:** dhan
- **gcp:** 
- **root:** Field-name mismatch
- **blast:** Options Intel misleading empty
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** Map pcr or emit pcr_oi/pcr_vol
- **struct:** Shared chain DTO types

## F-005 (P1) — CONFIRMED_MISWIRING

- **tab:** prediction-audit
- **component:** PredictionAudit.tsx
- **symptom:** Tab shows gates not prediction ledger
- **utc:** 2026-08-16T06:35:47Z
- **ist:** 2026-08-16 12:05:47 IST
- **expected:** Prediction vs actual audit
- **actual:** Uses /api/auto_gates; /api/predict* unused
- **evidence:** CURRENT_GITHUB_MAIN+REQUEST_SCOPED_LIVE_BROWSER
- **fe:** PredictionAudit.tsx
- **be:** /api/auto_gates
- **upstream:** 
- **gcp:** 
- **root:** Wrong API binding
- **blast:** Users misread gates as model audit
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** Wire predict APIs or rename tab
- **struct:** Prediction ledger store

## F-006 (P1) — CONFIRMED_MISSING

- **tab:** ml
- **component:** accuracy_trend
- **symptom:** API /api/accuracy_trend exists; SPA never calls it
- **utc:** 2026-08-16T06:35:47Z
- **ist:** 2026-08-16 12:05:47 IST
- **expected:** Spearman trend visible
- **actual:** API without UI
- **evidence:** CURRENT_GITHUB_MAIN+REQUEST_SCOPED_LIVE_API
- **fe:** 
- **be:** /api/accuracy_trend
- **upstream:** state validations
- **gcp:** 
- **root:** Missing FE consumer
- **blast:** ρ story incomplete
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** Add chart/table on ML or Truth
- **struct:** Canonical metrics store

## F-007 (P1) — CONFIRMED_MISSING

- **tab:** data
- **component:** OC storage
- **symptom:** Option-chain history not PRODUCTION_DURABLE on Cloud Run
- **utc:** 2026-08-16T06:35:47Z
- **ist:** 2026-08-16 12:05:47 IST
- **expected:** Immutable partitioned OC history for training/backtest
- **actual:** EPHEMERAL in-memory + SESSION_DURABLE local JSON
- **evidence:** CURRENT_GITHUB_MAIN
- **fe:** 
- **be:** app.py _PUSHED_CHAIN_CACHE
- **upstream:** Dhan
- **gcp:** Cloud Run ephemeral FS
- **root:** No OC lake
- **blast:** Backtest/training history insufficient
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** GCS/Parquet daily OC snapshots
- **struct:** Data lake + lineage IDs

## F-008 (P1) — CONFIRMED_MISSING

- **tab:** ml
- **component:** GainRank/Ensemble
- **symptom:** Production ranking primarily heuristic; institutional ML registry missing
- **utc:** 2026-08-16T06:35:47Z
- **ist:** 2026-08-16 12:05:47 IST
- **expected:** Versioned model registry with promotion gates
- **actual:** Heuristic + optional CSV ml_confidence; no MLflow; walk-forward promotion MISSING
- **evidence:** CURRENT_GITHUB_MAIN
- **fe:** MLPerformance.tsx
- **be:** /api/ml/performance
- **upstream:** pickles/CSV
- **gcp:** 
- **root:** Blueprint not implemented
- **blast:** Cannot claim institutional autonomous ML
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** Label UI REAL_MODEL vs HEURISTIC honestly
- **struct:** Registry+gates per blueprint

## F-009 (P2) — MARKET_HOURS_PROOF_REQUIRED

- **tab:** truth/genesis/e2e/overview/multibagger
- **component:** multiple
- **symptom:** WAITING visible on weekend closed session
- **utc:** 2026-08-16T06:35:47Z
- **ist:** 2026-08-16 12:05:47 IST
- **expected:** Explicit EXPECTED_AFTER_HOURS empty states
- **actual:** WAITING markers on several tabs while broker connected
- **evidence:** REQUEST_SCOPED_LIVE_BROWSER
- **fe:** SystemTruthControl/Genesis/EndToEndProof/Overview/Multibagger
- **be:** /api/state
- **upstream:** 
- **gcp:** 
- **root:** Proof gates wait for model/E2E/four-chain/market evidence
- **blast:** Looks broken after hours
- **conf:** LIKELY
- **mh:** YES
- **min_fix:** Session-aware empty states
- **struct:** Truth state machine

## F-010 (P2) — DEGRADED

- **tab:** genesis
- **component:** legacy routes
- **symptom:** GCP logs show HTTP 429 capacity aborts on /data-truth-score etc.
- **utc:** 2026-08-16T05:48:16Z
- **ist:** 2026-08-16 11:18:16 IST
- **expected:** Stable optional module responses
- **actual:** 429 no available instance (capacity), not Dhan 429
- **evidence:** LIVE_GCP_LOG
- **fe:** GenesisTab.tsx
- **be:** /data-truth-score
- **upstream:** 
- **gcp:** Cloud Run
- **root:** Burst load / scaling
- **blast:** Genesis soft-fail noise
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** Rate-limit/coalesce genesis probes; scale or cache
- **struct:** SLO for optional modules

## F-011 (P2) — DEGRADED

- **tab:** broker
- **component:** Secret Manager dhan-access-token
- **symptom:** 257 ENABLED versions retained
- **utc:** 2026-08-16T06:35:47Z
- **ist:** 2026-08-16 12:05:47 IST
- **expected:** Bounded enabled versions / disable old
- **actual:** enabled_count=257 latest=257
- **evidence:** LIVE_GCP_RESOURCE
- **fe:** 
- **be:** cloud_token_provider
- **upstream:** Secret Manager
- **gcp:** dhan-access-token
- **root:** No version GC
- **blast:** Ops confusion/cost
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** Disable older versions after N
- **struct:** Version retention policy

## F-012 (P2) — CONFIRMED_DEFECT

- **tab:** ci
- **component:** GitHub Actions on main
- **symptom:** Full Cloud Audit + Frontend Browser Smoke + Security Audit Evidence FAILED on c763ecf
- **utc:** 2026-08-16T05:29:21Z
- **ist:** 2026-08-16 10:59:21 IST
- **expected:** Required workflows green on main
- **actual:** failure run ids 31929124559 / 31929124562 / 31929124573
- **evidence:** CURRENT_GITHUB_MAIN
- **fe:** 
- **be:** 
- **upstream:** CI
- **gcp:** 
- **root:** Baseline debt and/or audit harness
- **blast:** Main not fully CI-green
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** Triage failures separately from this audit PR
- **struct:** Workflow priority policy

## F-013 (P3) — CORRECT_BEHAVIOR

- **tab:** chain-provenance
- **component:** OptionChain status strip
- **symptom:** Hypothesis: source=dhan not visible
- **utc:** 2026-08-16T06:32:00Z
- **ist:** 2026-08-16 12:02:00 IST
- **expected:** Visible source provenance
- **actual:** LIVE UI shows source=dhan priority=... universe=security_id_list.csv on chain tab
- **evidence:** REQUEST_SCOPED_LIVE_BROWSER
- **fe:** OptionChain.tsx
- **be:** /api/chain/NIFTY
- **upstream:** dhan
- **gcp:** 
- **root:** Prior proof-harness may miss strip
- **blast:** False missing-provenance claims
- **conf:** DISPROVEN_AS_UI_ABSENCE
- **mh:** NO
- **min_fix:** Fix proof selector if harness misses strip
- **struct:** Keep provenance strip mandatory

## F-014 (P0) — CORRECT_BEHAVIOR

- **tab:** safety
- **component:** live gates
- **symptom:** Safety flags
- **utc:** 2026-08-16T06:25:01Z
- **ist:** 2026-08-16 11:55:01 IST
- **expected:** LIVE off / no orders
- **actual:** live_trading_enabled=false order_placement_allowed=false UI Paper+Live off
- **evidence:** REQUEST_SCOPED_LIVE_API+REQUEST_SCOPED_LIVE_BROWSER
- **fe:** TopBar
- **be:** /api/broker/status
- **upstream:** 
- **gcp:** 
- **root:** Correct
- **blast:** n/a
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** None
- **struct:** Keep locks

## F-015 (P1) — CORRECT_BEHAVIOR

- **tab:** broker
- **component:** broker status
- **symptom:** Prior handoff said disconnected; current connected
- **utc:** 2026-08-16T06:25:01Z
- **ist:** 2026-08-16 11:55:01 IST
- **expected:** Fresh observation
- **actual:** connected=true secret_version=257 source=GCP_SECRET_MANAGER_DYNAMIC hours_remaining~22
- **evidence:** REQUEST_SCOPED_LIVE_API
- **fe:** BrokerProofPanel
- **be:** /api/broker/status
- **upstream:** Secret Manager
- **gcp:** dhan-access-token
- **root:** Rotation succeeded after prior ROTATION_FAILED era
- **blast:** Handoff historical only
- **conf:** CONFIRMED
- **mh:** NO
- **min_fix:** Do not mint from laptop
- **struct:** Keep Cloud Job sole mint

