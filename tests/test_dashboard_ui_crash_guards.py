"""Guard the dashboard against blank-page crashes and fake identity copy."""

from pathlib import Path

FRONTEND = Path(__file__).resolve().parents[1] / "dashboard" / "frontend" / "src"


def test_decision_intelligence_imports_lucide_icons_used_in_render():
    source = (FRONTEND / "components" / "workspaces" / "DecisionIntelligence.tsx").read_text(encoding="utf-8")
    assert "from 'lucide-react'" in source
    for name in ("Zap", "Shield", "Activity", "Database", "AlertTriangle"):
        assert name in source.split("from 'lucide-react'")[0], f"{name} must be imported or Decision Intel blanks /ui"


def test_topbar_is_public_readonly_not_fake_admin():
    source = (FRONTEND / "components" / "TopBar.tsx").read_text(encoding="utf-8")
    assert "Pritam S." not in source
    assert "Read-only" in source
    assert "AFTER HOURS" in source
    assert "dashboard-command" in source


def test_app_wraps_workspace_in_error_boundary():
    source = (FRONTEND / "App.tsx").read_text(encoding="utf-8")
    assert "ErrorBoundary" in source
    assert "dashboard-main" in source
    assert "Skip to content" in source
