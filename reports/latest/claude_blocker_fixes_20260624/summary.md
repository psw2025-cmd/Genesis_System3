# Blocker Fix Session — 2026-06-24 (Claude)

## All 4 blockers addressed, validated, committed

## B1 — DATA INTEGRITY (phantom-priced rows) ✅ FIXED + PROVEN
2-layer defense against corrupt bhavcopy rows (the -1.25L BANKNIFTY 60000CE@4440 bug):
- LAYER 1 (source): datasource_manager._parse_bhavcopy drops rows where
  extrinsic value > 5% of spot (3% for far-OTM). Bad rows never enter pipeline.
- LAYER 2 (decision): dhan_trade_rules.evaluate rejects same as AVOID.
- Calibration: extrinsic-based (ltp - intrinsic), tested against real bad row +
  5 legit rows. Phantom 4440 → DROP, all legit (ATM/OTM/ITM) → KEEP. PROVEN.

## B2 — PROFITABILITY GATE ✅ TOOL BUILT (needs laptop data to run)
New scripts/pf_gated_backtest.py — HONEST backtest, unlike old proof:
- Old costed_walkforward_proof.py PASSed on pipeline-correctness even at -102k net.
- New version: backtest_pass=True ONLY if Profit Factor >= 1.20 AND net > 0 after costs.
- Adds: phantom guard, near-ATM filter (3%), per-trade risk cap (2000), data-quality counts.
- Self-tested: phantom detection, cost model, PF logic all verified.
- TO RUN: needs storage/bhavcopy/*.csv on laptop (not in repo). Run:
  python scripts/pf_gated_backtest.py
  → writes reports/latest/recent_backtest_walkforward_proof/pf_gated_backtest.json

## C1 — SILENT MODEL FALLBACK ✅ FIXED (Genesis bug class)
ml_predictor.predict_direction now flags model health on EVERY row:
- prediction_source: ML_MODEL | NO_MODEL_FALLBACK | PREDICT_FAILED_FALLBACK | DELTA_PROXY_DEGRADED
- model_healthy: True only for real ML output
- LOUD error logs (not print) when model None or predict fails
- GATE: dhan_trade_rules blocks any trade where model_healthy=False
- Result: system can NEVER silently trade on 0.5-noise (the original Genesis catastrophe)

## C3 — RISK CONFIG RECONCILE ✅ FIXED
config/live_trade_config.py is now single source of truth with EXPLICIT units:
- HARD ₹ caps (authoritative): MAX_DAILY_DRAWDOWN_RUPEES=5000, MAX_RISK_PER_TRADE_RUPEES=2000
- SOFT % (advisory only): MAX_DAILY_LOSS_PCT=10.0, MAX_PORTFOLIO_HEAT_PCT=6.0
- Resolves the prior ambiguity (optimizer's max_daily_loss=10.0 was a % not ₹).

## STILL REQUIRED before real money (honest)
1. Run pf_gated_backtest.py on laptop with real bhavcopy → must show PF>=1.20
2. 5+ days prediction validation at rho>=0.70 (1/5 done, current rho=0.20)
3. Real market-day paper lifecycle proof (live 09:15-15:30 session)
4. Verify phantom guard against full historical bhavcopy (clean the dataset)

## VERDICT (unchanged — these fixes REDUCE risk, don't grant readiness)
trade_ready = FALSE
verdict = ANALYZER_READY_PROOF_INCOMPLETE
The 4 fixes make the system SAFER (no phantom trades, no silent-noise trades,
clear risk units, honest backtest tool). They do NOT prove profitability —
that still requires the laptop runs above.

## For local agents
- Keep all 4 guards — they are real-money safety, not optional
- Run node --check (dashboard) and python -m py_compile (engine) before pushing
- Next highest-value: get bhavcopy data + run pf_gated_backtest.py
