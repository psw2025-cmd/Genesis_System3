from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "audit" / "USER_RECOMMDATION_FOR _AGENT_UPDATE_RUNBOOK"


def test_ruhi_reference_pack_is_discoverable_and_fail_closed():
    readme = (REFERENCE / "README_RUHI.md").read_text(encoding="utf-8")
    rule = (ROOT / "docs" / "RUHI_RULE_V2.md").read_text(encoding="utf-8")
    assert "SYSTEM3_RUHI_USER_REFERENCE_V1" in readme
    assert "#RUHI" in readme
    assert "design references" in readme
    assert "UNVERIFIED" in readme
    assert "https://token.actions.githubus" in readme
    assert "Dhan remains the exclusive broker/live Indian market authority" in readme
    assert "USER_RECOMMDATION_FOR _AGENT_UPDATE_RUNBOOK/README_RUHI.md" in rule
    assert "Generated" in rule
    assert "images, percentages and historical narratives" in rule


def test_original_user_reference_files_are_preserved():
    expected = {
        "AGENT_CORDINATION_CLOUD.txt",
        "FOR_INFO_FOR_IMPROMENT.txt",
        "Copilot_20260824_002334.png",
        "Copilot_20260824_002608.png",
        "types-of-ai-trading-systems.png",
    }
    names = {path.name for path in REFERENCE.iterdir() if path.is_file()}
    assert expected <= names
    source = (REFERENCE / "FOR_INFO_FOR_IMPROMENT.txt").read_text(
        encoding="utf-8", errors="replace"
    )
    assert source.rstrip().endswith("https://token.actions.githubus")
