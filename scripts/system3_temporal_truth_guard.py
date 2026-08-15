#!/usr/bin/env python3
"""Fail closed when stored evidence is misused as current/live System3 truth.

A stored artifact is historical by default. It can support a time-sensitive verdict only
when its manifest explicitly declares request-scoped live observation timestamps and
passes the requested-at + age bounds supplied by the current investigation.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_MAX_AGE_SECONDS = 300
LIVE_CLASSES = {
    "REQUEST_SCOPED_LIVE_BROWSER",
    "REQUEST_SCOPED_LIVE_API",
    "LIVE_LOG_OBSERVATION",
    "DEPLOYMENT_METADATA",
}


def parse_utc(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def evaluate_manifest(
    manifest: dict[str, Any],
    *,
    requested_at: datetime | None = None,
    now: datetime | None = None,
    max_age_seconds: int | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    evidence_class = str(manifest.get("evidence_class") or "").strip()
    started = parse_utc(manifest.get("capture_started_at_utc"))
    captured = parse_utc(manifest.get("captured_at_utc") or manifest.get("capture_finished_at_utc"))
    declared_max_age = manifest.get("max_age_seconds")
    if max_age_seconds is None:
        try:
            max_age_seconds = int(declared_max_age)
        except (TypeError, ValueError):
            max_age_seconds = DEFAULT_MAX_AGE_SECONDS
    reasons: list[str] = []

    if evidence_class not in LIVE_CLASSES:
        reasons.append("EVIDENCE_CLASS_NOT_LIVE")
    if started is None:
        reasons.append("CAPTURE_START_MISSING_OR_INVALID")
    if captured is None:
        reasons.append("CAPTURE_TIME_MISSING_OR_INVALID")
    if requested_at is not None:
        requested_at = requested_at.astimezone(timezone.utc)
        if started is None or started < requested_at:
            reasons.append("CAPTURE_STARTED_BEFORE_CURRENT_REQUEST")
    age_seconds: float | None = None
    if captured is not None:
        age_seconds = (now - captured).total_seconds()
        if age_seconds < -30:
            reasons.append("CAPTURE_TIME_IN_FUTURE")
        elif age_seconds > max_age_seconds:
            reasons.append("EVIDENCE_TOO_OLD_FOR_CURRENT_VERDICT")

    safety = manifest.get("safety") if isinstance(manifest.get("safety"), dict) else {}
    if evidence_class in {"REQUEST_SCOPED_LIVE_BROWSER", "REQUEST_SCOPED_LIVE_API"}:
        if safety.get("read_only_capture") is not True:
            reasons.append("READ_ONLY_CAPTURE_NOT_PROVEN")
        if safety.get("mutation_endpoints_called") is not False:
            reasons.append("MUTATION_SAFETY_NOT_PROVEN")
        if safety.get("order_endpoints_called") is not False:
            reasons.append("ORDER_SAFETY_NOT_PROVEN")
        if safety.get("secret_values_exposed") is not False:
            reasons.append("SECRET_SAFETY_NOT_PROVEN")

    return {
        "state": "CURRENT_LIVE" if not reasons else "STALE_OR_NOT_CURRENT",
        "current_live_allowed": not reasons,
        "evidence_class": evidence_class or None,
        "capture_started_at_utc": started.isoformat() if started else None,
        "captured_at_utc": captured.isoformat() if captured else None,
        "requested_at_utc": requested_at.isoformat() if requested_at else None,
        "evaluated_at_utc": now.isoformat(),
        "age_seconds": round(age_seconds, 3) if age_seconds is not None else None,
        "max_age_seconds": max_age_seconds,
        "reasons": reasons,
        "rule": "SYSTEM3_TEMPORAL_TRUTH_V1",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--requested-at", help="UTC ISO timestamp for the current investigation/request")
    parser.add_argument("--max-age-seconds", type=int, default=None)
    args = parser.parse_args()

    payload = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("TEMPORAL_TRUTH_MANIFEST_NOT_OBJECT")
    requested_at = parse_utc(args.requested_at)
    if args.requested_at and requested_at is None:
        raise SystemExit("TEMPORAL_TRUTH_REQUESTED_AT_INVALID")
    verdict = evaluate_manifest(
        payload,
        requested_at=requested_at,
        max_age_seconds=args.max_age_seconds,
    )
    print("TEMPORAL_TRUTH_VERDICT", json.dumps(verdict, sort_keys=True))
    return 0 if verdict["current_live_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
