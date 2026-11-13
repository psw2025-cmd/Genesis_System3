"""One-shot NSE/Dhan read-only check; no renewal, orders or secret output."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
IST = ZoneInfo("Asia/Kolkata")


def main():
    now = datetime.now(timezone.utc)
    result = {"utc": now.isoformat(), "ist": now.astimezone(IST).isoformat(),
              "label": "UNVERIFIED", "orders_called": False, "token_renewal": False}
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    try:
        # Official JSON APIs only: never scrape the NSE website or bypass a block.
        calendar = session.get("https://www.nseindia.com/api/holiday-master?type=trading", timeout=15)
        result["nse_calendar_http"] = calendar.status_code
        result["nse_calendar_available"] = False
        if calendar.status_code == 200:
            result["nse_calendar_packet"] = calendar.json()
            result["nse_calendar_available"] = True
        r = session.get("https://www.nseindia.com/api/marketStatus", timeout=15)
        result["nse_http"] = r.status_code
        if r.status_code == 200:
            data = r.json()
            result["nse"] = [{k: row.get(k) for k in ("market", "marketStatus", "tradeDate", "index", "last")}
                             for row in data.get("marketState", []) if row.get("market") == "Capital Market"]
    except Exception as exc:
        result["nse_error"] = type(exc).__name__
    # Load existing credentials only; never invoke the adapter's renewal path.
    load_dotenv(ROOT / ".secrets/dhan.env", override=False)
    token, client = os.getenv("DHAN_ACCESS_TOKEN", ""), os.getenv("DHAN_CLIENT_ID", "")
    if not token or not client:
        result["dhan"] = {"status": "AUTH_UNAVAILABLE"}
    else:
        try:
            r = requests.post("https://api.dhan.co/v2/marketfeed/quote",
                              headers={"access-token": token, "client-id": client},
                              json={"IDX_I": [13]}, timeout=15)
            result["dhan_http"] = r.status_code
            if r.status_code == 200:
                body = r.json()
                quote = body.get("data", {}).get("IDX_I", {}).get("13", {})
                result["dhan"] = {"status": body.get("status"), "instrument": "NIFTY 50 / IDX_I / 13",
                                  "last_price": quote.get("last_price"),
                                  "last_trade_time": quote.get("last_trade_time")}
                if not quote:
                    result["dhan"]["status"] = "NO_QUOTE"
            else:
                result["dhan"] = {"status": "AUTH_OR_UPSTREAM_ERROR", "retry": "STOPPED; no token renewal"}
        except Exception as exc:
            result["dhan"] = {"status": "REQUEST_FAILED", "error_type": type(exc).__name__}
    received = datetime.now(timezone.utc)
    result["received_utc"] = received.isoformat()
    result["received_ist"] = received.astimezone(IST).isoformat()
    for source, value, fmt in (
        ("nse", (result.get("nse") or [{}])[0].get("tradeDate"), "%d-%b-%Y %H:%M"),
        ("dhan", result.get("dhan", {}).get("last_trade_time"), "%d/%m/%Y %H:%M:%S"),
    ):
        try:
            source_time = datetime.strptime(value, fmt).replace(tzinfo=IST)
            age = (received - source_time).total_seconds()
            result[source + "_age_s"] = round(age, 3)
            result[source + "_freshness"] = "FRESH" if -5 <= age <= 60 else "STALE_OR_CLOCK_MISMATCH"
        except (ValueError, TypeError):
            result[source + "_freshness"] = "UNKNOWN"
    # Transport success alone never certifies live data or clock synchronization.
    result["next"] = "Check source timestamp ages, same-instrument parity and independent clock evidence before LIVE."
    out = ROOT / "reports" / "market_truth" / now.strftime("%Y%m%dT%H%M%SZ")
    out.mkdir(parents=True, exist_ok=False)
    (out / "source_observation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "nse_calendar_packet"}))


if __name__ == "__main__":
    main()
