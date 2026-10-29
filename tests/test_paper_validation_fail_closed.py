"""Guard against manufactured paper-trading certification."""
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_paper_validation.py"


def test_paper_validation_fails_closed_without_real_evidence(tmp_path):
    # The script must not create validation output just because it is invoked.
    before = sorted((ROOT / "state" / "paper_validations").glob("*.json")) if (ROOT / "state" / "paper_validations").exists() else []
    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=tmp_path, capture_output=True, text=True, timeout=20)
    after = sorted((ROOT / "state" / "paper_validations").glob("*.json")) if (ROOT / "state" / "paper_validations").exists() else []
    assert result.returncode != 0
    assert "NOT VERIFIED" in result.stderr
    assert before == after


def test_no_hardcoded_pass_metrics_in_production_entrypoint():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "COSTED_WALK_FORWARD_PASS" not in text
    assert "PAPER_TR_20261029_" not in text
    assert '"spearman_correlation": 0.78' not in text
    assert '"walk_forward_trade_count": 24' not in text
