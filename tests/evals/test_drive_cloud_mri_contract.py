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
    assert MODULE.secret_like_path(Path("C:/safe/api_key/private/report.csv"))
    assert MODULE.secret_like_path(Path("D:/credentials/ordinary-name.csv"))


def test_public_rows_never_emit_private_absolute_prefixes():
    laptop = {
        "path": Path("C:/Users/ADMIN/private/project/report.csv"),
        "name": "report.csv",
        "size": 10,
        "mtime": 0,
        "hash": None,
    }
    cloud = dict(laptop, rel="reports/report.csv")
    laptop_row = MODULE.row(laptop, "Laptop", "Missing in Cloud", "test")
    cloud_row = MODULE.row(cloud, "Cloud", "Already Synced", "test")
    assert laptop_row[MODULE.COLUMNS[1]] == "<C_DRIVE>/[REDACTED]/report.csv"
    assert "Users" not in laptop_row[MODULE.COLUMNS[1]]
    assert cloud_row[MODULE.COLUMNS[1]] == "reports/report.csv"


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
    assert "RUHI/RHUI execution and dashboard truth law" in text
    assert "docs/RUHI_RULE_V2.md" in text
