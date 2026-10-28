import json
import os
import re
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent

    # Check 1: GenesisTab.tsx
    genesis_tab = (root / "dashboard" / "frontend" / "src" / "components" / "GenesisTab.tsx").read_text(encoding="utf-8-sig")
    assert "N/A - NO_PREDICTION" in genesis_tab, "Missing 'N/A - NO_PREDICTION' in GenesisTab.tsx"
    assert "1.85" not in genesis_tab, "Found '1.85' in GenesisTab.tsx"

    # Check 2: SystemTruthControl.tsx
    truth_control = (root / "dashboard" / "frontend" / "src" / "components" / "SystemTruthControl.tsx").read_text(encoding="utf-8-sig")
    assert "candidate_rows zero not fabricated into PASS" in truth_control, "Missing candidate_rows message in SystemTruthControl.tsx"
    assert "read-path presence does not prove completed lifecycle" in truth_control, "Missing read-path presence message in SystemTruthControl.tsx"
    assert "same Zustand state bounded read-only poller - no duplicate burst" in truth_control, "Missing Zustand poller message in SystemTruthControl.tsx"

    # Check 3: Forensic Artifacts
    forensic_dir = Path("C:/Temp/Genesis_Forensic")
    assert forensic_dir.is_dir(), f"Missing forensic directory {forensic_dir}"

    f01 = forensic_dir / "01_fake.txt"
    assert f01.exists() and f01.stat().st_size == 0, "01_fake.txt missing or not empty"

    f02 = forensic_dir / "02_blocked.txt"
    assert f02.exists() and f02.stat().st_size > 0, "02_blocked.txt missing or empty"
    t02 = f02.read_text(encoding="utf-8-sig", errors="ignore")
    assert "NO_PREDICTION_SOURCE_FOUND" in t02 or "REAL_PAPER_LIFECYCLE_NOT_PROVEN" in t02, "Blocker patterns not found in 02_blocked.txt"

    f04 = forensic_dir / "04_cloud.json"
    assert f04.exists() and f04.stat().st_size > 0, "04_cloud.json missing or empty"
    cloud_data = json.loads(f04.read_text(encoding="utf-8-sig"))
    assert cloud_data.get("performance", {}).get("status") == "PROVEN_ANALYZER_ONLY", "Cloud status not PROVEN_ANALYZER_ONLY"

    f05 = forensic_dir / "05_verify.txt"
    assert f05.exists() and f05.stat().st_size == 0, "05_verify.txt missing or not empty"

    proof = forensic_dir / "FINAL_AGY_FIX_PROOF.txt"
    assert proof.exists() and proof.stat().st_size > 0, "FINAL_AGY_FIX_PROOF.txt missing"
    proof_text = proof.read_text(encoding="utf-8-sig")
    assert "Security: LIVE_TRADING_ENABLED always 0" in proof_text, "Missing safety lock statement in FINAL_AGY_FIX_PROOF.txt"

    print(json.dumps({"verified": True, "status": "PASS"}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
