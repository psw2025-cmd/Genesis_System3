from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "system3_dhan_issuer_mri_bundle.ps1"


def test_mri_bundle_is_read_only_and_redacted() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "cloud_mutations = $false" in text
    assert "broker_mutations = $false" in text
    assert "order_calls = $false" in text
    assert "raw_token_exposed = $false" in text
    assert "pin_exposed = $false" in text
    assert "totp_exposed = $false" in text
    assert "secrets versions access" not in text.lower()
    assert "add-iam-policy-binding" not in text.lower()
    assert "remove-iam-policy-binding" not in text.lower()
    assert "jobs execute" not in text.lower()


def test_mri_bundle_covers_all_three_truth_layers() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for required in (
        "Get-CimInstance Win32_Process",
        "Get-ScheduledTask",
        'Safe-JsonCli gh',
        'Safe-JsonCli gcloud',
        '"/api/broker/truth"',
        '"/api/batch/chains?symbols=NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY"',
    ):
        assert required in text


def test_mri_bundle_can_target_actual_operator_checkout() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert '[string]$RepoPath = ""' in text
    assert "Resolve-Path -LiteralPath $RepoPath" in text
