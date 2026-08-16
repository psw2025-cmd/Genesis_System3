# Executive Verdict — System3 Full Cloud UI Forensic

**Session:** `20260816T062501Z`  
**Audit start:** 2026-08-16T06:25:01Z / 2026-08-16 11:55:01 IST  
**Capture end:** 2026-08-16T06:35:47Z / 2026-08-16 12:05:47 IST  
**Mode:** READ-ONLY — no functional remediation, no deploy, no IAM/token mutation.

## Live production snapshot (request-scoped)

| Item | Value |
|------|-------|
| UI | https://genesis-system3-web-doq2wplepa-el.a.run.app/ui |
| GitHub `main` | `c763ecf048478842688373cf674eb56a7dc04aa9` |
| Serving `/api/deploy/info` | `a48e7b3c7c086a21352f718355d1c12d4a48955b` |
| Revision | `genesis-system3-web-00384-tuw` |
| Image tag | `asia-south1-docker.pkg.dev/system3-openalgo-safe/system3-containers/genesis-system3:a48e7b3c7c08-1786830179` |
| Broker | **connected=true** (Dhan) |
| Token source | GCP_SECRET_MANAGER_DYNAMIC v257 |
| Live trading | **false** |
| Orders | **false** |
| Market | Weekend closed (Sunday) — `EXPECTED_AFTER_HOURS` |

## Verdict

Production UI is **reachable**, **broker-connected**, **Paper / Live off**, and **Option Chain provenance is visible** (`source=dhan · universe=security_id_list.csv`) for NIFTY weekend snapshot (**462 contracts, CE/PE 231/231**).

This is **NOT** a claim that System3 is institutionally complete.

Material blockers for ChatGPT remediation design:

1. **Serving SHA lag vs GitHub main** (F-001) — proofs must lock to serving SHA.
2. **Issue #188 universe parity incomplete** (F-002) — full broker universe not proven.
3. **Flaky multi-index chain under concurrency/timeouts** (F-003).
4. **UI/backend miswirings** (PCR fields, Prediction Audit→gates, accuracy_trend orphan) (F-004..F-006).
5. **No PRODUCTION_DURABLE option-chain lake / weak ML registry** (F-007, F-008).
6. **CI failures on current main** for Full Cloud Audit / Frontend Smoke / Security Audit Evidence (F-012).

Waiting tabs this capture: truth, genesis, e2e-proof, overview, multibagger, system — classify with market-hours re-proof before calling defects.

## Hypothesis recheck (section 26)

| Hypothesis | Classification |
|------------|----------------|
| Dhan OHLC/quote/LTP can hit HTTP 429 | NOT_PROVEN this window (GCP 429 samples were Cloud Run capacity aborts) |
| paced chain cache feeds indices | STILL_PRESENT (code + weekend snapshot path) |
| India VIX unavailable | NOT_PROVEN failure — wiring via `/api/market/live_board` exists |
| Truth WAITING | STILL_PRESENT (visible) |
| Genesis waits model evidence | STILL_PRESENT (WAITING) |
| E2E waits four chains | STILL_PRESENT (WAITING) |
| Overview waits market/model | STILL_PRESENT |
| Multibagger waits scans | STILL_PRESENT |
| Index chains hundreds of contracts | STILL_PRESENT for NIFTY (462); intermittent NO_DHAN_DATA for others under stampede |
| source= provenance missing | **FALSE_PREVIOUS_FINDING / DISPROVEN as UI absence** — visible on chain tab |
| broker connected | **CHANGED** — now true |
| health OK | STILL_PRESENT (`/api/health` status ok) |

## Counts (this package)

| Severity | Count (material findings listed) |
|----------|----------------------------------|
| P0 | 3 (F-001, F-002, F-014 safety OK listed separately) |
| P1 | 7 |
| P2 | 4 |
| P3 | 1 (provenance OK) |

See `11_P0_P3_REMEDIATION_BACKLOG.md` and `16_HANDOFF_TO_CHATGPT.md`.
