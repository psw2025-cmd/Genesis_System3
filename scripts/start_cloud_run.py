#!/usr/bin/env python3
"""Cloud Run launcher for the Genesis System3 analyzer-only API.

Cloud Run startup invariant: the HTTP ingress must be allowed to bind to the
injected PORT without waiting for broker/Secret Manager/network initialization.
The Dhan runtime patch therefore installs in a daemon thread after process
startup has begun. Any bootstrap failure is logged and the API remains up so
health/status endpoints can report the dependency failure explicitly.
"""
from __future__ import annotations

import json
import os
import threading

import uvicorn

from core.brokers.dhan.cloud_runtime_patch import install


def _install_runtime_patch() -> None:
    try:
        proof = install()
        print("[cloud-bootstrap] " + json.dumps(proof, sort_keys=True), flush=True)
    except Exception as exc:
        # Fail the broker dependency closed, not the HTTP ingress. LIVE is
        # independently forced OFF by deployment configuration and backend
        # mutation policy.
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
