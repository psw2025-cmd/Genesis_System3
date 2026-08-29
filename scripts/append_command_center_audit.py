#!/usr/bin/env python3
"""Append-only audit log for Command Center access/smoke events."""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "reports" / "coordination" / "AUDIT_LOG.jsonl"


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else "unspecified"
    result = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    run_id = os.environ.get("GITHUB_RUN_ID") or os.environ.get("CC_RUN_ID") or f"local-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    agent_id = os.environ.get("CC_AGENT_ID", "cursor-composer")
    entry_id = f"aud-{uuid.uuid4().hex[:12]}"
    # Ephemeral dry-run token id only — never a real secret
    token_id = os.environ.get("CC_TOKEN_ID") or f"dryrun-{run_id}"
    ttl = os.environ.get("CC_TOKEN_TTL", "0s-mint-denied")
    signer = os.environ.get("CC_SIGNER", "agent-id:cursor-composer")
    entry = {
        "entry_id": entry_id,
        "utc": datetime.now(timezone.utc).isoformat(),
        "agent_id": agent_id,
        "run_id": run_id,
        "action": action,
        "signer": signer,
        "token_id": token_id,
        "ttl": ttl,
        "result": result,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(entry_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
