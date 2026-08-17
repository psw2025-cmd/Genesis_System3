#!/usr/bin/env python3
"""Append one fail-closed proof-ledger + intent tick.

Usage:
  python scripts/system3_proof_ledger.py --offline
  python scripts/system3_proof_ledger.py --git-sha HEAD --next-id A2
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.backend.proof_ledger_service import (  # noqa: E402
    append_ledger_entry,
    verify_ledger_chain,
)


def _git_sha() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return (proc.stdout or "").strip()
    except Exception:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 append-only proof ledger")
    parser.add_argument("--git-sha", default="")
    parser.add_argument("--revision", default="")
    parser.add_argument("--next-id", default="")
    parser.add_argument("--broker-connected", choices=["true", "false", "unknown"], default="unknown")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    if args.verify_only:
        print(json.dumps(verify_ledger_chain(ROOT), indent=2))
        return 0 if verify_ledger_chain(ROOT)["ok"] else 1

    connected = None
    if args.broker_connected == "true":
        connected = True
    elif args.broker_connected == "false":
        connected = False

    entry = append_ledger_entry(
        ROOT,
        git_sha=args.git_sha or _git_sha(),
        cloud_run_revision=args.revision,
        broker_connected=connected,
        next_id=args.next_id,
        evidence_class="HISTORICAL_STORED" if args.offline else "REQUEST_SCOPED_LIVE",
    )
    proof = verify_ledger_chain(ROOT)
    print(json.dumps({"entry": entry, "chain": proof}, indent=2))
    return 0 if proof.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
