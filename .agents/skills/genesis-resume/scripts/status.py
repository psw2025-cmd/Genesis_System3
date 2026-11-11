#!/usr/bin/env python3
"""Read-only status check; never certifies a claim based on a label alone."""
import csv
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[4]
claim_path = root / "GENESIS_1872_MASTER_CHECKLIST.csv"
overlay_path = root / ".agents" / "state" / "INDEPENDENT_VERIFICATION.csv"

def load(path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))

original = load(claim_path)
overlay = load(overlay_path)
if len(overlay) != 1872 or len({row["ID"] for row in overlay}) != 1872:
    raise SystemExit("INVALID independent register: expected 1872 unique IDs")
if {r["ID"] for r in original} != {r["ID"] for r in overlay}:
    raise SystemExit("INVALID: claim and independent IDs differ")
raw = Counter((r.get("Independent Verdict") or "UNVERIFIED").upper() for r in overlay)
accepted = []
unsupported = []
for r in overlay:
    if (r.get("Independent Verdict") or "").upper() != "PASS":
        continue
    evidence = (r.get("Independent Raw Evidence URI") or "").strip()
    reviewer = (r.get("Independent Reviewer") or "").strip()
    stamp = (r.get("Verified UTC") or "").strip()
    observed = (r.get("Expected vs Observed") or "").strip()
    if not all((evidence, reviewer, stamp, observed)):
        unsupported.append(r["ID"])
        continue
    artifact = Path(evidence)
    if not artifact.is_absolute():
        artifact = root / artifact
    if not artifact.is_file():
        unsupported.append(r["ID"])
        continue
    accepted.append(r["ID"])
print(json.dumps({
    "note": "This is a tracker consistency audit only, not validation of live exchange data or independent reviewer identity.",
    "total_checks": len(overlay),
    "historical_claimed_pass": sum((r.get("Verified Verdict") or "").upper() == "PASS" for r in original),
    "independent_status_counts": dict(raw),
    "pass_rows_with_minimum_documentation": len(accepted),
    "pass_rows_missing_evidence_fields_or_artifact": len(unsupported),
    "sample_unsupported_ids": unsupported[:10],
    "certification": "NOT CERTIFIED until independent testing and sign-off"
}, indent=2))
