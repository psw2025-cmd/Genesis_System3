#!/usr/bin/env python3
"""Validate reports/coordination/ACCESS_POLICY.yaml schema + acceptance fields."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "reports" / "coordination" / "ACCESS_POLICY.yaml"

REQUIRED_TOP = ["apiVersion", "kind", "metadata", "spec"]
REQUIRED_META = [
    "name",
    "policy_id",
    "version",
    "signed_by",
    "signature_status",
    "notify_channel",
    "approver_email",
]
REQUIRED_SPEC = ["mode", "live_trading_allowed", "credentials", "permissions", "smoke_tests", "audit"]


def fail(msg: str) -> int:
    print(f"ACCESS_POLICY_INVALID: {msg}")
    return 1


def main() -> int:
    if yaml is None:
        # Minimal fallback parser for CI without PyYAML: require file exists and key strings present
        text = POLICY.read_text(encoding="utf-8")
        for key in ("apiVersion:", "kind:", "policy_id:", "signature_status:", "smoke_tests:", "audit:"):
            if key not in text:
                return fail(f"missing key marker {key} (PyYAML not installed; marker check failed)")
        print("ACCESS_POLICY_OK (marker-check; install PyYAML for deep validate)")
        return 0

    if not POLICY.exists():
        return fail(f"missing {POLICY}")
    data = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return fail("root must be mapping")
    for k in REQUIRED_TOP:
        if k not in data:
            return fail(f"missing top-level {k}")
    meta = data["metadata"]
    for k in REQUIRED_META:
        if k not in meta:
            return fail(f"missing metadata.{k}")
    spec = data["spec"]
    for k in REQUIRED_SPEC:
        if k not in spec:
            return fail(f"missing spec.{k}")
    if spec.get("live_trading_allowed") is True:
        return fail("live_trading_allowed must be false")
    if spec.get("laptop_broker_mint_allowed") is True:
        return fail("laptop_broker_mint_allowed must be false")
    creds = spec["credentials"]
    if creds.get("mint_allowed") is True and meta.get("signature_status") != "VERIFIED":
        return fail("mint_allowed true requires signature_status VERIFIED")
    print(
        "ACCESS_POLICY_OK",
        f"policy_id={meta.get('policy_id')}",
        f"signature_status={meta.get('signature_status')}",
        f"mint_allowed={creds.get('mint_allowed')}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
