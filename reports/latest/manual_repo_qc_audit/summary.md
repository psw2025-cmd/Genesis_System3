# Genesis System3 Continuous Audit — Single Master Report

Updated: `2026-08-11 11:49 IST`

## 0. Scope lock and revision truth

- Repository: `psw2025-cmd/Genesis_System3` only.
- Branch: `main`.
- Repository HEAD observed at start of this iteration: `e38ebf93b1c401b70eba2ea5d346d3bf09e5003c`.
- Compare proof: `b70af343340a73ed27ca548820d5893c779ab5bd..e38ebf93b1c401b70eba2ea5d346d3bf09e5003c` is **16 commits ahead**, **0 behind**, and changes only `reports/latest/manual_repo_qc_audit/summary.md`; latest application/source HEAD therefore remains `b70af343340a73ed27ca548820d5893c779ab5bd`.
- PR #97 remains OPEN at `29e7b2cfc9120976e9c0d33147d92e9dc64f7484`; it is not implemented on `main` and its synthetic-P&L guard still substitutes numeric zero for rejected/unavailable P&L rather than nullable typed truth.
- PR #96 remains the newest merged application/UI PR in the current evidence set.
- Exact application-HEAD CI proof remains **NOT PROVEN**: GitHub returned no workflow runs and no combined status checks for application HEAD `b70af343...` in this iteration.
- Google Cloud Run / Google Cloud services remain the sole deployment authority. Render-era runtime assumptions are migration debt only.
- Audit posture remains ANALYZER/PAPER. Live order placement, modification, cancellation and routing are prohibited.
- This Markdown is the single continuously maintained audit/remediation authority.

## 1. Executive verdict

| Area | Verdict | Solution state |
|---|---|---|
| Exact application HEAD CI/runtime proof | **NOT PROVEN** | exact-revision provenance gate required |
| Dashboard auth/session | **FAIL / P0-P1** | **READY TO PATCH via SessionTruth** |
| Mutation authorization / CSRF / idempotency | **INCOMPLETE / P0-P1** | **READY TO PATCH** |
| Global safety/mode truth | **FAIL / P0** | **READY TO PATCH** via `SafetyTruth` |
| DB/state-store authority | **FAIL / P0-P1** | **READY TO PATCH** via `StateTruth` + domain-CAS |
| WebSocket/REST stream truth | **FAIL / P0-P1** | **READY TO PATCH** via `StreamTruth` |
| Option-chain normalization/cache | **FAIL / P0-P1** | **READY TO PATCH** via `OptionChainTruth` |
| Scanner/ranker freshness + stability | **FAIL / P0-P1** | **READY TO PATCH** via `ScannerTruth` |
| Paper mutation/lifecycle | **FAIL / P0** | **READY TO PATCH** immutable lifecycle |
| Paper P&L/reconciliation | **NOT PROVEN / P0-P1** | after-cost reconciliation required |
| Pre-trade risk authority | **FAIL / P0** | server-owned policy + mandatory risk service |
| Execution guardrail | **FAIL / P0** | fail-closed patch required |
| AI prediction ledger | **MISSING / P0-P1** | **READY TO PATCH/DESIGN** via `PredictionTruth` |
| Model provenance / leakage control | **INCOMPLETE / P0-P1** | **READY TO PATCH** |
| Probability calibration / drift | **NOT PROVEN / P1** | **READY TO PATCH/DESIGN** |
| Responsive/mobile workstation | **FAIL / P1** | **READY TO PATCH** |
| Accessibility/keyboard/focus/live-state semantics | **FAIL / P1** | **READY TO PATCH** |
| Google Cloud deployment provenance | **FAIL / P0-P1** | **READY TO PATCH** via `DeploymentTruth` |
| Observability/runtime error truth | **INCOMPLETE / P1** | **READY TO PATCH/DESIGN** |
| Real-money trade ready | **NO** | locked |

## 2. Mandatory solution-driven audit rule

Every finding must include severity, exact proof, symptom, root cause, real-money impact, exact files/routes, target behavior, minimal safe implementation, ordered implementation steps, API/schema changes, compatibility notes, safety constraints, regression risks, exact tests, PASS criteria, rollback/fail-safe behavior, and implementation state `NOT STARTED | READY TO PATCH | PATCHED | VERIFIED`.

Missing, stale, parse-failed, unauthenticated or unproven evidence must never become green, PASS, zero-risk, zero-P&L, zero-Greek, PAPER SAFE, LIVE, calibrated confidence, model-ready, fresh-market-data, broker-connected, deployed-current or trade-ready through defaults.

## 3. Retained findings registry

- `AUTH-001..011` OPEN: login contract mismatch, pre-auth startup exposure, raw browser API-key storage, non-expiring deterministic server token, logout without server revocation, no proven auth-attempt throttling, cross-origin-capable global header injection, cookie security/runtime uncertainty and incomplete mutation idempotency coverage.
- `UI-001..019` OPEN: false-valid defaults, source inference, empty/error ambiguity, missing authoritative mode/provenance, weak responsive/accessibility and deployment/build truth.
- `CHAIN-001..014` OPEN: warming PCR false-data, weak Dhan proof, incomplete Greeks, null→zero parsing, spread validity, expiry-insensitive cache, weak disk-cache provenance, invented source, generic expiry fallback and parser-error collapse.
- `SCAN-001..010` OPEN: same-day stale rank acceptance, ignored refresh intent, scanner fallback auto-eligibility, hard-coded live provenance, rotating-shard high-watermark retention, stale-row restamping, disk-cache age/session ambiguity, duplicate REST/WS writers, load-heavy equity rotation and UI freshness/eligibility ambiguity.
- `READY-001..009` OPEN: missing safety evidence default-safe paths, semantic lifecycle/risk/economic gates incomplete, weak account-success semantics, Render-era Live Gate copy and evidence-poor human approval.
- `PAPER-001..016`, `TRADE-001..003`, `LEGACY-001` OPEN: default safety/data values, unproven mutation route, direct executor bypass, process-local lifecycle, stale-price handling, incomplete costs/reconciliation and legacy mutation UI residue.
- `RISK-001..009` OPEN: browser-owned limits, permissive defaults, zero-risk fallbacks, weak VaR contract, fail-open guardrail conditions, unproven canonical wiring and proxy gate semantics.
- `WS-001..011` OPEN/UNPROVEN: socket-open≠healthy stream, weak heartbeat truth, REST/WS ordering, stale-value re-stamping, malformed-event silence, stale-last-good semantics, duplicate transport policy, fake WebSocket proof, capped age and route-owner uncertainty.
- `GCP-001..011` OPEN: exact-revision proof missing, immutable digest absent, weak frontend SHA, double service mutation, legacy-key fallback, broad runtime IAM, default service-account fallback, weak typed safety/incident proof and incomplete Render retirement.
- `STATE-001..012` OPEN: file backend default, optional Firestore fallback, stale whole-snapshot overwrite, missing domain revisions/CAS, startup local-file promotion, plausible green defaults, duplicate SSOT methods, position error→empty collapse, weak identity, mixed-generation file sync and missing multi-writer tests.
- `ML-001..014` OPEN: missing immutable prediction ledger, overloaded model-proof boolean, dictionary-first model selection, rank→confidence misuse, ambiguous percentage units, unknown→zero metrics, tracker type bug, unsafe accuracy math, non-atomic tracker persistence, non-purged/non-global time split, incomplete artifact identity, selection/evaluation leakage, missing calibration and no prediction→after-cost linkage.
- `A11Y-001..012` OPEN: fixed shell, clipped truth, inefficient keyboard traversal, non-semantic interactive controls, color-only indicators, weak live-region semantics, very small text, fragile overflow ownership, inconsistent focus, dynamic-state announcement gap, contrast redundancy and missing exact-browser proof.

## 4. Latest deep slice — authentication, session lifetime, CSRF and mutation authorization

### AUTH-001 / P0 — primary login contract is broken while secondary unlock uses the correct contract

**Exact proof:** backend `DashboardAuthRequest` requires JSON field `api_key`. `create_dashboard_session()` validates `payload.api_key`. `LoginPage.tsx` POSTs `/api/auth/session` with `Content-Type` and `X-API-Key` headers but **no request body**. `AuthUnlock.tsx` separately POSTs `body: JSON.stringify({ api_key: apiKey.trim() })` and therefore matches the backend model.

**Symptom/root cause:** two frontend authentication surfaces implement different contracts; the main AuthGate login can receive FastAPI validation failure while the in-dashboard unlock can succeed.

**Real-money impact:** operators can be locked out of protected truth, while UI may surface auth failures as broker/data problems; future mutation authorization cannot rely on a login flow that is not contract-consistent.

**Exact files/routes:** `dashboard/frontend/src/components/LoginPage.tsx`, `dashboard/frontend/src/components/AuthUnlock.tsx`, `dashboard/backend/app.py:/api/auth/session`.

**Target behavior:** one shared `AuthClient.createSession(apiKey)` contract, used by every login/unlock surface; the API key is submitted once over TLS and never retained by the browser after cookie creation.

**Minimal safe implementation:** remove the `X-API-Key` login header and send only `{api_key}` to `/api/auth/session`; on success clear the component key state and rely exclusively on the HttpOnly cookie.

**API/schema changes:** keep current request body shape for compatibility; return a typed `SessionTruth` response containing session ID, issued/expiry times, auth method and policy revision, but never secret material.

**Regression risks:** tooling that currently authenticates only by header must remain supported for non-browser automation through a separate documented header-auth mode.

**Closure tests/PASS:** LoginPage and AuthUnlock both authenticate against the same test server; malformed/missing body returns controlled error; valid key establishes cookie; no browser storage contains the raw key afterward.

**Rollback/fail-safe:** auth failure keeps protected data and all mutations locked.

**Status:** `READY TO PATCH`.

### AUTH-002 / P0-P1 — raw API key is persisted in `sessionStorage` and globally attached to requests

**Exact proof:** `LoginPage.tsx` writes `sessionStorage.setItem('s3_api_key', key.trim())`. `useAuth.ts` reads that value in a global axios interceptor and a global replacement of `window.fetch`, attaching `X-API-Key` whenever the key exists.

**Symptom/root cause:** a long-lived reusable secret is kept in JavaScript-readable storage even though an HttpOnly cookie already exists.

**Real-money impact:** any successful XSS or compromised third-party script can read/exfiltrate the dashboard API key and then authenticate independently of the browser session.

**Solution:** cookie-only browser authentication. Remove `s3_api_key`, remove the axios/fetch API-key injection patches, and keep `credentials:'include'` only for same-origin System3 API calls.

**Security constraint:** no localStorage/sessionStorage/IndexedDB/raw JS variable persists reusable authentication material after session establishment.

**Tests/PASS:** browser storage scan after login shows no API key; protected API calls succeed via HttpOnly cookie; XSS simulation cannot read session credential through JavaScript.

**Status:** `READY TO PATCH`.

### AUTH-003 / P0-P1 — global fetch/axios patch can attach the API key outside the System3 origin

**Exact proof:** `useAuth.ts` replaces `window.fetch` globally and does not inspect the request URL/origin before adding `X-API-Key`; the axios interceptor similarly does not restrict `cfg.url` to the System3 API origin.

**Symptom/root cause:** authentication is implemented as a global browser networking side effect rather than a scoped API client.

**Real-money impact:** a future external fetch/axios call to analytics, documentation, sentiment/news, or another origin can transmit/preflight the dashboard key to that origin if browser CORS policy permits the request.

**Solution:** delete global secret injection entirely. Introduce a scoped same-origin `system3Api` client that sends cookies; explicitly reject absolute cross-origin URLs in the authenticated client.

**Tests/PASS:** instrument browser networking and prove no `X-API-Key` leaves the application origin; external fetch fixture never contains credentials beyond browser-standard policy.

**Status:** `READY TO PATCH`.

### AUTH-004 / P0-P1 — the advertised 12-hour session has no server-enforced issuance/expiry state

**Exact proof:** `_dashboard_session_token()` is `sha256("system3-dashboard-session-v1:" + API_KEY)`. `_has_dashboard_api_access()` compares the cookie directly to that deterministic value. `DASHBOARD_SESSION_MAX_AGE=43200` is used only as cookie `max_age`; there is no server-side issued-at/expiry check, session record, nonce or expiry embedded in the token.

**Symptom/root cause:** browser cookie expiry is treated as session expiry, while the server accepts the same token indefinitely as long as `API_KEY` remains unchanged.

**Real-money impact:** a copied/stolen session cookie can remain reusable after the original browser's 12-hour cookie disappears, until API key rotation invalidates it.

**Solution:** cryptographically random opaque session IDs stored server-side, or a signed token carrying `iat`, `exp`, `jti`, policy version and key/session epoch with server-side revocation support. Prefer opaque sessions in Firestore/Redis-equivalent shared store for Cloud Run multi-instance behavior.

**API/schema changes:** `SessionTruth {session_id_hash, issued_at, expires_at, last_seen_at, auth_method, policy_revision, revoked, runtime_revision}`; never return the raw session token.

**Tests/PASS:** copied cookie is rejected after expiry even if browser max-age is bypassed; clock-boundary tests; multi-instance expiry consistency; key rotation invalidates prior session epoch.

**Status:** `READY TO PATCH`.

### AUTH-005 / P0-P1 — logout deletes the browser cookie but does not revoke the server credential

**Exact proof:** `/api/auth/logout` only calls `response.delete_cookie(...)`; there is no session registry/revocation list because the token is deterministic from the API key.

**Symptom/root cause:** logout is client-side credential disposal, not server-side session invalidation.

**Real-money impact:** a previously copied cookie remains accepted after user logout.

**Solution:** server session registry with `revoked_at/reason`; logout transaction revokes session ID before deleting cookie. Add `logout_all`/key-epoch rotation for emergency response.

**Tests/PASS:** clone cookie into a second client, log out first client, second client must receive 401 immediately; revocation must work across Cloud Run instances.

**Status:** `READY TO PATCH`.

### AUTH-006 / P1 — authentication endpoint has no proven brute-force/rate-limit policy

**Exact proof:** application rate-limit middleware only adds delay to `/api/broker` and `/api/chain` prefixes. `/api/auth/session` is PUBLIC by security policy and the inspected code has no attempt counter, backoff or temporary lockout.

**Symptom/root cause:** the one secret protecting the dashboard can be attempted repeatedly without an application-level auth-specific rate policy.

**Real-money impact:** increases online guessing/credential-stuffing exposure, especially if Cloud Run ingress is public.

**Solution:** auth-specific rate limiting keyed by source + normalized account/system scope, exponential backoff, bounded failure counters, structured security events and alert threshold. Do not leak whether API key format/length is correct.

**Compatibility:** automation/header API auth should have separate service identity/rate policy rather than sharing human login throttles.

**Tests/PASS:** repeated invalid attempts trigger 429/backoff; valid session cannot bypass rate accounting through alternate login surface; secrets never enter logs.

**Status:** `READY TO PATCH/DESIGN`.

### AUTH-007 / P1 — cookie `Secure` depends on request scheme and exact production proxy behavior is not proven

**Exact proof:** `response.set_cookie(... secure=request.url.scheme == "https", samesite="lax")`. Cloud Run normally terminates TLS upstream; correctness therefore depends on the ASGI server/proxy-header configuration presenting the external scheme as HTTPS.

**Symptom/root cause:** a security attribute is runtime-derived rather than explicitly production-enforced.

**Impact:** if proxy scheme handling is ever misconfigured, the browser session cookie can be issued without `Secure`.

**Solution:** production configuration must set `SESSION_COOKIE_SECURE=1` and fail startup if deployed environment would issue an insecure auth cookie. Local development may explicitly opt out.

**Tests/PASS:** exact Cloud Run browser response must contain `Secure; HttpOnly`; deployment proof records cookie-policy hash without cookie value.

**Status:** `READY TO PATCH/VERIFY`.

### AUTH-008 / P1 — CSRF policy has a useful fail-closed base but needs typed session-bound mutation authority

**Positive proof:** `security_policy.evaluate_request()` rejects mutation routes when auth is disabled; when cookie auth is used without API-key header it validates Origin against same-origin/allowed origins. Worker push routes have separate worker-token checks.

**Residual issue:** policy receives only booleans (`dashboard_access`, `header_api_key_present`) and does not bind a mutation to a session ID, session age, authorization scope, policy revision or CSRF nonce. Browser and service auth are still represented as one coarse access boolean.

**Solution:** `MutationAuthContext` contains principal/session ID, auth method, issue/expiry/revocation state, origin result, CSRF result, permission scopes, policy revision and request/evidence ID. Cookie-authenticated unsafe methods require same-origin plus CSRF token bound to the session (or a rigorously verified same-site/origin-only policy with explicit proof).

**Tests/PASS:** missing/forged Origin, cross-site form, stale session, revoked session and wrong CSRF token all fail; valid same-origin session succeeds only for allowed scope.

**Status:** `READY TO PATCH`.

### AUTH-009 / P1 — idempotency enforcement covers only two hard-coded paths

**Exact proof:** `IDEMPOTENCY_REQUIRED_PATHS = {"/api/orders/create", "/place-order"}`. Other mutation routes are subject to auth/origin checks but not this policy's idempotency requirement.

**Symptom/root cause:** replay protection is path allow-list based instead of mutation-capability based.

**Real-money impact:** future paper/risk/settings/scheduler or order-adjacent mutations can be introduced without automatically receiving idempotency/replay protection.

**Solution:** classify every route by capability metadata (`READ`, `PREFERENCE_WRITE`, `PAPER_MUTATION`, `RISK_POLICY_WRITE`, `WORKER_INGEST`, `LIVE_MUTATION`) and require idempotency for all financially/state-significant mutations. Unknown new mutation category fails CI/security-policy tests.

**Tests/PASS:** route inventory test enumerates every POST/PUT/PATCH/DELETE and asserts explicit capability/auth/idempotency policy; no unclassified mutation is deployable.

**Status:** `READY TO PATCH`.

### AUTH-010 / P1 — browser auth UX advertises “SESSION 12 HRS” without authoritative server expiry evidence

**Exact proof:** `LoginPage.tsx` renders `SESSION 12 HRS`, while current server token has no verifiable issued/expiry fields and `/api/auth/status` returns only required/configured/authenticated/mode.

**Impact:** UI communicates stronger session-lifetime assurance than the backend proves.

**Solution:** Security / Settings screen consumes `SessionTruth.expires_at` and renders countdown/expiry source; until implemented display `SESSION EXPIRY: NOT PROVEN`, never a fixed 12-hour guarantee.

**Status:** `READY TO PATCH`.

### AUTH-011 / P1 — security/session observability and audit-export contract is incomplete

**Exact proof:** current auth status response does not provide session ID hash, issued/expiry, revocation, auth method detail, principal/scope, policy revision or security-event correlation ID.

**Impact:** operators cannot distinguish fresh session, nearly expired session, revoked/invalid session, header-service auth or policy mismatch from a single authenticated boolean.

**Solution:** expose sanitized `SessionTruth`, security event timeline and audit export containing only hashes/IDs/status, never API key, cookie, Dhan token/PIN/TOTP or worker token.

**Tests/PASS:** export redaction test, session lifecycle event tests, exact-revision evidence linkage and browser UI redaction proof.

**Status:** `READY TO PATCH/DESIGN`.

## 5. Positive security foundations to preserve

- Explicit CORS allow-list; wildcard and `null` origins are rejected at startup.
- Browser session cookie is `HttpOnly` and uses `SameSite=Lax`.
- `hmac.compare_digest` is used for API-key/cookie/worker-token comparisons.
- Mutations fail closed when dashboard authentication is disabled/unconfigured.
- Worker push paths use a distinct `X-Worker-Token` policy.
- Origin validation exists for cookie-authenticated mutations.
- Selected order paths already require `Idempotency-Key`.
- Auth smoke test verifies missing auth fails, header auth works, wrong key returns 401 and HttpOnly cookie auth works.

These are foundations, not proof of session expiry, revocation, browser-secret safety or complete mutation authorization.

## 6. Canonical truth contracts

### 6.1 `SafetyTruth`
Mode, nullable live/auto flags, router/kill-switch state, source/runtime/image/policy revisions, verified time/age, `PROVEN|STALE|UNKNOWN|ERROR`.

### 6.2 `SessionTruth` — NEW
`session_id_hash`, issued/expiry/last-seen times, auth method (`COOKIE|SERVICE_HEADER`), principal/scope, session epoch, policy revision, revoked state/time/reason, secure-cookie policy, origin/CSRF policy version, runtime/source revision and evidence ID. Raw tokens/secrets are never exposed.

### 6.3 `MutationAuthContext` — NEW
Request/evidence ID, session/principal, capability class, origin result, CSRF result, idempotency key/hash, permission decision, policy revision and fail-closed reason. Unknown capability or unknown session truth denies mutation.

### 6.4 `DataTruthEnvelope` / `StreamTruth`
Source/session/instrument, source/backend/frontend timestamps, uncapped age/TTL, schema/normalizer versions, transport vs heartbeat vs stream state, sequence/rejected-old events, quality and evidence.

### 6.5 `OptionChainTruth`
Underlying/security ID/segment, requested+resolved expiry authority, provider/session, times/age/TTL, expiry-aware cache identity, schema/normalizer versions, nullable quote/Greek fields + field quality, completeness, source/runtime revision and evidence ID.

### 6.6 `ScannerTruth`
Snapshot/cycle/session/universe IDs, per-row event time/revision/source/quote quality, age/TTL, rank policy/units, validation state, worker/load diagnostics and exact runtime/source revision. Old observations are never restamped fresh.

### 6.7 `DeploymentTruth`
Exact source/tree SHA, Cloud Build ID, immutable image digest, final Cloud Run revision/traffic, frontend/backend SHA, runtime app/service account, policy/config hash, secret/scheduler provenance, verified time and evidence ID.

### 6.8 `StateTruth`
Required shared backend, shared-state health, runtime/instance ID, last shared read/write, per-domain revision/writer/event/time/schema/quality/evidence. Global version is diagnostic only.

### 6.9 `PredictionTruth`
Immutable prediction ID/time, target/horizon/instrument, model/data/feature hashes, frozen cutoff, raw score/calibrated probability/uncertainty, input truth IDs, runtime/source revision, maturity state and append-only after-cost outcome links.

## 7. Canonical remediation roadmap

- `SOL-01 Auth/session + SessionTruth — READY TO PATCH`: unify login contract; cookie-only browser auth; remove browser API-key storage/global header patch; server-enforced expiry/revocation; auth throttling; secure-cookie proof; mutation capability inventory; CSRF/idempotency tests.
- `SOL-02 SafetyTruth — READY TO PATCH`: one backend authority; missing/stale => UNKNOWN.
- `SOL-03 DataTruthEnvelope — READY TO PATCH`: remove production zero/plausible defaults.
- `SOL-04 Semantic readiness — READY TO PATCH`: HTTP/object presence never PASS; lifecycle/reconciliation/risk/economics mandatory.
- `SOL-05 OptionChainTruth + Greeks — READY TO PATCH`: nullable parser, expiry-aware cache, explicit provenance/IV units/full Greeks.
- `SOL-06 Immutable paper lifecycle — READY TO PATCH`: durable event ledger, IDs/idempotency, restart replay/reconciliation, costed P&L.
- `SOL-07 ScannerTruth — READY TO PATCH`: latest-observation snapshots, per-row age, session TTL, rank/score/probability separation, independent candidate validation, ordered REST/WS merge.
- `SOL-08 DeploymentTruth + GCP least privilege — READY TO PATCH`: immutable digest/final revision/source SHA, one service mutation, dedicated identities, WIF-only auth.
- `SOL-09 PreTradeRiskService — READY TO PATCH`: server-owned policy; fresh PASS required; UNKNOWN/ERROR denies.
- `SOL-10 Legacy UI quarantine — READY TO PATCH`: production entrypoint guard; no legacy mutation surface.
- `SOL-11 StreamTruth — READY TO PATCH`: transport != healthy stream; heartbeat schema; ordered REST/WS merge; uncapped age; true WS proof.
- `SOL-12 RuntimeEventEnvelope — READY TO PATCH/DESIGN`: incidents/logs bound to source SHA + digest + Cloud Run revision.
- `SOL-13 StateTruth + domain-CAS — READY TO PATCH`: Firestore required in GCP; sparse domain writes; no local authority fallback; restart/multi-writer proof.
- `SOL-14 PredictionTruth + ModelArtifactManifest — READY TO PATCH/DESIGN`: immutable prediction ledger, exact model/data identity, purged walk-forward, untouched holdout, calibrated probability, drift and after-cost outcome linkage.
- `SOL-15 AccessibleWorkstationShell — READY TO PATCH`: responsive shell, tiered truth header, drawer/compact navigation, command palette, keyboard/focus/live regions, exact-revision Playwright/axe proof.
- `SOL-16 Scanner worker/load isolation — READY TO PATCH/DESIGN`: bounded provider worker, token-bucket pacing, cycle IDs/deadlines and load proof.

### SOL-01 ordered implementation

1. Create one shared frontend `AuthClient`; both LoginPage and AuthUnlock use it.
2. Fix `/api/auth/session` request to JSON body only; remove redundant API-key header from browser login.
3. Remove `sessionStorage` API key and global axios/window.fetch credential patches.
4. Add scoped same-origin API client with cookie credentials only.
5. Replace deterministic cookie token with random opaque server session ID or signed expiring token + revocation epoch.
6. Persist session records in shared GCP-safe store; include expiry/revocation/policy revision.
7. Make logout revoke server session before deleting cookie; add emergency revoke-all/session-epoch operation.
8. Add auth-attempt throttling/backoff and sanitized security events.
9. Enforce production `Secure; HttpOnly; SameSite` cookie policy independent of proxy ambiguity.
10. Introduce `MutationAuthContext` and capability metadata for every unsafe route.
11. Require session-bound CSRF/origin policy and idempotency for financially/state-significant mutation capabilities.
12. Extend `/api/auth/status` into sanitized `SessionTruth`; UI shows actual expiry/policy, not hard-coded 12 hours.
13. Add security/settings session list, revoke control and redacted audit export.
14. Run unit/integration/browser/security tests on exact application revision.

**SOL-01 PASS criteria:** primary login and unlock share one contract; no reusable API key exists in browser storage; no authenticated secret header can leave System3 origin; copied cookie expires server-side and is rejected after logout/revocation; exact Cloud Run response proves Secure+HttpOnly cookie; auth brute-force throttle works; every unsafe route has explicit capability/auth/CSRF/idempotency policy; no raw auth/broker secret appears in logs/UI/export; analyzer/paper/live-off remains unchanged.

**Rollback/fail-safe:** any session-store, policy, CSRF, cookie or authorization uncertainty sets auth state `UNKNOWN/ERROR`, hides protected truth, inhibits paper mutations and leaves live routing locked.

## 8. Verification counters

Independent reproduction paths only.

| Finding | Counter | State |
|---|---:|---|
| AUTH-001 | `4/20` | OPEN — main LoginPage still omits required JSON body |
| AUTH-002 | `3/20` | OPEN — raw browser API-key storage reproduced |
| AUTH-003 | `3/20` | OPEN — global axios/fetch injection reproduced |
| AUTH-004 | `2/20` | OPEN — deterministic non-expiring server token independently inspected |
| AUTH-005 | `1/20` | OPEN — logout has no server revocation |
| AUTH-006 | `1/20` | OPEN — no auth-specific throttling in inspected middleware |
| AUTH-007 | `1/20` | OPEN/VERIFY — Secure depends on runtime scheme handling |
| AUTH-008 | `1/20` | OPEN — coarse CSRF/mutation context |
| AUTH-009 | `1/20` | OPEN — idempotency allow-list limited to two paths |
| AUTH-010 | `1/20` | OPEN — UI fixed 12-hour claim exceeds server proof |
| AUTH-011 | `1/20` | OPEN — session/security observability incomplete |
| UI-001 | `17/20` | OPEN |
| UI-002 | `5/20` | OPEN |
| UI-003 | `8/20` | OPEN |
| UI-005 | `15/20` | OPEN |
| UI-006 | `9/20` | OPEN |
| UI-007 | `11/20` | OPEN |
| UI-009 | `6/20` | OPEN |
| UI-011 | `4/20` | OPEN |
| UI-016 | `11/20` | OPEN — session/security product truth remains incomplete |
| UI-018 | `2/20` | OPEN |
| CHAIN-001..014 | retained previous counters | OPEN |
| SCAN-001..010 | `1/20` each | OPEN |
| READY-001 | `5/20` | OPEN |
| READY-003 | `3/20` | OPEN |
| READY-008 | `2/20` | OPEN |
| PAPER-001..016 | retained previous counters | OPEN |
| RISK-001..009 | `1/20` each | OPEN |
| WS-001..010 | `1/20` each | OPEN |
| WS-011 | `1/20` | UNPROVEN |
| GCP-001..011 | `1/20` each | OPEN |
| STATE-001..012 | `1/20` each | OPEN |
| ML-001..014 | `1/20` each | OPEN |
| A11Y-001..012 | `1/20` each | OPEN |

No finding is `LOCKED-20X`.

## 9. Prioritized implementation order

### P0 Wave 1 — eliminate false-green/fail-open authorities
1. **SOL-01 auth contract + cookie-only SessionTruth + server expiry/revocation.**
2. SOL-02 authoritative `SafetyTruth`.
3. SOL-08 exact `DeploymentTruth` baseline.
4. SOL-13 shared `StateTruth` authority + domain-CAS.
5. SOL-05 OptionChainTruth null/cache/expiry correction.
6. SOL-11 StreamTruth and ordered REST/WS merge.
7. SOL-07 ScannerTruth current-snapshot/high-watermark correction.
8. SOL-09 server-owned risk + mandatory pre-trade authority.
9. SOL-06 durable lifecycle/idempotency/reconciliation.
10. SOL-14 model maturity split + immutable PredictionTruth foundation.
11. SOL-04 semantic readiness.
12. SOL-03 remaining zero/live/default-safe fallbacks.
13. SOL-10 legacy mutation UI quarantine.

### P1 Wave 2 — operator safety + statistical/economic proof
1. Complete mutation capability/CSRF/idempotency route inventory and exact browser security proof.
2. SOL-16 scanner worker/load isolation.
3. SOL-15 responsive/accessibility shell and exact-revision browser proof.
4. Purged walk-forward + untouched holdout, calibration, drift, model/data hashes.
5. Prediction→paper→after-cost outcome linkage.
6. Full Greeks/model provenance and true WebSocket proof.
7. GCP IAM split/WIF-only auth and revision-bound runtime incidents.

### P2 Wave 3 — institutional operator quality
Advanced command palette/search, customizable density, saved workspace layouts, session/device management, permission drilldowns and redacted audit export. These remain secondary to truth/safety.

## 10. Product information architecture target

1. Command Center — Overview + Decision Intel + authoritative truth strip.
2. Market / Scanner — watch, scanner, ranker, signals, snapshot history/rank movement and candidate drilldown.
3. Options & Greeks — chain, expiry/cache/provenance, IV/OI/liquidity/full Greeks.
4. AI Decision Audit — Genesis Brain + Prediction Audit + model provenance + calibration/drift + evidence/outcome linkage.
5. Paper / Trade Lifecycle — capability-driven ticket, immutable orders/fills/positions/P&L/reconciliation.
6. Portfolio & Risk — server-owned policy, exposure, aggregate Greeks, scenarios.
7. Data & Broker Health — state authority, domain revisions, transport/heartbeat/source/freshness/account/cache truth.
8. Readiness / Proof — semantic E2E gates + Live Gate.
9. Observability — deployment identity, incidents, logs, schema/parse errors, latency/reconnects and revision-bound evidence.
10. **Security / Settings — SessionTruth, devices/sessions, expiry/revocation, auth method, mutation policy, CSRF/idempotency status, IAM/policies, audit export and non-authoritative preferences.**

Current repo tabs remain represented through this rationalized hierarchy; conceptual renames never imply implemented capability.

## 11. Product UI visual evolution — V15

New concept: **Security & Session Control V15** — actual System3 `Security / Settings` product workspace.

Changes required by this iteration:
- header exposes auth/session state separately from Dhan broker auth;
- browser API key is never displayed or stored after session creation;
- session shows issued time, authoritative server expiry, auth method, policy revision and runtime revision;
- active-session/device table supports server-side revoke and emergency revoke-all;
- cookie policy shows `Secure`, `HttpOnly`, `SameSite` and exact-revision verification state;
- mutation authorization matrix shows capability, origin/CSRF, idempotency and backend enforcement state;
- security-event timeline records login failures, throttling, revoke, expiry and policy-denial events without secrets;
- redacted audit export explicitly excludes API key, cookie, Dhan token, PIN/TOTP and worker token;
- session/policy uncertainty sets protected capabilities to `INHIBITED`;
- live router remains locked.

Visual artifact: `Genesis_System3_Security_Session_Control_Target_V15.png`.

## 12. Positive foundations to preserve

- Explicit CORS allow-list and startup rejection of wildcard/null origins.
- `HttpOnly` browser cookie and `SameSite=Lax` baseline.
- `hmac.compare_digest` for secret comparisons.
- Mutation fail-closed behavior when auth is disabled/unconfigured.
- Separate worker token for ingestion paths.
- Existing cookie-auth Origin validation.
- Existing idempotency requirement on selected order paths.
- Native Sidebar buttons, named navigation landmark and `aria-current`.
- `prefers-reduced-motion` support.
- Prediction Audit's refusal to present gain-rank as a validated forecast.
- Firestore transaction/local temp+replace foundations.
- Serialized/rate-paced Dhan option-chain traffic and WS reconnect backoff+jitter foundations.
- Live Gate approval does not automatically enable live trading.

These are foundations, not readiness/security/profitability proof.

## 13. Historical proof/open-gate interpretation

Remain open:
- `EXACT_REVISION_CI_RUNTIME_NOT_PROVEN`
- `AUTH_LOGIN_CONTRACT_NOT_PROVEN`
- `SERVER_SESSION_EXPIRY_NOT_PROVEN`
- `SESSION_REVOCATION_NOT_PROVEN`
- `BROWSER_SECRET_ELIMINATION_NOT_PROVEN`
- `MUTATION_AUTHORIZATION_COVERAGE_NOT_PROVEN`
- `CSRF_POLICY_RUNTIME_NOT_PROVEN`
- `IDEMPOTENCY_ROUTE_COVERAGE_NOT_PROVEN`
- `DEPLOYMENT_TRUTH_NOT_PROVEN`
- `SHARED_STATE_AUTHORITY_NOT_PROVEN`
- `RESTART_CONSISTENCY_NOT_PROVEN`
- `MULTI_WRITER_LOST_UPDATE_PROTECTION_NOT_PROVEN`
- `SCANNER_CURRENT_SNAPSHOT_NOT_PROVEN`
- `SCANNER_ROW_FRESHNESS_NOT_PROVEN`
- `SCANNER_LOAD_STABILITY_NOT_PROVEN`
- `PREDICTION_LEDGER_NOT_PROVEN`
- `MODEL_ARTIFACT_IDENTITY_NOT_PROVEN`
- `PURGED_WALKFORWARD_NOT_PROVEN`
- `PROBABILITY_CALIBRATION_NOT_PROVEN`
- `PREDICTION_AFTER_COST_LINKAGE_NOT_PROVEN`
- `RESPONSIVE_WORKSTATION_NOT_PROVEN`
- `ACCESSIBILITY_AXE_BROWSER_PROOF_NOT_PROVEN`
- `REAL_MARKET_ANALYZER_PAPER_LIFECYCLE_NOT_PROVEN`
- `TRADE_READY_FALSE`
- `MULTI_DAY_STABILITY_NOT_PROVEN`
- `POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN`
- `WEBSOCKET_STREAM_HEALTH_NOT_PROVEN`
- `OPTION_CHAIN_RUNTIME_TRUTH_NOT_PROVEN`

`LIVE_TRADING_DISABLED_BY_DESIGN` remains required audit posture.

## 14. Closure standard

A finding becomes `CLOSED` only on the exact changed revision with source inspection; positive/negative tests; static/type/build checks; unit/integration/browser tests; auth/session expiry/revocation and secret-redaction tests; complete mutation capability/CSRF/idempotency inventory; route/schema reconciliation; model/data hashes and frozen-cutoff proof where applicable; leakage/purged-walk-forward/calibration/drift tests for ML; prediction→paper→after-cost reconciliation; concurrency/CAS/restart/failover tests; expiry/cache/freshness/order/reconnect tests; scanner current-snapshot/session/TTL/out-of-order/high-watermark/load tests; responsive viewport + 200%-zoom + keyboard + axe/console checks; immutable image digest + final Cloud Run revision/runtime proof; analyzer/live-off unchanged; and no contradictory independent evidence.

## 15. Next audit/solution slices

1. Exact mutation-route inventory: enumerate every POST/PUT/PATCH/DELETE and map capability, auth, CSRF, idempotency and live/paper enforcement.
2. Scanner concurrency follow-up: locate micro-loop/state-file writer and prove whether overlapping cycles can write out of order under Cloud Run concurrency.
3. ML follow-up: exact market-validation file semantics and frozen prediction IDs/cutoffs.
4. DB follow-up: exact paper/event persistence files and SQLite/JSON/Firestore duplicate authorities.
5. Browser follow-up once SOL-01/SOL-15 land: exact Playwright/axe/security proof across every workspace.

## 16. Hard safety rule

A green UI, endpoint HTTP 200, authenticated boolean, browser cookie presence, client-side cookie max-age, socket OPEN, historical parser/training PASS, AUC/accuracy, rank-derived confidence, scanner rank, high-watermark cached winner, image tag, UI badge, workflow success description, global state version, Firestore transaction, local atomic write, zero-valued quote/Greek/risk/P&L, static PAPER SAFE, stale cache, inferred Dhan source, human approval, accessible-looking static markup or process-local simulator never substitutes for authoritative session expiry/revocation+permission policy+source/event time+domain/snapshot revision+writer+freshness+schema+ordering+immutable prediction/model/data evidence+calibration+forward validation+lifecycle+enforceable risk+reconciliation+positive after-cost expectancy+exact source SHA+immutable image digest+final serving runtime revision proof. Live order placement, modification, cancellation and routing remain prohibited during this audit.