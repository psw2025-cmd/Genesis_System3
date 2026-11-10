"""Eval: Render.com hosting is forbidden. GCP Cloud Run is the only deploy authority.

Does not ban the English verb 'render' or UI visual-proof docs.
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path
from urllib.parse import urlparse

from dashboard.backend import app as app_mod

_URL_RE = re.compile(r"https?://[^\s\"'`<>]+", re.IGNORECASE)
_BARE_HOST_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9-./?&=])((?:[A-Za-z0-9-]+\.)*onrender\.com)(?![A-Za-z0-9-])"
)

ROOT = Path(__file__).resolve().parents[2]
GCP_UI = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
AUTHORITY_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "GOVERNANCE.md",
    ROOT / ".github" / "CLAUDE_INSTRUCTIONS.md",
    ROOT / "docs" / "authority" / "AUTONOMOUS_OPERATIONS_POLICY.md",
    ROOT / "docs" / "authority" / "RENDER_HOSTING_FORBIDDEN.md",
    ROOT / "docs" / "project_control" / "SYSTEM3_MASTER_GOAL_LOCK.md",
    ROOT / "docs" / "project_control" / "SYSTEM3_CURRENT_CONTROL_PLANE.md",
    ROOT / "docs" / "project_control" / "GLOBAL_CONTROL_PLANE_STRUCTURE_20260616.md",
    ROOT / "docs" / "project_control" / "REPO_CLEANUP_MANIFEST_20260616.md",
    ROOT / "docs" / "deploy" / "STAGING_AND_BRANCH_PROTECTION_SETUP.md",
    ROOT / "docs" / "SYSTEM3_VISUAL_PROOF_AND_RENDER_RULES.md",
]


def is_retired_render_hostname(host: str) -> bool:
    name = (host or "").strip(".").lower()
    return name == "onrender.com" or name.endswith(".onrender.com")


def text_has_retired_render_host(text: str) -> bool:
    """True only when a parsed hostname is onrender.com or a subdomain of it.

    Query/path embeddings such as https://evil.example/?q=onrender.com are not hits.
    """
    consumed: list[tuple[int, int]] = []
    for match in _URL_RE.finditer(text):
        consumed.append((match.start(), match.end()))
        if is_retired_render_hostname(urlparse(match.group(0)).hostname or ""):
            return True
    for match in _BARE_HOST_RE.finditer(text):
        start = match.start()
        if any(left <= start < right for left, right in consumed):
            continue
        if is_retired_render_hostname(match.group(1)):
            return True
    return False


def test_render_yaml_must_not_exist():
    assert not (ROOT / "render.yaml").exists()


def test_forbidden_policy_doc_exists():
    path = ROOT / "docs" / "authority" / "RENDER_HOSTING_FORBIDDEN.md"
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "forbidden" in lowered
    assert "Cloud Run" in text
    assert GCP_UI in text
    assert "render.yaml" in text
    assert "never" in lowered
    assert not text_has_retired_render_host(text)


def test_authority_docs_do_not_keep_render_as_runtime():
    banned = (
        "Authoritative Render runtime",
        "Active Render runtime map",
        "| Render config | `render.yaml` | KEEP",
        "Secrets must live only in GitHub Actions secrets, Render environment secrets",
    )
    for path in AUTHORITY_FILES:
        text = path.read_text(encoding="utf-8")
        assert not text_has_retired_render_host(text), f"{path.name} still contains a Render hostname"
        for needle in banned:
            assert needle not in text, f"{path.name} still treats Render as current: {needle}"
        lowered = text.lower()
        assert (
            "retired" in lowered
            or "forbidden" in lowered
            or "google cloud" in lowered
            or "cloud run" in lowered
            or "gcp project" in lowered
        ), f"{path.name} missing GCP/forbidden deploy authority"


def test_visual_proof_rules_are_gcp_not_render_host():
    text = (ROOT / "docs" / "SYSTEM3_VISUAL_PROOF_AND_RENDER_RULES.md").read_text(encoding="utf-8")
    assert GCP_UI in text
    assert "Render is retired" in text or "Render is forbidden" in text


def test_deploy_info_does_not_use_render_env_as_sha():
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


FORBIDDEN_LEFTOVER_PATHS = [
    ROOT / "tools" / "_render_hosting_retired.py",
    ROOT / "tools" / "system3_github_render_failure_tracker.py",
    ROOT / "tools" / "write_github_render_tracker_fallback.py",
    ROOT / "tools" / "render_deploy_commit_proof.py",
    ROOT / "tools" / "render_memory_stabilization_audit.py",
    ROOT / "tools" / "render_env_alignment_audit.py",
    ROOT / "tools" / "system3_render_worker_preflight.py",
    ROOT / "tools" / "system3_render_worker_env_audit.py",
    ROOT / "tools" / "system3_render_100_agent_swarm.py",
    ROOT / "tools" / "dedupe_failure_tracker_report.py",
    ROOT / "scripts" / "render_worker_mobile_check.sh",
    ROOT / "docs" / "render" / "RENDER_MEMORY_OOM_RUNBOOK.md",
    ROOT / "docs" / "SYSTEM3_GITHUB_RENDER_FAILURE_TODO.md",
    ROOT / "docs" / "render_trading_bot_deployment_blueprint.md",
]


def test_leftover_render_hosting_files_must_not_exist():
    present = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_LEFTOVER_PATHS if path.exists()]
    assert present == [], f"Render hosting leftovers must be deleted: {present}"


def test_sync_render_secrets_must_not_exist():
    assert not (ROOT / "tools" / "sync_render_secrets.py").exists()


def test_no_render_service_ids_in_source():
    ids = ("srv-d8ib83vlk1mc73801i1g", "srv-d92iqfnaqgkc739g226g")
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.split("/", 1)[0] in {"reports", ".git", "node_modules", ".venv", "tests", ".worktrees"}:
            continue
        if path.suffix.lower() not in {".py", ".md", ".yml", ".yaml", ".ts", ".tsx", ".json", ".sh"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(item in text for item in ids):
            hits.append(rel)
    assert hits == [], f"legacy Render service IDs still in source: {hits}"


def test_workflows_must_not_deploy_to_render():
    needles = (
        "render deploy",
        "render blueprint",
        "RENDER_DEPLOY_HOOK",
        "api.render.com",
        "RENDER_API_KEY",
    )
    hits: list[str] = []
    wf_dir = ROOT / ".github" / "workflows"
    for path in list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for needle in needles:
            if needle.lower() in text.lower():
                hits.append(f"{path.name}:{needle}")
    assert hits == [], f"workflows must not deploy to Render: {hits}"


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
        if rel.split("/", 1)[0] in {"reports", ".git", "node_modules", ".venv", "tests", ".worktrees"}:
            continue
        if rel in skip or rel.startswith("reports/") or rel.startswith("tests/"):
            continue
        if path.suffix.lower() not in {".py", ".md", ".yml", ".yaml", ".ts", ".tsx", ".json", ".sh"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if text_has_retired_render_host(text):
            hits.append(rel)
    assert hits == [], f"retired Render hostname still in source authority paths: {hits}"


def test_retired_host_check_uses_parsed_hostname_not_substring():
    assert text_has_retired_render_host("https://foo.onrender.com/ui")
    assert text_has_retired_render_host("genesis-system3-backend.onrender.com")
    assert not text_has_retired_render_host("https://evil.example/?q=onrender.com")
    assert not text_has_retired_render_host("https://evil.example/onrender.com")
    assert not text_has_retired_render_host("https://onrender.com.evil.example/")
    assert not text_has_retired_render_host("not-onrender.com")
