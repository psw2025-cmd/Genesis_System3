"""
Genesis System3 — Yahoo Finance Fallback Proof
===============================================
Proves the yfinance fallback data path works for index spot prices.
Uses urllib only (no pandas dependency) to fetch yfinance JSON feed.

Writes proof to:
  reports/latest/external_data_yahoo/yahoo_data_summary.json

Used by gate_data_automation() to clear 'external_yahoo_fallback_proof_missing' warning.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "reports" / "latest" / "external_data_yahoo"
OUT.mkdir(parents=True, exist_ok=True)

TICKERS = {
    "NIFTY50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
}

BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"


def fetch_yahoo(ticker: str, timeout: int = 15) -> dict:
    start = time.time()
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}?interval=1d&range=5d"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(100000).decode("utf-8", errors="replace")
            ms = int((time.time() - start) * 1000)
            data = json.loads(raw)
            result_data = data.get("chart", {}).get("result", [{}])[0]
            meta = result_data.get("meta", {})
            closes = result_data.get("indicators", {}).get("quote", [{}])[0].get("close", [])
            last_close = next((c for c in reversed(closes) if c is not None), None)
            return {
                "ticker": ticker,
                "ok": True,
                "latency_ms": ms,
                "last_close": last_close,
                "currency": meta.get("currency"),
                "exchange": meta.get("exchangeName"),
                "data_points": len([c for c in closes if c is not None]),
            }
    except urllib.error.HTTPError as e:
        return {"ticker": ticker, "ok": False, "error": f"HTTP {e.code}: {e.reason}", "latency_ms": None}
    except Exception as e:
        return {"ticker": ticker, "ok": False, "error": str(e)[:200], "latency_ms": None}


def run_proof() -> dict:
    started = datetime.now(timezone.utc).isoformat()
    print("[YahooFallbackProof] Testing yfinance JSON API ...")

    results = {}
    for name, ticker in TICKERS.items():
        r = fetch_yahoo(ticker)
        results[name] = r
        if r["ok"]:
            print(
                f"  {name} ({ticker}): close={r.get('last_close')} | {r.get('data_points')} days | {r.get('latency_ms')}ms"
            )
        else:
            print(f"  {name} ({ticker}): FAIL — {r.get('error')}")

    ok_count = sum(1 for r in results.values() if r["ok"])
    proof_pass = ok_count >= 1  # At least 1 index data available

    warnings = []
    blockers = []
    if ok_count == 0:
        blockers.append("all_yahoo_tickers_failed")
    elif ok_count < len(TICKERS):
        warnings.append(f"only_{ok_count}_of_{len(TICKERS)}_tickers_returned_data")

    summary = {
        "generated_utc": started,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "gate": "external_data_yahoo_fallback",
        "pass": proof_pass,
        "status": "PASS" if proof_pass else "FAIL",
        "tickers_tested": len(TICKERS),
        "tickers_ok": ok_count,
        "yahoo_api_reachable": ok_count > 0,
        "results": results,
        "blockers": blockers,
        "warnings": warnings,
        "note": (
            "yfinance provides NIFTY/BANKNIFTY spot prices as P5 fallback in DataSourceManager. "
            "Does NOT provide Indian options data (IV, OI, Greeks). NSE bhavcopy is primary OI source."
        ),
    }

    (OUT / "yahoo_data_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n[YahooFallbackProof] Result: {'PASS' if proof_pass else 'FAIL'} ({ok_count}/{len(TICKERS)} tickers)")
    print(f"  Report: {OUT / 'yahoo_data_summary.json'}")
    return summary


if __name__ == "__main__":
    result = run_proof()
    sys.exit(0 if result.get("pass") else 1)
