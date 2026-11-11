# India Market Session Authority — Genesis System3

Status: mandatory control-plane rule for all agents, schedulers, health checks, QC, scanners, dashboard badges, market-open logic and production acceptance.

## 1. Time-zone authority

All India-market decisions MUST use the IANA time zone `Asia/Kolkata` (IST, UTC+05:30).

Do not infer Indian market state from UTC clock time, Cloud Run host time, browser local time, GitHub Actions runner time, or a hard-coded offset without converting through `Asia/Kolkata`.

Every production proof that depends on market phase must record an IST timestamp.

## 2. Exchange-calendar authority

A weekday is not automatically a trading day. Before declaring `OPEN`, `PRE_OPEN`, `CLOSED`, `POST_CLOSE`, or evaluating missing market-session data, System3 must use the applicable official NSE/BSE trading calendar, including exchange holidays, special sessions, Muhurat/special trading, outages, and exchange-announced timing changes.

Official exchange timing/calendar evidence overrides stale repository assumptions.

## 3. NSE cash-equity baseline

Normal cash-equity continuous session baseline:

- Pre-open session: 09:00–09:15 IST.
- Normal/odd-lot market: 09:15–15:30 IST.
- Closing session: 15:40–16:00 IST.

These are baseline session windows only; exchange announcements/calendar rules remain authoritative.

## 4. NSE equity-derivatives baseline

For NSE equity derivatives, use the official session published by NSE for the applicable date and product. As of this control-rule update, NSE publishes normal equity-derivatives trading as 09:15–15:40 IST, with the pre-open mechanism applying to eligible futures from 09:00–09:15 IST.

Do not incorrectly reuse the 15:30 cash-equity close for every derivative product.

## 5. Runtime truth requirements

Any `market_status`, `is_open`, scanner/QC readiness, scheduler decision, freshness SLA, paper-trading acceptance, or dashboard market badge MUST be derived from:

1. current timestamp converted to `Asia/Kolkata`;
2. applicable exchange/product session;
3. current official trading-day calendar;
4. any special-session/outage override known for that date.

The API/UI must not report `market_status=open` outside the applicable official session merely because broker authentication is healthy.

Likewise, a `NO_QC_DATA`, zero cycles, empty scanner, or missing signal outside the applicable market session must not be misdiagnosed as a runtime failure solely from absence of live-session data.

## 6. Acceptance and forensic rule

Before diagnosing any production symptom as a market-hours failure or data-pipeline failure, every agent must explicitly state:

- `OBSERVED_AT_IST`
- `TRADING_DATE_IST`
- `MARKET_SEGMENT`
- `OFFICIAL_SESSION_FOR_DATE`
- `MARKET_PHASE`
- `HOLIDAY_OR_SPECIAL_SESSION_STATUS`

If this context is missing, the market-state conclusion is incomplete and cannot close a RHUI/RUHI gate.

## 7. Safety

Market-hours logic never authorizes LIVE trading. Genesis System3 remains PAPER/analyzer-only unless separately and explicitly authorized. Existing live-order safety locks remain mandatory.

## 8. Source authority

Primary references are official exchange publications/pages, especially NSE/BSE market timings and trading-holiday/special-session notices. Agents should re-verify official exchange sources when current timing materially affects a decision rather than relying indefinitely on this document's baseline hours.
