#!/usr/bin/env python3
"""Read-only diagnostics for the production UI lineage blocker; never grants PASS."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    from .system3_release_proof_gate import ROOT, resolve
except ImportError:  # direct script execution
    from system3_release_proof_gate import ROOT, resolve

BASE = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
OUTPUT = Path("live-production-ui-proof/lineage-diagnostic.json")


def diagnose(root: Path, fetch=None) -> dict:
    gate = resolve(root)
    fetch = fetch or fetch_public_deploy_info
    public = fetch()
    info = public.get("data", public) if isinstance(public, dict) else {}
    if not isinstance(info, dict):
        info = {}
    observed = info.get("git_sha") or info.get("github_sha") or info.get("sha")
    expected = gate.get("expected_source_sha")
    return {
        "schema": "system3-lineage-diagnostic-v1",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "state": "NOT_VERIFIED",
        "gate_state": gate["state"],
        "gate_reason": gate["reason"],
        "expected_sha": expected,
        "public_serving_sha": observed if isinstance(observed, str) and len(observed) == 40 and all(c in "0123456789abcdefABCDEF" for c in observed) else None,
        "public_revision": info.get("revision") if isinstance(info.get("revision"), str) else None,
        "next_action": "Authenticate to Cloud Run, confirm serving revision/image digest/source SHA, and produce owner-approved deployment lineage evidence; public endpoint alone is insufficient",
        "production_pass": False,
        "broker_calls": 0,
        "order_calls": 0,
    }


def fetch_public_deploy_info() -> dict:
    base = os.environ.get("SYSTEM3_PUBLIC_BASE_URL", BASE).rstrip("/")
    if not base.startswith("https://"):
        return {}
    try:
        req = urllib.request.Request(base + "/api/deploy/info", headers={"User-Agent": "System3-Lineage-Diagnostic/1"})
        with urllib.request.urlopen(req, timeout=12) as response:
            value = json.loads(response.read(32768).decode("utf-8"))
            return value if isinstance(value, dict) else {}
    except (OSError, ValueError, UnicodeError, TimeoutError):
        return {}


def main() -> int:
    result = diagnose(ROOT)
    target = ROOT / OUTPUT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("LINEAGE_DIAGNOSTIC=" + result["gate_reason"] + " production_pass=false")
    return 0  # Diagnostic succeeds; independent production proof gate remains blocking.


if __name__ == "__main__":
    raise SystemExit(main())
