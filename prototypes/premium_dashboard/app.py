"""Genesis System3 - Premium Dashboard prototype (honest-by-design).

Run:  uvicorn app:app --host 0.0.0.0 --port 8000
Open: http://localhost:8000/ui

Design rules (improvements over the original prompt):
* All market data here is SIMULATED. It is never labelled "NSE LIVE" and every
  JSON response carries ``data_mode="SIMULATED"`` and ``real=False``.
* Hashes are verifiable: ``hash = sha256(canonical_json(data) + timestamp)``.
  Evidence entries form a hash chain (each entry embeds ``prev_hash``) so
  ``/api/hash-chain`` can detect tampering instead of just printing hashes.
* GET routes are generated from catalogues (symbols, strikes, scanners) - the
  route total is *measured* from ``app.routes``, never hardcoded.
* Route status is observed (last HTTP status actually served), not a constant
  "ONLINE" string.
* The exception handler reports ``auto_corrected=False`` - nothing is silently
  "corrected"; the failure is logged to /api/audit.
* PAPER/ANALYZE only. This app contains no broker client and cannot place,
  modify or cancel orders.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import math
import os
import random
import threading
import time
import uuid
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = Path(os.environ.get("PREMIUM_TEMPLATE", BASE_DIR / "templates" / "premium.html"))
DATA_MODE = "SIMULATED"
DATA_SOURCE = "SIMULATED_FEED (random walk; not exchange data)"
SEED = int(os.environ.get("DASHBOARD_SEED", "20261102"))
TICK_SECONDS = float(os.environ.get("DASHBOARD_TICK_SECONDS", "1.0"))
SEED_ROUNDS = int(os.environ.get("DASHBOARD_SEED_ROUNDS", "200"))
EVIDENCE_MAX = int(os.environ.get("DASHBOARD_EVIDENCE_MAX", "20000"))
HISTORY_MAX = 500
ENABLE_FAULT_ROUTE = os.environ.get("ENABLE_FAULT_ROUTE", "0") == "1"

# Permanent PAPER/ANALYZE safety posture. Reported as *effective* values read
# from the environment so a misconfiguration is visible, never hidden.
SAFETY_DEFAULTS = {
    "ANALYZE_MODE": "1",
    "PAPER_MODE": "1",
    "SYSTEM3_MODE": "analyze",
    "LIVE_TRADING_ENABLED": "0",
    "SYSTEM3_LIVE_TRADING_ALLOWED": "0",
    "AUTO_EXECUTE_TRADES": "0",
    "LIVE_ORDER_AUTHORITY": "0",
    "ORDER_PLACEMENT_ALLOWED": "false",
}

SYMBOLS: list[str] = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "BHARTIARTL", "ITC",
    "KOTAKBANK", "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "BAJFINANCE", "WIPRO",
    "TATAMOTORS", "HINDALCO", "JSWSTEEL", "ADANIENT", "ADANIPORTS", "BAJAJFINSV", "BPCL",
    "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY", "EICHERMOT", "GRASIM",
    "HCLTECH", "HEROMOTOCO", "HINDUNILVR", "INDUSINDBK", "NESTLEIND", "ONGC", "POWERGRID",
    "SHREECEM", "SUNPHARMA", "TATASTEEL", "TECHM", "TITAN", "ULTRACEMCO", "UPL", "NIFTY",
    "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY", "SENSEX",
]
INDICES = {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY", "SENSEX"}
# Illustrative starting levels for the simulator only (not quotes).
BASE_PRICES: dict[str, float] = {
    "RELIANCE": 1300, "TCS": 3400, "INFY": 1500, "HDFCBANK": 1000, "ICICIBANK": 1400,
    "SBIN": 820, "BHARTIARTL": 1900, "ITC": 420, "KOTAKBANK": 2100, "LT": 3600,
    "AXISBANK": 1150, "ASIANPAINT": 2400, "MARUTI": 12500, "BAJFINANCE": 950, "WIPRO": 260,
    "TATAMOTORS": 700, "HINDALCO": 700, "JSWSTEEL": 1050, "ADANIENT": 2400, "ADANIPORTS": 1400,
    "BAJAJFINSV": 2000, "BPCL": 320, "BRITANNIA": 5800, "CIPLA": 1500, "COALINDIA": 390,
    "DIVISLAB": 6000, "DRREDDY": 1250, "EICHERMOT": 6500, "GRASIM": 2700, "HCLTECH": 1500,
    "HEROMOTOCO": 5200, "HINDUNILVR": 2450, "INDUSINDBK": 750, "NESTLEIND": 1200, "ONGC": 245,
    "POWERGRID": 290, "SHREECEM": 29000, "SUNPHARMA": 1650, "TATASTEEL": 160, "TECHM": 1450,
    "TITAN": 3500, "ULTRACEMCO": 12000, "UPL": 680, "NIFTY": 25500, "BANKNIFTY": 57000,
    "FINNIFTY": 27000, "MIDCAPNIFTY": 13000, "SENSEX": 83500,
}
SCANNER_SYMBOLS = SYMBOLS[:40]
STRIKES = list(range(1000, 1501, 5))  # 1000..1500 inclusive => 101 strikes
OPTION_DEFAULT_UNDERLYING = "RELIANCE"


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------
def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def canonical(v: Any) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), default=str)


def make_hash(v: Any, ts: str | None = None) -> str:
    """sha256(canonical_json(v) + iso_timestamp). Canonical JSON (sorted keys)
    replaces str(v) so the hash is reproducible by any client."""
    ts = ts or utcnow()
    return hashlib.sha256((canonical(v) + ts).encode("utf-8")).hexdigest()


def envelope(data: Any, kind: str, **extra: Any) -> dict:
    ts = utcnow()
    return {
        "kind": kind,
        "data": data,
        "data_mode": DATA_MODE,
        "real": False,
        "real_market_data": False,
        "source": DATA_SOURCE,
        "timestamp": ts,
        "hash": make_hash(data, ts),
        "hash_algorithm": "sha256(canonical_json(data) + timestamp)",
        **extra,
    }


# ---------------------------------------------------------------------------
# State: simulator + hash-chained evidence store
# ---------------------------------------------------------------------------
class State:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.rng = random.Random(SEED)
        self.prices: dict[str, float] = {s: float(BASE_PRICES[s]) for s in SYMBOLS}
        self.open_prices: dict[str, float] = dict(self.prices)
        self.history: dict[str, deque] = {s: deque(maxlen=HISTORY_MAX) for s in SYMBOLS}
        self.evidence: deque = deque(maxlen=EVIDENCE_MAX)
        self.seq = 0
        self.genesis_hash = hashlib.sha256(f"genesis:{SEED}".encode()).hexdigest()
        self.last_hash = self.genesis_hash
        self.started = time.time()
        self.ticks = 0
        self.route_stats: dict[str, dict] = {}
        self.logs: deque = deque(maxlen=500)
        self.audit: deque = deque(maxlen=200)

    # -- simulator ---------------------------------------------------------
    def _step_price(self, sym: str) -> float:
        vol = 0.0006 if sym in INDICES else 0.0012
        p = self.prices[sym] * math.exp(self.rng.gauss(0, vol))
        p = round(max(p, 1.0), 2)
        self.prices[sym] = p
        return p

    def _append_evidence(self, sym: str, price: float, ts: str, origin: str) -> dict:
        self.seq += 1
        body = {
            "seq": self.seq, "symbol": sym, "price": price, "timestamp": ts,
            "source": DATA_SOURCE, "data_mode": DATA_MODE, "origin": origin,
            "prev_hash": self.last_hash,
        }
        entry = dict(body, hash=make_hash(body, ts))
        self.last_hash = entry["hash"]
        self.evidence.append(entry)
        return entry

    def tick(self, ts: str | None = None, origin: str = "SIMULATED_TICK") -> None:
        with self.lock:
            ts = ts or utcnow()
            for s in SYMBOLS:
                p = self._step_price(s)
                self.history[s].append((ts, p))
                self._append_evidence(s, p, ts, origin)
            self.ticks += 1

    def seed(self, rounds: int) -> None:
        start = datetime.now(timezone.utc) - timedelta(seconds=rounds * TICK_SECONDS)
        for i in range(rounds):
            ts = (start + timedelta(seconds=i * TICK_SECONDS)).isoformat(timespec="milliseconds")
            self.tick(ts, origin="SIMULATED_SEED")
        with self.lock:
            self.open_prices = {s: self.history[s][0][1] for s in SYMBOLS}

    # -- integrity ---------------------------------------------------------
    def verify_chain(self, entries: list[dict] | None = None) -> dict:
        with self.lock:
            items = list(self.evidence) if entries is None else entries
        if not items:
            return {"verified": False, "checked": 0, "reason": "no evidence"}
        prev = items[0]["prev_hash"]
        for i, e in enumerate(items):
            body = {k: v for k, v in e.items() if k != "hash"}
            if e["prev_hash"] != prev:
                return {"verified": False, "checked": i, "broken_at_seq": e["seq"], "reason": "prev_hash link mismatch"}
            if make_hash(body, e["timestamp"]) != e["hash"]:
                return {"verified": False, "checked": i, "broken_at_seq": e["seq"], "reason": "content hash mismatch"}
            prev = e["hash"]
        return {
            "verified": True, "checked": len(items),
            "first_seq": items[0]["seq"], "last_seq": items[-1]["seq"],
            "anchor_prev_hash": items[0]["prev_hash"], "head_hash": items[-1]["hash"],
            "anchored_to_genesis": items[0]["prev_hash"] == self.genesis_hash,
        }

    def closes(self, sym: str) -> list[float]:
        with self.lock:
            return [p for _, p in self.history[sym]]


STATE = State()
STATE.seed(SEED_ROUNDS)


# ---------------------------------------------------------------------------
# Analytics (computed from the simulated series - nothing random per request)
# ---------------------------------------------------------------------------
def ema(values: list[float], n: int) -> list[float]:
    if not values:
        return []
    k = 2 / (n + 1)
    out = [values[0]]
    for v in values[1:]:
        out.append(v * k + out[-1] * (1 - k))
    return out


def rsi(values: list[float], n: int = 14) -> float | None:
    if len(values) <= n:
        return None
    gains, losses = [], []
    for a, b in zip(values[:-1], values[1:]):
        d = b - a
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    ag = sum(gains[:n]) / n
    al = sum(losses[:n]) / n
    for g, l in zip(gains[n:], losses[n:]):
        ag = (ag * (n - 1) + g) / n
        al = (al * (n - 1) + l) / n
    if al == 0:
        return 100.0
    return round(100 - 100 / (1 + ag / al), 2)


def macd(values: list[float]) -> dict | None:
    if len(values) < 35:
        return None
    line = [a - b for a, b in zip(ema(values, 12), ema(values, 26))]
    signal = ema(line, 9)
    return {"macd": round(line[-1], 4), "signal": round(signal[-1], 4), "histogram": round(line[-1] - signal[-1], 4)}


def quote(sym: str) -> dict:
    c = STATE.closes(sym)
    last, open_ = c[-1], STATE.open_prices[sym]
    with STATE.lock:
        last_ts = STATE.history[sym][-1][0]
    window = c[-120:]
    return {
        "symbol": sym, "price": last, "session_open": open_,
        "change": round(last - open_, 2), "change_pct": round((last / open_ - 1) * 100, 3),
        "high": max(window), "low": min(window), "last_tick_utc": last_ts,
        "instrument_type": "INDEX" if sym in INDICES else "EQUITY",
    }


def returns(c: list[float]) -> list[float]:
    return [b / a - 1 for a, b in zip(c[:-1], c[1:])]


def momentum_baseline(sym: str) -> dict:
    c = STATE.closes(sym)
    diffs = [b - a for a, b in zip(c[:-1], c[1:])]
    recent = diffs[-10:]
    drift = sum(recent) / len(recent) if recent else 0.0
    # Measured in-sample sign hit rate of the same rule on this simulated series.
    hits = total = 0
    for i in range(10, len(diffs)):
        pred = sum(diffs[i - 10:i])
        if pred == 0 or diffs[i] == 0:
            continue
        total += 1
        hits += (pred > 0) == (diffs[i] > 0)
    return {
        "symbol": sym, "model": "naive_10_tick_momentum_baseline", "last": c[-1],
        "next_estimate": round(c[-1] + drift, 2), "direction": "UP" if drift > 0 else "DOWN" if drift < 0 else "FLAT",
        "in_sample_sign_hit_rate": round(hits / total, 4) if total else None,
        "evaluated_points": total,
        "caveat": "Baseline on simulated random-walk data; expected hit rate ~0.5. Not a forecast, not investment advice.",
    }


def truth_score(sym: str) -> dict:
    with STATE.lock:
        entries = [e for e in STATE.evidence if e["symbol"] == sym][-200:]
    chain = STATE.verify_chain(list(STATE.evidence)[-2000:])
    own_ok = all(make_hash({k: v for k, v in e.items() if k != "hash"}, e["timestamp"]) == e["hash"] for e in entries)
    age = None
    if entries:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(entries[-1]["timestamp"])).total_seconds()
    components = {
        "symbol_entry_hashes_valid": own_ok and bool(entries),
        "recent_chain_links_valid": chain["verified"],
        "fresh_within_5s": age is not None and age <= 5,
        "real_exchange_source": False,  # simulated feed - honestly fails this component
    }
    score = round(100 * sum(components.values()) / len(components), 1)
    return {
        "symbol": sym, "integrity_score": score, "components": components,
        "evidence_entries_checked": len(entries), "last_evidence_age_s": None if age is None else round(age, 3),
        "meaning": "Data-integrity score (hashes, chain, freshness, source). It does NOT measure price correctness.",
    }


def norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def black_scholes(s: float, k: float, t: float, r: float, iv: float) -> dict:
    if t <= 0 or iv <= 0:
        return {"call": round(max(s - k, 0), 2), "put": round(max(k - s, 0), 2), "call_delta": None, "put_delta": None}
    d1 = (math.log(s / k) + (r + iv * iv / 2) * t) / (iv * math.sqrt(t))
    d2 = d1 - iv * math.sqrt(t)
    call = s * norm_cdf(d1) - k * math.exp(-r * t) * norm_cdf(d2)
    put = k * math.exp(-r * t) * norm_cdf(-d2) - s * norm_cdf(-d1)
    return {"call": round(call, 2), "put": round(put, 2), "call_delta": round(norm_cdf(d1), 4), "put_delta": round(norm_cdf(d1) - 1, 4)}


def var_and_drawdown(sym: str = "NIFTY", notional: float = 1_000_000.0, conf: float = 0.95) -> dict:
    c = STATE.closes(sym)
    r = sorted(returns(c))
    idx = max(0, int((1 - conf) * len(r)) - 1)
    var_ret = -r[idx] if r else 0.0
    peak, mdd = c[0], 0.0
    for p in c:
        peak = max(peak, p)
        mdd = max(mdd, (peak - p) / peak)
    return {
        "reference": sym, "notional_inr": notional, "confidence": conf,
        "historical_var_pct": round(var_ret * 100, 4), "historical_var_inr": round(var_ret * notional, 2),
        "horizon": f"1 simulated tick (~{TICK_SECONDS}s)", "max_drawdown_pct": round(mdd * 100, 4),
        "sample_size": len(r),
    }


def safety_flags() -> dict:
    eff = {k: os.environ.get(k, v) for k, v in SAFETY_DEFAULTS.items()}
    eff_ok = all(eff[k] == v for k, v in SAFETY_DEFAULTS.items())
    return {"effective": eff, "matches_required_paper_posture": eff_ok, "broker_client_present": False,
            "order_placement_possible": False}


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
async def _ticker() -> None:
    while True:
        await asyncio.sleep(TICK_SECONDS)
        STATE.tick()


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(_ticker())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="Genesis System3 Premium Dashboard (SIMULATED)", version="2.0.0", lifespan=lifespan)


@app.middleware("http")
async def observe(request: Request, call_next):
    t0 = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        key = getattr(route, "path", None) or request.url.path
        ms = round((time.perf_counter() - t0) * 1000, 2)
        with STATE.lock:
            st = STATE.route_stats.setdefault(key, {"hits": 0, "errors": 0})
            st["hits"] += 1
            st["errors"] += status >= 500
            st["last_status"] = status
            st["last_ms"] = ms
            st["last_utc"] = utcnow()
            STATE.logs.append({"utc": st["last_utc"], "method": request.method, "path": request.url.path, "status": status, "ms": ms})


@app.exception_handler(Exception)
async def on_error(request: Request, exc: Exception):
    rid = uuid.uuid4().hex[:12]
    rec = {"request_id": rid, "path": request.url.path, "error": f"{type(exc).__name__}: {exc}", "utc": utcnow()}
    with STATE.lock:
        STATE.audit.append(rec)
    body = dict(rec, auto_corrected=False, real=False, data_mode=DATA_MODE,
                note="Unhandled error captured and logged to /api/audit. Nothing was auto-corrected.")
    body["hash"] = make_hash(rec, rec["utc"])
    return JSONResponse(status_code=500, content=body)


def add_get(path: str, name: str, handler: Callable, tag: str) -> None:
    app.add_api_route(path, handler, methods=["GET"], name=name, tags=[tag])


# ---- Fallback UI (never a blank page) -------------------------------------
FALLBACK_HTML = """<!doctype html><html><head><meta charset="utf-8"><title>Genesis System3 - recovering UI</title>
<style>body{background:#0a0a0a;color:#eee;font-family:Segoe UI,Arial,sans-serif;padding:32px}
h1{color:#FFD700}.ok{color:#00FF88}.box{border:1px solid #333;border-radius:10px;padding:16px;margin:12px 0;background:#111}
.warn{color:#ff9f43}</style></head><body>
<h1>Genesis System3 Dashboard</h1>
<div class="box warn">Template <code>templates/premium.html</code> is missing or unreadable. Showing a minimal live view and
checking every 2 seconds; the full dashboard loads automatically once the template is back.</div>
<div class="box">Data mode: <b class="warn">SIMULATED</b> &middot; Registered GET routes: <b class="ok" id="rc">...</b></div>
<div class="box" id="mk">Loading market...</div>
<script>
async function poll(){
 try{const t=await (await fetch('/api/ui/template-status')).json(); if(t.data.available){location.reload();return;}}catch(e){}
 try{const r=await (await fetch('/api/routes')).json(); document.getElementById('rc').textContent=r.app_defined_get_routes;}catch(e){}
 try{const m=await (await fetch('/api/market')).json(); const q=m.data.quotes.filter(x=>['NIFTY','BANKNIFTY','RELIANCE'].includes(x.symbol));
  document.getElementById('mk').textContent=q.map(x=>x.symbol+' '+x.price.toFixed(2)).join('  |  ')+'  (hash 0x'+m.hash.slice(0,12)+')';}catch(e){}
}
poll(); setInterval(poll,2000);
</script></body></html>"""


async def ui():
    try:
        html = TEMPLATE_PATH.read_text(encoding="utf-8")
        if "<html" not in html.lower() or len(html) < 200:
            raise ValueError("template incomplete")
        return HTMLResponse(html, headers={"Cache-Control": "no-store", "X-UI-Source": "template"})
    except Exception as exc:  # noqa: BLE001 - deliberate: UI must never be blank
        with STATE.lock:
            STATE.audit.append({"request_id": "ui-fallback", "path": "/ui", "error": f"{type(exc).__name__}: {exc}", "utc": utcnow()})
        return HTMLResponse(FALLBACK_HTML, headers={"Cache-Control": "no-store", "X-UI-Source": "fallback"})


async def template_status():
    ok = TEMPLATE_PATH.is_file()
    return envelope({"available": ok, "path": str(TEMPLATE_PATH.name)}, "ui_template_status")


async def root(request: Request):
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse("/ui")
    return envelope({"service": app.title, "dashboard": "/ui", "routes": "/api/routes", "docs": "/docs"}, "index")


# ---- Core -----------------------------------------------------------------
DOC_PATHS = {"/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"}


async def list_routes():
    with STATE.lock:
        stats = {k: dict(v) for k, v in STATE.route_stats.items()}
    routes = []
    for r in app.routes:
        methods = getattr(r, "methods", None)
        if not methods or "GET" not in methods:
            continue
        st = stats.get(r.path, {})
        last = st.get("last_status")
        status = "NOT_CALLED_YET" if last is None else ("OK" if last < 400 else "CLIENT_ERROR" if last < 500 else "ERROR")
        routes.append({"path": r.path, "name": r.name, "registered": True, "status": status,
                       "hits": st.get("hits", 0), "last_status": last, "doc_route": r.path in DOC_PATHS})
    routes.sort(key=lambda x: x["path"])
    app_defined = [x for x in routes if not x["doc_route"]]
    groups: dict[str, int] = {}
    for x in app_defined:
        g = "/".join(x["path"].split("/")[:3]) or "/"
        groups[g] = groups.get(g, 0) + 1
    data = {"total": len(routes), "app_defined_get_routes": len(app_defined), "groups": groups, "routes": routes}
    env = envelope(data, "route_inventory")
    env.update(total=len(routes), app_defined_get_routes=len(app_defined), routes=routes,
               counting_method="measured from app.routes at request time")
    return env


async def market():
    return envelope({"quotes": [quote(s) for s in SYMBOLS], "count": len(SYMBOLS)}, "market_snapshot")


async def evidence(limit: int = Query(100, ge=1, le=1000), after_seq: int = Query(0, ge=0), symbol: str | None = None):
    with STATE.lock:
        items = [e for e in STATE.evidence if e["seq"] > after_seq and (symbol is None or e["symbol"] == symbol.upper())]
        total, head = len(STATE.evidence), STATE.last_hash
    return envelope({"entries": items[-limit:], "store_size": total, "head_hash": head, "max_retained": EVIDENCE_MAX}, "evidence")


async def history(symbol: str = "NIFTY", points: int = Query(200, ge=10, le=HISTORY_MAX)):
    sym = symbol.upper()
    if sym not in STATE.history:
        return JSONResponse(status_code=404, content=envelope({"error": f"unknown symbol {sym}"}, "error"))
    with STATE.lock:
        h = list(STATE.history[sym])[-points:]
    return envelope({"symbol": sym, "points": [{"t": t, "p": p} for t, p in h]}, "history")


async def depth(symbol: str = "NIFTY", levels: int = Query(5, ge=1, le=20)):
    sym = symbol.upper()
    if sym not in STATE.prices:
        return JSONResponse(status_code=404, content=envelope({"error": f"unknown symbol {sym}"}, "error"))
    p = STATE.prices[sym]
    tick = 0.05 if p < 5000 else 0.5
    r = random.Random(f"{sym}:{STATE.ticks}")
    bids = [{"price": round(p - tick * (i + 1), 2), "qty": r.randint(50, 5000)} for i in range(levels)]
    asks = [{"price": round(p + tick * (i + 1), 2), "qty": r.randint(50, 5000)} for i in range(levels)]
    return envelope({"symbol": sym, "bids": bids, "asks": asks, "note": "Synthetic depth around simulated price."}, "order_book")


async def decision():
    out = []
    for s in sorted(INDICES):
        c = STATE.closes(s)
        r_, m = rsi(c), macd(c)
        sig = "HOLD"
        if r_ is not None and m is not None:
            if m["histogram"] > 0 and r_ < 70:
                sig = "BULLISH_BIAS"
            elif m["histogram"] < 0 and r_ > 30:
                sig = "BEARISH_BIAS"
        out.append({"symbol": s, "research_signal": sig, "rsi14": r_, "macd": m})
    return envelope({"signals": out, "execution": "DISABLED (paper/analyze only)",
                     "rule": "MACD histogram sign gated by RSI14 30/70"}, "decision")


async def pnl():
    return envelope({"realized_inr": 0.0, "unrealized_inr": 0.0, "paper_trades": 0,
                     "note": "No paper ledger is connected to this prototype; values are zero, not estimated."}, "pnl")


async def health():
    with STATE.lock:
        last_age = (datetime.now(timezone.utc) - datetime.fromisoformat(STATE.evidence[-1]["timestamp"])).total_seconds()
        n = len(STATE.evidence)
    return envelope({"status": "ok" if last_age < 10 * TICK_SECONDS else "stale", "uptime_s": round(time.time() - STATE.started, 1),
                     "evidence_entries": n, "last_tick_age_s": round(last_age, 3), "ticks": STATE.ticks,
                     "template_available": TEMPLATE_PATH.is_file(), "safety": safety_flags()}, "health")


async def risk():
    return envelope(var_and_drawdown(), "risk")


async def positions():
    return envelope({"positions": [], "note": "Paper-only prototype; no positions are held or simulated."}, "positions")


async def orders():
    return envelope({"orders": [], "order_placement_possible": False,
                     "note": "This app has no broker client. Zero orders by construction."}, "orders")


# ---- Generated route factories ---------------------------------------------
def sym_market(sym):
    async def h():
        return envelope(quote(sym), "quote")
    return h


def sym_truth(sym):
    async def h():
        q = quote(sym)
        with STATE.lock:
            last = next((e for e in reversed(STATE.evidence) if e["symbol"] == sym), None)
        return envelope({"quote": q, "latest_evidence": last}, "truth")
    return h


def sym_predict(sym):
    async def h():
        return envelope(momentum_baseline(sym), "baseline_prediction")
    return h


def sym_truth_score(sym):
    async def h():
        return envelope(truth_score(sym), "integrity_score")
    return h


def sym_predict_next(sym):
    async def h():
        b = momentum_baseline(sym)
        return envelope({k: b[k] for k in ("symbol", "model", "last", "next_estimate", "direction", "caveat")}, "baseline_next")
    return h


def sym_predict_conf(sym):
    async def h():
        b = momentum_baseline(sym)
        return envelope({"symbol": sym, "calibrated_probability": None, "in_sample_sign_hit_rate": b["in_sample_sign_hit_rate"],
                         "evaluated_points": b["evaluated_points"],
                         "note": "No calibrated confidence exists for a baseline on simulated data; measured hit rate shown instead."}, "baseline_confidence")
    return h


def sym_margin(sym):
    async def h(qty: int = Query(1, ge=1, le=1_000_000)):
        p = STATE.prices[sym]
        rate = 0.12 if sym in INDICES else 0.20
        return envelope({"symbol": sym, "qty": qty, "price": p, "rate": rate, "margin_estimate_inr": round(p * qty * rate, 2),
                         "rule": "flat rate estimate (12% index / 20% equity); not exchange SPAN"}, "margin_estimate")
    return h


def scan_rsi(sym):
    async def h():
        return envelope({"symbol": sym, "rsi14": rsi(STATE.closes(sym))}, "scanner_rsi")
    return h


def scan_macd(sym):
    async def h():
        return envelope({"symbol": sym, **(macd(STATE.closes(sym)) or {"macd": None})}, "scanner_macd")
    return h


def option_strike(strike):
    async def h(underlying: str = OPTION_DEFAULT_UNDERLYING, days: float = Query(7.0, gt=0, le=365),
                iv: float = Query(0.22, gt=0, le=3), rate: float = Query(0.065, ge=0, le=0.5)):
        u = underlying.upper()
        if u not in STATE.prices:
            return JSONResponse(status_code=404, content=envelope({"error": f"unknown underlying {u}"}, "error"))
        s = STATE.prices[u]
        return envelope({"underlying": u, "spot": s, "strike": strike, "days": days, "iv": iv, "rate": rate,
                         "moneyness": "ITM_CALL" if s > strike else "ITM_PUT" if s < strike else "ATM",
                         **black_scholes(s, strike, days / 365, rate, iv), "model": "Black-Scholes (European), theoretical"}, "option_quote")
    return h


def scanner_list(kind):
    async def h(n: int = Query(10, ge=1, le=48)):
        qs = [quote(s) for s in SYMBOLS]
        if kind == "all":
            rows = qs
        elif kind == "top-gainers":
            rows = sorted(qs, key=lambda x: -x["change_pct"])[:n]
        elif kind == "top-losers":
            rows = sorted(qs, key=lambda x: x["change_pct"])[:n]
        elif kind == "breakouts":
            rows = [q for q in qs if q["price"] >= q["high"]]
        elif kind in ("52w-high", "52w-low"):
            # Only the retained simulated window exists; label it as such.
            out = []
            for s in SYMBOLS:
                c = STATE.closes(s)
                if (kind == "52w-high" and c[-1] >= max(c)) or (kind == "52w-low" and c[-1] <= min(c)):
                    out.append({"symbol": s, "price": c[-1], "window_points": len(c)})
            return envelope({"rows": out, "window": "retained simulated history only (NOT 52 weeks)"}, f"scanner_{kind}")
        elif kind == "volume-shockers":
            return envelope({"rows": [], "note": "Simulator produces no volume series; scanner intentionally empty."}, "scanner_volume")
        else:
            rows = []
        return envelope({"rows": rows, "count": len(rows)}, f"scanner_{kind}")
    return h


def system_route(kind):
    async def h():
        if kind == "kill-switch":
            data = {"live_trading": "DISABLED", "kill_switch_engaged": True, "reason": "permanent paper/analyze posture", **safety_flags()}
        elif kind == "settings":
            data = {"data_mode": DATA_MODE, "tick_seconds": TICK_SECONDS, "seed": SEED, "evidence_max": EVIDENCE_MAX,
                    "template": TEMPLATE_PATH.name, "safety": safety_flags()}
        elif kind == "logs":
            with STATE.lock:
                data = {"recent_requests": list(STATE.logs)[-100:]}
        elif kind == "metrics":
            with STATE.lock:
                hits = sum(v["hits"] for v in STATE.route_stats.values())
                errs = sum(v["errors"] for v in STATE.route_stats.values())
                data = {"requests": hits, "server_errors": errs, "routes_called": len(STATE.route_stats),
                        "evidence_entries": len(STATE.evidence), "ticks": STATE.ticks, "uptime_s": round(time.time() - STATE.started, 1)}
        elif kind == "audit":
            with STATE.lock:
                data = {"errors": list(STATE.audit)}
        elif kind == "hash-chain":
            data = STATE.verify_chain()
        elif kind == "var":
            data = var_and_drawdown()
        elif kind == "drawdown":
            d = var_and_drawdown()
            data = {k: d[k] for k in ("reference", "max_drawdown_pct", "sample_size")}
        else:
            data = {}
        return envelope(data, kind)
    return h


async def truth_proof(id: int):  # noqa: A002 - path name from spec
    with STATE.lock:
        e = next((x for x in STATE.evidence if x["seq"] == id), None)
        oldest = STATE.evidence[0]["seq"] if STATE.evidence else None
    if e is None:
        return JSONResponse(status_code=404, content=envelope({"error": f"evidence seq {id} not retained", "oldest_retained_seq": oldest}, "error"))
    body = {k: v for k, v in e.items() if k != "hash"}
    recomputed = make_hash(body, e["timestamp"])
    return envelope({"entry": e, "recomputed_hash": recomputed, "hash_matches": recomputed == e["hash"]}, "evidence_proof")


async def fault():
    raise RuntimeError("intentional fault for exception-handler verification")


# ---- Registration ----------------------------------------------------------
add_get("/", "root", root, "core")
add_get("/ui", "ui", ui, "core")
for _p, _h in [("/api/routes", list_routes), ("/api/market", market), ("/api/evidence", evidence),
               ("/api/decision", decision), ("/api/pnl", pnl), ("/api/health", health), ("/api/risk", risk),
               ("/api/positions", positions), ("/api/orders", orders), ("/api/history", history),
               ("/api/depth", depth), ("/api/ui/template-status", template_status)]:
    add_get(_p, _p.strip("/").replace("/", "_").replace("-", "_"), _h, "core")

for _s in SYMBOLS:
    _k = _s.lower()
    add_get(f"/api/market/{_s}", f"market_{_k}", sym_market(_s), "market")
    add_get(f"/api/truth/{_s}", f"truth_{_k}", sym_truth(_s), "truth")
    add_get(f"/api/predict/{_s}", f"predict_{_k}", sym_predict(_s), "predict")
    add_get(f"/api/truth/score/{_s}", f"truth_score_{_k}", sym_truth_score(_s), "truth")
    add_get(f"/api/predict/next/{_s}", f"predict_next_{_k}", sym_predict_next(_s), "predict")
    add_get(f"/api/predict/confidence/{_s}", f"predict_conf_{_k}", sym_predict_conf(_s), "predict")
    add_get(f"/api/margin/{_s}", f"margin_{_k}", sym_margin(_s), "risk")

for _k in ["all", "top-gainers", "top-losers", "breakouts", "52w-high", "52w-low", "volume-shockers"]:
    add_get("/api/scanner" if _k == "all" else f"/api/scanner/{_k}", f"scanner_{_k.replace('-', '_')}", scanner_list(_k), "scanner")
for _s in SCANNER_SYMBOLS:
    add_get(f"/api/scanner/rsi/{_s}", f"scanner_rsi_{_s.lower()}", scan_rsi(_s), "scanner")
    add_get(f"/api/scanner/macd/{_s}", f"scanner_macd_{_s.lower()}", scan_macd(_s), "scanner")

for _st in STRIKES:
    add_get(f"/api/option-chain/{_st}", f"option_chain_{_st}", option_strike(_st), "options")

add_get("/api/truth/proof/{id}", "truth_proof", truth_proof, "truth")
for _k in ["kill-switch", "settings", "logs", "metrics", "audit", "hash-chain", "var", "drawdown"]:
    add_get(f"/api/{_k}", _k.replace("-", "_"), system_route(_k), "system")

if ENABLE_FAULT_ROUTE:
    add_get("/api/_fault", "fault", fault, "test")
