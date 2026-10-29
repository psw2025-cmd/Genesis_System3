#!/usr/bin/env python3
"""Fail-closed entry point for evidence-backed paper validation.

The former implementation wrote fixed accuracy scores and fabricated trade IDs,
which could be mistaken for real evidence. Never write passing validation JSON
from this entry point without a verified prediction/outcome/trade reconciliation.
"""
from __future__ import annotations

import sys

MESSAGE = (
    "NOT VERIFIED: paper-trade lifecycle evidence is unavailable. "
    "This entry point will not generate synthetic PASS records. "
    "Use genuine timestamped prediction, fill, close, fee, and outcome records "
    "and independently validate their provenance before publishing evidence."
)


def main() -> int:
    print(MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
