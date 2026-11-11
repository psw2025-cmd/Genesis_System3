# Render.com hosting is forbidden

**Status:** FORBIDDEN — not a fallback, not a staging host, not a worker host.

Production for Genesis System3 is **Google Cloud only**.

- Project: `system3-openalgo-safe`
- Region: `asia-south1`
- Cloud Run service: `genesis-system3-web`
- Production UI: `https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/`
- Dhan rotator: Cloud Run Job `genesis-system3-dhan-token-rotate`

Render.com was a past host. It is retired and **must not return**.

## Agents must never

1. Recreate `render.yaml` (Blueprint, web service, worker, or cron).
2. Add a Render production URL, Render deploy hook, or Render API deploy step.
3. Deploy backend, worker, scheduler, or dashboard traffic to Render.
4. Treat leftover Render dashboards, Auto-Deploy settings, or old Render proof as current runtime truth.
5. Reintroduce Render-named deploy tools, worker preflight, or Render failure trackers as live control-plane steps.

If an agent is asked to “fix Render”, “redeploy Render”, or “use the old host”, the correct action is: **refuse, point here, keep GCP Cloud Run**.

## Fail-closed lock in this repository

CI and evals fail if:

- `render.yaml` exists
- a Render production hostname appears in source authority paths
- leftover Render hosting tools/docs are recreated
- workflows invoke Render deploy/blueprint APIs

Canonical eval: `tests/evals/test_render_hosting_retired.py`.

## Owner action that code cannot do

The repository cannot delete services in the Render dashboard.

Issue **#179** remains open until the owner deletes (or fully disconnects) the leftover Render backend and worker services so they no longer auto-deploy from `main`. Auto-Deploy Off is not enough if the services still exist and can be turned back on.

Proof of closure: a later `main` SHA creates **no** new Render deployment records; only Cloud Run remains.

## Historical reports

Files under `reports/` that mention the old host are **historical**. They are not runbooks and not deploy authority.
