#!/usr/bin/env python3
"""Cloud-only, fail-closed read-only checks; synthetic PAPER replay is NOT broker proof."""
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def emit(name, status, **fields):
    record = {"check": name, "status": status, **fields}
    line = json.dumps(record, sort_keys=True)
    print(line, flush=True)
    output = os.getenv("CLOUD_VERIFY_EVIDENCE")
    if output:
        with open(output, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")


def guard():
    expected = {"PAPER_MODE": "1", "LIVE_ORDER_AUTHORITY": "0", "REAL_BROKER_ORDERS": "0"}
    bad = {key: os.getenv(key) for key, value in expected.items() if os.getenv(key) != value}
    if bad:
        emit("ci_safety_environment", "FAIL", mismatched_keys=sorted(bad))
        raise RuntimeError("CI safety settings do not match required PAPER-only values")
    emit("ci_safety_environment", "PASS")


def dhan_orders():
    token = os.getenv("DHAN_ACCESS_TOKEN", "")
    client_id = os.getenv("DHAN_CLIENT_ID", "")
    if not token or not client_id:
        emit("dhan_orders_get", "NOT_VERIFIED", reason="missing GitHub secrets", missing_names=[name for name, value in (("DHAN_ACCESS_TOKEN", token), ("DHAN_CLIENT_ID", client_id)) if not value])
        return False
    request = Request(
        "https://api.dhan.co/v2/orders",
        headers={"access-token": token, "client-id": client_id, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=15) as response:
            body = response.read(2_000_001)
            if len(body) > 2_000_000:
                raise ValueError("oversized response")
            payload = json.loads(body)
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        emit("dhan_orders_get", "NOT_VERIFIED", error_type=type(exc).__name__)
        return False
    # Dhan may return an error object instead of a list. Never treat that as zero orders.
    if not isinstance(payload, list):
        emit("dhan_orders_get", "NOT_VERIFIED", reason="response is not an order list")
        return False
    count = len(payload)
    emit("dhan_orders_get", "PASS" if count == 0 else "FAIL",
         order_count=count, response_sha256=hashlib.sha256(body).hexdigest(),
         scope="Dhan GET /v2/orders response; not lifetime broker order-zero proof")
    return count == 0


def paper_lifecycle():
    # Calls repository's synthetic replay only. No HTTP or broker SDK imports in this path.
    from dashboard.backend.paper_market_replay import MarketTick, replay_paper_buy
    t = datetime(2026, 11, 7, 9, 15, tzinfo=timezone.utc)
    created = {"id": "CLOUD_VERIFY_SYNTHETIC_001", "state": "CREATED", "mode": "SYNTHETIC_PAPER_ONLY"}
    ack = {"id": created["id"], "state": "ACK", "mode": created["mode"]}
    ticks = [MarketTick(t.isoformat(), 99.0, 100.0, 1),
             MarketTick((t + timedelta(seconds=1)).isoformat(), 99.0, 100.0, 1)]
    fill = replay_paper_buy(ticks, qty=2, capital_limit=50000)
    ok = fill["status"] == "PAPER_FILLED" and fill["filled_qty"] == 2 and all(
        item["mode"] == "SYNTHETIC_PAPER_FILL_NOT_BROKER" for item in fill["fills"]
    )
    logged = {"id": created["id"], "state": "LOG", "fill_count": len(fill["fills"])}
    emit("synthetic_paper_lifecycle", "PASS" if ok else "FAIL",
         states=[created["state"], ack["state"], "FILLED (PAPER)" if ok else "BLOCKED", logged["state"]],
         evidence="DETERMINISTIC_SYNTHETIC_REPLAY_NOT_INTEGRATED_PAPER_LEDGER",
         broker_calls=0)
    return ok


def main():
    try:
        guard()
        paper_ok = paper_lifecycle()
        dhan_ok = dhan_orders()
    except Exception as exc:
        emit("cloud_verify_python", "FAIL", error_type=type(exc).__name__, message=str(exc)[:120])
        return 1
    return 0 if paper_ok and dhan_ok else 1


if __name__ == "__main__":
    sys.exit(main())
