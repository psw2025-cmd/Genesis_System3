#!/usr/bin/env python3
"""Reconcile Ultra MRI browser proof without hiding real runtime drift.

Ultra MRI runs on every main push, including documentation/control-plane-only commits
that intentionally do not deploy Cloud Run. The canonical dashboard proof correctly
fails when GITHUB_SHA differs from the serving DEPLOY_GIT_SHA. This reconciler may
retry that proof against the actual serving SHA only when git diff proves that every
commit since that serving SHA is non-runtime-affecting. Runtime changes never receive
this exception.
"""
from __future__ import annotations

import contextlib
import csv
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OUT = Path(os.getenv("SYSTEM3_ULTRA_MRI_OUT", "reports/latest/system3_ultra_mri"))
MATRIX = OUT / "CAPABILITY_MATRIX.csv"
VERDICT = OUT / "FINAL_VERDICT.json"
DEPLOY = OUT / "api_deploy_info.txt"
PROOF_LOG = OUT / "canonical_browser_proof.txt"
RECON = OUT / "BROWSER_SHA_RECONCILIATION.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")

RUNTIME_EXACT = {
    "scripts/gcp_worker_job.py",
    "scripts/smoke_ml_validate_e2e.py",
    "scripts/start_cloud_run.py",
    "scripts/gcp_dhan_token_rotation_job.py",
    "scripts/gcp_cloud_run_auto_deploy.py",
    "scripts/gcp_cloud_run_auto_deploy_impl.py",
    "scripts/gcp_runtime_iam_preflight.py",
    "scripts/gcp_failed_revision_forensic.py",
    "scripts/gcp_runtime_evidence.py",
    "scripts/gcp_public_dashboard_runtime_proof.py",
    "scripts/gcp_mutation_policy_runtime_proof.py",
    "scripts/gcp_runtime_identity_safety.py",
    "scripts/sync_dhan_instruments_master.py",
    ".github/workflows/cloud-run-auto-deploy.yml",
    ".github/workflows/gcp-dhan-token-rotation.yml",
}
RUNTIME_PREFIXES = ("dashboard/", "core/", "src/", "config/", "deploy/gcp/")


def _runtime_affecting(path: str) -> bool:
    return path in RUNTIME_EXACT or path.startswith(RUNTIME_PREFIXES)


def _deploy_json() -> dict:
    raw = DEPLOY.read_text(encoding="utf-8")
    lines = raw.splitlines()
    if lines and lines[0].startswith("HTTP "):
        raw = "\n".join(lines[1:])
    value = json.loads(raw)
    return value if isinstance(value, dict) else {}


def _rows() -> list[dict[str, str]]:
    with MATRIX.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_rows(rows: list[dict[str, str]]) -> None:
    with MATRIX.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["capability", "status", "critical", "detail"])
        w.writeheader()
        w.writerows(rows)


def _recompute(rows: list[dict[str, str]]) -> None:
    old = json.loads(VERDICT.read_text(encoding="utf-8")) if VERDICT.exists() else {}
    critical = [r for r in rows if r.get("critical") == "true" and r.get("status") != "PASS"]
    old.update({
        "access_certified": not critical,
        "critical_failures": critical,
        "capabilities_total": len(rows),
        "pass": sum(r.get("status") == "PASS" for r in rows),
        "fail": sum(r.get("status") == "FAIL" for r in rows),
    })
    VERDICT.write_text(json.dumps(old, indent=2, sort_keys=True), encoding="utf-8")
    md = [
        "# System3 Ultra MRI — Final Verdict", "",
        f"- ACCESS_CERTIFIED: **{str(old['access_certified']).upper()}**",
        f"- Capabilities: {old['pass']} PASS / {old['fail']} FAIL / {old['capabilities_total']} total", "",
        "## Critical failures",
    ]
    md += [f"- `{r['capability']}` — {r['detail']}" for r in critical] if critical else ["- None"]
    md += ["", "## Evidence policy", "Secret payloads are never dumped. Runtime SHA reconciliation is allowed only after a git-diff proof that no runtime-affecting file changed.", ""]
    (OUT / "FINAL_VERDICT.md").write_text("\n".join(md), encoding="utf-8")


def _valid_commit_sha(value: str) -> bool:
    """Accept only canonical full lowercase Git SHAs that exist in this checkout."""
    if not SHA40.fullmatch(value):
        return False
    proc = subprocess.run(
        ["git", "cat-file", "-e", f"{value}^{{commit}}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.returncode == 0


def _run_canonical_proof_in_process(serving_sha: str) -> tuple[int, str, str]:
    """Run the existing proof module in-process; never spawn a command from runtime data."""
    import scripts.gcp_public_dashboard_runtime_proof as proof_module

    stdout = io.StringIO()
    stderr = io.StringIO()
    original = proof_module.EXPECTED_SHA
    try:
        proof_module.EXPECTED_SHA = serving_sha
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = int(proof_module.main())
    except Exception as exc:
        print(f"canonical_proof_exception:{type(exc).__name__}", file=stderr)
        rc = 1
    finally:
        proof_module.EXPECTED_SHA = original
    return rc, stdout.getvalue(), stderr.getvalue()


def main() -> int:
    if not (MATRIX.exists() and VERDICT.exists() and DEPLOY.exists()):
        return 0
    rows = _rows()
    browser = next((r for r in rows if r.get("capability") == "canonical_browser_proof"), None)
    if not browser or browser.get("status") == "PASS":
        _recompute(rows)
        return 0

    deploy = _deploy_json()
    serving = str(deploy.get("git_sha") or "").strip().lower()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip().lower()
    report = {"head_sha": head, "serving_sha": serving, "eligible": False, "changed_files": [], "runtime_affecting": []}
    if not _valid_commit_sha(serving) or not _valid_commit_sha(head) or serving == head:
        report["sha_validation"] = "failed_or_no_reconciliation_needed"
        RECON.write_text(json.dumps(report, indent=2), encoding="utf-8")
        _recompute(rows)
        return 0

    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{serving}..{head}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode:
        report["git_diff_error"] = proc.stderr[-2000:]
        RECON.write_text(json.dumps(report, indent=2), encoding="utf-8")
        _recompute(rows)
        return 0
    changed = [x.strip() for x in proc.stdout.splitlines() if x.strip()]
    runtime = [x for x in changed if _runtime_affecting(x)]
    report.update({"changed_files": changed, "runtime_affecting": runtime, "eligible": not runtime})
    if runtime:
        RECON.write_text(json.dumps(report, indent=2), encoding="utf-8")
        _recompute(rows)
        return 0

    proof_rc, proof_out, proof_err = _run_canonical_proof_in_process(serving)
    report["retry_exit"] = proof_rc
    report["retry_stdout_tail"] = proof_out[-4000:]
    report["retry_stderr_tail"] = proof_err[-4000:]
    RECON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    with PROOF_LOG.open("a", encoding="utf-8") as fh:
        fh.write("\nRECONCILED_NON_RUNTIME_HEAD_AGAINST_SERVING_SHA\n")
        fh.write(proof_out[-10000:])
        fh.write("\n")
        fh.write(proof_err[-10000:])
        fh.write("\n")
    if proof_rc == 0:
        browser["status"] = "PASS"
        browser["detail"] = f"serving_sha_proof={serving};head_control_plane_only={head}"
        _write_rows(rows)
    _recompute(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
