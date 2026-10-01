from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest

from scripts.catalyst_feed_recheck import validate


RECORD = (
    Path(__file__).parents[1]
    / "research/evidence/catalyst/2026-10-02_MOLBIO_feed_recheck.json"
)


def _payload():
    return json.loads(RECORD.read_text(encoding="utf-8"))


def _rehash(payload):
    canonical = json.dumps(
        {key: value for key, value in payload.items() if key != "record_hash"},
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    payload["record_hash"] = sha256(canonical).hexdigest()


class CatalystFeedRecheckTests(unittest.TestCase):
    def test_committed_feed_recheck_is_post_issue_and_ineligible(self):
        result = validate(_payload())
        self.assertEqual(result["status"], "POST_ISSUE_FEED_SUPERSET_NO_MATCH_SEALED")
        self.assertEqual(result["prior_rows"], 531)
        self.assertEqual(result["current_rows"], 805)
        self.assertEqual(result["new_rows"], 274)
        self.assertEqual(result["exact_matches"], 0)
        self.assertEqual(result["eligible_catalyst_features"], 0)
        self.assertEqual(result["matured_outcomes"], 0)
        self.assertFalse(result["orders_allowed"])

    def test_rejects_backfill_absence_outcome_and_causality_mutations(self):
        cases = [
            (("prediction_id",), "EQ7D-2026-10-01-OTHER-V1", "prediction ID"),
            (("prediction_event_hash",), "0" * 64, "prediction event hash"),
            (("source_url",), "https://www.nseindia.com/api/corporate-announcements?index=equities&from_date=02-10-2026&to_date=02-10-2026", "exact official session query"),
            (("current_capture", "raw_gzip_path"), "research/evidence/catalyst/raw/wrong.json.gz", "artifact path"),
            (("current_capture", "raw_bytes"), 1, "byte counts"),
            (("feed_progression", "prior_exact_rows_removed"), 1, "not an exact superset"),
            (("feed_progression", "new_rows_with_dissemination_at_or_before_prediction"), 1, "pre-issue rows"),
            (("feed_progression", "dissemination_timezone_basis"), "UTC", "timezone basis"),
            (("feed_progression", "last_new_exchdisstime_raw"), "01-Oct-2026 18:18:26", "dissemination bounds"),
            (("feature_record", "feature_eligible"), True, "prediction feature"),
            (("feature_record", "promotion_status"), "IMPUTED", "silently imputed"),
            (("feature_record", "transformation"), "contains(symbol, 'MOL')", "exact-match transformation"),
            (("published_at",), "2026-10-01T18:00:00+05:30", "invent"),
            (("interpretation",), "NO_MATCH_MEANS_ABSENT", "limitation"),
            (("later_measured_return",), 0.25, "return"),
            (("catalyst_contribution",), "POSITIVE", "contribution"),
            (("causal_attribution",), "CLAIMED", "Causality"),
            (("orders_allowed",), True, "Unsafe"),
        ]
        for path, value, message in cases:
            with self.subTest(path=path):
                payload = deepcopy(_payload())
                target = payload
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                _rehash(payload)
                with self.assertRaisesRegex(ValueError, message):
                    validate(payload)

    def test_unrehash_mutation_is_detected(self):
        payload = _payload()
        payload["current_capture"]["captured_feed_rows"] = 999
        with self.assertRaisesRegex(
            ValueError, "row count|sequence IDs|do not reconcile|hash mismatch"
        ):
            validate(payload)


if __name__ == "__main__":
    unittest.main()
