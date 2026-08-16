[8/16/2026 4:53 PM] pritam warghade: ROLE: You are END-TO-END EXECUTOR + READ-WRITE AGENT for GCP and GitHub.
MISSION: Permanently fix "BROKER DISCONNECTED" for URL: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=decision-intel
RULE: No pending task. Do everything and verify at end. Commit everything to GitHub.

CONTEXT FROM AUDIT:
FAIL Reason: 2 access-token secrets fighting. dhan-access-token v258 is INVALID DH-906. 
Correct service: genesis-system3-web in asia-south1. Wrong region: europe-west.
Canonical secret must be: dhan-access-token

TASK LIST - EXECUTE IN ORDER:

TASK 1: SECRET MANAGER CLEANUP
1. Disable secret: system3-dhan-access-token
2. Disable secret: DHAN_BROKER_TOKEN  
3. Keep only dhan-access-token enabled. This is the single source of truth.
4. Add label to disabled secrets: "quarantined-by-agent-20260816"

TASK 2: GITHUB DOCUMENTATION UPDATE
File: /docs/BROKER_SETUP.md
Content to write:
# Broker Secret Policy
- Canonical Secret: dhan-access-token
- Banned Secrets: system3-dhan-access-token, DHAN_BROKER_TOKEN
- Service: genesis-system3-web @ asia-south1
- Auto-Heal: On DH-906, trigger rotate-job
Commit with message: "docs: define single canonical broker secret"

TASK 3: AUTO-HEAL ROTATE JOB
File: /infra/rotate-job.yaml
Create Cloud Run Job that:
1. Triggers only on PubSub topic: broker-token-rotate
2. Has mutex: 1 running at a time + 15min cooldown
3. Calls Dhan API to mint new token
4. Updates Secret Manager version of dhan-access-token
Commit with message: "feat: add mutex rotate job for broker token"

TASK 4: WEB APP HOT-RELOAD CODE
File: /src/broker/client.js or main broker client file
Add logic:
IF API response code = DH-906 THEN
    1. Publish to PubSub: broker-token-rotate
    2. Wait 10s
    3. Reload Secret Manager version for dhan-access-token
    4. Retry API call
Commit with message: "feat: auto-heal broker on DH-906 with hot-reload"

TASK 5: VERIFY CLOUD RUN ENV
Service: genesis-system3-web in asia-south1
Set env: DHAN_ACCESS_TOKEN_SECRET_ID=dhan-access-token
Deploy new revision

TASK 6: FINAL LIVE VERIFICATION
1. Wait 30s for deploy
2. Curl URL: https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/?tab=decision-intel
3. Check API /api/broker/status. Must return connected=true
4. Check UI TopBar. Must NOT show "Auth issue" or "TOKEN_EXPIRED"
5. If still FAIL, print logs and stop

TASK 7: FINAL AUDIT REPORT
Update file: reports/latest/broker_secret_dup_audit_20260816/FINAL_REPORT.md
Write PASS/FAIL, what was fixed, and URL screenshot status

OUTPUT FORMAT:
EXECUTION COMPLETE
1. Secrets Disabled: List
2. GitHub Commits: List with links
3. Deploy Status: Success/Fail
4. LIVE URL VERIFY: connected=true/false
5. FINAL VERDICT: PASS/FAIL
[8/16/2026 5:47 PM] pritam warghade: ============================================================
Q. FULL DATA → FEATURE → MODEL → STRATEGY → BACKTEST → UI LOOP
============================================================

This section is MANDATORY.

System3 is not complete merely because broker connectivity, option chains,
or UI tabs work.

Audit the entire quantitative lifecycle:

RAW DATA
→ DATA QUALITY
→ HISTORY
→ FEATURES
→ LABELS
→ MODEL TRAINING
→ MODEL VALIDATION
→ STRATEGY GENERATION
→ BACKTEST
→ PAPER / SIMULATION
→ PREDICTION
→ ACTUAL RESULT
→ ERROR ANALYSIS
→ SELF-CORRECTION
→ RETRAINING
→ MODEL/STRATEGY PROMOTION
→ PRODUCTION API
→ PRODUCTION UI
→ USER-VISIBLE PROOF
→ CONTINUOUS MONITORING

Every stage requires independent evidence.

============================================================
Q1. DATA FETCH MASTER CHECKLIST
============================================================

Audit all actual data acquisition paths.

DATA CATEGORIES:

A. Market master/reference
- NSE instrument master
- BSE instrument master
- security IDs
- trading symbols
- exchange segment
- underlying
- instrument type
- expiry
- strike
- CE/PE
- lot size
- tick size
- active/inactive status

B. Spot/cash
- NSE equities
- BSE equities
- NSE indices
- BSE indices where supported
- India VIX

C. Derivatives
- index futures
- equity futures
- index options
- equity options

D. Market fields
- LTP
- OHLC
- volume
- bid
- ask
- bid qty
- ask qty
- OI
- OI change
- IV
- Delta
- Gamma
- Theta
- Vega
- Rho where genuinely available/derived
- market timestamp

E. Historical data
- 1m
- 3m
- 5m
- 15m
- 30m
- 1h
- daily
- weekly
where genuinely supported

For EACH dataset prove:

SOURCE
ENDPOINT
CALLER
FETCH FREQUENCY
CACHE
RATE LIMIT
BATCH LIMIT
RETRY
BACKOFF
TIMEOUT
FRESHNESS
OBSERVED_AT
DATA QUALITY
DURABLE STORAGE
RETENTION
CONSUMERS
UI CONSUMER
MODEL CONSUMER
BACKTEST CONSUMER

Classify:

WORKING
PARTIAL
EMPTY
STALE
RATE_LIMITED
NOT_WIRED
UNSUPPORTED
UNKNOWN

============================================================
Q2. DATA QUALITY CHECKLIST
============================================================

For every important dataset test:

- duplicates
- missing timestamps
- missing sessions
- missing symbols
- missing expiries
- missing strikes
- CE without corresponding PE
- PE without corresponding CE
- zero/negative impossible values
- stale quote
- stale OI
- abnormal price jumps
- timestamp disorder
- timezone mismatch
- market-session mismatch
- bad security-ID mapping
- expired contract leakage
- wrong underlying mapping
- wrong exchange segment
- incorrect lot size
- malformed Greeks
- null fields
- source mismatch
- fallback falsely labelled Dhan
- synthetic/mock leakage
- historical/live schema mismatch

For every defect:
trace to exact upstream source and affected downstream consumers.

============================================================
Q3. HISTORICAL DATA CHECKLIST
============================================================

Find where historical data REALLY exists today.

Do not assume architecture documents mean implementation exists.

For each asset class:

NSE equities
BSE equities
indices
futures
index options
equity options

determine:

earliest timestamp
latest timestamp
number of sessions
number of symbols
number of expiries
number of option contracts
granularity
missing percentage
data source
storage technology
storage path/table/bucket/collection
partitioning
compression
retention
backup
versioning
deduplication
restart durability

Answer:

Can this history support:
- model training?
- walk-forward testing?
- options backtesting?
- volatility modeling?
- regime detection?
- prediction-vs-actual validation?

If not:
define exactly what historical-data pipeline must be built.

============================================================
Q4. FEATURE ENGINEERING CHECKLIST
============================================================

Inventory every actual feature used by System3.

Categories to inspect:
[8/16/2026 5:47 PM] pritam warghade: PRICE
- returns
- momentum
- ROC
- moving averages
- EMA
- trend
- gap
- breakout
- support/resistance

VOLATILITY
- ATR
- realized volatility
- implied volatility
- IV rank
- IV percentile
- IV skew
- volatility regime

VOLUME
- volume spike
- relative volume
- VWAP
- volume trend

DERIVATIVES
- OI
- change OI
- PCR
- CE/PE OI ratio
- max pain where valid
- futures basis
- rollover
- IV smile
- Greeks

MARKET REGIME
- trend/range
- bullish/bearish
- volatility regime
- market breadth
- index strength
- sector strength

LIQUIDITY
- spread
- depth
- volume
- OI
- slippage proxy

MULTI-TIMEFRAME
- 1m
- 3m
- 5m
- 15m
- 30m
- 1h
- daily

For every feature record:

feature name
formula
source fields
timeframe
lookback
null handling
normalization
timestamp alignment
future leakage risk
used by model?
used by strategy?
used by UI?
tested?
versioned?

Find missing high-value features, but do not add them merely because they
sound advanced.

============================================================
Q5. FEATURE VALIDATION
============================================================

Every feature must be tested for:

- data leakage
- lookahead
- future-bar usage
- timestamp alignment
- market-open gaps
- expiry rollover
- missing values
- outliers
- feature drift
- unstable distribution
- redundant correlation
- insufficient sample size

Identify which features actually provide predictive information.

Do not assume more features = better model.

============================================================
Q6. LABEL / TARGET CHECKLIST
============================================================

For every prediction/model establish:

WHAT IS BEING PREDICTED?

Examples:
- next-bar direction
- N-minute return
- end-of-day direction
- top gainer probability
- CE vs PE direction
- breakout probability
- target hit before stop
- future volatility
- rank score

For every label:

label definition
prediction horizon
entry reference time
exit/reference time
transaction-cost assumptions
class balance
neutral class
future leakage protection

If target definition is unclear:
model result is NOT_PROVEN.

============================================================
Q7. MODEL INVENTORY CHECKLIST
============================================================

Find every model actually present.

For each:

model name
algorithm
file
artifact path
artifact hash/version
active?
candidate?
obsolete?
input features
output
training date
training period
validation period
sample size
hyperparameters
metrics
calibration
deployment consumer
fallback

Algorithms may include only if actually present:
- logistic regression
- random forest
- XGBoost
- LightGBM
- neural networks
- time-series models
- ensembles
- ranking models
- heuristics/rules

Do not label heuristics as AI/ML.

============================================================
Q8. MODEL TRAINING CHECKLIST
============================================================

Trace:

historical data
→ feature generation
→ label generation
→ train split
→ validation split
→ test split
→ model fit
→ calibration
→ artifact creation
→ registry
→ candidate status
→ promotion

Verify:

- time-series split used?
- walk-forward?
- purged split?
- embargo around overlapping labels?
- class imbalance treatment?
- random seed?
- reproducibility?
- hyperparameter search?
- overfit detection?
- out-of-sample data untouched?
- cost/slippage incorporated where relevant?

============================================================
Q9. MODEL PERFORMANCE CHECKLIST
============================================================

Do NOT use accuracy alone.

Where appropriate calculate/check:

- accuracy
- balanced accuracy
- precision
- recall
- F1
- ROC-AUC
- PR-AUC
- log loss
- Brier score
- calibration
- ranking correlation
- top-K precision
- directional hit rate
- return-weighted hit rate

For strategy outputs also evaluate:
[8/16/2026 5:47 PM] pritam warghade: - expectancy
- profit factor
- Sharpe
- Sortino
- max drawdown
- recovery factor
- win/loss ratio
- average win
- average loss
- tail losses
- trade count
- regime-specific performance

No claim is valid without sample size and test period.

============================================================
Q10. MULTI-MODEL VALIDATION / TOURNAMENT
============================================================

If multiple models/strategies exist, create a fair tournament.

All candidates must use:

same dataset
same timestamps
same train/validation/test periods
same transaction-cost model
same slippage assumptions
same universe
same evaluation metrics

Compare:

MODEL A
MODEL B
MODEL C
CURRENT PRODUCTION MODEL
SIMPLE BASELINE

A sophisticated model must beat a simple baseline before promotion.

Never select a model because it has the most complex algorithm.

============================================================
Q11. STRATEGY INVENTORY CHECKLIST
============================================================

Find ALL strategy logic in repo.

Classify each:

ACTIVE_RUNTIME
WIRED_BUT_DISABLED
PAPER_ONLY
BACKTEST_ONLY
EXPERIMENTAL
DEAD_CODE
OBSOLETE
UNKNOWN

For each strategy record:

strategy name
source files
market
instrument types
timeframes
entry logic
exit logic
stop loss
target
trailing
filters
position sizing
risk
model dependency
data dependency
paper usage
production UI visibility

Look for duplicate strategies under different names/files.

============================================================
Q12. STRATEGY DISCOVERY / BEST-STRATEGY SEARCH
============================================================

Do not invent a “best strategy”.

Build an evidence-based candidate tournament.

Possible strategy families to compare only where supported:

trend
momentum
mean reversion
breakout
volatility
OI-based
PCR-based
IV/skew
multi-timeframe
regime-dependent
ML ranking
hybrid rule + ML
ensemble

Compare by:

out-of-sample expectancy
drawdown
profit factor
stability
sample size
market-regime robustness
liquidity
cost sensitivity
slippage sensitivity

“Best” means robust across unseen data, not highest historical P&L.

============================================================
Q13. BACKTEST CHECKLIST
============================================================

Backtest engine must prove:

- historical dataset authority
- timestamp ordering
- no future data
- entry timing
- exit timing
- realistic fills
- bid/ask where available
- spread
- slippage
- brokerage
- STT
- exchange charges
- GST
- stamp duty
- lot size
- liquidity filter
- OI filter
- volume filter
- expiry behavior
- stop/target ordering
- gap behavior
- intrabar ambiguity handling
- rejected trades
- duplicate signal handling

For options specifically:
- historical contract actually existed
- correct expiry
- correct strike
- CE/PE mapping
- no future option-chain knowledge

============================================================
Q14. WALK-FORWARD / ROBUSTNESS CHECKLIST
============================================================

Require where feasible:

TRAIN
→ VALIDATE
→ TEST
→ ROLL FORWARD
→ REPEAT

Compare performance across:

bull market
bear market
sideways
high volatility
low volatility
expiry week
normal week
high-gap days
event days

A model/strategy that works only in one regime must be labelled accordingly.

============================================================
Q15. PREDICTION-VS-ACTUAL CHECKLIST
============================================================

Every production prediction should eventually have:

prediction_id
model_version
strategy_version
symbol
instrument
timestamp
horizon
predicted direction
predicted probability
predicted return/rank
actual outcome
actual return
correct/incorrect
error magnitude

Store it durably.

UI should expose useful summary:
[8/16/2026 5:47 PM] pritam warghade: predictions
completed outcomes
hit rate
calibration
missed opportunities
false positives
false negatives
top-ranked prediction performance

============================================================
Q16. SELF-LEARNING / SELF-CORRECTION — SAFE DEFINITION
============================================================

Do NOT implement uncontrolled automatic model self-modification.

“Self-learning” must mean a controlled evidence loop:

NEW REAL DATA
→ append immutable history
→ calculate actual outcomes
→ prediction error analysis
→ drift check
→ candidate retraining
→ candidate evaluation
→ compare with current champion
→ independent validation
→ promotion gate
→ deploy candidate only if proven better
→ rollback available

The active production model must NEVER overwrite itself merely because a
single new trade/prediction failed.

============================================================
Q17. CHAMPION / CHALLENGER MODEL CHECKLIST
============================================================

Maintain:

CHAMPION = current approved model
CHALLENGER(S) = newly trained candidate models

Promotion requires:

minimum sample size
out-of-sample improvement
no material drawdown degradation
calibration acceptable
no leakage
reproducible training
artifact version/hash
rollback path
independent validation

If challenger fails:
keep champion.

If all models fail:
system must be allowed to say:
NO MODEL READY.

============================================================
Q18. SELF-CORRECTION CHECKLIST
============================================================

When prediction error occurs:

Do NOT immediately alter model.

Classify error:

DATA_ERROR
FEATURE_ERROR
MODEL_ERROR
REGIME_CHANGE
LIQUIDITY
SLIPPAGE
EXECUTION_ASSUMPTION
RANDOM_NOISE
UNKNOWN

Then determine:

does feature need correction?
does label need correction?
does model need retraining?
does strategy need filtering?
does data source need fixing?
is no change justified?

Every correction requires regression testing.

============================================================
Q19. PAPER / SIMULATION VALIDATION
============================================================

Before any model/strategy is treated as production-ready:

prediction
→ paper decision
→ paper entry
→ mark-to-market
→ paper exit
→ fees/slippage
→ P&L
→ reconciliation

must be proven.

Every paper record requires:
source
model version
strategy version
timestamp
symbol
entry
exit
reason
P&L
actual data provenance

============================================================
Q20. MODEL/STRATEGY PROMOTION GATE
============================================================

No strategy/model can be promoted merely because:

- backtest P&L is high
- accuracy improved
- one AI agent says PASS
- one day was profitable

Promotion requires:

DATA PASS
FEATURE PASS
LEAKAGE PASS
TRAINING PASS
OUT_OF_SAMPLE PASS
BACKTEST PASS
COST PASS
RISK PASS
PAPER PASS
MULTI-AGENT REVIEW PASS
CHATGPT CONSOLIDATION PASS
PRODUCTION UI TRUTH PASS

============================================================
Q21. URL-FIRST FINAL TRUTH LAW
============================================================

This is critical.

GitHub, GCP logs, databases and source code are diagnostic/implementation
evidence.

The USER'S FINAL ACCEPTANCE surface is the actual production URL:

https://genesis-system3-web-doq2wplepa-el.a.run.app/ui

Therefore every user-relevant capability eventually needs visible,
read-only truth in the production UI.

If important information exists only in GitHub/logs/backend and cannot be
seen from the production UI:

classify:

UI_OBSERVABILITY_GAP

and define the required UI upgrade.

============================================================
Q22. REQUIRED USER-VISIBLE PROGRESS/TRUTH SURFACE
============================================================

Audit whether existing Truth/System/Gates/Data Integrity/ML/Performance tabs
already expose the following.

If not, define a future consolidated read-only UI improvement.

The user should eventually be able to see from the URL:
[8/16/2026 5:47 PM] pritam warghade: SYSTEM STATUS
- serving SHA
- current runtime revision
- broker
- token version identifier only
- data status
- market session
- safety locks

DATA PIPELINE
- instrument universe coverage
- quote coverage
- option-chain coverage
- historical-data coverage
- freshness
- missing data
- 429 status

FEATURE PIPELINE
- feature-set version
- latest feature generation
- missing/stale features
- data-quality status

MODEL
- active model
- version
- trained date
- training-data period
- validation result
- model state

TRAINING
- last training
- next scheduled evaluation
- candidate models
- champion/challenger
- promotion blocked reason

PREDICTION
- latest predictions
- confidence
- actual-result status
- rolling validation

BACKTEST
- tested period
- trades
- expectancy
- drawdown
- profit factor
- costs included?
- leakage gate

PAPER
- open positions
- closed trades
- P&L
- reconciliation
- model/strategy source

STRATEGY
- active strategy
- candidate strategies
- validation status
- why strategy chosen

AGENT/REMEDIATION PROGRESS
- current wave
- current owner
- PASS/FAIL/BLOCKED
- next dependency
- last verified UTC/IST

Do not expose secrets or sensitive internal credentials.

============================================================
Q23. URL-ONLY USER PROGRESS REQUIREMENT
============================================================

The long-term user experience should NOT require the user to read:

GitHub Actions
Cloud Run logs
Secret Manager
terminal commands
local reports

for routine System3 status.

Those sources remain engineering evidence.

But the production UI must summarize the authoritative safe outcome.

If this currently does not exist:
mark it as a confirmed product/observability gap.

Do not fabricate status merely to fill the UI.

============================================================
Q24. EVERY AGENT MUST VERIFY UI AFTER IMPLEMENTATION
============================================================

For every production-relevant change:

AGENT A:
diagnoses/fixes backend/data/model.

AGENT B:
independently verifies code/tests.

BUT FINAL PRODUCT VERIFICATION MUST INCLUDE:
NEW production browser evidence.

Agents must not call final PASS from:
- code review
- unit tests
- API only
- logs only
- GitHub workflow only

Final user-facing PASS requires the relevant production URL/tab visibly
reflects correct semantic state.

============================================================
Q25. URL VERIFICATION MATRIX
============================================================

For each implemented micro-part record:

MICRO_PART
EXPECTED_UI_TAB
EXPECTED_VISIBLE_RESULT
BACKEND_API
SOURCE
FRESHNESS
SCREENSHOT
CAPTURE_TIME
SERVING_SHA
PASS/FAIL

Examples:

broker reliability
→ Broker / Truth / System

option-chain source
→ Option Chain

model version
→ ML / Truth

prediction performance
→ Prediction Audit / Performance

historical coverage
→ Data Integrity / ML

backtest metrics
→ Performance / ML or future Backtest surface

paper lifecycle
→ Paper / Positions / Performance

If no suitable tab exists:
UI_GAP = TRUE.

============================================================
Q26. CHART / GRAPH CHECKLIST
============================================================

For every meaningful dataset determine whether the UI should provide:

PRICE
- candlestick
- line
- multi-timeframe

DERIVATIVES
- CE/PE OI
- OI change
- volume
- PCR
- IV smile
- IV skew
- Greeks by strike
- OI heatmap

MODEL
- prediction vs actual
- rolling accuracy
- calibration
- model drift
- feature importance
- regime performance

STRATEGY
- equity curve
- drawdown
- trade distribution
- expectancy
- profit factor
- regime split

SYSTEM
- quote freshness
- API latency
- HTTP 429 timeline
- missing-symbol coverage
- scheduler/job health
- model-training timeline

Never add decorative graphs.

Every graph needs:
question answered
authoritative data source
backend endpoint
history availability
UI destination
test
production URL proof.
[8/16/2026 5:47 PM] pritam warghade: ============================================================
Q27. CONTINUOUS BACKGROUND PROGRESS LOOP
============================================================

Background/automation work must follow the same dependency graph.

Do not run all remediation tasks against the sa