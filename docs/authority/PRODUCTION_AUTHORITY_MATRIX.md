# Genesis System3 Production Authority Matrix

| Capability | Authoritative identity/path | Autonomous | Explicitly prohibited |
|---|---|---:|---|
| Source code/config | `psw2025-cmd/Genesis_System3` `main` | Yes | Other repositories as production authority |
| Production runtime | GCP `system3-openalgo-safe` / `asia-south1` | Yes | Render production authority |
| Cloud Run service deploy/traffic | `genesis-system3-automation` via GitHub WIF | Yes | JSON service-account keys |
| Cloud Build / image deployment | `genesis-system3-automation` | Yes | Broker-secret access by deployer |
| IAM drift repair | primary `gs3-iam-repair`, fallback `gs3-iam-repair-b`, exact repair-workflow WIF claim | Yes, declared baseline only | Arbitrary destructive IAM cleanup; Dhan job execution; secret payload access |
| Runtime logs/monitoring | evidence/deploy identities as configured | Yes | Secret payload logging |
| Dhan daily token mint | `gs3-scheduler` -> `genesis-system3-dhan-token-rotate` | Yes | Web/deploy-time mint |
| Dhan guarded recovery | `gs3-token-recovery` -> rotator | Yes, bounded/single-flight | Retry storms |
| Dhan token secret write | `genesis-system3-dhan-rotator` | Yes | Any web/deployer/repair writer |
| Web Dhan token read | `genesis-system3-web` dynamic Secret Manager source | Yes | Mounted static access-token env secret |
| UI/API runtime proof | Cloud Run + browser/API proof workflows | Yes | Readiness claim from source only |
| LIVE trading enablement | none | No | Autonomous LIVE enablement/order execution |
| Project deletion/billing ownership | human owner break-glass | No | Autonomous destructive project/account changes |

## Normal failure sequence

`detect -> classify -> safe repair -> tests -> zero-traffic candidate -> readiness -> promote -> API/UI proof -> evidence`

## IAM failure sequence

`deploy permission failure -> primary repair -> fallback only if primary fails -> compare baseline -> add only missing declared authority -> one deploy retry -> verify exact SHA`

A repair run with zero IAM changes must not trigger a deploy retry. This prevents repair/deploy loops for non-IAM failures.

## Bootstrap sequence

`deploy/gcp/bootstrap_all.sh` is the authoritative one-time owner/admin entrypoint. It runs the existing WIF/runtime bootstrap first, then installs the redundant repair identities and exact-workflow repair claim.
