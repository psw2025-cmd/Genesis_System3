# RETIRED — Render memory/OOM runbook

Render.com hosting is retired and non-authoritative.

Production runtime is GCP Cloud Run:

- project `system3-openalgo-safe`
- region `asia-south1`
- service `genesis-system3-web`
- UI `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`

Do not recreate `render.yaml`. Memory/OOM work belongs on the Cloud Run service and worker Jobs.
