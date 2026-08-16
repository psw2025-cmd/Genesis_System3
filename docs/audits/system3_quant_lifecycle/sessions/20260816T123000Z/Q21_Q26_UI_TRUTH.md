# Q21–Q26 — URL-first truth & charts

**Production UI:** https://genesis-system3-web-doq2wplepa-el.a.run.app/ui  
**Law:** GitHub/GCP diagnose; **URL is user acceptance surface**.

## Q21 URL-first — **PARTIAL**
Broker/chains/system health visible. Full Q lifecycle truth **not** fully visible → many **UI_OBSERVABILITY_GAP**.

## Q22 Required surfaces

| Surface | Tab(s) | Status |
|---------|--------|--------|
| SYSTEM STATUS (SHA, broker, token ver, locks) | System / Broker / TopBar / Data Integrity | **PARTIAL** (improved token chip pending deploy from PR #245) |
| DATA PIPELINE coverage/freshness/429 | Data Integrity / System | **PARTIAL** |
| FEATURE PIPELINE version | — | **UI_OBSERVABILITY_GAP** |
| MODEL active/version/trained | ML Model | **PARTIAL** |
| TRAINING champion/challenger | — | **UI_OBSERVABILITY_GAP** |
| PREDICTION vs actual rolling | Prediction Audit / Accuracy | **PARTIAL** |
| BACKTEST metrics/costs/leakage | Performance / ML | **UI_OBSERVABILITY_GAP** / PARTIAL |
| PAPER lifecycle | Paper Trades / Positions | **PARTIAL** |
| STRATEGY why-chosen | — | **UI_OBSERVABILITY_GAP** |
| AGENT/REMEDIATION progress | — | **UI_OBSERVABILITY_GAP** |

## Q23 URL-only user progress — **GAP CONFIRMED**
Routine status still often requires GitHub Actions / logs / local reports.

## Q24 Verify UI after implementation — **POLICY ADOPTED**
Broker fix used live URL + browser TopBar proof. Future waves must keep this.

## Q25 URL verification matrix (examples)

| MICRO_PART | Tab | Expected | API | Result |
|------------|-----|----------|-----|--------|
| Broker reliability | Broker / Decision Intel | Connected | `/api/broker/status` | **PASS** (v259) |
| Gain rank | Rankings / related | Table | `/api/gain_rank` | **PARTIAL** (payload exists) |
| Accuracy ρ | Accuracy / Performance | Trend | `/api/accuracy_trend` | **PARTIAL** |
| Option chain source | Option Chain | source=dhan visible | chain APIs | **PARTIAL** (weekend/market dependent) |
| Champion model | ML | version+hash | — | **UI_GAP** |
| Costed backtest | Performance | expectancy+costs | — | **UI_GAP** |

## Q26 Charts — **PARTIAL**
Some performance/accuracy visuals exist; institutional set (IV smile, calibration, equity curve with costs, 429 timeline, training timeline) largely **missing or decorative-risk**. Every new graph needs authoritative API + URL proof.

## Q27 Continuous background loop
**Instruction truncated** in `chatgpt_instruction_for_cursar_2.md` — cannot complete Q27 textually; treat as **INCOMPLETE_INSTRUCTION**.
