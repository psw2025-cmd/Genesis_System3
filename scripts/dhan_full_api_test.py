"""
Dhan Full API Test — All Available Data for Traders
=====================================================
Tests every safe read-only endpoint available through Dhan broker.
Run this to confirm what data is available for the trading system.

Usage:
    python scripts/dhan_full_api_test.py
    python scripts/dhan_full_api_test.py --save    # save results to logs/
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".secrets" / "dhan.env", override=True)

# ── Dhan client setup ──────────────────────────────────────────────────────────
from dhanhq import dhanhq as DhanHQ
from dhanhq.dhan_context import DhanContext

CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "")
ctx = DhanContext(CLIENT_ID, ACCESS_TOKEN)
client = DhanHQ(ctx)

# ── Constants ──────────────────────────────────────────────────────────────────
NIFTY_SEC_ID = "13"  # NIFTY 50 index security ID
BANKNIFTY_SEC_ID = "25"  # BANK NIFTY index security ID
NIFTY_IT_SEC_ID = "27"  # NIFTY IT index security ID
SENSEX_SEC_ID = "51"  # SENSEX

RESULTS = {}
PASS = "✅ PASS"
FAIL = "❌ FAIL"
SKIP = "⏭  SKIP"


def test(name, fn):
    """Run one test, capture result."""
    print(f"\n  [{name}]", end=" ", flush=True)
    t0 = time.time()
    try:
        data = fn()
        ms = int((time.time() - t0) * 1000)
        # Check for Dhan error responses
        if isinstance(data, dict):
            if data.get("status") == "failure" or data.get("errorCode"):
                msg = data.get("remarks") or data.get("errorCode") or str(data)
                print(f"{FAIL} ({ms}ms) — {msg}")
                RESULTS[name] = {"status": "FAIL", "error": msg, "ms": ms}
                return None
        print(f"{PASS} ({ms}ms)")
        RESULTS[name] = {"status": "PASS", "ms": ms}
        return data
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        err = str(e)[:120]
        print(f"{FAIL} ({ms}ms) — {err}")
        RESULTS[name] = {"status": "FAIL", "error": err, "ms": ms}
        return None


def section(title):
    print(f"\n{'═'*55}")
    print(f"  {title}")
    print(f"{'═'*55}")


def show(label, value, indent=4):
    sp = " " * indent
    if isinstance(value, dict):
        for k, v in list(value.items())[:8]:
            print(f"{sp}{k}: {v}")
    elif isinstance(value, list):
        print(f"{sp}count: {len(value)}")
        if value and isinstance(value[0], dict):
            print(f"{sp}sample keys: {list(value[0].keys())[:8]}")
    else:
        print(f"{sp}{label}: {value}")


# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "╔" + "═" * 53 + "╗")
print("║       DHAN FULL API TEST — Genesis System3         ║")
print("╚" + "═" * 53 + "╝")
print(f"  Client  : ...{CLIENT_ID[-4:]}")
print(f"  Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ── 1. ACCOUNT DATA ───────────────────────────────────────────────────────────
section("1. ACCOUNT & PORTFOLIO DATA")

r = test("Fund Limits / Balance", lambda: client.get_fund_limits())
if r:
    d = r.get("data", r)
    print(f"    availableBalance  : ₹{d.get('availabelBalance', 0):.2f}")
    print(f"    sodLimit          : ₹{d.get('sodLimit', 0):.2f}")
    print(f"    withdrawableBalance: ₹{d.get('withdrawableBalance', 0):.2f}")
    print(f"    utilizedAmount    : ₹{d.get('utilizedAmount', 0):.2f}")

r = test("Holdings (long-term)", lambda: client.get_holdings())
if r:
    items = r if isinstance(r, list) else r.get("data", [])
    print(f"    holdings count: {len(items)}")
    if items:
        h = items[0]
        print(f"    sample: {h.get('tradingSymbol')} qty={h.get('totalQty')} avg={h.get('avgCostPrice')}")

r = test("Open Positions", lambda: client.get_positions())
if r:
    items = r if isinstance(r, list) else r.get("data", [])
    print(f"    positions count: {len(items)}")
    if items:
        p = items[0]
        print(f"    sample: {p.get('tradingSymbol')} qty={p.get('netQty')} pnl={p.get('realizedProfit')}")

r = test("Order List (today)", lambda: client.get_order_list())
if r:
    items = r if isinstance(r, list) else r.get("data", [])
    print(f"    orders today: {len(items)}")

r = test("Trade Book (today)", lambda: client.get_trade_book())
if r:
    items = r if isinstance(r, list) else r.get("data", [])
    print(f"    trades today: {len(items)}")

r = test(
    "Trade History (last 30 days)",
    lambda: client.get_trade_history(
        from_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        to_date=datetime.now().strftime("%Y-%m-%d"),
        page_number=0,
    ),
)
if r:
    items = r if isinstance(r, list) else r.get("data", [])
    print(f"    trades in last 30 days: {len(items)}")

r = test(
    "Ledger Report (last 30 days)",
    lambda: client.ledger_report(
        from_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        to_date=datetime.now().strftime("%Y-%m-%d"),
    ),
)
if r:
    items = r if isinstance(r, list) else r.get("data", [])
    print(f"    ledger entries: {len(items)}")


# ── 2. OPTIONS CHAIN DATA ─────────────────────────────────────────────────────
section("2. OPTIONS CHAIN DATA")

# Get expiry list first
nifty_expiries = []
r = test("NIFTY Expiry List", lambda: client.expiry_list(NIFTY_SEC_ID, client.NSE_FNO))
if r:
    data = r if isinstance(r, list) else r.get("data", [])
    nifty_expiries = data[:5] if data else []
    print(f"    upcoming expiries: {nifty_expiries[:4]}")

r = test("BANKNIFTY Expiry List", lambda: client.expiry_list(BANKNIFTY_SEC_ID, client.NSE_FNO))
if r:
    data = r if isinstance(r, list) else r.get("data", [])
    print(f"    upcoming expiries: {(data or [])[:4]}")

# Option chain for nearest expiry
if nifty_expiries:
    nearest = nifty_expiries[0]
    r = test(f"NIFTY Option Chain ({nearest})", lambda: client.option_chain(NIFTY_SEC_ID, client.NSE_FNO, nearest))
    if r:
        data = r.get("data", r)
        if isinstance(data, dict):
            chain = data.get("oc", data)
            strikes = list(chain.keys()) if isinstance(chain, dict) else []
            print(f"    strikes available: {len(strikes)}")
            if strikes:
                mid = strikes[len(strikes) // 2]
                ce = chain[mid].get("ce", {})
                pe = chain[mid].get("pe", {})
                print(f"    ATM strike ~{mid}:")
                print(f"      CE OI={ce.get('oi',0):,}  IV={ce.get('iv',0):.1f}%  LTP={ce.get('last_price',0)}")
                print(f"      PE OI={pe.get('oi',0):,}  IV={pe.get('iv',0):.1f}%  LTP={pe.get('last_price',0)}")
        elif isinstance(data, list):
            print(f"    option records: {len(data)}")
else:
    print(f"  {SKIP} Option Chain — no expiry dates available")


# ── 3. MARKET QUOTE DATA ─────────────────────────────────────────────────────
section("3. REAL-TIME MARKET QUOTE DATA")

securities_nse = {client.NSE_FNO: [NIFTY_SEC_ID, BANKNIFTY_SEC_ID]}

r = test("Quote Data (NIFTY + BANKNIFTY)", lambda: client.quote_data(securities_nse))
if r:
    data = r.get("data", r)
    if isinstance(data, dict):
        for sec_id, q in list(data.items())[:2]:
            print(
                f"    secId={sec_id}: ltp={q.get('last_price',0)} open={q.get('open',0)} high={q.get('high',0)} low={q.get('low',0)} close={q.get('close',0)}"
            )

r = test("OHLC Data (NIFTY + BANKNIFTY)", lambda: client.ohlc_data(securities_nse))
if r:
    data = r.get("data", r)
    if isinstance(data, dict):
        for sec_id, q in list(data.items())[:2]:
            print(
                f"    secId={sec_id}: open={q.get('open',0)} high={q.get('high',0)} low={q.get('low',0)} close={q.get('close',0)}"
            )


# ── 4. HISTORICAL / CANDLE DATA ───────────────────────────────────────────────
section("4. HISTORICAL CANDLE DATA")

today = datetime.now().strftime("%Y-%m-%d")
from_30d = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
from_5d = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

r = test(
    "NIFTY Daily Candles (30 days)",
    lambda: client.historical_daily_data(
        security_id=NIFTY_SEC_ID,
        exchange_segment=client.NSE_FNO,
        instrument_type="INDEX",
        from_date=from_30d,
        to_date=today,
    ),
)
if r:
    data = r.get("data", r)
    if isinstance(data, dict):
        opens = data.get("open", [])
        print(f"    candles returned: {len(opens)}")
        if opens:
            print(f"    latest close: {data.get('close', [])[-1] if data.get('close') else 'N/A'}")

r = test(
    "NIFTY 1-min Intraday (today)",
    lambda: client.intraday_minute_data(
        security_id=NIFTY_SEC_ID,
        exchange_segment=client.NSE_FNO,
        instrument_type="INDEX",
        from_date=today,
        to_date=today,
        interval=1,
    ),
)
if r:
    data = r.get("data", r)
    if isinstance(data, dict):
        opens = data.get("open", [])
        print(f"    1-min candles today: {len(opens)}")

r = test(
    "NIFTY 5-min Intraday (last 5 days)",
    lambda: client.intraday_minute_data(
        security_id=NIFTY_SEC_ID,
        exchange_segment=client.NSE_FNO,
        instrument_type="INDEX",
        from_date=from_5d,
        to_date=today,
        interval=5,
    ),
)
if r:
    data = r.get("data", r)
    if isinstance(data, dict):
        opens = data.get("open", [])
        print(f"    5-min candles (5 days): {len(opens)}")


# ── 5. INSTRUMENT / SECURITY LIST ─────────────────────────────────────────────
section("5. INSTRUMENT / SECURITY MASTER")

r = test("Security List Download (compact)", lambda: DhanHQ.fetch_security_list(mode="compact"))
if r is not None:
    print(f"    Security list: downloaded to security_id_list.csv")
    import os

    if os.path.exists("security_id_list.csv"):
        with open("security_id_list.csv") as f:
            lines = f.readlines()
        print(f"    Total instruments: {len(lines)-1:,}")
        if lines:
            print(f"    Headers: {lines[0].strip()[:80]}")


# ── 6. MARGIN CALCULATOR ──────────────────────────────────────────────────────
section("6. MARGIN CALCULATOR")

r = test(
    "Margin for NIFTY 1 lot (simulation)",
    lambda: client.margin_calculator(
        security_id=NIFTY_SEC_ID,
        exchange_segment=client.NSE_FNO,
        transaction_type=client.BUY,
        quantity=50,  # 1 NIFTY lot = 50
        product_type=client.MARGIN,
        price=23600,
        trigger_price=0,
    ),
)
if r:
    data = r.get("data", r)
    if isinstance(data, dict):
        print(f"    total_margin: ₹{data.get('total_margin', data.get('totalMargin', 'N/A'))}")
        print(f"    span_margin : ₹{data.get('span_margin', data.get('spanMargin', 'N/A'))}")


# ── SUMMARY ───────────────────────────────────────────────────────────────────
section("SUMMARY")
passed = sum(1 for v in RESULTS.values() if v["status"] == "PASS")
failed = sum(1 for v in RESULTS.values() if v["status"] == "FAIL")
total = len(RESULTS)

print(f"\n  Total tests : {total}")
print(f"  Passed      : {passed}  ✅")
print(f"  Failed      : {failed}  ❌")
print(f"\n  FAILED TESTS:")
for name, v in RESULTS.items():
    if v["status"] == "FAIL":
        print(f"    • {name}: {v.get('error','?')[:80]}")

if failed == 0:
    print("\n  ALL DATA ENDPOINTS WORKING — system has full data access for trading.\n")
else:
    print(f"\n  {passed}/{total} endpoints working.\n")


# ── SAVE REPORT ───────────────────────────────────────────────────────────────
import argparse

if "--save" in sys.argv:
    report_path = ROOT / "logs" / f"api_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "results": RESULTS}, f, indent=2)
    print(f"  Report saved: {report_path}")
