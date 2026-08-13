#!/usr/bin/env python3
"""Smoke E2E for durable ML Spearman accumulation (PAPER / analyzer only).

Replays historical-shaped validation days into Firestore so /api/auto_gates and
the System Health UI can prove days_recorded increments — without enabling LIVE.

Usage:
  python scripts/smoke_ml_validate_e2e.py
  python scripts/smoke_ml_validate_e2e.py --write-firestore
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Keep smoke firmly in analyzer mode.
os.environ["LIVE_TRADING_ENABLED"] = "0"
os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
os.environ.setdefault("SYSTEM3_FIRESTORE_PROJECT", os.environ.get("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe"))
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")


def _hist_days() -> list[dict]:
    """Historical-shaped days for smoke (not a live-trading claim)."""
    # Keep most days below 0.70 so the gate does not falsely PASS; one day >= 0.70
    # proves "passing day" counting works.
    return [
        {
            "date": "2026-08-08",
            "rank_correlation_spearman": 0.42,
            "match_rate_top3": 0.33,
            "grade": "C",
            "predicted_top_symbols": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"],
            "actual_top_symbols": ["BANKNIFTY", "NIFTY", "MIDCPNIFTY", "FINNIFTY"],
            "source": "smoke_e2e_historical_replay",
            "validated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
        {
            "date": "2026-08-11",
            "rank_correlation_spearman": 0.58,
            "match_rate_top3": 0.66,
            "grade": "B",
            "predicted_top_symbols": ["NIFTY", "FINNIFTY", "BANKNIFTY", "MIDCPNIFTY"],
            "actual_top_symbols": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"],
            "source": "smoke_e2e_historical_replay",
            "validated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
        {
            "date": "2026-08-12",
            "rank_correlation_spearman": 0.71,
            "match_rate_top3": 0.66,
            "grade": "A",
            "predicted_top_symbols": ["BANKNIFTY", "NIFTY", "MIDCPNIFTY", "FINNIFTY"],
            "actual_top_symbols": ["BANKNIFTY", "NIFTY", "FINNIFTY", "MIDCPNIFTY"],
            "source": "smoke_e2e_historical_replay",
            "validated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
        {
            "date": "2026-08-13",
            "rank_correlation_spearman": 0.63,
            "match_rate_top3": 0.33,
            "grade": "B",
            "predicted_top_symbols": ["MIDCPNIFTY", "NIFTY", "BANKNIFTY", "FINNIFTY"],
            "actual_top_symbols": ["NIFTY", "MIDCPNIFTY", "BANKNIFTY", "FINNIFTY"],
            "source": "smoke_e2e_historical_replay",
            "validated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
    ]


def _eval_local() -> dict:
    from scripts.system3_gate_evaluator import eval_spearman_gate

    return eval_spearman_gate(ROOT)


def _write_firestore(days: list[dict]) -> list[dict]:
    from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend

    backend = FirestoreSchedulerEvidenceBackend()
    stored = []
    for day in days:
        stored.append(backend.upsert_validation_day(day))
    return stored


def _try_live_rank_validate() -> dict | None:
    """Optional: exercise validator against durable rank + Dhan (no Firestore publish here)."""
    try:
        from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend
        from src.validation.market_result_validator import MarketResultValidator

        rank = FirestoreSchedulerEvidenceBackend().load_artifact("rank")
        if not rank or rank.get("status") != "PASS":
            return {"status": "SKIPPED", "reason": "no PASS rank artifact"}
        rows = (rank.get("payload") or {}).get("rows") or []
        predictions = [
            {"underlying": str(r.get("underlying")).upper(), "rank": int(r.get("rank") or i + 1)}
            for i, r in enumerate(rows)
            if r.get("underlying")
        ]
        if not predictions:
            return {"status": "SKIPPED", "reason": "rank rows empty", "rank_date": rank.get("business_date")}
        report = MarketResultValidator().validate_today(prediction_snapshot=predictions)
        return {
            "status": "OK" if not report.get("error") else "BLOCKED",
            "rank_date": rank.get("business_date"),
            "report": report,
        }
    except Exception as exc:
        return {"status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-firestore", action="store_true", help="Upsert smoke historical days to Firestore")
    args = parser.parse_args()

    before = _eval_local()
    live_probe = _try_live_rank_validate()
    days = _hist_days()
    written = []
    if args.write_firestore:
        written = _write_firestore(days)
    after = _eval_local()

    out = {
        "live_trading_enabled": False,
        "mode": "PAPER",
        "before_gate": {
            "days_recorded": before.get("days_recorded"),
            "days_passing_threshold": before.get("days_passing_threshold"),
            "latest_rho": before.get("latest_rho"),
            "pass": before.get("pass"),
        },
        "live_rank_validate_probe": live_probe,
        "smoke_days": [{"date": d["date"], "rho": d["rank_correlation_spearman"], "source": d["source"]} for d in days],
        "firestore_writes": len(written),
        "after_gate": {
            "days_recorded": after.get("days_recorded"),
            "days_passing_threshold": after.get("days_passing_threshold"),
            "latest_rho": after.get("latest_rho"),
            "pass": after.get("pass"),
            "days": after.get("days"),
        },
    }
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
