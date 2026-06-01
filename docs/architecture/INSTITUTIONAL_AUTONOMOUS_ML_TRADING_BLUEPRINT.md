# System3 Institutional Autonomous ML Architecture Blueprint

## Decision

System3 must move from scattered proof scripts into a controlled autonomous ML platform. Deployment is a support layer. The core system must have data lineage, repeatable research, gated model promotion, market regime awareness, resilient event processing, and analyzer/paper safety.

## Target operating loop

```text
market close -> ingest -> validate -> feature build -> replay -> score drift -> train candidate -> optimize -> promote only if gates pass -> next session analyzer runtime -> report
```

## Pillar 1: Workflow automation

### Nightly ingestion

Required design:

1. Start after market close.
2. Collect daily OHLCV, tick snapshots, option chain snapshots, lifecycle records, and risk events.
3. Store raw data as immutable Parquet partitions.
4. Validate schema, gaps, stale symbols, bad timestamps, and missing option-chain fields.
5. Build feature tables only from validated data.

Recommended stack:

- Prefect for orchestration.
- Parquet for raw and curated data.
- DuckDB for local analytics.
- Pandera or Great Expectations for data checks.
- GCS later for durable object storage.

### Automated replay and backtest

Every night, replay the latest market day against the active model bundle and store:

- model version
- data version
- feature version
- config version
- signal quality
- fill realism
- slippage estimate
- drawdown
- rejected signals
- missed opportunity classification

### Model lifecycle

A candidate model cannot replace the active model unless it passes:

1. data-quality gate
2. backtest gate
3. walk-forward validation gate
4. paper/analyzer simulation gate
5. risk gate
6. calibration gate
7. governance manifest gate

Recommended stack:

- MLflow model registry
- Prefect model workflow
- GitHub Actions code gates
- signed model manifest with sha256 and metric summary

## Pillar 2: Self-learning and optimization

### Objective design

The objective must optimize robust after-cost behavior, not raw historical profit.

Candidate scoring should include:

- net result after cost
- drawdown penalty
- slippage penalty
- late-exit penalty
- overtrade penalty
- illiquidity penalty
- confidence calibration
- stability across regimes

### Hyperparameter optimization

Use:

- Optuna for local Bayesian tuning.
- Ray Tune for distributed weekend tuning.

Parameter groups:

- strike selection
- IV thresholds
- OI thresholds
- volatility windows
- momentum windows
- entry confidence
- exit rules
- position sizing rules
- time-of-day filters
- liquidity/spread filters

### Overfitting control

Mandatory controls:

- walk-forward validation
- purged time-series splits
- embargo windows around expiry/event sessions
- separate checks by regime
- minimum sample count per strategy bucket
- reject fragile parameter sets
- reject improvements limited to one day or one expiry

## Pillar 3: Market regime detection

Regime engine output:

- trend_up
- trend_down
- mean_reverting
- high_volatility
- low_volatility
- low_liquidity
- event_shock
- expiry_decay_dominant

Inputs:

- multi-timeframe trend slope
- realized volatility
- ATR expansion
- IV percentile
- OI buildup/unwind
- spread/depth proxy
- breadth and sector participation
- time-of-day phase

Classifier path:

1. rules plus gradient boosting baseline
2. online change-point detection
3. HMM for regime persistence
4. temporal neural model only after clean labels exist

## Pillar 4: Execution and infrastructure

Target event flow:

```text
market stream -> async queue -> feature update -> prediction -> risk gate -> action intent -> lifecycle monitor -> async persistence
```

Requirements:

- Async event loop.
- Separate data, prediction, reporting, and dashboard processes.
- Database writes via queue only.
- Backpressure detection.
- Heartbeats for stream, model server, writer, and dashboard.

Database direction:

- Local proof: SQLite and DuckDB with WAL and async writer queue.
- Production lifecycle store: Postgres or TimescaleDB.
- Research store: Parquet plus DuckDB.

Infrastructure direction:

- Dashboard/API: GCP Cloud Run.
- Research/training: GCP VM or batch worker with Ray.
- Execution core: dedicated VM after paper proof.
- Storage: GCS data lake plus relational lifecycle store.

## Safety policy

Until multi-week analyzer proof exists:

- live mode remains disabled
- model promotion cannot enable live mode
- deploy workflows cannot alter runtime trading mode
- every promotion needs a manifest and rollback target

## Immediate conclusion

The first structural upgrade is the autonomous ML control plane: authoritative data, model registry, candidate promotion rules, drift reports, and proof gates.
