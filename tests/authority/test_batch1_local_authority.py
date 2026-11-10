"""Batch 1: local authority, one alwaysApply rule, no active Cloud Run URLs."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / ".cursor" / "rules"
ACTIVE_TEXT = [
    ROOT / "AGENTS.md",
    ROOT / ".cursorrules",
    ROOT / "agent_policy.yaml",
    RULES / "00-repository-safety.mdc",
    RULES / "10-autonomous-verification.mdc",
    RULES / "20-ui-data-truth.mdc",
    RULES / "30-dhan-readonly-and-paper.mdc",
    RULES / "40-ml-prediction-validation.mdc",
    RULES / "50-testing-evidence.mdc",
    RULES / "60-git-change-control.mdc",
]
DEPRECATED_RULES = [
    "canonical-laptop-repo-path.mdc",
    "continuous-closure.mdc",
    "end-to-end-issues-solutions.mdc",
    "gemini-autonomous-loop.mdc",
    "governance-watchdog.mdc",
    "infinite-gitops-loop.mdc",
    "master-automation-runbook.mdc",
    "session-issues-master.mdc",
]
CLOUD_RUN_RE = re.compile(r"genesis-system3-web-doq2wplepa-el\.a\.run\.app", re.I)
SIX_INDEX = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX")


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    block = text[3:end] if end > 0 else ""
    return yaml.safe_load(block) or {}


def test_only_universal_safety_rule_is_always_applied():
    always = []
    for path in RULES.glob("*.mdc"):
        meta = _frontmatter(path)
        if meta.get("alwaysApply") is True:
            always.append(path.name)
    assert always == ["00-repository-safety.mdc"]


def test_legacy_rules_are_non_authoritative_redirects():
    for name in DEPRECATED_RULES:
        path = RULES / name
        text = path.read_text(encoding="utf-8")
        meta = _frontmatter(path)
        assert meta.get("alwaysApply") is False
        assert "HISTORICAL_NON_AUTHORITY" in text


def test_active_authority_has_no_cloudrun_acceptance_url():
    for path in ACTIVE_TEXT:
        text = path.read_text(encoding="utf-8")
        assert CLOUD_RUN_RE.search(text) is None, path


def test_agents_md_declares_local_canonical_and_safety():
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert r"C:\Genesis_System3_Clean" in text
    assert "127.0.0.1:8000" in text
    assert "LIVE_TRADING_ENABLED=0" in text
    assert "Issue #188 is historical" in text or "not a mandatory bus" in text


def test_dhan_rule_lists_six_indices():
    text = (RULES / "30-dhan-readonly-and-paper.mdc").read_text(encoding="utf-8")
    for name in SIX_INDEX:
        assert name in text


def test_vscode_tasks_open_local_8000_not_streamlit_8501():
    text = (ROOT / ".vscode" / "tasks.json").read_text(encoding="utf-8")
    assert "127.0.0.1:8000" in text
    assert "8501" not in text
    assert "run.app" not in text
