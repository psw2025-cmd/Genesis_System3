from pathlib import Path

from dashboard.backend.security_policy import evaluate_request


ROOT = Path(__file__).resolve().parents[1]


def test_public_dashboard_reads_are_always_allowed_without_browser_credentials():
    decision = evaluate_request(method="GET", path="/api/state")
    assert decision.allowed is True
    assert decision.status_code == 200


def test_public_dashboard_mutations_fail_closed_independently_of_browser_credentials():
    decision = evaluate_request(method="POST", path="/api/paper/tick")
    assert decision.allowed is False
    assert decision.status_code == 403
    assert decision.code == "PUBLIC_DASHBOARD_READ_ONLY"


def test_frontend_has_no_dashboard_login_gate():
    app = (ROOT / "dashboard/frontend/src/App.tsx").read_text(encoding="utf-8")
    assert "LoginPage" not in app
    assert "useAuth" not in app
    assert "AuthGate" not in app


def test_active_auth_notice_never_collects_or_submits_credentials():
    notice = (ROOT / "dashboard/frontend/src/components/AuthUnlock.tsx").read_text(encoding="utf-8")
    forbidden = (
        'type="password"',
        "/api/auth/" + "session",
        "JSON.stringify",
        "apiKey",
        "Enter the dashboard" + " API key",
    )
    for marker in forbidden:
        assert marker not in notice
    assert "do not request or enter credentials" in notice
    assert "Public read contract error" in notice


def test_server_session_authority_is_deleted():
    assert not (ROOT / "dashboard/backend/session_truth.py").exists()
    assert not (ROOT / "tests/test_session_truth.py").exists()
    assert not (ROOT / "scripts/gcp_session_runtime_proof.py").exists()


def test_canonical_gcp_deployer_scrubs_retired_dashboard_auth_configuration():
    deploy = (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
    assert "RETIRED_DASHBOARD_ENV" in deploy
    assert "RETIRED_DASHBOARD_SECRETS" in deploy
    assert "--remove-env-vars=" in deploy
    assert "--remove-secrets=" in deploy
    assert "_assert_candidate_has_no_dashboard_credentials" in deploy
    assert '"credential_surface") == "REMOVED"' in deploy
    assert "DASHBOARD_PUBLIC_READONLY enforced" in deploy


def test_manual_gcp_wrapper_has_no_independent_auth_or_deploy_authority():
    deploy = (ROOT / "deploy/gcp/deploy_web.sh").read_text(encoding="utf-8")
    assert "gcloud run deploy" not in deploy
    assert "exec python scripts/gcp_cloud_run_auto_deploy.py" in deploy
    assert "LIVE_TRADING_ENABLED=0" in deploy
    assert "SYSTEM3_LIVE_TRADING_ALLOWED=0" in deploy
    assert "AUTO_EXECUTE_TRADES=0" in deploy


def test_approved_deploy_workflow_proves_public_readonly_live_off_and_actual_ui_visual():
    workflow = (ROOT / ".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
    proof = (ROOT / "scripts/gcp_public_dashboard_runtime_proof.py").read_text(encoding="utf-8")
    assert "scripts/gcp_public_dashboard_runtime_proof.py" in workflow
    assert "public-paper-dashboard-proof-" in workflow
    assert "dashboard_visible_without_login" in proof
    assert "public-dashboard/runtime-proof" in proof
    assert "--headless" in proof
    assert 'OUT / "dashboard.png"' in proof
    assert 'relative.get("dashboard") or "/ui"' in proof
    assert "dashboard_ui_http_status" in proof
    assert "rendered_product_marker_missing" in proof
    assert "dashboard_login_prompt_still_rendered" in proof
    assert "real_deployed_cloud_run_dashboard_ui" in proof
    assert '"dashboard_path": dashboard_path' in proof
    assert '"dashboard_api_key_prompt_rendered": False' in proof
    assert '"api_key_used": False' in proof
    assert "LIVE_TRADING_ENABLED=0" in workflow
    assert "SYSTEM3_LIVE_TRADING_ALLOWED=0" in workflow
    assert "AUTO_EXECUTE_TRADES=0" in workflow


def test_no_extra_workflow_added_for_dashboard_proof():
    assert not (ROOT / ".github/workflows/public-paper-dashboard-proof.yml").exists()
