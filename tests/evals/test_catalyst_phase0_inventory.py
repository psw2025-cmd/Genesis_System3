"""Eval: Catalyst Phase-0 source inventory CSV is present, complete, and fail-closed."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "reports/coordination/catalyst_source_capability_matrix.csv"

REQUIRED_COLUMNS = [
    "source_id",
    "category",
    "provider",
    "free_or_paid",
    "present_in_repo",
    "repo_paths",
    "present_in_gcp",
    "access_method",
    "requires_secret",
    "live_or_delayed",
    "expected_cadence",
    "observed_latency_ms",
    "observed_freshness_s",
    "coverage",
    "historical_depth",
    "rate_limit",
    "failure_mode",
    "fallback_provider",
    "trust_tier",
    "legal_notes",
    "prediction_use",
    "smoke_result",
    "proof_artifact",
    "owner",
    "status",
    "next_action",
]

REQUIRED_CATEGORIES = {
    "dhan_rest",
    "dhan_ws",
    "option_chains",
    "security_master_fo",
    "historical_data",
    "scanners_rankers",
    "prediction_models",
    "multibagger_inputs",
    "news_sentiment_event",
    "provider_fallback_cache",
    "backend_apis_store_ui",
}

ALLOWED_STATUS = {
    "EXISTS_WORKING",
    "EXISTS_BROKEN",
    "EXISTS_UNUSED",
    "DUPLICATE",
    "MISSING",
    "UNKNOWN",
}

FORBIDDEN_LIVE_INVENTIONS = (
    "ltp=",
    "nifty=",
    "spot=24",
    "pcr=0.",
)


def _rows() -> list[dict[str, str]]:
    with MATRIX.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def test_catalyst_phase0_matrix_exists_with_plan_columns():
    assert MATRIX.is_file(), "Phase-0 matrix missing; do not implement runtime Catalyst without it"
    with MATRIX.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == REQUIRED_COLUMNS
        rows = list(reader)
    assert len(rows) >= 20


def test_catalyst_phase0_covers_required_source_classes():
    rows = _rows()
    categories = {row["category"] for row in rows}
    assert REQUIRED_CATEGORIES <= categories
    statuses = {row["status"] for row in rows}
    assert statuses <= ALLOWED_STATUS
    assert "MISSING" in statuses
    assert "EXISTS_BROKEN" in statuses


def test_catalyst_phase0_does_not_claim_dhan_ws_or_news_as_working():
    rows = {row["source_id"]: row for row in _rows()}
    assert rows["dhan_official_market_ws"]["status"] == "EXISTS_BROKEN"
    assert rows["sebi_filings_feed"]["status"] == "MISSING"
    assert rows["rbi_policy_feed"]["status"] == "MISSING"
    assert rows["bse_exchange_notices"]["status"] == "MISSING"
    assert rows["options_intel_abnormal_activity"]["status"] == "MISSING"
    assert rows["pcr_local_sentiment"]["status"] == "EXISTS_UNUSED"
    assert "NO_CATALYST_FEED" in rows["options_intel_abnormal_activity"]["failure_mode"]


def test_catalyst_phase0_observed_metrics_are_not_invented():
    rows = _rows()
    allowed_latency = {"NOT_PROBED", "n/a"}
    allowed_freshness = {"NOT_PROBED", "n/a", "STALE_WEEKEND_WRONG_DATE"}
    for row in rows:
        latency = row["observed_latency_ms"]
        freshness = row["observed_freshness_s"]
        assert latency in allowed_latency or latency.startswith("NOT_")
        assert freshness in allowed_freshness or freshness.startswith("NOT_")
        blob = " ".join(row.values()).lower()
        for token in FORBIDDEN_LIVE_INVENTIONS:
            assert token not in blob
        assert "100000x" not in blob
        assert row["source_id"]
        assert row["next_action"]


def test_catalyst_phase0_health_proof_artifact_is_same_session_and_non_secret():
    proof = ROOT / "reports/coordination/catalyst_phase0_ruhi022_health_proof_20260822T115910Z.json"
    text = proof.read_text(encoding="utf-8")
    assert "431bbccac48e5536b8c5bc5eb09863e0a9419b16" in text
    assert '"scheduler_healthy": true' in text
    assert "*/5 * * * *" in text
    assert "access_token" not in text.lower()
    assert "DHAN_ACCESS_TOKEN" not in text
    rows = {row["source_id"]: row for row in _rows()}
    assert (
        "catalyst_phase0_ruhi022_health_proof_20260822T115910Z.json"
        in rows["gcp_dhan_token_rotate_daily"]["proof_artifact"]
    )
    assert rows["gcp_dhan_token_rotate_daily"]["status"] == "EXISTS_WORKING"
