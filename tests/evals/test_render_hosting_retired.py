"""Eval: Render.com hosting is retired. GCP Cloud Run is the only deploy authority.

Does not ban the English verb 'render' or UI visual-proof docs.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GCP_UI = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
AUTHORITY_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "GOVERNANCE.md",
    ROOT / "docs" / "authority" / "AUTONOMOUS_OPERATIONS_POLICY.md",
    ROOT / "docs" / "project_control" / "SYSTEM3_MASTER_GOAL_LOCK.md",
    ROOT / "docs" / "project_control" / "SYSTEM3_CURRENT_CONTROL_PLANE.md",
    ROOT / "docs" / "project_control" / "GLOBAL_CONTROL_PLANE_STRUCTURE_20260616.md",
    ROOT / "docs" / "project_control" / "REPO_CLEANUP_MANIFEST_20260616.md",
    ROOT / "docs" / "deploy" / "STAGING_AND_BRANCH_PROTECTION_SETUP.md",
    ROOT / "docs" / "SYSTEM3_VISUAL_PROOF_AND_RENDER_RULES.md",
]


def test_render_yaml_must_not_exist():
    assert not (ROOT / "render.yaml").exists()


def test_authority_docs_do_not_keep_render_as_runtime():
    banned = (
        "Authoritative Render runtime",
        "Active Render runtime map",
        "| Render config | `render.yaml` | KEEP",
        "genesis-system3-backend-staging.onrender.com",
        "Secrets must live only in GitHub Actions secrets, Render environment secrets",
    )
    for path in AUTHORITY_FILES:
        text = path.read_text(encoding="utf-8")
        for needle in banned:
            assert needle not in text, f"{path.name} still treats Render as current: {needle}"
        lowered = text.lower()
        assert (
            "retired" in lowered
            or "google cloud" in lowered
            or "cloud run" in lowered
            or "gcp project" in lowered
        ), f"{path.name} missing GCP/retired deploy authority"


def test_visual_proof_rules_are_gcp_not_render_host():
    text = (ROOT / "docs" / "SYSTEM3_VISUAL_PROOF_AND_RENDER_RULES.md").read_text(encoding="utf-8")
    assert GCP_UI in text
    assert "Render is retired" in text


def test_deploy_info_does_not_use_render_env_as_sha():
    from dashboard.backend import app as app_mod

    src = inspect.getsource(app_mod.get_deploy_info)
    assert "RENDER_GIT_COMMIT" not in src
    assert "RENDER_SERVICE_NAME" not in src
    assert "RENDER_GIT_BRANCH" not in src
    assert "DEPLOY_GIT_SHA" in src
    assert "K_SERVICE" in src


def test_control_plane_keep_list_is_not_render_yaml():
    text = (ROOT / "system3_control_plane.py").read_text(encoding="utf-8")
    assert '"render.yaml"' not in text


def test_master_proof_treats_render_yaml_as_retired_blocker_if_present():
    text = (ROOT / "scripts" / "system3_master_proof_orchestrator.py").read_text(encoding="utf-8")
    assert "render_yaml_missing" not in text
    assert "render_yaml_present_retired_host" in text


RETIRED_TOOLS = [
    ROOT / "tools" / "system3_github_render_failure_tracker.py",
    ROOT / "tools" / "write_github_render_tracker_fallback.py",
    ROOT / "tools" / "render_deploy_commit_proof.py",
    ROOT / "tools" / "render_memory_stabilization_audit.py",
    ROOT / "tools" / "render_env_alignment_audit.py",
    ROOT / "tools" / "system3_render_worker_preflight.py",
    ROOT / "tools" / "system3_render_worker_env_audit.py",
    ROOT / "tools" / "system3_render_100_agent_swarm.py",
    ROOT / "scripts" / "render_worker_mobile_check.sh",
]


def test_leftover_render_tools_are_retired_stubs():
    for path in RETIRED_TOOLS:
        text = path.read_text(encoding="utf-8")
        assert "retired" in text.lower(), f"{path.name} is not marked retired"
        assert "Cloud Run" in text or "gcp-cloud-run" in text or "genesis-system3-web" in text
        assert "onrender.com" not in text


def test_sync_render_secrets_must_not_exist():
    assert not (ROOT / "tools" / "sync_render_secrets.py").exists()


def test_proof_board_does_not_require_render_host():
    text = (ROOT / "docs" / "SYSTEM3_VISUAL_AND_PAPER_PROOF_BOARD.md").read_text(encoding="utf-8")
    assert "Render/backend health" not in text
    assert "Cloud Run" in text


def test_blocker_matrix_uses_cloud_run_not_render_host():
    text = (ROOT / "docs" / "SYSTEM3_360_ROOT_CAUSE_BLOCKERS.md").read_text(encoding="utf-8")
    assert "live Render dashboard UI" not in text
    assert "genesis-system3-web-doq2wplepa-el.a.run.app" in text
    assert "Render.com is not current proof" in text


def test_kid_runbook_does_not_deploy_to_render():
    text = (ROOT / "docs" / "SYSTEM3_KID_LEVEL_FULL_SYSTEM_RUNBOOK.md").read_text(encoding="utf-8")
    assert "Use Render only after" not in text
    assert "Render backend smoke PASS if using Render" not in text
    assert "genesis-system3-web-doq2wplepa-el.a.run.app" in text


def test_production_probe_fails_if_render_yaml_present():
    text = (ROOT / "scripts" / "system3_maximum_safe_production_probe.py").read_text(encoding="utf-8")
    assert "live_trading_disabled_in_render" not in text
    assert "render_yaml_present_retired_host" in text


def test_source_tree_has_no_onrender_authority_urls():
    skip = {
        "reports",
        "CHANGE_LOG.md",
        "AGENT_CONTEXT_SNAPSHOT.md",
        "check_integrity.py",
    }
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.split("/", 1)[0] in {"reports", ".git", "node_modules", ".venv", "tests"}:
            continue
        if rel in skip or rel.startswith("reports/") or rel.startswith("tests/"):
            continue
        if path.suffix.lower() not in {".py", ".md", ".yml", ".yaml", ".ts", ".tsx", ".json", ".sh"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "onrender.com" in text:
            hits.append(rel)
    assert hits == [], f"onrender.com still in source authority paths: {hits}"


def test_retired_helper_writes_cloud_run_pass(tmp_path):
    from tools._render_hosting_retired import render_yaml_exists, write_retired_report

    assert not render_yaml_exists()
    code = write_retired_report(tmp_path)
    assert code == 0
    payload = json.loads((tmp_path / "summary.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert payload["hosting_authority"] == "gcp-cloud-run"
    assert payload["render_yaml_exists"] is False
