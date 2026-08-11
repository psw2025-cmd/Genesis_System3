#!/usr/bin/env python3
"""Cloud Run launcher for the Genesis System3 analyzer-only API."""
from __future__ import annotations

import json
import os

import uvicorn

from core.brokers.dhan.cloud_runtime_patch import install


def main() -> None:
    proof = install()
    print("[cloud-bootstrap] " + json.dumps(proof, sort_keys=True))
    uvicorn.run(
        "dashboard.backend.secure_app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        workers=1,
        timeout_keep_alive=20,
        limit_max_requests=1000,
        limit_concurrency=50,
        log_level=os.getenv("UVICORN_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
