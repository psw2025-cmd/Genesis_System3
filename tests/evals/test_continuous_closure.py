"""Eval: continuous closure parse + resume + fail-closed merge."""

from __future__ import annotations

import asyncio
import inspect
import time
from pathlib import Path

from dashboard.backend.continuous_closure_service import (
    REQUEST_PATH_CACHE_TTL_S,
    REQUEST_PATH_EVIDENCE_CLASS,
    REQUEST_PATH_LIVE_TIMEOUT_S,
    build_continuous_closure_report,
    merge_cards,
    multi_source_verify,
    parse_backlog_cards,
    pick_resume_target,
    stamp_closure_request_path,
    write_closure_artifacts,
)
from dashboard.backend.dashboard_truth import classify_overview_data_source


SAMPLE_BACKLOG = """
| ID | Severity | Defect | Evidence | Status |
|----|----------|--------|----------|--------|
| A1 | P0 | spots missing | gain_rank | VERIFIED LIVE |
| A2 | P0 | ML spearman | auto_gates | OPEN — do not force PASS |
| A3 | P1 | NO_TRADE | /api/state | OPEN |
"""


def test_parse_backlog_and_resume_order():
    cards = parse_backlog_cards(SAMPLE_BACKLOG)
    assert [c["id"] for c in cards] == ["A1", "A2", "A3"]
    assert cards[0]["state"] == "RESOLVED"
    assert cards[1]["state"] == "OPEN"
    merged = merge_cards(cards)
    nxt = pick_resume_target(merged)
    assert nxt is not None
    assert nxt["next_id"] == "A2"


def test_fail_closed_merge_prefers_open_gate():
    backlog = [{"id": "G1", "severity": "P0", "state": "RESOLVED", "source": "backlog_md", "defect": "x"}]
    gates = [{"id": "G1", "severity": "P0", "state": "OPEN", "source": "auto_gates", "defect": "gate"}]
    merged = merge_cards(backlog, gates)
    assert len(merged) == 1
    assert merged[0]["state"] == "OPEN"


def test_build_offline_and_write_artifacts(tmp_path):
    root = tmp_path
    backlog_dir = root / "reports" / "latest" / "autonomous_loop"
    backlog_dir.mkdir(parents=True)
    (backlog_dir / "BACKLOG.md").write_text(SAMPLE_BACKLOG, encoding="utf-8")
    (root / "agent_policy.yaml").write_text("version: 2\n", encoding="utf-8")
    report = build_continuous_closure_report(root, include_live=False)
    assert report["schema"] == "continuous_closure_v1"
    assert report["summary"]["open"] >= 2
    assert report["phases"]["auto_resume"]["next_id"] == "A2"
    assert report["safety"]["live_trading_enabled"] is False
    summary, state = write_closure_artifacts(root, report)
    assert summary.exists()
    assert state.exists()
    assert "continuous_closure_resume_v1" in state.read_text(encoding="utf-8")


def test_request_path_live_timeout_is_bounded():
    assert REQUEST_PATH_LIVE_TIMEOUT_S <= 3.0
    assert REQUEST_PATH_CACHE_TTL_S <= 5.0


def test_cached_closure_report_stays_historical():
    generated = "2026-08-23T08:00:00Z"
    stamped = stamp_closure_request_path(
        {
            "schema": "continuous_closure_v1",
            "generated_at_utc": generated,
            "safety": {"live_trading_enabled": False},
            "request_path": {"self_http_fanout": False},
        },
        cache_hit=True,
        cache_age_s=4.2,
        live_query=True,
    )
    assert stamped["generated_at_utc"] == generated
    assert stamped["request_path"]["cache_hit"] is True
    assert stamped["request_path"]["cache_age_s"] == 4.2
    assert stamped["request_path"]["evidence_class"] == REQUEST_PATH_EVIDENCE_CLASS
    assert stamped["request_path"]["self_http_fanout"] is False
    assert stamped["served_at_utc"]


def test_overview_data_source_is_not_bare_live_when_closed():
    closed = classify_overview_data_source(market_open=False, broker_connected=True)
    assert closed == "broker_connected_market_closed"
    assert closed != "live"
    assert classify_overview_data_source(market_open=True, broker_connected=True) == (
        "broker_connected_market_open"
    )


def test_multi_source_verify_fail_closed_fast_on_hang(monkeypatch, tmp_path):
    """Hanging production URLs must not wedge the closure feed (Cloud Run deadlock)."""

    def _hang(*_args, **_kwargs):
        time.sleep(1.2)
        raise TimeoutError("simulated hung peer")

    monkeypatch.setattr(
        "dashboard.backend.continuous_closure_service.urllib.request.urlopen",
        _hang,
    )
    (tmp_path / "reports" / "latest" / "autonomous_loop").mkdir(parents=True)
    (tmp_path / "reports" / "latest" / "autonomous_loop" / "BACKLOG.md").write_text(
        SAMPLE_BACKLOG, encoding="utf-8"
    )
    (tmp_path / "agent_policy.yaml").write_text("version: 2\n", encoding="utf-8")
    started = time.monotonic()
    result = multi_source_verify(tmp_path, timeout_s=0.2, max_budget_s=0.8)
    elapsed = time.monotonic() - started
    assert elapsed < 2.5
    assert result["sources"]["live"]["ok"] is False
    assert result.get("auto_gates") in (None, {})


def test_http_handler_never_fans_out_self_http():
    from dashboard.backend.app import get_continuous_closure

    src = inspect.getsource(get_continuous_closure)
    assert "include_live=False" in src
    assert "include_live=bool(live)" not in src
    assert "live: bool = False" in src
    assert "_TTL_AUTO_GATES" not in src
    assert "REQUEST_PATH_CACHE_TTL_S" in src
    assert "stamp_closure_request_path" in src


def test_http_handler_calls_build_offline_even_when_live_query(monkeypatch, tmp_path):
    from dashboard.backend import app as app_mod

    seen: dict = {}

    def fake_build(root, *, include_live=True, **_kwargs):
        seen["include_live"] = include_live
        return {
            "schema": "continuous_closure_v1",
            "phases": {"blocker_cards": [], "auto_resume": None},
            "summary": {"open": 0, "resolved": 0, "total_cards": 0},
            "safety": {"live_trading_enabled": False},
        }

    monkeypatch.setattr(
        "dashboard.backend.continuous_closure_service.build_continuous_closure_report",
        fake_build,
    )
    monkeypatch.setattr(
        "dashboard.backend.continuous_closure_service.write_closure_artifacts",
        lambda *_a, **_k: (tmp_path, tmp_path),
    )
    report = asyncio.run(app_mod.get_continuous_closure(refresh=True, live=True))
    assert seen.get("include_live") is False
    assert report["request_path"]["self_http_fanout"] is False
    assert report["safety"]["live_trading_enabled"] is False


def test_frontend_board_uses_offline_request_path():
    text = (
        Path(__file__).resolve().parents[2]
        / "dashboard"
        / "frontend"
        / "src"
        / "components"
        / "ContinuousClosureBoard.tsx"
    ).read_text(encoding="utf-8")
    assert "live=false" in text
    assert "live=true" not in text
    assert "closure-evidence-class" in text
    assert "HISTORICAL_STORED" in text
