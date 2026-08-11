from pathlib import Path

from dashboard.backend.security_policy import evaluate_request


ROOT = Path(__file__).resolve().parents[1]


def test_anonymous_dashboard_reads_are_allowed_when_api_key_disabled():
    decision = evaluate_request(
        method="GET",
        path="/api/state",
        require_api_key=False,
        api_key_configured=False,
        dashboard_access=False,
    )
    assert decision.allowed is True
    assert decision.status_code == 200


def test_anonymous_mutations_fail_closed_when_api_key_disabled():
    decision = evaluate_request(
        method="POST",
        path="/api/paper/tick",
        require_api_key=False,
        api_key_configured=False,
        dashboard_access=False,
    )
    assert decision.allowed is False
    assert decision.status_code == 503
    assert decision.code == "AUTH_REQUIRED_FOR_MUTATION"


def test_frontend_has_no_dashboard_api_key_gate():
    app = (ROOT / "dashboard/frontend/src/App.tsx").read_text(encoding="utf-8")
    assert "LoginPage" not in app
    assert "useAuth" not in app
    assert "AuthGate" not in app


def test_gcp_auto_deploy_is_public_readonly_and_unmounts_api_key():
    deploy = (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
    assert '("REQUIRE_API_KEY", "false")' in deploy
    assert 'env_map.pop("API_KEY", None)' in deploy
    assert "DASHBOARD_PUBLIC_READONLY enforced" in deploy
    assert "API_KEY_SECRET_ID" not in deploy


def test_manual_gcp_deploy_removes_dashboard_api_key_secret():
    deploy = (ROOT / "deploy/gcp/deploy_web.sh").read_text(encoding="utf-8")
    assert "REQUIRE_API_KEY=false" in deploy
    assert "--remove-secrets=API_KEY" in deploy
    assert "API_KEY_SECRET_ID" not in deploy


def test_approved_deploy_workflow_proves_no_key_access_live_off_and_actual_ui_visual():
    workflow = (ROOT / ".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
    deploy = (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
    proof = (ROOT / "scripts/gcp_public_dashboard_runtime_proof.py").read_text(encoding="utf-8")

    # One canonical service mutation owns final env/scaling/secrets; the
    # workflow verifies that revision instead of creating a second revision.
    assert "CANONICAL_RUNTIME_SPEC" in workflow
    assert "CANONICAL_RUNTIME_SPEC" in deploy
    assert "gcloud run services update" not in workflow
    assert '("REQUIRE_API_KEY", "false")' in deploy
    assert 'env_map.pop("API_KEY", None)' in deploy
    assert '("DHAN_TOKEN_SOURCE", "gcp-secret-manager-dynamic")' in deploy
    assert '"scaling": {"minInstanceCount": 0, "maxInstanceCount": 1}' in deploy

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

    # Final live-off configuration is owned by the canonical deploy script and
    # rechecked by workflow verification/runtime proof.
    assert '("LIVE_TRADING_ENABLED", "0")' in deploy
    assert '("SYSTEM3_LIVE_TRADING_ALLOWED", "0")' in deploy
    assert '("AUTO_EXECUTE_TRADES", "0")' in deploy
    assert "LIVE_TRADING_ENABLED" in workflow
    assert "SYSTEM3_LIVE_TRADING_ALLOWED" in workflow
    assert "AUTO_EXECUTE_TRADES" in workflow


def test_no_extra_workflow_added_for_dashboard_proof():
    assert not (ROOT / ".github/workflows/public-paper-dashboard-proof.yml").exists()
