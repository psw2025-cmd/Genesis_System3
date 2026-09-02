# Broker Auth Incident — 2026-08-16 (Mumbai / IST)

**Audience:** ChatGPT + operators  
**Operator locale:** Mumbai, India (`Asia/Kolkata`, IST = UTC+5:30)  
**Production URL:** https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/

---

## 1. What the user saw (screenshot ~17:04 IST)

| UI signal | Meaning |
|-----------|---------|
| TopBar **Broker Dhan · Auth issue** | `/api/broker/status` had `connected=false` |
| Data Integrity → Authentication **Dhan login: Not connected** | Same broker connected flag |
| **Token: Unknown** + box **TOKEN_EXPIRED_OR_INVALID** | App label for Dhan auth reject (often DH-906), **not** proof the JWT wall-clock expired |
| Deploy SHA **a48e7b3** | Serving image **before** PR #244 auto-heal deploy finished |
| Network tab all **200** | Frontend APIs responded; failure is **broker auth**, not UI HTTP outage |
| Console only `API_BASE configured` | No frontend crash |

**Important:** Screenshot time (~17:04 IST / 11:34 UTC) is **before** the successful remint that created Secret Manager **`dhan-access-token` v259** at **17:10 IST / 11:40 UTC**.

---

## 2. Ultra-micro root cause (broker)

1. Canonical secret `dhan-access-token` **v258** was rejected by Dhan (`DH-906 Invalid Token`) while `hours_remaining` still showed ~20h.
2. Duplicate secrets (`system3-dhan-access-token`, `DHAN_BROKER_TOKEN`) created confusion but web already pointed at `dhan-access-token`.
3. Web self-heal was **OFF** (`DHAN_CANONICAL_ROTATION_SELF_HEAL=0`) → reload storms, no automatic remint.
4. First rotate Job attempts failed until stale **TOTP** versions were disabled (only latest TOTP/PIN enabled).
5. Successful Job `genesis-system3-dhan-token-rotate-fmvkc` wrote **v259**; Dhan profile returned **HTTP 200**.

**Not the cause:** Google Cloud Storage Insights incident `NHLVNDD` (us-central1 metadata snapshots). See §4.

---

## 3. What we implemented (why)

| Action | Why |
|--------|-----|
| Quarantine duplicate token secrets | Single source of truth: `dhan-access-token` |
| Remint via Cloud Run Job only | Sole mint authority (never mint in web process) |
| Enable `DHAN_CANONICAL_ROTATION_SELF_HEAL=1` + 900s cooldown | On DH-906, web invokes Job, waits for SM version advance, hot-reloads |
| Pub/Sub topic `broker-token-rotate` + web publisher | Operator/event signal (mint still only via Job) |
| Grant web SA `run.invoker` on rotate Job | Required for auto-heal invoke |
| Docs `docs/BROKER_SETUP.md` + former `infra/rotate-job.yaml` | Historical 2026-08-16 implementation; the GCP manifest was later retired and is non-authoritative |
| PR #244 merged | Code + deploy contract on `main` |

**Safety unchanged:** `LIVE_TRADING_ENABLED=false`, orders disabled.

---

## 4. Google Storage Insights incident NHLVNDD — UNRELATED

| Claim | Verdict |
|-------|---------|
| Affects Cloud Run / Dhan token / UI auth? | **NO** |
| Affects normal GCS object read/write? | **NO** (per Google notice) |
| Affects Storage Insights inventory views in us-central1? | **YES** (metadata snapshots only) |
| Used by Genesis broker path? | **NO** — repo scan found **0** references to `object_attributes_view` / Storage Insights |
| Region of our web service | **asia-south1** (Mumbai), not us-central1 Insights path |

**Operator rule:** Do **not** treat NHLVNDD as explanation for `TOKEN_EXPIRED_OR_INVALID`. Defer only Storage Insights–driven cleanup/inventory jobs until snapshot freshness is proven.

---

## 5. Live re-proof (after fix) — 2026-08-16 ~17:25 IST

| Check | Result |
|-------|--------|
| `/api/broker/status` | `connected=true`, secret **v259**, LIVE=false |
| Dhan `/v2/profile` | **HTTP 200** |
| UI TopBar | **Broker Connected** |
| Serving SHA | `2d6a9e888d6bac96147a1325bbcc5bf93a76f500` (PR #244) |
| Revision | `genesis-system3-web-00388-bel` |
| Region | asia-south1 |

---

## 6. Checklist (ultra micro) — for next Auth issue

- [ ] Note **IST** wall time of screenshot vs SM version `createTime` (UTC+5:30)
- [ ] `GET /api/broker/status` → `connected`, `error`, `token_proof.secret_version`, `hours_remaining`, `canonical_rotation`
- [ ] `GET /api/deploy/info` → `git_sha`, region
- [ ] Secret Manager: only `dhan-access-token` should be the live token; banned secrets stay quarantined
- [ ] Dhan profile with client-id header → 200 vs DH-906/DH-901 (**do not paste tokens**)
- [ ] Rotate Job recent executions succeededCount/failedCount
- [ ] TOTP/PIN: only **latest** versions ENABLED
- [ ] Env: `DHAN_CANONICAL_ROTATION_SELF_HEAL=1`, cooldown 900, secret id `dhan-access-token`
- [ ] Confirm NHLVNDD / Storage Insights **not** in the failure path
- [ ] If disconnected + self-heal skipped: check Job IAM invoker includes web SA; check cooldown; remint via Job

---

## 7. Related evidence paths

- PR #244: https://github.com/psw2025-cmd/Genesis_System3/pull/244
- RCA addendum (PR #242): `docs/audits/system3_full_cloud_ui/sessions/20260816T062501Z/21_POST_RECOVERY_RCA_ADDENDUM_V257_V258.md`
- Local proof: `reports/latest/broker_secret_dup_audit_20260816/FINAL_REPORT.md`
- This incident note: `docs/incidents/BROKER_AUTH_20260816_IST.md`

---

## 8. Request-scoped re-proof — 2026-08-17 09:35–09:48 IST

The scheduled rotation produced v261 but production later returned
`DHAN_REQUEST_REJECTED_906`. The bounded manual recovery workflow was executed
with its force input and created canonical secret v262.

Post-recovery proof:

- GitHub recovery run `31993268520`: PASS.
- `/api/broker/status`: `connected=true`, `error=null`, secret v262, dynamic
  Secret Manager source.
- `/api/health`: `status=ok`, broker connected, analyzer ready.
- Live Dhan data: current gain-rank rows with spots and populated NIFTY /
  BANKNIFTY option chains.
- Fresh production browser: TopBar `Dhan · Connected`, Broker tab connected,
  Option Chain populated.
- Production SHA `4185162b2b6dd69beb034c4cf84aec4dda95900b` equals GitHub
  `main`; Cloud Run revision `genesis-system3-web-00425-dec` serves 100%.
- Safety unchanged: LIVE=false and order placement disabled.

Scope note: broker health is confirmed. Overall strategy readiness remains
blocked by genuine proof gates (including ML Spearman); no gate was weakened.
