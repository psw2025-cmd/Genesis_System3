#!/usr/bin/env python3
"""Append one fully identified evidence receipt; never truncate existing entries."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re

LEDGER = Path(__file__).resolve().parents[1] / "02_EVIDENCE" / "EVIDENCE.ndjson"
STATUSES = {"PASS", "FAIL", "BLOCKED", "UNKNOWN"}
URL_PREFIX = "https://github.com/psw2025-cmd/Genesis_System3/"
SHA40 = re.compile(r"[0-9a-f]{40}\Z")


def append_receipt(path: Path, record: dict) -> None:
    if not path.is_file():
        raise FileNotFoundError("append-only ledger must be initialized first")
    if record.get("status") not in STATUSES:
        raise ValueError("invalid verification status")
    if not isinstance(record.get("evidence_url"), str) or not record["evidence_url"].startswith(URL_PREFIX):
        raise ValueError("primary evidence URL is required")
    if not isinstance(record.get("source_sha"), str) or not SHA40.fullmatch(record["source_sha"]):
        raise ValueError("exact source SHA required")
    if not isinstance(record.get("claim"), str) or not record["claim"].strip():
        raise ValueError("nonempty evidence claim required")
    if not isinstance(record.get("id"), str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", record["id"]):
        raise ValueError("stable evidence ID required")
    old = path.read_bytes()
    if old and not old.endswith(b"\n"):
        raise ValueError("previous ledger must end in a complete newline")
    rows = [json.loads(line) for line in old.decode("utf-8").splitlines()]
    if record["id"] in {row.get("id") for row in rows}:
        raise ValueError("duplicate evidence ID; append a new receipt instead of overwriting history")
    complete = {"schema": "system3-evidence-v1",
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(), **record}
    if "recorded_at_utc" in record or "schema" in record:
        raise ValueError("timestamp/schema are controlled by append writer")
    line = (json.dumps(complete, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    with path.open("ab") as fp:
        fp.write(line)
    updated = path.read_bytes()
    if not updated.startswith(old) or len(updated) != len(old) + len(line):
        raise RuntimeError("append-only integrity failure")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True)
    p.add_argument("--status", required=True, choices=sorted(STATUSES))
    p.add_argument("--claim", required=True)
    p.add_argument("--url", required=True)
    p.add_argument("--sha", required=True)
    a = p.parse_args()
    append_receipt(LEDGER, {"id": a.id, "status": a.status, "claim": a.claim,
                             "evidence_url": a.url, "source_sha": a.sha})
    print("EVIDENCE_RECEIPT_APPENDED; NOT_A_PRODUCTION_CERTIFICATE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
