# Staging Environment + Branch Protection — Setup Needed From You

Everything in this doc requires account-owner access (Render dashboard, GitHub repo
settings) that isn't available from this environment. The code-side pieces that
*can* be prepared without that access are already done — listed under each
section so you know what's left versus what's already in place.

## 1. Staging environment (Render)

**Already done:**
- `render.yaml` has a commented-out `genesis-system3-backend-staging` service
  block, configured identically to production except for a separate service
  name and a `staging` branch trigger.
- `tests/dashboard_browser_proof.spec.ts` and
  `tools/playwright-setup/verify_all_ui_tabs.spec.ts` already read their
  target URL from `DASHBOARD_URL` — no code change needed once staging exists.

**Needs you:**
1. Create a `staging` branch in GitHub (`git checkout -b staging && git push -u origin staging`).
2. In the Render dashboard, either:
   - Uncomment the staging block in `render.yaml` and push to `staging` — Render
     will pick it up as a new Blueprint service on next sync, **or**
   - Manually create a new Web Service in Render's UI pointing at the
     `staging` branch with the same Dockerfile.
3. Set staging-specific env vars in Render's dashboard for that service —
   **use test/sandbox Dhan credentials, not production ones.** Re-using
   production `DHAN_ACCESS_TOKEN` etc. on staging risks rate-limit
   contention or accidental cross-environment state confusion.
4. Once the staging URL exists, point CI/manual e2e runs at it:
   `DASHBOARD_URL=https://genesis-system3-backend-staging.onrender.com/ui npx playwright test`

## 2. GitHub branch protection on `main`

**Needs you** (Settings → Branches → Branch protection rules → add rule for `main`):
- Require a pull request before merging (disables direct pushes to `main`).
- Require status checks to pass before merging — once GitHub Actions billing
  is fixed (separate issue, see below) and CI is green, select the
  `workflow-policy-guard`, `full-proof-pack-validation`, and `frontend-build`
  jobs from `.github/workflows/ci.yml` as required checks.
- Require branches to be up to date before merging.
- Consider requiring at least 1 approving review if more than one person
  works on this repo.

**Why this matters right now specifically:** this session, at least two
processes were committing directly to `main` concurrently with no review
step at all — that's exactly the scenario branch protection exists to
prevent. Worth turning on regardless of CI status.

## 3. Prerequisite: GitHub Actions billing

Branch protection's "require status checks" is only useful if checks can
actually run. Right now **no GitHub Actions job has executed all session** —
confirmed via `gh run view`, zero logs exist for any recent run. The
annotation on every run is:

> The job was not started because recent account payments have failed or
> your spending limit needs to be increased. Please check the 'Billing &
> plans' section in your settings.

Fix this first (GitHub account settings → Billing & plans) — branch
protection's CI requirement is meaningless until jobs can run at all.
