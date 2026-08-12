#!/usr/bin/env python3
"""Fail-closed container image provenance helpers for Genesis System3.

The deployment authority may supply an Artifact Registry tag while Cloud Run
reports the immutable revision image as an ``@sha256:`` reference.  This module
resolves both references to immutable fully-qualified digests before comparing
them.  Resolution or schema ambiguity is a hard failure.
"""
from __future__ import annotations

import json
import subprocess
from typing import Any, Callable

RunFn = Callable[[list[str]], str]


def _default_run(args: list[str]) -> str:
    proc = subprocess.run(args, text=True, capture_output=True, check=False)
    if proc.returncode:
        raise RuntimeError(
            f"artifact_registry_describe_failed:{proc.returncode}:"
            f"{(proc.stderr or proc.stdout or '')[-1000:]}"
        )
    return (proc.stdout or "").strip()


def _repository(ref: str) -> str:
    value = str(ref or "").strip()
    if not value:
        raise RuntimeError("image_reference_empty")
    before_digest = value.split("@", 1)[0]
    last_slash = before_digest.rfind("/")
    last_colon = before_digest.rfind(":")
    if last_colon > last_slash:
        before_digest = before_digest[:last_colon]
    if ".pkg.dev/" not in before_digest:
        raise RuntimeError(f"artifact_registry_reference_required:{value}")
    return before_digest


def _digest_from_ref(ref: str) -> str:
    value = str(ref or "").strip()
    marker = "@sha256:"
    if marker not in value:
        return ""
    digest = value.split(marker, 1)[1].strip()
    if len(digest) != 64 or any(ch not in "0123456789abcdefABCDEF" for ch in digest):
        raise RuntimeError(f"invalid_sha256_digest:{value}")
    return f"sha256:{digest.lower()}"


def _find_digest(payload: Any) -> str:
    candidates: set[str] = set()

    def visit(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child in value.items():
                visit(child, str(child_key))
            return
        if isinstance(value, list):
            for child in value:
                visit(child, key)
            return
        if not isinstance(value, str):
            return

        text = value.strip()
        if "@sha256:" in text:
            candidates.add(_digest_from_ref(text))
        elif key.lower() == "digest" and text.startswith("sha256:"):
            digest = text.removeprefix("sha256:")
            if len(digest) == 64 and all(ch in "0123456789abcdefABCDEF" for ch in digest):
                candidates.add(f"sha256:{digest.lower()}")

    visit(payload)
    candidates.discard("")
    if len(candidates) != 1:
        raise RuntimeError(f"artifact_digest_resolution_ambiguous:{sorted(candidates)}")
    return next(iter(candidates))


def resolve_artifact_digest(ref: str, *, run: RunFn = _default_run) -> tuple[str, str]:
    """Return ``(repository, sha256:digest)`` for an Artifact Registry image."""
    repository = _repository(ref)
    direct = _digest_from_ref(ref)
    if direct:
        return repository, direct

    raw = run([
        "gcloud", "artifacts", "docker", "images", "describe", ref,
        "--format=json",
    ])
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("artifact_registry_describe_schema_error") from exc
    return repository, _find_digest(payload)


def assert_same_artifact_image(
    expected: str,
    deployed: str,
    *,
    run: RunFn = _default_run,
) -> tuple[str, str]:
    """Fail unless expected and deployed resolve to the same repo+digest."""
    expected_repo, expected_digest = resolve_artifact_digest(expected, run=run)
    deployed_repo, deployed_digest = resolve_artifact_digest(deployed, run=run)
    if expected_repo != deployed_repo or expected_digest != deployed_digest:
        raise RuntimeError(
            "candidate image mismatch: "
            f"expected={expected_repo}@{expected_digest} "
            f"actual={deployed_repo}@{deployed_digest}"
        )
    return expected_repo, expected_digest
