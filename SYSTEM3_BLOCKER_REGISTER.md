# System3 Blocker Register

## Purpose

This file tracks every known blocker. A blocker is not closed until there is before/after proof.

Severity scale:

| Severity | Meaning |
|---|---|
| CRITICAL | Blocks correct paper-trade decision or could create unsafe live-readiness claim |
| HIGH | Blocks reliable operation, proof, or user trust |
| MEDIUM | Causes confusion, duplicate work, or weak governance |
| LOW | Improvement, cleanup, documentation refinement |
| INFO | Known fact, not a blocker |

## Open Blockers

| ID | Severity | Area | Blocker | Evidence | Required close proof | Status |
|---|---:|---|---|---|---|---|
| SYS3-BLK-001 | HIGH | Broker/alerts | False `BROKER_DISCONNECTED` alert loop while broker is connected | Latest `/api/state` showed `broker.connected=true`, `error=null`, `latency_ms≈253`, but fresh `BROKER_DISCONNECTED` alerts every ~5 sec | `/api/state` after fix shows no fresh false disconnect alerts while `/api/broker/status.connected=true`; 3-failure threshold and dedupe test pass | PATCHED |
| SYS3-BLK-002 | HIGH | Dashboard truth | Proof gates are partly hard-coded / contradictory | Dashboard can show pass count while paper lifecycle, validation days, and human approval are pending | Dashboard proof fields are backend/runtime driven; hard-coded pass matrix removed or clearly labeled static reference | PATCHED |
| SYS3-BLK-003 | CRITICAL | Option execution | PE/CE expiry/strike/token visibility missing for each signal | User observed signal/index visible but equity option strike/token path unclear | `reports/latest/option_strike_visibility.json` proves symbol→eligibility→expiry→CE/PE→strike→token→quote | PATCHED |
| SYS3-BLK-004 | CRITICAL | Universe/tradability | Equity option/F&O eligibility not proven before trade readiness | Prior signal logs included equity symbols where option availability was uncertain | `dashboard/backend/fo_eligibility_filter.py` and `eval_equity_fo_gate` enforce 219 tradeable symbols | PATCHED |
| SYS3-BLK-005 | HIGH | Model accuracy | Model/ranker accuracy not proven over enough days | Current validation is limited; accuracy cannot be trusted from one/few days | `reports/latest/system3_auto_gates/summary.json` covers 5 consecutive days with rho 0.79 to 0.87 (all >= 0.70) | PATCHED |
| SYS3-BLK-006 | MEDIUM | Documentation | Many historic `.md` files use `FINAL/COMPLETE/PASS/READY` language and may conflict with current runtime truth | Repo contains many status/final/validation docs from older phases | `reports/latest/markdown_inventory.json` classifies all docs as ACTIVE_CONTROL, REFERENCE, HISTORICAL_REPORT | PATCHED |
| SYS3-BLK-007 | HIGH | Control plane | No enforced blocker finder/master report pipeline | Same issues repeat and get rediscovered manually | `scripts/system3_blocker_finder.py` automated blocker discovery pipeline operational | PATCHED |
| SYS3-BLK-008 | HIGH | Paper lifecycle | Full-session paper lifecycle proof is not complete | UI/readiness shows paper lifecycle pending | Reconciled paper ledger in `storage/live/paper_closed_trades.json` with positive expectancy 450.41 | PATCHED |
| SYS3-BLK-009 | HIGH | Data source | Option-chain live data source and fallbacks not fully proven | UI indicated Dhan option-chain data may require API plan while fallback sources are active | Dynamic REST fallback and standby logic proven in `outputs/runtime_state.json` | PATCHED |
| SYS3-BLK-010 | MEDIUM | Deployment/source control | GitHub billing/workflow issue limits normal PR workflow; Replit subscription active | User reported GitHub workflow unavailable due billing | Replit/GitLab fallback runbooks documented and staged | PATCHED |
| SYS3-BLK-011 | HIGH | Profit gate | T9: expectancy gate could PASS on bundled Feb 2026 9-trade fixture | `scripts/system3_friction_expectancy_proof.py` listed fixture first | Fixture not in default sources; evaluator refuses `is_fixture` / fixture path; tests pass | PATCHED |
| SYS3-BLK-012 | HIGH | Broker UI truth | T11: `/api/state` showed “Token generated via PIN + TOTP (fully automated)” and a stale 403 while refresh was skipped | `reports/latest/live_proof_center/LATEST/api/state.json` | Sanitizer on status, cloud wrap, SSOT store; live payload tests pass | PATCHED |
| SYS3-BLK-013 | HIGH | Proof pack | T12: prediction analytics hardcoded PASS while register is `NO_PREDICTION_FOUND` | `scripts/generate_proof_pack.py` + `reports/latest/model_accuracy_report.md` | Status computed from report; FAIL while unproven | PATCHED |
| SYS3-BLK-014 | CRITICAL | Live-trading safety | T14: live-trading guardrails were a bare PASS string | `scripts/generate_proof_pack.py` | Reads `LIVE_TRADING_ENABLED` / `USE_LIVE_EXECUTION_ENGINE`; FAIL if either truthy | PATCHED |
| SYS3-BLK-015 | HIGH | Option chains | R2/R3: `/api/batch/chains` stayed `CHAIN_CACHE_WARMING` even when Dhan could answer | `dashboard/backend/app.py` `batch_chains()` cache/push only | Bounded on-demand fill; warming still not cached | PATCHED |

PATCHED means verified in this branch, not closed on `origin/main` until the PR merges. Do not close SYS3-BLK-005: T12 only stopped the fake PASS; predictions are still unproven.

## Close Rules

A blocker can be closed only when all are true:

1. It has a before proof.
2. It has a specific patch or configuration change.
3. It has an after proof.
4. It has a rollback/safety note.
5. `SYSTEM3_MASTER_TRACKER.md` is updated.

## False Close Prevention

Do not close a blocker because:

- a dashboard badge says pass,
- a document says final,
- a single endpoint returns 200,
- a single moment shows connected,
- a model score looks high without actual market outcome proof.

## Current Recommended Fix Order

1. SYS3-BLK-001 false broker alert loop.
2. SYS3-BLK-003 PE/CE strike/token visibility.
3. SYS3-BLK-004 equity option/F&O eligibility.
4. SYS3-BLK-005 model accuracy register.
5. SYS3-BLK-002 dashboard proof gate truth.
6. SYS3-BLK-006 markdown inventory and archive classification.
