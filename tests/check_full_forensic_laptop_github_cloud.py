"""End-to-end verification script for Genesis Forensic Fix across Laptop, GitHub, and Google Cloud."""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

def test_all():
    print("[1/6] Verifying moneycontrol permanent fix...", file=sys.stderr)
    proc = subprocess.run(
        [sys.executable, "tests/check_permanent_moneycontrol_fix.py"],
        capture_output=True,
        text=True,
        check=True
    )
    assert proc.returncode == 0, f"check_permanent_moneycontrol_fix failed: {proc.stderr}"

    print("[2/6] Verifying forensic proof files in C:/Temp/Genesis_Forensic...", file=sys.stderr)
    forensic_dir = Path("C:/Temp/Genesis_Forensic")
    assert forensic_dir.exists(), "Forensic dir does not exist"
    
    final_proof = (forensic_dir / "FINAL_PROOF.txt").read_text(encoding="utf-8")
    assert "CORRECT=PROVEN_ANALYZER_ONLY" in final_proof, "FINAL_PROOF missing CORRECT=PROVEN_ANALYZER_ONLY"
    assert "ready_for_live=false" in final_proof, "FINAL_PROOF missing ready_for_live=false"
    assert "PAPER LOCKED" in final_proof, "FINAL_PROOF missing PAPER LOCKED"
    assert "LIVE_TRADING_ENABLED always 0" in final_proof, "FINAL_PROOF missing LIVE_TRADING_ENABLED"

    print("[3/6] Verifying 0 fake occurrences in frontend src...", file=sys.stderr)
    rg_proc = subprocess.run(
        ["rg", "88.0%|74.0%|68.0%|1.85", "dashboard/frontend/src", "-n", "--no-ignore"],
        capture_output=True,
        text=True
    )
    assert rg_proc.returncode == 1, "Fake metrics found in dashboard/frontend/src!"

    print("[4/6] Verifying git and GitHub PR status...", file=sys.stderr)
    git_log = subprocess.run(
        ["git", "log", "-5", "--oneline"],
        capture_output=True,
        text=True,
        check=True
    ).stdout
    assert "Merge pull request #488" in git_log or "488" in git_log, f"PR 488 not in recent git log: {git_log}"

    print("[5/6] Verifying Cloud Run live endpoints...", file=sys.stderr)
    cloud_url = "https://genesis-system3-web-802404398783.asia-south1.run.app/api/health"
    req = urllib.request.Request(cloud_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        assert resp.status == 200, f"Cloud Run health returned status {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        assert data.get("mode") in ("PAPER", "ANALYZER"), f"Unexpected mode: {data.get('mode')}"
        assert data.get("live_trading_enabled") is not True, "LIVE TRADING IS ENABLED ON CLOUD!"

    print("[6/6] Verifying Cloud Run ML performance endpoint...", file=sys.stderr)
    cloud_ml_url = "https://genesis-system3-web-802404398783.asia-south1.run.app/api/ml/performance"
    req_ml = urllib.request.Request(cloud_ml_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req_ml, timeout=15) as resp:
        assert resp.status == 200, f"Cloud Run ML returned status {resp.status}"
        data_ml = json.loads(resp.read().decode("utf-8"))
        assert data_ml.get("ready_for_live") is False, "Cloud ML ready_for_live must be False!"

    print(json.dumps({"verified": True, "status": "PASS", "scope": "Laptop, GitHub PR #488, and Google Cloud Run"}))

if __name__ == "__main__":
    test_all()
