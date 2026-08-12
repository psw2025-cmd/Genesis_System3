#!/usr/bin/env python3
"""Sanitize Cloud Run DSM option-chain log entries for read-only diagnosis.

This script never reads credentials or market payload files.  It accepts the
JSON emitted by ``gcloud logging read`` and emits only whitelisted DSM messages
with credential-like strings redacted plus a small classification summary.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

_TOKEN_PATTERNS = (
    re.compile(r"eyJ[A-Za-z0-9_.-]{20,}"),
    re.compile(r"(?i)(access[-_ ]?token\s*[:=]\s*)[^\s,}]+"),
    re.compile(r"(?i)(authorization\s*[:=]\s*(?:bearer\s+)?)\S+"),
)
_ALLOWED_MARKERS = (
    "Dhan option_chain fetch:",
    "Dhan option_chain non-success for",
    "Dhan option_chain retry failed for",
    "Dhan fetch_option_chain failed for",
    "expiry_list failed for",
    "Dhan client init failed:",
)


def _redact(message: str) -> str:
    text = message
    for pattern in _TOKEN_PATTERNS:
        text = pattern.sub(lambda m: (m.group(1) if m.lastindex else "") + "<REDACTED>", text)
    return text[:500]


def _classify(message: str) -> str:
    lower = message.lower()
    if "option_chain fetch:" in lower:
        return "FETCH_ATTEMPT"
    if "retry failed" in lower:
        return "RETRY_FAILED"
    if "non-success" in lower:
        if "429" in lower or "rate" in lower or "too many" in lower:
            return "NON_SUCCESS_RATE_LIMIT"
        if "subscription" in lower or "subscribe" in lower or "entitlement" in lower:
            return "NON_SUCCESS_ENTITLEMENT"
        if "401" in lower or "unauthor" in lower or "invalid token" in lower:
            return "NON_SUCCESS_AUTH"
        return "NON_SUCCESS_OTHER"
    if "expiry_list failed" in lower:
        return "EXPIRY_LIST_FAILED"
    if "client init failed" in lower:
        return "CLIENT_INIT_FAILED"
    if "fetch_option_chain failed" in lower:
        return "FETCH_EXCEPTION"
    return "OTHER"


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: gcp_dhan_oc_log_diagnostic.py <gcloud-json>")
    entries = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    counts: Counter[str] = Counter()
    selected = []
    for entry in entries if isinstance(entries, list) else []:
        message = str(entry.get("textPayload") or entry.get("jsonPayload", {}).get("message") or "")
        if "[DSM]" not in message or not any(marker in message for marker in _ALLOWED_MARKERS):
            continue
        classification = _classify(message)
        counts[classification] += 1
        selected.append(
            {
                "timestamp": entry.get("timestamp"),
                "classification": classification,
                "message": _redact(message),
            }
        )

    print("DHAN_OC_SANITIZED_LOG_DIAGNOSTIC")
    print(json.dumps({"matched": len(selected), "classification_counts": dict(counts)}, sort_keys=True))
    for row in selected[-80:]:
        print(json.dumps(row, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
