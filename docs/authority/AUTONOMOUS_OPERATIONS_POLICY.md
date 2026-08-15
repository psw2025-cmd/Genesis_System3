# Genesis System3 Autonomous Operations Policy

## Authority

- Google Cloud project `system3-openalgo-safe` is the authoritative production/runtime platform.
- GitHub repository `psw2025-cmd/Genesis_System3` is the authoritative code/configuration source.
- Render is retired/non-authoritative for production.
- GitHub Actions authenticates to Google Cloud only through keyless Workload Identity Federation (WIF). User-managed Google service-account JSON keys are forbidden.

## Operating objective

Routine production engineering must not depend on the user running technical commands. The control plane should investigate, patch, test, deploy, roll back, repair declared IAM drift, collect logs/evidence, and verify runtime/UI truth through GitHub Actions and Google Cloud.

## Safety boundary

The autonomous control plane MUST NOT:

1. enable LIVE trading;
2. set `AUTO_EXECUTE_TRADES=1`;
3. place, modify, cancel, or square-off real orders;
4. print/read broker secret payloads except inside the dedicated runtime identity that already requires them;
5. create or export service-account private keys;
6. delete the Google Cloud project or change billing ownership;
7. remove unknown IAM principals automatically without forensic classification.

Analyzer/PAPER remains the default. `LIVE_TRADING_ENABLED=0`, `SYSTEM3_LIVE_TRADING_ALLOWED=0`, `AUTO_EXECUTE_TRADES=0`, and `ANALYZE_MODE=1` are mandatory production deployment locks until a separate explicit human live-enablement process exists.

## Identity separation

- `genesis-system3-automation`: normal deployment/configuration identity. No broker secret payload role.
- `gs3-iam-repair`: guarded IAM-reconciliation identity. It may only restore the repository-declared System3 IAM baseline and known Dhan job invoker restrictions. It must never execute the Dhan rotation job.
- `genesis-system3-dhan-rotator`: only identity that reads PIN/TOTP/client-id/access-token material and adds a new canonical access-token version.
- `gs3-scheduler`: normal 07:30 Asia/Kolkata Dhan rotation invoker.
- `gs3-token-recovery`: bounded manual/recovery invoker.
- `genesis-system3-web`: runtime web identity; may read canonical client-id/access-token and worker token, but must not mint Dhan tokens.

## IAM drift behavior

`deploy/gcp/system3_iam_baseline.json` is the machine-readable minimum authority baseline.

When Cloud Run Auto Deploy fails due to missing declared IAM:

1. `GCP Authority Repair` runs from trusted `main`.
2. It authenticates as `gs3-iam-repair` through a WIF claim restricted to the exact repair workflow.
3. It compares live IAM with the declared baseline.
4. It adds only missing allowlisted bindings and removes only explicitly listed forbidden Dhan job invokers.
5. It never reads Secret Manager payloads and never invokes the rotator.
6. It triggers one Cloud Run Auto Deploy retry only when IAM drift was actually repaired.
7. If no declared IAM drift exists, it stops; no retry loop is permitted.

## Broker rotation authority

- Daily scheduler at 07:30 Asia/Kolkata remains the normal mint authority.
- Web self-heal minting remains OFF (`DHAN_CANONICAL_ROTATION_SELF_HEAL=0`).
- Deploy workflows configure the rotator/scheduler but must not execute the rotator.
- Recovery must remain single-flight/cooldown guarded; repeated mint retries are forbidden.

## Evidence rule

No production-ready claim is allowed from source code alone. Final proof must include exact deployed SHA/revision, runtime safety flags, broker status, health status, and visible UI data where the feature is UI-facing.

## Human-only break-glass boundary

Human intervention can still be required for external account/billing suspension, organization-level policy outside this project, revoked GitHub/GCP account ownership, external broker identity/MFA reset, or intentionally destructive actions. These are not normal System3 operational tasks.
