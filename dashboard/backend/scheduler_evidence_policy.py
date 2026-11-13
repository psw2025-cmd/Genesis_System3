"""Select independently configured Cloud Scheduler evidence without changing SSOT writes.

Using SYSTEM3_STATE_BACKEND=firestore merely to inspect scheduler receipts
also enables Firestore runtime-state writes; never make that coupling necessary.
"""
from __future__ import annotations
import os
from typing import Mapping, Optional


def scheduler_evidence_backend(environ: Optional[Mapping[str, str]] = None) -> str:
    env = os.environ if environ is None else environ
    explicit = str(env.get("SYSTEM3_SCHEDULER_EVIDENCE_BACKEND") or "").strip().lower()
    if explicit:
        if explicit not in {"firestore", "file", "local"}:
            raise ValueError("UNSUPPORTED_SCHEDULER_EVIDENCE_BACKEND")
        return explicit
    inherited = str(env.get("SYSTEM3_STATE_BACKEND", "file")).strip().lower()
    return "firestore" if inherited == "firestore" else "file"
