# Catalyst Early Warning Intelligence — Implementation Authority

Status: PROPOSED / DOCS-ONLY / NO RUNTIME MUTATION
Updated: 2026-08-22
Authority: GitHub current `main` + GCP runtime truth. LIVE/orders remain disabled.

## 1. Product goal

System3 must not become a simple news widget. The target is a **Catalyst Early Warning Intelligence System** that uses trusted live/near-live information to improve prediction before a large move is fully priced.

Canonical flow:

`REAL SOURCE -> SOURCE TRUST -> DEDUP/ENTITY -> CATALYST CLASSIFIER -> HISTORICAL ANALOGUES -> CURRENT MARKET/OPTION CHAIN -> EARLY-MOVE STATE -> UNDERLYING PREDICTION -> OPTION OPPORTUNITY -> TOP-10 RANKING -> PAPER PREDICTION -> ACTUAL OUTCOME -> CALIBRATION/LEARNING -> PRODUCTION UI`

The objective is **best calibrated prediction and earliest useful lead time**, not retrospective explanation after a move has already happened.

## 2. Required prediction surfaces

### Index options
Required live-market PAPER intelligence for:
- NIFTY
- BANKNIFTY
- FINNIFTY
- MIDCPNIFTY
- other supported index options only when exact broker/API/UI coverage is proven

### Equity options
Scan the full eligible Indian F&O universe, rank candidates cross-sectionally, then perform deeper option-chain analysis on shortlisted symbols. Output a **Top 10 Equity Option Opportunities** list.

### Multibagger equity research
Maintain a separate longer-horizon **Top 10 Multibagger Research** surface. Do not mix intraday option logic with long-horizon equity scoring. Option overlays are allowed only when F&O/liquidity/expiry suitability are proven.

## 3. Live/near-live source architecture

### Free baseline — must keep the system operational without subscriptions

| Priority | Source class | Examples | Primary use | Rules |
|---|---|---|---|---|
| P0 | Official exchange/company disclosures | NSE corporate filings/RSS, BSE announcements, company IR | Earnings, orders, contracts, guidance, board outcomes, management, corporate actions | Highest trust; preserve source URL + first-public timestamp |
| P0 | Regulatory | SEBI | Orders, circulars, enforcement, listing/regulatory events | Highest trust |
| P0 | Broker market data | Dhan REST/WS/option-chain/security master/historical where supported | LTP/OHLC/volume/OI/IV/Greeks/bid-ask/chain/universe | Market confirmation and option scoring; rate-limit aware |
| P1 | Macro official | RBI, Govt/PIB, ministries, official economic releases | Rates, policy, sector/macroeconomic catalysts | High trust |
| P1 | Secondary official | Exchange financial results, board meetings, corporate actions, insider/promoter disclosures | Event enrichment / multibagger | High trust |
| P2 | Secondary news discovery | reputable financial media / free feeds where technically/legal suitable | Context and cross-confirmation | Never outrank official source |
| P3 | Public social chatter | public social sources where legally/technically suitable | Weak attention/rumour feature only | Never primary evidence; cannot alone produce HIGH opportunity |

### Optional subscription adapters
Premium subscriptions must **enhance** System3, never become a single point of failure.

If a user configures a supported premium provider, System3 should automatically test and activate it through a provider adapter. If it expires/fails, the router falls back to the free baseline and locally degrades only affected features.

Provider health contract:

```text
provider_name
connected
trust_score
latency_ms
last_success_at
freshness_seconds
error_rate
rate_limit_state
cost_tier
capabilities[]
```

Routing principle:

`official/free healthy -> use official truth`
`premium healthy and adds latency/depth/coverage -> enrich/confirm`
`provider failed -> next healthy provider`
`no fresh provider -> last verified snapshot + DEGRADED`
`never fabricate`

## 4. No-single-point-of-failure rule

One provider failure must not stop the full system.

Examples:
- Catalyst: NSE -> BSE -> Company IR -> SEBI/RBI/Govt -> optional premium -> verified snapshot
- Market price: Dhan WS -> Dhan REST -> last verified snapshot (with age visible)
- Option chain: Dhan option-chain -> last verified chain snapshot (with source/freshness visible)
- Macro: RBI/Govt -> optional premium -> last verified official release

The UI must expose the active route, fallback state, freshness and degradation reason.

## 5. Point-in-time / anti-lookahead authority

Every event and prediction must preserve:

```text
event_first_public_at
source_received_at
model_cutoff_at
prediction_created_at
market_snapshot_at
source_url/source_id
content_hash
```

Historical validation may use only information available at `model_cutoff_at`. Future information is forbidden. Any backtest that cannot prove point-in-time lineage is NOT_ACCEPTED.

## 6. Catalyst intelligence blocks

1. **Source trust engine** — authority, freshness, cross-confirmation.
2. **Deduplication/fingerprint** — same announcement mirrored by many sites counts once.
3. **Entity resolution** — company, symbol, sector, suppliers/customers/peers/index exposure.
4. **Catalyst classifier** — order win, result surprise, guidance, regulation, promoter action, legal risk, capacity expansion, corporate action, macro policy, etc.
5. **Materiality** — scale event relative to revenue/profit/market cap/order book where data exists.
6. **Novelty** — routine/repeated vs genuinely new information.
7. **Expectation/surprise engine** — actual outcome vs market expectation; raw positive news may still be a negative surprise.
8. **Historical analogue retrieval** — same company/sector/event type/regime/size bucket.
9. **Reaction model** — direction, magnitude, lead time, peak time, failure risk.
10. **Sector/relationship graph** — primary and secondary beneficiaries/losers.

## 7. Historical Catalyst Reaction Library

For each event capture, when supported by data:

- underlying price at -5D, -1D, -60m, -15m, event, +1m, +5m, +15m, +30m, +60m, close, +1D, +3D, +5D
- volume / relative volume
- market/sector regime
- option-chain snapshot: IV, OI, volume, skew, bid/ask, Greeks, ATM/OTM premiums
- best CE/PE realized multiple by strike/expiry
- time-to-peak
- max favorable/adverse excursion
- IV expansion/crush
- sector/index spillover
- outcome classification: continuation / delayed / false breakout / opposite / already priced / illiquid

No historical accuracy, 2x/5x/10x probability or hit-rate may be shown unless the sample size and point-in-time lineage are available.

## 8. Two-model prediction authority

Never collapse underlying direction and option payoff into one number.

### Model A — underlying
Outputs:
- direction probabilities
- expected move distribution
- expected reaction window
- confidence/calibration
- market/sector regime

### Model B — option opportunity
Outputs:
- eligible expiry/strike candidates
- liquidity/spread gate
- IV/volatility state
- OI/skew structure
- theta/gamma/event-decay risk
- probabilities of 1.5x / 2x / 5x / 10x where statistically supported
- expected time-to-peak

Underlying can be correct while an option loses due to IV crush/theta/spread; both scores must remain separate.

## 9. Early-move state machine

Mandatory states:

`NOT_PRICED -> EARLY -> CONFIRMING -> EXTENDED -> EXHAUSTED`

Ranking priority is normally:

`NOT_PRICED > EARLY > CONFIRMING`

EXTENDED/EXHAUSTED candidates receive a chase penalty or rejection unless a separate continuation model proves edge.

The state must use event timestamp, current price move, volatility, volume and historical analogue response — never an LLM-only label.

## 10. Prediction ensemble

Candidate features may include, subject to source/data proof:

- catalyst trust/materiality/novelty/surprise
- historical analogue strength and consistency
- price/trend/momentum
- volume/relative volume
- option OI/PCR/skew/IV/Greeks/bid-ask/liquidity
- market/sector breadth and regime
- macro sensitivity
- sector/relationship graph
- already-moved/chase penalty
- stale-data/provider-degradation penalty
- model calibration and sample-size penalty

A single sentiment score is insufficient.

## 11. Whole-universe scan design

Do not continuously request full option chains for every stock.

Preferred flow:

`full eligible universe -> cheap/streaming first-stage features -> Top 50 -> catalyst/technical/regime rank -> Top 20 -> deep option-chain requests -> Top 10`

The four required index chains remain separately prioritized.

This architecture is required to limit Dhan 429/805 pressure and request amplification.

## 12. Model tournament before production ranking

Before choosing the champion, run read-only/offline/shadow comparisons across at least:

1. technical baseline
2. technical + option-chain
3. catalyst + historical analogue
4. technical + catalyst
5. full ensemble
6. full ensemble + early-move penalty
7. full ensemble + regime filter
8. full ensemble + sector graph
9. calibrated probability model
10. champion/challenger ML variants where justified

Required metrics:
- direction precision/recall
- Top-10 precision
- major-move recall
- median lead time before move
- expected value / costed paper expectancy
- max adverse excursion / drawdown
- option 1.5x/2x/5x precision where sample size permits
- false-positive rate
- probability calibration
- performance by market regime/event class
- liquidity/slippage realism
- stale/degraded-source rejection quality

Highest raw backtest accuracy alone does not select the winner.

## 13. Mandatory smoke/dry-run scenarios

At minimum:
- normal market-open day
- major corporate catalyst day
- expiry/high-gamma day
- gap-up/gap-down already-priced catalyst
- market-closed/weekend
- high-volatility day
- low-volatility day
- RBI/macro event
- stock-specific earnings/result event
- false/low-trust rumour
- illiquid option
- provider outage/fallback
- Dhan 429/805/degraded market feed
- stale snapshot
- duplicate same-news from multiple sources

Each scenario must produce an artifact with input provenance, expected behavior and actual result.

## 14. Non-coder UI architecture

Primary new central tab: **Catalyst & Opportunities**

Recommended subviews:
- Early Warning
- Index Setups
- Equity Options Top 10
- Multibagger Top 10
- News & Catalysts
- Upcoming Events
- Accuracy & History
- Sources / Provider Health

Existing `OptionsIntelligence` and `MultibaggerResearch` should be reused/extended rather than duplicated.

Every primary opportunity card must answer four questions:
1. What happened?
2. What can it affect?
3. Has the move started / is it already priced?
4. What should the user watch next?

Example visible fields:

```text
RELIANCE — EARLY OPPORTUNITY
Source: NSE OFFICIAL ✓
Detected: 14:03:07 IST
Catalyst: Large Contract
Move state: NOT_PRICED
Underlying P(up): 72%
Expected move: +1.7% to +3.4%
Historical analogues: 83
Option opportunity: HIGH
Liquidity: PASS
Freshness: 11 sec
Execution: PAPER / ORDERS OFF
[WHY?] [OPEN CHAIN] [HISTORY] [SOURCE]
```

No undefined “AI score” without WHY/evidence drill-down.

## 15. Provider UI behavior

Non-coder status examples:

```text
NSE Official       PRIMARY ✓
BSE Official       BACKUP ✓
Dhan Market Data   LIVE ✓
Premium Provider   NOT CONFIGURED
System             OPERATIONAL
```

If premium expires:

```text
Premium Provider: SUBSCRIPTION EXPIRED
Fallback: NSE/BSE
System: OPERATIONAL
Prediction confidence adjusted
```

No full-screen failure solely because one provider is unavailable.

## 16. Paper prediction / learning loop

Every accepted opportunity must freeze a paper prediction record containing:
- exact prediction timestamp
- model/version/hash
- input/source hashes
- direction probabilities
- expected move distribution
- horizon
- option candidate and liquidity state
- early-move state
- WHY/evidence list

Later evaluator captures actual 1m/5m/15m/30m/60m/EOD/+1D results, maximum favorable/adverse move, option payoff path and miss reason.

The model can learn/recalibrate only from immutable observed outcomes. Never rewrite old predictions after seeing the result.

## 17. Accuracy UI

Required visible performance, with sample size:
- predictions / eligible predictions
- direction precision
- Top-10 precision
- early-detection rate
- median lead time
- probability calibration buckets
- option multiplier precision where statistically supported
- false positives
- failure reason distribution
- regime/event-class breakdown

No “world-class accuracy” claim without reproducible out-of-sample evidence.

## 18. Implementation sequence

### Phase 0 — read-only existing-source inventory
Classify every relevant current repo/runtime path as:
`EXISTS_WORKING / EXISTS_BROKEN / EXISTS_UNUSED / DUPLICATE / MISSING / UNKNOWN`

Inventory must cover:
- Dhan REST
- Dhan WS
- option chains
- security master / F&O universe
- historical data
- existing scanners/rankers
- prediction models/features
- multibagger inputs
- news/sentiment/event code
- provider/fallback/cache code
- backend APIs/store/UI consumers

### Phase 1 — source capability smoke tests
For every proposed source, measure:
- Cloud Run/GCP accessibility
- auth requirement
- latency
- freshness
- completeness
- update cadence
- dedup quality
- rate-limit/blocking/CAPTCHA behavior
- timestamp quality
- historical depth
- failure behavior
- cost/licensing suitability
- predictive usefulness potential

### Phase 2 — provider abstraction + provenance
Implement provider interface/router/fallback without changing prediction ranking yet.

### Phase 3 — trusted catalyst ingestion + point-in-time store
Official/free baseline first. Optional premium adapters remain plug-ins.

### Phase 4 — historical reaction library
Build immutable event/reaction datasets and anti-leakage checks.

### Phase 5 — model tournament
Shadow/dry-run candidate models; select champion only from out-of-sample evidence.

### Phase 6 — early-move + option opportunity engines
Integrate catalyst, technical, market regime and option-chain evidence.

### Phase 7 — Top-10 ranking surfaces
Index, equity options, and multibagger remain distinct horizons/models.

### Phase 8 — non-coder production UI
Central `Catalyst & Opportunities` plus compact summaries in Options Intelligence, Prediction, Scanner and Multibagger.

### Phase 9 — shadow PAPER run
No real orders. Freeze prediction before outcome.

### Phase 10 — outcome/calibration loop
Automated evaluation, miss classification, champion/challenger governance and drift detection.

## 19. Acceptance definition

This feature is NOT DONE because:
- news appears in UI
- a sentiment model runs
- a backtest is high
- Top-10 cards render

DONE requires:

`REAL SOURCE -> exact timestamp/provenance -> model cutoff -> historical evidence -> current market/option evidence -> early prediction -> PAPER record -> production UI -> later immutable outcome -> calibration/history`

For production UI, require exact-serving SHA/revision plus API -> frontend store -> rendered UI semantic equality, source/freshness visibility, responsive desktop/mobile proof, and no placeholder/dummy/hardcoded market intelligence.

## 20. Safety / authority lock

- ANALYZE/PAPER only
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- no broker order API calls for this feature
- no secret/token exposure
- no IAM weakening
- no blind token rotation
- no provider may fabricate data on failure

## 21. Agent coordination / ownership

Before any implementation, agents must read:
1. `AGENTS.md`
2. `docs/RUHI_RULE_V2.md`
3. `docs/handoffs/CURSOR_TO_CHATGPT_PATH_INDEX.md`
4. `reports/coordination/ruhi_task_ledger.csv`
5. `docs/handoffs/MULTI_AI_COORDINATION_LIVE.md`
6. Issue #188
7. this document

One write lane per file/defect surface. Do not overlap Cursor/ChatGPT/Claude work.

Current implementation directive:
- Do **not** interrupt or widen Cursor RUHI-022 / PR #321.
- First executable Catalyst task after current owned P0 lane is clear: **Phase 0 read-only existing-source inventory**.
- No production implementation PR for Catalyst Early Warning until the inventory and source smoke-test matrix identify the narrowest reusable architecture.
- Every BLOCKED/NOT_PROVEN item must include exact error + path/function + next proof-producing action.
- Every completion must link to reproducible artifact(s).

## 22. First proof artifact to produce

`reports/coordination/catalyst_source_capability_matrix.csv`

Recommended columns:

```text
source_id
category
provider
free_or_paid
present_in_repo
repo_paths
present_in_gcp
access_method
requires_secret
live_or_delayed
expected_cadence
observed_latency_ms
observed_freshness_s
coverage
historical_depth
rate_limit
failure_mode
fallback_provider
trust_tier
legal_notes
prediction_use
smoke_result
proof_artifact
owner
status
next_action
```

The matrix must be produced read-only first. It becomes the authority for deciding what to reuse, add, reject or reserve for optional subscription adapters.
