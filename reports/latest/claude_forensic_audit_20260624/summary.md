# Full Repo Forensic Audit — 2026-06-24 (Claude, bug-finder + option-chain pass)

## Scope: 1,748 files (868 .py), 202 trading-critical modules audited

## ════════════════════════════════════════════
## 🔴 BLOCKER-LEVEL FINDINGS (must fix before real money)
## ════════════════════════════════════════════

### B1 — DATA INTEGRITY: phantom-priced contracts [PARTIALLY FIXED]
The only costed walk-forward proof (costed_walkforward_proof.json) shows
net -₹102,636 over 8 trades. ROOT CAUSE: ONE corrupted row.
- BANKNIFTY 60000 CE entry ₹4,440 → exit ₹281 = single -₹125,051 loss
- BANKNIFTY spot was ~57,300; a 60000 CE (2,700 pts OTM) cannot be worth ₹4,440
- Fair value ≈ ₹200-400 (the ₹281 exit is correct; the ₹4,440 ENTRY is the bug)
- Bad bhavcopy row or wrong strike match fed a phantom 15x premium
- WITHOUT this one row: net = +₹22,415 on 7 trades
- FIX APPLIED: phantom-premium guard in dhan_trade_rules.py rejects any option
  priced above intrinsic + 12% of spot. But the UPSTREAM bhavcopy cleaning
  still needs a dedup/sanity pass (laptop task).

### B2 — STRATEGY NOT PROVEN PROFITABLE
Even excluding the bad row, the "OI-change-ranked ATM CE, next-day exit"
strategy is only marginally positive and was NOT designed as a live signal
(file explicitly says "not a trading signal"). There is NO costed backtest of
the actual live signal pipeline (ml_predictor + enhanced_scorer) showing
PF ≥ 1.20 after costs. Per user's own prior gate: NO strategy is APPROVED FOR LIVE.

### B3 — PREDICTION QUALITY: rho=0.20, RETRAIN_NEEDED
market_validation_2026-06-12: Spearman 0.20, hit_rate 0.667, retrain_signal=true.
Only 1 validation day on record. Gate requires 5+ days at rho≥0.70.
Predicted ranking [NIFTY,MIDCPNIFTY,FINNIFTY,BANKNIFTY] vs actual
[NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY] — only NIFTY rank correct.

## ════════════════════════════════════════════
## 🟡 CODE-QUALITY / RISK FINDINGS
## ════════════════════════════════════════════

### C1 — Silent model-fallback (Genesis bug pattern resurfacing)
ml_predictor.predict_direction() returns ml_probability=0.5 (neutral) when
model is None — does NOT raise or loudly flag. If the model silently fails to
load (the original Genesis catastrophe), the system trades on 0.5 noise.
RECOMMENDATION: hard-fail or set a LOUD health alert when model is None during
market hours, never silently degrade to 0.5.

### C2 — Legacy "Angel One" cruft in Dhan executor
dhan_trade_executor.py docstrings + comments still say "Angel order payload",
"ANGEL ONE TRADE EXECUTOR". Cosmetic but risky — suggests copy-paste lineage;
verify build_order_payload field names match Dhan, not Angel, before any live use.

### C3 — Risk config inconsistency
config/live_trade_config.py: MAX_RISK_PER_TRADE_RUPEES=2000, MAX_DAILY_DRAWDOWN=5000
dhan_risk_profile_optimizer_v3.py: max_daily_loss=10.0 (10 what? % or ₹?)
These two risk ceilings are not reconciled. Before live, ONE source of truth.

## ════════════════════════════════════════════
## 🟢 CONFIRMED SAFE
## ════════════════════════════════════════════
- LIVE_TRADING_ENABLED=False, USE_LIVE_EXECUTION_ENGINE=False (hard-gated)
- dhan_trade_executor: pure DRY_RUN, no live API calls
- dhan_readonly: place/modify/cancel_order all raise RuntimeError
- Cost model is realistic (₹20/side + STT + exchange + 18% GST + SEBI + slippage)
- Position limits enforced (10/day, 3/underlying)

## ════════════════════════════════════════════
## REAL-MONEY READINESS VERDICT
## ════════════════════════════════════════════
trade_ready = FALSE
verdict = ANALYZER_READY_PROOF_INCOMPLETE
Top 3 blockers before ANY real capital:
  1. Clean bhavcopy data + prove phantom guard works (B1)
  2. Costed backtest of the ACTUAL live signal pipeline, PF≥1.20 (B2)
  3. 5+ days rho≥0.70 prediction validation (B3, 1/5 done)

## For local AI agents (Cursor/Codex/Gemini/DeepSeek)
- DO NOT enable live trading to "test" — gates exist for a reason
- The phantom-premium guard (dhan_trade_rules.py) must stay; it's real-money safety
- Next highest-value task: bhavcopy data cleaner + costed backtest of live pipeline
- Run `node --check dashboard/app.js` before any dashboard push (multi-agent dupe risk)
