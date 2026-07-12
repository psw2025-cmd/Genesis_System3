# System3 Visual Proof and Render Blocker Rules

Owner/operator: **PRITAM S. WARGHADE**

## Non-negotiable rule

No feature, fix, model, paper-trade path, broker path, data path, or dashboard change may be called resolved unless fresh dashboard visual proof exists after that change.

## Always-required verification for every step

Every step/change must include all three proof classes before any resolved claim:

1. **Render verification**
   - Render backend must answer required APIs.
   - Deploy info must match the expected commit or be marked BLOCKED.
   - Render stale frontend, cold start, rate limit, auth, memory, or worker proof problems are blockers.

2. **Dashboard visual proof**
   - Fresh screenshot set must exist after the change.
   - Screenshot file size alone is not enough.
   - Screenshots must visibly contain required text.
   - Owner/operator must be visible: `PRITAM S. WARGHADE`.
   - Production Proof Bar must be visible.

3. **Integration verification**
   - API smoke must pass or list exact blockers.
   - UI tab smoke must pass or list exact blockers.
   - Model, paper, broker, and data paths must show source/provenance.
   - Any failing integration gate blocks production-grade claim.

## Visual proof required for all changes

Every critical change must produce fresh screenshots under:

```text
reports/latest/dashboard_visual_production_proof/screenshots/
```

Required screenshots:

```text
truth.png
signals.png
paper.png
broker.png
ml.png
gates.png
overview.png
mobile_390x844.png
```

## Dashboard identity requirement

The dashboard top bar or global proof bar must visibly show:

```text
OWNER / OPERATOR
PRITAM S. WARGHADE
```

This owner badge must be checked by visual proof before it is called proven.

## Production proof bar requirement

Dashboard must visibly show these seven gates:

```text
OWNER      PRITAM S. WARGHADE
LIVE       OFF
MODE       PAPER ONLY
DATA       DHAN ONLY REQUIRED
ML SCORE   TRAINING PROOF REQUIRED or proven score
PAPER      PROVENANCE REQUIRED or proven source
RENDER     VISUAL PROOF REQUIRED or latest proof status
```

Unproven gates must stay visible as REQUIRED/BLOCKED, not hidden or falsely passed.

## Render-related issue rule

Render issues must never be ignored or treated as cosmetic. These are production blockers until visually and API-proven resolved:

- Render deploy commit mismatch
- Render backend unavailable
- Render cold-start timeout
- Render rate-limit / throttle
- Render API auth failure
- Render worker-to-backend authorization failure
- Render memory pressure / OOM risk
- Render frontend stale bundle
- Render dashboard screenshot missing or stale
- Render UI tabs loading but not ready
- Render Dhan credentials missing or expired
- Render Dhan chain endpoint blocked
- Render scheduler/worker not writing latest proof

## Visual proof blocker solution map

| Blocker | Required solution |
|---|---|
| OWNER_BADGE_NOT_VISIBLE | Fix owner/global proof bar and regenerate screenshots. |
| PRODUCTION_PROOF_BAR_NOT_VISIBLE | Fix fixed production proof bar and regenerate screenshots. |
| SAFETY_LABELS_NOT_VISIBLE | Show PAPER and LIVE OFF in screenshots. |
| ML_PROOF_TEXT_NOT_VISIBLE | ML tab must show proof records, training status, accuracy/AUC/model score or BLOCKED reason. |
| PAPER_TRUTH_NOT_VISIBLE | Paper tab must show paper provenance, rejected fake/fixture rows, source file, and order endpoints NOT CALLED. |
| SCREENSHOT_MISSING_OR_EMPTY | Fix Playwright capture, route loading, tab selector, auth, or Render timeout. |
| API_FAIL | Fix endpoint/auth/deploy/rate-limit before visual proof can pass. |
| CHAIN_NOT_TRADE_READY | Fix Dhan option-chain, expiry, security-id, credential, or scheduler data path. |
| UI_FAIL | Fix UI rendering/loading/exceptions before claim. |
| RENDER_WORKER_PUSH_FAIL | Align backend and worker proof settings; do not expose private values. |
| RENDER_DEPLOY_COMMIT_MISMATCH | Redeploy correct commit and verify deploy info. |
| RENDER_STALE_FRONTEND | Force frontend rebuild/redeploy and verify screenshot changed. |
| INTEGRATION_GATE_FAIL | Fix API/UI/model/paper/broker integration path and publish proof. |

## Proof hierarchy

1. Code commit is not enough.
2. API 200 is not enough.
3. Screenshot file size is not enough.
4. Screenshot must visibly contain required text.
5. Dashboard visual proof summary must list blockers and required solutions.
6. Render verification must be checked for every step.
7. Integration verification must be checked for every step.
8. Final public truth cannot pass if visual proof is missing, stale, or incomplete.

## Live trading safety

Live trading remains OFF. Any live order route, order placement, modify, cancel, or broker execution function must remain untouched unless explicitly proven analyzer-only. If touched without proof, status is BLOCKED.
