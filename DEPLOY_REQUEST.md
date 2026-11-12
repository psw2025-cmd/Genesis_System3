# Deployment request - NOT AUTHORIZED / NOT EXECUTED

Scope: market-status safety patch on fix/owner-nse-dhan-truth-20261112, based on main c6f63aec9b2e45c2871ffeed56dd7f4a58e722db. Exact candidate SHA will be recorded after commit. Code source hash: 60895ad1e6b7a99613e2783d61c4a6b9ed4c7db39b3e3086542229cca08c2248.

Change: absent market-source evidence is UNKNOWN rather than CLOSED. Preserve actual source last_ok instead of manufacturing a current verification time. This patch does not implement or certify an entire NSE/Dhan ingestion pipeline.
Validation: 15 targeted offline regression tests exit 0; syntax checks; diff check. Full hosted CI, integration/API consumers of nullable is_open and production UI parity remain required. Do not weaken them to deploy.

Target: GCP project system3-openalgo-safe, region asia-south1, Cloud Run service genesis-system3-web. Owner must separately approve billable build/image push/deploy or a main merge that triggers the existing deployment workflow. No IAM, billing, secret rotation or real orders requested by this document.

Current observed traffic revision: genesis-system3-web-00131-2md; image digest sha256:acbd3d376a89afd236cba747f3af60cb3cb84c5bae134b41520fcd190bc24bc5. This is a previous serving revision, NOT a certified known-good product. Never label it known good without evidence.

Risk: is_open is nullable when source evidence is absent; clients must show unknown. Existing feed/UI/data-quality issues may persist after this scoped patch. Build/deployment incurs cloud charges.

Rollback if an approved deployment regresses: restore prior observed traffic using:
`gcloud run services update-traffic genesis-system3-web --project system3-openalgo-safe --region asia-south1 --to-revisions genesis-system3-web-00131-2md=100`
This command is a proposed cloud mutation, not executed. Expected operational duration is not measured; target under five minutes, verify readiness and UI afterward. Rollback restores prior traffic, not proven product readiness.

Post-deploy: capture serving SHA/digest, enforce PAPER locks, inspect fresh NSE and Dhan, reconcile UI/API on desktop/mobile, repeat after 10 minutes. If unable to establish known-good rollback or exact-head validation, keep request pending and do not deploy.
