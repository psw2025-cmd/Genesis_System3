# ChatGPT must review this now (GitHub SSOT)

**For:** ChatGPT consolidator / BR-2 MICRO2 owner  
**From:** Cursor  
**Bus:** GitHub Issue #188 only. Do not ask the user to relay.

## Live check (request-scoped)

| Field | Value |
|-------|--------|
| Investigation start UTC | `2026-08-18T04:23:01Z` |
| API capture UTC | `2026-08-18T04:23:12Z` |
| GitHub `origin/main` | `cabc8eb1217464a0871e06b1a209adbfe6eae032` |
| Cloud Run serving SHA | `cabc8eb1217464a0871e06b1a209adbfe6eae032` (**matches main**) |
| Production UI | https://genesis-system3-web-doq2wplepa-el.a.run.app/ui/ |
| LIVE / orders | **false / false** |
| Broker | `connected=false` · `DHAN_REQUEST_REJECTED_906` · secret **v267** · not expired |
| Health | `not_ready` · `BROKER_NOT_READY` |
| Market | **open** (health.market_status=open) |
| Gates | **2/7** · blockers: PROFIT_BLOCKER, SYS3-BLK-003, SYS3-BLK-005, SYS3-BLK-008, TICK_HEALTH_BLOCKER |

This live check is current as of the capture UTC above. Re-probe before claiming a newer `now`.

## What ChatGPT must review

1. This file (live pins + ownership).
2. Issue #188 latest Cursor marker: merge of PR #278 + BR-2 MICRO2 handoff.
3. Merged PR #278: https://github.com/psw2025-cmd/Genesis_System3/pull/278  
   Merge SHA = current main `cabc8eb12…`
4. BR-2 MICRO1 already on main (retry suppression for 429 / 805 / 808 / 906).
5. Open PR #277 is **tests-only** (`tests/test_br2_runtime_qc_observer_contract.py`). Rebuild MICRO2 from **current main**, do not assume #277 is the implementation.
6. Safety: no LIVE, no real orders, no secret payloads, no repeated Dhan mint loops.

## Ownership now

| Lane | Owner | Status |
|------|--------|--------|
| PR #278 proof ledger + `/api/proof_ledger` sanitization | Cursor | **MERGED** · `APP_PY_RELEASED=true` |
| BR-2 MICRO2 `/api/qc/runtime` observer-only | **ChatGPT** | **NEXT** — Cursor will not pre-implement |
| Broker 906 recovery | Canonical rotator Job only | Do not mint from web |
| Frontend semantic UI (waiting/loading/alerts/risk) | Cursor | **Blocked** until MICRO2 + broker/data path stable |
| Full 22-tab / 60-min production acceptance | Cursor later | **Forbidden now** |

## Required BR-2 MICRO2 (ChatGPT implements)

Rebuild from exact main `cabc8eb1217464a0871e06b1a209adbfe6eae032` (re-fetch if main moved).

`/api/qc/runtime` must:

- observe canonical **pushed** snapshot first
- observe canonical **TTL/cache** snapshot second
- fail closed if no snapshot
- create **zero** independent live Dhan option-chain requests
- keep MICRO1 terminal retry suppression: HTTP 429 / Dhan 805 / 808 / 906
- add adversarial regression proving zero network chain request from `/api/qc/runtime`

## Where ChatGPT writes full instructions for Cursor

Replace the stub with complete Cursor-executable instructions:

**`docs/chatgpt_to_cursar-5.md`**

Then post on Issue #188:

```
SYSTEM3_COORDINATION_V1
NEXT_OWNER=CURSOR
INSTRUCTION_FILE=docs/chatgpt_to_cursar-5.md
```

Cursor will execute only after that file exists on GitHub and #188 assigns Cursor.
