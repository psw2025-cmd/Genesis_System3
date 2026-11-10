"""Fail-closed, sanitized Cloud Run PAPER configuration receipt.

Reads only a gcloud run services describe JSON document. Never prints environment
values, secret references, image repository URLs or arbitrary upstream metadata.
The receipt is a read-only diagnostic, NOT a deployed source-SHA certificate.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

EXPECTED = {"PAPER_MODE": "1", "LIVE_ORDER_AUTHORITY": "0", "REAL_BROKER_ORDERS": "0"}
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")


def classify(doc: Mapping[str, Any], ci_env: Mapping[str, str]) -> dict[str, Any]:
    spec = doc.get("spec") or {}
    template = doc.get("template") or {}
    containers = ((spec.get("template") or {}).get("spec") or {}).get("containers") or template.get("containers") or []
    statuses: dict[str, str] = {}
    if len(containers) != 1:
        statuses = {key: "CONTAINER_COUNT_UNVERIFIED" for key in EXPECTED}
    else:
        entries = containers[0].get("env") or []
        for key, desired in EXPECTED.items():
            found = [entry for entry in entries if isinstance(entry, dict) and entry.get("name") == key]
            if not found:
                result = "MISSING"
            elif len(found) != 1:
                result = "DUPLICATE"
            elif found[0].get("valueFrom") is not None or found[0].get("valueSource") is not None:
                result = "REFERENCE_NOT_PLAINLY_VERIFIED"
            elif found[0].get("value") != desired:
                result = "VALUE_MISMATCH"
            elif ci_env.get(key) != desired:
                result = "CI_EXPECTATION_MISMATCH"
            else:
                result = "MATCH"
            statuses[key] = result
    service_status = doc.get("status") or {}
    traffic = []
    for item in service_status.get("traffic") or []:
        if not isinstance(item, dict):
            continue
        traffic.append({
            "revision": str(item.get("revisionName") or "")[:150],
            "percent": item.get("percent") if isinstance(item.get("percent"), int) else None,
        })
    image_digest = None
    if len(containers) == 1:
        image = str(containers[0].get("image") or "")
        match = DIGEST.search(image)
        if match:
            image_digest = match.group(0)
    passed = len(containers) == 1 and all(v == "MATCH" for v in statuses.values())
    return {
        "schema": "cloud-run-readonly-paper-safety-v1",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "check": "cloud_run_paper_environment",
        "status": "PASS" if passed else "FAIL",
        "container_count": len(containers),
        "checks": statuses,
        "latest_ready_revision": str(service_status.get("latestReadyRevisionName") or "")[:150] or None,
        "traffic": traffic,
        "image_digest_from_service_definition_only": image_digest,
        "deployed_source_sha_verified": False,
        "broker_orders_placed": False,
        "no_secret_values_collected": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    doc = json.loads(args.input.read_text(encoding="utf-8"))
    result = classify(doc, os.environ)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for key, label in result["checks"].items():
        print("CLOUD_RUN_SAFE_ENV_CHECK key=" + key + " result=" + label)
    print("CLOUD_RUN_SAFE_ENV_RESULT=" + result["status"])
    print("CLOUD_RUN_LATEST_READY_REVISION=" + str(result["latest_ready_revision"]))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
