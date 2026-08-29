"""Eval: /api/accuracy_trend must share Spearman days with auto_gates (no fake PASS)."""

from __future__ import annotations

from dashboard.backend.accuracy_trend_service import build_accuracy_trend_payload
from scripts.system3_gate_evaluator import load_spearman_days


def test_accuracy_trend_aligns_with_load_spearman_days(tmp_path, monkeypatch):
    root = tmp_path
    mv = root / "state" / "market_validations"
    mv.mkdir(parents=True)
    (mv / "market_validation_2026-06-12.json").write_text(
        '{"date":"2026-06-12","rank_correlation_spearman":0.2,"hit_rate":0.6667,'
        '"status":"RETRAIN_NEEDED","predicted_ranking":["NIFTY"],"actual_ranking":["BANKNIFTY"]}',
        encoding="utf-8",
    )

    class FakeBackend:
        def list_validation_days(self):
            return [
                {
                    "date": "2026-08-11",
                    "rank_correlation_spearman": 0.55,
                    "hit_rate": 0.5,
                    "grade": "B",
                },
                {
                    "date": "2026-08-12",
                    "rank_correlation_spearman": 0.72,
                    "hit_rate": 0.7,
                    "grade": "A",
                },
            ]

    monkeypatch.setattr(
        "dashboard.backend.firestore_state_backend.FirestoreSchedulerEvidenceBackend",
        FakeBackend,
    )
    monkeypatch.setenv("SYSTEM3_STATE_BACKEND", "firestore")

    gate_days, passing, latest = load_spearman_days(root)
    payload = build_accuracy_trend_payload(root, retrain_needed=False)

    assert payload["status"] == "ok"
    assert payload["source"] == "load_spearman_days"
    assert payload["days_available"] == len(gate_days) == 2
    assert [row["date"] for row in payload["trend"]] == [d["date"] for d in gate_days]
    assert [row["rho"] for row in payload["trend"]] == [d["rho"] for d in gate_days]
    assert payload["avg_rho"] == round((0.55 + 0.72) / 2, 4)
    assert latest == 0.72
    assert passing == 1  # only 0.72 crosses 0.70 — gate still honestly failing
    assert all(row["date"] != "2026-06-12" for row in payload["trend"])


def test_accuracy_trend_empty_when_no_days(tmp_path, monkeypatch):
    class EmptyBackend:
        def list_validation_days(self):
            return []

    monkeypatch.setattr(
        "dashboard.backend.firestore_state_backend.FirestoreSchedulerEvidenceBackend",
        EmptyBackend,
    )
    payload = build_accuracy_trend_payload(tmp_path)
    assert payload["days_available"] == 0
    assert payload["trend"] == []
    assert payload["status"] == "no_data"
