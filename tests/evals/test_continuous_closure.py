"""Eval: continuous closure parse + resume + fail-closed merge."""

from __future__ import annotations

from dashboard.backend.continuous_closure_service import (
    build_continuous_closure_report,
    merge_cards,
    parse_backlog_cards,
    pick_resume_target,
    write_closure_artifacts,
)


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
