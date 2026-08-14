#!/usr/bin/env python3
"""Fetch the Security Audit artifact for the exact GitHub SHA.

Uses GitHub Actions read API only. Failure/timeout is explicit; no stale artifact
is accepted as exact-source evidence.
"""
from __future__ import annotations

import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
REPO = os.getenv("GITHUB_REPOSITORY", "").strip()
SHA = os.getenv("GITHUB_SHA", "").strip()
API = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
OUT = Path(os.getenv("SYSTEM3_SECURITY_AUDIT_DIR", "reports/latest/security_audit"))
TIMEOUT_S = int(os.getenv("SYSTEM3_SECURITY_WAIT_SECONDS", "600"))


def _request(url: str) -> bytes:
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "Genesis-System3-audit",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def _json(url: str):
    return json.loads(_request(url).decode())


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    state_path = OUT / "exact_fetch_state.json"
    if not TOKEN or "/" not in REPO or len(SHA) != 40:
        state_path.write_text(json.dumps({"state": "BLOCKED_INPUT_MISSING"}, indent=2), encoding="utf-8")
        return 2
    workflow_url = f"{API}/repos/{REPO}/actions/workflows/security-audit.yml/runs?head_sha={urllib.parse.quote(SHA)}&per_page=10"
    deadline = time.time() + TIMEOUT_S
    chosen = None
    while time.time() < deadline:
        data = _json(workflow_url)
        runs = data.get("workflow_runs") or []
        exact = [r for r in runs if r.get("head_sha") == SHA and r.get("event") == "push"]
        if exact:
            exact.sort(key=lambda r: r.get("created_at") or "", reverse=True)
            chosen = exact[0]
            if chosen.get("status") == "completed":
                break
        time.sleep(15)
    if not chosen or chosen.get("status") != "completed":
        state_path.write_text(json.dumps({"state": "BLOCKED_EXACT_SECURITY_RUN_TIMEOUT", "sha": SHA}, indent=2), encoding="utf-8")
        return 2
    run_id = chosen.get("id")
    artifacts = _json(f"{API}/repos/{REPO}/actions/runs/{run_id}/artifacts?per_page=100").get("artifacts") or []
    candidates = [a for a in artifacts if str(a.get("name") or "").startswith("security-audit-") and not a.get("expired")]
    if not candidates:
        state_path.write_text(json.dumps({"state": "BLOCKED_SECURITY_ARTIFACT_MISSING", "run_id": run_id}, indent=2), encoding="utf-8")
        return 2
    blob = _request(str(candidates[0]["archive_download_url"]))
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        names = zf.namelist()
        target = next((n for n in names if n.endswith("security_audit.json")), None)
        if not target:
            state_path.write_text(json.dumps({"state": "BLOCKED_SECURITY_JSON_MISSING", "run_id": run_id}, indent=2), encoding="utf-8")
            return 2
        content = zf.read(target)
    (OUT / "security_audit.json").write_bytes(content)
    state = {
        "state": "PASS",
        "sha": SHA,
        "run_id": run_id,
        "run_conclusion": chosen.get("conclusion"),
        "artifact_id": candidates[0].get("id"),
        "stale_evidence_accepted": False,
    }
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    print("EXACT_SECURITY_AUDIT_FETCH " + json.dumps(state, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
