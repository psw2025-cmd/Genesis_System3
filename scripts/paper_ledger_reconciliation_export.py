"""Read-only, hash-verified and broker-free date-wise PAPER ledger receipt.

Exports CSV and JSON from the immutable-sequence SQLite master event ledger.
It NEVER substitutes simulated fills or estimated charges for broker truth.
The manifest is published last and contains hashes independently read back.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dashboard.backend.autonomous_paper_core import (
    FILL_MODE, MasterPaperLedger, PaperEvidenceError, estimate_costed_paper_pnl,
)

FIELDS = (
    "position_id", "status", "underlying", "option_type", "strike", "qty",
    "entry_timestamp", "exit_timestamp_utc", "exit_day_utc", "entry_price",
    "exit_price", "estimated_net_pnl_inr", "paper_fill_mode",
    "pnl_verification_status", "outcome_validation_status", "legacy_unverified",
)


def _timestamp_day(value: Any) -> str:
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return "UNVERIFIED_DATE"
    if dt.tzinfo is None or dt.utcoffset() is None:
        return "UNVERIFIED_DATE"
    return dt.astimezone(timezone.utc).date().isoformat()


def _csv_text(rows: list[dict], fields: tuple[str, ...]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def generate_receipt(path: Path | str) -> tuple[dict, str, str]:
    """Fail closed on missing/corrupt ledger; report contains no broker secrets."""
    file = Path(path)
    if not file.is_file():
        raise PaperEvidenceError("PAPER_MASTER_LEDGER_MISSING")
    ledger = MasterPaperLedger(file)
    with ledger._db() as db:
        db.execute("BEGIN")
        events = ledger._verified_events(db)
        state = ledger._project(events)
        latest = db.execute("SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
    rows: list[dict] = []
    days = defaultdict(lambda: {"closed_trades": 0, "simulated_net_pnl_inr": 0.0,
                               "independent_source_attested_outcomes": 0})
    for trade in state["open_positions"] + state["closed_positions"]:
        legacy = trade.get("legacy_unverified") is True
        closed = trade.get("status") == "CLOSED"
        tid = str(trade["position_id"])
        outcome = state["outcomes"].get(tid) or {}
        net = None
        if closed and not legacy:
            if trade.get("paper_fill_mode") != FILL_MODE:
                raise PaperEvidenceError("PAPER_FILL_PROVENANCE_MISMATCH")
            actual = trade.get("realized_pnl")
            if isinstance(actual, bool) or not isinstance(actual, (int, float)):
                raise PaperEvidenceError("MISSING_PAPER_COSTED_NET_PNL")
            if not math.isfinite(float(actual)):
                raise PaperEvidenceError("NONFINITE_PAPER_COSTED_NET_PNL")
            net = estimate_costed_paper_pnl(
                float(trade["entry_price"]), float(trade["exit_price"]), int(trade["qty"])
            )
            if abs(net - float(actual)) > 0.011:
                raise PaperEvidenceError("PAPER_NET_PNL_RECONCILIATION_FAILED")
        exit_at = trade.get("exit_timestamp_utc") if closed else None
        day = _timestamp_day(exit_at) if exit_at else "UNVERIFIED_DATE"
        rows.append({
            "position_id": tid, "status": trade.get("status", "UNKNOWN"),
            "underlying": trade.get("underlying"), "option_type": trade.get("option_type"),
            "strike": trade.get("strike"), "qty": trade.get("qty"),
            "entry_timestamp": trade.get("timestamp"),
            "exit_timestamp_utc": exit_at, "exit_day_utc": day,
            "entry_price": trade.get("entry_price"),
            "exit_price": trade.get("exit_price") if closed else None,
            "estimated_net_pnl_inr": net,
            "paper_fill_mode": trade.get("paper_fill_mode"),
            "pnl_verification_status": trade.get("pnl_verification_status")
                if closed else "OPEN_UNREALIZED_NOT_RECONCILED",
            "outcome_validation_status": outcome.get("validation_status", "NOT_VERIFIED"),
            "legacy_unverified": legacy,
        })
        if closed and net is not None and day != "UNVERIFIED_DATE":
            bucket = days[day]
            bucket["closed_trades"] += 1
            bucket["simulated_net_pnl_inr"] += net
            bucket["independent_source_attested_outcomes"] += int(
                outcome.get("validation_status") == "SOURCE_ATTESTED"
            )
    for bucket in days.values():
        bucket["simulated_net_pnl_inr"] = round(bucket["simulated_net_pnl_inr"], 2)
    rows.sort(key=lambda x: (x["exit_day_utc"], x["position_id"]))
    daily_rows = [{"exit_day_utc": day, **data} for day, data in sorted(days.items())]
    if state["legacy_unverified"]:
        status = "BLOCKED_LEGACY_NOT_VERIFIED"
    elif not events:
        status = "NO_TRADES_NOT_VERIFIED"
    else:
        status = "PASS_HASH_VERIFIED_PAPER_SIMULATION_ONLY"
    csv_text = _csv_text(rows, FIELDS)
    daily_text = _csv_text(daily_rows, (
        "exit_day_utc", "closed_trades", "simulated_net_pnl_inr",
        "independent_source_attested_outcomes",
    ))
    manifest = {
        "schema": "genesis-paper-ledger-dated-reconciliation-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "ledger_event_count": len(events),
        "ledger_hash_chain_verified": state["verified_hash_chain"],
        "ledger_tip_hash": latest[0] if latest else None,
        "open_positions": len(state["open_positions"]),
        "closed_positions": len(state["closed_positions"]),
        "legacy_unverified": state["legacy_unverified"],
        "simulation_only": True,
        "real_broker_orders_count_verified": False,
        "real_broker_fills_verified": False,
        "cost_method": "ESTIMATED_CHARGES_AND_SLIPPAGE_NOT_ACTUAL_BROKER_COSTS",
        "independent_market_outcome_count": sum(
            int(x.get("validation_status") == "SOURCE_ATTESTED")
            for x in state["outcomes"].values()
        ),
        "trades_csv_sha256": hashlib.sha256(csv_text.encode("utf-8")).hexdigest(),
        "daily_csv_sha256": hashlib.sha256(daily_text.encode("utf-8")).hexdigest(),
    }
    return manifest, csv_text, daily_text


def _atomic(path: Path, content: str) -> None:
    fd, temp_name = tempfile.mkstemp(prefix=".paper-receipt-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def publish(path: Path | str, target: Path | str) -> dict:
    receipt, trades, daily = generate_receipt(path)
    folder = Path(target)
    folder.mkdir(parents=True, exist_ok=True)
    _atomic(folder / "paper_trades.csv", trades)
    _atomic(folder / "paper_daily.csv", daily)
    for name, digest in (("paper_trades.csv", receipt["trades_csv_sha256"]),
                         ("paper_daily.csv", receipt["daily_csv_sha256"])):
        if hashlib.sha256((folder / name).read_bytes()).hexdigest() != digest:
            raise PaperEvidenceError("PAPER_RECEIPT_WRITE_READBACK_MISMATCH")
    _atomic(folder / "paper_receipt.json",
            json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n")
    if json.loads((folder / "paper_receipt.json").read_text()) != receipt:
        raise PaperEvidenceError("PAPER_MANIFEST_WRITE_READBACK_MISMATCH")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = publish(args.ledger, args.out)
    except (PaperEvidenceError, OSError, ValueError, KeyError, TypeError) as exc:
        # Do not leak paths, SQL statements or user-supplied payloads.
        print("PAPER_RECONCILIATION=FAIL_CLOSED type=" + type(exc).__name__)
        return 2
    print("PAPER_RECONCILIATION=" + receipt["status"])
    print("PAPER_LEDGER_EVENT_COUNT=" + str(receipt["ledger_event_count"]))
    return 0 if receipt["status"] == "PASS_HASH_VERIFIED_PAPER_SIMULATION_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
