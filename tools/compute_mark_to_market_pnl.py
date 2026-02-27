"""Compute mark-to-market P&L from ledger and market snapshot.

Reads:
  - `storage/live/live_orders_ledger.csv` (ledger of orders)
  - `storage/market_snapshot.json` (optional) or `storage/live/market_snapshot.json`

Writes:
  - `logs/inspector/mtm_pnl_<timestamp>.csv` containing per-position MTM

Behavior:
  - For each FILLED order (status or broker_status containing 'FILLED'),
    attempts to find a mark price in the snapshot. It looks for option keys
    like `UNDERLYING_STRIKE_TYPE` (e.g. `NIFTY_18000_CE`) then falls back to
    the underlying price (e.g. `NIFTY`). If no price is found, the row is
    marked as 'price_missing'.
  - P&L per order = (mark_price - entry_price) * qty  (qty sign matters)
  - Aggregates P&L per instrument key and prints a concise table.

Usage:
  .\venv\Scripts\python.exe tools\compute_mark_to_market_pnl.py
  Options: --ledger, --snapshot, --out
"""

import csv
import json
from pathlib import Path
from datetime import datetime
import argparse
from collections import defaultdict


ROOT = Path(__file__).resolve().parents[1]
LEDGER_DEFAULT = ROOT / "storage" / "live" / "live_orders_ledger.csv"
SNAPSHOT_CANDIDATES = [
    ROOT / "storage" / "market_snapshot.json",
    ROOT / "storage" / "live" / "market_snapshot.json",
]
INSPECTOR_DIR = ROOT / "logs" / "inspector"
INSPECTOR_DIR.mkdir(parents=True, exist_ok=True)


def load_snapshot(path: Path):
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def read_ledger(path: Path):
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def find_mark_price(snapshot: dict, underlying: str, strike: str, option_type: str):
    # Try option-specific key patterns, then underlying
    keys_to_try = []
    if underlying:
        u = underlying.upper()
        if strike and option_type:
            keys_to_try.append(f"{u}_{strike}_{option_type.upper()}")
            keys_to_try.append(f"{u}_{strike}{option_type.upper()}")
            keys_to_try.append(f"{u}{strike}{option_type.upper()}")
        keys_to_try.append(u)

    for k in keys_to_try:
        if k in snapshot:
            try:
                return float(snapshot[k])
            except Exception:
                continue
    # try lowercase keys as fallback
    for k, v in snapshot.items():
        if k.upper() in keys_to_try:
            try:
                return float(v)
            except Exception:
                continue
    return None


def compute_mtm(ledger_rows, snapshot):
    per_order = []
    per_instrument = defaultdict(lambda: {"qty": 0.0, "pnl": 0.0, "notional": 0.0, "count": 0})

    for r in ledger_rows:
        status = (r.get("status") or r.get("broker_status") or "").upper()
        if "FILLED" not in status:
            continue

        underlying = (r.get("underlying") or "").strip()
        strike = (r.get("strike") or "").strip()
        option_type = (r.get("option_type") or "").strip()

        try:
            entry_price = float(r.get("entry_price") or 0.0)
        except Exception:
            entry_price = 0.0
        try:
            qty = float(r.get("qty") or 0.0)
        except Exception:
            qty = 0.0

        mark_price = find_mark_price(snapshot, underlying, strike, option_type)

        if mark_price is None:
            pnl = None
            notional = entry_price * qty
        else:
            pnl = (mark_price - entry_price) * qty
            notional = mark_price * qty

        # instrument key for aggregation
        inst_key = None
        if underlying and strike and option_type:
            inst_key = f"{underlying}_{strike}_{option_type}".upper()
        elif underlying:
            inst_key = underlying.upper()
        else:
            inst_key = "UNKNOWN"

        per_order.append(
            {
                "local_order_id": r.get("local_order_id") or r.get("id") or "",
                "instrument": inst_key,
                "entry_price": entry_price,
                "qty": qty,
                "mark_price": mark_price,
                "pnl": pnl,
                "status": status,
                "timestamp": r.get("last_update_ts") or r.get("timestamp") or "",
            }
        )

        if pnl is not None:
            per_instrument[inst_key]["qty"] += qty
            per_instrument[inst_key]["pnl"] += pnl
            per_instrument[inst_key]["notional"] += notional
            per_instrument[inst_key]["count"] += 1

    return per_order, per_instrument


def write_csv(out_path: Path, rows):
    fieldnames = ["local_order_id", "instrument", "entry_price", "qty", "mark_price", "pnl", "status", "timestamp"]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            # convert None to empty string
            rr = {k: ("" if r.get(k) is None else r.get(k)) for k in fieldnames}
            w.writerow(rr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=str, default=str(LEDGER_DEFAULT))
    parser.add_argument("--snapshot", type=str, default="")
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args()

    ledger_path = Path(args.ledger)
    snapshot_path = Path(args.snapshot) if args.snapshot else None

    if snapshot_path is None or not snapshot_path.exists():
        # try defaults
        for p in SNAPSHOT_CANDIDATES:
            if p.exists():
                snapshot_path = p
                break

    snapshot = load_snapshot(snapshot_path) if snapshot_path else {}

    ledger_rows = read_ledger(ledger_path)

    per_order, per_instrument = compute_mtm(ledger_rows, snapshot)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path(args.out) if args.out else (INSPECTOR_DIR / f"mtm_pnl_{ts}.csv")

    write_csv(out_path, per_order)

    # Print summary table
    print("MTM summary written to:", out_path)
    print("Per-instrument summary:")
    print(f"{'Instrument':30} {'Qty':>10} {'P&L':>15} {'Notional':>15} {'Count':>6}")
    total_pnl = 0.0
    for inst, v in per_instrument.items():
        print(f"{inst:30} {v['qty']:10.2f} {v['pnl']:15.2f} {v['notional']:15.2f} {v['count']:6d}")
        total_pnl += v["pnl"]
    print("-" * 80)
    print(f"{'TOTAL':30} {'':10} {total_pnl:15.2f}")


if __name__ == "__main__":
    import argparse

    main()
