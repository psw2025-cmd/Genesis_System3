# Live docs cross-verify matrix — 2026-08-16

Authorities: GitHub `origin/main`, Issue #188, production URL
`https://genesis-system3-web-doq2wplepa-el.a.run.app/ui`.

Captured UTC approximately 2026-08-16T15:15Z by Cursor docs-sync.

## Live production pin (request-scoped)

| Field | Value |
|-------|-------|
| Serving SHA | `997daef4cfb3322e317da69b5cbb5b69950dab26` |
| Broker connected | **false** |
| Broker error | `TOKEN_EXPIRED_OR_INVALID` |
| Secret Manager generation | `259` |
| LIVE | false |
| Order placement | false |
| Remote main | `ebd77a0efe545bedaab9fcc1de3a1a180466c263` |

## Document inventory vs GitHub online

| Document | Required by | On `main` now? | On open PR? | Cross-verify result |
|----------|-------------|----------------|-------------|---------------------|
| `docs/BROKER_SETUP.md` canonical secret policy | Broker permanence / ChatGPT | YES | n/a | PASS — canonical `dhan-access-token`; banned aliases documented |
| `docs/incidents/BROKER_AUTH_20260816_IST.md` | Broker auth incident | YES | n/a | PASS as historical; live broker currently disconnected again |
| Q1–Q26 extracts session `20260816T123000Z/` | ChatGPT Q package / PR #249 | YES | merged #249 | PASS on GitHub; lifecycle still PARTIAL/NOT_PROVEN |
| `18_CURRENT_REMOTE_MAIN_REVALIDATION_ADDENDUM_20260816.md` | Cursor revalidation after stale PR #249 claims | **NO before this PR** | was only on #251 | FIXED in this docs PR |
| `docs/security/SEC1_NPM_AUDIT_REMEDIATION_20260816.md` | SEC-1 | **NO on main** | PR #252 | PENDING merge of #252 |
| UI-OBS-1 frontend truth docs/code | UI-OBS-1 | NO | PR #251 | PENDING merge after SEC-1 |
| BR-1 broker defense code | BR-1 | NO | PR #250 | PENDING ChatGPT |
| `SYSTEM_STATE.md` | Agent SSOT | YES but **STALE** (header 2026-06-14; Render-era) | this PR refreshes live pins | PARTIAL → updated pins in this PR |
| `CHANGE_LOG.md` | Agent bus companion | YES through Q package | missing SEC-1/UI-OBS/#252 | FIXED append in this PR |
| `reports/latest/broker_secret_dup_audit_20260816/FINAL_REPORT.md` | Older 16:53 tasklist | **MISSING** | none | NOT DONE — not Cursor SEC-1 scope; ChatGPT/token owner |
| Issue #188 coordination markers | Autonomous multi-AI | live on GitHub Issues | n/a | PASS as bus (not a repo file) |

## Open PR heads (docs must not pretend these are on main)

| PR | Wave | Head | Docs/code status |
|----|------|------|------------------|
| #252 | SEC-1 | `7e037c3b…` | CI PASS; awaiting ChatGPT merge |
| #251 | UI-OBS-1 | `df8738e0…` | frozen; addendum now also on docs PR for main |
| #250 | BR-1 | `999d0e6a…` | ChatGPT-owned |

## Verdict

- **Not all live docs were already updated on `main`.** Several truth docs lived only on open PRs or were stale.
- This PR brings the revalidation addendum + SYSTEM_STATE/CHANGE_LOG pin refresh onto GitHub for cross-verify.
- SEC-1 security doc remains correctly owned by PR #252 (avoid duplicate-path conflict).
- Final user PASS still requires ChatGPT merge/deploy + new URL proof; docs alone are not URL PASS.
