from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.cepe_post_decision_source import validate


RECORD = (
    Path(__file__).parents[1]
    / "research/evidence/cepe/2026-10-01_cepe_post_decision_source.json"
)


def _payload():
    return json.loads(RECORD.read_text(encoding="utf-8"))


class PostDecisionSourceTests(unittest.TestCase):
    def test_committed_receipt_preserves_locked_abstention(self):
        result = validate(_payload())
        self.assertEqual(
            result["status"], "OFFICIAL_SOURCE_CAPTURED_AFTER_LOCKED_ABSTENTION"
        )
        self.assertEqual(result["option_rows"], 32597)
        self.assertEqual(result["mechanically_screened_observations"], 5509)
        self.assertEqual(result["qualified_candidates"], 0)
        self.assertEqual(result["issued_contract_forecasts"], 0)
        self.assertEqual(result["matured_forward_outcomes"], 0)
        self.assertFalse(result["second_email_allowed"])
        self.assertFalse(result["orders_allowed"])

    def test_rejects_lookahead_source_inflation_and_unsafe_mutations(self):
        cases = [
            (("evidence_as_of",), "2026-10-01T18:00:00+05:30", "completed repeat observation"),
            (("prior_decision_lock", "second_email_allowed"), True, "second email"),
            (("prior_decision_lock", "decision_rewrite_allowed"), True, "rewrite"),
            (("availability_timeline", 3, "request_started_at"), "2026-10-01T20:00:00+05:30", "retrieval chronology"),
            (("official_archive", "exchange_publication_time"), "2026-10-01T19:00:00+05:30", "invent"),
            (("official_archive", "url"), "https://nsearchives.nseindia.com/content/fo/wrong.zip", "exact official session source"),
            (("official_archive", "member"), "wrong.csv", "member name"),
            (("mechanical_universe", "screen_is_prediction"), True, "prediction"),
            (("forward_state", "qualified_candidates"), 1, "cannot create a forecast"),
            (("forward_state", "expected_premium_move_range"), [1.0, 3.0], "premium range"),
            (("feature_registry", 11, "missing_count"), 0, "silently imputed"),
            (("gate_status", "minimum_oos_days"), 1, "Project gate thresholds"),
            (("gate_status", "directional_accuracy"), 1.0, "must remain null"),
            (("gate_status", "strategy_promoted"), True, "promoted or retuned"),
            (("orders_allowed",), True, "Unsafe or dishonest"),
        ]
        for path, value, message in cases:
            with self.subTest(path=path):
                payload = deepcopy(_payload())
                target = payload
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate(payload)


if __name__ == "__main__":
    unittest.main()
