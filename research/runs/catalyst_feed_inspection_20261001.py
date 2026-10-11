"""Reproduce the post-issue MOLBIO official-feed inspection."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path

from scripts.catalyst_feed_inspection import build_no_match_inspection


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-gzip", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = gzip.decompress(args.source_gzip.read_bytes())
    receipt = json.loads(args.receipt.read_text())
    result = build_no_match_inspection(
        raw,
        receipt,
        symbol="MOLBIO",
        isin="INE869T01028",
        prediction_id="EQ7D-2026-10-01-MOLBIO-V1",
        prediction_event_hash="91912ef5ef5264cdff60fd06449f355fcd4bfcedc6b743e46c7b6ded7236744f",
        prediction_issued_at="2026-10-01T12:44:51.984966Z",
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    raw_output = (json.dumps(result, indent=2, allow_nan=False) + "\n").encode()
    args.output.write_bytes(raw_output)
    print(json.dumps({
        "record_sha256": sha256(raw_output).hexdigest(),
        "record_hash": result["record_hash"],
        "captured_feed_rows": result["captured_feed_rows"],
        "exact_matches": result["exact_symbol_or_isin_matches"],
        "feature_eligible": result["feature_eligible"],
    }, indent=2))


if __name__ == "__main__":
    main()
