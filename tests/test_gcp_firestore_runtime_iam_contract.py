from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_iam_preflight_is_narrow_and_fail_closed():
    text = (ROOT / "scripts/gcp_runtime_iam_preflight.py").read_text(encoding="utf-8")
    assert 'FIRESTORE_ROLE = "roles/datastore.user"' in text
    assert 'genesis-system3-web@{PROJECT}.iam.gserviceaccount.com' in text
    assert "projects add-iam-policy-binding" not in text  # command is tokenized, not shell-injected
    assert '"projects",\n            "add-iam-policy-binding"' in text
    assert "SYSTEM3_STATE_BACKEND_REQUIRED" in text
    assert "LIVE_TRADING" in text
    assert "secret_payloads_accessed" in text
    assert "FIRESTORE_RUNTIME_IAM_PRECHECK_FAILED" in text


def test_bootstrap_provisions_dedicated_web_runtime_firestore_role():
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


def test_canonical_deployer_keeps_required_firestore_state():
    text = (ROOT / "scripts/gcp_cloud_run_auto_deploy.py").read_text(encoding="utf-8")
    assert '("SYSTEM3_STATE_BACKEND", "firestore")' in text
    assert '("SYSTEM3_STATE_BACKEND_REQUIRED", "1")' in text
    assert 'RUNTIME_SA = f"genesis-system3-web@{PROJECT}.iam.gserviceaccount.com"' in text
