"""Guard the dashboard against blank-page crashes and fake identity copy."""

from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[1] / "dashboard" / "frontend" / "src"
BACKEND = Path(__file__).resolve().parents[1] / "dashboard" / "backend" / "app.py"


def test_decision_intelligence_imports_lucide_icons_used_in_render():
    source = (FRONTEND / "components" / "workspaces" / "DecisionIntelligence.tsx").read_text(encoding="utf-8")
    assert "from 'lucide-react'" in source
    for name in ("Zap", "Shield", "Activity", "Database", "AlertTriangle"):
        assert name in source.split("from 'lucide-react'")[0], f"{name} must be imported or Decision Intel blanks /ui"


def test_topbar_is_public_readonly_not_fake_admin():
    source = (FRONTEND / "components" / "TopBar.tsx").read_text(encoding="utf-8")
    assert "Pritam S." not in source
    assert "Paper" in source
    assert "Live off" in source or "Live on" in source
    assert "dashboard-command" in source
    assert "System health" in source


def test_app_wraps_workspace_in_error_boundary():
    source = (FRONTEND / "App.tsx").read_text(encoding="utf-8")
    assert "ErrorBoundary" in source
    assert "dashboard-main" in source
    assert "Skip to content" in source
    assert "SystemHealthDiagnostics" in source
    assert 'variant="sr-only"' in source


def test_use_data_fetches_full_state_for_live_kpis():
    source = (FRONTEND / "hooks" / "useData.ts").read_text(encoding="utf-8")
    assert "fetchJSON('/api/state'" in source
    assert "fetchJSON('/api/deploy/info'" in source
    assert "fetchJSON('/api/research/multibagger'" in source


def test_batch_market_data_keeps_live_ops_kpis():
    source = BACKEND.read_text(encoding="utf-8")
    assert "batch_market_data_v2" in source
    assert '"cycle_count": state.get("cycle_count")' in source
    assert '"exposure": risk.get("exposure")' in source


def test_multibagger_empty_state_is_operator_friendly():
    source = (FRONTEND / "components" / "workspaces" / "MultibaggerResearch.tsx").read_text(encoding="utf-8")
    assert "No verified candidates yet" in source
    assert "View data integrity" in source
    assert "View research criteria" in source
    assert "NO VERIFIED CANDIDATES" not in source
    assert "Analyzer mode" not in source
    assert "humanizeContractReason" in source


def test_proof_bar_diagnostics_not_required_in_multibagger_title():
    source = (FRONTEND / "components" / "workspaces" / "MultibaggerResearch.tsx").read_text(encoding="utf-8")
    assert "UI RENDERED" not in source
    assert "SHA" not in source or "shortSha" not in source
    assert "production-proof-bar" not in source


def test_feed_quality_never_claims_live_when_market_closed():
    source = (FRONTEND / "lib" / "feedQuality.ts").read_text(encoding="utf-8")
    assert "never claim Live" in source.lower() or "Never claim Live" in source
    assert "Delayed" in source
    assert "Stale" in source
    assert "!marketOpen" in source or "marketOpen" in source
