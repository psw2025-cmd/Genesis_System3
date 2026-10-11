"""Reproduce the 1 October seven-day exploratory equity PAPER prediction.

Run from the repository root with an immutable source directory and a new
output directory.  This issues no broker order and claims no calibrated edge.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from scripts.equity_forward_prediction import GENESIS_HASH, build_prediction


FILES = {
    "cash": "cm_20261001.zip",
    "company": "EQUITY_L.csv",
    "etf": "eq_etfseclist.csv",
    "actions": "corporate_actions.json",
    "index": "index_close_20261001.csv",
    "holiday_calendar": "trading_holidays.json",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--model-spec", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--issued-at", required=True)
    args = parser.parse_args()

    receipt_rows = json.loads((args.source_dir / "receipts.json").read_text())
    receipts = {row["file"]: row for row in receipt_rows}
    missing = set(FILES.values()) - set(receipts)
    if missing:
        raise ValueError(f"Missing source receipts: {sorted(missing)}")
    equity_roles = ("cash", "company", "etf", "actions")
    result = build_prediction(
        equity_sources={role: (args.source_dir / FILES[role]).read_bytes() for role in equity_roles},
        equity_receipts={role: receipts[FILES[role]] for role in equity_roles},
        index_raw=(args.source_dir / FILES["index"]).read_bytes(),
        index_receipt=receipts[FILES["index"]],
        holiday_raw=(args.source_dir / FILES["holiday_calendar"]).read_bytes(),
        holiday_receipt=receipts[FILES["holiday_calendar"]],
        model_spec_raw=args.model_spec.read_bytes(),
        issued_at=args.issued_at,
        previous_event_hash=GENESIS_HASH,
        now=datetime.now(timezone.utc),
    )
    args.output_dir.mkdir(parents=True, exist_ok=False)
    output = args.output_dir / "2026-10-01_equity_forward_prediction.json"
    raw = (json.dumps(result, indent=2, allow_nan=False) + "\n").encode()
    output.write_bytes(raw)
    print(json.dumps({
        "file": str(output),
        "file_sha256": sha256(raw).hexdigest(),
        "event_hash": result["event_hash"],
        "prediction_id": result["prediction_id"],
        "symbol": result["prediction"]["symbol"],
        "entry_reference_close": result["prediction"]["entry_reference_close"],
        "due_session_date": result["due_session_date"],
        "counts": result["counts"],
        "orders_allowed": result["safety"]["orders_allowed"],
    }, indent=2))


if __name__ == "__main__":
    main()
