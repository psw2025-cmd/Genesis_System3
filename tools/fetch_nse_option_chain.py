#!/usr/bin/env python3
"""
Fetch NSE NIFTY (or other index) option-chain JSON locally.

Uses hardened session + option-chain-v3 API (contract-info for expiry).

Usage:
  python tools/fetch_nse_option_chain.py
  python tools/fetch_nse_option_chain.py --symbol BANKNIFTY --out state/nifty_oc.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.data.nse_session import NSEFetchError, fetch_option_chain_json  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch NSE option chain JSON")
    parser.add_argument("--symbol", default="NIFTY", help="Index symbol (default: NIFTY)")
    parser.add_argument(
        "--expiry",
        default=None,
        help="Expiry DD-Mon-YYYY (default: nearest from contract-info)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Save JSON to path (default: state/nse_oc_<symbol>_<ts>.json)",
    )
    args = parser.parse_args()

    symbol = args.symbol.upper()
    try:
        data = fetch_option_chain_json(symbol, expiry=args.expiry)
    except NSEFetchError as exc:
        print(f"FAIL [{symbol}]: {exc}", file=sys.stderr)
        return 1

    records = data.get("records", {})
    spot = records.get("underlyingValue")
    rows = len(records.get("data") or [])
    expiries = records.get("expiryDates") or []
    print(f"OK [{symbol}] spot={spot} strikes={rows} expiries={len(expiries)}")

    out = args.out
    if not out:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = str(ROOT / "state" / f"nse_oc_{symbol}_{ts}.json")
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
