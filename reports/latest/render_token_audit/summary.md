# Render Token Refresh Audit

## Verdict

`PASS_WITH_WARNINGS`

A safe daemon-level cooldown was added for Render/cloud token refresh attempts.

## Render log issue proven by user excerpt

- `generate_token` returned: `Token can be generated once every 2 minutes.`
- `renew_token` failed with: `DH-906 Invalid Token`.
- Manual OAuth fallback was printed during cloud startup.
- One minute later, `generate_token` succeeded and token was set in cloud process env.

## Fix applied

File changed:

- `scripts/dhan_token_auto_refresh.py`

Commit:

- `3c9f344452ea6a6c2126535f79fc1c8d88cb0cd3`

Changes:

- Added cloud detection.
- Added 130-second refresh cooldown.
- Added guarded `_safe_refresh()` wrapper.
- Startup invalid-token refresh now respects cooldown.
- Scheduled daemon refresh now respects cooldown.
- Manual OAuth remains available only through explicit `--oauth` command.

## Safety

- Live trading unchanged and disabled.
- No broker secrets touched.
- No `.env` changed.
- No real orders enabled.

## Remaining risk

Backend startup may still call `token_manager.refresh_token()` directly outside the daemon path. If Render logs still show automatic OAuth manual fallback, the next patch must harden `core/brokers/dhan/token_manager.py` itself with a cloud-mode no-auto-OAuth guard.

## Next verification after Render deploy

Check logs for:

- no repeated `generate_token` attempts inside 2 minutes,
- no automatic OAuth consent URL during normal Render startup,
- token refresh either succeeds once or reports cooldown cleanly,
- dashboard still shows live trading disabled.
