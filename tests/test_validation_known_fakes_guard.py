"""Regression checks for known manufactured Genesis validation evidence."""
from pathlib import Path
import ast


ROUTER = Path(__file__).resolve().parents[1] / "dashboard" / "backend" / "routers" / "ml.py"


def test_validation_rejects_generated_paper_ids_and_date_mismatches():
    source = ROUTER.read_text(encoding="utf-8")
    tree = ast.parse(source)
    methods = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    func = ast.get_source_segment(source, methods["_assess_validation_file"])
    assert "PAPER_TR_20261029_" in func
    assert "known generated paper-trade IDs are not reconciliation evidence" in func
    assert "validation filename date differs from report date" in func


def test_market_rank_study_does_not_prove_paper_trade_lifecycle():
    source = ROUTER.read_text(encoding="utf-8")
    func = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "_assess_validation_file")
    text = ast.get_source_segment(source, func)
    assert "real_bhavcopy_5day_validation.py" in text
    assert "market ranking study is not closed paper-trade reconciliation" in text


def test_validation_requires_source_record_hashes():
    source = ROUTER.read_text(encoding="utf-8")
    func = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "_assess_validation_file")
    text = ast.get_source_segment(source, func)
    for field in ("source_evidence", "predictions_sha256", "outcomes_sha256", "closed_trades_sha256"):
        assert field in text


def test_unverified_accuracy_never_falls_back_to_june_stub():
    source = ROUTER.read_text(encoding="utf-8")
    func = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "_primary_validation_metrics")
    body = ast.get_source_segment(source, func)
    assert "market_validation_2026-06-12.json" not in body
    assert '"no verified validation report"' in body
    assert "_assess_validation_file(path)" in body


def test_historical_accuracy_uses_only_assessed_reports():
    source = ROUTER.read_text(encoding="utf-8")
    func = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "_validation_metrics")
    body = ast.get_source_segment(source, func)
    assert "_assess_validation_file(path)" in body
    assert "if not ok:" in body
    assert "validations = _load_validations()" not in body


def test_readiness_does_not_recommend_disabled_synthetic_generator():
    source = ROUTER.read_text(encoding="utf-8")
    assert 'REAL_PAPER_LIFECYCLE_NOT_PROVEN - run scripts/run_paper_validation.py' not in source
    assert 'REAL_PAPER_LIFECYCLE_NOT_PROVEN - verified trade and market evidence unavailable' in source
