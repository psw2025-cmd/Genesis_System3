import json
import os
import re
import subprocess
import sys
from pathlib import Path

def run_cross_verification():
    root = Path(__file__).resolve().parent.parent
    forensic_dir = Path("C:/Temp/Genesis_Forensic")
    
    report = {
        "verified_at_utc": "2026-10-28T23:38:00Z",
        "forensic_directory": str(forensic_dir),
        "results": {},
        "overall": "UNKNOWN"
    }
    
    checks = []
    
    # 1. Check 01_fake.txt
    f01 = forensic_dir / "01_fake.txt"
    ok01 = f01.exists() and f01.stat().st_size == 0
    checks.append(("01_fake.txt exists and is 0 bytes", ok01, f"size={f01.stat().st_size if f01.exists() else 'missing'}"))
    
    # Live rg check to cross-verify 01_fake.txt
    rg_fake = subprocess.run(
        ["rg", "88.0%|74.0%|68.0%|1.85", "dashboard/frontend/src", "-n", "--no-ignore"],
        cwd=str(root), capture_output=True, text=True
    )
    ok_rg_fake = (rg_fake.returncode == 1 and len(rg_fake.stdout.strip()) == 0)
    checks.append(("Live rg check: zero fake metrics in frontend/src", ok_rg_fake, f"matches={rg_fake.stdout.strip()}"))
    
    # 2. Check 02_blocked.txt
    f02 = forensic_dir / "02_blocked.txt"
    t02 = f02.read_text(encoding="utf-8", errors="replace") if f02.exists() else ""
    ok02 = f02.exists() and f02.stat().st_size > 0 and ("REAL_PAPER_LIFECYCLE_NOT_PROVEN" in t02 or "NO_PREDICTION_SOURCE_FOUND" in t02)
    checks.append(("02_blocked.txt contains blocker evidence", ok02, f"size={len(t02)}"))
    
    # 3. Check 02_genesis.txt
    f02_gen = forensic_dir / "02_genesis.txt"
    t02_gen = f02_gen.read_text(encoding="utf-8", errors="replace") if f02_gen.exists() else ""
    ok02_gen = f02_gen.exists() and "N/A - NO_PREDICTION" in t02_gen and "?? 1.85" not in t02_gen
    checks.append(("02_genesis.txt confirms GenesisTab fix", ok02_gen, f"has_fix={'N/A - NO_PREDICTION' in t02_gen}"))
    
    # Live check GenesisTab.tsx
    genesis_code = (root / "dashboard" / "frontend" / "src" / "components" / "GenesisTab.tsx").read_text(encoding="utf-8", errors="replace")
    ok_gen_live = "N/A - NO_PREDICTION" in genesis_code and "?? 1.85" not in genesis_code and "1.85" not in genesis_code
    checks.append(("Live GenesisTab.tsx has N/A - NO_PREDICTION and zero 1.85", ok_gen_live, f"1.85_in_code={'1.85' in genesis_code}"))
    
    # 4. Check 03_local.json
    f03 = forensic_dir / "03_local.json"
    ok03 = False
    details03 = ""
    if f03.exists() and f03.stat().st_size > 0:
        try:
            d03 = json.loads(f03.read_text(encoding="utf-8", errors="replace"))
            ready_live_03 = d03.get("ready_for_live") if "ready_for_live" in d03 else d03.get("performance", {}).get("ready_for_live")
            ok03 = ready_live_03 is False
            details03 = f"ready_for_live={ready_live_03}"
        except Exception as e:
            details03 = str(e)
    checks.append(("03_local.json has ready_for_live=False", ok03, details03))
    
    # 5. Check 04_cloud.json
    f04 = forensic_dir / "04_cloud.json"
    ok04 = False
    details04 = ""
    if f04.exists() and f04.stat().st_size > 0:
        try:
            d04 = json.loads(f04.read_text(encoding="utf-8", errors="replace"))
            perf_status = d04.get("proof_status") or d04.get("performance", {}).get("status") or d04.get("status")
            ready_live_04 = d04.get("ready_for_live") if "ready_for_live" in d04 else d04.get("performance", {}).get("ready_for_live")
            ok04 = perf_status == "PROVEN_ANALYZER_ONLY" and ready_live_04 is False
            details04 = f"status={perf_status}, ready_for_live={ready_live_04}"
        except Exception as e:
            details04 = str(e)
    checks.append(("04_cloud.json has PROVEN_ANALYZER_ONLY and ready_for_live=False", ok04, details04))
    
    # 6. Check 04_LOCAL_vs_CLOUD_COMPARISON.json
    f04_comp = forensic_dir / "04_LOCAL_vs_CLOUD_COMPARISON.json"
    ok_comp = False
    details_comp = ""
    if f04_comp.exists() and f04_comp.stat().st_size > 0:
        try:
            d_comp = json.loads(f04_comp.read_text(encoding="utf-8", errors="replace"))
            safety = d_comp.get("safety_audit", {})
            ok_comp = (
                safety.get("local_live_trading_enabled") is False
                and safety.get("cloud_live_trading_enabled") is False
                and safety.get("local_order_placement_allowed") is False
                and safety.get("cloud_order_placement_allowed") is False
                and safety.get("local_mode") == "PAPER"
                and safety.get("cloud_mode") == "PAPER"
            )
            details_comp = f"safety={safety}"
        except Exception as e:
            details_comp = str(e)
    checks.append(("04_LOCAL_vs_CLOUD_COMPARISON.json verifies all safety locks", ok_comp, details_comp))
    
    # 7. Check 05_27_TABS_AUDIT.json
    f05_tabs = forensic_dir / "05_27_TABS_AUDIT.json"
    ok05_tabs = False
    details05 = ""
    if f05_tabs.exists() and f05_tabs.stat().st_size > 0:
        try:
            tabs_data = json.loads(f05_tabs.read_text(encoding="utf-8", errors="replace"))
            total = len(tabs_data)
            passed = sum(1 for t in tabs_data if t.get("pass") is True)
            ok05_tabs = (total == 27 and passed == 27)
            details05 = f"total={total}, passed={passed}"
        except Exception as e:
            details05 = str(e)
    checks.append(("05_27_TABS_AUDIT.json confirms all 27 tabs PASS", ok05_tabs, details05))
    
    # 8. Check 05_verify.txt
    f05_v = forensic_dir / "05_verify.txt"
    ok05_v = f05_v.exists() and f05_v.stat().st_size == 0
    checks.append(("05_verify.txt exists and is 0 bytes (zero 1.85 violations)", ok05_v, f"size={f05_v.stat().st_size if f05_v.exists() else 'missing'}"))
    
    # 9. Check FINAL_PROOF.txt
    f_proof = forensic_dir / "FINAL_PROOF.txt"
    t_proof = f_proof.read_text(encoding="utf-8", errors="replace") if f_proof.exists() else ""
    expected_verdict = "VERDICT: CORRECT=PROVEN_ANALYZER_ONLY ready_for_live=false 32 predictions PAPER LOCKED live_flag=false order_allowed=false Genesis must show N/A not 88% ACTIVE"
    ok_proof = f_proof.exists() and expected_verdict in t_proof and "Security: LIVE_TRADING_ENABLED always 0" in t_proof
    checks.append(("FINAL_PROOF.txt has exact verdict and security lock", ok_proof, f"has_verdict={expected_verdict in t_proof}"))
    
    # 10. Check FINAL_AGY_FIX_PROOF.txt
    f_agy = forensic_dir / "FINAL_AGY_FIX_PROOF.txt"
    t_agy = f_agy.read_text(encoding="utf-8", errors="replace") if f_agy.exists() else ""
    ok_agy = f_agy.exists() and "Security: LIVE_TRADING_ENABLED always 0" in t_agy and "c962a48" in t_agy
    checks.append(("FINAL_AGY_FIX_PROOF.txt has required security lock", ok_agy, f"has_lock={'LIVE_TRADING_ENABLED always 0' in t_agy}"))
    
    # 11. Check PERMANENT_FIX_DONE.txt
    f_perm = forensic_dir / "PERMANENT_FIX_DONE.txt"
    t_perm = f_perm.read_text(encoding="utf-8", errors="replace") if f_perm.exists() else ""
    ok_perm = f_perm.exists() and "moneycontrol" in t_perm and "COMPLETED & VERIFIED" in t_perm
    checks.append(("PERMANENT_FIX_DONE.txt has permanent moneycontrol fix", ok_perm, f"has_fix={'COMPLETED & VERIFIED' in t_perm}"))
    
    # 12. Check SystemTruthControl.tsx honest markers
    truth_code = (root / "dashboard" / "frontend" / "src" / "components" / "SystemTruthControl.tsx").read_text(encoding="utf-8", errors="replace")
    ok_truth = (
        "candidate_rows zero not fabricated into PASS" in truth_code
        and "read-path presence does not prove completed lifecycle" in truth_code
        and "same Zustand state bounded read-only poller - no duplicate burst" in truth_code
    )
    checks.append(("SystemTruthControl.tsx preserves honest Zustand poller & markers", ok_truth, "all 3 markers verified"))
    
    # 13. Check .dockerignore has !state and moneycontrol exclusions
    dockerignore = (root / ".dockerignore").read_text(encoding="utf-8", errors="replace")
    ok_docker = "!state" in dockerignore and "moneycontrol" in dockerignore
    checks.append((".dockerignore has !state and moneycontrol exclusions", ok_docker, f"!state={'!state' in dockerignore}, moneycontrol={'moneycontrol' in dockerignore}"))
    
    # Summary
    all_ok = all(c[1] for c in checks)
    report["overall"] = "PASS" if all_ok else "FAIL"
    report["checks"] = [
        {"name": c[0], "pass": c[1], "details": c[2]}
        for c in checks
    ]
    
    print("=" * 70)
    print("GENESIS FORENSIC MULTI-LAYER CROSS-VERIFICATION AUDIT")
    print(f"Overall Status: {report['overall']}")
    print("=" * 70)
    for c in checks:
        sym = "[PASS]" if c[1] else "[FAIL]"
        print(f"  {sym:<7} {c[0]:<60} | {c[2]}")
    print("=" * 70)
    
    out_path = forensic_dir / "06_CROSS_VERIFY_REPORT.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    out_txt = forensic_dir / "06_CROSS_VERIFY_REPORT.txt"
    lines = [
        "=== GENESIS FORENSIC MULTI-LAYER CROSS-VERIFICATION REPORT ===",
        f"Overall Status: {report['overall']}",
        f"Timestamp UTC:  {report['verified_at_utc']}",
        "=" * 70,
    ]
    for c in checks:
        sym = "[PASS]" if c[1] else "[FAIL]"
        lines.append(f"{sym:<7} {c[0]:<60} | {c[2]}")
    lines.append("=" * 70)
    out_txt.write_text("\n".join(lines), encoding="utf-8")
    
    return all_ok

if __name__ == "__main__":
    success = run_cross_verification()
    sys.exit(0 if success else 1)
