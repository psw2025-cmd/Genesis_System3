"""Regression gates for institutional PAPER truth and 23-tab UI presence."""
from __future__ import annotations

import ast
import re
from pathlib import Path

from dashboard.backend.live_profit_validator import LiveProfitValidator

ROOT = Path(__file__).resolve().parents[1]


def paper_position(**kw):
    base = {
        "position_id": "PAPER_CASE_01",
        "underlying": "SENSEX",
        "strike": 87300,
        "option_type": "CE",
        "entry_price": 8.65,
        "current_price": 8.50,
        "qty": 20,
        "positionType": "LONG",
    }
    base.update(kw)
    return base


def test_no_option_quote_is_not_success_and_never_uses_zero_yahoo_spot():
    validator = LiveProfitValidator()
    r = validator.validate_against_market_data(paper_position())
    assert r["status"] == "NO_OPTION_QUOTE"
    assert r["pnl"] is None


def test_no_independent_quote_cannot_claim_pnl_pass():
    validator = LiveProfitValidator()
    validator._load_historical_data = lambda: []
    r = validator.multi_validate_profit(paper_position(), -3.0)
    assert r["validation_status"] == "NO_INDEPENDENT_OPTION_QUOTE"
    assert r["sources_used"] == 0


def test_timestamped_independent_dhan_option_quote_can_reconcile():
    validator = LiveProfitValidator()
    pos = paper_position(
        validation_option_ltp=8.50,
        validation_option_source="DHAN_OPTION_CHAIN",
        validation_option_timestamp="2026-11-13T07:58:00Z",
    )
    r = validator.multi_validate_profit(pos, -3.00, validation_sources=["internal", "market"])
    assert r["validation_status"] == "PASS"
    assert r["consensus_pnl"] == -3.00
    assert r["sources_used"] == 1


def test_reported_unrealized_pnl_mismatch_remains_fail():
    validator = LiveProfitValidator()
    pos = paper_position(
        validation_option_ltp=8.50,
        validation_option_source="DHAN_OPTION_CHAIN",
        validation_option_timestamp="2026-11-13T07:58:00Z",
    )
    r = validator.multi_validate_profit(pos, -50.85, validation_sources=["internal", "market"])
    assert r["validation_status"] == "FAIL"


def test_short_pnl_sign_is_correct():
    validator = LiveProfitValidator()
    pos = paper_position(
        positionType="SHORT",
        validation_option_ltp=9.00,
        validation_option_source="DHAN_OPTION_CHAIN",
        validation_option_timestamp="2026-11-13T07:58:00Z",
    )
    r = validator.validate_against_market_data(pos)
    assert r["status"] == "SUCCESS"
    assert round(r["pnl"], 2) == -7.0


def test_untrusted_option_quote_source_does_not_prove_pnl():
    validator = LiveProfitValidator()
    pos = paper_position(
        validation_option_ltp=8.50,
        validation_option_source="YAHOO_INDEX_SPOT",
        validation_option_timestamp="2026-11-13T07:58:00Z",
    )
    assert validator.validate_against_market_data(pos)["status"] == "NO_OPTION_QUOTE"


def test_truth_routes_present_and_declared_read_only():
    tree = ast.parse((ROOT / "dashboard/backend/app.py").read_text(encoding="utf-8"))
    functions = {
        node.name: node for node in tree.body if isinstance(node, ast.AsyncFunctionDef)
    }
    for name in ("get_data_truth_score", "get_compliance_check"):
        fn = functions[name]
        assert any("app.get" in ast.unparse(dec) for dec in fn.decorator_list)
    source = (ROOT / "dashboard/backend/app.py").read_text(encoding="utf-8")
    assert '"score_pct"' in source
    assert '"legal_compliance_certified": False' in source
    assert '"production_grade_certified": False' in source


def test_23_sidebar_tabs_are_unique_and_readiness_is_reachable():
    sidebar = (ROOT / "dashboard/frontend/src/components/Sidebar.tsx").read_text(encoding="utf-8")
    tab_ids = re.findall(r"\{ id: '([^']+)',\s+label:", sidebar)
    assert len(tab_ids) == 23
    assert len(set(tab_ids)) == 23
    assert "system-readiness" in tab_ids
