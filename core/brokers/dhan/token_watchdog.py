"""Retired Dhan token watchdog compatibility module.

Google Cloud Run Job ``genesis-system3-dhan-token-rotate`` is the sole token
mint/renew authority. The former watchdog refreshed tokens locally and could
invalidate the token consumed by the production Cloud Run service without
advancing Google Secret Manager. All compatibility functions below are
non-mutating.
"""
from __future__ import annotations

import threading


def watchdog_cycle() -> str:
    return "retired_gcp_rotation_authoritative"


def run_watchdog_loop() -> None:
    # Do not create a persistent process: callers from legacy startup paths must
    # return immediately rather than becoming another token authority.
    return None


def start_watchdog_thread() -> threading.Thread:
    thread = threading.Thread(target=lambda: None, name="RetiredDhanTokenWatchdog", daemon=True)
    thread.start()
    return thread
