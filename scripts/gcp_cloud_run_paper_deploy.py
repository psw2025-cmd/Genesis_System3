#!/usr/bin/env python3
"""Cloud Run deployment entrypoint for automated PAPER execution.

The existing guarded candidate/rollback deployer remains authoritative for image,
traffic, IAM and LIVE safety. This thin layer replaces only its web-runtime mode
contract before candidate creation so future deployments cannot reset the service
to analyzer-only defaults.
"""
from __future__ import annotations

import gcp_cloud_run_auto_deploy as guarded_deploy
import gcp_cloud_run_auto_deploy_impl as deploy_impl

PAPER_RUNTIME_ENV = {
    "ANALYZE_MODE": "0",
    "SYSTEM3_MODE": "PAPER",
    "CLOUD_PAPER_ENGINE": "1",
    "AUTO_EXECUTE_TRADES": "1",
    "LIVE_TRADING_ENABLED": "0",
    "SYSTEM3_LIVE_TRADING_ALLOWED": "0",
}


def apply_paper_runtime_contract() -> dict[str, str]:
    env = dict(deploy_impl.SAFE_ENV)
    env.update(PAPER_RUNTIME_ENV)
    # Preserve tuple ordering for deterministic gcloud env serialization.
    keys = [key for key, _ in deploy_impl.SAFE_ENV]
    for key in PAPER_RUNTIME_ENV:
        if key not in keys:
            keys.append(key)
    deploy_impl.SAFE_ENV = tuple((key, env[key]) for key in keys)

    effective = dict(deploy_impl.SAFE_ENV)
    for key, expected in PAPER_RUNTIME_ENV.items():
        actual = effective.get(key)
        if actual != expected:
            raise RuntimeError(f"paper_runtime_env_drift:{key}:expected={expected}:actual={actual}")
    if effective["LIVE_TRADING_ENABLED"] != "0" or effective["SYSTEM3_LIVE_TRADING_ALLOWED"] != "0":
        raise RuntimeError("paper_deploy_refuses_live_trading")
    print("CLOUD_PAPER_RUNTIME_CONTRACT", PAPER_RUNTIME_ENV)
    return effective


def main() -> int:
    apply_paper_runtime_contract()
    return guarded_deploy.main()


if __name__ == "__main__":
    raise SystemExit(main())
