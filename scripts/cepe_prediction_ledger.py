"""Issue and settle CE/PE research predictions with byte-bound receipts.

Usage:
  python -m scripts.cepe_prediction_ledger issue --previous FILE --previous-day YYYY-MM-DD --following-day YYYY-MM-DD --candidates PICKS.json --output RECEIPT.json --cutoff ISO_TIMESTAMP
  python -m scripts.cepe_prediction_ledger settle --previous FILE --following FILE --receipt RECEIPT.json --output REPORT.json

Commit the receipt to an independently timestamped append-only destination BEFORE
the next market open. A local receipt alone is not proof of advance issuance.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Any

from scripts.cepe_forward_scorecard import _identity, score
from scripts.cepe_next_open_proof import _rows, compare

IST = timezone(timedelta(hours=5, minutes=30))


def _iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timestamp must include timezone")
    return parsed


def _canonical(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def issue(previous: bytes, previous_day: date, following_day: date,
          candidates: list[dict[str, Any]], cutoff: datetime,
          *, now: datetime | None = None, target_multiple: float = 3.0) -> dict[str, Any]:
    """Create an unmodifiable on-disk receipt from available prior-day data."""
    issued = now or datetime.now(timezone.utc)
    if issued.tzinfo is None or cutoff.tzinfo is None:
        raise ValueError("Timestamps require timezones")
    next_open = datetime.combine(following_day, time(9, 15), tzinfo=IST)
    if not previous_day < following_day or not previous_day <= issued.astimezone(IST).date():
        raise ValueError("Previous and following dates conflict with issuance")
    if issued > cutoff or cutoff >= next_open:
        raise ValueError("Issuance and cutoff must precede next opening")
    if not target_multiple > 1 or not target_multiple < float("inf"):
        raise ValueError("Invalid pre-registered target")
    rows = _rows(previous, previous_day)
    selected = set()
    picks = []
    source_hash = sha256(previous).hexdigest()
    for item in candidates:
        key = _identity(item)
        if key not in rows:
            raise ValueError("Candidate absent from previous market snapshot")
        if key in selected:
            raise ValueError("Duplicate candidate")
        selected.add(key)
        picks.append(dict(symbol=key[0], expiry=key[1], strike=key[2], type=key[3],
                          issued_at=issued.isoformat(), source_sha256=source_hash))
    record = dict(schema="cepe-preissue-v1", previous_day=previous_day.isoformat(),
                  following_day=following_day.isoformat(), previous_sha256=source_hash,
                  issued_at=issued.isoformat(), cutoff=cutoff.isoformat(),
                  target_multiple=target_multiple, predictions=picks,
                  orders_allowed=False)
    return {"record": record, "record_sha256": sha256(_canonical(record)).hexdigest()}


def settle(previous: bytes, following: bytes, receipt: dict[str, Any],
           *, publication_time: datetime | None = None) -> dict[str, Any]:
    """Score a receipt; external publication time is required for forward proof."""
    record = receipt["record"]
    if record.get("schema") != "cepe-preissue-v1":
        raise ValueError("Unknown receipt schema")
    if sha256(_canonical(record)).hexdigest() != receipt["record_sha256"]:
        raise ValueError("Receipt hash mismatch")
    if sha256(previous).hexdigest() != record["previous_sha256"]:
        raise ValueError("Previous source bytes changed")
    cutoff = _iso(record["cutoff"])
    issued = _iso(record["issued_at"])
    if issued > cutoff:
        raise ValueError("Receipt was issued after cutoff")
    compared = compare(previous, following, date.fromisoformat(record["previous_day"]),
                       date.fromisoformat(record["following_day"]))
    result = score(record["predictions"], compared, target_multiple=record["target_multiple"],
                   issued_cutoff=cutoff)
    result["receipt_sha256"] = receipt["record_sha256"]
    next_open = datetime.combine(date.fromisoformat(record["following_day"]), time(9, 15), tzinfo=IST)
    if publication_time is not None:
        if publication_time.tzinfo is None or not issued <= publication_time <= cutoff:
            raise ValueError("Independent publication must fall between issuance and cutoff")
        result["independent_publication_time"] = publication_time.isoformat()
    result["forward_proof_status"] = (
        "INDEPENDENT_PUBLICATION_TIMESTAMP_SUPPLIED_UNVERIFIED"
        if publication_time is not None else "LOCAL_RECEIPT_ONLY_NOT_PROVEN"
    )
    result["verified_forecast_accuracy"] = None
    return result


def _write_new(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(_canonical(payload))
        stream.flush()
        os.fsync(stream.fileno())


def main() -> None:
    parser = argparse.ArgumentParser()
    modes = parser.add_subparsers(dest="mode", required=True)
    for name in ("issue", "settle"):
        command = modes.add_parser(name)
        command.add_argument("--previous", required=True, type=Path)
        command.add_argument("--output", required=True, type=Path)
        if name == "issue":
            command.add_argument("--previous-day", required=True, type=date.fromisoformat)
            command.add_argument("--following-day", required=True, type=date.fromisoformat)
            command.add_argument("--candidates", required=True, type=Path)
            command.add_argument("--cutoff", required=True, type=_iso)
            command.add_argument("--target-multiple", type=float, default=3.0)
        else:
            command.add_argument("--following", required=True, type=Path)
            command.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    before = args.previous.read_bytes()
    if args.mode == "issue":
        output = issue(before, args.previous_day, args.following_day,
                       json.loads(args.candidates.read_text()), args.cutoff,
                       target_multiple=args.target_multiple)
    else:
        output = settle(before, args.following.read_bytes(),
                        json.loads(args.receipt.read_text()))
    _write_new(args.output, output)
    print(args.output)


if __name__ == "__main__":
    main()
