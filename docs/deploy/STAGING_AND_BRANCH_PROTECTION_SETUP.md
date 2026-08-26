# Staging Environment + Branch Protection

Render.com staging is forbidden (retired host) and non-authoritative. Production deploy authority is GCP Cloud Run only. Canonical lock: `docs/authority/RENDER_HOSTING_FORBIDDEN.md`.

## 1. Staging / production runtime (GCP)

**Already done:**
- Production service: `genesis-system3-web` in project `system3-openalgo-safe`, region `asia-south1`.
- Auto deploy: `.github/workflows/cloud-run-auto-deploy.yml` on `push` to `main` (dashboard/core/deploy paths).
- Browser proofs read `DASHBOARD_URL`. Default production UI:
  `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`

**Needs a merge-capable/admin actor (not this Cloud Agent):**
1. Keep `main` as the only production deploy branch.
2. Do not recreate `render.yaml` or Render Blueprint services.
3. Point e2e at Cloud Run:
   `DASHBOARD_URL=https://genesis-system3-web-doq2wplepa-el.a.run.app/ui npx playwright test`

## 2. GitHub branch protection on `main`

**Needs repo admin** (Settings → Branches → rule for `main`):
- Require a pull request before merging.
- Require the blocking jobs from `.github/workflows/ci.yml` to pass.
- Require branches to be up to date before merging.

## 3. Retired

- Render dashboard, Render Blueprint, Render public hostnames, and `render.yaml` staging blocks are not current authority.
