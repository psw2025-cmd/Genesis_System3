"""Reproduce the retained 30 September cash observation packet, without orders.

Run from the repository root with python -m research.runs.equity_source_20261001
--source-dir research/evidence/equity/raw/2026-10-01 --output-dir NEW_DIRECTORY
--as-of TIMESTAMP_FROM_THE_COMMITTED_SUMMARY.
"""
import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path

from scripts.equity_observation_packet import build_packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args()
    files = {"cash": "cm_20260930.zip", "company": "EQUITY_L.csv",
             "etf": "eq_etfseclist.csv", "actions": "corporate_actions.json"}
    records = {r["file"]: r for r in json.loads((args.source_dir / "receipts.json").read_text())}
    receipts = {k: records[v] for k, v in files.items()}
    packet = build_packet({k: (args.source_dir / v).read_bytes() for k, v in files.items()},
                          receipts, as_of=args.as_of)
    raw = (json.dumps(packet, indent=2, allow_nan=False) + "\n").encode()
    compressed = gzip.compress(raw, mtime=0)
    summary = {k: v for k, v in packet.items() if k != "observations"}
    action_statuses = Counter(r["action_review"]["status"] for r in packet["observations"])
    summary.update(
        task_id="EQ-SOURCE-007", previous_task="MB-REF-006",
        evaluator_parent="6c8db7b45b6329215d4f1a28eedaf76faa3eee67",
        full_packet_file="2026-10-01_equity_source_packet.full.json.gz",
        full_packet_sha256=sha256(compressed).hexdigest(),
        uncompressed_packet_sha256=sha256(raw).hexdigest(),
        action_review_counts=dict(action_statuses),
        examples=[r for r in packet["observations"] if r["symbol"] in {"POLICYBZR", "BAJAJ-AUTO", "RELIANCE"}],
        action_flagged_observations=[r for r in packet["observations"] if r["action_review"]["action_count"]],
        status="OFFICIAL_OBSERVATIONS_CAPTURED_NOT_A_FORECAST",
        limitations=[
            "Prices are raw exchange references; adjusted prices and complete action coverage remain NOT_PROVEN.",
            "Current company/ETF masters classify at capture time, not historical universe membership.",
            "No qualified forecast, expected return range, calibration or mature forward outcome is created.",
            "Corporate-action rows without dissemination times cannot be backfilled into earlier predictions.",
        ])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / summary["full_packet_file"]).open("xb") as stream:
        stream.write(compressed)
    with (args.output_dir / "2026-10-01_equity_source_packet.json").open("x") as stream:
        json.dump(summary, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"counts": packet["counts"], "observations": packet["company_eq_observation_count"],
                      "action_review_counts": action_statuses, "full_packet_sha256": summary["full_packet_sha256"]}, indent=2))


if __name__ == "__main__":
    main()
