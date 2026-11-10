from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dashboard" / "frontend" / "src" / "components" / "GenesisTab.tsx"


def test_genesis_uses_rank_rows_as_neutral_evidence_without_inventing_direction():
    text = SOURCE.read_text(encoding="utf-8")
    assert "gainRank?.latest?.rankings" in text
    assert "RANK EVIDENCE · ${topRankedUnderlying}" in text
    assert "data.brain?.directional_bias" in text
    assert "otherwise current durable rank evidence is shown neutrally" in text
