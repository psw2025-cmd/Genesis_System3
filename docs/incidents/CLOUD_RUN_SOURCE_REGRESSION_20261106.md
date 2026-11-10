# Genesis System3 Cloud Run source regression — 2026-11-06

## Scope and safety
Project `system3-openalgo-safe`, region `asia-south1`. Read-only forensic review
plus owner-authorized staging deployment. Production service, traffic, Dhan
Secret Manager values, Scheduler jobs and token writers were not changed.
All staged runtime controls are PAPER-only and LIVE/order-disabled.

## Verified root cause
- Production service: `genesis-system3-web`, serving revision
  `genesis-system3-web-00090-qj4`, image digest
  `sha256:2239d78b7025bae24506bdbb883216a6e05b3b96e92824c975aa5229d5d67d05`.
- Image produced by Cloud Build `4b5b6763-f382-498e-95f7-53a5865ab6a8`
  on 2026-11-01 19:21 UTC.
- Build source: `gs://run-sources-system3-openalgo-safe-asia-south1/services/genesis-system3-web/1793560883.062913-3bb2d9f43e764c3fa77066590dc6cdc0.zip`.
  The verified GCS object size is 20,649 bytes. It contains 15 archive
  entries, three Python files and **no** `dashboard/backend/app.py`.
- The real GitHub `main` at `7fdd44fae1582d5ddb656afbb45ba025f93514ad`
  contains a 500,396-byte `dashboard/backend/app.py`, the canonical
  `dashboard/backend/Dockerfile`, `scripts/start_cloud_run.py` and the
  API routes that the uploaded mini-app lacks.
- Production GET probes returned `/api/health` 404,
  `/api/broker/status` 404, `/api/batch/market-data` 404,
  while `/ui` returned 200. HTTP 200 on UI alone was misleading.
- The canonical repository `cloudbuild.yaml` already targets
  `dashboard/backend/Dockerfile` but lacked an explicit integrity gate
  to reject partial source packages.

## Recovered candidate and staging proof
- Candidate previous full revision: `genesis-system3-web-00047-wzn`
  (created 2026-10-29 11:02 UTC), image
  `sha256:6809f21292e134b1f576c4ffebe951941f5d9ab52243b2d1ef7ae6b2b3faf624`.
- Candidate image is linked by digest to Cloud Build
  `a1369f3f-287c-43a7-a0d4-dea0e02bc86d`, successful on
  2026-10-29 10:58 UTC; source was a Cloud Build GCS `.tgz` archive.
  The exact Git commit of that source is **not independently certified**.
- Staging service `genesis-system3-web-staging` was repaired with the
  pinned candidate image as revision `genesis-system3-web-staging-00003-7cl`.
  The staging service requires authentication (no public invoker grant).
- Staging read probes returned HTTP 200 for `/ui`, `/api/health`,
  `/api/healthz`, `/api/broker/status`,
  `/api/batch/market-data`, `/api/chain/NIFTY`.
  `/api/options/gainers` returned 404. `/openapi.json` timed out
  in the short initial probe; full route enumeration is not certified.
- Staging has `PAPER_MODE=1`, `LIVE_TRADING_ENABLED=0`,
  `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`,
  `LIVE_ORDER_AUTHORITY=0`, `REAL_BROKER_ORDERS=0`,
  `ORDER_PLACEMENT_ALLOWED=false`, and Dhan token remint/refresh paths
  disabled. No broker credentials were injected into staging.

## Fix implemented in this PR
1. `scripts/cloud_run_source_integrity_gate.py`: deterministic, stdlib-only
   build-context and API-route validation, producing only source hashes.
2. `tests/test_cloud_run_source_integrity_gate.py`: positive and negative
   tests that reject miniature or incomplete builds.
3. `cloudbuild.yaml`: fail-closed source-integrity preflight before Docker.
4. This incident record.

The guard protects canonical `cloudbuild.yaml` builds. It **cannot stop**
an Owner from manually bypassing Cloud Build and deploying an unrelated
source-based service. Production permissions/process governance must enforce
digest-based promotions with proof of source identity.

## Remaining blockers — no production promotion
- Canonical current `main` image has not been rebuilt and staged in this
  evidence set; its full functional correctness is not proven.
- Candidate staging has no broker-secret injection; successful route
  responses do not establish authentic Dhan holdings, live chain freshness,
  paper lifecycle, CE/PE gainers or predictive accuracy.
- Four scheduled Genesis jobs target nonexistent Cloud Run jobs; their
  replacement/fix requires a separate correctness review.
- Canonical Dhan rotation Job returned
  `BLOCKED_CANDIDATE_SECRET_NOT_READY` on recent attempts, whereas
  direct read-only Dhan profile authentication succeeded with the canonical
  existing secret. Token writers must not be deleted or reminted blindly.
- No live broker orders were placed or enabled; proof of paper trading
  lifecycle remains a separate gate.

## Production promotion gate
**NO-GO** until ALL of the following are verified with timestamps:
- [ ] Exact Git SHA -> Cloud Build ID -> source hash -> pushed image digest.
- [ ] Canonical source gate and all required CI tests PASS on exact SHA.
- [ ] Staging health, broker, market-data, option-chain and UI route tests.
- [ ] At least one real Dhan read-only profile plus freshness/lineage proof.
- [ ] Order authority remains OFF and zero real broker orders proven.
- [ ] Scheduler/token writer safety and permission checks approved.
- [ ] Correct image is promoted by **digest**, not a mutable tag.

## Rollback plan (for a future separately approved production promotion)
1. Capture the prechange service configuration, original serving revision,
   digest, IAM bindings and traffic split, and current safety flags.
2. Promote the already-staging-tested immutable digest without changing
   Dhan token writers or Scheduler.
3. Test readiness, canonical routes, safety and data truth immediately.
4. If any gate fails, restore the captured prechange image and traffic
   allocation; note that returning to image `2239d78b...` also
   returns to the *known incomplete application*, so prefer a verified
   route-complete candidate once independently approved.
5. Log revision, UTC+IST timestamps, result, and rollback receipt.
