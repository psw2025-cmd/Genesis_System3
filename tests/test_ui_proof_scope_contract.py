from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / "scripts" / "frontend_local_runtime_smoke.py"
PRODUCTION = ROOT / "scripts" / "gcp_ui_tab_visual_proof.py"


def test_local_browser_smoke_is_explicitly_non_production() -> None:
    source = LOCAL.read_text(encoding="utf-8")
    required = [
        'PROOF_SCOPE = "LOCAL_NON_PRODUCTION"',
        "PRODUCTION_AUTHORITY = False",
        "BROKER_CONNECTIVITY_PROVEN = False",
        '"production_claim_allowed": False',
        '"served_from": "127.0.0.1_vite_preview"',
    ]
    for marker in required:
        assert marker in source, marker


def test_local_smoke_cannot_emit_connected_or_production_claim() -> None:
    source = LOCAL.read_text(encoding="utf-8")
    forbidden = [
        'BROKER_CONNECTIVITY_PROVEN = True',
        'PRODUCTION_AUTHORITY = True',
        '"production_claim_allowed": True',
    ]
    for marker in forbidden:
        assert marker not in source, marker


def test_gcp_visual_proof_remains_deployed_authority_path() -> None:
    source = PRODUCTION.read_text(encoding="utf-8")
    required = [
        '"source": "real_deployed_cloud_run_ui"',
        'EXPECTED_SHA = os.getenv("GITHUB_SHA", "").strip()',
        '"gcloud", "run", "services", "describe"',
        "https://",
    ]
    for marker in required:
        assert marker in source, marker


def test_production_and_local_proof_paths_are_structurally_distinct() -> None:
    local = LOCAL.read_text(encoding="utf-8")
    production = PRODUCTION.read_text(encoding="utf-8")
    assert "127.0.0.1_vite_preview" in local
    assert '"source": "real_deployed_cloud_run_ui"' in production
    assert '"source": "real_deployed_cloud_run_ui"' not in local
