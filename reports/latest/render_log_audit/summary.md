# Render Log Excerpt Audit

## Verdict

`PASS_WITH_WARNINGS`

The pasted excerpt does **not** prove an OOM event. It proves three actionable problems:

1. Dashboard UI exposed raw Vue `{{ ... }}` template text.
2. Dhan token refresh had a startup/rate-limit failure before later success.
3. Several dashboard API calls are slow enough to create Render starter load pressure.

## Findings

| Priority | Area | Finding | Action |
|---|---|---|---|
| P0 | Dashboard UI | Raw Vue template expressions were visible in the user-provided dashboard text. | Browser proof now fails if raw `{{ ... }}` tokens are visible. |
| P0 | Dhan token refresh | `generate_token` hit Dhan 2-minute rate limit; `renew_token` failed with `DH-906 Invalid Token`; OAuth manual fallback printed. | Add Render-cloud guard/cooldown so duplicate refresh does not spam/fallback. |
| P1 | Token recovery | One minute later, `generate_token` succeeded and token was set in cloud env process. | Auto-refresh works but needs startup overlap protection. |
| P1 | API performance | `/api/state`, `/api/paper`, `/api/broker/status`, `/api/trades/today` took 3–5 seconds in the excerpt. | Add TTL/cache/coalescing for heavy polling endpoints. |
| P1 | Memory pressure | Instruments loaded from runtime JSON: 143079 rows. | Treat as startup memory pressure; not proven leak. |
| P2 | Model proof | ML signal CSV missing; `ml_confidence_score=0`. | Prediction factor incomplete for current session. |

## Action already taken

- Updated `tests/dashboard_browser_proof.spec.ts` so dashboard proof fails if raw Vue `{{ ... }}` template text is visible.
- Added this log audit report:
  - `reports/latest/render_log_audit/summary.md`
  - `reports/latest/render_log_audit/summary.json`

## Remaining required action

1. Patch token refresh cloud behavior:
   - no automatic manual OAuth URL printing in Render auto-start path,
   - cooldown/lock for 2-minute Dhan generate-token rate limit,
   - no secrets printed.
2. Add endpoint load protection:
   - short TTL cache for heavy dashboard endpoints,
   - request coalescing while one request is already running.
3. Run Playwright proof after deploy:
   - PASS only if no visible `{{ ... }}` tokens,
   - screenshots saved under `reports/latest/dashboard_browser_proof/screenshots/`.
4. Collect actual OOM/restart lines if memory crash continues.

## Live trading status

`DISABLED` — no live orders enabled or changed.
