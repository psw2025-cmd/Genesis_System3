from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_identity_preflight_is_non_admin_and_candidate_authoritative():
    text = (ROOT / "scripts/gcp_runtime_iam_preflight.py").read_text(encoding="utf-8")
    assert 'FIRESTORE_ROLE = "roles/datastore.user"' in text
    assert 'genesis-system3-web@{PROJECT}.iam.gserviceaccount.com' in text
    assert '"service-accounts",\n            "describe"' in text
    assert "projects get-iam-policy" not in text
    assert '"projects",\n            "get-iam-policy"' not in text
    assert "projects add-iam-policy-binding" not in text
    assert '"projects",\n            "add-iam-policy-binding"' not in text
    assert '"project_iam_introspected": False' in text
    assert '"project_iam_mutated": False' in text
    assert '"permission_proof_authority": "zero_traffic_candidate_startup"' in text
    assert '"secret_payloads_accessed": False' in text
    assert '"live_trading_changed": False' in text
    # Compatibility marker remains for the permanent workflow static gate only.
    assert 'STATIC_COMPATIBILITY_MARKER = "FIRESTORE_RUNTIME_IAM_OK"' in text


def test_bootstrap_owns_dedicated_web_runtime_firestore_role():
    text = (ROOT / "deploy/gcp/bootstrap_github_wif.sh").read_text(encoding="utf-8")
    assert 'WEB_RUNTIME_SA_NAME="${WEB_RUNTIME_SA_NAME:-genesis-system3-web}"' in text
    assert '--role="roles/datastore.user"' in text
    assert 'serviceAccount:${WEB_RUNTIME_SA}' in text
    assert "dhan-pin" not in _web_runtime_secret_block(text)
    assert "dhan-totp-secret" not in _web_runtime_secret_block(text)


def _web_runtime_secret_block(text: str) -> str:
    start = text.index("for SECRET in system3-dhan-client-id dhan-access-token system3-dashboard-worker-push-token")
    end = text.index("# Deployment identity may administer", start)
    return text[start:end]


def test_canonical_deployer_makes_zero_traffic_candidate_prove_required_firestore():
    text = (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
    assert '("SYSTEM3_STATE_BACKEND", "firestore")' in text
    assert '("SYSTEM3_STATE_BACKEND_REQUIRED", "1")' in text
    assert 'RUNTIME_SA = f"genesis-system3-web@{PROJECT}.iam.gserviceaccount.com"' in text
    assert '"--no-traffic"' in text
    assert "_wait_revision_ready" in text
    assert "gcp_failed_revision_forensic.py" in text
    assert "PREVIOUS_TRAFFIC_RESTORED" in text


def test_required_firestore_startup_is_fail_closed_and_exercises_read_write_path():
    state_store = (ROOT / "dashboard/backend/runtime_state_store.py").read_text(encoding="utf-8")
    app = (ROOT / "dashboard/backend/app.py").read_text(encoding="utf-8")
    assert 'raise RuntimeError("Required Firestore state load failed")' in state_store
    assert 'raise RuntimeError("Required Firestore state write failed")' in state_store
    assert "_state_store.load_state()" in state_store
    # Import-time SSOT initialization loads Firestore and sync_from_files writes
    # through update_state(), so a required backend permission failure prevents
    # the candidate app from reaching Ready.
    assert "state_store = get_state_store(OUTPUTS_DIR)" in app
    assert "state_store.sync_from_files()" in app
