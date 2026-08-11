# Dhan Token Rotation Runbook

## Authority

The only production token mint authority is `scripts/gcp_dhan_token_rotation_job.py` running as a Cloud Run Job. Legacy token writers remain retired.

## Safety invariants

- LIVE trading OFF; ANALYZE/PAPER only.
- Never call place/modify/cancel order endpoints as token verification.
- Never print or persist raw token, PIN or TOTP values in evidence.
- Never grant `roles/secretmanager.admin`; use secret-level least privilege.
- A new token is accepted only after read-only Dhan profile validation and Secret Manager version advancement.

## Automatic path

1. Read mounted/current token and validate with Dhan profile.
2. If healthy and outside rotation threshold, exit `SKIPPED_TOKEN_HEALTHY`.
3. If invalid/near expiry, generate a new token using the canonical PIN+TOTP flow.
4. Validate the generated token with Dhan profile before persistence.
5. Add exactly one new version to `dhan-access-token`.
6. Re-read latest-version metadata and prove the version advanced.
7. Emit secret-safe structured audit metadata with trace ID, version ID, status, timestamps, and `order_endpoints_called=false`.
8. Verify `/api/broker/status` shows dynamic Secret Manager source, connected read-only broker proof, LIVE false and order placement false.

## Retry/circuit breaker

- Single-flight only.
- Existing runtime self-heal cooldown remains authoritative.
- No more than two automated rotation attempts for the same failure condition inside 15 minutes.
- Never delete a failed new secret version automatically; preserve it for metadata forensics while the serving runtime continues using the last proven token path.
- Escalate after two failed attempts or when human Dhan authentication/PIN/TOTP intervention is genuinely required.

## Closure proof

- canonical Cloud Run Job execution SUCCESS;
- read-only Dhan profile SUCCESS;
- secret version advanced when rotation was required;
- raw token exposed = false;
- order endpoints called = false;
- broker runtime proof connected/read-only;
- LIVE OFF/LOCKED.
