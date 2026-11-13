"""Deterministic, isolated exchange-closed PAPER pipeline replay.

No real broker API, Cloud Run execution, Secret Manager, or Firestore imports.
The synthetic price generator and simulated outcomes are NEVER validation
evidence for live-model promotion, actual trading, or broker health.

Run: python scripts/system3_market_closed_paper_replay.py --mock-replay
"""
from __future__ import annotations

import argparse
import json
import tempfile
import sys
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.backend.autonomous_paper_core import (
    MasterPaperLedger, estimate_costed_paper_pnl,
)

IST = ZoneInfo("Asia/Kolkata")
SCHEMA_VERSION = "genesis-mock-replay-v1"
SYNTHETIC_SOURCE = "OFFLINE_SYNTHETIC_FIXTURE_NOT_EXCHANGE_DATA"


def run_mock_replay(*, symbol_count: int = 219) -> dict:
    """Run market detection -> mock ranking -> entry -> exit -> reconciliation.

    The simulation clock is controlled and intentionally independent from
    exchange time. All writes are confined to a TemporaryDirectory.
    """
    if not 3 <= symbol_count <= 1000:
        raise ValueError("mock symbol_count must be 3..1000")
    wall_time = datetime.now(timezone.utc).isoformat()
    session = datetime.now(IST).date().isoformat()
    sim_open = datetime.now(IST).replace(hour=9, minute=15, second=0, microsecond=0)
    # All rows are fictitious identifiers. Never mix with the live NSE universe.
    fixtures = [
        {
            "symbol": f"SIM_FO_{i:04d}",
            "security_id": f"SIM_ONLY_{i:06d}",
            "exchange_segment": "MOCK_NSE_FNO",
            "premium_ltp": float(10 + i % 7),
            "spot": float(5000 + i * 3),
            "opportunity_score": round(((i * 47) % 101) / 100, 2),
            "source": SYNTHETIC_SOURCE,
            "observed_at_utc": wall_time,
        }
        for i in range(1, symbol_count + 1)
    ]
    selection = sorted(
        fixtures, key=lambda x: (-x["opportunity_score"], x["symbol"])
    )[:3]
    if len(selection) != 3 or any(x["source"] != SYNTHETIC_SOURCE for x in selection):
        raise AssertionError("replay fixture source is not isolated")

    closed = []
    duplicate_guard = []
    validation = []
    # Windows' inherited system TEMP may be denied to the desktop worker.
    # Choose an explicitly writable ephemeral root, never an application state
    # directory or cloud database. Linux Cloud Run defaults to /tmp.
    temp_root = os.environ.get("SYSTEM3_MOCK_REPLAY_TEMP_ROOT")
    if not temp_root and os.name == "nt":
        desktop = Path.home() / "Desktop"
        temp_root = str(desktop) if desktop.is_dir() else None
    with tempfile.TemporaryDirectory(
        prefix="system3-replay-ephemeral-", dir=temp_root
    ) as tmp:
        path = Path(tmp) / "paper.db"
        ledger = MasterPaperLedger(path)
        for idx, selected in enumerate(selection):
            name = f"MOCK_PAPER_{idx+1:03d}"
            opened_at = (sim_open + timedelta(seconds=idx)).isoformat()
            mark_at = (sim_open + timedelta(minutes=5, seconds=idx)).isoformat()
            closed_at = (sim_open + timedelta(minutes=10, seconds=idx)).isoformat()
            outcome_at = (sim_open + timedelta(minutes=15, seconds=idx)).isoformat()
            entry = float(selected["premium_ltp"])
            mark = entry + (1.5 if idx % 2 == 0 else -0.5)
            exit_price = entry + (2.5 if idx % 2 == 0 else -1)
            qty = 20
            pos = {
                "position_id": name,
                "underlying": selected["symbol"],
                "strike": 5000 + idx * 50,
                "option_type": "CE" if idx % 2 == 0 else "PE",
                "qty": qty,
                "entry_price": entry,
                "current_price": entry,
                "status": "OPEN",
                "timestamp": opened_at,
                "market_data_source": SYNTHETIC_SOURCE,
                "model_verified": False,
            }
            if ledger.record_open(pos, opened_at) is not True:
                raise AssertionError("paper open failed")
            duplicate_guard.append(ledger.record_open(pos, opened_at) is False)
            if ledger.record_mark({
                **pos, "current_price": mark,
                "unrealized_pnl": estimate_costed_paper_pnl(entry, mark, qty),
            }, mark_at) is not True:
                raise AssertionError("paper mark failed")
            final = {
                **pos, "status": "CLOSED",
                "exit_price": exit_price,
                "realized_pnl": estimate_costed_paper_pnl(entry, exit_price, qty),
                "exit_reason": "MOCK_EXIT_RULE",
            }
            if ledger.record_close(final, closed_at) is not True:
                raise AssertionError("paper close failed")
            closed.append(final)
            observed = ledger.record_outcome(
                name, reference_price=exit_price, at=outcome_at,
                source=SYNTHETIC_SOURCE,
            )
            validation.append(observed.get("validation_status"))
        # Re-open SQLite to prove deterministic restart / event-hash recovery.
        restarted = MasterPaperLedger(path)
        state = restarted.snapshot()
        reconcile = restarted.reconcile([], closed)
        learning = restarted.learning_proposal(
            (sim_open + timedelta(minutes=30)).isoformat())
        passed = all((
            state["verified_hash_chain"] is True,
            len(state["open_positions"]) == 0,
            len(state["closed_positions"]) == 3,
            reconcile["status"] == "PASS",
            all(duplicate_guard),
            all(v == "NOT_VERIFIED" for v in validation),
            learning["status"] == "NOT_VERIFIED",
            learning.get("model_promoted") is not True,
        ))
        result = {
            "schema": SCHEMA_VERSION,
            "status": "MOCK_REPLAY_PASS" if passed else "MOCK_REPLAY_FAIL",
            "production_readiness": "NOT_PROVEN",
            "source": SYNTHETIC_SOURCE,
            "is_synthetic": True,
            "generated_at_utc": wall_time,
            "simulation_session": session,
            "mock_instrument_count": len(fixtures),
            "mock_inference_engine": "DETERMINISTIC_RULE_ONLY_NOT_TRAINED_MODEL",
            "mock_positions_opened_and_closed": len(closed),
            "event_count": state["event_count"],
            "ledger_hash_chain_verified": state["verified_hash_chain"],
            "restart_reconciliation": reconcile["status"],
            "idempotency_guards_pass": all(duplicate_guard),
            "synthetic_outcomes": validation,
            "learning_eligible_trades": learning.get("eligible_trades"),
            "model_promoted": bool(learning.get("model_promoted")),
            "real_broker_order_calls": 0,
            "firestore_writes": 0,
            "secret_reads": 0,
            "production_state_mutated": False,
            "selected_mock_underlyings": [row["symbol"] for row in selection],
        }
    if not passed:
        raise RuntimeError("MOCK_REPLAY_INVARIANT_FAILURE")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Isolated PAPER-only closed-market synthetic replay")
    parser.add_argument("--mock-replay", action="store_true", required=True)
    parser.add_argument("--symbol-count", type=int, default=219)
    args = parser.parse_args()
    try:
        payload = run_mock_replay(symbol_count=args.symbol_count)
    except Exception as exc:
        print(json.dumps({
            "schema": SCHEMA_VERSION,
            "status": "MOCK_REPLAY_FAIL",
            "error_type": type(exc).__name__,
            "production_readiness": "NOT_PROVEN",
        }, sort_keys=True))
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
