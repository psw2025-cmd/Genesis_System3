from __future__ import annotations

import asyncio
from pathlib import Path

import pandas as pd

from dashboard.backend import chain_adapter
from dashboard.backend.ml_evidence_store import load_rank_history
from scripts.system3_model_accuracy_tracker import load_prediction_sources


def test_firestore_rank_wins_over_conflicting_local_scratch(tmp_path, monkeypatch):
    local = tmp_path / "state" / "gain_rank_history.json"
    local.parent.mkdir(parents=True)
    local.write_text('[{"date":"2026-08-28","predictions":[{"underlying":"LOCAL","gain_score":99}]}]')
    monkeypatch.setenv("SYSTEM3_STATE_BACKEND", "firestore")
    monkeypatch.setenv("SYSTEM3_STATE_BACKEND_REQUIRED", "1")

    class Backend:
        def load_artifact(self, lane):
            assert lane == "rank"
            return {
                "status": "PASS",
                "business_date": "2026-08-28",
                "produced_at_utc": "2026-08-28T03:45:00Z",
                "run_id": "rank-1",
                "artifact_version": 3,
                "payload": {"rows": [{"underlying": "NIFTY", "rank": 1, "gain_score": 72.5}]},
            }

    monkeypatch.setattr("dashboard.backend.firestore_state_backend.FirestoreSchedulerEvidenceBackend", Backend)
    history, source, required = load_rank_history(tmp_path)
    assert required is True
    assert source == "firestore:artifact_rank"
    assert history[0]["predictions"][0]["underlying"] == "NIFTY"
    rows, sources = load_prediction_sources(tmp_path, api_base=None)
    assert [row["underlying"] for row in rows] == ["NIFTY"]
    assert sources == ["firestore:artifact_rank"]


def test_required_firestore_missing_never_falls_back_local(tmp_path, monkeypatch):
    local = tmp_path / "state" / "gain_rank_history.json"
    local.parent.mkdir(parents=True)
    local.write_text('[{"date":"2026-08-28","predictions":[{"underlying":"LOCAL","gain_score":99}]}]')
    monkeypatch.setenv("SYSTEM3_STATE_BACKEND", "firestore")
    monkeypatch.setenv("SYSTEM3_STATE_BACKEND_REQUIRED", "1")

    class Backend:
        def load_artifact(self, lane):
            return None

    monkeypatch.setattr("dashboard.backend.firestore_state_backend.FirestoreSchedulerEvidenceBackend", Backend)
    history, source, required = load_rank_history(tmp_path)
    assert history == []
    assert source == "firestore:artifact_rank:missing"
    assert required is True
    rows, sources = load_prediction_sources(tmp_path, api_base=None)
    assert rows == []
    assert sources == ["firestore:artifact_rank:missing"]


def test_liquidity_bouncer_and_missing_greeks_contract():
    df = pd.DataFrame(
        [
            {"strike": 18500, "option_type": "CE", "oi": 0, "volume": 50, "ltp": 1},
            {"strike": 18500, "option_type": "PE", "oi": 50, "volume": 0, "ltp": 1},
            {"strike": 18600, "option_type": "CE", "oi": 50, "volume": 25, "ltp": 10},
            {"strike": 18600, "option_type": "PE", "oi": 75, "volume": 30, "ltp": 11, "delta": 0.0, "gamma": None},
        ]
    )

    class DSM:
        def fetch_option_chain(self, underlying, expiry=""):
            return df, 18600.0

    payload = chain_adapter.fetch_chain_for_api(DSM(), "NIFTY")
    assert payload is not None
    assert payload["broker_rows_total"] == 4
    assert payload["liquidity_eligible_rows_total"] == 2
    assert payload["liquidity_filtered_rows"] == 2
    assert {row["strike"] for row in payload["contracts"]} == {18600.0}
    ce = next(row for row in payload["contracts"] if row["option_type"] == "CE")
    pe = next(row for row in payload["contracts"] if row["option_type"] == "PE")
    assert ce["delta"] is None and ce["gamma"] is None and ce["theta"] is None and ce["vega"] is None
    assert pe["delta"] == 0.0
    assert pe["gamma"] is None


def test_live_gate_uses_shared_rank_correlation_loader(monkeypatch):
    import dashboard.backend.app as app_module

    monkeypatch.setattr(
        "scripts.system3_gate_evaluator.load_spearman_days",
        lambda root: ([{"date": "2026-08-28", "rho": 0.8}] * 10, 10, 0.8),
    )
    payload = asyncio.run(app_module.get_live_trading_gate())
    gates = {row["gate"]: row for row in payload["gates"]}
    assert gates["validation_days"]["passed"] is True
    assert gates["ml_accuracy_rho"]["passed"] is True
