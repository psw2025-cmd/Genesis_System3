#!/usr/bin/env python3
"""Inject read-only research proof routes into dashboard/backend/app.py.

The routes expose only generated JSON/CSV proof artifacts. They do not train,
promote models, call brokers, or place orders.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "dashboard" / "backend" / "app.py"
MARKER = "# SYSTEM3_ADVANCED_RESEARCH_PROOF_ROUTES"
BLOCK = r'''

__MARKER__
def _advanced_research_proof_root():
    return Path(os.environ.get(
        "SYSTEM3_RESEARCH_PROOF_ROOT",
        str(ROOT_DIR / "reports" / "latest" / "options_bigdata_artifact_model"),
    )).resolve()


def _read_research_json(relative_path: str):
    path = _advanced_research_proof_root() / relative_path
    if not path.exists():
        return None, path
    try:
        return json.loads(path.read_text(encoding="utf-8")), path
    except Exception as exc:
        return {"status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}, path


def _read_research_csv_tail(relative_path: str, limit: int = 20):
    path = _advanced_research_proof_root() / relative_path
    if not path.exists():
        return [], path
    import csv as _csv
    with path.open(encoding="utf-8", errors="replace", newline="") as handle:
        rows = list(_csv.DictReader(handle))
    return rows[-max(1, min(limit, 200)):], path


@app.get("/api/research/model-proof")
async def get_advanced_research_model_proof():
    proof, path = _read_research_json("artifact_model_final_proof.json")
    if not proof:
        return {
            "status": "NOT_READY",
            "message": "Full archive model proof artifact is not present.",
            "proof_path": str(path),
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "promotion_allowed": False,
        }
    model = proof.get("model_backtest") or {}
    return {
        "status": proof.get("status", "UNKNOWN"),
        "source_archive_run_id": proof.get("source_archive_run_id"),
        "calendar": proof.get("calendar") or {},
        "archive_profile": proof.get("archive_profile") or {},
        "feature_generation": model.get("feature_generation") or {},
        "split": model.get("split") or {},
        "selected_config": model.get("selected_config") or {},
        "challenger_tuning": model.get("challenger_tuning") or {},
        "walk_forward": model.get("walk_forward") or {},
        "frozen_test": model.get("frozen_test") or {},
        "candidate_assessment": model.get("candidate_assessment") or {},
        "model_sha256": model.get("model_sha256"),
        "proof_path": str(path),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "promotion_allowed": False,
    }


@app.get("/api/research/backtest-proof")
async def get_advanced_research_backtest_proof():
    proof, path = _read_research_json("model/advanced_model_backtest_proof.json")
    if not proof:
        return {
            "status": "NOT_READY", "proof_path": str(path),
            "live_trading_enabled": False, "promotion_allowed": False,
        }
    return {
        "status": proof.get("status", "UNKNOWN"),
        "split": proof.get("split") or {},
        "selected_config": proof.get("selected_config") or {},
        "validation_best": proof.get("validation_best") or {},
        "walk_forward": proof.get("walk_forward") or {},
        "frozen_test": proof.get("frozen_test") or {},
        "candidate_assessment": proof.get("candidate_assessment") or {},
        "transaction_cost_bps": proof.get("transaction_cost_bps") or [],
        "proof_path": str(path),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "promotion_allowed": False,
    }


@app.get("/api/research/paper-proof")
async def get_advanced_research_paper_proof(limit: int = 20):
    summary, summary_path = _read_research_json("model/normalized_paper_summary.json")
    daily, daily_path = _read_research_csv_tail("model/normalized_paper_daily.csv", limit)
    trades, trades_path = _read_research_csv_tail("model/frozen_selected_trades.csv", limit)
    if not summary:
        return {
            "status": "NOT_READY",
            "summary_path": str(summary_path),
            "daily": [], "trades": [],
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        }
    return {
        "status": summary.get("status", "UNKNOWN"),
        "summary": summary,
        "daily": daily,
        "trades": trades,
        "paths": {
            "summary": str(summary_path),
            "daily": str(daily_path),
            "trades": str(trades_path),
        },
        "paper_truth": {
            "source_file": str(summary_path),
            "displayed_rows": len(trades),
            "fake_fixture_rows_rejected": 0,
            "broker_order_endpoints_called": False,
            "historical_lot_sizes_used": False,
            "broker_fills_used": False,
            "normalized_notional": True,
        },
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
'''.replace("__MARKER__", MARKER)


def main() -> int:
    text = APP.read_text(encoding="utf-8")
    if MARKER in text:
        print("advanced research proof routes already present")
        return 0
    APP.write_text(text.rstrip() + BLOCK + "\n", encoding="utf-8")
    print("injected advanced research proof routes into dashboard/backend/app.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
