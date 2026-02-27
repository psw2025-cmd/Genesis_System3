"""Live visualizer for filled orders (quick view).

Usage:
  .\venv\Scripts\python.exe tools\visualize_live_fills.py --live

What it shows:
  - A live-updating Matplotlib window plotting cumulative filled notional
    (sum of entry_price * qty for orders with status containing 'FILLED').

Notes:
  - This is a quick visual aid. For real mark-to-market P&L you need a
    market price feed; see the TODOs in the script to integrate a price API.
"""

import csv
import time
from pathlib import Path
from datetime import datetime
import argparse

try:
    import matplotlib.pyplot as plt
except Exception as e:
    print("matplotlib is required. Install with: pip install matplotlib")
    raise


LEDGER = Path(__file__).resolve().parents[1] / "storage" / "live" / "live_orders_ledger.csv"


def read_ledger(path: Path):
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def parse_ts(s: str):
    if not s:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def compute_cumulative_filled(rows):
    # Rows expected to have at least: timestamp, entry_price, qty, status
    entries = []
    for r in rows:
        status = (r.get("status") or r.get("broker_status") or "").upper()
        if "FILLED" in status:
            ts = parse_ts(r.get("last_update_ts") or r.get("timestamp") or "")
            try:
                price = float(r.get("entry_price") or 0)
            except Exception:
                price = 0.0
            try:
                qty = float(r.get("qty") or 0)
            except Exception:
                qty = 0.0
            entries.append((ts or datetime.now(), price * qty))
    entries.sort(key=lambda x: x[0])
    times = [t for t, v in entries]
    vals = []
    s = 0.0
    for _, v in entries:
        s += v
        vals.append(s)
    return times, vals


def live_plot(poll_interval=5.0):
    plt.ion()
    fig, ax = plt.subplots(figsize=(9, 5))
    (line,) = ax.plot([], [], "-o")
    ax.set_title("Cumulative Filled Notional (live)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Notional (entry_price * qty)")

    try:
        while True:
            rows = read_ledger(LEDGER)
            times, vals = compute_cumulative_filled(rows)
            if times:
                ax.clear()
                ax.plot(times, vals, "-o")
                ax.set_title("Cumulative Filled Notional (live)")
                ax.set_xlabel("Time")
                ax.set_ylabel("Notional (entry_price * qty)")
                fig.autofmt_xdate()
                ax.grid(True)
                plt.pause(0.01)
            else:
                ax.clear()
                ax.text(0.5, 0.5, "No FILLED orders found in ledger", ha="center")
                plt.pause(0.01)
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("\nStopped.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run live poll/plot loop")
    parser.add_argument("--interval", type=float, default=5.0, help="Poll interval seconds")
    args = parser.parse_args()

    if not LEDGER.exists():
        print("Ledger not found at", LEDGER)
        return

    if args.live:
        live_plot(poll_interval=args.interval)
    else:
        rows = read_ledger(LEDGER)
        times, vals = compute_cumulative_filled(rows)
        if not times:
            print("No FILLED orders found in ledger")
            return
        plt.plot(times, vals, "-o")
        plt.title("Cumulative Filled Notional")
        plt.xlabel("Time")
        plt.ylabel("Notional")
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    main()
