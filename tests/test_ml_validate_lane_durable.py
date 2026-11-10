from scripts.system3_gate_evaluator import load_spearman_days


def test_load_spearman_days_uses_firestore_only_in_cloud_mode(tmp_path, monkeypatch):
    root = tmp_path
    mv = root / "state" / "market_validations"
    mv.mkdir(parents=True)
    (mv / "market_validation_2026-06-12.json").write_text(
        '{"date":"2026-06-12","rank_correlation_spearman":0.2,"hit_rate":0.5}',
        encoding="utf-8",
    )

    class FakeBackend:
        def list_validation_days(self):
            return [
                {
                    "date": "2026-08-11",
                    "rank_correlation_spearman": 0.75,
                    "hit_rate": 0.66,
                    "grade": "A",
                },
                {
                    "date": "2026-06-12",
                    "rank_correlation_spearman": 0.55,
                    "hit_rate": 0.4,
                    "grade": "B",
                },
            ]

    monkeypatch.setattr(
        "dashboard.backend.firestore_state_backend.FirestoreSchedulerEvidenceBackend",
        FakeBackend,
    )
    monkeypatch.setenv("SYSTEM3_STATE_BACKEND", "firestore")
    days, passing, latest = load_spearman_days(root)
    assert [d["date"] for d in days] == ["2026-06-12", "2026-08-11"]
    # Firestore is the single cloud authority, including duplicate dates.
    assert days[0]["rho"] == 0.55
    assert days[1]["rho"] == 0.75
    assert passing == 1
    assert latest == 0.75


def test_validate_lane_persists_day_when_rank_and_actuals_ok(monkeypatch):
    from scripts import gcp_worker_job

    monkeypatch.setenv("SYSTEM3_JOB_PUBLISH_STATE", "0")
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "0")
    monkeypatch.setenv("SYSTEM3_LIVE_TRADING_ALLOWED", "0")
    monkeypatch.setenv("CLOUD_RUN_EXECUTION", "validate-exec-1")
    monkeypatch.setattr(
        gcp_worker_job,
        "_business_context",
        lambda lane: ("2026-08-14", True, "OPEN_SESSION"),
    )

    class FakeBackend:
        def load_artifact(self, lane):
            assert lane == "rank"
            return {
                "business_date": "2026-08-14",
                "status": "PASS",
                "output_sha256": "a" * 64,
                "output_bytes_b64": "e30=",  # {}
                "payload": {
                    "rows": [
                        {"underlying": "NIFTY", "rank": 1},
                        {"underlying": "BANKNIFTY", "rank": 2},
                    ]
                },
            }

        def upsert_validation_day(self, report):
            assert report["rank_correlation_spearman"] == 0.8
            return {"date": report["date"], "rank_correlation_spearman": 0.8}

        def publish_artifact(self, lane, artifact):
            assert lane == "validate"
            assert artifact["status"] == "PASS"
            return {**artifact, "artifact_version": 1, "lane": "validate"}

    class FakeValidator:
        def validate_today(self, prediction_snapshot=None):
            assert prediction_snapshot[0]["underlying"] == "NIFTY"
            return {
                "date": "2026-08-14",
                "rank_correlation_spearman": 0.8,
                "match_rate_top3": 0.66,
                "grade": "A",
                "predicted_top_symbols": ["NIFTY", "BANKNIFTY"],
                "actual_top_symbols": ["NIFTY", "BANKNIFTY"],
            }

    monkeypatch.setattr(
        "dashboard.backend.firestore_state_backend.FirestoreSchedulerEvidenceBackend",
        FakeBackend,
    )
    monkeypatch.setattr(
        "src.validation.market_result_validator.MarketResultValidator",
        FakeValidator,
    )
    result = gcp_worker_job.run_job("validate")
    assert result["business_artifact"]["lane"] == "validate"
    assert result["business_artifact"]["status"] == "PASS"
