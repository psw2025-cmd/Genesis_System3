# System3 patch 0021 — Cursor verification (2026-08-26)

**Status:** VERIFIED locally. Not yet on `origin/main`.  
**Agent:** Cursor cloud run `bc-a73319a2-01a2-482a-a4b4-92e50e5393e4`  
**Base:** `0d6955987115f88b710aca0f0f0dec68d23fa6bc` (`main` after #371)  
**Gift SHA Claude named:** `b33685e0f` (#370). Main moved once more with docs-only #371.

## Live cross-check (before any code change)

| Source | Result |
|---|---|
| Gmail `1a03f7a69595be5d` 19:09 UTC | Claude: one consolidated patch `0021-consolidated-t9-t11-t12-r2r3-t14.patch`. **No attachment bytes.** Do not use 0019/0020. |
| GitHub `claude/` and `claude/patches/` | **Missing** on `main`. Search for `0021-consolidated` returned 0 files. |
| Cursor cloud | This run only. Message queue empty. |
| Live `/api/state` snapshot | Broker connected, 11 holdings, live trading OFF. `auto_refresh` still said `"Token generated via PIN + TOTP (fully automated)"` while `attempted=false`, `success=false`, `skipped=AUTO_REFRESH_DISABLED_OR_LIVE_GATE`. `canonical_rotation` still showed a stale 403 while skipped. |

## What was implemented (Cursor reconstruction of 0021)

Claude could not push. Cursor rebuilt the five fail-closed fixes against current `main`.

| ID | Lie | Fix |
|---|---|---|
| T9 | Profit gate could PASS on bundled 9-trade fixture | Fixture removed from default sources; gate evaluator refuses fixture path/`is_fixture` |
| T11 | Success-sounding token copy + stale 403 while skipped | `sanitize_attempt_block` / `sanitize_status_payload` on status, cloud wrap, and SSOT store |
| T12 | `"6_prediction_analytics": "PASS"` while register is `NO_PREDICTION_FOUND` | Status computed from the accuracy report |
| T14 | `"7_live_trading_guardrails": "PASS"` even if flags flipped | Reads `config/live_trade_config.py`; PASS only when both flags are False |
| R2/R3 | `/api/batch/chains` stayed `CHAIN_CACHE_WARMING` even if Dhan could answer | `wrap_batch_chains_ondemand` in `dashboard/backend/routers/chain.py` (installed from the existing `install_legacy_bridge` startup hook). Incomplete payloads still never cached. |

Live trading was **not** enabled. Secrets were **not** touched.

## Proof

```
collected 43 items
tests/test_system3_patch_0021_fail_closed.py ...........................
tests/evals/test_eval_chain_warm_batch_readiness.py ..............
======================== 43 passed, 9 warnings in 1.51s ========================
```

Command:

```
python3 -m pytest tests/test_system3_patch_0021_fail_closed.py \
  tests/evals/test_eval_chain_warm_batch_readiness.py --disable-warnings
```

Compile: `py_compile` of all edited Python files succeeded.

## Still pending (not this patch)

1. Merge this PR into `main`, then redeploy only if you accept a **runtime** path change.
2. GitHub branch protection on `main` (human Settings action).
3. Watchdog standing FAILs and `/api/healthz` flap (alert then resolve ~48s).
4. Claude still cannot push (`not in this session's authorized repository set`).
5. Model accuracy remains unproven (`NO_PREDICTION_FOUND`). T12 now **reports FAIL** honestly; it does not invent predictions.
6. SYS3-BLK-001 false `BROKER_DISCONNECTED` alert loop is unchanged.

## Do not

- Apply patches 0019 or 0020.
- Enable live trading.
- Treat dashboard PASS badges as truth without runtime proof.
