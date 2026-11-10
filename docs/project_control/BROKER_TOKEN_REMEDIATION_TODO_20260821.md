# Broker Token Permanent Remediation — Living TODO

Status timestamp: 2026-08-21T06:35Z  
Authority: `psw2025-cmd/Genesis_System3` current `origin/main`  
Safety: ANALYZE/PAPER only; no order API; no secret payload in evidence.

## Current verdict

`FAIL_CLOSED`. Production serves SHA `4f89321ead6bc8db252acd1df0cb4016a88baf43`, but Dhan Profile rejects Secret Manager version 281 with `DH-906 / Invalid Token`. Health is `NOT_READY`; four canonical option chains are empty; quote traffic has returned HTTP 429 / Dhan 805.

Version 281 was created by the scheduled canonical job at 02:00:16Z and the newly generated token passed Profile validation before persistence. It later became invalid. This proves invalidation-after-validation; it does not yet prove which external/manual actor generated or renewed another token.

## P0 — token authority and recovery

- [x] Prove exactly one repository mint primitive: `scripts/gcp_dhan_token_rotation_job.py`.
- [x] Prove GitHub Actions stores no Dhan payload secret.
- [x] Prove Secret Manager canonical access-token name is `dhan-access-token`.
- [x] Prove current job uses PIN/TOTP secrets through `latest` and LIVE/order flags are off.
- [x] Correlate v280/v281 with canonical job executions.
- [x] Attribute version 279 operationally: operator confirmed it was the manual Dhan recovery token. GCP Data Access principal remains unavailable, so this is user-confirmed context rather than an audit-principal proof.
- [x] Attempt one bounded canonical recovery execution (`gn7bm`); it failed closed, created no version.
- [ ] Deploy safe failure-stage telemetry and rerun once to distinguish generate, validate, persist, or advance failure.
- [x] Identify destructive state-loss gap: Dhan mint may invalidate the predecessor before replacement validation; old code discarded a generated replacement when validation/persistence failed.
- [x] Implement quarantine flow: persist minted replacement to non-consumer `dhan-access-token-candidate`, retry Profile validation, and promote to canonical only after PASS.
- [x] Provision empty candidate secret with only rotator `secretVersionAdder`; web/runtime/deployer receive no candidate payload access.
- [x] Add 30-minute fresh-invalid re-mint lock and change normal expiry threshold from six hours to two hours.
- [ ] Recover Profile to `AUTH_OK` and prove runtime loaded the new concrete version.
- [ ] Observe 180 seconds with zero new auth rejection and zero unexpected version creation.
- [ ] Disable superseded enabled versions only after latest-only consumer proof and rollback decision.

## P0 — classifier correction

- [x] Establish official taxonomy: DH-901 is auth; DH-906 is normally request/order error.
- [x] Establish observed Profile anomaly: Dhan returns `DH-906` plus explicit `Invalid Token` for an invalid token.
- [x] Implement hybrid rule: bare 906 remains non-auth; Profile 906 plus explicit auth marker is auth.
- [x] Remove 906 header-contract fallback amplification.
- [ ] Pass all focused classifier/read-only/runtime tests.
- [ ] Verify current-main GCP Dhan Token Fix CI exact head.

## P0 — recovery interval

- [x] Identify daily-only blind window: an out-of-band invalidation after 07:30 IST can remain broken nearly 24 hours.
- [x] Change scheduler contract to hourly at minute 30 IST. Healthy tokens remain no-op; mint remains authorized only by affirmative auth rejection or <=6h expiry.
- [ ] Deploy scheduler change and verify next two deliveries and job outcomes.
- [ ] Confirm no overlapping executions and no duplicate version creation.

## P0 — Dhan 805/429

- [x] Confirm official Quote API limit: one request per second account-wide.
- [x] Map direct quote callers: index board, equity holdings enrichment, position enrichment.
- [x] Map option-chain fan-out and process-global 3.4-second lock.
- [x] Confirm current quote single-flight/cache/cooldown scope is process-local.
- [x] Confirm Cloud Run permits multiple instances; process-local coordination cannot enforce an account-wide limit.
- [x] Cap serving max instances at one until a distributed broker-data governor is implemented and tested.
- [ ] Add caller/source counters and request timestamps without credentials.
- [ ] Prove no 805/429 during the 180-second observation.
- [ ] Build a Firestore/Redis/global broker-data lease before restoring horizontal scale above one.

## P0 — semantic recovery

- [ ] Broker endpoint connected and auth classification `AUTH_OK`.
- [ ] Health/QC ready.
- [ ] NIFTY fresh Dhan CE and PE rows.
- [ ] BANKNIFTY fresh Dhan CE and PE rows.
- [ ] FINNIFTY fresh Dhan CE and PE rows.
- [ ] MIDCPNIFTY fresh Dhan CE and PE rows.
- [ ] Index ribbon has live values without fallback contradiction.
- [ ] Fresh browser/API session after deployment; all relevant timestamps recorded.
- [ ] Full 22-tab semantic proof only after broker/data gates pass.

## P1 — laptop and GitHub hygiene

- [x] Local filenames-only scan; contents not read.
- [ ] Operator-approved quarantine/removal of `.env`, `iam_temp.json`, `NEW_DHAN_TOKEN.txt`, and `gcp_access_token.txt` artifacts where redundant. Never commit them.
- [ ] Resolve dirty main laptop worktree or keep remediation isolated.
- [ ] Add MRI workflow/scheduled evidence artifact without Dhan payload permissions.
- [ ] Detect any future source mint primitive outside the canonical job.
- [ ] Detect any future GitHub Dhan token payload secret name.

## P1 — Secret Manager hygiene

- [ ] Define retention: one enabled active version plus a bounded disabled rollback version.
- [ ] Add post-rotation latest-consumer proof before disabling previous version.
- [ ] Alert on version creation without a matching canonical execution window.
- [ ] Alert on more than one new version inside the recovery cooldown.
- [ ] Keep `secretVersionAdder` exclusive to the rotator identity.

## Affected files in this remediation

- `core/brokers/dhan/cloud_status_probe.py` — observed Profile auth classifier and no-amplification fallback.
- `core/brokers/dhan/dhan_readonly.py` — matching safe payload/HTTP taxonomy.
- `scripts/gcp_dhan_token_rotation_job.py` — safe failure-stage telemetry.
- `.github/workflows/cloud-run-auto-deploy.yml` — hourly scheduler contract.
- `dashboard/backend/scheduler_contract.py` — runtime scheduler expectation.
- `scripts/gcp_runtime_identity_safety.py` — live audit expectation.
- `scripts/gcp_cloud_run_auto_deploy_impl.py` — one-instance account-rate-limit containment and schedule label.
- Focused tests under `tests/` and `tests/evals/`.

## Acceptance law

Do not declare resolved from token creation, CI green, HTTP 200, or rendered tabs alone. Resolution requires exact-head CI, deployed exact SHA, one canonical token authority, successful rotation/no-op behavior, 180-second clean observation, connected Profile, no 805/429, ready health, four populated Dhan chains, and new browser/API semantic evidence.
## 2026-08-21 enabled-version read-only validation

All enabled Secret Manager versions were tested independently against the Dhan read-only profile endpoint. Token values were never printed, persisted, or committed; no order endpoint was called and the production alias was not changed.

| Secret version | JWT clock state | Dhan response | Result |
|---|---|---|---|
| `279` | Expired at `2026-08-20T14:13:51Z` | HTTP `401`, `DH-901`, `Invalid_Authentication` | FAIL — expired/invalid |
| `280` | Not clock-expired; expiry `2026-08-21T16:36:20Z` | HTTP `400`, `DH-906`, `Order_Error`, `Invalid Token` | FAIL — broker-invalid before JWT expiry |
| `281` | Not clock-expired; expiry `2026-08-22T02:00:13Z` | HTTP `400`, `DH-906`, `Order_Error`, `Invalid Token` | FAIL — broker-invalid before JWT expiry |

Inference: no enabled historical version can restore broker connectivity. Versions 280 and 281 demonstrate broker-side invalidation before their embedded JWT expiry; this is consistent with a later token issuance invalidating earlier tokens, but the actor/source that issued it is not yet proven. A newly issued Dhan token is required for immediate recovery, while permanent remediation must retain single-writer rotation, post-write profile validation, failure-stage telemetry, and rollback/fail-closed behavior.
