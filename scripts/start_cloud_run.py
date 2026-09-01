#!/usr/bin/env python3
"""Cloud Run launcher for the Genesis System3 PAPER API.

Cloud Run startup invariant: HTTP ingress binds immediately and never waits for
broker/Secret Manager/network initialization. Broker bootstrap and the optional
PAPER execution loop therefore run in daemon threads. The PAPER loop is guarded
by an explicit fail-closed environment contract and has no live-order path.
"""
from __future__ import annotations

import json
import os
import threading

import uvicorn


def _install_runtime_patch() -> None:
    try:
        # Keep even the broker module import out of the launcher pre-bind path.
        from core.brokers.dhan.cloud_runtime_patch import install

        proof = install()
        print("[cloud-bootstrap] " + json.dumps(proof, sort_keys=True), flush=True)
    except Exception as exc:
        # Fail the broker dependency closed, not HTTP ingress. LIVE is
        # independently forced OFF by deployment configuration and mutation policy.
        print(
            "[cloud-bootstrap] "
            + json.dumps(
                {
                    "installed": False,
                    "error_type": type(exc).__name__,
                    "message": str(exc)[:160],
                    "live_trading_enabled": False,
                    "order_placement_allowed": False,
                },
                sort_keys=True,
            ),
            flush=True,
        )


def _paper_engine_enabled() -> bool:
    return os.getenv("CLOUD_PAPER_ENGINE", "0").strip().lower() in {"1", "true", "yes", "on"}


def _run_cloud_paper_engine() -> None:
    try:
        from scripts.cloud_paper_engine import run_forever

        run_forever()
    except Exception as exc:
        # PAPER engine failure must be visible and fail closed, but must not take
        # down the read-only dashboard needed to diagnose/recover the dependency.
        print(
            "[cloud-paper] "
            + json.dumps(
                {
                    "state": "STARTUP_FAILED_FAIL_CLOSED",
                    "error_type": type(exc).__name__,
                    "message": str(exc)[:200],
                    "broker_orders_called": False,
                    "live_trading_enabled": False,
                    "system3_live_trading_allowed": False,
                },
                sort_keys=True,
            ),
            flush=True,
        )


def main() -> None:
    port = int(os.getenv("PORT", "8080"))
    print(f"[cloud-start] binding 0.0.0.0:{port}", flush=True)

    # Never gate Cloud Run's PORT bind on Secret Manager, Dhan, metadata-server,
    # or any other outbound dependency.
    threading.Thread(
        target=_install_runtime_patch,
        name="system3-cloud-broker-bootstrap",
        daemon=True,
    ).start()

    if _paper_engine_enabled():
        threading.Thread(
            target=_run_cloud_paper_engine,
            name="system3-cloud-paper-engine",
            daemon=True,
        ).start()
        print("[cloud-start] PAPER engine supervisor enabled", flush=True)
    else:
        print("[cloud-start] PAPER engine supervisor disabled", flush=True)

    uvicorn.run(
        "dashboard.backend.secure_app:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        timeout_keep_alive=20,
        limit_max_requests=1000,
        limit_concurrency=50,
        log_level=os.getenv("UVICORN_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
