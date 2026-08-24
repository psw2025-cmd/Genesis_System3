from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = spec_from_file_location("drive_mri", ROOT / "scripts" / "system3_drive_cloud_mri.py")
MODULE = module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_exact_user_csv_contract():
    assert MODULE.COLUMNS == [
        "File Name",
        "Path",
        "Drive",
        "Repo (Laptop/Cloud)",
        "Status (Missing in Cloud / Duplicate / Outdated / Already Synced)",
        "Reason (Why missing or outdated)",
        "Improvement Potential (Prediction accuracy, dashboard, orchestration)",
        "Global Best Practice Comparison",
        "Better Solution Reference (tools, workflows, datasets)",
    ]


def test_secret_and_noise_exclusions_are_fail_closed():
    assert MODULE.SECRET_RE.search("broker-access-token.txt")
    assert MODULE.SECRET_RE.search("api_key.json")
    assert "node_modules" in MODULE.SKIP_DIRS
    assert ".git" in MODULE.SKIP_DIRS
    assert "__pycache__" in MODULE.SKIP_DIRS


def test_recommendations_route_by_asset_role():
    assert "Prediction" in MODULE.useful_fields(Path("history.parquet"))[0]
    assert "Dashboard" in MODULE.useful_fields(Path("chart.tsx"))[0]
    assert "Orchestration" in MODULE.useful_fields(Path("runner.py"))[0]


def test_runbook_locks_cloud_authority_and_large_report_handling():
    text = (ROOT / "docs" / "control_plane" / "SYSTEM3_AGENT_RUNBOOK.md").read_text(encoding="utf-8")
    assert "Drive-to-cloud MRI and single-authority import law" in text
    assert "Laptop drives are read-only discovery/input surfaces" in text
    assert "Large inventories" in text and "GitHub release asset" in text
    assert "never bulk-copy laptop history" in text
