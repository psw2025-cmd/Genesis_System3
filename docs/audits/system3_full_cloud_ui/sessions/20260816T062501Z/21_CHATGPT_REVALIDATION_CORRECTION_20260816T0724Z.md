# 21 — ChatGPT Independent Revalidation Correction

**Revalidation time:** 2026-08-16T07:24Z  
**Audit package:** `20260816T062501Z` / PR #242  
**Current GitHub main observed:** `41f7a80cf0c31711f4c26d46fdc0e3f26fc6a311`  
**Historical serving SHA recorded by the audit:** `a48e7b3c7c086a21352f718355d1c12d4a48955b`

This file is an evidence-only temporal correction. It does not mutate runtime, GCP, IAM, broker credentials, token state, or trading behavior.

## Correction C-001 — F-001 `serving != main` is not, by itself, deployment drift

**Status:** `DISPROVEN_AS_DEFECT_ON_CURRENT_SOURCE_EVIDENCE`

The current deploy-trigger contract is implemented by `scripts/system3_resolve_runtime_deploy_sha.py`. It explicitly states that proof/security/docs-only commits may advance repository `main` without requiring Cloud Run to advance. The expected serving identity is the newest first-parent commit that changed one of the exact Cloud Run deploy-trigger paths.

Independent GitHub comparison of historical serving SHA `a48e7b3c...` through current main `41f7a80c...` shows 14 commits and only these changed paths:

- `.github/workflows/frontend-runtime-smoke.yml`
- `docs/SYSTEM3_VISUAL_PROOF_AND_RENDER_RULES.md`
- `docs/authority/TEMPORAL_TRUTH_AND_LIVE_EVIDENCE_POLICY.md`
- `scripts/gcp_live_ui_snapshot.py`
- `scripts/security_audit_summary.py`
- `scripts/system3_resolve_runtime_deploy_sha.py`
- `tests/test_live_ui_truth_remediation_contract.py`
- `tests/test_security_audit_static_shell_review.py`
- `tests/test_temporal_truth_contract.py`

None matches the resolver's current `DEPLOY_TRIGGER_PATTERNS`. Therefore, on current repository evidence, `a48e7b3c...` remains the expected runtime-affecting SHA despite `main` being newer. A fresh GCP serving-revision observation is still required before making a claim about what is serving *now*, but the mere SHA inequality must not remain a P0 defect.

**Backlog correction:** replace F-001 `serving drift` with a temporal/provenance check: `actual serving SHA == resolved expected runtime-affecting SHA`. Only a mismatch against the resolver result is a deployment defect.

## Correction C-002 — F-016 / M-001 historical destroyed TOTP version is not a current user break-glass requirement

**Status:** `HISTORICAL_RISK_NOT_CURRENTLY_PROVEN`

The audit amendment records execution `genesis-system3-dhan-token-rotate-25szr` resolving `dhan-totp-secret/versions/latest` to historical version 8 in `DESTROYED` state. That is valid historical evidence for that execution only. It is insufficient to claim that the *current* `versions/latest` resolution is unusable or that user/TOTP action is currently required.

Do **not** request TOTP, secret payload, or Secret Manager user action from this historical execution. Before escalation, obtain a new read-only GCP observation of:

1. current `dhan-totp-secret` version metadata and current `latest` resolution without reading payload;
2. latest Dhan rotator execution identity/status;
3. execution-scoped logs/failure class if the current execution failed;
4. current broker status as a separate signal.

Only a new bounded rotation failure specifically attributable to current TOTP-secret resolution, or fresh metadata proving current `latest` is unusable, may create `BLOCKED_USER_ACTION`.

## Correction C-003 — audit-time broker/UI observations remain historical

The audit's `broker connected=true`, NIFTY contract count, WAITING tabs, option-chain timeout observations, Cloud Run 429 counts, and serving-revision metadata were captured around 2026-08-16T06:25Z–06:45Z. They are useful historical baselines, not current truth after this correction time. Any remediation decision that depends on present broker/UI/GCP state requires a new request/run-scoped production observation.

## Current safe dependency order after correction

1. Revalidate current GCP serving SHA against the runtime resolver result; do not deploy merely because repo main is newer.
2. Revalidate IAM-vs-baseline, current scheduler/rotator metadata, current TOTP-secret metadata (no payload), and current UI/API truth.
3. Confirm whether request amplification / option-chain coalescing defects still reproduce before functional mutation.
4. Continue Issue #188 universe-count/provenance instrumentation only from current-main-based branches and exact-head gates.
5. Keep all market-hours-only claims open until a fresh market-hours proof window.

## Safety

- `ANALYZE_MODE=1`
- `LIVE_TRADING_ENABLED=0`
- `SYSTEM3_LIVE_TRADING_ALLOWED=0`
- `AUTO_EXECUTE_TRADES=0`
- no live order placement/modification/cancel/square-off
- no secret payload reads/prints
- no blind token rotation
- no deployment performed by this correction

**Canonical-use rule:** PR #242 may be used as a historical forensic baseline only when this correction is read together with files `16_`, `17_`, `18_`, and `20_`. F-001 must not be carried forward as a deployment defect solely from `serving != main`, and F-016/M-001 must not be carried forward as a current user-action requirement without fresh GCP evidence.
