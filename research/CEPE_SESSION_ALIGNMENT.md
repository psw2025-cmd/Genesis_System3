# CEPE-SESSION-004 — missing-session guard

Evidence date: 2026-09-26. Parent: `4951de2e3c3539872bec59b2e837023efa62a76c`.

Previously, any two observations up to five calendar days apart could be called
adjacent sessions. A missing Tuesday file therefore allowed Monday-to-Wednesday
returns to enter a next-opening scorecard. This changes the measured horizon.

`cepe_session_scope.py` now supplies the same alignment contract to comparison,
historical replay, prediction issuance and settlement. Without a calendar, only
consecutive dated observations can establish that no intervening date was skipped.
A wider interval remains available as `HISTORICAL_INTERVAL_ONLY`; its `next_open`
is null and the observation is named `observed_open`. Replay and forward scoring
reject it. A missing file or ordinary weekday heuristic never proves closure.

## Optional calendar declaration

`--session-calendar` takes UTF-8 JSON with schema `nse-session-calendar-v1`, segment
`FO`, inclusive ISO `start` and `end`, timezone-aware `available_at`, official NSE
HTTPS `source_url`, raw `source_sha256`, and `days`. Every date in the inclusive
range must be present in `days`: null declares closure; a timezone-aware timestamp
declares that session's opening. Both endpoints must be open and every intervening
date closed. Special sessions must appear explicitly. Duplicate keys, missing dates,
an intervening open session, a late calendar, or inconsistent timestamps fail closed.

This is a **sourced declaration**, not independently verified exchange evidence.
The result says `DECLARED_SOURCE_NOT_INDEPENDENTLY_VERIFIED`. No new official
calendar was authenticated in this checkpoint. On consecutive dates without a
calendar, 09:15 IST remains an explicit `REGULAR_SESSION_ASSUMPTION`, not proof of
special-session timing. Real forward promotion still requires verified timing.

Issuance binds the exact calendar bytes and hash inside the immutable receipt;
settlement cannot introduce a different calendar. Existing consecutive-date v1
receipts still settle. Older multi-day receipts without calendars now fail closed;
do not alter their original bytes to manufacture advance evidence.

## Verification

Command from the isolated GitHub-derived workspace:

```sh
PYTHONPATH=_testdeps:. python -m pytest tests/test_cepe_next_open_proof.py tests/test_cepe_forward_scorecard.py tests/test_cepe_prediction_ledger.py tests/test_cepe_walkforward_baseline.py tests/test_cepe_session_scope.py tests/test_nse_option_gainers.py -o addopts='' -q --tb=short
```

2026-09-26, approximately 11:38 UTC; cwd
`/workspace/scratch/6ff6830099fe/system3_work_20260926`; exit 0;
**42 tests and 5 unittest subtests passed in 0.05 seconds**. Synthetic contract
tests only, not local Windows runtime or market success. The existing Global
Safety workflow now runs these tests too; no new workflow or runner was added.

The old walk-forward test fixture accidentally ranked the later winner first while
asserting it was missed. Running unchanged parent code reproduced that contradiction.
The fixture's B opening was corrected from 10 to 80 to exercise the intended missed
winner scenario. Expected results and the actual ranking strategy were not relaxed.

Real-data regression on exact officially retrieved July 21/22, 2025 bytes reproduces
4,712 matches, 11 >=3x, maximum 4.526316x. Skipping the actual July 22 observation now
marks July 21→23 as an interval and rejects next-open replay. These are regression
checks on previously inspected data and add no new independent market observations.
The earlier July 25→28 research receipt is retained; next-session qualification of
that wider date gap now needs a sourced complete calendar. Do not silently count it
as verified next-session evidence or erase its archived raw arithmetic.

## New real observations

`evidence/2026-09-26_cepe_session_evidence.json` stores exact source ZIP/CSV hashes,
retrieval times, complete sorted multiple distributions, top reference moves and
every qualified POLICYBZR contract. Raw sources remain reproducible at the listed
official NSE URLs. Files were retrieved after their historical dates, so source
availability at hypothetical earlier issue times is NOT_PROVEN.

Filters unchanged: prior close >=1, positive next opening, volume >=100 in **both**
daily files. Following-day volume is retrospective: it cannot be used for advance
selection or establish liquidity at the opening print. No ratios are winsorized.

| Historical interval | Matched contracts | >=3x | >=10x | >=20x | >=30x | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sep 23→24, 2026 | 4,675 | 111 | 19 | 12 | 8 | 58.064516x |
| Sep 24→25, 2026 | 5,330 | 5 | 0 | 0 | 0 | 8.75x |

The first maximum is MFSL 29-Sep-2026 1500 PE: 1.55 close→90 opening.
POLICYBZR 29-Sep-2026 1680 PE: 1 close→51.25 opening on Sep 24.
These are dated gross reference observations, not executable fills or predictions.

The unchanged prior-day momentum top100 rule selected 200 contracts, with 175
scoreable, **0 hits, 175 false picks, 25 unscoreable and 116 missed >=3x movers**.
Its last-pair `holdout` field is merely the script's retrospective split; this is
not an untouched strategy test or independently pre-issued forecast evidence.
Do not promote this rule from the large observed opportunity multiples.

## Numerical gap and next target

Real forward issued/settled forecasts remain **0/0**. Valid forward OOS trades/days
are **0/0**, versus current-main targets **100/60**, gaps **100/60**. Directional
accuracy, top-decile precision, Sharpe, drawdown and DSR are NOT_PROVEN, with null
numerical gaps against targets 65%, 70%, 2.5, <=10%, >=0.95 respectively. Retrospective
3x-event precision is not directional accuracy or top-decile precision. Source
authenticity of these files does not establish costs, calibration or causation.

CEPE-NEXT-005: pre-register a liquidity/volatility-normalized baseline and dated
fees/slippage before evaluating later untouched dates. Catalyst additions require
a separate no-catalyst ablation and earlier-known publication evidence. These Sep
23–25 outcomes are now inspected diagnostics and cannot become an untouched test.
Expand source coverage toward two continuous years; current sparse samples do not
satisfy that request. PAPER/ANALYZE only, no broker calls, no orders, no merge.
