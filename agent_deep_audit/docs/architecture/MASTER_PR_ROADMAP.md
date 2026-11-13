# System3 Master PR Roadmap

## Phase 0: Control plane and truth foundation

### PR19 - Institutional autonomous ML architecture blueprint

Status: current PR.

Deliverables:

- autonomous ML architecture blueprint
- brutal gap analysis
- master PR roadmap
- machine-readable gap matrix

### PR20 - Authoritative runtime and data map

Goal: identify the active runtime files and all duplicate same-purpose files.

Deliverables:

- runtime authority map
- duplicate module classification
- protected file list
- quarantine policy

No deletion allowed.

## Phase 1: Data lineage and ingestion

### PR21 - Data contracts and schema gates

Deliverables:

- raw market data schema
- options chain schema
- lifecycle schema
- validation rules
- data quality report format

### PR22 - Nightly ingestion orchestrator

Deliverables:

- Prefect flow skeleton
- post-market ingestion job
- immutable raw partition path rules
- retry and failure reporting

### PR23 - Feature store boundary

Deliverables:

- offline feature definitions
- online feature definitions
- feature version manifest
- feature parity tests

## Phase 2: Backtest and drift engine

### PR24 - Daily replay and backtest engine

Deliverables:

- replay runner
- fees and slippage model
- lifecycle PnL join
- missed opportunity classification

### PR25 - Drift and degradation report

Deliverables:

- daily drift metrics
- calibration metrics
- strategy degradation alerts
- report artifact

## Phase 3: Model registry and promotion

### PR26 - MLflow model registry integration

Deliverables:

- model manifest
- registry pointer
- active versus candidate model state
- rollback target

### PR27 - Model promotion gate

Deliverables:

- promotion rules
- walk-forward validation gate
- paper/analyzer gate
- no-live-mode guarantee

## Phase 4: Self-learning and optimization

### PR28 - Optuna local optimization engine

Deliverables:

- tunable parameter registry
- objective function
- anti-overfit checks
- weekend run mode

### PR29 - Ray Tune distributed optimization plan

Deliverables:

- Ray Tune adapter
- distributed worker config
- budget limits
- artifact storage

## Phase 5: Market regime intelligence

### PR30 - Regime classifier baseline

Deliverables:

- labels
- features
- rules plus gradient boosting baseline
- regime report

### PR31 - Strategy router

Deliverables:

- regime to strategy mapping
- risk overlay
- analyzer-only routing proof

## Phase 6: Execution safety and low latency

### PR32 - Async event bus and non-blocking persistence

Deliverables:

- async queue design
- DB writer isolation
- backpressure metrics
- heartbeat proof

### PR33 - WebSocket tick stream authority proof

Deliverables:

- broker stream adapter map
- tick freshness proof
- disconnect recovery plan

## Phase 7: Dashboard truth and operations

### PR34 - Live truth dashboard data contract

Deliverables:

- dashboard API contract
- live versus static labels
- provenance fields
- latency metrics

### PR35 - Operational command center

Deliverables:

- health panels
- model state
- data freshness
- risk gates
- paper trade lifecycle truth

## Phase 8: Deployment hardening

### PR36 - Production FastAPI backend container proof

Deliverables:

- uvicorn runtime Dockerfile
- health endpoint proof
- analyzer mode environment lock

### PR37 - GCP Cloud Run dry-run proof

Deliverables:

- Artifact Registry proof
- Cloud Run dry-run proof
- identity proof

## Phase 9: Long paper validation

### PR38 - Multi-week analyzer validation pack

Deliverables:

- daily paper report
- model stability tracking
- drawdown report
- false positive report
- promotion readiness gate

## Strategic rule

No real-money live trading PR can be opened until Phase 9 produces multi-week analyzer evidence with no unresolved safety failures.
