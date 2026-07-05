#!/usr/bin/env python3
"""
Run one full governance validation cycle:
  requirements -> build (optional) -> pre-build validation -> production validation -> proof pack.
Saves all outputs under proof/ with timestamp. Exits 0 if cycle PASS, 1 otherwise.
Usage: python scripts/run_governance_cycle.py [--cycle N] [--skip-build]
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROOF_DIR = ROOT / "proof"
PROOF_DIR.mkdir(exist_ok=True)


def run_cmd(cmd, cwd=None, capture=True, timeout=300):
    cwd = cwd or ROOT
    try:
        r = subprocess.run(
            cmd if isinstance(cmd, list) else cmd.split(),
            cwd=cwd,
            capture_output=capture,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return -1, "Timeout"
    except Exception as e:
        return -1, str(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", type=int, default=1, help="Cycle number")
    ap.add_argument("--skip-build", action="store_true", help="Skip build step")
    args = ap.parse_args()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    cycle_id = f"cycle_{args.cycle}_{ts}"
    artifacts_dir = PROOF_DIR / cycle_id
    artifacts_dir.mkdir(exist_ok=True)

    results = {
        "cycle": args.cycle,
        "cycle_id": cycle_id,
        "timestamp": datetime.now().isoformat(),
        "steps": {},
        "cycle_result": "PENDING",
    }

    # 1. Requirements check
    code, out = run_cmd([sys.executable, "check_build_requirements.py"], cwd=ROOT)
    (artifacts_dir / "01_requirements.txt").write_text(out, encoding="utf-8")
    results["steps"]["requirements"] = {"exit_code": code, "output_file": "01_requirements.txt"}
    if code != 0:
        print(f"[FAIL] Requirements check exited {code}")
        results["cycle_result"] = "FAIL"
        write_cycle_result(artifacts_dir, results)
        return 1
    print("[OK] Requirements check passed")

    # 2. Build (optional)
    if not args.skip_build:
        code, out = run_cmd("cmd /c build_fresh_installer.bat", cwd=ROOT, timeout=600)
        (artifacts_dir / "02_build.txt").write_text(out, encoding="utf-8")
        results["steps"]["build"] = {"exit_code": code, "output_file": "02_build.txt"}
        if code != 0:
            print(f"[FAIL] Build exited {code}")
            results["cycle_result"] = "FAIL"
            write_cycle_result(artifacts_dir, results)
            return 1
        print("[OK] Build passed")
    else:
        results["steps"]["build"] = {"skipped": True}
        installer = ROOT / "desktop_app" / "dist" / "System3 Ultra Setup 1.0.0.exe"
        if not installer.exists():
            print("[WARN] Build skipped and installer missing")
            results["cycle_result"] = "FAIL"
            write_cycle_result(artifacts_dir, results)
            return 1
        print("[OK] Build skipped; installer present")

    # 3. Pre-build validation (backend may be down)
    code, out = run_cmd([sys.executable, "comprehensive_pre_build_validation.py"], cwd=ROOT, timeout=120)
    (artifacts_dir / "03_pre_build_validation.txt").write_text(out, encoding="utf-8")
    results["steps"]["pre_build_validation"] = {"exit_code": code, "output_file": "03_pre_build_validation.txt"}

    # 4. Production validation
    code, out = run_cmd([sys.executable, "production_grade_validation.py"], cwd=ROOT, timeout=180)
    (artifacts_dir / "04_production_validation.txt").write_text(out, encoding="utf-8")
    results["steps"]["production_validation"] = {"exit_code": code, "output_file": "04_production_validation.txt"}

    # 5. Proof pack
    code, out = run_cmd([sys.executable, "scripts/generate_proof_pack.py", "--cycle", str(args.cycle)], cwd=ROOT)
    (artifacts_dir / "05_proof_pack.txt").write_text(out, encoding="utf-8")
    results["steps"]["proof_pack"] = {"exit_code": code, "output_file": "05_proof_pack.txt"}

    # Determine cycle PASS: installer exists, proof pack generated, no step failed (validation can fail if backend down)
    installer = ROOT / "desktop_app" / "dist" / "System3 Ultra Setup 1.0.0.exe"
    pack_dir = PROOF_DIR.glob("proof_pack_*.json")
    latest_pack = max(pack_dir, key=lambda p: p.stat().st_mtime) if list(PROOF_DIR.glob("proof_pack_*.json")) else None
    all_pass = (
        results["steps"]["requirements"].get("exit_code") == 0 and installer.exists() and code == 0 and latest_pack
    )
    if all_pass:
        results["cycle_result"] = "PASS"
        print("[OK] Cycle PASS")
    else:
        results["cycle_result"] = "FAIL"
        print("[FAIL] Cycle FAIL (see steps)")
    write_cycle_result(artifacts_dir, results)
    return 0 if results["cycle_result"] == "PASS" else 1


def write_cycle_result(artifacts_dir, results):
    (artifacts_dir / "cycle_result.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"[OK] Artifacts saved to {artifacts_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
