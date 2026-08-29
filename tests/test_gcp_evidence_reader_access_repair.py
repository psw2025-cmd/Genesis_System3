import json
from pathlib import Path

SCRIPT = Path("scripts/gcp_evidence_reader_access_repair.py").read_text(encoding="utf-8")
BASELINE = json.loads(Path("deploy/gcp/system3_evidence_reader_baseline.json").read_text(encoding="utf-8"))
RECON = Path("scripts/system3_ultra_mri_reconcile.py").read_text(encoding="utf-8")


def test_evidence_reader_roles_are_read_only_and_exact():
    expected = {
        "roles/iam.serviceAccountViewer",
        "roles/iam.workloadIdentityPoolViewer",
        "roles/storage.viewer",
        "roles/cloudsql.viewer",
        "roles/cloudfunctions.viewer",
        "roles/pubsub.viewer",
    }
    assert set(BASELINE["roles"]) == expected
    assert set(BASELINE["forbidden_roles"]).isdisjoint(expected)
    assert "secretAccessor" not in " ".join(BASELINE["roles"])


def test_repair_is_bounded_to_one_member_and_no_secret_payload_actions():
    assert "ALLOWED_MEMBER" in SCRIPT
    assert "ALLOWED_ROLES" in SCRIPT
    assert "add-iam-policy-binding" in SCRIPT
    assert "secretmanager versions access" not in SCRIPT
    assert "service-account keys create" not in SCRIPT
    assert '"live_trading_changed": False' in SCRIPT
    assert '"order_action_performed": False' in SCRIPT


def test_browser_reconciler_adds_repo_root_before_scripts_import():
    assert "REPO_ROOT = Path(__file__).resolve().parents[1]" in RECON
    assert "sys.path.insert(0, str(REPO_ROOT))" in RECON
    assert "import scripts.gcp_public_dashboard_runtime_proof as proof_module" in RECON
